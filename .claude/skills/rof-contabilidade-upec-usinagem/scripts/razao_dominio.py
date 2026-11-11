#!/usr/bin/env python3
"""Razão do Domínio (XLS ou CSV) como MODELO de lançamentos: aprende "favorecido → conta" da conta do banco.

  python razao_dominio.py aprender Razao.xls --conta-banco 8 [-e empresas/<empresa>.json] \
      [-o trabalho/regras_razao.json] [--csv trabalho/razao_lancamentos.csv]

Saída:
  - padrões do banco: descrição normalizada → contrapartida (quantidade, total, % de consistência);
  - lançamentos com várias partidas (contrapartida em branco no razão: guia dividida, multa/juros...);
  - regras sugeridas (JSON) para colar em "regras" da empresa: status CONFIRMADO quando o padrão se
    repetiu ≥ 2 vezes sempre na mesma conta; PROVÁVEL quando apareceu 1 vez; conflitos ficam de fora
    e são listados para perguntar.
O razão só é modelo se foi conferido: o que contrariar o padrão ROF ou decisões já registradas na
empresa deve ser perguntado, não copiado.
"""
import argparse
import csv
import json
import os
import re
import sys
import unicodedata
from collections import Counter, defaultdict
from datetime import date, timedelta

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from plano_contas import linhas_planilha  # noqa: E402

PREFIXOS = r"(SISPAG FORNECEDORES|SISPAG TRIBUTOS|SISPAG SALARIOS|SISPAG PIX QR-CODE|SISPAG|PIX ENVIADO|" \
           r"BOLETO PAGO|RECEBIMENTO PIX TRANSF|RECEBIMENTO SISPAG|RECEBIMENTO REDE|RECEBIMENTO MOV TIT COB|" \
           r"RECEBIMENTO|TED ENVIADA|TED|DOC|DA|PAGTO|PAG)"
VAZIAS = {"DO", "DA", "DE", "DOS", "DAS", "E", "SA", "S", "A", "LTDA", "ME", "EPP", "CIA", "COM", "IND"}
GENERICOS = {"RECEBIMENTO PIX TRANSF", "RECEBIMENTO MOV TIT COB", "SISPAG SALARIOS"}


def normalizar(t):
    t = unicodedata.normalize("NFKD", t or "").encode("ascii", "ignore").decode().upper()
    return re.sub(r"\s+", " ", t).strip()


def num(v):
    v = str(v or "").strip()
    if "," in v:
        v = v.replace(".", "").replace(",", ".")
    try:
        return float(v)
    except ValueError:
        return 0.0


def ler_razao(caminho):
    linhas, conta = [], None
    for r in linhas_planilha(caminho):
        if len(r) > 2 and r[0] == "Conta:":
            conta = (r[1], r[2], next((c for c in r[3:] if c), ""))
            continue
        if conta and r and re.fullmatch(r"\d{5}(\.\d+)?", r[0]) and len(r) > 9:
            d = date(1899, 12, 30) + timedelta(days=int(float(r[0])))
            linhas.append({"conta": conta[0], "classificacao": conta[1], "nome": conta[2],
                           "data": d.strftime("%d/%m/%Y"), "lote": r[1], "historico": r[2], "contrapartida": r[7],
                           "debito": num(r[8]), "credito": num(r[9])})
    return linhas


def chave(hist):
    """Descrição → padrão: tipo de movimento + começo do nome do favorecido (sem datas e números)."""
    h = normalizar(re.sub(r"^REF\.?\s*A\.?\s*", "", hist, flags=re.I))
    h = re.sub(r"\d{2}/\d{2}S?\b", " ", h)
    m = re.match(PREFIXOS + r"\s*(.*)", h)
    if not m:
        return re.sub(r"[\d*.\-/]+", " ", h).split(" - ")[0].strip()[:30], ""
    tipo, resto = m.group(1), m.group(2)
    if tipo in GENERICOS:
        return tipo, ""
    resto = re.sub(r"[\d*.\-/,]+", " ", resto)
    palavras = resto.split()
    # até achar uma palavra "de verdade" (4+ letras), no máximo 3 palavras; sem conectivos no fim
    nome = []
    for w in palavras[:3]:
        nome.append(w)
        if len(w) >= 4 and w not in VAZIAS:
            break
    if not any(len(w) >= 4 and w not in VAZIAS for w in nome):
        # nome só de iniciais (ex.: "W P", "A R"): usa o trecho inteiro e não vale para outros tipos de pagamento
        return (f"{tipo} {' '.join(palavras[:4])}".strip(), "")
    while nome and (nome[-1] in VAZIAS or len(nome[-1]) == 1) and len(nome) > 1:
        nome.pop()
    nome = " ".join(nome)
    return (f"{tipo} {nome}".strip(), nome)


def cmd_aprender(a):
    lanc = ler_razao(a.arquivo)
    if not lanc:
        raise SystemExit("Nenhum lançamento lido. O arquivo é o Razão do Domínio?")
    contas = {}
    if a.empresa:
        contas = json.load(open(a.empresa, encoding="utf-8")).get("contas") or {}
    if a.csv:
        with open(a.csv, "w", encoding="utf-8-sig", newline="") as f:
            w = csv.DictWriter(f, fieldnames=list(lanc[0]), delimiter=";")
            w.writeheader()
            w.writerows(lanc)
    banco = [l for l in lanc if l["conta"] == a.conta_banco]
    lotes = defaultdict(list)
    for l in lanc:
        lotes[l["lote"]].append(l)
    periodo = f"{min(l['data'][6:] + l['data'][3:5] + l['data'][:2] for l in lanc)}"
    print(f"{len(lanc)} lançamentos em {len({l['conta'] for l in lanc})} contas | banco {a.conta_banco}: {len(banco)} movimentos")

    padroes = defaultdict(lambda: {"contas": Counter(), "total": 0.0, "tipo": "", "exemplo": "", "nome": ""})
    multiplas = []
    for l in banco:
        tipo = "entrada" if l["debito"] > 0 else "saida"
        k, nome = chave(l["historico"])
        p = padroes[(tipo, k)]
        p["tipo"], p["exemplo"], p["nome"] = tipo, l["historico"], nome
        p["total"] += l["debito"] + l["credito"]
        if l["contrapartida"]:
            p["contas"][l["contrapartida"]] += 1
        else:
            partes = [x for x in lotes[l["lote"]] if x["conta"] != a.conta_banco]
            desc = " + ".join(f"{x['conta']} {contas.get(x['conta'], x['nome'])[:30]} {x['debito'] or x['credito']:.2f}"
                              for x in partes)
            p["contas"]["(várias)"] += 1
            multiplas.append((l["data"], l["historico"], l["debito"] or l["credito"], desc))

    regras, conflitos = [], []
    print("\n=== PADRÕES DO BANCO (descrição → contrapartida) ===")
    for (tipo, k), p in sorted(padroes.items(), key=lambda kv: -sum(kv[1]["contas"].values())):
        qtd = sum(p["contas"].values())
        conta, n = p["contas"].most_common(1)[0]
        pct = n / qtd
        lista = ", ".join(f"{c} {contas.get(c, '')[13:38]}({q})" for c, q in p["contas"].most_common(4))
        print(f"  {tipo[0].upper()} {k[:40]:40} {qtd:4} R$ {p['total']:>12,.2f} | {lista}")
        if conta == "(várias)":
            continue
        if pct < 1 or len(p["contas"]) > 1:
            conflitos.append((tipo, k, dict(p["contas"])))
            continue
        termos = [k]
        if p["nome"] and tipo == "saida" and re.match(r"(SISPAG FORNECEDORES|SISPAG|PIX ENVIADO|BOLETO PAGO|TED ENVIADA|PAGTO|PAG) ", k):
            # o mesmo favorecido pode ser pago por SISPAG, boleto ou PIX
            termos = [f"{t} {p['nome']}" for t in ("SISPAG FORNECEDORES", "BOLETO PAGO", "PIX ENVIADO", "TED ENVIADA",
                                                    "PIX QR CODE", "SISPAG TRIBUTOS")]
        regras.append({"nome": f"Razão modelo: {k.title()}", "tipo": tipo, "contem": termos,
                       "conta": conta, "status": "CONFIRMADO" if qtd >= 2 else "PROVÁVEL",
                       "origem": f"razão {os.path.basename(a.arquivo)} ({qtd}x)"})
    print(f"\n=== LANÇAMENTOS COM VÁRIAS PARTIDAS: {len(multiplas)} (criar regra manual ou dividir) ===")
    for d, h, v, desc in multiplas:
        print(f"  {d} {h[:45]:45} {v:>10,.2f} → {desc}")
    print(f"\n=== PADRÕES COM MAIS DE UMA CONTA: {len(conflitos)} (perguntar) ===")
    for tipo, k, cs in conflitos:
        print(f"  {tipo[0].upper()} {k[:40]:40} → " + ", ".join(f"{c} {contas.get(c, '')[13:35]}({q})" for c, q in cs.items()))
    # regras mais específicas (com nome) antes das genéricas
    regras.sort(key=lambda r: (-len(r["contem"][-1]), r["contem"][0]))
    with open(a.saida, "w", encoding="utf-8") as f:
        json.dump(regras, f, ensure_ascii=False, indent=1)
    print(f"\n{len(regras)} regra(s) sugerida(s) -> {a.saida} "
          f"({sum(r['status'] == 'CONFIRMADO' for r in regras)} CONFIRMADO, {sum(r['status'] == 'PROVÁVEL' for r in regras)} PROVÁVEL)")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("aprender")
    s.add_argument("arquivo")
    s.add_argument("--conta-banco", required=True)
    s.add_argument("-e", "--empresa")
    s.add_argument("-o", "--saida", default="regras_razao.json")
    s.add_argument("--csv", help="grava todos os lançamentos do razão em CSV")
    a = ap.parse_args()
    cmd_aprender(a)


if __name__ == "__main__":
    main()
