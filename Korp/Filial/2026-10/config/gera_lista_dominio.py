# Lista prática para corrigir a integração no Domínio (Filial 145) - 10/2026
from openpyxl import Workbook
from openpyxl.styles import Font, Alignment, Border, Side, PatternFill
from openpyxl.worksheet.datavalidation import DataValidation
F=lambda **k: Font(**{'name':'Arial','size':11,**k})
s=Side(style='thin',color='BFBFBF'); B=Border(top=s,bottom=s,left=s,right=s)
HEAD=PatternFill('solid',fgColor='1F4E78'); NOVO=PatternFill('solid',fgColor='C6EFCE'); EDIT=PatternFill('solid',fgColor='FFF2CC'); CCF=PatternFill('solid',fgColor='DDEBF7')
CCN={5:'COM BRUNO ECKS',10:'ADM FINANCEIRO',12:'DES BACKOFFICE',13:'DES PRODUÇÃO',15:'CS CUSTOMER SUCCESS'}
# cc, aba, lanc, descrição, débito hoje, débito novo, crédito hoje, crédito novo, observação
L=[(5,'Folha',8781,'DIAS NORMAIS','2323','','2531','2521',''),
   (5,'Folha',853,'REFLEXO COMISSÕES DSR','2867','','2524','2521',''),
   (10,'Folha',8813,'BOLSA AUX DIAS AFASTAMENTO DIREITOS INT','2995','','2521','2526',''),
   (12,'Folha',812,'INSS FÉRIAS','2524','','0251','2531','0251 não existe'),
   (12,'Folha',937,'ADIANTAMENTO DE FÉRIAS','não existe','2524','não existe','2463','Criar lançamento novo (Novo) e selecionar a rubrica 937'),
   (13,'Rescisão',511,'DESCONTO AJUDA DE CUSTO HOME OFFICE','0252','2523','2888','','0252 não existe'),
   (13,'Rescisão',989,'INSS 13 SAL. RESCISÃO','2523','','2888','2531',''),
   (13,'Rescisão',9601,'MÉDIA HORAS 13º 1/12 INDENIZADO','3009','','2823','2523','2823 digitada errada'),
   (15,'Rescisão',9601,'MÉDIA HORAS 13º 1/12 INDENIZADO','2524','2324','2523','',''),
   (15,'Empresa',23,'INSS TERCEIROS 13º INDENIZADO','2332','','0251','2531','0251 não existe')]
H=[(5,'Folha',302,'HORAS EXTRAS 50%','HORAS EXTRAS 75%'),(13,'Folha',8781,'DESC VALE REFEIÇÃO','DIAS NORMAIS'),
   (15,'Rescisão',8550,'13 SALARIO ADIANTADO','13 SALARIO RESCISAO'),(13,'Empresa',24,'INSS Terceiros 13º Indenizado','INSS Acid. Trabalho 13º Indenizado')]
wb=Workbook(); ws=wb.active; ws.title='Corrigir contas'
ws['A1']='KORP FILIAL (145) — O que corrigir na integração do Domínio (10/2026)'; ws['A1'].font=F(bold=True,size=14)
ws['A2']='Abra o Centro de custo → aba → digite o Nº do lançamento → troque só o que está em VERDE → marque "Feito?".'; ws['A2'].font=F(italic=True,color='444444')
def cab(w,row,hs):
  for c,h in enumerate(hs,1):
    x=w.cell(row,c,h); x.font=F(bold=True,color='FFFFFF'); x.fill=HEAD; x.border=B; x.alignment=Alignment(horizontal='center',vertical='center',wrap_text=True)
cab(ws,4,['CC','Nome do CC','Aba','Nº Lançamento','Descrição','Débito HOJE','Débito NOVO','Crédito HOJE','Crédito NOVO','Feito?','Observação'])
r=5
for cc,aba,lc,d,dh,dn,ch,cn,ob in L:
  for c,v in enumerate([cc,CCN[cc],aba,lc,d,dh,dn or 'não muda',ch,cn or 'não muda','',ob],1):
    x=ws.cell(r,c,int(v) if isinstance(v,str) and v.isdigit() and c in (6,7,8,9) and not v.startswith('0') else v); x.font=F(); x.border=B
    x.alignment=Alignment(horizontal='left' if c in (2,5,11) else 'center',vertical='center',wrap_text=c==11)
    if c in (1,2): x.fill=CCF; x.font=F(bold=True)
    if c in (7,9): 
      if (dn if c==7 else cn): x.fill=NOVO; x.font=F(bold=True,size=12)
      else: x.font=F(color='999999')
    if c in (6,8) and str(v).startswith('0'): x.font=F(bold=True,color='C00000')
    if c==10: x.fill=EDIT
  ws.row_dimensions[r].height=30; r+=1
last=r-1
ws.cell(r+1,5,'Feitos:').font=F(bold=True); ws.cell(r+1,5).alignment=Alignment(horizontal='right')
ws.cell(r+1,6,f'=COUNTIF(J5:J{last},"Sim")&" de {last-4}"').font=F(bold=True)
dv=DataValidation(type='list',formula1='"Sim,Não"',allow_blank=True); ws.add_data_validation(dv); dv.add(f'J5:J{last}')
for c,w in zip('ABCDEFGHIJK',[6,24,11,14,40,13,13,13,13,9,36]): ws.column_dimensions[c].width=w
ws.freeze_panes='D5'
w2=wb.create_sheet('Corrigir histórico')
w2['A1']='Só o histórico está errado — as contas estão certas'; w2['A1'].font=F(bold=True,size=14)
cab(w2,3,['CC','Nome do CC','Aba','Nº Lançamento','Histórico HOJE','Histórico CERTO','Feito?'])
r=4
for cc,aba,lc,a,b in H:
  for c,v in enumerate([cc,CCN[cc],aba,lc,a,b,''],1):
    x=w2.cell(r,c,v); x.font=F(); x.border=B; x.alignment=Alignment(horizontal='left' if c in (2,5,6) else 'center')
    if c in (1,2): x.fill=CCF; x.font=F(bold=True)
    if c==6: x.fill=NOVO; x.font=F(bold=True)
    if c==7: x.fill=EDIT
  r+=1
dv2=DataValidation(type='list',formula1='"Sim,Não"',allow_blank=True); w2.add_data_validation(dv2); dv2.add(f'G4:G{r-1}')
w2.cell(r+1,1,'Não precisa mexer: ajuda de custo de estagiário na rescisão (Erik, CC 13) eu corrijo no TXT.').font=F(italic=True,color='444444')
for c,w in zip('ABCDEFG',[6,24,11,14,34,36,9]): w2.column_dimensions[c].width=w
wb.save('Corrigir_Integracao_Dominio_Filial.xlsx'); print('ok')
