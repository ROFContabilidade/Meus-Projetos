#!/usr/bin/env python3
"""Extrato Mensal da folha (Domínio Folha, PDF) -> folha.csv (competencia;nome;cpf;tipo;adiantamento;liquido;admissao).

Uso: python folha_csv.py "Extrato Mensal.pdf" -o folha.csv
"""
import argparse, csv, re
import pdfplumber


def num(s):
    return s.replace(".", "").replace(",", ".") if s else "0"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("pdf")
    ap.add_argument("-o", "--saida", required=True)
    a = ap.parse_args()
    with pdfplumber.open(a.pdf) as p:
        t = "\n".join((pg.extract_text() or "") for pg in p.pages)
    out = []
    for bloco in re.split(r"(?=Competência: )", t):
        c = re.match(r"Competência: (\S+)", bloco)
        if not c:
            continue
        for e in re.split(r"(?=Empr\.: |Contr: )", bloco)[1:]:
            m = re.match(r"(?:Empr\.:|Contr:) \d+(.+?) Situação: (.+?) CPF:([\d\.\-]+)", e)
            if not m:
                continue
            ad = re.search(r"DESC.ADIANT.SALARIAL [\d\.,]+ ([\d\.,]+)D", e)
            lq = re.search(r"Líquido: ([\d\.,]+)", e)
            adm = re.search(r"Adm: (\d\d/\d\d/\d{4})", e)
            tipo = "socio" if e.startswith("Contr") else "empregado"
            out.append([c.group(1), m.group(1).strip(), re.sub(r"\D", "", m.group(3)), tipo,
                        num(ad.group(1) if ad and tipo == "empregado" else ""), num(lq.group(1) if lq else ""), adm.group(1) if adm else ""])
    with open(a.saida, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f, delimiter=";")
        w.writerow(["competencia", "nome", "cpf", "tipo", "adiantamento", "liquido", "admissao"])
        w.writerows(out)
    print(f"{len(out)} linhas -> {a.saida}")


if __name__ == "__main__":
    main()
