#!/usr/bin/env python3
"""Demonstrativos (XLS) e Resumo dos Impostos (PDF) do Domínio (ICMS, IPI, IRRF, CRF, ISS retido, INSS retido, PIS, COFINS,
IRPJ, CSLL) x pagamentos do extrato.

  ler      python impostos_dominio.py ler Demonst*.xls Resumo*.pdf -o empresas/<cod>-impostos.csv [--acrescentar]
           Uma linha por aba: imposto, competência, código da receita (quando está no nome da aba),
           valor a recolher e saldo credor.
  conferir python impostos_dominio.py conferir trabalho/classificado.csv -i empresas/<cod>-impostos.csv \
               [-e empresas/<empresa>.json] [--aplicar trabalho/classificado_impostos.csv]
           Procura no extrato, pelo valor exato, a guia de cada imposto com valor a recolher: mensais da
           competência anterior ao mês do pagamento; IRPJ/CSLL do trimestre anterior (cota única ou 3 quotas).
           --aplicar grava a conta de 'contas_impostos' do JSON: CONFIRMADO se a empresa tiver
           "contas_impostos_confirmadas": true (contadora já confirmou as contas); senão PROVÁVEL.

Guia com multa/juros não bate pelo valor: é listada como "não encontrada" para conferir com o comprovante.
"""
import argparse
import csv
import json
import os
import re
import sys
from datetime import date, timedelta

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from plano_contas import linhas_planilha  # noqa: E402

CAMPOS = ["imposto", "competencia", "periodo", "codigo_receita", "a_recolher", "saldo_credor", "aba", "arquivo"]
# rótulo da linha de resultado em cada demonstrativo
RE_RECOLHER = re.compile(r"^(ICMS a recolher|Saldo devedor de IPI|Saldo devedor do IRRF|Saldo devedor das Contribui"
                         r"|ISS Retido a recolher|Saldo devedor INSS Retido|Saldo devedor de IRPJ|Saldo devedor de Contribui"
                         r"|Saldo devedor de PIS|Saldo devedor da COFINS|Saldo devedor de COFINS|PIS a recolher"
                         r"|COFINS a recolher|Valor a recolher|Total a recolher)", re.I)
RE_CREDOR = re.compile(r"^Saldo credor .*(seguinte|próximo)", re.I)
NOMES = [("ICMS", "ICMS"), ("IPI", "IPI"), ("IRRF", "IRRF"), ("CRF", "CRF"), ("ISS RET", "ISS_RET"),
         ("INSS-RET", "INSS_RET"), ("INSS RET", "INSS_RET"), ("IRPJ", "IRPJ"), ("CSOC", "CSLL"), ("CSLL", "CSLL"),
         ("COFINS", "COFINS"), ("PIS", "PIS")]
CONTAS_PADRAO = {"ICMS": "172", "IPI": "171", "IRRF": "178", "CRF": "182", "ISS_RET": "183", "INSS_RET": "184",
                 "IRPJ": "176", "CSLL": "177", "PIS": "179", "COFINS": "180"}


def num(v):
    v = str(v or "").strip()
    if "," in v:
        v = v.replace(".", "").replace(",", ".")
    try:
        return round(float(v), 2)
    except ValueError:
        return 0.0


def brl(v):
    return f"{v:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


def comp_de_serial(v):
    try:
        d = date(1899, 12, 30) + timedelta(days=int(float(v)))
        return f"{d.month:02d}/{d.year}"
    except ValueError:
        m = re.search(r"(\d{2})/(\d{4})", v)
        return f"{m.group(1)}/{m.group(2)}" if m else ""


def ler_resumo_pdf(arq):
    """PDF "Resumo dos Impostos" do Domínio: impostos lançados (ICMS, IPI, IRRF, CRF, ISS...) e
    calculados (PIS, COFINS, IRPJ, CSLL), por competência."""
    try:
        import pdfplumber
        with pdfplumber.open(arq) as pdf:
            texto = "\n".join(p.extract_text(layout=True) or "" for p in pdf.pages)
    except ImportError:
        from pypdf import PdfReader
        texto = "\n".join(p.extract_text() or "" for p in PdfReader(arq).pages)
    regs, comp, secao = [], "", ""
    rotulos = [("CONTRIBUIÇÕES RETIDAS", "CRF"), ("ISS RETIDO", "ISS_RET"), ("INSS RETIDO", "INSS_RET"),
               ("ICMS", "ICMS"), ("IPI", "IPI"), ("IRRF", "IRRF"), ("IRPJ", "IRPJ"), ("CSLL", "CSLL"),
               ("CONTRIBUIÇÃO SOCIAL", "CSLL"), ("COFINS", "COFINS"), ("PIS", "PIS")]
    for linha in texto.splitlines():
        t = re.sub(r"\s+", " ", linha).strip()
        if "IMPOSTOS LANÇADOS" in t.upper():
            secao = "lancados"
        elif "IMPOSTOS CALCULADOS" in t.upper():
            secao = "calculados"
        m = re.match(r"Compet[êe]ncia: (\d{2}/\d{4})$", t)
        if m:
            comp = m.group(1)
            continue
        if not comp or not secao or t.upper().startswith("TOTAL"):
            continue
        imposto = next((k for n, k in rotulos if t.upper().startswith(n)), "")
        if not imposto:
            continue
        cod = re.search(r"- (\d{6})\b", t)
        nums = [num(x) for x in re.findall(r"-?[\d.]+,\d{2}", t)]
        if not nums:
            continue
        if secao == "lancados" and len(nums) >= 9:
            a_rec, credor = nums[6], nums[8]
        elif secao == "calculados" and len(nums) >= 10:
            a_rec, credor = nums[7], nums[9]
        else:  # PIS/COFINS em linha curta: valor do imposto a recolher
            a_rec, credor = nums[0], 0.0
        per = "T" if imposto in ("IRPJ", "CSLL") else "M"
        regs.append({"imposto": imposto, "competencia": comp, "periodo": per,
                     "codigo_receita": f"{cod.group(1)[:4]}-{cod.group(1)[4:]}" if cod else "",
                     "a_recolher": f"{a_rec:.2f}", "saldo_credor": f"{credor:.2f}",
                     "aba": f"Resumo dos impostos ({secao})", "arquivo": os.path.basename(arq)})
    return regs


def cmd_ler(a):
    regs = []
    for arq in a.arquivos:
        if arq.lower().endswith(".pdf"):
            regs += ler_resumo_pdf(arq)
            continue
        atual = None
        for row in linhas_planilha(arq):
            cel = [c for c in row if c != ""]
            if not cel:
                continue
            if cel[0] == "#ABA":
                aba = cel[1]
                up = aba.upper()
                imposto = next((k for n, k in NOMES if n in up), "")
                per = "T" if re.search(r"\(\d\s*T\)", aba) else "M"
                cod = re.search(r"\b(\d{6})\b", aba)
                atual = {"imposto": imposto, "competencia": "", "periodo": per,
                         "codigo_receita": f"{cod.group(1)[:4]}-{cod.group(1)[4:]}" if cod else "",
                         "a_recolher": "", "saldo_credor": "", "aba": aba, "arquivo": os.path.basename(arq)}
                regs.append(atual)
                continue
            if atual is None:
                continue
            if cel[0].startswith("Competência") and len(cel) > 1 and not atual["competencia"]:
                atual["competencia"] = comp_de_serial(cel[1])
            elif RE_RECOLHER.match(cel[0]) and len(cel) > 1:
                atual["a_recolher"] = f"{num(cel[-1]):.2f}"
            elif RE_CREDOR.match(cel[0]) and len(cel) > 1:
                atual["saldo_credor"] = f"{num(cel[-1]):.2f}"
    regs = [r for r in regs if r["imposto"]]
    unicos = {}
    for r in regs:  # o mesmo imposto pode vir no demonstrativo (XLS) e no resumo (PDF): fica o último lido
        antigo = unicos.get((r["imposto"], r["competencia"]))
        if antigo and antigo.get("codigo_receita") and not r.get("codigo_receita"):
            r["codigo_receita"] = antigo["codigo_receita"]  # o código da receita vem no nome da aba do XLS
        unicos[(r["imposto"], r["competencia"])] = r
    regs = list(unicos.values())
    antigos = []
    if a.acrescentar and os.path.exists(a.saida):
        ch = {(r["imposto"], r["competencia"]) for r in regs}
        with open(a.saida, encoding="utf-8-sig") as f:
            antigos = [r for r in csv.DictReader(f, delimiter=";")
                       if (r["imposto"], r["competencia"]) not in ch]
    todos = sorted(antigos + regs, key=lambda r: (r["competencia"][3:] + r["competencia"][:2], r["imposto"]))
    with open(a.saida, "w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=CAMPOS, delimiter=";", extrasaction="ignore")
        w.writeheader()
        w.writerows(todos)
    print(f"{len(regs)} demonstrativo(s) lido(s) -> {a.saida}")
    print("Imposto  | Competência | Código   | A recolher | Saldo credor")
    for r in regs:
        print(f"  {r['imposto']:8} {r['competencia']} {r['periodo']} {r['codigo_receita']:9} "
              f"{brl(num(r['a_recolher'])):>10} {brl(num(r['saldo_credor'])):>10}")
    faltam = {"PIS", "COFINS"} - {r["imposto"] for r in regs}
    if faltam:
        print(f"AVISO: não vieram demonstrativos de {', '.join(sorted(faltam))}.")


def mes_anterior(comp):
    m, y = int(comp[:2]), int(comp[3:])
    return f"{m - 1:02d}/{y}" if m > 1 else f"12/{y - 1}"


def trimestre_anterior(comp):
    m, y = int(comp[:2]), int(comp[3:])
    fim = ((m - 1) // 3) * 3  # último mês do trimestre anterior
    return f"{fim:02d}/{y}" if fim else f"12/{y - 1}"


def cmd_conferir(a):
    with open(a.impostos, encoding="utf-8-sig") as f:
        imp = [r for r in csv.DictReader(f, delimiter=";") if num(r["a_recolher"]) > 0]
    with open(a.extrato, encoding="utf-8-sig") as f:
        extrato = list(csv.DictReader(f, delimiter=";"))
    contas, confirmadas = dict(CONTAS_PADRAO), False
    if a.empresa:
        emp = json.load(open(a.empresa, encoding="utf-8"))
        contas.update(emp.get("contas_impostos") or {})
        confirmadas = bool(emp.get("contas_impostos_confirmadas"))  # contadora confirmou as contas desta empresa
    termos = [t.upper() for t in a.termos]
    pags = [l for l in extrato if num(l["valor"]) < 0 and (l.get("status") or "").upper() != "CONFIRMADO"
            and any(t in l["descricao"].upper() for t in termos)]
    res, usados = {}, set()
    print("=== GUIAS x EXTRATO ===")
    for l in pags:
        v, comp = -num(l["valor"]), l["data"][3:]
        opcoes = []
        for r in imp:
            k = (r["imposto"], r["competencia"], r["codigo_receita"])
            if k in usados:
                continue
            if r["periodo"] == "M" and r["competencia"] == mes_anterior(comp):
                opcoes.append((r, num(r["a_recolher"]), "cota única"))
            if r["periodo"] == "T" and r["competencia"] in (trimestre_anterior(comp), mes_anterior(comp)):
                total = num(r["a_recolher"])
                opcoes += [(r, total, "cota única"), (r, round(total / 3, 2), "1 de 3 quotas")]
        achou = next(((r, como) for r, val, como in opcoes if abs(val - v) < 0.005), None)
        if achou:
            r, como = achou
            if como == "cota única":
                usados.add((r["imposto"], r["competencia"], r["codigo_receita"]))
            res[l["id"]] = r
            print(f"  OK  {l['data']} {brl(v):>10} = {r['imposto']} {r['competencia']} {r['codigo_receita']} ({como}) "
                  f"→ conta {contas.get(r['imposto'], '?')}")
    sem = [l for l in pags if l["id"] not in res]
    print(f"\n=== GUIAS DO EXTRATO SEM DEMONSTRATIVO: {len(sem)} ===")
    for l in sem:
        print(f"  {l['data']} {brl(-num(l['valor'])):>10} {l['descricao'][:50]}")
    comps = {mes_anterior(l["data"][3:]) for l in pags}
    abertos = [r for r in imp if r["periodo"] == "M" and r["competencia"] in comps
               and (r["imposto"], r["competencia"], r["codigo_receita"]) not in usados
               and not any(x is r for x in res.values())]
    print(f"\n=== IMPOSTOS A RECOLHER SEM PAGAMENTO NESTE EXTRATO: {len(abertos)} ===")
    for r in abertos:
        print(f"  {r['imposto']:8} {r['competencia']} {r['codigo_receita']:9} {brl(num(r['a_recolher'])):>10}")
    print(f"\nResumo: {len(res)} de {len(pags)} guias identificadas.")
    if a.aplicar:
        saida = []
        for l in extrato:
            r = res.get(l["id"])
            if r:
                l = dict(l, conta=contas.get(r["imposto"], ""), status="CONFIRMADO" if confirmadas else "PROVÁVEL",
                         regra=f"Imposto: {r['imposto']} {r['competencia']} {r['codigo_receita']} (demonstrativo)")
            saida.append(l)
        campos = list(extrato[0].keys()) + [c for c in ("conta", "regra", "status") if c not in extrato[0]]
        with open(a.aplicar, "w", encoding="utf-8-sig", newline="") as f:
            w = csv.DictWriter(f, fieldnames=campos, delimiter=";", extrasaction="ignore")
            w.writeheader()
            w.writerows(saida)
        print(f"Guias aplicadas em: {a.aplicar} (status {'CONFIRMADO' if confirmadas else 'PROVÁVEL: contas ainda não confirmadas'})")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("ler")
    s.add_argument("arquivos", nargs="+")
    s.add_argument("-o", "--saida", required=True)
    s.add_argument("--acrescentar", action="store_true")
    s = sub.add_parser("conferir")
    s.add_argument("extrato")
    s.add_argument("-i", "--impostos", required=True)
    s.add_argument("-e", "--empresa")
    s.add_argument("--aplicar")
    s.add_argument("--termos", nargs="*", default=["TRIB", "DARF", "GUIA", "GR-PR", "GARE", "DAS", "ICMS", "RECEITA",
                                                   "SEFAZ", "FAZENDA", "IMPOSTO", "MUNICIPIO", "PREFEITURA"])
    a = ap.parse_args()
    return cmd_ler(a) if a.cmd == "ler" else cmd_conferir(a)


if __name__ == "__main__":
    main()
