#!/usr/bin/env python3
"""Mohr (1005): pagamentos a fornecedor entram na 506 só até o limite disponível; o excedente vai para a 470 (CMV).

Uso: python limite_506.py classificado.csv --limite 24754,62 [--com-nota "DELIZ;FOLINI;GUSTAVO KLEMTZ;LWSA;..."]
  --limite   saldo credor da 506 no início do mês + notas de entrada do mês + devoluções creditadas na 506
  --com-nota favorecidos com nota no fiscal: ficam sempre na 506
O excedente sai dos pagamentos SEM nota, do mais recente para o mais antigo; o último é dividido em lote C (506 + 470).
Regra validada por Rosangela em 19/11/2026. Grava o próprio CSV.
"""
import argparse, csv
from decimal import Decimal as D
from datetime import datetime

ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
ap.add_argument("csv"); ap.add_argument("--limite", required=True)
ap.add_argument("--com-nota", default="DELIZ;FOLINI;GUSTAVO KLEMTZ;LWSA;ROSANGELA DE OLIVEIRA;TABELIONATO")
a = ap.parse_args()
LIM = D(a.limite.replace(".", "").replace(",", ".")) if "," in a.limite else D(a.limite)
COM = [k.strip().upper() for k in a.com_nota.split(";") if k.strip()]
rows = list(csv.DictReader(open(a.csv, encoding="utf-8-sig"), delimiter=";"))
def p506(r):
    if r.get("partidas"):
        return sum(D(x.split("=")[1].replace(",", ".")) for x in r["partidas"].split("+") if x.startswith("506="))
    return -D(r["valor"]) if r["conta"] == "506" and D(r["valor"]) < 0 else D(0)
pool = [r for r in rows if p506(r) > 0]
exc = sum(p506(r) for r in pool) - LIM
print(f"pagamentos na 506: {sum(p506(r) for r in pool)} | limite: {LIM} | excedente para 470: {max(exc, 0)}")
sem = sorted([r for r in pool if not r.get("partidas") and not any(k in r["descricao"].upper() for k in COM)],
             key=lambda r: (datetime.strptime(r["data"], "%d/%m/%Y"), r.get("id", "")), reverse=True)
for r in sem:
    if exc <= 0: break
    v = -D(r["valor"])
    if v <= exc:
        r["conta"], r["nota"], exc = "470", "excedente ao saldo da 506 → CMV", exc - v
    else:
        r["partidas"] = f"506={str(v - exc).replace('.', ',')}+470={str(exc).replace('.', ',')}"
        r["nota"], exc = "parte até o limite da 506, resto CMV", D(0)
    print("  ->", r["data"], r["valor"], r["descricao"][:50], r["conta"], r.get("partidas", ""))
if exc > 0: print(f"ATENÇÃO: sobrou {exc} sem pagamento sem nota para reclassificar")
w = csv.DictWriter(open(a.csv, "w", encoding="utf-8-sig", newline=""), fieldnames=list(rows[0].keys()), delimiter=";", extrasaction="ignore")
w.writeheader(); w.writerows(rows)
