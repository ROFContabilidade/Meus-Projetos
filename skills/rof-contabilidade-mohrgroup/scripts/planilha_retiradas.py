#!/usr/bin/env python3
"""Planilha de retiradas de sócio – LAYOUT APROVADO pela Rosangela em 21/11/2026. NÃO MUDAR O LAYOUT.

Uso: python3 planilha_retiradas.py dados.json saida.xlsx

Partes (sempre nesta ordem, uma aba por mês):
 1. Pagamentos ao sócio: data, banco, histórico, sócio, CPF, valor pago, pró-labore líquido (D 188),
    retirada de lucros (D conta do sócio), saldo de pró-labore a pagar após o PIX.
 2. Total por banco (todos os bancos da empresa, mesmo com zero).
 3. Pró-labore do mês (folha): bruto, INSS retido, líquido, pago no mês, em aberto na 188.
 4. Resumo para a EFD-Reinf R-4010: total pago − pró-labore líquido = lucros; teste dos R$ 50 mil
    (Lei 15.270/2025) e IRRF 10% sobre o excedente.
 + "Não entram" (o que ficou fora e por quê).
Regra: só pagamento ao CPF do próprio sócio. Em ordem de data, paga-se primeiro o pró-labore líquido;
o que passar é retirada de lucros. Totais em fórmula. Nunca começar texto com "=".

dados.json:
{"empresa":"NOME LTDA","cnpj":"00.000.000/0001-00","codigo":"1005","mes":9,"ano":2026,
 "conta_prolabore":"188","conta_inss":"191",
 "bancos":[{"nome":"Itaú (conta 6)","chave":"Itaú"},{"nome":"Sicredi 0725/07383-3","chave":"Sicredi"}],
 "socios":[{"nome":"SOCIO A","cpf":"000.000.000-00","conta":"539","prolabore_bruto":1621.00,"inss_pct":0.11}],
 "pagamentos":[{"data":"2026-09-10","banco":"Sicredi 0725/07383-3","historico":"PIX ...","socio":"SOCIO A","valor":3700.00}],
 "nota_bancos":"Itaú: nenhum pagamento a sócio no mês.",
 "nota_inss":"INSS 11% dos sócios recolhido na guia única (conta 191).",
 "nao_entram":["• PIX para a própria empresa ...","• PIX a familiar ... – despesa na 362."]}
O campo "banco" do pagamento deve começar com a "chave" do banco (usada no total por banco).
"""
import json, sys
from datetime import date
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side

MESES = ["", "janeiro", "fevereiro", "março", "abril", "maio", "junho", "julho", "agosto",
         "setembro", "outubro", "novembro", "dezembro"]
AZ = PatternFill("solid", fgColor="1F4E78"); CL = PatternFill("solid", fgColor="DDEBF7")
VD = PatternFill("solid", fgColor="E2EFDA"); W = Font(bold=True, color="FFFFFF"); B = Font(bold=True)
GR = Font(italic=True, color="666666"); th = Side(style="thin", color="999999")
BX = Border(top=th, bottom=th, left=th, right=th); MO = '#,##0.00;[Red]-#,##0.00;"-"'


def main(src, out):
    d = json.load(open(src, encoding="utf-8"))
    mes, ano = d["mes"], d["ano"]; cp = d.get("conta_prolabore", "188")
    wb = Workbook(); ws = wb.active; ws.title = f"{MESES[mes].capitalize()} {ano}"

    def hdr(r, cols):
        for i, c in enumerate(cols, 1):
            x = ws.cell(r, i, c); x.font = W; x.fill = AZ; x.border = BX
            x.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)

    def row(r, vals, fill=None, bold=False):
        for i, v in enumerate(vals, 1):
            x = ws.cell(r, i, v); x.border = BX
            if fill: x.fill = fill
            if bold: x.font = B
            if isinstance(v, (int, float)) or (isinstance(v, str) and v.startswith("=")): x.number_format = MO
            if isinstance(v, date): x.number_format = "DD/MM/YYYY"

    socios = d["socios"]; contas = " / ".join(f"{s['conta']} {s['nome'].split()[0].title()}" for s in socios)
    ws["A1"] = f"{d['empresa']} – CNPJ {d['cnpj']} – Empresa {d['codigo']}"; ws["A1"].font = Font(bold=True, size=13)
    ws["A2"] = f"Retiradas dos sócios – {MESES[mes]}/{ano} (pró-labore x retirada de lucros) – base para a EFD-Reinf R-4010"; ws["A2"].font = B
    ws["A3"] = (f"Regra: só entra pagamento feito ao CPF do próprio sócio. O pró-labore líquido do mês é pago primeiro "
                f"(conta {cp}); o que passa dele é retirada de lucros ({contas})."); ws["A3"].font = GR

    liq = {s["nome"]: round(s["prolabore_bruto"] - round(s["prolabore_bruto"] * s.get("inss_pct", 0.11), 2), 2) for s in socios}
    cpf = {s["nome"]: s["cpf"] for s in socios}
    pags = sorted(d.get("pagamentos", []), key=lambda p: p["data"])
    cs = "/".join(dict.fromkeys(x["conta"] for x in socios if any(q["socio"] == x["nome"] for q in pags))) or socios[0]["conta"]
    ws["A5"] = "1. PAGAMENTOS AO SÓCIO (extratos bancários)"; ws["A5"].font = B
    hdr(6, ["Data", "Banco", "Histórico do extrato", "Sócio", "CPF", "Valor pago", f"Pró-labore líquido (D {cp})",
            f"Retirada de lucros (D {cs})", "Saldo de pró-labore a pagar após o PIX"])
    r = 7; falta = dict(liq)
    for p in pags:
        s = p["socio"]; v = p["valor"]; pl = round(min(v, falta[s]), 2); falta[s] = round(falta[s] - pl, 2)
        y, m, dd = map(int, p["data"].split("-"))
        row(r, [date(y, m, dd), p["banco"], p["historico"], s, cpf[s], v, pl, round(v - pl, 2),
                f'={liq[s]}-SUMIF($D$7:D{r},D{r},$G$7:G{r})']); r += 1
    if not pags:
        row(r, ["", "", "Nenhum pagamento a sócio no mês", "", "", 0, 0, 0, ""]); r += 1
    tot = r; f0, f1 = 7, r - 1
    row(r, ["TOTAL", "", "", "", "", f"=SUM(F{f0}:F{f1})", f"=SUM(G{f0}:G{f1})", f"=SUM(H{f0}:H{f1})", ""], CL, True)
    if d.get("nota_bancos"): r += 1; ws.cell(r, 1, d["nota_bancos"]).font = GR

    r += 2; ws.cell(r, 1, "2. TOTAL POR BANCO").font = B; r += 1
    hdr(r, ["Banco", "", "", "", "", "Valor pago", "Pró-labore líquido", "Retirada de lucros", ""]); r += 1; b0 = r
    for b in d["bancos"]:
        k = b["chave"]
        row(r, [b["nome"], "", "", "", ""] + [f'=SUMIF($B${f0}:$B${f1},"{k}*",{c}${f0}:{c}${f1})' for c in "FGH"] + [""]); r += 1
    row(r, ["TOTAL", "", "", "", ""] + [f"=SUM({c}{b0}:{c}{r-1})" for c in "FGH"] + [""], CL, True)

    r += 3; ws.cell(r, 1, "3. PRÓ-LABORE DO MÊS (folha) – vai no eSocial/DCTFWeb, NÃO no R-4010").font = B; r += 1
    hdr(r, ["Sócio", "CPF", "", "Pró-labore bruto", f"INSS {round(socios[0].get('inss_pct', 0.11)*100)}% retido", "Pró-labore líquido", "Pago no mês", f"Em aberto na {cp}", ""]); r += 1; p0 = r
    for s in socios:
        n = s["nome"]
        row(r, [n, s["cpf"], "", s["prolabore_bruto"], f"=ROUND(D{r}*{s.get('inss_pct', 0.11)},2)", f"=D{r}-E{r}",
                f'=SUMIF($D${f0}:$D${f1},A{r},$G${f0}:$G${f1})', f"=F{r}-G{r}", ""]); r += 1
    row(r, ["TOTAL", "", ""] + [f"=SUM({c}{p0}:{c}{r-1})" for c in "DEFGH"] + [""], CL, True)
    if d.get("nota_inss"): r += 1; ws.cell(r, 1, d["nota_inss"]).font = GR

    r += 3; ws.cell(r, 1, "4. RESUMO PARA A EFD-REINF – R-4010 (lucros e dividendos, natureza 12001)").font = B; r += 1
    hdr(r, ["Sócio", "CPF", "", "Total pago no mês", "(-) Pró-labore líquido", "Retirada de lucros (R-4010)",
            "Acima de R$ 50 mil? (Lei 15.270/2025)", "IRRF 10% sobre o excedente", ""]); r += 1
    for s in socios:
        row(r, [s["nome"], s["cpf"], "", f'=SUMIF($D${f0}:$D${f1},A{r},$F${f0}:$F${f1})',
                f'=SUMIF($D${f0}:$D${f1},A{r},$G${f0}:$G${f1})', f"=D{r}-E{r}",
                f'=IF(F{r}>50000,"SIM","Não")', f"=MAX(0,F{r}-50000)*0.1", ""], VD, True); r += 1
    if d.get("nao_entram"):
        r += 1; ws.cell(r, 1, "Não entram (não são pagamento ao CPF do sócio):").font = B; r += 1
        for t in d["nao_entram"]: ws.cell(r, 1, t); r += 1
    for c, wd in zip("ABCDEFGHI", [12, 22, 40, 20, 16, 14, 18, 18, 16]): ws.column_dimensions[c].width = wd
    ws.row_dimensions[6].height = 45; ws.freeze_panes = "A7"
    ws.page_setup.orientation = "landscape"; ws.sheet_properties.pageSetUpPr.fitToPage = True
    ws.page_setup.fitToWidth = 1; ws.page_setup.fitToHeight = 0
    wb.save(out); print("ok:", out)


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
