"""Gera o Simulador de Regime Tributario 2027 (Simples x Presumido x Real).
Uso: python gerar_simulador.py [saida.xlsx]
"""
import sys
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.comments import Comment
from openpyxl.chart import BarChart, Reference
from openpyxl.worksheet.datavalidation import DataValidation

OUT = sys.argv[1] if len(sys.argv) > 1 else "Simulador_Regime_Tributario_2027.xlsx"
F = "Arial"
BLUE = Font(name=F, color="0000FF", size=10)
BLACK = Font(name=F, size=10)
GREEN = Font(name=F, color="008000", size=10)
BOLD = Font(name=F, bold=True, size=10)
WH = Font(name=F, bold=True, color="FFFFFF", size=10)
TITLE = Font(name=F, bold=True, size=14, color="3B2417")
YEL = PatternFill("solid", fgColor="FFFF00")
HDR = PatternFill("solid", fgColor="3B2417")
SUB = PatternFill("solid", fgColor="F3E9DF")
thin = Side(style="thin", color="D9CBBD")
BOX = Border(top=thin, bottom=thin, left=thin, right=thin)
R = '#,##0;(#,##0);"-"'
P = '0.0%;(0.0%);"-"'
P2 = '0.00%;(0.00%);"-"'
WRAP = Alignment(wrap_text=True, vertical="top")

wb = Workbook()

def hdr(ws, row, labels, col=1):
    for i, t in enumerate(labels):
        c = ws.cell(row=row, column=col + i, value=t)
        c.font = WH; c.fill = HDR; c.alignment = Alignment(wrap_text=True, vertical="center"); c.border = BOX

def inp(c, v, fmt=None, note=None):
    c.value = v; c.font = BLUE; c.fill = YEL; c.border = BOX
    if fmt: c.number_format = fmt
    if note: c.comment = Comment(note, "Simulador")

def f(c, v, fmt=None, font=BLACK):
    c.value = v; c.font = font; c.border = BOX
    if fmt: c.number_format = fmt

# ------------------------------------------------------------------ LEIA-ME
ws = wb.active; ws.title = "LEIA-ME"
ws.column_dimensions["A"].width = 110
lines = [
    ("Simulador de Regime Tributário 2027 — Simples × Lucro Presumido × Lucro Real", TITLE),
    ("Modelo reutilizável: uma cópia deste arquivo por CNPJ.", BOLD),
    ("", BLACK),
    ("COMO USAR", BOLD),
    ("1. Aba 'Dados de Entrada': preencha só as células AMARELAS com texto AZUL (identificação, receita anual por linha, folha).", BLACK),
    ("2. Aba 'Compras e Despesas': valores anuais e o tipo de crédito de CBS/IBS de cada gasto.", BLACK),
    ("3. Aba 'Parâmetros': alíquotas e tabelas. Atualize a alíquota da CBS após a Resolução do Senado (prazo 15/12/2026).", BLACK),
    ("4. Aba 'Comparativo': resultado, ranking, alertas e gráfico. Aba 'Cálculos' mostra a memória de cálculo.", BLACK),
    ("5. Aba 'Checklist de Dados': o que buscamos sozinhos (certificado/procuração) e o que pedir ao cliente.", BLACK),
    ("Os valores que vêm preenchidos são EXEMPLO (cafeteria fictícia) para mostrar o formato — substitua pelos dados reais.", Font(name=F, bold=True, color="B3261E", size=10)),
    ("", BLACK),
    ("CORES", BOLD),
    ("Azul em fundo amarelo = dado a preencher · Preto = fórmula · Verde = vínculo com outra aba.", BLACK),
    ("", BLACK),
    ("PREMISSAS E SIMPLIFICAÇÕES (ler antes de apresentar ao cliente)", BOLD),
    ("• Ano de referência: 2027 (CBS no lugar de PIS/COFINS; IBS 0,1%; ICMS e ISS sem mudança; IPI zerado; Imposto Seletivo embutido no custo de compra).", BLACK),
    ("• A receita informada é o valor total recebido do cliente e é a mesma em todos os regimes; os tributos são tratados como custo da empresa.", BLACK),
    ("• Simples: alíquota efetiva calculada sobre a receita anual (como RBT12), por anexo (LC 123, Anexos I, II e III). CPP já incluída no DAS.", BLACK),
    ("  Linhas com ICMS-ST na compra excluem a parcela de ICMS do DAS. Não simula a opção de recolher IBS/CBS 'por fora' do Simples (avaliar à parte).", BLACK),
    ("• Presumido/Real: CBS/IBS não cumulativos — débito pelo tratamento da linha (zero / restaurante -40% / cheia) menos créditos das compras.", BLACK),
    ("  Saldo credor não é devolvido no cálculo (fica zero). Crédito presumido de produtor rural não considerado (conservador).", BLACK),
    ("• ICMS no regime normal: informe a CARGA EFETIVA por linha = (débito − crédito) ÷ receita. Mercadoria com ICMS-ST já pago: use 0%.", BLACK),
    ("• Contribuição patronal fora do Simples: 20% sobre salários e pró-labore + RAT ajustado + terceiros sobre salários. FGTS igual em todos (só informativo).", BLACK),
    ("• Lucro Real: lucro = receita − CBS/IBS − ICMS − ISS − compras e despesas − folha e encargos. Sem adições/exclusões do LALUR e sem prejuízo fiscal.", BLACK),
    ("• Presunção acima de R$ 5 milhões (LC 224/2025): parâmetro opcional, começa em 0% — confirmar antes de usar.", BLACK),
    ("• Lei 15.270/2025 (IRRF 10% sobre lucros acima de R$ 50 mil/mês por sócio) vale nos três regimes e não entra no comparativo.", BLACK),
    ("", BLACK),
    ("PRAZOS", BOLD),
    ("• Sair do Simples por opção com efeito em 1º/01: comunicar no Portal do Simples até o último dia útil de janeiro.", BLACK),
    ("• Lucro Presumido: opção pelo pagamento do 1º DARF de IRPJ do ano. Lucro Real: estimativa mensal (1º DARF em fevereiro) ou trimestral.", BLACK),
    ("", BLACK),
    ("BASE LEGAL: LC 123/2006 · LC 214/2025 (arts. 273–276, Anexo I) · TCU, cálculo da CBS 2027 · MP 1.399/2026 (Imposto Seletivo) · Lei 8.212/1991.", Font(name=F, italic=True, size=9, color="5D6472")),
]
for i, (t, ft) in enumerate(lines, 1):
    c = ws.cell(row=i, column=1, value=t); c.font = ft; c.alignment = Alignment(wrap_text=True)

# ------------------------------------------------------------------ PARAMETROS
pa = wb.create_sheet("Parâmetros")
pa.column_dimensions["A"].width = 48; pa.column_dimensions["B"].width = 14; pa.column_dimensions["C"].width = 70
pa["A1"] = "Parâmetros 2027"; pa["A1"].font = TITLE
hdr(pa, 3, ["Parâmetro", "Valor", "Fonte / observação"])
params = [
    ("Alíquota CBS 2027", 0.112, P2, "TCU: referência 11,3% (out/2026) − 0,1 p.p. em 2027. ATUALIZAR com a Resolução do Senado (até 15/12/2026)."),
    ("Alíquota IBS 2027 (estadual + municipal)", 0.001, P2, "LC 214/2025: 0,1% em 2027 e 2028."),
    ("Redução bares e restaurantes", 0.40, P, "LC 214/2025, art. 275. Não vale para bebida alcoólica (art. 273, §2º, III)."),
    ("IRPJ", 0.15, P, "Alíquota básica."),
    ("Adicional de IRPJ", 0.10, P, "Sobre a base que exceder o limite anual abaixo."),
    ("Limite anual do adicional (R$)", 240000, R, "R$ 20 mil/mês."),
    ("CSLL", 0.09, P, ""),
    ("INSS patronal (salários e pró-labore)", 0.20, P, "Lei 8.212/1991, art. 22, I e III."),
    ("RAT ajustado (RAT × FAP)", 0.02, P2, "Conferir o CNAE e o FAP da empresa."),
    ("Terceiros (Sistema S, salário-educação etc.)", 0.058, P2, "Conferir FPAS da empresa."),
    ("FGTS", 0.08, P, "Igual em todos os regimes — só informativo."),
    ("Alíquota de ISS (município)", 0.05, P, "Conferir a alíquota do serviço no município (ex.: cursos, eventos)."),
    ("Crédito do aluguel pago a PJ (fração da alíquota cheia)", 0.30, P, "Locação de imóvel: redução de 70% na LC 214/2025 → crédito de 30% da alíquota."),
    ("Crédito sobre compra de fornecedor do Simples (% da compra)", 0.02, P2, "Estimativa: o fornecedor do Simples transfere só a CBS/IBS que paga no DAS. Ajustar."),
    ("Acréscimo de presunção acima de R$ 5 mi (LC 224/2025)", 0.0, P, "Opcional — confirmar a regra; usar 10% se aplicável."),
    ("Limite de receita do Simples (R$)", 4800000, R, "LC 123, art. 3º. Soma das empresas com os mesmos sócios (art. 3º, §4º, III)."),
    ("Sublimite estadual ICMS/ISS (R$)", 3600000, R, "Acima dele, ICMS e ISS são pagos fora do DAS."),
]
for i, (a, v, fmt, note) in enumerate(params, 4):
    pa.cell(row=i, column=1, value=a).font = BLACK
    inp(pa.cell(row=i, column=2), v, fmt)
    pa.cell(row=i, column=3, value=note).font = Font(name=F, size=9, color="5D6472")
# names: B4 CBS, B5 IBS, B6 red rest, B7 IRPJ, B8 adic, B9 lim, B10 CSLL, B11 INSS, B12 RAT, B13 terc, B14 FGTS, B15 ISS, B16 cred aluguel, B17 cred simples, B18 presun extra, B19 lim simples, B20 sublim

pa["A23"] = "Tabelas do Simples Nacional (LC 123/2006, redação da LC 155/2016)"; pa["A23"].font = BOLD
hdr(pa, 24, ["Faixa", "Receita de (R$)", "Receita até (R$)", "Anexo I alíq.", "Anexo I dedução", "Anexo I % ICMS",
              "Anexo II alíq.", "Anexo II dedução", "Anexo II % ICMS", "Anexo III alíq.", "Anexo III dedução"])
tab = [
    (1, 0, 180000, .04, 0, .34, .045, 0, .32, .06, 0),
    (2, 180000.01, 360000, .073, 5940, .34, .078, 5940, .32, .112, 9360),
    (3, 360000.01, 720000, .095, 13860, .335, .10, 13860, .32, .135, 17640),
    (4, 720000.01, 1800000, .107, 22500, .335, .112, 22500, .32, .16, 35640),
    (5, 1800000.01, 3600000, .143, 87300, .335, .147, 85500, .32, .21, 125640),
    (6, 3600000.01, 4800000, .19, 378000, 0, .30, 720000, 0, .33, 648000),
]
fmts = [None, R, R, P, R, P, P, R, P, P, R]
for r, row in enumerate(tab, 25):
    for cidx, v in enumerate(row, 1):
        c = pa.cell(row=r, column=cidx)
        inp(c, v, fmts[cidx - 1])
for col in "DEFGHIJK":
    pa.column_dimensions[col].width = 12
pa["A32"] = "Faixa 6: ICMS/ISS fora do DAS (acima do sublimite). Repartição do ICMS conforme Anexos I e II da LC 123."
pa["A32"].font = Font(name=F, size=9, color="5D6472")

# ------------------------------------------------------------------ DADOS DE ENTRADA
de = wb.create_sheet("Dados de Entrada")
widths = {"A": 46, "B": 15, "C": 10, "D": 11, "E": 11, "F": 13, "G": 11, "H": 13, "I": 9, "J": 44}
for k, v in widths.items(): de.column_dimensions[k].width = v
de["A1"] = "Dados de entrada da empresa"; de["A1"].font = TITLE
ident = [("Razão social", "EMPRESA EXEMPLO LTDA"), ("CNPJ", "00.000.000/0001-00"),
         ("Regime atual", "Simples Nacional"),
         ("Receita anual das outras empresas dos mesmos sócios (R$)", 0)]
for i, (a, v) in enumerate(ident, 3):
    de.cell(row=i, column=1, value=a).font = BOLD
    inp(de.cell(row=i, column=2), v, R if isinstance(v, (int, float)) else None)
de["B6"].comment = Comment("Some aqui o faturamento anual das outras empresas com os mesmos sócios (limite global do Simples).", "Simulador")

de["A8"] = "Receita anual por linha (R$) — projeção 2027"; de["A8"].font = BOLD
hdr(de, 9, ["Linha de receita", "Receita anual (R$)", "Anexo Simples", "Presunção IRPJ", "Presunção CSLL",
            "CBS/IBS 2027", "ICMS-ST na compra?", "Carga efetiva ICMS (regime normal)", "Tem ISS?", "Observação"])
REV = [
    ("Café em pacote — varejo (NCM 09.01 / 2101.1)", 120000, "I", .08, .12, "ZERO", "N", .07, "N", "Cesta básica: alíquota zero."),
    ("Atacado de café (NCM 09.01 / 2101.1)", 300000, "I", .08, .12, "ZERO", "N", .07, "N", "Alíquota zero."),
    ("Café servido, comida e bebida não alcoólica preparada", 700000, "I", .08, .12, "REST", "N", .04, "N", "Regime de bares e restaurantes (−40%)."),
    ("Bebida alcoólica (servida ou revenda)", 150000, "I", .08, .12, "CHEIA", "S", 0, "N", "Fora da redução; IS embutido no custo."),
    ("Cerveja, água e refrigerante (revenda)", 80000, "I", .08, .12, "CHEIA", "S", 0, "N", "Fim do monofásico de PIS/COFINS."),
    ("Outras mercadorias de revenda (doces, acessórios)", 30000, "I", .08, .12, "CHEIA", "N", .07, "N", ""),
    ("Café torrado pela própria empresa (indústria)", 0, "II", .08, .12, "ZERO", "N", .07, "N", "Só se torrar: Anexo II no Simples."),
    ("Eventos — alimentação preparada", 60000, "I", .08, .12, "REST", "N", .04, "N", ""),
    ("Eventos — espaço / organização", 20000, "III", .32, .32, "CHEIA", "N", 0, "S", "Serviço: ISS."),
    ("Cursos e treinamentos", 20000, "III", .32, .32, "CHEIA", "N", 0, "S", "Serviço: ISS."),
    ("Aluguel de máquinas (bens móveis)", 20000, "III", .32, .32, "CHEIA", "N", 0, "N", "Locação de bem móvel: sem ISS."),
]
R0 = 10
for i, row in enumerate(REV):
    r = R0 + i
    de.cell(row=r, column=1, value=row[0]).font = BLACK
    de.cell(row=r, column=1).border = BOX
    fm = [R, None, P, P, None, None, P, None]
    for j, v in enumerate(row[1:9]):
        inp(de.cell(row=r, column=2 + j), v, fm[j])
    de.cell(row=r, column=10, value=row[9]).font = Font(name=F, size=9, color="5D6472")
RL = R0 + len(REV) - 1  # last revenue row (20)
RT = RL + 1
de.cell(row=RT, column=1, value="TOTAL").font = BOLD
f(de.cell(row=RT, column=2), f"=SUM(B{R0}:B{RL})", R, BOLD)
dv1 = DataValidation(type="list", formula1='"I,II,III"', allow_blank=True); de.add_data_validation(dv1); dv1.add(f"C{R0}:C{RL}")
dv2 = DataValidation(type="list", formula1='"ZERO,REST,CHEIA"', allow_blank=True); de.add_data_validation(dv2); dv2.add(f"F{R0}:F{RL}")
dv3 = DataValidation(type="list", formula1='"S,N"', allow_blank=True); de.add_data_validation(dv3); dv3.add(f"G{R0}:G{RL}"); dv3.add(f"I{R0}:I{RL}")
de["F9"].comment = Comment("ZERO = cesta básica (alíquota zero)\nREST = bares e restaurantes (−40%)\nCHEIA = alíquota cheia", "Simulador")
de["H9"].comment = Comment("Carga efetiva = (ICMS débito − crédito) ÷ receita da linha. Com ICMS-ST já pago na compra, use 0%.", "Simulador")

FR = RT + 3
de.cell(row=FR - 1, column=1, value="Folha de pagamento — valores anuais (R$)").font = BOLD
folha = [("Salários CLT (com 13º e férias)", 300000), ("Pró-labore dos sócios", 60000), ("Nº de empregados (informativo)", 8)]
for i, (a, v) in enumerate(folha):
    de.cell(row=FR + i, column=1, value=a).font = BLACK
    inp(de.cell(row=FR + i, column=2), v, R)
SAL, PRO = f"'Dados de Entrada'!$B${FR}", f"'Dados de Entrada'!$B${FR+1}"

# ------------------------------------------------------------------ COMPRAS E DESPESAS
cd = wb.create_sheet("Compras e Despesas")
for k, v in {"A": 50, "B": 15, "C": 14, "D": 12, "E": 16, "F": 48}.items(): cd.column_dimensions[k].width = v
cd["A1"] = "Compras e despesas anuais (R$) — créditos de CBS/IBS"; cd["A1"].font = TITLE
cd["A2"] = "Tipo de crédito: ZERO = sem crédito · CHEIA = alíquota cheia · ALUGUEL = aluguel pago a PJ (30%) · SIMPLES = fornecedor do Simples · MANUAL = % informado na coluna D"
cd["A2"].font = Font(name=F, size=9, color="5D6472")
hdr(cd, 4, ["Descrição", "Valor anual (R$)", "Tipo de crédito", "% manual", "Crédito CBS/IBS (R$)", "Observação"])
EXP = [
    ("Café comprado (produtor rural ou fornecedor)", 250000, "ZERO", "Cesta básica — sem crédito. Produtor PF: lembrar do Funrural."),
    ("Leite e açúcar", 60000, "ZERO", "Cesta básica — sem crédito."),
    ("Bebidas alcoólicas compradas", 70000, "CHEIA", "CBS destacada na nota do fornecedor."),
    ("Cerveja, água e refrigerante comprados", 45000, "CHEIA", ""),
    ("Outros insumos e embalagens (chocolate, xaropes, copos)", 80000, "CHEIA", ""),
    ("Compras de fornecedores do Simples", 40000, "SIMPLES", "Crédito limitado ao que o fornecedor paga no DAS."),
    ("Energia elétrica", 36000, "CHEIA", ""),
    ("Aluguel pago a pessoa jurídica", 0, "ALUGUEL", ""),
    ("Aluguel pago a pessoa física", 72000, "ZERO", "PF não contribuinte: sem crédito."),
    ("Serviços de PJ (manutenção, internet, marketing)", 30000, "CHEIA", ""),
    ("Taxas de cartão e tarifas bancárias", 25000, "ZERO", "Serviço financeiro: regime específico — conservador."),
    ("Outras despesas sem crédito", 20000, "ZERO", ""),
    ("Depreciação do ano (só para o Lucro Real)", 15000, "ZERO", "Não é compra do ano; só reduz o lucro real."),
]
E0 = 5
for i, (a, v, t, o) in enumerate(EXP):
    r = E0 + i
    cd.cell(row=r, column=1, value=a).font = BLACK; cd.cell(row=r, column=1).border = BOX
    inp(cd.cell(row=r, column=2), v, R)
    inp(cd.cell(row=r, column=3), t)
    inp(cd.cell(row=r, column=4), 0, P2)
    f(cd.cell(row=r, column=5),
      f"=IF(C{r}=\"CHEIA\",B{r}*(Parâmetros!$B$4+Parâmetros!$B$5),"
      f"IF(C{r}=\"ALUGUEL\",B{r}*(Parâmetros!$B$4+Parâmetros!$B$5)*Parâmetros!$B$16,"
      f"IF(C{r}=\"SIMPLES\",B{r}*Parâmetros!$B$17,IF(C{r}=\"MANUAL\",B{r}*D{r},0))))", R)
    cd.cell(row=r, column=6, value=o).font = Font(name=F, size=9, color="5D6472")
EL = E0 + len(EXP) - 1
ET = EL + 1
cd.cell(row=ET, column=1, value="TOTAL").font = BOLD
f(cd.cell(row=ET, column=2), f"=SUM(B{E0}:B{EL})", R, BOLD)
f(cd.cell(row=ET, column=5), f"=SUM(E{E0}:E{EL})", R, BOLD)
dv4 = DataValidation(type="list", formula1='"ZERO,CHEIA,ALUGUEL,SIMPLES,MANUAL"', allow_blank=True)
cd.add_data_validation(dv4); dv4.add(f"C{E0}:C{EL}")

# ------------------------------------------------------------------ CALCULOS
ca = wb.create_sheet("Cálculos")
for k, v in {"A": 46, "B": 14, "C": 9, "D": 11, "E": 12, "F": 13, "G": 13, "H": 13, "I": 13, "J": 13, "K": 13}.items():
    ca.column_dimensions[k].width = v
ca["A1"] = "Memória de cálculo"; ca["A1"].font = TITLE
ca["A3"] = "Receita anual total (base para a faixa do Simples)"; ca["A3"].font = BOLD
f(ca["B3"], f"='Dados de Entrada'!B{RT}", R, GREEN)
ca["A4"] = "Faixa do Simples"; f(ca["B4"], "=MATCH(B3,Parâmetros!$B$25:$B$30,1)", "0")
ca["A5"] = "Alíquota efetiva Anexo I"
f(ca["B5"], "=IF(B3=0,0,(B3*INDEX(Parâmetros!$D$25:$D$30,B4)-INDEX(Parâmetros!$E$25:$E$30,B4))/B3)", P2)
ca["A6"] = "Alíquota efetiva Anexo II"
f(ca["B6"], "=IF(B3=0,0,(B3*INDEX(Parâmetros!$G$25:$G$30,B4)-INDEX(Parâmetros!$H$25:$H$30,B4))/B3)", P2)
ca["A7"] = "Alíquota efetiva Anexo III"
f(ca["B7"], "=IF(B3=0,0,(B3*INDEX(Parâmetros!$J$25:$J$30,B4)-INDEX(Parâmetros!$K$25:$K$30,B4))/B3)", P2)
ca["A8"] = "Parcela de ICMS no DAS — Anexo I / Anexo II"
f(ca["B8"], "=INDEX(Parâmetros!$F$25:$F$30,B4)", P)
f(ca["C8"], "=INDEX(Parâmetros!$I$25:$I$30,B4)", P)

hdr(ca, 10, ["Linha de receita", "Receita", "Anexo", "DAS Simples", "Base IRPJ (presumida)", "Base CSLL (presumida)",
             "Débito CBS/IBS", "ICMS (regime normal)", "ISS (regime normal)"])
C0 = 11
for i in range(len(REV)):
    r = C0 + i; s = R0 + i
    f(ca.cell(row=r, column=1), f"='Dados de Entrada'!A{s}", None, GREEN)
    f(ca.cell(row=r, column=2), f"='Dados de Entrada'!B{s}", R, GREEN)
    f(ca.cell(row=r, column=3), f"='Dados de Entrada'!C{s}", None, GREEN)
    f(ca.cell(row=r, column=4),
      f"=B{r}*IF(C{r}=\"II\",$B$6,IF(C{r}=\"III\",$B$7,$B$5))"
      f"*(1-IF('Dados de Entrada'!G{s}=\"S\",IF(C{r}=\"II\",$C$8,IF(C{r}=\"III\",0,$B$8)),0))", R)
    f(ca.cell(row=r, column=5), f"=B{r}*'Dados de Entrada'!D{s}", R)
    f(ca.cell(row=r, column=6), f"=B{r}*'Dados de Entrada'!E{s}", R)
    f(ca.cell(row=r, column=7),
      f"=B{r}*(Parâmetros!$B$4+Parâmetros!$B$5)*IF('Dados de Entrada'!F{s}=\"ZERO\",0,"
      f"IF('Dados de Entrada'!F{s}=\"REST\",1-Parâmetros!$B$6,1))", R)
    f(ca.cell(row=r, column=8), f"=B{r}*'Dados de Entrada'!H{s}", R)
    f(ca.cell(row=r, column=9), f"=IF('Dados de Entrada'!I{s}=\"S\",B{r}*Parâmetros!$B$15,0)", R)
CL = C0 + len(REV) - 1; CT = CL + 1
ca.cell(row=CT, column=1, value="TOTAL").font = BOLD
for col in "BDEFGHI":
    f(ca[f"{col}{CT}"], f"=SUM({col}{C0}:{col}{CL})", R, BOLD)

S = CT + 2
ca.cell(row=S, column=1, value="Apurações").font = BOLD
rows = [
    ("Presunção extra LC 224 (sobre o excedente de R$ 5 mi)", f"=MAX(0,B{CT}-5000000)/MAX(B{CT},1)*Parâmetros!$B$18", P2),
    ("Base IRPJ presumida ajustada", f"=E{CT}*(1+B{S+1})", R),
    ("Base CSLL presumida ajustada", f"=F{CT}*(1+B{S+1})", R),
    ("IRPJ — Lucro Presumido", f"=B{S+2}*Parâmetros!$B$7+MAX(0,B{S+2}-Parâmetros!$B$9)*Parâmetros!$B$8", R),
    ("CSLL — Lucro Presumido", f"=B{S+3}*Parâmetros!$B$10", R),
    ("Créditos de CBS/IBS das compras", "='Compras e Despesas'!E%d" % ET, R),
    ("CBS/IBS a recolher (débito − crédito)", f"=MAX(0,G{CT}-B{S+6})", R),
    ("ICMS — regime normal", f"=H{CT}", R),
    ("ISS — regime normal", f"=I{CT}", R),
    ("Contribuição patronal fora do Simples", f"={SAL}*(Parâmetros!$B$11+Parâmetros!$B$12+Parâmetros!$B$13)+{PRO}*Parâmetros!$B$11", R),
    ("FGTS (igual em todos os regimes)", f"={SAL}*Parâmetros!$B$14", R),
    ("Lucro contábil estimado (base do Lucro Real)",
     f"=B{CT}-B{S+7}-B{S+8}-B{S+9}-'Compras e Despesas'!B{ET}-{SAL}-{PRO}-B{S+10}-B{S+11}", R),
    ("IRPJ — Lucro Real", f"=MAX(0,B{S+12})*Parâmetros!$B$7+MAX(0,B{S+12}-Parâmetros!$B$9)*Parâmetros!$B$8", R),
    ("CSLL — Lucro Real", f"=MAX(0,B{S+12})*Parâmetros!$B$10", R),
    ("DAS — Simples Nacional (inclui CPP, ICMS e ISS)", f"=D{CT}", R),
]
for i, (a, fo, fm) in enumerate(rows, 1):
    ca.cell(row=S + i, column=1, value=a).font = BLACK
    f(ca.cell(row=S + i, column=2), fo, fm)
A = lambda k: f"Cálculos!$B${S + k}"

# ------------------------------------------------------------------ COMPARATIVO
co = wb.create_sheet("Comparativo", 1)
for k, v in {"A": 40, "B": 17, "C": 17, "D": 17}.items(): co.column_dimensions[k].width = v
co["A1"] = "Comparativo de regimes — 2027"; co["A1"].font = TITLE
co["A2"] = "='Dados de Entrada'!B3&\"  ·  CNPJ \"&'Dados de Entrada'!B4"; co["A2"].font = BOLD
hdr(co, 4, ["Tributo (R$/ano)", "Simples Nacional", "Lucro Presumido", "Lucro Real"])
comp = [
    ("DAS (tributos unificados + CPP)", A(15), "0", "0"),
    ("IRPJ", "0", A(4), A(13)),
    ("CSLL", "0", A(5), A(14)),
    ("CBS/IBS líquido", "0", A(7), A(7)),
    ("ICMS", "0", A(8), A(8)),
    ("ISS", "0", A(9), A(9)),
    ("Contribuição patronal (INSS + RAT + terceiros)", "0", A(10), A(10)),
]
for i, (a, s1, s2, s3) in enumerate(comp, 5):
    co.cell(row=i, column=1, value=a).font = BLACK; co.cell(row=i, column=1).border = BOX
    for j, v in enumerate((s1, s2, s3), 2):
        f(co.cell(row=i, column=j), "=" + v, R, GREEN if "!" in v else BLACK)
TOT = 5 + len(comp)
co.cell(row=TOT, column=1, value="TOTAL DE TRIBUTOS").font = BOLD
for col in "BCD":
    c = co[f"{col}{TOT}"]; f(c, f"=SUM({col}5:{col}{TOT-1})", R, BOLD); c.fill = SUB
co.cell(row=TOT + 1, column=1, value="% sobre a receita").font = BLACK
for col in "BCD":
    f(co[f"{col}{TOT+1}"], f"=IF(Cálculos!$B$3=0,0,{col}{TOT}/Cálculos!$B$3)", P)
co.cell(row=TOT + 2, column=1, value="Diferença em relação ao Simples").font = BLACK
for col in "BCD":
    f(co[f"{col}{TOT+2}"], f"={col}{TOT}-$B${TOT}", R)
co.cell(row=TOT + 3, column=1, value="FGTS (igual em todos — informativo)").font = Font(name=F, size=9, color="5D6472")
for col in "BCD":
    f(co[f"{col}{TOT+3}"], "=" + A(11), R, GREEN)

W = TOT + 5
co.cell(row=W, column=1, value="Regime de menor carga").font = BOLD
H = W + 11  # linha auxiliar (Simples vedado = valor muito alto)
co.cell(row=H, column=1, value="Auxiliar do ranking (não editar)").font = Font(name=F, size=8, color="9AA0A8")
f(co.cell(row=H, column=2), f"=IF($E${W+6}=\"VEDADO\",9E+99,$B${TOT})", R, Font(name=F, size=8, color="9AA0A8"))
f(co.cell(row=H, column=3), f"=$C${TOT}", R, Font(name=F, size=8, color="9AA0A8"))
f(co.cell(row=H, column=4), f"=$D${TOT}", R, Font(name=F, size=8, color="9AA0A8"))
c = co.cell(row=W, column=2, value=f"=INDEX($B$4:$D$4,MATCH(MIN($B${H}:$D${H}),$B${H}:$D${H},0))")
c.font = Font(name=F, bold=True, size=12, color="1B7A3D")
co.cell(row=W + 1, column=1, value="Economia anual frente à 2ª opção (R$)").font = BOLD
f(co.cell(row=W + 1, column=2), f"=SMALL($B${H}:$D${H},2)-MIN($B${H}:$D${H})", R, BOLD)

co.cell(row=W + 3, column=1, value="Alertas").font = BOLD
co.cell(row=W + 4, column=1, value="Receita do grupo (esta empresa + outras dos mesmos sócios)").font = BLACK
f(co.cell(row=W + 4, column=2), "=Cálculos!$B$3+'Dados de Entrada'!$B$6", R)
co.cell(row=W + 5, column=1, value="Acima do sublimite de ICMS/ISS (R$ 3,6 mi)?").font = BLACK
f(co.cell(row=W + 5, column=2), f"=IF(Cálculos!$B$3>Parâmetros!$B$20,\"SIM — ICMS/ISS fora do DAS\",\"Não\")")
co.cell(row=W + 6, column=1, value="Simples permitido pelo limite global (R$ 4,8 mi)?").font = BLACK
f(co.cell(row=W + 6, column=2), f"=IF(B{W+4}>Parâmetros!$B$19,\"NÃO — limite excedido\",\"Sim\")")
f(co.cell(row=W + 6, column=5), f"=IF(B{W+4}>Parâmetros!$B$19,\"VEDADO\",\"OK\")")
co.cell(row=W + 6, column=5).font = Font(name=F, size=8, color="FFFFFF")
co.cell(row=W + 7, column=1, value="Lucro contábil estimado (confira se faz sentido)").font = BLACK
f(co.cell(row=W + 7, column=2), "=" + A(12), R, GREEN)
co.cell(row=W + 9, column=1, value="Resultado indicativo. A decisão final considera também obrigações acessórias, custo de contabilidade, perfil dos clientes (PJ × consumidor) e planos de crescimento.").font = Font(name=F, italic=True, size=9, color="5D6472")

ch = BarChart(); ch.type = "col"; ch.title = "Total de tributos por regime (R$/ano)"
ch.add_data(Reference(co, min_col=2, max_col=4, min_row=TOT, max_row=TOT), from_rows=True, titles_from_data=False)
ch.set_categories(Reference(co, min_col=2, max_col=4, min_row=4, max_row=4))
ch.legend = None; ch.roundedCorners = False; ch.title.overlay = False
ch.x_axis.delete = False; ch.y_axis.delete = False; ch.y_axis.numFmt = '#,##0'
ch.height = 7.5; ch.width = 15
co.add_chart(ch, "F4")

# ------------------------------------------------------------------ CHECKLIST
ck = wb.create_sheet("Checklist de Dados")
for k, v in {"A": 6, "B": 52, "C": 34, "D": 40, "E": 12}.items(): ck.column_dimensions[k].width = v
ck["B1"] = "Checklist de dados do estudo"; ck["B1"].font = TITLE
hdr(ck, 3, ["#", "Informação", "Quem obtém / onde", "Para que serve", "Status"])
items = [
    ("NÓS — com procuração eletrônica no e-CAC ou certificado digital", None, None),
    ("Extratos do PGDAS-D e DAS pagos (12 meses)", "Nós — e-CAC / Portal do Simples", "Receita por anexo e faixa atual"),
    ("Situação fiscal, parcelamentos e pendências", "Nós — e-CAC", "Riscos antes de mudar de regime"),
    ("Folha: remunerações, pró-labore e nº de empregados", "Nós — eSocial / DCTFWeb", "Encargo patronal fora do Simples"),
    ("EFD-Reinf: retenções e aquisição de produção rural (R-2055)", "Nós — e-CAC / Reinf", "Funrural e passivos"),
    ("XMLs de NF-e emitidas e recebidas", "Nós — Receita/PR com certificado ou captura automática de XML", "Mix de vendas, NCMs, compras e créditos"),
    ("NFC-e emitidas (varejo/cafeteria)", "Nós — Receita/PR com certificado", "Receita por item e NCM"),
    ("NFS-e emitidas e tomadas", "Nós — portal da NFS-e do município", "Receita de serviços e ISS"),
    ("Cartão CNPJ, CNAEs e sócios", "Nós — consulta pública", "Enquadramento e limite do grupo"),
    ("CLIENTE — só o que não conseguimos sozinhos", None, None),
    ("Procuração eletrônica no e-CAC (ou certificado A1) e acesso à Receita/PR", "Cliente — 10 minutos", "Libera todos os itens acima"),
    ("Extratos bancários de 2026 (OFX/PDF)", "Cliente", "Conferir receita e despesas"),
    ("Relatório de vendas do PDV por item (12 meses)", "Cliente — exporta do sistema", "Separar café servido × pacote × álcool"),
    ("Aluguel: valor e se o locador é PF ou PJ", "Cliente — 1 resposta", "Crédito de CBS"),
    ("Balancete/DRE 2026 ou contato do contador atual", "Cliente", "Lucro real e margem"),
    ("Respostas rápidas: torram café? compram de produtor do PR? fazem eventos para empresas? planos para 2027?", "Cliente — conversa", "Premissas do estudo"),
]
r = 4; n = 0
for a, b, cc in items:
    if b is None:
        ck.cell(row=r, column=2, value=a).font = WH
        for col in range(1, 6): ck.cell(row=r, column=col).fill = PatternFill("solid", fgColor="8A5A2B")
    else:
        n += 1
        ck.cell(row=r, column=1, value=n).font = BLACK
        ck.cell(row=r, column=2, value=a).font = BLACK
        ck.cell(row=r, column=3, value=b).font = BLACK
        ck.cell(row=r, column=4, value=cc).font = BLACK
        inp(ck.cell(row=r, column=5), "Pendente")
        for col in range(1, 5):
            ck.cell(row=r, column=col).border = BOX; ck.cell(row=r, column=col).alignment = WRAP
    r += 1
dv5 = DataValidation(type="list", formula1='"Pendente,Solicitado,Recebido,N/A"', allow_blank=True)
ck.add_data_validation(dv5); dv5.add(f"E4:E{r}")

for sh in wb.worksheets:
    sh.sheet_view.showGridLines = False
    sh.freeze_panes = None
wb.save(OUT)
print("ok", OUT)
