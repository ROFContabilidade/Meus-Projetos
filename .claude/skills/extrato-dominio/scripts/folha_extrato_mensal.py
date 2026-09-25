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


CAMPOS_ENC = ["competencia", "calculo", "fgts", "fgts_rescisorio", "inss", "inss_alternativos", "irrf", "arquivo"]


def ler_encargos(caminho):
    """Resumo de cada competência: FGTS, FGTS rescisório, total do INSS e IRRF (base da guia do FGTS
    Digital e da DCTFWeb). O relatório traz o resumo do serviço e o da empresa; os valores do INSS
    podem diferir por centavos, por isso todos são guardados em inss_alternativos."""
    enc = {}
    for pagina in texto_pdf(caminho):
        if "Valor do FGTS" not in pagina:
            continue
        c = re.search(r"C[áa]lculo:\s*(.+?)\s{2,}", pagina)
        m = re.search(r"Compet[êe]ncia:\s*(\d{2}/\d{4})", pagina)
        if not (c and m):
            continue
        g = lambda rot: (re.search(rot + r":\s*([\d.,]+)", pagina) or [None, "0,00"])[1]
        k = (m.group(1), c.group(1).strip())
        e = enc.setdefault(k, {"competencia": k[0], "calculo": k[1], "inss_alternativos": "",
                               "arquivo": os.path.basename(caminho)})
        e["fgts"], e["fgts_rescisorio"], e["irrf"] = g("Valor do FGTS"), g("Valor FGTS Rescis[óo]rio"), g("Valor Total do IRRF")
        e["inss"] = g("Total INSS")  # o último resumo (empresa) prevalece
        alts = [x for x in e["inss_alternativos"].split("|") if x] + [e["inss"]]
        e["inss_alternativos"] = "|".join(dict.fromkeys(alts))
    return list(enc.values())


def caminho_encargos(folha_csv):
    base, ext = os.path.splitext(folha_csv)
    return f"{base}-encargos{ext or '.csv'}"


def brl(v):
    return f"{v:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


def num(s):
    s = (s or "0").strip()
    return round(float(s.replace(".", "").replace(",", ".")) if "," in s else float(s), 2)


CONTAS_FOLHA_PADRAO = {"salario": "", "adiantamento": "", "rescisao": "", "pro_labore": "",
                       "fgts": "", "inss": "", "irrf": "", "consignado": ""}


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


def itens_encargos(encargos, comp_pag):
    """Guias pagas no mês comp_pag, da competência anterior: FGTS Digital e DCTFWeb (INSS + IRRF numa guia só)."""
    ant = mes_anterior(comp_pag)
    opcoes = []
    for e in encargos:
        if e["competencia"] != ant or e["calculo"] != "Folha Mensal":
            continue
        fg, fr, ir = num(e.get("fgts")), num(e.get("fgts_rescisorio")), num(e.get("irrf"))
        base = {"competencia": ant, "cpf": "", "_esperado": True}
        if fg:
            opcoes.append([dict(base, nome="FGTS", _tipo="fgts", _v=fg)])
            if fr:
                opcoes.append([dict(base, nome="FGTS + rescisório", _tipo="fgts", _v=round(fg + fr, 2))])
        if fr:
            opcoes.append([dict(base, nome="FGTS rescisório", _tipo="fgts", _v=fr, _esperado=False)])
        for inss in dict.fromkeys(num(x) for x in (e.get("inss_alternativos") or e.get("inss") or "").split("|") if x):
            if inss and ir:
                opcoes.append([dict(base, nome="DCTFWeb", _tipo="inss", _v=inss),
                               dict(base, nome="DCTFWeb", _tipo="irrf", _v=ir)])
            if inss:
                opcoes.append([dict(base, nome="INSS", _tipo="inss", _v=inss)])
        if ir:
            opcoes.append([dict(base, nome="IRRF", _tipo="irrf", _v=ir, _esperado=False)])
    return opcoes


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
        print("Nenhum pagamento de pessoal encontrado no extrato.")
    comps = sorted({l["data"][3:] for l in extrato if num(l["valor"]) < 0})
    itens = []
    for c in comps:
        itens += itens_folha(folha, c)
    print("Meses de pagamento no extrato: " + ", ".join(comps))
    print("\n=== PAGAMENTOS DO EXTRATO x FOLHA ===")
    rotulo = {"salario": "Salário", "adiantamento": "Adiantamento", "rescisao": "Rescisão", "pro_labore": "Pró-labore",
              "fgts": "FGTS", "inss": "INSS (DCTFWeb)", "irrf": "IRRF s/ folha (DCTFWeb)",
              "consignado": "Consignado (guia do FGTS)"}
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
    # --- guias da folha: FGTS Digital e DCTFWeb (INSS + IRRF), sempre divididas por conta
    enc_csv = caminho_encargos(a.folha)
    guias_ok = []
    if os.path.exists(enc_csv):
        with open(enc_csv, encoding="utf-8-sig") as f:
            encargos = list(csv.DictReader(f, delimiter=";"))
        termos_g = [t.upper() for t in a.termos_guias]
        cand_pags = [l for l in extrato if num(l["valor"]) < 0 and l["id"] not in resultado
                     and any(t in l["descricao"].upper() for t in termos_g)]
        print("\n=== GUIAS DA FOLHA (FGTS / DCTFWeb) x EXTRATO ===")
        for c in comps or sorted({l["data"][3:] for l in cand_pags}):
            opcoes = itens_encargos(encargos, c)
            achou = set()
            for l in cand_pags:
                if l["id"] in resultado or l["data"][3:] != c:
                    continue
                v = -num(l["valor"])
                op = next((o for o in opcoes if o[0]["_tipo"] not in achou
                           and abs(sum(x["_v"] for x in o) - v) < 0.005), None)
                if op:
                    resultado[l["id"]] = op
                    achou.add(op[0]["_tipo"])
                    guias_ok.append(l)
                    desc = " + ".join(f"{x['_tipo'].upper()} {brl(x['_v'])} → conta {contas.get(x['_tipo']) or '?'}" for x in op)
                    print(f"  OK  {l['data']} {brl(v):>10} = {op[0]['nome']} {op[0]['competencia']}: {desc}")
            # guia do FGTS Digital com consignado (Crédito do Trabalhador): FGTS da folha + diferença no consignado
            fg_ops = [o for o in opcoes if o[0]["_tipo"] == "fgts" and o[0]["_esperado"]]
            if "fgts" not in achou and fg_ops and contas.get("consignado"):
                for l in cand_pags:
                    if l["id"] in resultado or l["data"][3:] != c:
                        continue
                    v = -num(l["valor"])
                    base = max(fg_ops, key=lambda o: o[0]["_v"])[0]
                    if base["_v"] < v <= base["_v"] * 2 and any(t in l["descricao"].upper() for t in ("FGTS", "CEF", "CAIXA", "PIX QR", "GFD")):
                        dif = round(v - base["_v"], 2)
                        op = [base, dict(base, nome="Consignado (FGTS Digital)", _tipo="consignado", _v=dif)]
                        resultado[l["id"]] = op
                        achou.add("fgts")
                        guias_ok.append(l)
                        print(f"  OK? {l['data']} {brl(v):>10} = FGTS {base['competencia']} {brl(base['_v'])} → conta "
                              f"{contas.get('fgts')} + consignado {brl(dif)} → conta {contas['consignado']} (conferir o valor do consignado)")
                        break
            for tipo, rot in (("fgts", "FGTS"), ("inss", "DCTFWeb/INSS")):
                if tipo not in achou and any(o[0]["_tipo"] == tipo and o[0]["_esperado"] for o in opcoes):
                    vals = sorted({brl(sum(x['_v'] for x in o)) for o in opcoes if o[0]["_tipo"] == tipo})
                    print(f"  ??  {rot} {mes_anterior(c)} não encontrado no extrato de {c} (valores possíveis: {', '.join(vals)})")
    else:
        print(f"\n(Sem {os.path.basename(enc_csv)}: rode o 'ler' de novo para registrar FGTS/INSS/IRRF.)")

    print("\n=== NA FOLHA, SEM PAGAMENTO NESTE EXTRATO ===")
    faltam = [it for it in itens if it["_esperado"]]
    for it in faltam:
        obs = "  (pró-labore: sócio pode não ter retirado)" if it["_tipo"] == "pro_labore" else ""
        print(f"  {rotulo[it['_tipo']]:12} {it['competencia']} {it['nome'][:35]:35} {brl(it['_v']):>10}{obs}")
    if not faltam:
        print("  Nenhum.")
    print(f"\nResumo: {len(resultado) - len(guias_ok)} de {len(pags)} pagamentos de pessoal conferidos; "
          f"{len(sobra)} sem correspondente; {len(faltam)} valor(es) da folha sem pagamento neste extrato; "
          f"{len(guias_ok)} guia(s) FGTS/DCTFWeb identificada(s).")

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
                n["regra"] = f"Folha: {rotulo[it['_tipo']]} {it['competencia']}" + (f" {it['nome']}" if it.get("cpf") else "")
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
    s.add_argument("--termos-guias", nargs="*",
                   default=["TRIB", "PIX QR", "FGTS", "DARF", "DCTF", "GPS", "INSS", "RECEITA", "CAIXA", "GRF", "GFD"])
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

    enc_novos = []
    for f in a.pdfs:
        enc_novos += ler_encargos(f)
    ch_enc = {(e["competencia"], e["calculo"]) for e in enc_novos}
    enc_path = caminho_encargos(a.saida)
    enc_antigos = []
    if a.acrescentar and os.path.exists(enc_path):
        with open(enc_path, encoding="utf-8-sig") as f:
            enc_antigos = [e for e in csv.DictReader(f, delimiter=";") if (e["competencia"], e["calculo"]) not in ch_enc]
    enc_todos = sorted(enc_antigos + enc_novos, key=lambda e: (e["competencia"][3:] + e["competencia"][:2], e["calculo"]))
    with open(enc_path, "w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=CAMPOS_ENC, delimiter=";", extrasaction="ignore")
        w.writeheader()
        w.writerows(enc_todos)

    print(f"{len(novos)} registro(s) lidos | total no arquivo: {len(todos)} -> {a.saida}")
    print(f"Encargos (FGTS/INSS/IRRF) de {len(enc_novos)} cálculo(s) -> {enc_path}")
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
