#!/usr/bin/env python3
"""Comprovantes de pagamento do Itaú (PDF ou texto) → favorecido de cada pagamento do extrato.

  ler      python comprovantes_itau.py ler "Relatório pagamentos realizados.xls" Comprovante*.pdf -o trabalho/comprovantes.csv
           (o relatório de pagamentos do Itaú é a fonte principal; os comprovantes completam juros/multa)
           Uma linha por comprovante: tipo (boleto, PIX, QR Code, tributo), data, valor pago, favorecido,
           CPF/CNPJ, valor original, desconto, juros/multa.
  aplicar  python comprovantes_itau.py aplicar trabalho/normalizado.csv -c trabalho/comprovantes.csv \
               -o trabalho/normalizado_nomes.csv
           Casa cada saída do extrato com um comprovante (mesma data e mesmo valor) e reescreve a descrição
           como "SISPAG FORNECEDORES <FAVORECIDO>" (ou "BOLETO PAGO"/"PIX ENVIADO"), para as regras do
           razão modelo reconhecerem o favorecido. Guarda CNPJ e juros no campo documento.

Requer pdfplumber (ou pypdf) para PDF. O texto também pode vir do Google Drive (read_file_content).
"""
import argparse
import csv
import os
import re
import sys
from collections import defaultdict
from datetime import datetime, timedelta

CAMPOS = ["tipo", "data", "valor", "favorecido", "cpf_cnpj", "valor_documento", "desconto", "juros_multa", "arquivo"]
V = r"([\d.]+,\d{2})"
D = r"(\d{2}/\d{2}/\d{4})"
DOC = r"(\d{2}\.\d{3}\.\d{3}/\d{4}-\d{2}|[\d*.\\/-]{11,20})"


def num(v):
    return round(float(str(v or "0").replace(".", "").replace(",", ".")), 2)


def texto_arquivo(caminho):
    if caminho.lower().endswith(".pdf"):
        try:
            import pdfplumber
            with pdfplumber.open(caminho) as pdf:
                return "\n".join(p.extract_text() or "" for p in pdf.pages)
        except ImportError:
            from pypdf import PdfReader
            return "\n".join(p.extract_text() or "" for p in PdfReader(caminho).pages)
    with open(caminho, encoding="utf-8", errors="replace") as f:
        return f.read()


def texto_layout(caminho):
    """Texto do PDF preservando colunas (pdftotext -layout), para o layout novo do Itaú (2026)."""
    import shutil
    import subprocess
    if caminho.lower().endswith(".pdf") and shutil.which("pdftotext"):
        return subprocess.run(["pdftotext", "-layout", caminho, "-"], capture_output=True, text=True).stdout
    return ""


ROTULOS_NOVO = sorted(["nome", "nome do recebedor", "nome do pagador", "nome do devedor", "CPF/CNPJ", "CPF/CNPJ do recebedor",
                       "CPF/CNPJ do pagador", "CPF/CNPJ do devedor", "razão social", "valor", "valor do documento",
                       "valor do pagamento", "valor da transação", "desconto", "abatimento", "mora", "multa", "juros",
                       "data do pagamento", "data do vencimento", "data da transferência", "código de barras",
                       "tipo de pagamento", "tipo de transação", "chave", "instituição", "agência/conta"],
                      key=len, reverse=True)


def extrair_novo(texto, arquivo=""):
    """Layout novo do Itaú (a partir de abr/2026): blocos "comprovante de ..." com linhas "rótulo   valor".

    Tipos: pagamento de boleto (Itaú ou outro banco), transferência (PIX), pagamento QR Code.
    Débito automático é ignorado: o extrato já traz o nome (DA COPEL, DA VIVO...).
    """
    regs = []
    blocos = re.split(r"(?m)^\s*(?=comprovante de )", texto)
    for b in blocos:
        tit = b.split("\n", 1)[0].strip().lower()
        if not tit.startswith("comprovante de"):
            continue
        secao, campos = "", {}
        for linha in b.splitlines()[1:]:
            ls = linha.strip()
            if ls.lower().startswith("dados d"):
                secao = ls.lower()
                continue
            m = re.match(r"^\s*(\S.*?)\s{2,}(\S.*)$", linha)
            if not m:  # texto de OCR: rótulo e valor separados por um espaço só
                m = re.match(r"^\s*(" + "|".join(map(re.escape, ROTULOS_NOVO)) + r")\s+(\S.*)$", linha, re.I)
            if m:
                campos.setdefault((secao, m.group(1).strip().lower()), m.group(2).strip())
                campos.setdefault(("", m.group(1).strip().lower()), m.group(2).strip())
        g = lambda k, sec="": campos.get((sec, k), "")
        val = lambda k, sec="": (re.search(V, g(k, sec)) or [None, "0,00"])[1]
        dt = lambda x: (re.search(D, x or "") or [None, ""])[1]
        if "boleto" in tit:
            sec = "dados do beneficiário"
            fav = g("razão social", sec) or g("nome", sec)
            juros = num(val("mora")) + num(val("multa")) + num(val("juros"))
            regs.append({"tipo": "boleto", "data": dt(g("data do pagamento")), "valor": val("valor do pagamento"),
                         "favorecido": fav, "cpf_cnpj": g("cpf/cnpj", sec), "valor_documento": val("valor do documento"),
                         "desconto": val("desconto"), "juros_multa": f"{juros:.2f}".replace(".", ","), "arquivo": arquivo})
        elif "qr code" in tit or "or code" in tit:  # OCR às vezes lê "QR" como "OR"
            efet = re.search(r"efetuad[oa] em " + D, b)
            juros = num(val("juros")) + num(val("multa"))
            regs.append({"tipo": "PIX QR Code", "data": efet.group(1) if efet else "", "valor": val("valor da transação") if g("valor da transação") else val("valor"),
                         "favorecido": g("nome do recebedor"), "cpf_cnpj": g("cpf/cnpj do recebedor"),
                         "valor_documento": val("valor do documento"), "desconto": val("desconto"),
                         "juros_multa": f"{juros:.2f}".replace(".", ","), "arquivo": arquivo,
                         "devedor": g("nome do devedor")})
        elif "transferência" in tit or "transferencia" in tit:
            regs.append({"tipo": "PIX", "data": dt(g("data da transferência")), "valor": val("valor"),
                         "favorecido": g("nome do recebedor"), "cpf_cnpj": g("cpf/cnpj do recebedor"),
                         "valor_documento": "", "desconto": "0,00", "juros_multa": "0,00", "arquivo": arquivo})
    return [r for r in regs if r["data"] and r["valor"] != "0,00"]


def extrair(texto, arquivo=""):
    t = re.sub(r"\s+", " ", texto.replace("\\*", "*"))
    regs = []
    # boletos
    PAGADOR = r"(?:\d{2}\.\d{3}\.\d{3}/\d{4}-\d{2}|\d{3}\.\d{3}\.\d{3}-\d{2})"  # CNPJ da empresa ou CPF (boleto em nome de funcionário)
    for m in re.finditer(r"Beneficiário: (.+?) CPF/CNPJ do beneficiário: (.{0,160}?)"
                         r"Valor do boleto \(R\$\); ?" + V + r" \(-\) Desconto \(R\$\): ?" + V +
                         r" \(\+\) ?(?:Juros/)?Mora/Multa \(R\$\): ?" + V + r".{0,160}?\(=\) Valor do pagamento \(R\$\):.{0,120}?"
                         + PAGADOR + r" " + V + r".{0,400}?Data de pagamento: ?.{0,200}?" + D, t):
        fav, meio, vdoc, desc, mora, vpag, dpag = m.groups()
        dm = re.search(DOC, meio)
        doc = dm.group(1) if dm else ""
        # boleto de intermediador (PagCerto, Asaas...): o fornecedor de verdade é o "Beneficiário Final"
        bf = re.search(r"Beneficiário Final: CPF/CNPJ do beneficiário final: \(=\) Data de pagamento: (.+?) " + DOC,
                       t[m.start():m.end() + 300])
        if bf and bf.group(1).strip():
            fav, doc = bf.group(1).strip(), bf.group(2)
        regs.append({"tipo": "boleto", "data": dpag, "valor": vpag, "favorecido": fav.strip(), "cpf_cnpj": doc,
                     "valor_documento": vdoc, "desconto": desc, "juros_multa": mora})
    # transferências PIX / TED
    for m in re.finditer(r"nome do recebedor: ([^:]{2,60}?) chave: [^:]{0,120}?CPF / CNPJ do recebedor: (\S+) "
                         r".{0,300}?valor: R\$ " + V + r" data da transferência: " + D +
                         r" tipo de pagamento: (.{2,40}?) mensagem", t):
        fav, doc, v, d, tp = m.groups()
        regs.append({"tipo": "PIX" if "PIX" in tp else tp.strip(), "data": d, "valor": v, "favorecido": fav.strip(),
                     "cpf_cnpj": doc, "valor_documento": v, "desconto": "0,00", "juros_multa": "0,00"})
    # PIX QR Code
    for m in re.finditer(r"Comprovante de pagamento QR Code .*?nome do recebedor: (.+?) CPF / CNPJ do recebedor: (\S+)"
                         r".*?desconto: " + V + r".*?juros: " + V + r" multa: " + V + r" valor final: " + V +
                         r".*?Pagamento efetuado em " + D, t):
        fav, doc, desc, juros, multa, v, d = m.groups()
        regs.append({"tipo": "PIX QR Code", "data": d, "valor": v, "favorecido": fav.strip(), "cpf_cnpj": doc,
                     "valor_documento": v, "desconto": desc, "juros_multa": f"{num(juros) + num(multa):.2f}".replace(".", ",")})
    # tributos (municipais, estaduais, federais, concessionárias)
    for m in re.finditer(r"Comprovante de Pagamento (?:de )?(Tributos [A-Za-zçãõé ]+?|DARF[^ ]*|GPS|FGTS[^ ]*|"
                         r"[Cc]oncessionárias?|com código de barras)"
                         r" .{0,300}?Valor do documento: R\$ " + V + r".{0,400}?efetuada em " + D, t):
        tp, v, d = m.groups()
        regs.append({"tipo": tp.strip(), "data": d, "valor": v, "favorecido": tp.strip().upper(), "cpf_cnpj": "",
                     "valor_documento": v, "desconto": "0,00", "juros_multa": "0,00"})
    # DARE da Sefaz-SP (ICMS SP)
    for m in re.finditer(r"Comprovante de pagamento - (SEFAZ-[A-Z]{2})/DARE.{0,600}?valor: R\$ " + V, t):
        uf, v = m.groups()
        d = re.search(r"(?:data de pagamento|pago em|efetuad[oa] em)[: ]*" + D, t[m.start():m.start() + 1500], re.I) \
            or re.search(D, t[max(0, m.start() - 400):m.start()])
        regs.append({"tipo": "DARE", "data": d.group(1) if d else "", "valor": v, "favorecido": f"{uf} DARE (ICMS)",
                     "cpf_cnpj": "", "valor_documento": v, "desconto": "0,00", "juros_multa": "0,00"})
    for r in regs:
        r["arquivo"] = os.path.basename(arquivo)
    return regs


def ler_relatorio_pagamentos(caminho):
    """XLS "Relatório de pagamentos realizados" do Itaú: favorecido, CPF/CNPJ, tipo, data, valor, status."""
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from plano_contas import linhas_planilha
    regs, cab = [], None
    for row in linhas_planilha(caminho):
        low = [c.lower() for c in row]
        if any("favorecido" in c for c in low):
            cab = {c: i for i, c in enumerate(low)}
            continue
        if not cab or len(row) < 6 or not re.match(r"\d{2}/\d{2}/\d{4}", row[cab.get("data do pagamento", 4)] or ""):
            continue
        g = lambda nome, pad: row[cab[nome]] if nome in cab and cab[nome] < len(row) else pad
        if "efetuad" not in g("status", "efetuado").lower():
            continue
        v = float(str(g("valor (r$)", "0")).replace(",", "."))
        tipo = g("tipo de pagamento", "")
        regs.append({"tipo": "boleto" if "boleto" in tipo.lower() else "PIX QR Code" if "qr" in tipo.lower()
                     else "PIX" if "pix" in tipo.lower() else tipo,
                     "data": g("data do pagamento", ""), "valor": f"{v:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."),
                     "favorecido": g("favorecido / beneficiário", "").strip(), "cpf_cnpj": g("cpf/cnpj", ""),
                     "valor_documento": "", "desconto": "0,00", "juros_multa": "0,00", "arquivo": os.path.basename(caminho)})
    return regs


def cmd_ler(a):
    regs = []
    for f in a.arquivos:
        if f.lower().endswith((".xls", ".xlsx", ".csv")):
            regs += ler_relatorio_pagamentos(f)
            continue
        achados = extrair(texto_arquivo(f), f)
        regs += achados or extrair_novo(texto_layout(f) if f.lower().endswith(".pdf") else texto_arquivo(f), f)
    # o mesmo comprovante pode aparecer em dois arquivos: remove repetidos
    # O mesmo pagamento pode estar no relatório (XLS) e num comprovante (PDF): conta-se o maior número de
    # ocorrências entre as fontes (dois pagamentos iguais no mesmo dia continuam dois), preferindo o PDF.
    grupos = defaultdict(lambda: {"xls": [], "pdf": []})
    for r in regs:
        k = (r["data"], r["valor"])  # o nome muda entre relatório e comprovante (ex.: ACNIS BRASIL x ACNIS DO BRASIL)
        grupos[k]["pdf" if r["arquivo"].lower().endswith(".pdf") else "xls"].append(r)
    unicos = []
    for g in grupos.values():
        n = max(len(g["xls"]), len(g["pdf"]))
        unicos += (g["pdf"] + g["xls"])[:n]
    regs = sorted(unicos, key=lambda r: (r["data"][6:] + r["data"][3:5] + r["data"][:2], r["favorecido"]))
    with open(a.saida, "w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=CAMPOS, delimiter=";", extrasaction="ignore")
        w.writeheader()
        w.writerows(regs)
    tipos = defaultdict(int)
    for r in regs:
        tipos[r["tipo"]] += 1
    print(f"{len(regs)} comprovante(s) -> {a.saida} | " + ", ".join(f"{k}: {v}" for k, v in sorted(tipos.items())))
    print(f"Total pago: {sum(num(r['valor']) for r in regs):,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))


def _aplicar_comp(l, c, v, nomes_folha, novas):
    """Reescreve a linha do extrato com o favorecido do comprovante; juros/multa viram linha própria."""
    prefixo = {"boleto": "BOLETO PAGO", "PIX": "PIX ENVIADO", "PIX QR Code": "PIX QR CODE"}.get(c["tipo"], "SISPAG")
    if c["tipo"].startswith(("Tributos", "DARF", "GPS", "FGTS")):
        prefixo = "SISPAG TRIBUTOS"
    if c["tipo"] in ("DARE",) or c["tipo"].lower().startswith(("concession", "com código")):
        prefixo = "SISPAG TRIBUTOS" if c["tipo"] == "DARE" else "SISPAG"
    l["descricao"] = f"{prefixo} {c['favorecido']}".strip()
    # pessoa física (CPF) que não está na folha: marcada para a regra de serviços de terceiros
    if re.fullmatch(r"[\d*]{3}\.[\d*]{3}\.[\d*]{3}-[\d*]{2}", c["cpf_cnpj"] or "") and nomes_folha is not None:
        nome = re.sub(r"[^A-Z ]", "", c["favorecido"].upper()).split()
        if not any(" ".join(nome[:2]) in f for f in nomes_folha):
            l["descricao"] += " (PESSOA FISICA)"
    l["documento"] = c["cpf_cnpj"] or l.get("documento", "")
    juros = num(c["juros_multa"])
    if juros > 0:  # pago com atraso: principal na conta do favorecido, juros/multa em linha própria
        l["valor"] = f"{-(v - juros):.2f}"
        novas.append(dict(l, id=l["id"] + "-J", valor=f"{-juros:.2f}",
                          descricao=f"JUROS/MULTA {prefixo} {c['favorecido']}".strip()))


def cmd_aplicar(a):
    with open(a.comprovantes, encoding="utf-8-sig") as f:
        comps = list(csv.DictReader(f, delimiter=";"))
    with open(a.extrato, encoding="utf-8-sig") as f:
        extrato = list(csv.DictReader(f, delimiter=";"))
    nomes_folha = None
    if a.folha:
        with open(a.folha, encoding="utf-8-sig") as f:
            nomes_folha = {re.sub(r"[^A-Z ]", "", r["nome"].upper()) for r in csv.DictReader(f, delimiter=";")}
    livres = defaultdict(list)
    for c in comps:
        livres[(c["data"], num(c["valor"]))].append(c)
    usados = casados = 0
    sem, novas, pendentes = [], [], []
    for l in extrato:
        v = round(-float(l["valor"]), 2)
        if v <= 0:
            continue
        lista = livres.get((l["data"], v))
        if lista:
            casados += 1
            _aplicar_comp(l, lista.pop(0), v, nomes_folha, novas)
        else:
            pendentes.append((l, v))
    # pagamento feito no fim de semana/feriado entra no extrato no dia útil seguinte (até 3 dias depois)
    for l, v in pendentes:
        d = datetime.strptime(l["data"], "%d/%m/%Y")
        lista = next((livres[k] for k in (((d - timedelta(days=n)).strftime("%d/%m/%Y"), v) for n in (1, 2, 3))
                      if livres.get(k)), None)
        if lista:
            casados += 1
            _aplicar_comp(l, lista.pop(0), v, nomes_folha, novas)
        elif re.search(r"SISPAG (FORNECEDORES|TRIBUTOS)|^REF A\.?$|^$", l["descricao"].strip()):
            sem.append(l)
    for n in novas:  # linha de juros logo depois do pagamento
        extrato.insert(next(i for i, x in enumerate(extrato) if x["id"] == n["id"][:-2]) + 1, n)
    if novas:
        print(f"{len(novas)} pagamento(s) com juros/multa separados em linha própria (JUROS/MULTA ...)")
    for lista in livres.values():
        usados += len(lista)
    with open(a.saida, "w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(extrato[0].keys()), delimiter=";")
        w.writeheader()
        w.writerows(extrato)
    print(f"{casados} pagamento(s) identificados pelos comprovantes -> {a.saida}")
    print(f"Comprovantes sem pagamento no extrato: {usados}")
    for lista in livres.values():
        for c in lista:
            print(f"  {c['data']} {c['valor']:>12} {c['tipo']} {c['favorecido'][:40]}")
    print(f"Pagamentos SISPAG ainda sem comprovante: {len(sem)}")
    for l in sem[:40]:
        print(f"  {l['data']} {l['valor']:>12} {l['descricao'][:40]}")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("ler")
    s.add_argument("arquivos", nargs="+")
    s.add_argument("-o", "--saida", required=True)
    s = sub.add_parser("aplicar")
    s.add_argument("extrato")
    s.add_argument("-c", "--comprovantes", required=True)
    s.add_argument("-f", "--folha", help="CSV da folha: PIX a pessoa física fora da folha ganha '(PESSOA FISICA)'")
    s.add_argument("-o", "--saida", required=True)
    a = ap.parse_args()
    return cmd_ler(a) if a.cmd == "ler" else cmd_aplicar(a)


if __name__ == "__main__":
    sys.exit(main())
