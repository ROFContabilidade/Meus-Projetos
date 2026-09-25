#!/usr/bin/env python3
"""Lê o relatório "Extrato Mensal" da folha do Domínio (PDF) e gera o registro da folha.

Uma linha por pessoa, cálculo e competência: tipo (empregado/contribuinte/estagiário),
código, nome, CPF, situação, proventos, descontos, líquido e observação (férias,
demissão, afastamento). Serve de base para a conferência dos pagamentos no extrato.

Uso:
  ler      python folha_extrato_mensal.py ler Extrato_Mensal*.pdf -o empresas/60-folha.csv [--acrescentar]
           (--acrescentar junta ao CSV existente, substituindo competência+cálculo repetidos)
  conferir python folha_extrato_mensal.py conferir trabalho/classificado.csv -f empresas/60-folha.csv \
               -e empresas/60-empresa.json [--aplicar trabalho/classificado_folha.csv]
           Confere os pagamentos do extrato com a folha, pelo valor exato: salário (Folha Mensal da
           competência anterior), adiantamento, rescisão (rubrica LIQUIDO RESCISAO, que sai junto com a
           Folha Mensal) e pró-labore; acha pagamentos que somam dois valores da mesma pessoa.
           --aplicar grava o CSV com as contas de 'contas_folha' (status CONFIRMADO).

Requer: pip install pdfplumber (ou pypdf).
"""
import argparse
import csv
import json
import os
import re
import sys

CAMPOS = ["competencia", "calculo", "tipo", "codigo", "nome", "cpf", "situacao",
          "proventos", "descontos", "liquido", "liquido_rescisao", "observacao", "arquivo"]
RE_RESC = re.compile(r"LIQUIDO RESCISAO(?: ESTAGIARIO)?\s+[\d.,]+\s+([\d.,]+)D")
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
            r = RE_RESC.search(linha)
            if r and atual is not None and "proventos" not in atual:
                atual["liquido_rescisao"] = r.group(1)
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


CONTAS_FOLHA_PADRAO = {"salario": "", "adiantamento": "", "rescisao": "", "pro_labore": ""}


def mes_anterior(comp):
    m, y = int(comp[:2]), int(comp[3:])
    return f"{m - 1:02d}/{y}" if m > 1 else f"12/{y - 1}"


def itens_folha(folha, comp_pag):
    """Tudo que pode ser pago no mês comp_pag: salário da competência anterior, adiantamentos
    (do mês e atrasado do anterior), rescisões (anterior e do mês) e pró-labore."""
    ant = mes_anterior(comp_pag)
    itens = []
    for r in folha:
        c, calc = r["competencia"], r["calculo"]
        liq, resc = num(r.get("liquido")), num(r.get("liquido_rescisao"))
        if calc == "Folha Mensal" and c == ant and liq > 0:
            tipo = "pro_labore" if r["tipo"] == "contribuinte" else "salario"
            itens.append(dict(r, _v=liq, _tipo=tipo, _esperado=True))
        if calc == "Adiantamento" and c in (comp_pag, ant) and liq > 0:
            itens.append(dict(r, _v=liq, _tipo="adiantamento", _esperado=(c == comp_pag)))
        if calc == "Folha Mensal" and c in (comp_pag, ant) and resc > 0:
            itens.append(dict(r, _v=resc, _tipo="rescisao", _esperado=(c == comp_pag)))
    return itens


def primeiro_nome(nome):
    return " ".join(nome.split()[:2]).upper()


def cmd_conferir(a):
    with open(a.folha, encoding="utf-8-sig") as f:
        folha = list(csv.DictReader(f, delimiter=";"))
    with open(a.extrato, encoding="utf-8-sig") as f:
        extrato = list(csv.DictReader(f, delimiter=";"))
    contas = dict(CONTAS_FOLHA_PADRAO)
    if a.empresa:
        contas.update(json.load(open(a.empresa, encoding="utf-8")).get("contas_folha") or {})
    termos = [t.upper() for t in a.termos]
    nomes = {primeiro_nome(r["nome"]) for r in folha}
    pags = [l for l in extrato if num(l["valor"]) < 0 and (
        any(t in l["descricao"].upper() for t in termos) or any(n in l["descricao"].upper() for n in nomes))]
    if not pags:
        print("Nenhum pagamento de folha encontrado no extrato.")
        return
    comps = sorted({l["data"][3:] for l in pags})
    itens = []
    for c in comps:
        itens += itens_folha(folha, c)
    print("Meses de pagamento no extrato: " + ", ".join(comps))
    print("\n=== PAGAMENTOS DO EXTRATO x FOLHA ===")
    rotulo = {"salario": "Salário", "adiantamento": "Adiantamento", "rescisao": "Rescisão", "pro_labore": "Pró-labore"}
    resultado, sobra = {}, []

    def pref(l, it):
        """Prefere o tipo do calendário e a competência esperada: salário/pró-labore do mês anterior,
        adiantamento do próprio mês; valores atrasados só se não houver o esperado."""
        d, comp = int(l["data"][:2]), l["data"][3:]
        ordem = (["salario", "pro_labore"] if d <= 10 else ["adiantamento"] if 15 <= d <= 20 else ["rescisao"])
        comp_esperada = comp if it["_tipo"] in ("adiantamento", "rescisao") else mes_anterior(comp)
        return (0 if it["_tipo"] in ordem else 1, 0 if it["competencia"] == comp_esperada else 1)

    for l in pags:
        v = -num(l["valor"])
        cand = sorted([it for it in itens if abs(it["_v"] - v) < 0.005], key=lambda it: pref(l, it))
        comb = None
        if not cand:  # pagamento que soma dois valores da mesma pessoa (ex.: salário + adiantamento atrasado)
            for i, x in enumerate(itens):
                for y in itens[i + 1:]:
                    if x["cpf"] == y["cpf"] and abs(x["_v"] + y["_v"] - v) < 0.005:
                        comb = [x, y]
                        break
                if comb:
                    break
        partes = [cand[0]] if cand else comb
        if partes:
            for it in partes:
                itens.remove(it)
            resultado[l["id"]] = partes
            desc = " + ".join(f"{rotulo[it['_tipo']]} {it['competencia']} {brl(it['_v'])}"
                              f" → conta {contas.get(it['_tipo']) or '?'}" for it in partes)
            print(f"  OK  {l['data']} {brl(v):>10} = {partes[0]['nome'][:32]}: {desc}")
        else:
            sobra.append(l)
            pessoa = next((r for r in folha if primeiro_nome(r["nome"]) in l["descricao"].upper()), None)
            extra = ""
            if pessoa and pessoa["tipo"] == "contribuinte":
                extra = ("  <<< SÓCIO/CONTRIBUINTE: valor diferente do pró-labore líquido. O líquido vai para "
                         "pró-labore e a diferença é RETIRADA DE SÓCIO: avisar o usuário antes de lançar")
            print(f"  ??  {l['data']} {brl(v):>10} {l['descricao'][:40]}  SEM correspondente na folha{extra}")
    print("\n=== NA FOLHA, SEM PAGAMENTO NESTE EXTRATO ===")
    faltam = [it for it in itens if it["_esperado"]]
    for it in faltam:
        obs = "  (pró-labore: sócio pode não ter retirado)" if it["_tipo"] == "pro_labore" else ""
        print(f"  {rotulo[it['_tipo']]:12} {it['competencia']} {it['nome'][:35]:35} {brl(it['_v']):>10}{obs}")
    if not faltam:
        print("  Nenhum.")
    print(f"\nResumo: {len(resultado)} de {len(pags)} pagamentos conferidos; {len(sobra)} sem correspondente; "
          f"{len(faltam)} valor(es) da folha sem pagamento neste extrato.")

    if a.aplicar:
        faltando = sorted({it["_tipo"] for ps in resultado.values() for it in ps if not contas.get(it["_tipo"])})
        if faltando:
            raise SystemExit(f"Defina 'contas_folha' no JSON da empresa para: {', '.join(faltando)}")
        saida = []
        for l in extrato:
            partes = resultado.get(l["id"])
            if not partes:
                saida.append(l)
                continue
            for k, it in enumerate(partes, 1):
                n = dict(l)
                n["id"] = l["id"] if len(partes) == 1 else f"{l['id']}-{k}"
                n["valor"] = f"{-it['_v']:.2f}"
                n["conta"] = contas[it["_tipo"]]
                n["regra"] = f"Folha: {rotulo[it['_tipo']]} {it['competencia']} {it['nome']}"
                n["status"] = "CONFIRMADO"
                saida.append(n)
        campos = list(extrato[0].keys()) + [c for c in ("conta", "historico", "complemento", "regra", "status")
                                             if c not in extrato[0]]
        with open(a.aplicar, "w", encoding="utf-8-sig", newline="") as f:
            w = csv.DictWriter(f, fieldnames=campos, delimiter=";", extrasaction="ignore")
            w.writeheader()
            w.writerows(saida)
        print(f"Classificação da folha aplicada em: {a.aplicar}")


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
    s.add_argument("-e", "--empresa", help="JSON da empresa (contas_folha: salario, adiantamento, rescisao, pro_labore)")
    s.add_argument("--aplicar", help="grava um CSV classificado com as contas da folha (divide pagamentos somados)")
    s.add_argument("--termos", nargs="*", default=["SALARIO", "FOLHA", "PAGTO SAL", "PRO LABORE", "PRO-LABORE", "RESCIS"])
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
