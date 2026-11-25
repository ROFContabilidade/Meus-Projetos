from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter as L
from openpyxl.worksheet.datavalidation import DataValidation
import os
OUT=os.path.join(os.path.dirname(os.path.abspath(__file__)),'..','Relatorio_Interno_Divergencias_London_2026.xlsx')
F='Arial'; NAVY='7F1F1F'; BLUE='C00000'; GOLD='FFF2CC'; GREY='F2F2F2'
NUM='#,##0.00;[Red]-#,##0.00;"-"'
thin=Side(style='thin',color='BFBFBF'); BOX=Border(left=thin,right=thin,top=thin,bottom=thin)
fill=lambda c: PatternFill('solid',start_color=c,end_color=c)
wb=Workbook(); wb.remove(wb.active)
SUB='USO INTERNO – NÃO FAZ PARTE DA PRESTAÇÃO DE CONTAS · Condomínio London Residence · Período 12/2025 a 11/2026 · ROF Contabilidade · posição de 23/11/2026'
def sheet(name,title,widths):
    ws=wb.create_sheet(name); ws.sheet_view.showGridLines=False
    for i,w in enumerate(widths,1): ws.column_dimensions[L(i)].width=w
    n=len(widths)
    ws.merge_cells(start_row=1,start_column=1,end_row=1,end_column=n); ws.merge_cells(start_row=2,start_column=1,end_row=2,end_column=n)
    ws['A1']=title; ws['A1'].font=Font(name=F,bold=True,size=14,color='FFFFFF'); ws['A1'].fill=fill(NAVY); ws['A1'].alignment=Alignment(vertical='center',indent=1); ws.row_dimensions[1].height=28
    ws['A2']=SUB; ws['A2'].font=Font(name=F,italic=True,size=9,color='C00000'); ws['A2'].alignment=Alignment(indent=1,wrap_text=True)
    ws.page_setup.orientation='landscape'; ws.page_setup.paperSize=ws.PAPERSIZE_A4; ws.sheet_properties.pageSetUpPr.fitToPage=True; ws.page_setup.fitToWidth=1; ws.page_setup.fitToHeight=0
    ws.page_margins.left=ws.page_margins.right=0.4
    ws.oddFooter.left.text='London Residence – Relatório interno'; ws.oddFooter.left.size=8; ws.oddFooter.right.text='Página &P de &N'; ws.oddFooter.right.size=8
    return ws
def hdr(ws,r,vals):
    for i,v in enumerate(vals,1):
        c=ws.cell(r,i,v); c.font=Font(name=F,bold=True,color='FFFFFF',size=10); c.fill=fill(BLUE); c.alignment=Alignment(horizontal='center',vertical='center',wrap_text=True); c.border=BOX
    ws.row_dimensions[r].height=30; ws.print_title_rows=f'{r}:{r}'
def row(ws,r,vals,fmts=None,h=42):
    for i,v in enumerate(vals,1):
        c=ws.cell(r,i,v); c.font=Font(name=F,size=10,bold=(i==1)); c.border=BOX; c.alignment=Alignment(wrap_text=True,vertical='center',horizontal=('center' if i==1 else None))
        if fmts and fmts.get(i): c.number_format=fmts[i]
    ws.row_dimensions[r].height=h
def status(ws,col,r0,r1,opts='"Pendente,Corrigido no AcolWeb,Esclarecido"'):
    dv=DataValidation(type='list',formula1=opts,allow_blank=True); ws.add_data_validation(dv); dv.add(f'{col}{r0}:{col}{r1}')
    for r in range(r0,r1+1):
        c=ws[f'{col}{r}']; c.value='Pendente'; c.fill=fill(GOLD); c.alignment=Alignment(horizontal='center',vertical='center'); c.font=Font(name=F,size=10,bold=True)

# 1 divergências
ws=sheet('Divergências AcolWeb','DIVERGÊNCIAS DE CADASTRO E CLASSIFICAÇÃO – EXTRATO SICREDI × ACOLWEB',[5,12,13,36,40,40,18])
r=4; hdr(ws,r,['Nº','Data','Valor (R$)','O que o extrato mostra','O que o AcolWeb mostra','O que fazer','Situação']); r+=1; r0=r
for d in [('24/03/2026',25.58,'PIX para Eletrorastro Comércio de Material Elétrico','Fornecedor "WB Equipamentos Eletrônicos" (material elétrico)','Corrigir o fornecedor no lançamento do AcolWeb'),
          ('06/01/2026',250.00,'PIX para Argemiro Breiko','Jardinagem – "Leonilda Aparecida Barreiros"','Confirmar no comprovante/recibo quem prestou o serviço e corrigir o favorecido'),
          ('09/12/2025',268.22,'PIX para Marcos Antonio Sartori Pereira (síndico)','Cartório – registro da ata AGO 12/2025 (Tabelionato de Fazenda Rio Grande)','Arquivar o recibo do cartório e anotar no histórico que foi reembolso ao síndico'),
          ('11/11/2026',2427.00,'PIX para Asset Solution – motor do portão','Relatório 01–19/11: "Outras áreas comuns" · Balancete anual: "Portão entrada"','Definir a conta (sugestão: Portão entrada) e deixar igual nos dois relatórios'),
          ('09/11/2026',12.00,'PIX para Chaveiro Pioneiros','Relatório 01–19/11: "Outras áreas comuns" · Balancete anual: "Chaves de acesso"','Definir a conta (sugestão: Chaves de acesso)'),
          ('06/11/2026',13279.29,'PIX do advogado (acordo judicial) – competência jul/2025 dentro do repasse: R$ 622,31','Balancete detalhado: competência jul/2025 = R$ 522,31; "Multas e juros" de novembro = R$ 100,00','Confirmar se os R$ 100,00 foram separados como multa/juros do acordo (o total confere)'),
          ('Vários',None,'Favorecido "Luiz Marcelo de Godoy" (telhado e calhas)','Fornecedor cadastrado como "Luiz Marcelo de Gocoy"','Corrigir o nome no cadastro de fornecedores')]:
    row(ws,r,[r-r0+1,*d,None],fmts={3:NUM}); r+=1
status(ws,'G',r0,r-1)
r+=1; ws.merge_cells(start_row=r,start_column=1,end_row=r,end_column=7)
c=ws.cell(r,1,'Nenhum item acima altera saldo ou resultado: os saldos de fim de mês e o total de cada conta de despesa conferem entre extrato e AcolWeb nos 12 meses. São ajustes de cadastro e classificação.')
c.font=Font(name=F,italic=True,size=9); c.alignment=Alignment(wrap_text=True); ws.row_dimensions[r].height=26

# 2 fechamento de novembro
w2=sheet('Fechamento de novembro','DIFERENÇA DE DATA – FECHAMENTO DE NOVEMBRO/2026',[5,44,16,50,18])
r=4; hdr(w2,r,['Nº','Item','Valor (R$)','O que fazer','Situação']); r+=1; r0=r
for d in [('Taxas recebidas de 20 a 23/11/2026, já lançadas no AcolWeb e ainda não presentes no extrato salvo (que vai até 19/11)',1413.22,'Salvar na pasta 11_2026 o extrato do Sicredi posterior a 23/11 e conferir os recebimentos'),
          ('Débito automático da Copel agendado para 26/11/2026',603.91,'Lançar no AcolWeb após o débito'),
          ('Saldo da conta principal: AcolWeb R$ 28.202,25 × extrato de 19/11 R$ 26.789,03',1413.22,'Some após o extrato atualizado (mesma origem do item 1)')]:
    row(w2,r,[r-r0+1,*d,None],fmts={3:NUM}); r+=1
status(w2,'E',r0,r-1,'"Pendente,Resolvido"')

# 3 pendências antes da AGO
w3=sheet('Pendências antes da AGO','PONTOS A RESOLVER ANTES DA AGO DE 26/11/2026',[5,30,70,18])
r=4; hdr(w3,r,['Nº','Assunto','O que falta','Situação']); r+=1; r0=r
for a,b in [('Pintura do estacionamento','R$ 25.000,00 pagos × R$ 20.000,00 aprovados (R$ 26.500,00 com a lavagem do teto). Quem aprovou a diferença? Pedir nota fiscal e contrato da Fidelidade Drywall.'),
 ('Pintura da fachada','R$ 47.500,00 pagos × contrato de R$ 45.000,00 (dentro dos R$ 48.000,00 aprovados). Houve aditivo ou serviço extra?'),
 ('Pintura dos corredores','Nenhum pagamento no período. Foi executada, ficou para 2027 ou o fundo de R$ 70,00 foi usado no estacionamento?'),
 ('Notas fiscais faltantes','Fidelidade Drywall: R$ 25.000,00 (pintura) + R$ 1.500,00 (lavagem) + R$ 1.680,00 (iluminação da rua). Tintas Verginia: R$ 1.600,00.'),
 ('Retenções fiscais','INSS de 11% não retido nas NFS-e da Santos Aleluia (Lei 8.212/91, art. 31; IN RFB 2.110/2022). NFS-e 23 com ISS em Araucária – devido em Fazenda Rio Grande (LC 116/03, art. 3º, III). Verificar as notas da Fidelidade quando chegarem.'),
 ('Fundo de reserva sem conta própria','Arrecadou R$ 7.080,00 no período, mas a conta do fundo segue em R$ 284,50: o dinheiro está na conta principal (Convenção, art. 41). Sugerir na AGO aplicação mensal separada.'),
 ('Fundo de pintura – valor exato','O saldo de R$ 3.451,61 parte de duas premissas: toda a poupança de 30/11/2025 (R$ 33.456,65) era fundo de pintura; e R$ 70 de cada R$ 100 pagos à parte (aptos 209, 301, 303, 305, 310 e 308). Pedir o relatório do AcolWeb com a composição do boleto por item.'),
 ('Inadimplência por unidade','Pedir o relatório de inadimplência por unidade para informar na AGO o número de unidades que compõem os R$ 280,54 (sem nomes).'),
 ('Divulgação e parecer','Enviar a prestação aos condôminos antes da AGO (Convenção, art. 6º, § 2º) e colher o parecer do conselho fiscal (Brenda Trento, apto 208).')]:
    row(w3,r,[r-r0+1,a,b,None],h=48); r+=1
status(w3,'D',r0,r-1,'"Pendente,Resolvido,Levar à AGO"')
wb.save(OUT); print(OUT)
