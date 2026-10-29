"""Gera a planilha do estudo 'Simples Nacional 2026 x 2027' e um resumo.json para o parecer em Word.

Uso:
  python estudo_simples.py --apuracao apuracao.json --compras compras.json --empresa "NOME" --cnpj 00.000.000/0001-00 \\
      --saida PLANILHA.xlsx --resumo resumo.json [--canal "Comissão do marketplace" --canal-pct 0.16] \\
      [--despesas-pct 0.10 --usar-fretes] [--margem 0.10] [--aliq-regular 0.092]

Regras (ver SKILL.md): em 2027 a fatia de PIS+COFINS da receita monofásica deixa de ser zerada (vira CBS+IBS dentro do
DAS). Aumento do mês = receita monofásica x (alíquota de PIS + COFINS da seção tributada normal do mesmo mês)."""
import argparse, json
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.chart import BarChart, Reference
from openpyxl.chart.label import DataLabelList

ap = argparse.ArgumentParser()
for k in ['apuracao', 'compras', 'empresa', 'cnpj', 'saida', 'resumo']: ap.add_argument('--' + k, required=k != 'compras')
ap.add_argument('--canal', default='Comissão do marketplace / taxas de cartão'); ap.add_argument('--canal-pct', type=float, default=0.16)
ap.add_argument('--despesas', default='Despesas de venda'); ap.add_argument('--despesas-pct', type=float, default=0.05)
ap.add_argument('--usar-fretes', action='store_true', help='usa fretes CT-e reais como despesas de venda')
ap.add_argument('--mes-manual', action='append', default=[],
                help='mês sem relatório: "07/2026;rpa=70336.04;das=4803.72[;mono=68863.96]" (mono padrão = média do ano)')
ap.add_argument('--margem', type=float, default=0.10); ap.add_argument('--aliq-regular', type=float, default=0.092)
a = ap.parse_args()
ap_ = json.load(open(a.apuracao)); comp = json.load(open(a.compras)) if a.compras else {}
for mm in a.mes_manual:
    p_ = mm.split(';'); kv = dict(x.split('=') for x in p_[1:])
    rpa_ = float(kv['rpa']); pct_ = sum(x['receita_monofasica'] for x in ap_) / sum(x['rpa'] for x in ap_)
    mono_ = float(kv.get('mono', rpa_ * pct_))
    ap_.append(dict(competencia=p_[0], rpa=rpa_, das=float(kv['das']), receita_monofasica=mono_, receita_normal=rpa_ - mono_,
                    aliq_pis_cofins=None, estimado=True))
ap_.sort(key=lambda x: x['competencia'][3:] + x['competencia'][:2])
for i, m in enumerate(ap_):  # mês manual herda a alíquota de PIS+COFINS do mês anterior (ou seguinte)
    if m.get('aliq_pis_cofins') is None:
        viz = [x['aliq_pis_cofins'] for x in ap_[i - 1::-1] + ap_[i + 1:] if x.get('aliq_pis_cofins')]
        m['aliq_pis_cofins'] = viz[0] if viz else 0
ult = [m for m in ap_ if not m.get('estimado')][-1]
hist = [(m, v) for m, v in ult.get('historico_12m', [])]
meses_ano = {m['competencia']: m for m in ap_}
base12 = [(m, v) for m, v in hist if m not in meses_ano][-(12 - len(ap_)):] if len(ap_) < 12 else []
fat12 = base12 + [(m['competencia'], m['rpa']) for m in ap_][-12:]
AZ = '1F4E78'; H = Font(bold=True, color='FFFFFF'); HF = PatternFill('solid', fgColor=AZ); B = Font(bold=True)
Y = PatternFill('solid', fgColor='FFF2CC'); TOT = PatternFill('solid', fgColor='DEEAF6'); M = '#,##0.00'; P = '0.00%'
thin = Side(style='thin', color='BFBFBF'); BR = Border(left=thin, right=thin, top=thin, bottom=thin)
wb = Workbook()
def title(ws, t, s=None):
    ws['A1'] = t; ws['A1'].font = Font(bold=True, size=13, color=AZ)
    if s: ws['A2'] = s; ws['A2'].font = Font(italic=True, color='595959')
def hdr(ws, r, vals):
    for i, v in enumerate(vals, 1):
        c = ws.cell(r, i, v); c.font = H; c.fill = HF; c.border = BR; c.alignment = Alignment(wrap_text=True, horizontal='center', vertical='center')
def put(ws, r, c, v, fmt=None, bold=False, fill=None):
    x = ws.cell(r, c, v); x.border = BR
    if fmt: x.number_format = fmt
    if bold: x.font = B
    if fill: x.fill = fill
    return x
def W(ws, d):
    for k, v in d.items(): ws.column_dimensions[k].width = v

# 1 faturamento
f = wb.active; f.title = '1-Faturamento'
title(f, f'{a.empresa} – Faturamento usado no estudo', 'Fonte: relatórios do Domínio (Produtos monofásicos/subst. trib.) e anexo do PGDAS')
hdr(f, 4, ['Competência', 'Faturamento', 'Receita tributada normal', 'Receita monofásica', '% monofásica'])
r0 = 5
for i, (mes, v) in enumerate(fat12, r0):
    put(f, i, 1, mes); put(f, i, 2, v, M)
    if mes in meses_ano: put(f, i, 3, meses_ano[mes]['receita_normal'], M); put(f, i, 4, meses_ano[mes]['receita_monofasica'], M); put(f, i, 5, f'=D{i}/B{i}', P)
    else: [put(f, i, c, '–') for c in (3, 4, 5)]
rT = r0 + len(fat12); first_ano = r0 + len(base12)
put(f, rT, 1, 'Total 12 meses', bold=True, fill=TOT); put(f, rT, 2, f'=SUM(B{r0}:B{rT-1})', M, True, TOT)
put(f, rT + 1, 1, 'Total do ano analisado', bold=True, fill=TOT)
for c_, col in [(2, 'B'), (3, 'C'), (4, 'D')]: put(f, rT + 1, c_, f'=SUM({col}{first_ano}:{col}{rT-1})', M, True, TOT)
put(f, rT + 1, 5, f'=D{rT+1}/B{rT+1}', P, True, TOT)
W(f, dict(A=20, B=18, C=20, D=20, E=12))
# 2 DAS
d = wb.create_sheet('2-DAS 2026 x 2027')
title(d, 'DAS pago × DAS com as regras de 2027 (mesmo faturamento)', 'Em 2027 a fatia de PIS+COFINS (15,50%) vira CBS 15,33% + IBS 0,17% e deixa de ser zerada na receita monofásica')
hdr(d, 4, ['Competência', 'Faturamento', 'Receita monofásica', 'PIS+COFINS (% da receita)', 'DAS atual (pago)', 'DAS 2027 (estimado)', 'Aumento R$', 'Aumento %'])
for i, m in enumerate(ap_, 5):
    put(d, i, 1, m['competencia'] + (' (estimado)' if m.get('estimado') else '')); put(d, i, 2, m['rpa'], M); put(d, i, 3, m['receita_monofasica'], M)
    put(d, i, 4, (m['aliq_pis_cofins'] or 0) / 100, '0.0000%'); put(d, i, 5, m['das'], M)
    put(d, i, 6, f'=E{i}+C{i}*D{i}', M); put(d, i, 7, f'=F{i}-E{i}', M); put(d, i, 8, f'=G{i}/E{i}', P)
r = 5 + len(ap_)
put(d, r, 1, 'Total', bold=True, fill=TOT)
for c_, col in [(2, 'B'), (3, 'C'), (5, 'E'), (6, 'F'), (7, 'G')]: put(d, r, c_, f'=SUM({col}5:{col}{r-1})', M, True, TOT)
put(d, r, 8, f'=G{r}/E{r}', P, True, TOT)
a0 = r + 3; d.cell(a0, 1, 'Projeção anual – mesmo faturamento dos últimos 12 meses').font = Font(bold=True, color=AZ)
hdr(d, a0 + 1, ['Item', 'Valor'])
pr = [('Faturamento 12 meses', f"='1-Faturamento'!B{rT}", M), ('Carga atual do DAS (DAS pago ÷ faturamento do ano)', f'=E{r}/B{r}', P),
      ('% receita monofásica (média do ano)', f'=C{r}/B{r}', P), ('PIS+COFINS que passa a ser cobrado (último mês)', f'=D{r-1}', '0.0000%'),
      ('DAS anual atual', f'=B{a0+2}*B{a0+3}', M), ('DAS anual 2027', f'=B{a0+6}+B{a0+2}*B{a0+4}*B{a0+5}', M),
      ('Aumento anual', f'=B{a0+7}-B{a0+6}', M), ('Aumento médio mensal', f'=B{a0+8}/12', M), ('Aumento %', f'=B{a0+7}/B{a0+6}-1', P),
      ('Carga DAS 2027', f'=B{a0+7}/B{a0+2}', P)]
for i, (t, v, fm) in enumerate(pr, a0 + 2): put(d, i, 1, t); put(d, i, 2, v, fm, bold=t.startswith('Aumento'))
C26 = f"'2-DAS 2026 x 2027'!$B${a0+3}"; C27 = f"'2-DAS 2026 x 2027'!$B${a0+11}"; PC = f"'2-DAS 2026 x 2027'!$B${a0+5}"
W(d, dict(A=48, B=16, C=16, D=16, E=16, F=18, G=12, H=11))
ch = BarChart(); ch.type = 'col'; ch.title = 'DAS mensal: atual × 2027 estimado'
ch.add_data(Reference(d, min_col=5, max_col=6, min_row=4, max_row=r - 1), titles_from_data=True); ch.set_categories(Reference(d, min_col=1, min_row=5, max_row=r - 1))
for s_, col in zip(ch.series, ['2A78D6', 'EB6834']): s_.graphicalProperties.solidFill = col; s_.graphicalProperties.line.solidFill = col
ch.y_axis.numFmt = '#,##0'; ch.height = 9; ch.width = 22; ch.legend.position = 'b'; ch.x_axis.delete = False; ch.y_axis.delete = False
d.add_chart(ch, 'J4')
ch2 = BarChart(); ch2.type = 'col'; ch2.title = 'Aumento mensal do DAS (R$)'; ch2.legend = None
ch2.add_data(Reference(d, min_col=7, min_row=4, max_row=r - 1), titles_from_data=True); ch2.set_categories(Reference(d, min_col=1, min_row=5, max_row=r - 1))
ch2.series[0].graphicalProperties.solidFill = 'EB6834'; ch2.series[0].graphicalProperties.line.solidFill = 'EB6834'
ch2.dataLabels = DataLabelList(); ch2.dataLabels.showVal = True; ch2.dataLabels.showCatName = False; ch2.dataLabels.showSerName = False; ch2.dataLabels.showLegendKey = False
ch2.height = 8; ch2.width = 22; ch2.x_axis.delete = False; ch2.y_axis.delete = False; d.add_chart(ch2, 'J24')
# 3 compras
c = wb.create_sheet('3-Compras')
title(c, 'Compras no mesmo período', 'Acompanhamento de Entradas do Domínio: mercadorias (101-105) e fretes CT-e (300/301)')
hdr(c, 4, ['Competência', 'Mercadorias', 'Fretes (CT-e)', 'Faturamento', 'Mercadorias ÷ faturamento', 'Fretes ÷ faturamento'])
i = 4
for i, m in enumerate([x['competencia'] for x in ap_], 5):
    cc = comp.get(m, {}); put(c, i, 1, m); put(c, i, 2, cc.get('mercadorias', 0), M); put(c, i, 3, cc.get('fretes', 0), M)
    put(c, i, 4, meses_ano[m]['rpa'], M); put(c, i, 5, f'=B{i}/D{i}', P); put(c, i, 6, f'=C{i}/D{i}', P)
rc = i + 1; put(c, rc, 1, 'Total', bold=True, fill=TOT)
for k, col in [(2, 'B'), (3, 'C'), (4, 'D')]: put(c, rc, k, f'=SUM({col}5:{col}{rc-1})', M, True, TOT)
put(c, rc, 5, f'=B{rc}/D{rc}', P, True, TOT); put(c, rc, 6, f'=C{rc}/D{rc}', P, True, TOT)
CP = f"'3-Compras'!$E${rc}"; FP = f"'3-Compras'!$F${rc}"
W(c, dict(A=14, B=16, C=16, D=16, E=18, F=16))
# 4 preço
p = wb.create_sheet('4-Formação de preço')
title(p, 'Quanto aumentar o preço – 3 cenários', 'Amarelo = premissa editável. Preço = Custo ÷ (1 − soma dos percentuais sobre a venda)')
hdr(p, 4, ['Premissa', 'Valor', 'Origem'])
desp = f'={FP}' if a.usar_fretes else a.despesas_pct
pp = [('Custo do produto (exemplo)', 100, M, 'Exemplo'), ('Carga do DAS atual', f'={C26}', P, 'Aba 2'), ('Carga do DAS 2027', f'={C27}', P, 'Aba 2'),
      (a.canal + ' (% da venda)', a.canal_pct, P, 'ESTIMATIVA – ajustar'), (a.despesas + ' (% da venda)', desp, P, 'Fretes reais (aba 3)' if a.usar_fretes else 'ESTIMATIVA – ajustar'),
      ('Margem de lucro desejada', a.margem, P, 'ESTIMATIVA – definir com o cliente')]
for i, (t, v, fm, o) in enumerate(pp, 5):
    put(p, i, 1, t); x = put(p, i, 2, v, fm); put(p, i, 3, o)
    if isinstance(v, (int, float)): x.fill = Y
hdr(p, 13, ['Cenário', 'O que entra', '% atual', '% 2027', 'Preço atual', 'Preço 2027', 'Aumento R$', 'Aumento %'])
cen = [('1 – Só impostos', 'DAS + margem', '=$B$6+$B$10', '=$B$7+$B$10'),
       ('2 – Impostos + ' + a.canal.lower(), 'DAS + canal + margem', '=$B$6+$B$8+$B$10', '=$B$7+$B$8+$B$10'),
       ('3 – Impostos + canal + ' + a.despesas.lower(), 'DAS + canal + despesas + margem', '=$B$6+$B$8+$B$9+$B$10', '=$B$7+$B$8+$B$9+$B$10')]
for i, (n, o, x26, x27) in enumerate(cen, 14):
    put(p, i, 1, n, bold=True); put(p, i, 2, o); put(p, i, 3, x26, P); put(p, i, 4, x27, P)
    put(p, i, 5, f'=$B$5/(1-C{i})', M); put(p, i, 6, f'=$B$5/(1-D{i})', M); put(p, i, 7, f'=F{i}-E{i}', M); put(p, i, 8, f'=F{i}/E{i}-1', '0.00%', True)
W(p, dict(A=50, B=32, C=12, D=12, E=12, F=12, G=12, H=12))
ch3 = BarChart(); ch3.type = 'bar'; ch3.title = 'Reajuste necessário por cenário'; ch3.legend = None
ch3.add_data(Reference(p, min_col=8, min_row=13, max_row=16), titles_from_data=True); ch3.set_categories(Reference(p, min_col=1, min_row=14, max_row=16))
ch3.series[0].graphicalProperties.solidFill = '2A78D6'; ch3.dataLabels = DataLabelList(); ch3.dataLabels.showVal = True
ch3.dataLabels.showCatName = False; ch3.dataLabels.showSerName = False; ch3.dataLabels.showLegendKey = False; ch3.dataLabels.numFmt = '0.00%'
ch3.x_axis.delete = False; ch3.y_axis.delete = False; ch3.height = 7; ch3.width = 20; p.add_chart(ch3, 'A19')
# 5 híbrido
h = wb.create_sheet('5-Puro x Híbrido')
title(h, 'Simples puro × híbrido (IBS/CBS fora do DAS) – estimativa', f'Alíquota IBS + CBS no regime regular: {a.aliq_regular*100:.1f}% (premissa)')
hdr(h, 4, ['Item', 'Valor', 'Observação'])
hh = [('Faturamento 12 meses', f"='1-Faturamento'!B{rT}", M, ''), ('Alíquota IBS + CBS regime regular', a.aliq_regular, P, 'Premissa'),
      ('Compras de mercadorias ÷ faturamento', f'={CP}', P, 'Aba 3'), ('Fretes ÷ faturamento', f'={FP}', P, 'Crédito considerado (a favor do híbrido)'),
      ('IBS/CBS por fora (débito − crédito)', '=MAX(0,B6*(1-B7-B8))', P, 'Supõe crédito integral'),
      ('DAS sem a fatia CBS/IBS', f'={C27}-{PC}', P, 'Aproximação: carga 2027 menos a fatia de PIS+COFINS/CBS+IBS'),
      ('Carga total – híbrido', '=B9+B10', P, '=IF(B7+B8>1,"NÃO CONFIÁVEL: compras maiores que o faturamento declarado","")'),
      ('Carga total – Simples puro 2027', f'={C27}', P, ''), ('Diferença anual (híbrido − puro)', '=(B11-B12)*B5', M, 'Positivo = híbrido custa mais')]
for i, (t, v, fm, o) in enumerate(hh, 5):
    put(h, i, 1, t); x = put(h, i, 2, v, fm, bold=t.startswith('Diferença')); put(h, i, 3, o)
    if isinstance(v, float): x.fill = Y
W(h, dict(A=40, B=16, C=70))
wb.calculation.fullCalcOnLoad = True; wb.save(a.saida)
# resumo para o Word (valores calculados aqui, iguais às fórmulas)
R12 = sum(v for _, v in fat12); das = sum(m['das'] for m in ap_); rpa = sum(m['rpa'] for m in ap_); mono = sum(m['receita_monofasica'] for m in ap_)
pc = (ap_[-1]['aliq_pis_cofins'] or 0) / 100; carga26 = das / rpa; carga27 = carga26 + mono / rpa * pc
mens = [dict(mes=m['competencia'], estimado=bool(m.get('estimado')), rpa=m['rpa'], mono=m['receita_monofasica'], das=m['das'], das27=m['das'] + m['receita_monofasica'] * (m['aliq_pis_cofins'] or 0) / 100) for m in ap_]
compras = sum(comp.get(m['competencia'], {}).get('mercadorias', 0) for m in ap_); fretes = sum(comp.get(m['competencia'], {}).get('fretes', 0) for m in ap_)
desp_v = fretes / rpa if a.usar_fretes else a.despesas_pct
def reaj(outros): return (1 - outros - carga26) / (1 - outros - carga27) - 1
cred = (compras + fretes) / rpa; hib = max(0, a.aliq_regular * (1 - cred)) + (carga27 - pc)
res = dict(empresa=a.empresa, cnpj=a.cnpj, meses=mens, fat12=R12, carga26=carga26, carga27=carga27, das_ano=R12 * carga26, das27_ano=R12 * carga27,
           mono_pct=mono / rpa, reajustes=[reaj(a.margem), reaj(a.margem + a.canal_pct), reaj(a.margem + a.canal_pct + desp_v)],
           canal=a.canal, despesas=a.despesas, canal_pct=a.canal_pct, despesas_pct=desp_v, margem=a.margem, pis_cofins_pct=pc,
           meses_estimados=[m['competencia'] for m in ap_ if m.get('estimado')], compras_pct=compras / rpa, fretes_pct=fretes / rpa, aliq_regular=a.aliq_regular,
           hibrido=hib, hibrido_confiavel=cred <= 1, dif_hibrido=(hib - carga27) * R12)
json.dump(res, open(a.resumo, 'w'), ensure_ascii=False, indent=1)
print('ok', a.saida, '| aumento anual', round(res['das27_ano'] - res['das_ano'], 2), '| reajustes', [round(x * 100, 2) for x in res['reajustes']])
