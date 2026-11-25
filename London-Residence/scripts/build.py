import os
HERE=os.path.dirname(os.path.abspath(__file__))
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter as L
from openpyxl.chart import BarChart, Reference
from openpyxl.chart.label import DataLabelList
from openpyxl.comments import Comment

OUT=os.path.join(HERE,'..','Prestacao_Contas_2026_London_Residence.xlsx')
F='Arial'
NAVY='1F3864'; BLUE='2E75B6'; LIGHT='DDEBF7'; GREY='F2F2F2'; GOLD='FFF2CC'; GREEN='E2EFDA'; RED='FCE4D6'
NUM='#,##0.00;[Red]-#,##0.00;"-"'
thin=Side(style='thin',color='BFBFBF')
BOX=Border(left=thin,right=thin,top=thin,bottom=thin)
def font(**k): return Font(name=F,**k)
def fill(c): return PatternFill('solid',start_color=c,end_color=c)

wb=Workbook()
def sheet(name,title,sub,widths):
    ws=wb.create_sheet(name)
    ws.sheet_view.showGridLines=False
    for i,w in enumerate(widths,1): ws.column_dimensions[L(i)].width=w
    n=len(widths)
    ws.merge_cells(start_row=1,start_column=1,end_row=1,end_column=n)
    ws.merge_cells(start_row=2,start_column=1,end_row=2,end_column=n)
    ws['A1']=title; ws['A1'].font=font(bold=True,size=15,color='FFFFFF'); ws['A1'].fill=fill(NAVY)
    ws['A1'].alignment=Alignment(vertical='center',indent=1); ws.row_dimensions[1].height=30
    ws['A2']=sub; ws['A2'].font=font(italic=True,size=10,color='595959'); ws['A2'].alignment=Alignment(indent=1,wrap_text=True,vertical='top'); ws.row_dimensions[2].height=28
    ws.page_setup.orientation='landscape'; ws.page_setup.paperSize=ws.PAPERSIZE_A4
    ws.page_setup.fitToWidth=1; ws.page_setup.fitToHeight=0; ws.sheet_properties.pageSetUpPr.fitToPage=True
    ws.print_options.horizontalCentered=True
    ws.page_margins.left=ws.page_margins.right=0.4; ws.page_margins.top=0.5; ws.page_margins.bottom=0.6
    return ws
def hdr(ws,r,vals,c0=1,color=BLUE):
    for i,v in enumerate(vals):
        c=ws.cell(r,c0+i,v); c.font=font(bold=True,color='FFFFFF',size=10); c.fill=fill(color)
        c.alignment=Alignment(horizontal='center',vertical='center',wrap_text=True); c.border=BOX
    ws.row_dimensions[r].height=42
def cell(ws,r,c,v,bold=False,fmt=None,bg=None,color='000000',align=None,wrap=False,size=10,italic=False):
    x=ws.cell(r,c,v); x.font=font(bold=bold,color=color,size=size,italic=italic); x.border=BOX
    if fmt: x.number_format=fmt
    if bg: x.fill=fill(bg)
    x.alignment=Alignment(horizontal=align,vertical='center',wrap_text=wrap)
    return x
def section(ws,r,text,n,color=LIGHT):
    ws.merge_cells(start_row=r,start_column=1,end_row=r,end_column=n)
    c=ws.cell(r,1,text); c.font=font(bold=True,size=11,color=NAVY); c.fill=fill(color)
    c.alignment=Alignment(indent=1,vertical='center'); ws.row_dimensions[r].height=20

SUB='CONDOMÍNIO LONDON RESIDENCE · CNPJ 29.855.208/0001-74 · Período: 01/12/2025 a 30/11/2026 · AGO de 26/11/2026 · Fonte: balancete AcolWeb (regime de caixa, 23/11/2026) e extratos Sicredi 61921-3 – saldos conciliados'
MES=['dez/25','jan/26','fev/26','mar/26','abr/26','mai/26','jun/26','jul/26','ago/26','set/26','out/26','nov/26']
z=[0]*12
def m(**k):
    a=[0]*12
    for i,v in k.items(): a[int(i[1:])]=v
    return a

REC=[('Taxa condominial','Quotas condominiais (taxas recebidas)',[8266.70,9249.94,8474.80,15386.48,10250.19,15763.37,16549.44,12133.40,11577.03,12799.91,11987.38,24587.23]),
 ('Taxa condominial','Multas e juros',m(m11=100)),
 ('Taxa condominial','Estorno (devolução de prestador)',m(m10=570)),
 ('Fundos','Fundo de reserva',[600,600,540,540,540,600,570,600,570,660,450,810])]
DES=[('Despesas administrativas','Salário do síndico',[1518,1518]+[1621]*10),
 ('Despesas administrativas','Honorários administrativos (ROF)',[400,800]+[486.30]*10),
 ('Despesas administrativas','Assessoria jurídica',m(m4=1621,m6=1000)),
 ('Despesas administrativas','Despesas bancárias',[140.60,143,145.80,151.40,162.60,164.60,173,184.20,192.60,184.20,173,84]),
 ('Despesas administrativas','Cartório (registro da ata)',m(m0=268.22)),
 ('Despesas administrativas','Software de gestão e certificado',[177.17,173.59,177.42,173.59,333.31]+[208.31]*7),
 ('Despesas administrativas','Internet',[112.12,99.90,112.23,99.90,99.90,99.90,99.90,99.90,99.90,109.90,109.90,109.90]),
 ('Despesas administrativas','Chaves de acesso',m(m5=24,m11=12)),
 ('Despesas administrativas','Despesas de assembleia',m(m0=95,m1=75)),
 ('Manutenção predial','Pintura predial',[0,10000,15000,18000,4500,6000,10000,9000,1600,0,0,0]),
 ('Manutenção predial','Elevador (TK)',[400.03,398.43,404.83,398.43,398.43,398.43,398.43,398.43,398.43,427.25,535.64,427.25]),
 ('Manutenção predial','Manutenção de áreas comuns',[301.72,1500,0,1680,826,0,0,0,200,115,0,0]),
 ('Manutenção predial','Portão de entrada',m(m8=109,m9=750,m10=1050,m11=2427)),
 ('Manutenção predial','Telhado e calhas',m(m1=565,m2=340,m8=455,m9=2170)),
 ('Manutenção predial','Câmeras de segurança',m(m6=1310.30,m7=610.30,m8=610.30)),
 ('Manutenção predial','Dedetização',m(m2=590,m10=500,m11=500)),
 ('Manutenção predial','Material de limpeza',[121.50,180,94,100,0,104,0,130,0,242.50,0,0]),
 ('Manutenção predial','Sistema contra incêndio',m(m3=422.96,m4=410.50)),
 ('Manutenção predial',"Bomba d'água",m(m0=541)),
 ('Manutenção predial','Material elétrico',m(m2=134.99,m3=25.58,m5=69.96,m9=199.18,m10=63.30)),
 ('Serviços essenciais','Água e esgoto',[1222.46,1839.52,1226.62,1226.62,1367.06,1692.71,1811.94,1762.64,1779.72,1367.20,1899.30,1975.95]),
 ('Serviços essenciais','Energia elétrica (Copel)',[456.25,435.42,413.36,418.12,400.56,450.98,511.18,525.61,537.07,623.07,570.73,0]),
 ('Serviços essenciais','Gás',m(m0=435,m2=435,m4=880,m6=482.38,m7=481.78,m10=890)),
 ('Serviços essenciais','Seguro predial obrigatório (HDI)',[274.48,274.52,0]+[317.77]*9),
 ('Prestadores de serviço','Zeladora',[765,765]+[865]*10),
 ('Prestadores de serviço','Jardinagem',m(m1=250,m4=580,m5=300,m7=300,m8=830,m10=350,m11=450)),
 ('Prestadores de serviço','Eletricista',m(m0=150)),
 ('Encargos','Retenção na fonte (TK – DARF 0385)',[19.44]*9+[20.83]*3),
 ('Aquisição de bens','Cartão de acesso do carrinho de compras',m(m5=114.42))]
POUP_R=[224.79,10223.84,15159.32,15659.23,4508.66]+[0]*7
POUP_D=[50.57,10050.37,15035.83,15613.33,4508.66]+[0]*7

wb.remove(wb.active)
# ================= MENSAL =================
ws=sheet('Mês a mês','RECEITAS E DESPESAS MÊS A MÊS (R$)',SUB,[40]+[11.5]*12+[13,12])
r=4; hdr(ws,r,['Conta']+MES+['Total','Média/mês'])
ws.freeze_panes='B5'
def datarow(r,name,vals,bg=None):
    cell(ws,r,1,name,bg=bg)
    for i,v in enumerate(vals): cell(ws,r,2+i,v,fmt=NUM,color='000000',bg=bg)
    cell(ws,r,14,f'=SUM(B{r}:M{r})',fmt=NUM,bold=True,bg=bg); cell(ws,r,15,f'=N{r}/12',fmt=NUM,bg=bg)
def sumrow(r,name,rows,bg=GREY,bold=True):
    cell(ws,r,1,name,bold=bold,bg=bg)
    for c in range(2,16):
        col=L(c)
        f='='+'+'.join(f'{col}{x}' for x in rows) if isinstance(rows,list) else f'=SUM({col}{rows[0]}:{col}{rows[1]})'
        if c==15: f=f'=N{r}/12'
        cell(ws,r,c,f,fmt=NUM,bold=bold,bg=bg)
R={}
r=5; section(ws,r,'RECEITAS',15); r+=1
s=r
for g,n,v in REC: datarow(r,n,v); R[n]=r; r+=1
sumrow(r,'TOTAL DE RECEITAS',(s,r-1),bg=GREEN); R['REC']=r; r+=2
section(ws,r,'DESPESAS',15); r+=1
grp_rows={}; grp_tot=[]
cur=None
for g,n,v in DES:
    if g!=cur:
        if cur: sumrow(r,'Subtotal '+cur.lower(),(gs,r-1)); grp_rows[cur]=r; grp_tot.append(r); r+=1
        cur=g; c=ws.cell(r,1,g.upper()); c.font=font(bold=True,size=10,color=BLUE); r+=1; gs=r
    datarow(r,'   '+n,v); R[n]=r; r+=1
sumrow(r,'Subtotal '+cur.lower(),(gs,r-1)); grp_rows[cur]=r; grp_tot.append(r); r+=1
sumrow(r,'TOTAL DE DESPESAS',grp_tot,bg=RED); R['DES']=r; r+=2
section(ws,r,'RESULTADO E SALDO',15); r+=1
sumrow(r,'Resultado do mês (receitas − despesas)',[R['REC']],bg=None)
for c in range(2,15):
    ws.cell(r,c).value=f"={L(c)}{R['REC']}-{L(c)}{R['DES']}"
R['RES']=r; r+=1
cell(ws,r,1,'Despesas sem a pintura (custo ordinário)')
for c in range(2,15): cell(ws,r,c,f"={L(c)}{R['DES']}-{L(c)}{R['Pintura predial']}",fmt=NUM)
cell(ws,r,15,f'=N{r}/12',fmt=NUM); R['ORD']=r; r+=1
cell(ws,r,1,'Rendimento líquido da poupança (rend. − IR)')
for i in range(12): cell(ws,r,2+i,round(POUP_R[i]-POUP_D[i],2),fmt=NUM,color='000000')
cell(ws,r,14,f'=SUM(B{r}:M{r})',fmt=NUM,bold=True); cell(ws,r,15,f'=N{r}/12',fmt=NUM)
ws.cell(r,1).comment=Comment('Balancete anual AcolWeb: linha Poupança Integrada (receitas) menos linha Poupança Integrada (despesas). Resgates e aplicações são transferências entre contas do próprio condomínio e se anulam; sobra só o rendimento menos o IR retido.','ROF')
R['POUP']=r; r+=1
cell(ws,r,1,'Saldo inicial em 30/11/2025 (todas as contas)',bg=GOLD)
cell(ws,r,2,41110.84,fmt=NUM,color='000000',bg=GOLD); R['SI']=r
ws.cell(r,2).comment=Comment('Conta principal 7.369,69 (extrato Sicredi, saldo anterior de 12/2025) + poupança 33.456,65 + fundo de reserva 284,50.','ROF'); r+=1
cell(ws,r,1,'Saldo acumulado no fim do mês',bold=True,bg=GOLD)
for c in range(2,14):
    prev=f"$B${R['SI']}" if c==2 else f'{L(c-1)}{r}'
    cell(ws,r,c,f"={prev}+{L(c)}{R['RES']}+{L(c)}{R['POUP']}",fmt=NUM,bold=True,bg=GOLD)
R['SALDO']=r; r+=2
note=ws.cell(r,1,'A movimentação entre conta corrente e poupança (aplicações e resgates de R$ 45,3 mil) não entra como receita nem despesa: é transferência entre contas do condomínio.')
note.font=font(italic=True,size=9,color='595959'); ws.merge_cells(start_row=r,start_column=1,end_row=r,end_column=15); note.alignment=Alignment(wrap_text=True); ws.row_dimensions[r].height=28
ws.print_title_rows='4:4'

# ================= DETALHE =================
wd=sheet('Detalhe por fornecedor','RECEITAS E DESPESAS DETALHADAS NO PERÍODO (R$)',SUB,[30,58,15,11])
r=4; hdr(wd,r,['Conta','Fornecedor / descrição','Valor (R$)','% do grupo']); wd.freeze_panes='A5'
DREC=[('Quotas por competência','Competências de 2025 em atraso (jan, abr, jul, set, out)',471.50+347+522.31+1763.36+395.50),
 ('Quotas por competência','Competência nov/2025',7133.40),('Quotas por competência','Competência dez/2025',8385.17),
 ('Quotas por competência','Competência jan/2026',8539.39),('Quotas por competência','Competência fev/2026',7392.60),
 ('Quotas por competência','Competência mar/2026',8698.76),('Quotas por competência','Competência abr/2026',7846.36),
 ('Quotas por competência','Competência mai/2026',7374.76),('Quotas por competência','Competência jun/2026',9674.77),
 ('Quotas por competência','Competência jul/2026',9814.86),('Quotas por competência','Competência ago/2026',10187.91),
 ('Quotas por competência','Competência set/2026',10439.92),('Quotas por competência','Competência out/2026',9080.44),
 ('Quotas por competência','Fundo de pintura – lançamentos da AGO 2023 (R$ 70)',21447.25),
 ('Quotas por competência','Fundo de pintura – lançamentos da AGO 12/2025 (7º assunto: R$ 70 e extras)',21287.06),
 ('Quotas por competência','Fundo de reserva + pintura pagos à parte – aptos 209, 301, 303, 305 e 310',1000.00),
 ('Quotas por competência','Fundo de reserva + pintura pagos à parte – apto 308',205.10),
 ('Quotas por competência','Pagamento judicial de taxas (acordo)',4605.45),
 ('Quotas por competência','Multas do regimento interno (arts. 17, 34, 40, 52, 58 e 60)',413.00),
 ('Multas e juros','Multa – arts. 30 e 33 "c" do regimento',100.00),
 ('Estorno','Devolução de prestador (Dilervaldo, 01/10/2026)',570.00),
 ('Fundo de reserva','Fundo de reserva (R$ 30/unidade)',7080.00)]
DDES=[('Salário do síndico','Marcos Antonio Sartori Pereira',19246.00),
 ('Honorários administrativos','ROF Contabilidade – mensalidades',5263.00),('Honorários administrativos','ROF Contabilidade – serviços e AGO 12/2025',800.00),
 ('Assessoria jurídica','Everton Soares Sociedade Individual de Advocacia',2621.00),
 ('Despesas bancárias','Sicredi – tarifas de cobrança',1238.00),('Despesas bancárias','Sicredi – cesta de relacionamento',661.00),
 ('Cartório','Tabelionato de Fazenda Rio Grande – registro da ata AGO 12/2025',268.22),
 ('Software','Group Software (AcolWeb)',2368.25),('Software','ACINFAZ – certificado digital',125.00),
 ('Internet','Direct Wifi Telecom',1253.35),
 ('Chaves de acesso','Leandro Gutoski dos Santos (MEI)',24.00),('Chaves de acesso','Chaveiro Pioneiros',12.00),
 ('Despesas de assembleia','Upy Upy Festas – locação de cadeiras',170.00),
 ('Pintura predial','Santos Aleluia Ltda – fachada',47500.00),('Pintura predial','Fidelidade Drywall – estacionamento',25000.00),('Pintura predial','Tintas Verginia – tinta Dacar',1600.00),
 ('Elevador','TK Elevadores – manutenção mensal',4984.01),
 ('Áreas comuns','Fidelidade Drywall – infraestrutura e iluminação na rua',1680.00),('Áreas comuns','Fidelidade Drywall – lavagem do teto do estacionamento',1500.00),
 ('Áreas comuns','Dilervaldo Cavalcante – manutenção do interfone',826.00),('Áreas comuns','Dilervaldo Cavalcante – porta social do hall',301.72),
 ('Áreas comuns','Brener N. T. V. da Silva – playground',200.00),('Áreas comuns','Cazama – corda',115.00),
 ('Portão de entrada','Asset Solution – compra e instalação do motor',2427.00),('Portão de entrada','Asset Solution – controlador de acesso e visita técnica',1050.00),
 ('Portão de entrada','Dilervaldo Cavalcante – manutenção e revisão',750.00),('Portão de entrada','Asset Solution – controles',109.00),
 ('Telhado','Luiz Marcelo de Godoy – manutenção do telhado',2065.00),('Telhado','Telhadão – telhas',1125.00),('Telhado','Luiz Marcelo de Godoy – troca de calha',340.00),
 ('Câmeras','Asset Solution – troca de câmeras e fiação (entrada + 1/3)',1310.30),('Câmeras','Asset Solution – parcelas 2/3 e 3/3',1220.60),
 ('Dedetização','VIP Dedetizadora',1090.00),('Dedetização','Meliponário Bini – remoção de vespas',500.00),
 ('Material de limpeza','Ecolimp Produtos Saneantes',972.00),
 ('Sistema contra incêndio','Platina Extintores – recarga e teste de mangueiras (2 parcelas)',833.46),
 ("Bomba d'água",'Antonio Pereira Lima – manutenção',541.00),
 ('Material elétrico','Eletrorastro – materiais e lâmpadas',467.43),('Material elétrico','WB Equipamentos Eletrônicos',25.58),
 ('Água e esgoto','Sanepar',18521.74),('Água e esgoto','Rodrigues Água Potável',650.00),
 ('Energia elétrica','Copel',5342.35),('Gás','BR Distribuidora de Gás',3604.16),('Seguro predial','HDI Seguros',3408.93),
 ('Zeladora','Araceli de Fátima',10180.00),
 ('Jardinagem','Lucas Aurélio Agostinho Mathias (L.A Jardinagem)',2260.00),('Jardinagem','Brener N. T. V. da Silva',550.00),('Jardinagem','Leonilda Aparecida Barreiros',250.00),
 ('Eletricista','Gilvan José de Lira',150.00),
 ('Retenção na fonte','DARF 0385 – retenção TK Elevadores',237.45),
 ('Carrinho de compras','Mercado Pago – cartão de acesso',114.42)]
r=5; section(wd,r,'RECEITAS',4); r+=1; s=r
for a,b,v in DREC:
    cell(wd,r,1,a); cell(wd,r,2,b,wrap=True); cell(wd,r,3,v,fmt=NUM,color='000000'); cell(wd,r,4,f'=C{r}/C$%d'%0,fmt='0.0%'); r+=1
er=r
for x in range(s,er): wd.cell(x,4).value=f'=C{x}/$C${er}'
cell(wd,r,1,'TOTAL DE RECEITAS',bold=True,bg=GREEN); cell(wd,r,2,'',bg=GREEN); cell(wd,r,3,f'=SUM(C{s}:C{r-1})',fmt=NUM,bold=True,bg=GREEN); cell(wd,r,4,f'=C{r}/C{r}',fmt='0.0%',bg=GREEN)
DR_TOT=r

r+=3; section(wd,r,'DESPESAS',4); r+=1; s=r
for a,b,v in sorted(DDES,key=lambda t:-t[2]):
    cell(wd,r,1,a); cell(wd,r,2,b,wrap=True); cell(wd,r,3,v,fmt=NUM,color='000000'); r+=1
er=r
for x in range(s,er): cell(wd,x,4,f'=C{x}/$C${er}',fmt='0.0%')
cell(wd,r,1,'TOTAL DE DESPESAS',bold=True,bg=RED); cell(wd,r,2,'',bg=RED); cell(wd,r,3,f'=SUM(C{s}:C{r-1})',fmt=NUM,bold=True,bg=RED); cell(wd,r,4,f'=C{r}/C{r}',fmt='0.0%',bg=RED)

wd.cell(4,4).value='% do total'
for x in range(6,DR_TOT): pass

# ================= CONCILIAÇÃO =================
wc=sheet('Conciliação bancária','SALDOS BANCÁRIOS CONCILIADOS – SICREDI CONTA 61921-3 (R$)',SUB,[26,18,18,20,16,10,30])
r=4; hdr(wc,r,['Mês','Saldo inicial','Movimento do mês','Saldo final conciliado','Situação'])
ext=[('dez/25',7369.69,8838.40,8838.40,'12_2025 / extrato (8).pdf'),('jan/26',8838.40,9651.52,9651.52,'01_2026 / extrato (9).pdf'),
('fev/26',9651.52,11600.33,11600.33,'02_2026 / extrato (10).pdf'),('mar/26',11600.33,5920.70,5920.70,'03_2026 / Extrato / extrato.pdf'),
('abr/26',5920.70,6330.68,6330.68,'04_2026 / extrato (11).pdf'),('mai/26',6330.68,9757.23,9757.23,'05_2026 / 05_2026.pdf'),
('jun/26',9757.23,7571.72,7571.72,'06_2026 / sicredi_1782910943869.pdf'),('jul/26',7571.72,3294.44,3294.44,'07_2026 / extrato.pdf'),
('ago/26',3294.44,5111.63,5111.63,'08_2026 / extrato (12).pdf'),('set/26',5111.63,8864.03,8864.03,'09_2026 / extrato (14).pdf'),
('out/26',8864.03,12210.33,12210.33,'10_2026 / extrato (15).pdf'),('até 19/11/26',12210.33,26789.03,26789.03,'11_2026 / extrato (16).pdf')]
r=5
for mm,a,b,c,f in ext:
    cell(wc,r,1,mm,align='center'); cell(wc,r,2,a,fmt=NUM,color='000000'); cell(wc,r,3,f'=D{r}-B{r}',fmt=NUM)
    cell(wc,r,4,b,fmt=NUM,color='000000',bold=True); cell(wc,r,5,'Conciliado',align='center',bold=True,color='375623',bg=GREEN); r+=1
r+=1; section(wc,r,'POSIÇÃO DAS CONTAS',7); r+=1
hdr(wc,r,['Conta','30/11/2025','Posição 23/11/2026','Variação','Observação']); wc.merge_cells(start_row=r,start_column=5,end_row=r,end_column=7); r+=1; s=r
for n,a,b,o in [('Conta principal 61921-3',7369.69,28202.25,'Saldo atualizado em 23/11/2026'),
                ('Poupança / aplicação',33456.65,65.07,'Resgatada para pagar a pintura'),('Fundo de reserva',284.50,284.50,'Sem movimento: o fundo arrecadado ficou na conta principal')]:
    cell(wc,r,1,n); cell(wc,r,2,a,fmt=NUM,color='000000'); cell(wc,r,3,b,fmt=NUM,color='000000'); cell(wc,r,4,f'=C{r}-B{r}',fmt=NUM)
    wc.merge_cells(start_row=r,start_column=5,end_row=r,end_column=7); cell(wc,r,5,o,size=9,wrap=True); wc.row_dimensions[r].height=26; r+=1
cell(wc,r,1,'TOTAL',bold=True,bg=GOLD)
for c in (2,3,4): cell(wc,r,c,f'=SUM({L(c)}{s}:{L(c)}{r-1})',fmt=NUM,bold=True,bg=GOLD)
POS_TOT=r; r+=1

r+=2; section(wc,r,'RESGATES E APLICAÇÕES DA POUPANÇA (transferências para pagar a pintura)',7); r+=1
hdr(wc,r,['Data','Movimento','Valor','Uso']); wc.merge_cells(start_row=r,start_column=4,end_row=r,end_column=7); r+=1; s=r
for d,mv,v,u in [('20/01/2026','Resgate',10000,'1ª parcela fachada – Santos Aleluia (10.000)'),('18/02/2026','Resgate',15000,'2ª parcela fachada – Santos Aleluia (15.000)'),
                 ('25/03/2026','Aplicação',-5600,'Sobra de caixa aplicada'),('31/03/2026','Resgate',10000,'Parcela fachada 31/03 – Santos Aleluia (8.000)'),('07/04/2026','Resgate',4508.66,'Última parcela fachada – Santos Aleluia (4.500)')]:
    cell(wc,r,1,d,align='center'); cell(wc,r,2,mv); cell(wc,r,3,v,fmt=NUM,color='000000'); wc.merge_cells(start_row=r,start_column=4,end_row=r,end_column=7); cell(wc,r,4,u,size=9); r+=1
cell(wc,r,2,'Resgate líquido',bold=True,bg=GOLD); cell(wc,r,3,f'=SUM(C{s}:C{r-1})',fmt=NUM,bold=True,bg=GOLD)

# ================= PINTURA =================
wp=sheet('Obras e pintura','OBRAS DE PINTURA 2026 – APROVADO × PAGO (R$)',SUB,[44,22,16,16,52])
r=4; hdr(wp,r,['Obra','Aprovado (AGO 01/12/2025, 7º assunto)','Contrato','Pago','Diferença pago × aprovado / Situação']); r+=1
PG=[('20/01/2026','Santos Aleluia Ltda','Fachada',10000,'NFS-e 17'),('18/02/2026','Santos Aleluia Ltda','Fachada',15000,'NFS-e 19'),
('13/03/2026','Santos Aleluia Ltda','Fachada',5000,'NFS-e 23'),('20/03/2026','Santos Aleluia Ltda','Fachada',5000,'NFS-e 24'),
('31/03/2026','Santos Aleluia Ltda','Fachada',8000,'NFS-e 27'),('07/04/2026','Santos Aleluia Ltda','Fachada',4500,'NFS-e 28'),
('25/05/2026','Fidelidade Drywall','Estacionamento',6000,'Comprovante PIX'),('18/06/2026','Fidelidade Drywall','Estacionamento',10000,'Comprovante PIX'),
('02/07/2026','Fidelidade Drywall','Estacionamento',3000,'Comprovante PIX'),('10/07/2026','Fidelidade Drywall','Estacionamento',6000,'Comprovante PIX'),
('07/08/2026','Tintas Verginia','Material',1200,'Comprovante PIX'),('27/08/2026','Tintas Verginia','Material',400,'Comprovante PIX')]
pr0=12
obras=[('Fachada superior – Santos Aleluia','Fachada',48000,45000),('Teto e colunas do estacionamento – Fidelidade Drywall','Estacionamento',20000,None),
       ('Material (tinta Dacar) – Tintas Verginia','Material',None,None),('Corredores (fundo de R$ 70/mês desde 04/2026)','Corredores',None,None)]
o0=r
for n,k,a,c in obras:
    cell(wp,r,1,n,wrap=True); cell(wp,r,2,a,fmt=NUM,color='000000'); cell(wp,r,3,c,fmt=NUM,color='000000')
    cell(wp,r,4,f'=SUMIF($C${pr0+1}:$C${pr0+len(PG)},"{k}",$D${pr0+1}:$D${pr0+len(PG)})',fmt=NUM,bold=True)
    txt={'Fachada':f'=IF(B{r}="","",D{r}-B{r})','Estacionamento':f'=D{r}-B{r}'}.get(k)
    if k=='Fachada': cell(wp,r,5,'Dentro do valor aprovado',wrap=True,bg=GREEN,size=9)
    elif k=='Estacionamento': cell(wp,r,5,'R$ 5.000,00 acima do valor aprovado (a lavagem do teto, R$ 1.500,00, está em manutenção de áreas comuns)',wrap=True,bg=GOLD,size=9)
    elif k=='Material': cell(wp,r,5,'Tinta comprada à parte',wrap=True,size=9)
    else: cell(wp,r,5,'Sem pagamentos no período',wrap=True,size=9)
    wp.row_dimensions[r].height=30; r+=1
cell(wp,r,1,'TOTAL',bold=True,bg=GREY)
for c in (2,3,4): cell(wp,r,c,f'=SUM({L(c)}{o0}:{L(c)}{r-1})',fmt=NUM,bold=True,bg=GREY)
cell(wp,r,5,'',bg=GREY)
r+=2
assert r<=pr0-1, r
r=pr0-1; section(wp,r,'PAGAMENTOS DA PINTURA (extratos Sicredi)',5); r=pr0
hdr(wp,r,['Data','Fornecedor','Obra','Valor (R$)','Documento'])
for i,(d,f,o,v,doc) in enumerate(PG):
    rr=pr0+1+i; cell(wp,rr,1,d,align='center'); cell(wp,rr,2,f); cell(wp,rr,3,o); cell(wp,rr,4,v,fmt=NUM,color='000000'); cell(wp,rr,5,doc,size=9,bg=None)
r=pr0+1+len(PG); cell(wp,r,3,'Total pago',bold=True,bg=GREY); cell(wp,r,4,f'=SUM(D{pr0+1}:D{r-1})',fmt=NUM,bold=True,bg=GREY)
r+=2; section(wp,r,'FUNDO DE PINTURA NO PERÍODO',5); r+=1
hdr(wp,r,['Item','Quantidade','Valor unitário','Valor (R$)','Base']); r+=1; f0=r
rows=[('Previsto: R$ 70/mês por unidade',240,70,'AGO 30/11/2023, 9º assunto (20 unid. × 12 meses)'),
      ('Previsto: extra de 03/2026',20,520,'AGO 01/12/2025, 7º assunto'),('Previsto: extras de 05 e 06/2026',40,500,'AGO 01/12/2025, 7º assunto')]
for n,q,u,b in rows:
    cell(wp,r,1,n); cell(wp,r,2,q,color='000000'); cell(wp,r,3,u,fmt=NUM,color='000000'); cell(wp,r,4,f'=B{r}*C{r}',fmt=NUM); cell(wp,r,5,b,size=9); r+=1
cell(wp,r,1,'Total previsto',bold=True,bg=GREY); cell(wp,r,4,f'=SUM(D{f0}:D{r-1})',fmt=NUM,bold=True,bg=GREY); PREV=r; r+=1
cell(wp,r,1,'Recebido – lançamentos da AGO 2023 (R$ 70)'); cell(wp,r,4,21447.25,fmt=NUM,color='000000'); cell(wp,r,5,'Balancete detalhado',size=9); a1=r; r+=1
cell(wp,r,1,'Recebido – lançamentos da AGO 12/2025 (7º assunto)'); cell(wp,r,4,21287.06,fmt=NUM,color='000000'); cell(wp,r,5,'Balancete detalhado',size=9); r+=1
cell(wp,r,1,'Recebido – parte de pintura nos pagamentos à parte'); cell(wp,r,2,1205.10,fmt=NUM,color='000000'); cell(wp,r,3,0.7,fmt='0%',color='000000'); cell(wp,r,4,f'=ROUND(B{r}*C{r},2)',fmt=NUM)
cell(wp,r,5,'R$ 70 de cada R$ 100 (aptos 209, 301, 303, 305, 310 e 308)',size=9); r+=1
cell(wp,r,1,'Total recebido',bold=True,bg=GREY); cell(wp,r,4,f'=SUM(D{a1}:D{r-1})',fmt=NUM,bold=True,bg=GREY); REC_=r; r+=1
cell(wp,r,1,'Previsto e ainda não recebido'); cell(wp,r,4,f'=D{PREV}-D{REC_}',fmt=NUM); r+=1
cell(wp,r,1,'Poupança em 30/11/2025 (reserva da pintura)'); cell(wp,r,4,33456.65,fmt=NUM,color='000000'); cell(wp,r,5,'Reserva aplicada em poupança',size=9); po=r; r+=1
cell(wp,r,1,'Rendimento líquido da poupança'); cell(wp,r,4,f"='Mês a mês'!N{R['POUP']}",fmt=NUM,color='000000'); rd=r; r+=1
cell(wp,r,1,'(−) Pintura paga'); cell(wp,r,4,f"=-'Mês a mês'!N{R['Pintura predial']}",fmt=NUM,color='000000'); pp=r; r+=1
cell(wp,r,1,'Saldo do fundo de pintura',bold=True,bg=GOLD); cell(wp,r,4,f'=D{REC_}+D{po}+D{rd}+D{pp}',fmt=NUM,bold=True,bg=GOLD); cell(wp,r,5,'Hoje está na conta principal (a poupança tem R$ 65,07)',size=9,bg=GOLD)

# ================= INADIMPLÊNCIA =================
wi=sheet('Inadimplência','INADIMPLÊNCIA E ACORDO JUDICIAL (R$)',SUB,[46,16,50])
r=4; cell(wi,r,1,'Inadimplência acumulada em 30/11/2026',bold=True,bg=GOLD); cell(wi,r,2,280.54,fmt=NUM,bold=True,color='000000',bg=GOLD)
cell(wi,r,3,'',bg=GOLD); r+=2
section(wi,r,'Acordo judicial – valor repassado pelo advogado em 06/11/2026 (unidade não identificada nesta apresentação)',3); r+=1
hdr(wi,r,['Competência quitada','Valor (R$)','Observação']); r+=1; s=r
for c_,v in [('jul/2025',622.31),('nov/2025',632.67),('dez/2025',563.28),('jan/2026',562.57),('fev/2026',1039.00),('mar/2026',562.69),('abr/2026',1115.42),
             ('mai/2026',950.87),('jun/2026',528.69),('jul/2026',528.82),('ago/2026',565.25),('set/2026',541.12),('out/2026',461.15),('Pagamento judicial de taxas (débitos anteriores)',4605.45)]:
    cell(wi,r,1,c_); cell(wi,r,2,v,fmt=NUM,color='000000'); cell(wi,r,3,''); r+=1
cell(wi,r,1,'Total recebido no acordo',bold=True,bg=GREY); cell(wi,r,2,f'=SUM(B{s}:B{r-1})',fmt=NUM,bold=True,bg=GREY); cell(wi,r,3,'Recebido em 06/11/2026',size=9,bg=GREY); r+=2
section(wi,r,'Outros repasses do advogado e custo jurídico',3); r+=1
for n,v,o in [('Repasse de acordo – 19/12/2025',571.50,'Entrada'),('Repasse de acordo – 18/02/2026',447.00,'Entrada'),('Assessoria jurídica – 02/04/2026',-1621.00,'Despesa'),('Assessoria jurídica – 12/06/2026',-1000.00,'Despesa')]:
    cell(wi,r,1,n); cell(wi,r,2,v,fmt=NUM,color='000000'); cell(wi,r,3,o,size=9); r+=1
r+=1; section(wi,r,'Regras aplicáveis',3); r+=1
for t in ['Encargos: juros de 1% ao mês + correção monetária + multa de 2% (Convenção, art. 36; CC art. 1.336, § 1º).',
          'Tolerância de 3 meses e depois cobrança mais incisiva (AGO 22/12/2022, 2º assunto).',
          'Condômino inadimplente não vota em assembleia (Convenção, art. 8º, § 3º; CC art. 1.335, III).']:
    wi.merge_cells(start_row=r,start_column=1,end_row=r,end_column=3); c=wi.cell(r,1,t); c.font=font(size=10); c.alignment=Alignment(wrap_text=True); r+=1

# ================= PENDÊNCIAS =================
wq=sheet('Pendências','PONTOS A CONFIRMAR ANTES DA AGO DE 26/11/2026',SUB,[5,34,70,16])
r=4; hdr(wq,r,['Nº','Assunto','O que falta','Situação']); r+=1
for i,(a,b) in enumerate([
 ('Pintura do estacionamento','R$ 25.000 pagos × R$ 20.000 aprovados (R$ 26.500 com a lavagem). Quem aprovou a diferença? Pedir nota fiscal e contrato da Fidelidade Drywall.'),
 ('Pintura da fachada','R$ 47.500 pagos × contrato de R$ 45.000 (dentro dos R$ 48.000 aprovados). Houve aditivo ou serviço extra?'),
 ('Pintura dos corredores','Nenhum pagamento. Foi executada, ficou para 2027 ou o fundo foi usado no estacionamento?'),
 ('Fundo de reserva','Arrecadou R$ 7.080 no período, mas a conta do fundo segue em R$ 284,50. Propor aplicação mensal separada (Convenção, art. 41).'),
 ('Fechamento de novembro','Salvar o extrato do Sicredi posterior a 23/11 e incluir a Copel de R$ 603,91 de 26/11.'),
 ('Fundo de pintura exato','Relatório do AcolWeb com a composição do boleto por item. Confirmar se toda a poupança de 30/11/2025 era fundo de pintura.'),
 ('Retenções fiscais','INSS 11% não retido nas notas da Santos Aleluia (Lei 8.212/91, art. 31). NFS-e 23 com ISS em Araucária – devido em Fazenda Rio Grande (LC 116/03, art. 3º, III). Verificar notas da Fidelidade.'),
 ('Divulgação e parecer','Enviar a prestação aos condôminos antes da AGO (Convenção, art. 6º, § 2º) e colher o parecer do conselho fiscal (Brenda Trento, apto 208).')],1):
    cell(wq,r,1,i,align='center'); cell(wq,r,2,a,bold=True,wrap=True); cell(wq,r,3,b,wrap=True); cell(wq,r,4,'Pendente',align='center',bg=GOLD); wq.row_dimensions[r].height=42; r+=1
from openpyxl.worksheet.datavalidation import DataValidation
dv=DataValidation(type='list',formula1='"Pendente,Resolvido,Levar à AGO"',allow_blank=True); wq.add_data_validation(dv); dv.add(f'D5:D{r-1}')

# ================= RESUMO (capa) =================
w=sheet('Resumo','PRESTAÇÃO DE CONTAS 2026 – RESUMO',SUB,[46,18,4,40,18])
wb.move_sheet(w,offset=-(len(wb.sheetnames)-1))
M="'Mês a mês'!"
r=4; section(w,r,'RESULTADO DO PERÍODO (12/2025 a 11/2026)',2); section_=None
r=5
items=[('Saldo inicial em 30/11/2025',f"={M}B{R['SI']}",None),('(+) Receitas',f"={M}N{R['REC']}",GREEN),
 ('(+) Rendimento líquido da poupança',f"={M}N{R['POUP']}",None),('(−) Despesas',f"=-{M}N{R['DES']}",RED),
 ('      das quais: pintura predial',f"=-{M}N{R['Pintura predial']}",None),('(=) Resultado do período',None,None),('Saldo final (posição de 23/11/2026)',None,GOLD)]
rs={}
for n,f,bg in items:
    cell(w,r,1,n,bold=n.startswith(('(=','Saldo')),bg=bg); cell(w,r,2,f,fmt=NUM,bold=True,bg=bg); rs[n]=r; r+=1
w.cell(rs['(=) Resultado do período'],2).value=f"=B{rs['(+) Receitas']}+B{rs['(+) Rendimento líquido da poupança']}+B{rs['(−) Despesas']}"
w.cell(rs['Saldo final (posição de 23/11/2026)'],2).value=f"=B{rs['Saldo inicial em 30/11/2025']}+B{rs['(=) Resultado do período']}"
cell(w,r,1,'Inadimplência acumulada em 30/11/2026'); cell(w,r,2,"='Inadimplência'!B4",fmt=NUM,bold=True); r+=1
cell(w,r,1,'Custo ordinário médio por mês (sem pintura)'); cell(w,r,2,f"={M}O{R['ORD']}",fmt=NUM,bold=True)
# right side: saldos e grupos
rr=4; w.merge_cells(start_row=rr,start_column=4,end_row=rr,end_column=5); c=w.cell(rr,4,'ONDE ESTÁ O DINHEIRO'); c.font=font(bold=True,size=11,color=NAVY); c.fill=fill(LIGHT); c.alignment=Alignment(indent=1)
rr=5
for i,n in enumerate(['Conta principal 61921-3','Poupança / aplicação','Fundo de reserva','Total']):
    cell(w,rr,4,n,bold=(n=='Total'),bg=(GOLD if n=='Total' else None)); cell(w,rr,5,f"='Conciliação bancária'!C{POS_TOT-3+i}",fmt=NUM,bold=True,bg=(GOLD if n=='Total' else None)); rr+=1
rr+=1; w.merge_cells(start_row=rr,start_column=4,end_row=rr,end_column=5); c=w.cell(rr,4,'DESPESAS POR GRUPO'); c.font=font(bold=True,size=11,color=NAVY); c.fill=fill(LIGHT); c.alignment=Alignment(indent=1); rr+=1
g0=rr
for g in grp_rows:
    cell(w,rr,4,g); cell(w,rr,5,f"={M}N{grp_rows[g]}",fmt=NUM); rr+=1
cell(w,rr,4,'Total',bold=True,bg=GREY); cell(w,rr,5,f'=SUM(E{g0}:E{rr-1})',fmt=NUM,bold=True,bg=GREY)
r=max(r,rr)+2
w.merge_cells(start_row=r,start_column=1,end_row=r+2,end_column=5)
c=w.cell(r,1,'Leitura: a arrecadação cobriu o custo ordinário do prédio em todos os 12 meses. O resultado negativo vem da pintura (fachada e estacionamento), paga com o fundo de pintura e com a reserva que estava na poupança. Os saldos bancários estão conciliados em todos os meses (aba Conciliação bancária).')
c.font=font(size=10,italic=True); c.alignment=Alignment(wrap_text=True,vertical='top')
r+=4
# chart data helper (hidden-ish area on Mensal referenced directly)
ch=BarChart(); ch.type='col'; ch.grouping='clustered'; ch.title='Arrecadação × despesas por mês (R$)'
ch.y_axis.title=None; ch.height=9; ch.width=26
data=Reference(wb['Mês a mês'],min_col=1,max_col=13,min_row=R['REC'],max_row=R['REC'])
ch.add_data(data,from_rows=True,titles_from_data=True)
data2=Reference(wb['Mês a mês'],min_col=1,max_col=13,min_row=R['ORD'],max_row=R['ORD']); ch.add_data(data2,from_rows=True,titles_from_data=True)
data3=Reference(wb['Mês a mês'],min_col=1,max_col=13,min_row=R['Pintura predial'],max_row=R['Pintura predial']); ch.add_data(data3,from_rows=True,titles_from_data=True)
ch.set_categories(Reference(wb['Mês a mês'],min_col=2,max_col=13,min_row=4,max_row=4))
cols=['A6A6A6','595959','2E75B6']
for s_,cl in zip(ch.series,cols): s_.graphicalProperties.solidFill=cl; s_.graphicalProperties.line.solidFill=cl
ch.roundedCorners=False; ch.legend.position='b'; ch.legend.overlay=False; ch.title.overlay=False
ch.x_axis.delete=False; ch.y_axis.delete=False; ch.y_axis.numFmt='#,##0'; ch.y_axis.majorGridlines=None
w.add_chart(ch,f'A{r}')
w.page_setup.orientation='landscape'; w.page_setup.fitToHeight=1

exec(open(os.path.join(HERE,'extra.py')).read())
order_=['Visão geral','Resumo','Mês a mês','Detalhe por fornecedor','Razão diário','Razão por conta','Conciliação bancária','Obras e pintura','Inadimplência']
wb.remove(wb['Pendências'])
wb._sheets=[wb[n] for n in order_]
for s_ in wb.worksheets:
    s_.oddFooter.left.text='Condomínio London Residence – Prestação de Contas 2026'; s_.oddFooter.left.size=8
    s_.oddFooter.center.text='&A'; s_.oddFooter.center.size=8
    s_.oddFooter.right.text='Página &P de &N'; s_.oddFooter.right.size=8
    s_.page_setup.paperSize=s_.PAPERSIZE_A4
wb['Detalhe por fornecedor'].print_title_rows='4:4'
wb['Detalhe por fornecedor'].page_setup.orientation='portrait'
wb['Razão por conta'].page_setup.orientation='portrait'
for n_ in ('Conciliação bancária','Obras e pintura','Inadimplência'):
    wb[n_].page_setup.fitToHeight=1
wb['Obras e pintura'].page_setup.orientation='portrait'
wb['Inadimplência'].page_setup.orientation='portrait'
wb.active=0
for s_ in wb.worksheets:
    for row in s_.iter_rows():
        for c in row:
            if c.font and c.font.name!=F: c.font=Font(name=F,size=c.font.size,bold=c.font.bold,italic=c.font.italic,color=c.font.color)
wb.save(OUT); print(OUT,R['REC'],R['DES'],R['SALDO'])
