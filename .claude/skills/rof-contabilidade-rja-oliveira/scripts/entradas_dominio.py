#!/usr/bin/env python3
"""Relatório "Acompanhamento de Entradas" do Domínio (notas de fornecedores) x pagamentos do extrato.

  ler      python entradas_dominio.py ler Entradas.xls -o empresas/<cod>-entradas.csv [--acrescentar]
           Uma linha por nota: emissão, entrada, número, fornecedor, CNPJ, CFOP, acumulador, valor
           contábil, retenções (IRRF, CRF, ISS retido, INSS retido) e valor líquido a pagar.
  conferir python entradas_dominio.py conferir trabalho/classificado.csv -n empresas/<cod>-entradas.csv \
               [-e empresas/<empresa>.json] [--aplicar trabalho/classificado_nf.csv]
           Para cada pagamento ainda não confirmado, procura a nota:
             NOME + VALOR  → fornecedor da descrição do extrato e valor da nota (cheio, líquido ou parcela)
             SÓ VALOR      → pagamento sem nome (ex.: SISPAG FORNECEDORES) com valor igual a uma única nota
             SÓ NOME       → fornecedor encontrado, mas o valor não bate (parcela, juros, várias notas)
           --aplicar grava a conta de fornecedores (JSON: conta_fornecedores; padrão do escritório 506, pois a
           nota já foi contabilizada pela Escrita Fiscal): NOME + VALOR = CONFIRMADO; SÓ VALOR = PROVÁVEL.
           Os demais casos (só nome, várias notas, sem nota) são informados ao usuário para identificar junto.

Lê .xls (leitor tolerante do plano_contas.py; precisa de olefile) ou CSV com ';'.
"""
import argparse
import csv
import json
import os
import re
import sys
import unicodedata
from datetime import date, datetime, timedelta

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from plano_contas import linhas_planilha  # noqa: E402

CAMPOS = ["codigo", "emissao", "entrada", "nota", "serie", "fornecedor", "cnpj", "cfop", "acumulador", "uf",
          "valor", "irrf", "crf", "iss_ret", "inss_ret", "liquido"]
RETENCOES = {"IRRF": "irrf", "CRF": "crf", "ISS RET": "iss_ret", "INSS RET": "inss_ret", "INSS": "inss_ret"}
PALAVRAS_VAZIAS = {"LTDA", "ME", "EPP", "EIRELI", "SA", "S", "A", "DE", "DO", "DA", "DOS", "DAS", "E", "CIA", "COM",
                   "IND", "COMERCIO", "INDUSTRIA", "BRASIL", "DO BRASIL", "SERVICOS"}


def normalizar(t):
    t = unicodedata.normalize("NFKD", t or "").encode("ascii", "ignore").decode().upper()
    return re.sub(r"[^A-Z0-9 ]+", " ", t)


def num(v):
    v = str(v or "").strip()
    if not v:
        return 0.0
    if "," in v:
        v = v.replace(".", "").replace(",", ".")
    try:
        return round(float(v), 2)
    except ValueError:
        return 0.0


def data_excel(v):
    v = str(v).strip()
    if re.fullmatch(r"\d{5}(\.\d+)?", v):
        return (date(1899, 12, 30) + timedelta(days=int(float(v)))).strftime("%d/%m/%Y")
    return v


def brl(v):
    return f"{v:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


def cmd_ler(a):
    notas, atual = [], None
    for row in linhas_planilha(a.arquivo):
        if row and row[0].isdigit() and len(row) > 19 and row[10]:
            atual = {"codigo": row[0], "emissao": data_excel(row[1]), "entrada": data_excel(row[4]),
                     "nota": row[5], "serie": row[7], "fornecedor": re.sub(r"\s+", " ", row[10]).strip(),
                     "cnpj": row[12], "cfop": row[16], "acumulador": row[17], "uf": row[18],
                     "valor": num(row[19]), "irrf": 0.0, "crf": 0.0, "iss_ret": 0.0, "inss_ret": 0.0}
            notas.append(atual)
            tipo = row[20].strip().upper() if len(row) > 20 else ""
        elif atual is not None and len(row) > 23 and not (row[0] or "").strip():
            tipo = row[20].strip().upper()
        else:
            atual = None if row and row[0].startswith(("Total", "ACOMPANHAMENTO")) else atual
            continue
        campo = RETENCOES.get(tipo)
        if campo and atual is not None:
            atual[campo] = round(atual[campo] + num(row[23]), 2)
    # a mesma nota pode ter vários lançamentos (CFOPs diferentes): somar por fornecedor + nota
    agrup = {}
    for n in notas:
        k = (re.sub(r"\D", "", n["cnpj"]) or n["fornecedor"], n["nota"], n["serie"])
        if k in agrup:
            g = agrup[k]
            for c in ("valor", "irrf", "crf", "iss_ret", "inss_ret"):
                g[c] = round(g[c] + n[c], 2)
            g["cfop"] = "/".join(dict.fromkeys((g["cfop"] + "/" + n["cfop"]).split("/")))
        else:
            agrup[k] = dict(n)
    lista = list(agrup.values())
    for n in lista:
        n["liquido"] = round(n["valor"] - n["irrf"] - n["crf"] - n["iss_ret"] - n["inss_ret"], 2)
    antigos = []
    if a.acrescentar and os.path.exists(a.saida):
        chaves = {(n["cnpj"], n["nota"], n["serie"]) for n in lista}
        with open(a.saida, encoding="utf-8-sig") as f:
            antigos = [r for r in csv.DictReader(f, delimiter=";") if (r["cnpj"], r["nota"], r["serie"]) not in chaves]
    todos = antigos + [{k: (f"{v:.2f}" if isinstance(v, float) else v) for k, v in n.items()} for n in lista]
    todos.sort(key=lambda r: datetime.strptime(r["entrada"], "%d/%m/%Y") if re.match(r"\d\d/\d\d/\d{4}", r["entrada"]) else datetime.min)
    with open(a.saida, "w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=CAMPOS, delimiter=";", extrasaction="ignore")
        w.writeheader()
        w.writerows(todos)
    tot = sum(n["valor"] for n in lista)
    ret = sum(n["valor"] - n["liquido"] for n in lista)
    datas = [datetime.strptime(n["entrada"], "%d/%m/%Y") for n in lista if re.match(r"\d\d/\d\d/\d{4}", n["entrada"])]
    print(f"{len(lista)} nota(s) | valor contábil {brl(tot)} | retenções {brl(ret)} | "
          f"{min(datas):%d/%m/%Y} a {max(datas):%d/%m/%Y} -> {a.saida}")
    print(f"Conferência com o 'Total Geral' do relatório: some o valor contábil ({brl(tot)}) e compare.")


# nome no extrato → começo da razão social na nota (acrescente no JSON: "apelidos_fornecedor")
APELIDOS = {"VIVO": "TELEFONICA", "COPEL": "COPEL", "SANEPAR": "COMPANHIA DE SANEAMENTO", "CLARO": "CLARO",
            "TIM": "TIM"}


def chave_nome(texto):
    """Palavras significativas do nome, para casar a descrição truncada do extrato com o fornecedor.
    O CNPJ que o MEI leva no começo do nome (ex.: "61.173.722 CAROLINE RIBEIRO") é ignorado."""
    return [p for p in normalizar(texto).split() if p not in PALAVRAS_VAZIAS and len(p) > 1 and not p.isdigit()]


def nome_no_extrato(desc):
    d = normalizar(desc)
    m = (re.search(r"\b(BOLETO PAGO|PIX ENVIADO|PIX QR CODE|TED ENVIADA|PAGTO)\s+(.*)", d)
         or re.match(r"(DA|PAG|DEB AUT|DEBITO AUT)\s+(.*)", d))  # "DA COPEL" = débito automático
    nome = m.group(2).strip() if m else ""
    for apelido, nome_nf in APELIDOS.items():  # nome comercial no extrato x razão social na nota
        if re.match(apelido + r"\b", nome):
            nome = nome_nf + " " + nome[len(apelido):]
    return nome.strip()


def casa_nome(nome_ext, fornecedor):
    """O extrato corta o nome (~13 letras): casa se o começo do fornecedor bate com o trecho do extrato."""
    e = chave_nome(nome_ext)
    f = chave_nome(fornecedor)
    if not e or not f:
        return False
    alvo = " ".join(f)
    trecho = " ".join(e)
    if alvo.startswith(trecho) or trecho.startswith(alvo):
        return True
    # primeira palavra igual e a segunda (cortada) é prefixo
    if e[0] == f[0] and (len(e) == 1 or len(f) == 1 or f[1].startswith(e[1]) or e[1].startswith(f[1])):
        return True
    return len(e[0]) >= 5 and f[0].startswith(e[0])


def valores_da_nota(n):
    v, liq = num(n["valor"]), num(n["liquido"])
    op = [(v, "valor da nota")]
    if abs(liq - v) > 0.004:
        op.append((liq, "líquido das retenções"))
    for p in range(2, 13):
        op.append((round(v / p, 2), f"parcela 1/{p}"))
        if abs(liq - v) > 0.004:
            op.append((round(liq / p, 2), f"parcela 1/{p} do líquido"))
    return op


def cmd_conferir(a):
    with open(a.notas, encoding="utf-8-sig") as f:
        notas = list(csv.DictReader(f, delimiter=";"))
    with open(a.extrato, encoding="utf-8-sig") as f:
        extrato = list(csv.DictReader(f, delimiter=";"))
    conta, com_nf = "", {}
    if a.empresa:
        emp = json.load(open(a.empresa, encoding="utf-8"))
        conta = str(emp.get("conta_fornecedores") or "")
        # despesa lançada sem nota → conta de passivo quando a nota existe (ex.: 354 energia → 584)
        com_nf = {str(k): str(v) for k, v in (emp.get("contas_com_nf") or {}).items()}
        APELIDOS.update({normalizar(k).strip(): normalizar(v).strip() for k, v in (emp.get("apelidos_fornecedor") or {}).items()})
    for n in notas:
        n["_dt"] = datetime.strptime(n["entrada"] or n["emissao"], "%d/%m/%Y")
    alvo = [l for l in extrato if num(l["valor"]) < 0 and ((l.get("status") or "").upper() != "CONFIRMADO"
                                                         or (l.get("conta") or "") in com_nf
                                                         or "(PESSOA FISICA)" in l["descricao"])]
    if a.somente:
        alvo = [l for l in alvo if any(t.upper() in l["descricao"].upper() for t in a.somente)]
    res, usadas = {}, set()
    for l in alvo:
        v = -num(l["valor"])
        dt = datetime.strptime(l["data"], "%d/%m/%Y")
        janela = [n for n in notas if dt - timedelta(days=a.dias) <= n["_dt"] <= dt + timedelta(days=5)]
        nome_ext = nome_no_extrato(l["descricao"])
        por_nome = [n for n in janela if nome_ext and casa_nome(nome_ext, n["fornecedor"])]
        # CNPJ do favorecido (vindo do relatório de pagamentos/comprovante) casa com o CNPJ da nota,
        # mesmo quando o nome é diferente (ex.: PIX para o dono "GILMAR PEDRO..." = nota da "GP EXPRESS")
        cnpj_pag = re.search(r"\d{2}\.\d{3}\.\d{3}/\d{4}-\d{2}", l.get("documento") or "")
        if cnpj_pag:
            alvo_cnpj = re.sub(r"\D", "", cnpj_pag.group(0))
            por_nome += [n for n in janela if re.sub(r"\D", "", n["cnpj"]) == alvo_cnpj and n not in por_nome]

        def com_valor(lista):
            out = []
            for n in lista:
                for val, como in valores_da_nota(n):
                    if abs(val - v) < 0.015:
                        out.append((n, como))
                        break
            return out

        ok = com_valor(por_nome)
        if ok:
            ok.sort(key=lambda x: (x[1] != "valor da nota" and x[1] != "líquido das retenções", -x[0]["_dt"].timestamp()))
            res[l["id"]] = ("NOME + VALOR", ok[0][0], ok[0][1], [])
        elif por_nome:
            res[l["id"]] = ("SÓ NOME", por_nome[-1], "valor não bate com nenhuma nota ou parcela", por_nome)
        elif not nome_ext or a.valor_sem_nome:
            cands = [(n, c) for n, c in com_valor(janela) if c in ("valor da nota", "líquido das retenções")]
            if not cands:  # parcela de boleto parcelado (só se for a única nota possível)
                cands = com_valor(janela)
            chaves = {(n["cnpj"], n["nota"]) for n, _ in cands}
            if len(chaves) == 1:
                res[l["id"]] = ("SÓ VALOR", cands[0][0], cands[0][1], [])
            elif len(chaves) > 1:
                res[l["id"]] = ("VÁRIAS NOTAS", cands[0][0], f"{len(chaves)} notas com esse valor", [n for n, _ in cands])

    grupos = {"NOME + VALOR": [], "SÓ VALOR": [], "SÓ NOME": [], "VÁRIAS NOTAS": []}
    for l in alvo:
        if l["id"] in res:
            grupos[res[l["id"]][0]].append(l)
    sem = [l for l in alvo if l["id"] not in res]
    for g, itens in grupos.items():
        print(f"\n=== {g}: {len(itens)} ===")
        for l in itens:
            _, n, como, outros = res[l["id"]]
            print(f"  {l['data']} {brl(-num(l['valor'])):>10} {l['descricao'][:34]:34} → NF {n['nota']} "
                  f"{n['fornecedor'][:32]} ({n['entrada']}, {brl(num(n['valor']))}; {como})")
            if g == "VÁRIAS NOTAS":
                for o in outros[1:4]:
                    print(f"{'':50}ou NF {o['nota']} {o['fornecedor'][:32]} ({o['entrada']})")
    print(f"\n=== SEM NOTA ENCONTRADA: {len(sem)} ===")
    for l in sem:
        print(f"  {l['data']} {brl(-num(l['valor'])):>10} {l['descricao'][:60]}")
    print(f"\nResumo: {len(alvo)} pagamento(s) analisados | nome+valor {len(grupos['NOME + VALOR'])} | "
          f"só valor {len(grupos['SÓ VALOR'])} | só nome {len(grupos['SÓ NOME'])} | "
          f"várias notas {len(grupos['VÁRIAS NOTAS'])} | sem nota {len(sem)}")

    if sem or grupos["SÓ NOME"] or grupos["VÁRIAS NOTAS"]:
        print("\n>>> Informar ao usuário os pagamentos SEM NOTA, SÓ NOME e VÁRIAS NOTAS para identificar junto "
              "(use também a planilha mensal de conciliação enviada com o extrato).")

    if a.aplicar:
        if not conta:
            raise SystemExit("Defina 'conta_fornecedores' no JSON da empresa (confirmar com a contadora).")
        saida = []
        for l in extrato:
            r = res.get(l["id"])
            if r and "(PESSOA FISICA)" in l["descricao"]:
                if r[0] == "NOME + VALOR":  # pessoa física com nota fiscal (MEI/autônomo com nota) → fornecedores
                    l = dict(l, conta=conta, status="CONFIRMADO",
                             regra=f"NF {r[1]['nota']} {r[1]['fornecedor']} (pessoa física com nota → fornecedores)")
            elif r and (l.get("conta") or "") in com_nf:
                if r[0] == "NOME + VALOR":
                    l = dict(l, conta=com_nf[l["conta"]], status="CONFIRMADO",
                             regra=f"NF {r[1]['nota']} {r[1]['fornecedor']} (com nota → conta {com_nf[l['conta']]})")
            elif r and r[0] in ("NOME + VALOR", "SÓ VALOR"):
                # nome + valor = nota identificada (CONFIRMADO); só valor = PROVÁVEL, vai para a lista de conferência
                status = "CONFIRMADO" if r[0] == "NOME + VALOR" else "PROVÁVEL"
                l = dict(l, conta=conta, status=status,
                         regra=f"NF {r[1]['nota']} {r[1]['fornecedor']} ({r[0]}; {r[2]})")
            saida.append(l)
        campos = list(extrato[0].keys()) + [c for c in ("conta", "regra", "status") if c not in extrato[0]]
        with open(a.aplicar, "w", encoding="utf-8-sig", newline="") as f:
            w = csv.DictWriter(f, fieldnames=campos, delimiter=";", extrasaction="ignore")
            w.writeheader()
            w.writerows(saida)
        print(f"Notas aplicadas em: {a.aplicar} (nome + valor = CONFIRMADO; só valor = PROVÁVEL)")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("ler")
    s.add_argument("arquivo")
    s.add_argument("-o", "--saida", required=True)
    s.add_argument("--acrescentar", action="store_true")
    s = sub.add_parser("conferir")
    s.add_argument("extrato")
    s.add_argument("-n", "--notas", required=True)
    s.add_argument("-e", "--empresa")
    s.add_argument("--aplicar")
    s.add_argument("--dias", type=int, default=150, help="janela de busca de notas antes do pagamento")
    s.add_argument("--somente", nargs="*", help="analisar só descrições com estes termos")
    s.add_argument("--valor-sem-nome", action="store_true", help="tentar só valor também quando há nome")
    a = ap.parse_args()
    return cmd_ler(a) if a.cmd == "ler" else cmd_conferir(a)


if __name__ == "__main__":
    main()
