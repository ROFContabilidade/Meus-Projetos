#!/usr/bin/env python3
"""Retiradas da sócia para a EFD-Reinf (R-4010), a partir das planilhas Conferencia_Mtz_Fl_AAAA-MM.xlsx do rotina_mes.py.

Uso: python reinf_retiradas.py --saida DIR_DO_MOTOR --meses 10/2026,11/2026 -o Retiradas_Adriana_Reinf.xlsx

Critério (Rosangela, 21/11/2026): total pago à sócia pelas duas lojas no mês (Sicredi da matriz + Itaú da filial)
- pró-labore líquido do mês (188 na matriz; na filial é a parte que foi para a 544/espelho 188)
= retiradas (531); - devoluções da sócia à empresa = retirada líquida declarada na Reinf.
Os espelhos da matriz (banco 544) são ignorados para não contar o mesmo PIX duas vezes.
"""
import argparse, glob
import openpyxl
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill

SOCIA = "ADRIANA RODRIGUES"
BANCOS = (("34", "Matriz", "Sicredi - matriz (0001-93)"), ("118", "Filial", "Itaú - filial (0002-74)"))


def f2(x):
    return float(str(x).replace(",", "."))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--saida", required=True)
    ap.add_argument("--meses", required=True, help="MM/AAAA separados por vírgula")
    ap.add_argument("-o", "--arquivo", required=True)
    a = ap.parse_args()
    meses = [m.strip() for m in a.meses.split(",")]
    rows = []
    for emp, aba, banco in BANCOS:
        for comp in meses:
            iso = f"{comp[3:]}-{comp[:2]}"
            for f in glob.glob(f"{a.saida}/{iso}/Conferencia_*.xlsx"):
                for r in openpyxl.load_workbook(f, read_only=True)[aba].iter_rows(min_row=2, values_only=True):
                    if r[8] == "OMITIDO" or SOCIA not in (r[2] or "").upper() or str(r[1]) == "544":
                        continue
                    v = r[4]
                    parts = dict((p.split("=")[0], f2(p.split("=")[1])) for p in r[7].split("; ")) if r[7] else {(r[5] if v < 0 else r[6]): abs(v)}
                    pl = parts.get("188", 0) + (parts.get("544", 0) if emp == "118" else 0)
                    ret = parts.get("531", 0)
                    rows.append([comp, r[0], banco, "Pagamento à sócia" if v < 0 else "Devolução da sócia à empresa",
                                 abs(v), pl if v < 0 else 0, ret if v < 0 else 0, abs(v) if v > 0 else 0])
    rows.sort(key=lambda x: (x[0][3:], x[0][:2], x[1][6:], x[1][3:5], x[1][:2]))
    B = Font(bold=True); G = PatternFill("solid", fgColor="D9EAD3")
    wb = Workbook(); ws = wb.active; ws.title = "Retiradas"
    ws.append(["ADRIANA RODRIGUES DE PAULA - ADRIANA R. DE PAULA LTDA (matriz 0001-93 + filial 0002-74)"]); ws["A1"].font = B
    ws.append(["Pró-labore líquido do mês deduzido do total pago à sócia pelas duas lojas."]); ws.append([])
    ws.append(["Mês", "Data", "Banco", "Tipo", "Valor do PIX", "Pró-labore deduzido", "Retirada (lucro)", "Devolução"])
    for c in ws[4]: c.font = B
    res = []
    for comp in meses:
        L = [x for x in rows if x[0] == comp]
        for x in L: ws.append(x)
        pag = sum(x[4] for x in L if x[3].startswith("Pag")); pl = sum(x[5] for x in L)
        ret = sum(x[6] for x in L); dev = sum(x[7] for x in L)
        ws.append([f"Total {comp}", "", "", "", round(pag, 2), round(pl, 2), round(ret, 2), round(dev, 2)])
        for c in ws[ws.max_row]: c.font = B
        ws.append(["", "", "", "RETIRADA LÍQUIDA PARA A EFD-REINF (retirada − devoluções)", "", "", round(ret - dev, 2), ""])
        for c in ws[ws.max_row]: c.font = B; c.fill = G
        ws.append([]); res.append((comp, round(pag, 2), round(pl, 2), round(ret, 2), round(dev, 2), round(ret - dev, 2)))
    w2 = wb.create_sheet("Resumo Reinf")
    w2.append(["Mês", "Total pago à sócia", "(-) Pró-labore líquido", "= Retiradas", "(-) Devoluções", "= Retirada líquida (R-4010)"])
    for c in w2[1]: c.font = B
    for r in res: w2.append(list(r))
    for wsx in (ws, w2):
        for c, wd in zip("ABCDEFGH", (12, 12, 26, 52, 14, 18, 16, 12)): wsx.column_dimensions[c].width = wd
    wb.save(a.arquivo)
    for r in res: print(r)


if __name__ == "__main__":
    main()
