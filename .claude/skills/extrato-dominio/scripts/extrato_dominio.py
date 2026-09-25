#!/usr/bin/env python3
"""Extrato bancário -> lançamentos contábeis em TXT para o sistema Domínio.

Subcomandos:
  ler         Lê extrato (OFX, CSV ou TXT já importado no Domínio) e gera CSV.
  classificar Aplica as regras da empresa e gera CSV classificado.
  analisar    Relatório de conferência (totais, saldo, duplicidades, pendências).
  gerar       Gera o TXT de importação do Domínio a partir do CSV classificado.

Exemplos:
  python extrato_dominio.py ler extrato.ofx -o normalizado.csv
  python extrato_dominio.py classificar normalizado.csv -e empresas/123.json -o classificado.csv
  python extrato_dominio.py analisar classificado.csv -e empresas/123.json
  python extrato_dominio.py gerar classificado.csv -e empresas/123.json -o lancamentos.txt
  python extrato_dominio.py ler antigo_PAGAR.txt --juntar antigo_RECEBER.txt -e empresas/123.json -o historico.csv
"""
import argparse
import csv
import json
import re
import sys
import unicodedata
from collections import Counter, defaultdict
from datetime import datetime
from decimal import Decimal, InvalidOperation
from pathlib import Path

CSV_SEP = ";"
CAMPOS_NORMALIZADO = ["data", "descricao", "documento", "valor", "id"]
CAMPOS_CLASSIFICADO = CAMPOS_NORMALIZADO + ["conta", "historico", "complemento", "regra", "status"]
STATUS_OK = "CONFIRMADO"  # demais: PROVÁVEL, NÃO CRUZADO, DIVERGENTE (padrão ROF)

LAYOUT_PADRAO = {
    "formato": "dominio",   # "dominio" (|0000|/|6000|/|6100|) ou "delimitado"
    "separador": ";",
    "campos": ["data", "conta_debito", "conta_credito", "valor", "historico", "complemento"],
    "formato_data": "%d/%m/%Y",
    "decimal": ",",
    "encoding": "cp1252",
    "quebra_linha": "\r\n",
    "tam_max_complemento": 200,
    "cabecalho": False,
}


# ---------------------------------------------------------------- utilidades

def normalizar_texto(s):
    s = unicodedata.normalize("NFKD", s or "")
    s = "".join(c for c in s if not unicodedata.combining(c))
    return re.sub(r"\s+", " ", s).strip().upper()


def ler_arquivo_texto(caminho):
    dados = Path(caminho).read_bytes()
    for enc in ("utf-8-sig", "cp1252", "latin-1"):
        try:
            return dados.decode(enc)
        except UnicodeDecodeError:
            continue
    return dados.decode("latin-1", errors="replace")


def parse_valor(texto):
    """Aceita '1.234,56', '1234.56', '-1.234,56', '1.234,56 D', '(1.234,56)', 'R$ 10,00'."""
    if texto is None:
        return None
    t = str(texto).strip().upper().replace("R$", "").replace(" ", "")
    if not t or t in ("-", "--"):
        return None
    negativo = False
    if t.endswith("D") or t.endswith("-"):
        negativo, t = True, t[:-1]
    elif t.endswith("C") or t.endswith("+"):
        t = t[:-1]
    if t.startswith("(") and t.endswith(")"):
        negativo, t = True, t[1:-1]
    if t.startswith("-"):
        negativo, t = not negativo, t[1:]
    if "," in t and "." in t:
        if t.rfind(",") > t.rfind("."):
            t = t.replace(".", "").replace(",", ".")
        else:
            t = t.replace(",", "")
    elif "," in t:
        t = t.replace(",", ".")
    elif t.count(".") > 1:
        t = t.replace(".", "")
    try:
        v = Decimal(t)
    except InvalidOperation:
        return None
    return -v if negativo else v


def parse_data(texto):
    t = (texto or "").strip()
    for fmt in ("%d/%m/%Y", "%d/%m/%y", "%Y-%m-%d", "%d-%m-%Y", "%d.%m.%Y", "%Y%m%d"):
        try:
            return datetime.strptime(t[:10] if fmt != "%Y%m%d" else t[:8], fmt).date()
        except ValueError:
            continue
    return None


def ler_csv(caminho):
    with open(caminho, encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f, delimiter=CSV_SEP))


def gravar_csv(caminho, linhas, campos):
    with open(caminho, "w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=campos, delimiter=CSV_SEP, extrasaction="ignore")
        w.writeheader()
        w.writerows(linhas)


def carregar_empresa(caminho):
    with open(caminho, encoding="utf-8") as f:
        emp = json.load(f)
    layout = dict(LAYOUT_PADRAO)
    layout.update(emp.get("layout_txt") or {})
    emp["layout_txt"] = layout
    emp.setdefault("regras", [])
    return emp


def fmt_brl(v):
    s = f"{abs(v):,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    return ("-" if v < 0 else "") + s


# ---------------------------------------------------------------- leitura

def ler_ofx(texto):
    def tag(bloco, nome):
        m = re.search(rf"<{nome}>([^<\r\n]*)", bloco, re.I)
        return m.group(1).strip() if m else ""

    info = {
        "banco": tag(texto, "BANKID"),
        "agencia": tag(texto, "BRANCHID"),
        "conta": tag(texto, "ACCTID"),
        "inicio": tag(texto, "DTSTART")[:8],
        "fim": tag(texto, "DTEND")[:8],
    }
    m = re.search(r"<LEDGERBAL>(.*?)(</LEDGERBAL>|<AVAILBAL>|</STMTRS>)", texto, re.I | re.S)
    if m:
        info["saldo_final"] = tag(m.group(1), "BALAMT")
        info["data_saldo"] = tag(m.group(1), "DTASOF")[:8]

    linhas = []
    for bloco in re.findall(r"<STMTTRN>(.*?)(?=</STMTTRN>|<STMTTRN>|</BANKTRANLIST>)", texto, re.I | re.S):
        valor = parse_valor(tag(bloco, "TRNAMT").replace(",", "."))
        data = parse_data(tag(bloco, "DTPOSTED")[:8])
        if valor is None or data is None:
            continue
        memo = tag(bloco, "MEMO")
        nome = tag(bloco, "NAME")
        descricao = memo if not nome or nome in memo else (f"{nome} {memo}".strip() if memo else nome)
        linhas.append({
            "data": data.strftime("%d/%m/%Y"),
            "descricao": re.sub(r"\s+", " ", descricao),
            "documento": tag(bloco, "CHECKNUM") or tag(bloco, "REFNUM"),
            "valor": str(valor),
            "id": tag(bloco, "FITID"),
        })
    return linhas, info


def _achar_coluna(cabecalho, candidatos):
    norm = {normalizar_texto(c): c for c in cabecalho}
    for cand in candidatos:
        for n, original in norm.items():
            if n == cand:
                return original
    for cand in candidatos:
        for n, original in norm.items():
            if cand in n:
                return original
    return None


def ler_csv_banco(texto):
    amostra = "\n".join(texto.splitlines()[:20])
    try:
        sep = csv.Sniffer().sniff(amostra, delimiters=";,\t|").delimiter
    except csv.Error:
        sep = ";"
    todas = list(csv.reader(texto.splitlines(), delimiter=sep))
    # pula linhas de título até achar um cabeçalho com "data"
    inicio = next((i for i, l in enumerate(todas) if any("DATA" in normalizar_texto(c) for c in l)), 0)
    cab = [c.strip() for c in todas[inicio]]
    c_data = _achar_coluna(cab, ["DATA", "DATA LANCAMENTO", "DT"])
    c_desc = _achar_coluna(cab, ["DESCRICAO", "HISTORICO", "LANCAMENTO", "MEMO", "DETALHE"])
    c_doc = _achar_coluna(cab, ["DOCUMENTO", "DOC", "N DOCUMENTO", "NUMERO"])
    c_valor = _achar_coluna(cab, ["VALOR", "VALOR (R$)", "MONTANTE", "QUANTIA"])
    c_cred = _achar_coluna(cab, ["CREDITO", "ENTRADA", "ENTRADAS"])
    c_deb = _achar_coluna(cab, ["DEBITO", "SAIDA", "SAIDAS"])
    c_tipo = _achar_coluna(cab, ["TIPO", "D/C", "DC", "NATUREZA"])
    if not c_data or not (c_valor or c_cred or c_deb):
        raise SystemExit(f"CSV sem colunas reconhecíveis de data/valor. Cabeçalho encontrado: {cab}")

    linhas = []
    for bruto in todas[inicio + 1:]:
        if not any(x.strip() for x in bruto):
            continue
        reg = dict(zip(cab, bruto))
        data = parse_data(reg.get(c_data, ""))
        if data is None:
            continue
        desc = (reg.get(c_desc) or "").strip()
        if "SALDO" in normalizar_texto(desc) and ("ANTERIOR" in normalizar_texto(desc) or "DO DIA" in normalizar_texto(desc)):
            continue
        if c_valor:
            valor = parse_valor(reg.get(c_valor))
            if valor is not None and c_tipo and normalizar_texto(reg.get(c_tipo, "")).startswith("D") and valor > 0:
                valor = -valor
        else:
            cr = parse_valor(reg.get(c_cred)) if c_cred else None
            db = parse_valor(reg.get(c_deb)) if c_deb else None
            valor = (cr or Decimal(0)) - abs(db or Decimal(0))
            if not cr and not db:
                valor = None
        if valor is None or valor == 0:
            continue
        linhas.append({
            "data": data.strftime("%d/%m/%Y"),
            "descricao": re.sub(r"\s+", " ", desc),
            "documento": (reg.get(c_doc) or "").strip() if c_doc else "",
            "valor": str(valor),
            "id": "",
        })
    return linhas, {}


PREFIXO_REF = re.compile(r"^REF\.?\s*A\.?\s*", re.I)


def ler_txt_dominio(texto, conta_banco):
    """Lê TXT já importado no Domínio (registros 6100) e devolve movimentos já classificados."""
    if not conta_banco:
        raise SystemExit("Para ler TXT do Domínio informe a empresa (-e), que define a conta_banco.")
    linhas = []
    for bruto in texto.splitlines():
        campos = bruto.strip().split("|")
        if len(campos) < 8 or campos[1] != "6100":
            continue
        _, _, data, deb, cred, valor, hist, comp = campos[:8]
        v = parse_valor(valor)
        if deb == conta_banco:
            contra = cred
        elif cred == conta_banco:
            contra, v = deb, -v
        else:
            print(f"AVISO: lançamento sem a conta do banco {conta_banco}, ignorado: {bruto.strip()}")
            continue
        desc = PREFIXO_REF.sub("", comp).strip()
        linhas.append({"data": data, "descricao": desc, "documento": "", "valor": str(v), "id": "",
                       "conta": contra, "historico": hist, "complemento": "", "regra": "TXT Domínio",
                       "status": STATUS_OK})
    return linhas


def ler_pdf_itau(caminho):
    """Extrato PDF do Itaú Empresas: "DD/MM DESCRIÇÃO [AG] VALOR [SALDO]". Guarda o saldo diário
    "SDO CTA/APL AUTOMATICAS" (conta + aplicação automática) para montar a aplicação."""
    try:
        import pdfplumber
        with pdfplumber.open(caminho) as pdf:
            texto = "\n".join(p.extract_text() or "" for p in pdf.pages)
    except ImportError:
        from pypdf import PdfReader
        texto = "\n".join(p.extract_text() or "" for p in PdfReader(caminho).pages)
    ano = re.search(r"Extrato de \d{2}/\d{2}/(\d{4})", texto)
    ano = ano.group(1) if ano else str(datetime.now().year)
    linhas, saldos, info = [], {}, {}
    for l in texto.splitlines():
        m = re.match(r"^(\d{2}/\d{2}) (.+?) (-?[\d.]+,\d{2})(?: (-?[\d.]+,\d{2}))?$", l.strip())
        if not m:
            continue
        dm, desc, v1, v2 = m.groups()
        data = f"{dm}/{ano}"
        d = desc.strip()
        if "SALDO ANTERIOR" in d:
            info["saldo_inicial"] = v1
            continue
        if d.replace(" ", "") == "SALDO":
            info["saldo_final"] = v1
            continue
        if d.startswith("SDO CTA/APL"):
            saldos[data] = parse_valor(v1)
            continue
        ag = re.search(r" (\d{3,4})$", d)
        doc = ""
        if ag:
            d, doc = d[:ag.start()].strip(), ag.group(1)
        linhas.append({"data": data, "descricao": d, "documento": "", "valor": str(parse_valor(v1)), "id": ""})
    return linhas, info, saldos


def aplicacao_automatica(linhas, saldos, saldo_aplic_inicial):
    """Conta que fica com saldo fixo (ex.: R$ 1,00): o líquido de cada dia vai para a aplicação (saldo sobrou)
    ou sai dela (faltou). Confere com o saldo diário "conta + aplicação" do extrato."""
    por_dia = defaultdict(Decimal)
    for l in linhas:
        por_dia[l["data"]] += Decimal(l["valor"])
    novos, difs, aplic = [], [], Decimal(str(saldo_aplic_inicial))
    for data in sorted(por_dia, key=lambda d: datetime.strptime(d, "%d/%m/%Y")):
        liq = por_dia[data]
        aplic += liq
        if liq > 0:
            novos.append({"data": data, "descricao": "APLICACAO AUT MAIS", "documento": "", "valor": str(-liq), "id": ""})
        elif liq < 0:
            novos.append({"data": data, "descricao": "RESGATE APLIC AUT MAIS", "documento": "", "valor": str(-liq), "id": ""})
        if data in saldos and Decimal(str(saldos[data])) != aplic + 1:
            difs.append((data, saldos[data], aplic + 1))
    return novos, difs, aplic


def cmd_ler(a):
    if a.arquivo.lower().endswith(".pdf"):
        linhas, info, saldos = ler_pdf_itau(a.arquivo)
        if a.aplicacao_inicial is not None:
            novos, difs, aplic = aplicacao_automatica(linhas, saldos, parse_valor(a.aplicacao_inicial))
            linhas += novos
            info["aplicacao_final"] = fmt_brl(aplic)
            info["aplicacao_movimentos"] = len(novos)
            info["aplicacao_conferencia"] = "OK: bate com o saldo diário do extrato" if not difs else \
                f"DIVERGE em {len(difs)} dia(s), 1º: {difs[0][0]} extrato {fmt_brl(difs[0][1])} x calculado {fmt_brl(difs[0][2])}"
        linhas.sort(key=lambda l: (datetime.strptime(l["data"], "%d/%m/%Y"), "APLIC" in l["descricao"] or "RESGATE" in l["descricao"]))
        for i, l in enumerate(linhas, 1):
            l["id"] = f"L{i:05d}"
        gravar_csv(a.saida, linhas, CAMPOS_NORMALIZADO)
        ent = sum(Decimal(l["valor"]) for l in linhas if Decimal(l["valor"]) > 0)
        sai = sum(Decimal(l["valor"]) for l in linhas if Decimal(l["valor"]) < 0)
        print(f"Origem: PDF Itaú | Movimentos: {len(linhas)} | Entradas: {fmt_brl(ent)} | Saídas: {fmt_brl(sai)} | Líquido: {fmt_brl(ent + sai)}")
        for k, v in info.items():
            print(f"{k}: {v}")
        print(f"Arquivo gerado: {a.saida}")
        return
    texto = ler_arquivo_texto(a.arquivo)
    info = {}
    campos = CAMPOS_NORMALIZADO
    if texto.lstrip().startswith("|0000|"):
        emp = carregar_empresa(a.empresa) if a.empresa else {}
        linhas = ler_txt_dominio(texto, str(emp.get("conta_banco") or ""))
        origem, campos = "TXT Domínio (já classificado)", CAMPOS_CLASSIFICADO
    elif "<OFX>" in texto.upper() or "OFXHEADER" in texto.upper():
        linhas, info = ler_ofx(texto)
        origem = "OFX"
    else:
        linhas, info = ler_csv_banco(texto)
        origem = "CSV"
    for extra in a.juntar or []:
        emp = carregar_empresa(a.empresa) if a.empresa else {}
        linhas += ler_txt_dominio(ler_arquivo_texto(extra), str(emp.get("conta_banco") or ""))
    linhas.sort(key=lambda l: datetime.strptime(l["data"], "%d/%m/%Y"))
    for i, l in enumerate(linhas, 1):
        l["id"] = l["id"] or f"L{i:05d}"
    gravar_csv(a.saida, linhas, campos)
    ent = sum(Decimal(l["valor"]) for l in linhas if Decimal(l["valor"]) > 0)
    sai = sum(Decimal(l["valor"]) for l in linhas if Decimal(l["valor"]) < 0)
    print(f"Origem: {origem} | Movimentos: {len(linhas)}")
    if linhas:
        print(f"Período: {linhas[0]['data']} a {linhas[-1]['data']}")
    print(f"Entradas: {fmt_brl(ent)} | Saídas: {fmt_brl(sai)} | Líquido: {fmt_brl(ent + sai)}")
    for k, v in info.items():
        if v:
            print(f"{k}: {v}")
    print(f"Arquivo gerado: {a.saida}")


# ---------------------------------------------------------------- classificação

def regra_casa(regra, desc_norm, valor, data=None):
    tipo = regra.get("tipo", "ambos")
    if data and ("dia_de" in regra or "dia_ate" in regra):
        dia = datetime.strptime(data, "%d/%m/%Y").day
        if not int(regra.get("dia_de", 1)) <= dia <= int(regra.get("dia_ate", 31)):
            return False
    if tipo == "entrada" and valor <= 0:
        return False
    if tipo == "saida" and valor >= 0:
        return False
    termos = regra.get("contem") or []
    if isinstance(termos, str):
        termos = [termos]
    if termos and not any(normalizar_texto(t) in desc_norm for t in termos):
        return False
    excluir = regra.get("nao_contem") or []
    if isinstance(excluir, str):
        excluir = [excluir]
    if any(normalizar_texto(t) in desc_norm for t in excluir):
        return False
    if "regex" in regra and not re.search(regra["regex"], desc_norm, re.I):
        return False
    return bool(termos) or "regex" in regra


def cmd_classificar(a):
    emp = carregar_empresa(a.empresa)
    linhas = ler_csv(a.arquivo)
    pend = []
    for l in linhas:
        valor = Decimal(l["valor"])
        dn = normalizar_texto(l["descricao"])
        l.setdefault("conta", "")
        if l.get("conta"):  # já classificado manualmente: preserva
            continue
        for i, r in enumerate(emp["regras"]):
            if regra_casa(r, dn, valor, l["data"]):
                l["conta"] = str(r["conta"])
                l["historico"] = str(r.get("historico", emp.get("historico_padrao", "")))
                l["complemento"] = r.get("complemento") or l["descricao"]
                l["regra"] = r.get("nome") or f"regra {i + 1}"
                l["status"] = r.get("status", STATUS_OK)
                break
        else:
            l["historico"] = str(emp.get("historico_padrao", ""))
            l["complemento"] = l["descricao"]
            l["regra"] = ""
            l["status"] = ""
            pend.append(l)
    gravar_csv(a.saida, linhas, CAMPOS_CLASSIFICADO)
    print(f"Classificados: {len(linhas) - len(pend)} de {len(linhas)} | Pendentes: {len(pend)}")
    if pend:
        grupos = defaultdict(list)
        for l in pend:
            chave = re.sub(r"[\d\W_]+", " ", normalizar_texto(l["descricao"])).strip()[:40]
            grupos[(chave, "E" if Decimal(l["valor"]) > 0 else "S")].append(l)
        print("\nPENDENTES agrupados (descrição | E=entrada S=saída | qtd | total):")
        for (chave, t), itens in sorted(grupos.items(), key=lambda kv: -len(kv[1])):
            tot = sum(Decimal(i["valor"]) for i in itens)
            print(f"  {chave or '(sem descrição)'} | {t} | {len(itens)} | {fmt_brl(tot)}")
    print(f"Arquivo gerado: {a.saida}")


# ---------------------------------------------------------------- análise

def cmd_analisar(a):
    emp = carregar_empresa(a.empresa) if a.empresa else {}
    linhas = ler_csv(a.arquivo)
    if not linhas:
        print("Nenhum movimento.")
        return
    valores = [Decimal(l["valor"]) for l in linhas]
    ent = sum(v for v in valores if v > 0)
    sai = sum(v for v in valores if v < 0)
    datas = [datetime.strptime(l["data"], "%d/%m/%Y").date() for l in linhas]
    print("=== RESUMO DO EXTRATO ===")
    print(f"Período: {min(datas):%d/%m/%Y} a {max(datas):%d/%m/%Y} | Movimentos: {len(linhas)}")
    print(f"Entradas: {fmt_brl(ent)} ({sum(1 for v in valores if v > 0)})")
    print(f"Saídas:   {fmt_brl(sai)} ({sum(1 for v in valores if v < 0)})")
    print(f"Líquido:  {fmt_brl(ent + sai)}")
    if a.saldo_inicial is not None:
        si = parse_valor(a.saldo_inicial)
        calc = si + ent + sai
        print(f"Saldo inicial informado: {fmt_brl(si)} -> saldo final calculado: {fmt_brl(calc)}")
        if a.saldo_final is not None:
            sf = parse_valor(a.saldo_final)
            dif = calc - sf
            print(f"Saldo final do extrato: {fmt_brl(sf)} | Diferença: {fmt_brl(dif)}"
                  + ("  OK" if dif == 0 else "  <<< DIVERGENTE"))

    # duplicidades: mesma data, valor e descrição
    cont = Counter((l["data"], l["valor"], normalizar_texto(l["descricao"])) for l in linhas)
    dups = [(k, n) for k, n in cont.items() if n > 1]
    print("\n=== POSSÍVEIS DUPLICIDADES ===")
    if dups:
        for (d, v, desc), n in dups:
            print(f"  {d} | {fmt_brl(Decimal(v))} | {desc[:60]} | {n}x")
    else:
        print("  Nenhuma.")

    if "conta" in linhas[0]:
        pend = [l for l in linhas if not l.get("conta")]
        print(f"\n=== PENDENTES DE CLASSIFICAÇÃO: {len(pend)} ===")
        for l in pend[: a.max_itens]:
            print(f"  {l['id']} | {l['data']} | {fmt_brl(Decimal(l['valor']))} | {l['descricao'][:70]}")
        if len(pend) > a.max_itens:
            print(f"  ... e mais {len(pend) - a.max_itens}")
        por_conta = defaultdict(lambda: [0, Decimal(0)])
        for l in linhas:
            if l.get("conta"):
                por_conta[l["conta"]][0] += 1
                por_conta[l["conta"]][1] += Decimal(l["valor"])
        nomes = {str(k): v for k, v in (emp.get("contas") or {}).items()}
        print("\n=== TOTAL POR CONTA (contrapartida) ===")
        for conta, (n, tot) in sorted(por_conta.items(), key=lambda kv: kv[1][1]):
            print(f"  {conta:>8} {nomes.get(conta, '')[:40]:40} | {n:4} | {fmt_brl(tot)}")

    print(f"\n=== MAIORES VALORES (top {min(10, len(linhas))}) ===")
    for l in sorted(linhas, key=lambda l: -abs(Decimal(l["valor"])))[:10]:
        print(f"  {l['data']} | {fmt_brl(Decimal(l['valor']))} | {l['descricao'][:70]}")


# ---------------------------------------------------------------- geração TXT

def limpar_campo(texto, sep, tam=None):
    t = unicodedata.normalize("NFC", str(texto or ""))
    t = t.replace(sep, " ").replace("\r", " ").replace("\n", " ").replace('"', "'")
    t = re.sub(r"\s+", " ", t).strip()
    return t[:tam] if tam else t


def montar_lancamentos(linhas, emp, usar_transitoria):
    lay = emp["layout_txt"]
    conta_banco = str(emp.get("conta_banco") or "").strip()
    if not conta_banco:
        raise SystemExit("Configure 'conta_banco' (código reduzido da conta do banco no Domínio) no arquivo da empresa.")
    transitoria = str(emp.get("conta_transitoria") or "").strip()
    pend = [l for l in linhas if not (l.get("conta") or "").strip()]
    if pend and not usar_transitoria:
        print(f"ERRO: {len(pend)} movimento(s) sem conta. Classifique-os ou use --usar-transitoria.")
        for l in pend[:20]:
            print(f"  {l['id']} | {l['data']} | {l['valor']} | {l['descricao'][:60]}")
        sys.exit(1)
    if pend and not transitoria:
        raise SystemExit("--usar-transitoria exige 'conta_transitoria' no arquivo da empresa.")
    modelo = [l for l in linhas if (l.get("conta") or "").strip("0 ") == ""
              and (l.get("conta") or "").strip()]
    if modelo:
        raise SystemExit(f"{len(modelo)} movimento(s) com conta '0000' do modelo. "
                         "Troque pelos códigos reais do plano de contas no JSON da empresa.")

    prefixo = emp.get("prefixo_complemento", "")
    lancs = []
    for l in linhas:
        valor = Decimal(l["valor"])
        contra = (l.get("conta") or "").strip() or transitoria
        if valor > 0:   # entrada: D banco / C contrapartida
            deb, cred = conta_banco, contra
        else:           # saída: D contrapartida / C banco
            deb, cred = contra, conta_banco
        v = f"{abs(valor):.2f}"
        if lay["decimal"] == ",":
            v = v.replace(".", ",")
        comp = l.get("complemento") or l["descricao"]
        if l.get("documento") and emp.get("documento_no_complemento", True) and l["documento"] not in comp:
            comp = f"{comp} DOC {l['documento']}"
        if prefixo and not comp.upper().startswith(prefixo.strip().upper()):
            comp = prefixo + comp
        lancs.append({
            "entrada": valor > 0,
            "valor_abs": abs(valor),
            "data": datetime.strptime(l["data"], "%d/%m/%Y").strftime(lay["formato_data"]),
            "conta_debito": deb,
            "conta_credito": cred,
            "valor": v,
            "historico": str(l.get("historico") or emp.get("historico_padrao", "")),
            "complemento": comp,
            "documento": l.get("documento") or "",
            "codigo_empresa": str(emp.get("codigo_empresa", "")),
            "cnpj": re.sub(r"\D", "", str(emp.get("cnpj", ""))),
            "filial": str(emp.get("filial", "")),
            "vazio": "",
        })
    return lancs, pend, transitoria


def linhas_delimitado(lancs, lay):
    sep = lay["separador"]
    saida = [sep.join(c.upper() for c in lay["campos"])] if lay.get("cabecalho") else []
    for x in lancs:
        faltando = [c for c in lay["campos"] if c not in x]
        if faltando:
            raise SystemExit(f"Campo(s) de layout desconhecido(s): {faltando}.")
        saida.append(sep.join(
            limpar_campo(x[c], sep, lay.get("tam_max_complemento") if c == "complemento" else None)
            for c in lay["campos"]))
    return saida


def linhas_dominio(lancs, lay, emp):
    """Leiaute padrão do Domínio (registros 0000 / 6000 / 6100), lote tipo X = 1 débito x 1 crédito."""
    cnpj = re.sub(r"\D", "", str(emp.get("cnpj", "")))
    if len(cnpj) not in (11, 14):
        raise SystemExit("O formato 'dominio' exige o CNPJ (ou CPF) da empresa no JSON.")
    saida = [f"|0000|{cnpj}|"]
    for x in lancs:
        comp = limpar_campo(x["complemento"], "|", lay.get("tam_max_complemento"))
        saida.append("|6000|X||||")
        saida.append(f"|6100|{x['data']}|{x['conta_debito']}|{x['conta_credito']}|{x['valor']}|"
                     f"{limpar_campo(x['historico'], '|')}|{comp}||||")
    return saida


def gravar_txt(caminho, linhas_txt, lay):
    with open(caminho, "w", encoding=lay["encoding"], errors="replace", newline="") as f:
        f.write(lay["quebra_linha"].join(linhas_txt) + lay["quebra_linha"])


def conferir_para_entrega(linhas, a):
    """Regras invioláveis do padrão ROF: saldo fechando e só lançamentos CONFIRMADOS no TXT definitivo."""
    problemas = []
    ent = sum(Decimal(l["valor"]) for l in linhas if Decimal(l["valor"]) > 0)
    sai = sum(Decimal(l["valor"]) for l in linhas if Decimal(l["valor"]) < 0)
    if a.saldo_inicial is None or a.saldo_final is None:
        problemas.append("saldo inicial/final do extrato não informado (--saldo-inicial / --saldo-final)")
    else:
        si, sf = parse_valor(a.saldo_inicial), parse_valor(a.saldo_final)
        dif = (sf - si) - (ent + sai)
        print(f"Conferência de saldo: {fmt_brl(si)} + entradas {fmt_brl(ent)} + saídas {fmt_brl(sai)} "
              f"= {fmt_brl(si + ent + sai)} | extrato {fmt_brl(sf)} | diferença {fmt_brl(dif)}")
        if dif != 0:
            problemas.append(f"saldo NÃO fecha (diferença {fmt_brl(dif)})")
    nao_ok = [l for l in linhas if "status" in l and (l.get("status") or "").upper() != STATUS_OK]
    if nao_ok:
        cont = Counter((l.get("status") or "PENDENTE").upper() for l in nao_ok)
        problemas.append("lançamentos não confirmados: " + ", ".join(f"{k} {v}" for k, v in cont.items()))
    return problemas


def cmd_gerar(a):
    emp = carregar_empresa(a.empresa)
    lay = emp["layout_txt"]
    linhas = ler_csv(a.arquivo)
    problemas = conferir_para_entrega(linhas, a)
    if problemas and not a.previa:
        print("TXT DEFINITIVO NÃO GERADO (padrão ROF):")
        for p in problemas:
            print(f"  - {p}")
        print("Resolva as pendências ou gere uma prévia com --previa.")
        sys.exit(1)
    if problemas:
        a.saida = str(Path(a.saida).with_name(Path(a.saida).stem + "_PREVIA" + Path(a.saida).suffix))
        print("ATENÇÃO: arquivo gerado como PRÉVIA. Não importar como definitivo:")
        for p in problemas:
            print(f"  - {p}")
    lancs, pend, transitoria = montar_lancamentos(linhas, emp, a.usar_transitoria)

    def render(grupo):
        if lay.get("formato", "delimitado") == "dominio":
            return linhas_dominio(grupo, lay, emp)
        return linhas_delimitado(grupo, lay)

    separar = a.separar or emp.get("separar_pagar_receber", False)
    base = Path(a.saida)
    if separar:
        arquivos = [(base.with_name(f"{base.stem}_PAGAR{base.suffix}"), [x for x in lancs if not x["entrada"]]),
                    (base.with_name(f"{base.stem}_RECEBER{base.suffix}"), [x for x in lancs if x["entrada"]])]
    else:
        arquivos = [(base, lancs)]
    for caminho, grupo in arquivos:
        if not grupo:
            continue
        gravar_txt(caminho, render(grupo), lay)
        tot = sum(x["valor_abs"] for x in grupo)
        print(f"Arquivo gerado: {caminho} | {len(grupo)} lançamento(s) | total {fmt_brl(tot)}")
    if pend:
        print(f"ATENÇÃO: {len(pend)} lançamento(s) na conta transitória {transitoria}.")
    formato = lay.get("formato", "delimitado")
    print(f"Formato: {formato}" + ("" if formato == "dominio" else f" ({lay['separador'].join(lay['campos'])})")
          + f" | encoding {lay['encoding']}")


# ---------------------------------------------------------------- CLI

def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)

    s = sub.add_parser("ler", help="OFX/CSV/TXT Domínio -> CSV normalizado")
    s.add_argument("arquivo")
    s.add_argument("-e", "--empresa", help="JSON da empresa (obrigatório para TXT do Domínio)")
    s.add_argument("--juntar", nargs="*", help="outros TXT do Domínio a juntar (ex.: _RECEBER com _PAGAR)")
    s.add_argument("--aplicacao-inicial", help="PDF Itaú com aplicação automática: saldo da aplicação no início "
                   "(balancete); gera as linhas APLICACAO/RESGATE diárias e confere com o saldo do extrato")
    s.add_argument("-o", "--saida", default="extrato_normalizado.csv")
    s.set_defaults(func=cmd_ler)

    s = sub.add_parser("classificar", help="aplica regras da empresa")
    s.add_argument("arquivo")
    s.add_argument("-e", "--empresa", required=True)
    s.add_argument("-o", "--saida", default="extrato_classificado.csv")
    s.set_defaults(func=cmd_classificar)

    s = sub.add_parser("analisar", help="relatório de conferência")
    s.add_argument("arquivo")
    s.add_argument("-e", "--empresa")
    s.add_argument("--saldo-inicial")
    s.add_argument("--saldo-final")
    s.add_argument("--max-itens", type=int, default=50)
    s.set_defaults(func=cmd_analisar)

    s = sub.add_parser("gerar", help="gera TXT para importação no Domínio")
    s.add_argument("arquivo")
    s.add_argument("-e", "--empresa", required=True)
    s.add_argument("-o", "--saida", default="lancamentos_dominio.txt")
    s.add_argument("--usar-transitoria", action="store_true",
                   help="lança pendentes na conta_transitoria em vez de abortar")
    s.add_argument("--saldo-inicial", help="saldo inicial do extrato (obrigatório no TXT definitivo)")
    s.add_argument("--saldo-final", help="saldo final do extrato (obrigatório no TXT definitivo)")
    s.add_argument("--previa", action="store_true",
                   help="gera mesmo com saldo não conferido ou itens não confirmados (arquivo _PREVIA)")
    s.add_argument("--separar", action="store_true",
                   help="gera dois arquivos: _PAGAR (saídas) e _RECEBER (entradas)")
    s.set_defaults(func=cmd_gerar)

    a = p.parse_args()
    a.func(a)


if __name__ == "__main__":
    main()
