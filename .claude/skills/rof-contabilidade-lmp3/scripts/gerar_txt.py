"""Gera o TXT Domínio da LMP3 a partir do CSV de lançamentos do mês.

CSV (;  utf-8-sig): data;debito;credito;valor;historico;status[;grupo]
- Linhas com o mesmo `grupo` (não vazio) são UM movimento do banco com várias contrapartidas.
  Viram um lote de várias partidas, padrão ROF (validado em Ribeiro e GL Car):
    |6000|C||||  1 crédito (banco, total) e vários débitos  -> saída do banco dividida
    |6000|D||||  1 débito (banco, total) e vários créditos  -> entrada no banco dividida
  1ª linha 6100 = banco com o total; as seguintes = cada contrapartida.
- Linhas sem grupo: |6000|X|||| (um débito para um crédito).

Uso: python gerar_txt.py lancamentos_MM.csv saida.txt [--banco 8] [--hist-grupo "texto"]
"""
import csv, sys
from collections import OrderedDict

CNPJ = "22993076000106"


def br(v):
    return f"{v:.2f}".replace(".", ",")


def gerar(csv_in, txt_out, banco="8"):
    rows = list(csv.reader(open(csv_in, encoding="utf-8-sig"), delimiter=";"))[1:]
    lotes = OrderedDict()
    for i, r in enumerate(rows):
        g = r[6].strip() if len(r) > 6 else ""
        lotes.setdefault(g or f"_{i}", []).append(r)
    out = [f"|0000|{CNPJ}|"]
    for k, rs in lotes.items():
        if len(rs) == 1:
            d, de, cr, v, h = rs[0][:5]
            out += ["|6000|X||||", f"|6100|{d}|{de}|{cr}|{v}||REF. A {h[:190]}||||"]
            continue
        d = rs[0][0]
        val = lambda x: float(x.replace(",", "."))
        base = rs[0][4].split(" - ")[0]
        if all(r[2] == banco for r in rs):  # saída: 1 crédito no banco, vários débitos
            out += ["|6000|C||||", f"|6100|{d}||{banco}|{br(sum(val(r[3]) for r in rs))}||REF. A {base[:190]}||||"]
            out += [f"|6100|{d}|{r[1]}||{r[3]}||REF. A {r[4][:190]}||||" for r in rs]
        elif all(r[1] == banco for r in rs):  # entrada: 1 débito no banco, vários créditos
            out += ["|6000|D||||", f"|6100|{d}|{banco}||{br(sum(val(r[3]) for r in rs))}||REF. A {base[:190]}||||"]
            out += [f"|6100|{d}||{r[2]}|{r[3]}||REF. A {r[4][:190]}||||" for r in rs]
        else:
            raise SystemExit(f"grupo {k}: linhas não têm o banco {banco} do mesmo lado")
    with open(txt_out, "w", encoding="cp1252", newline="") as f:
        f.write("\r\n".join(out) + "\r\n")
    return len(lotes)


if __name__ == "__main__":
    a = sys.argv[1:]
    banco = a[a.index("--banco") + 1] if "--banco" in a else "8"
    print(gerar(a[0], a[1], banco), "lotes")
