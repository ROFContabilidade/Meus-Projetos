# Rubricas não configuradas na integração do Domínio (Filial 145) - relatório de 25/11/2026
from openpyxl import Workbook
from openpyxl.styles import Font, Alignment, Border, Side, PatternFill
from openpyxl.worksheet.datavalidation import DataValidation
F=lambda **k: Font(**{'name':'Arial','size':11,**k})
s=Side(style='thin',color='BFBFBF'); B=Border(top=s,bottom=s,left=s,right=s)
HEAD=PatternFill('solid',fgColor='1F4E78'); CONTA=PatternFill('solid',fgColor='C6EFCE'); EDIT=PatternFill('solid',fgColor='FFF2CC'); CCF=PatternFill('solid',fgColor='DDEBF7')
CCN={7:'DES TECNOLOGIA',12:'DES BACKOFFICE',13:'DES PRODUÇÃO',15:'CS CUSTOMER SUCCESS',17:'DES FISCAL CONTABIL'}
DES=dict(sal=2884,fer=2907,d13=3009,ajuda=2888,inss=2885,fgts=2886,fgtsr=2886)
COM=dict(sal=2323,fer=2576,d13=2324,ajuda=2578,inss=2332,fgts=2334,fgtsr=2335)
FER=[(29,'FERIAS PROPORCIONAIS'),(811,'FERIAS 1/12 INDENIZADO'),(815,'MEDIA HR FER PROPORCIONAL'),(816,'MEDIA VL FER PROPORCIONAL'),(8126,'1/3 FERIAS INDENIZADAS RESC'),(8156,'MEDIA VALOR FERIAS 1/12 INDENIZADO'),(8157,'MEDIA HORAS FERIAS 1/12 INDENIZADO'),(8169,'1/3 FERIAS PROPORCIONAIS RESCISAO')]
D13=[(8550,'13 SALARIO RESCISAO'),(8551,'MEDIA HORAS 13o RESCISAO'),(8552,'MEDIA VALOR 13o RESCISAO'),(9592,'13o 1/12 INDENIZADO'),(9600,'MEDIA VALOR 13o 1/12 INDENIZADO'),(9601,'MEDIA HORAS 13o 1/12 INDENIZADO')]
SAL=[(9180,'SALDO DE SALARIO DIAS'),(9591,'AVISO PREVIO'),(9597,'MEDIA HORAS AVISO PREVIO')]
FGR=[(23,'F.G.T.S DE RESCISAO'),(32,'F.G.T.S 40%'),(35,'FGTS 13o SALARIO RESCISAO'),(9637,'F.G.T.S DE AVISO PRÉVIO')]
INR=[(826,'INSS SOBRE RESCISAO'),(989,'INSS 13 SAL.RESCISAO')]
BOLSA=[(8490,'BOLSA AUXILIO FERIAS PROPORCIONAIS'),(8496,'BOLSA AUXILIO 1/3 FERIAS PROP RESCISAO'),(8797,'DIAS BOLSA AUXILIO')]
IN13=[(6,'INSS Empresa 13o.'),(7,'INSS Terceiros 13o.'),(8,'INSS Acid. Trabalho 13o.'),(22,'INSS Empresa 13º Indenizado'),(23,'INSS Terceiros 13º Indenizado'),(24,'INSS Acid. Trabalho 13º Indenizado')]
G=[]  # (cc, aba, histórico do lançamento, débito, crédito, [rubricas], nota)
def g(cc,aba,h,d,c,rubs,nota=''): G.append((cc,aba,h,d,c,rubs,nota))
g(7,'Folha','DESC. EMP. CRED. TRAB (consignado)',2521,3137,[(9750,'DESC. EMP. CRED. TRAB Nº #CONTRATO')],'Consignado: sempre C 3137')
g(12,'Folha','INSS DIFERENÇA FÉRIAS',2521,2531,[(821,'INSS DIFERENCA FERIAS')],'Desconto no recibo mensal')
g(17,'Folha','AJUDA DE CUSTO',2888,2521,[(745,'AJUDA DE CUSTO')])
g(12,'Empresa','INSS PATRONAL FÉRIAS',2885,2531,[(11,'INSS Empresa Férias'),(12,'INSS Terceiros Férias'),(13,'INSS Acid. Trabalho Férias')])
g(13,'Empresa','INSS PATRONAL 13º',2885,2531,IN13)
g(15,'Empresa','INSS PATRONAL 13º',2332,2531,IN13,'CS usa contas do Comercial')
g(12,'Férias','FÉRIAS',2907,2524,[(8783,'DIAS FERIAS'),(805,'MEDIA VALOR FERIAS'),(806,'MEDIA HORAS FERIAS'),(931,'1/3 DAS FERIAS')])
g(12,'Férias','INSS FÉRIAS',2524,2531,[(812,'INSS FERIAS')])
g(12,'Férias','FGTS FÉRIAS',2886,2530,[(813,'FGTS FERIAS')])
g(7,'Rescisão','BOLSA AUXÍLIO RESCISÃO ESTÁGIO',2910,2526,BOLSA,'Estagiário DES: D 2910 / C 2526 (decisão da skill)')
for cc,A,nt in ((13,DES,''),(15,COM,'CS usa contas do Comercial')):
  g(cc,'Rescisão','SALDO DE SALÁRIO / AVISO PRÉVIO',A['sal'],2523,SAL,nt)
  g(cc,'Rescisão','FÉRIAS RESCISÃO',A['fer'],2523,FER,nt)
  g(cc,'Rescisão','13º SALÁRIO RESCISÃO',A['d13'],2523,D13,nt)
  g(cc,'Rescisão','FGTS RESCISÃO',A['fgtsr'],2530,FGR,('2335 = FGTS s/ rescisões trabalhistas (comercial). ' if cc==15 else '')+nt)
  g(cc,'Rescisão','INSS RESCISÃO',2523,2531,INR,nt)
  g(cc,'Rescisão','VALE REFEIÇÃO NÃO UTILIZADO',2523,A['ajuda'],[(275,'VALE REFEIÇÃO NAO UTILIZADO')],'Desconto na rescisão vai a crédito da Ajuda de Custo do grupo. '+nt)
g(13,'Rescisão','AJUDA DE CUSTO HOME OFFICE',2888,2523,[(499,'AJUDA DE CUSTO - HOME OFFICE')])
g(13,'Rescisão','DESCONTO AJUDA DE CUSTO',2523,2888,[(511,'DESCONTO AJUDA DE CUSTO - HOME OFFICE')])
g(13,'Rescisão','HORAS FALTAS',2523,2884,[(8069,'HORAS FALTAS PARCIAL')])
g(13,'Rescisão','BOLSA AUXÍLIO RESCISÃO ESTÁGIO',2910,2526,BOLSA,'Estagiário DES: D 2910 / C 2526')
g(15,'Rescisão','IRRF RESCISÃO',2523,2533,[(828,'IRRF SOBRE RESCISÃO.')],'CS usa contas do Comercial')
ORD={'Folha':0,'Empresa':1,'Férias':2,'Rescisão':3}
G.sort(key=lambda x:(x[0],ORD[x[1]]))

wb=Workbook(); ws=wb.active; ws.title='Lançamentos a criar'
ws['A1']='KORP FILIAL (145) — Rubricas não configuradas: lançamentos para criar na integração do Domínio'; ws['A1'].font=F(bold=True,size=14)
ws['A2']='Uma linha = um lançamento: CC → aba → "Novo" → Débito e Crédito em verde → selecionar as rubricas da coluna "Rubricas". Se já existir no CC um lançamento com o mesmo débito/crédito, basta incluir as rubricas nele.'; ws['A2'].font=F(italic=True,color='444444')
H=['CC','Nome do CC','Aba','Descrição / histórico','Conta DÉBITO','Conta CRÉDITO','Rubricas (código - nome)','Qtde','Feito?','Observação']
for c,h in enumerate(H,1):
  x=ws.cell(4,c,h); x.font=F(bold=True,color='FFFFFF'); x.fill=HEAD; x.border=B; x.alignment=Alignment(horizontal='center',vertical='center',wrap_text=True)
r=5; tot=0
for cc,aba,h,d,c,rubs,nota in G:
  txt='\n'.join(f'{k} - {n}' for k,n in rubs); tot+=len(rubs)
  for col,v in enumerate([cc,CCN[cc],aba,h,d,c,txt,len(rubs),'',nota],1):
    x=ws.cell(r,col,v); x.font=F(); x.border=B; x.alignment=Alignment(horizontal='left' if col in (2,4,7,10) else 'center',vertical='center',wrap_text=col in (7,10))
    if col in (1,2): x.fill=CCF; x.font=F(bold=True)
    if col in (5,6): x.fill=CONTA; x.font=F(bold=True,size=13)
    if col==9: x.fill=EDIT
    if col==10 and not nota: x.fill=EDIT
  ws.row_dimensions[r].height=max(18,15*len(rubs)+4); r+=1
last=r-1
ws.cell(r+1,7,f'Total: {tot} rubricas em {last-4} lançamentos').font=F(bold=True)
ws.cell(r+1,9,f'=COUNTIF(I5:I{last},"Sim")&" de {last-4}"').font=F(bold=True)
dv=DataValidation(type='list',formula1='"Sim,Não"',allow_blank=True); ws.add_data_validation(dv); dv.add(f'I5:I{last}')
for c,w in zip('ABCDEFGHIJ',[6,22,11,34,12,12,46,7,9,40]): ws.column_dimensions[c].width=w
ws.freeze_panes='E5'; ws.auto_filter.ref=f'A4:J{last}'

w2=wb.create_sheet('Por rubrica')
H2=['CC','Nome do CC','Aba','Rubrica','Descrição','Conta DÉBITO','Conta CRÉDITO']
for c,h in enumerate(H2,1):
  x=w2.cell(1,c,h); x.font=F(bold=True,color='FFFFFF'); x.fill=HEAD; x.border=B; x.alignment=Alignment(horizontal='center')
r=2
for cc,aba,h,d,c,rubs,nota in G:
  for k,n in rubs:
    for col,v in enumerate([cc,CCN[cc],aba,k,n,d,c],1):
      x=w2.cell(r,col,v); x.font=F(); x.border=B; x.alignment=Alignment(horizontal='left' if col in (2,5) else 'center')
      if col in (6,7): x.fill=CONTA; x.font=F(bold=True)
    r+=1
for c,w in zip('ABCDEFG',[6,22,11,10,42,13,13]): w2.column_dimensions[c].width=w
w2.freeze_panes='D2'; w2.auto_filter.ref=f'A1:G{r-1}'
wb.save('Rubricas_Nao_Configuradas_Filial.xlsx'); print(tot,'rubricas,',last-4,'lançamentos')
