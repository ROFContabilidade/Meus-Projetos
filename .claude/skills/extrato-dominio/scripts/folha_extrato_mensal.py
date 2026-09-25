#!/usr/bin/env python3
"""Lê o relatório "Extrato Mensal" da folha do Domínio (PDF) e gera o registro da folha.

Uma linha por pessoa, cálculo e competência: tipo (empregado/contribuinte/estagiário),
código, nome, CPF, situação, proventos, descontos, líquido e observação (férias,
demissão, afastamento). Serve de base para a conferência dos pagamentos no extrato.

Uso:
  ler      python folha_extrato_mensal.py ler Extrato_Mensal*.pdf -o empresas/60-folha.csv [--acrescentar]
           (--acrescentar junta ao CSV existente, substituindo competência+cálculo repetidos)
  conferir python folha_extrato_mensal.py conferir trabalho/classificado.csv -f empresas/60-folha.csv
           Confere os pagamentos de salário do extrato com os líquidos da folha:
           início do mês (dia 1-10) -> Folha Mensal da competência anterior;
           dia 15-20 -> Adiantamento da competência do mês.

Requer: pip install pdfplumber (ou pypdf).
"""
import argparse
import csv
import os
import re
import sys

CAMPOS = ["competencia", "calculo", "tipo", "codigo", "nome", "cpf", "situacao",
          "proventos", "descontos", "liquido", "observacao", "arquivo"]
RE_PESSOA = re.compile(r"^\s*(Empr|Contr|Estag)\.?:\s*(\d+)\s*(.+?)\s+Situa[çc][ãa]o:\s*(.+?)\s+CPF:\s*([\d.\-]+)")
RE_LIQ = re.compile(r"Proventos:\s*([\d.,]+)\s+Descontos:\s*([\d.,]+).*L[íi]quido:\s*(-?[\d.,]+)")
TIPOS = {"Empr": "empregado", "Contr": "contribuinte", "Estag": "estagiario"}


def texto_pdf(caminho):
    try:
        import pdfplumber
        with pdfplumber.open(caminho) as pdf:
            return [p.extract_text(layout=True) or "" for p in pdf.pages]
    except ImportError:
        from pypdf import PdfReader
        return [p.extract_text(extraction_mode="layout") or "" for p in PdfReader(caminho).pages]


def ler_extrato_mensal(caminho):
    regs, atual = [], None
    for pagina in texto_pdf(caminho):
        c = re.search(r"C[áa]lculo:\s*(.+?)\s{2,}", pagina)
        m = re.search(r"Compet[êe]ncia:\s*(\d{2}/\d{4})", pagina)
        calculo = c.group(1).strip() if c else ""
        comp = m.group(1) if m else ""
        for linha in pagina.splitlines():
            p = RE_PESSOA.match(linha)
            if p:
                atual = {"competencia": comp, "calculo": calculo, "tipo": TIPOS[p.group(1)],
                         "codigo": p.group(2), "nome": re.sub(r"\s+", " ", p.group(3)).strip(),
                         "situacao": re.sub(r"\s+", " ", p.group(4)).strip(), "cpf": p.group(5),
                         "observacao": "", "arquivo": os.path.basename(caminho)}
                regs.append(atual)
                continue
            l = RE_LIQ.search(linha)
            if l and atual is not None and "proventos" not in atual:
                atual["proventos"], atual["descontos"], atual["liquido"] = l.groups()
                continue
            t = re.sub(r"\s+", " ", linha).strip()
            if atual is not None and "proventos" in atual and re.match(
                    r"^(FERIAS DE|DEMITIDO EM|Novo afast|Afast|AFAST|RETORNO|LICEN)", t, re.I):
                atual["observacao"] = (atual["observacao"] + " | " + t).strip(" |")
            if t.startswith("Resumo por Rubricas"):
                atual = None
    return regs


def brl(v):
    return f"{v:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


def num(s):
    s = (s or "0").strip()
    return round(float(s.replace(".", "").replace(",", ".")) if "," in s else float(s), 2)


def cmd_conferir(a):
    with open(a.folha, encoding="utf-8-sig") as f:
        folha = list(csv.DictReader(f, delimiter=";"))
    with open(a.extrato, encoding="utf-8-sig") as f:
        extrato = list(csv.DictReader(f, delimiter=";"))
    termos = [t.upper() for t in a.termos]
    pags = [l for l in extrato if num(l["valor"]) < 0 and any(t in l["descricao"].upper() for t in termos)]
    if not pags:
        print("Nenhum pagamento de salário encontrado no extrato.")
        return
    # competências esperadas a partir das datas do extrato
    esperados = {}
    for l in pags:
        d, m, y = (int(x) for x in l["data"].split("/"))
        if d <= 10:
            m2, y2 = (m - 1, y) if m > 1 else (12, y - 1)
            esperados[(f"{m2:02d}/{y2}", "Folha Mensal")] = True
        elif 15 <= d <= 20:
            esperados[(f"{m:02d}/{y}", "Adiantamento")] = True
    abertos = [dict(r, _v=num(r.get("liquido"))) for r in folha
               if (r["competencia"], r["calculo"]) in esperados and num(r.get("liquido")) > 0]
    print("Folhas esperadas no extrato: " + ", ".join(f"{c} {k}" for c, k in esperados))
    print("\n=== PAGAMENTOS DO EXTRATO x FOLHA ===")
    sobra = []
    for l in pags:
        v = -num(l["valor"])
        d = int(l["data"][:2])
        calc = "Folha Mensal" if d <= 10 else "Adiantamento" if 15 <= d <= 20 else None
        cand = [r for r in abertos if abs(r["_v"] - v) < 0.005 and (calc is None or r["calculo"] == calc)] \
            or [r for r in abertos if abs(r["_v"] - v) < 0.005]
        if cand:
            r = cand[0]
            abertos.remove(r)
            print(f"  OK  {l['data']} {brl(v):>10} = {r['nome']} ({r['calculo']} {r['competencia']})")
        else:
            sobra.append(l)
            print(f"  ??  {l['data']} {brl(v):>10} {l['descricao'][:40]}  SEM correspondente na folha"
                  + ("" if calc else "  (fora do calendário)"))
    print("\n=== NA FOLHA, SEM PAGAMENTO IDENTIFICADO NESTE EXTRATO ===")
    for r in abertos:
        print(f"  {r['competencia']} {r['calculo']:12} {r['tipo']:12} {r['nome'][:35]:35} {brl(r['_v']):>10}")
    if not abertos:
        print("  Nenhum.")
    print("\n=== RESCISÕES / DEMISSÕES NAS COMPETÊNCIAS (líquido da rescisão é pago à parte) ===")
    comps = {c for c, _ in esperados} | {f"{int(p['data'][3:5]):02d}/{p['data'][6:]}" for p in pags}
    dem = [r for r in folha if r["competencia"] in comps and "DEMITIDO" in (r.get("observacao") or "").upper()]
    for r in {(r["nome"], r["observacao"]): r for r in dem}.values():
        print(f"  {r['competencia']} {r['nome'][:35]:35} {r['observacao'][:80]}")
    if not dem:
        print("  Nenhuma.")
    print(f"\nResumo: {len(pags) - len(sobra)} de {len(pags)} pagamentos conferidos; "
          f"{len(sobra)} sem correspondente; {len(abertos)} líquido(s) da folha sem pagamento neste extrato.")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("ler")
    s.add_argument("pdfs", nargs="+")
    s.add_argument("-o", "--saida", required=True)
    s.add_argument("--acrescentar", action="store_true")
    s = sub.add_parser("conferir")
    s.add_argument("extrato", help="CSV normalizado ou classificado do extrato")
    s.add_argument("-f", "--folha", required=True, help="CSV da folha gerado pelo 'ler'")
    s.add_argument("--termos", nargs="*", default=["SALARIO", "FOLHA", "PAGTO SAL", "PRO LABORE", "PRO-LABORE"])
    a = ap.parse_args()
    if a.cmd == "conferir":
        return cmd_conferir(a)

    novos = []
    for f in a.pdfs:
        novos += ler_extrato_mensal(f)
    chaves = {(r["competencia"], r["calculo"]) for r in novos}
    antigos = []
    if a.acrescentar and os.path.exists(a.saida):
        with open(a.saida, encoding="utf-8-sig") as f:
            antigos = [r for r in csv.DictReader(f, delimiter=";") if (r["competencia"], r["calculo"]) not in chaves]
    todos = antigos + novos
    todos.sort(key=lambda r: (r["competencia"][3:] + r["competencia"][:2], r["calculo"], r["tipo"], r["nome"]))
    with open(a.saida, "w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=CAMPOS, delimiter=";", extrasaction="ignore")
        w.writeheader()
        w.writerows(todos)

    print(f"{len(novos)} registro(s) lidos | total no arquivo: {len(todos)} -> {a.saida}")
    resumo = {}
    for r in novos:
        k = (r["competencia"], r["calculo"])
        v = float((r.get("liquido") or "0").replace(".", "").replace(",", "."))
        n, s = resumo.get(k, (0, 0.0))
        resumo[k] = (n + (1 if v else 0), s + v)
    print("Competência | Cálculo | pessoas com líquido | total líquido")
    for (comp, calc), (n, s) in sorted(resumo.items(), key=lambda kv: (kv[0][0][3:] + kv[0][0][:2], kv[0][1])):
        print(f"  {comp} | {calc} | {n} | {s:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
    sem = [r for r in novos if "liquido" not in r]
    if sem:
        print(f"AVISO: {len(sem)} pessoa(s) sem linha de líquido reconhecida: " + ", ".join(r["nome"] for r in sem[:5]))


if __name__ == "__main__":
    sys.exit(main())
