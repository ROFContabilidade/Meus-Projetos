# Lista prática para corrigir a integração no Domínio (Matriz 140) - uma linha por lançamento
from openpyxl import Workbook
from openpyxl.styles import Font, Alignment, Border, Side, PatternFill
from openpyxl.worksheet.datavalidation import DataValidation
F=lambda **k: Font(**{'name':'Arial','size':11,**k})
s=Side(style='thin',color='BFBFBF'); B=Border(top=s,bottom=s,left=s,right=s)
HEAD=PatternFill('solid',fgColor='1F4E78'); NOVO=PatternFill('solid',fgColor='C6EFCE'); EDIT=PatternFill('solid',fgColor='FFF2CC'); CCF=PatternFill('solid',fgColor='DDEBF7')
CCN={2:'DES BACKOFFICE',10:'CONSULTORIA INTERNA E GP',15:'ADM FINANCEIRO',18:'SD INFRAESTRUTURA',30:'SD SUPORTE',31:'DES PRODUÇÃO/SUPORTE',41:'COM HANTERS'}
INSS=['INSS Empresa','INSS Terceiros','INSS Acid. Trabalho']
L=[]  # cc, aba, lanc, descr, dh, dn, ch, cn
def add(cc,aba,lanc,desc,dh,dn,ch,cn): L.append((cc,aba,lanc,desc,dh,dn,ch,cn))
for x in INSS: add(2,'Empresa','(ver nota)',x,'3142','2885','2531','')
add(10,'Folha','821','INSS DIFERENÇA FÉRIAS','2524','2521','2531','')
add(10,'Folha','806','MÉDIA HORAS FÉRIAS (invertido)','2524','3098','3098','2524')
add(15,'Folha','8781','DIAS NORMAIS','2884','2994','2521','')
add(15,'Folha','318','ADICIONAL NOTURNO 20%','2884','2994','2521','')
add(15,'Folha','854','REFLEXO ADIC. NOTURNO DSR','2884','2994','2521','')
add(15,'Folha','992','TROCO DO MÊS','2884','2994','2521','')
add(15,'Folha','993','TROCO MÊS ANTERIOR','2521','','2884','2994')
add(15,'Folha','302','HORAS EXTRAS 75%','2904','3004','2521','')
add(15,'Folha','250','REFLEXO EXTRAS DSR','2904','3004','2521','')
add(15,'Folha','606','CONTRIBUIÇÃO ASSISTENCIAL','2521','','2905','3145')
add(15,'Folha','346','VALE TRANSPORTE (invertido)','3144','2521','2521','3144')
add(15,'Empresa','(ver nota)','FGTS','2886','2997','2530','')
for r,d in (('8781','DIAS NORMAIS'),('318','ADICIONAL NOTURNO 20%'),('854','REFLEXO ADIC. NOTURNO DSR'),('992','TROCO DO MÊS'),('8699','MÉDIA AFAST. DOENÇA'),('8870','DIAS AFAST. P/ DOENÇA')): add(18,'Folha',r,d,'2884','2891','2521','')
for r,d in (('993','TROCO MÊS ANTERIOR'),('8069','HORAS FALTAS PARCIAL')): add(18,'Folha',r,d,'2521','','2884','2891')
for r,d in (('302','HORAS EXTRAS 75%'),('200','HORAS EXTRAS 100%'),('250','REFLEXO EXTRAS DSR')): add(18,'Folha',r,d,'2904','2917','2521','')
add(18,'Folha','606','CONTRIBUIÇÃO ASSISTENCIAL','2521','','2905','2923')
add(18,'Folha','8111','DESCONTO PLANO DE SAÚDE','2521','','3019','2918')
add(18,'Folha','295','COPARTICIPAÇÃO SAÚDE/DENTAL','2521','','3019','2918')
add(18,'Empresa','(ver nota)','FGTS','2886','2913','2530','')
for x in INSS: add(18,'Empresa','(ver nota)',x,'2885','3078','2531','')
add(30,'Folha','821','INSS DIFERENÇA FÉRIAS','2524','2521','2531','')
add(31,'Folha','732','DESC. EMP. CRED. TRAB. (consignado)','2521','','2891','3137')
for x in INSS: add(31,'Empresa','(ver nota)',x,'3078','3142','2531','')
add(31,'Cadastro do CC','—','CC contábil do centro de custo 31','CC 1 Desenvolvimento','CC 2 Qualidade','','')
for r,d in (('8781','DIAS NORMAIS'),('992','TROCO DO MÊS')): add(41,'Folha',r,d,'2884','2323','2521','')
for r,d in (('993','TROCO MÊS ANTERIOR'),('8069','HORAS FALTAS PARCIAL')): add(41,'Folha',r,d,'2521','','2884','2323')
for r,d in (('302','HORAS EXTRAS 75%'),('250','REFLEXO EXTRAS DSR')): add(41,'Folha',r,d,'2904','2577','2521','')
add(41,'Folha','499','AJUDA DE CUSTO HOME OFFICE','2888','2578','2521','')
add(41,'Folha','606','CONTRIBUIÇÃO ASSISTENCIAL','2521','','2905','3148')
add(41,'Folha','8783','DIAS FÉRIAS','2907','2576','2524','')
add(41,'Empresa','(ver nota)','FGTS','2886','2334','2530','')
for x in INSS: add(41,'Empresa','(ver nota)',x,'2885','2332','2531','')

wb=Workbook(); ws=wb.active; ws.title='Corrigir no Domínio'
ws['A1']='KORP MATRIZ (140) — O que corrigir na integração contábil do Domínio'; ws['A1'].font=F(bold=True,size=14)
ws['A2']='Como usar: abra o Centro de custo → aba indicada → digite o Nº do lançamento → troque só as contas em VERDE → marque "Feito?".'; ws['A2'].font=F(italic=True,color='444444')
ws['A3']='Nº do lançamento = código da rubrica (ex.: 8783 = DIAS FÉRIAS). Aba Empresa (FGTS/INSS): procure pela descrição com os botões >>.'; ws['A3'].font=F(italic=True,color='C00000')
H=['CC','Nome do CC','Aba','Nº Lançamento','Descrição','Débito HOJE','Débito NOVO','Crédito HOJE','Crédito NOVO','Feito?','Observação']
for c,h in enumerate(H,1):
  x=ws.cell(5,c,h); x.font=F(bold=True,color='FFFFFF'); x.fill=HEAD; x.border=B; x.alignment=Alignment(horizontal='center',vertical='center',wrap_text=True)
r=6
for cc,aba,lanc,desc,dh,dn,ch,cn in L:
  vals=[cc,CCN[cc],aba,lanc,desc,dh,dn or 'não muda',ch,cn or 'não muda','','']
  for c,v in enumerate(vals,1):
    x=ws.cell(r,c,int(v) if isinstance(v,str) and v.isdigit() else v); x.font=F(); x.border=B
    x.alignment=Alignment(horizontal='left' if c in (2,5,11) else 'center',vertical='center')
    if c in (1,2): x.fill=CCF; x.font=F(bold=True)
    if c in (7,9):
      if (dn if c==7 else cn): x.fill=NOVO; x.font=F(bold=True,size=12)
      else: x.font=F(color='999999')
    if c in (10,11): x.fill=EDIT
  r+=1
last=r-1
ws.cell(r+1,5,'Feitos:').font=F(bold=True); ws.cell(r+1,5).alignment=Alignment(horizontal='right')
ws.cell(r+1,6,f'=COUNTIF(J6:J{last},"Sim")&" de {last-5}"').font=F(bold=True)
dv=DataValidation(type='list',formula1='"Sim,Não"',allow_blank=True); ws.add_data_validation(dv); dv.add(f'J6:J{last}')
for c,w in zip('ABCDEFGHIJK',[6,26,15,14,36,13,13,13,13,9,30]): ws.column_dimensions[c].width=w
ws.freeze_panes='D6'; ws.auto_filter.ref=f'A5:K{last}'

w2=wb.create_sheet('Conferir outras abas')
w2['A1']='Abas de Férias e Rescisão dos CCs 15, 18 e 41 — abra o lançamento pelo Nº; se a conta estiver como "Se estiver", troque pela verde.'; w2['A1'].font=F(bold=True,size=12)
w2['A2']='Se o lançamento já estiver com a conta verde, só marque "Sim". Se o Nº não existir nesse CC, marque "Não existe". Na Rescisão, o outro lado das verbas deve ser 2523.'; w2['A2'].font=F(italic=True,color='444444')
H2=['CC','Nome do CC','Aba','Nº Lançamento','Descrição','Lado','Se estiver (DES)','Trocar para','Feito?','Observação']
for c,h in enumerate(H2,1):
  x=w2.cell(4,c,h); x.font=F(bold=True,color='FFFFFF'); x.fill=HEAD; x.border=B; x.alignment=Alignment(horizontal='center',vertical='center',wrap_text=True)
DES=dict(sal=2884,fer=2907,d13=3009,he=2904,contrib=2905,ajuda=2888)
ACC={15:dict(sal=2994,fer=3017,d13=3017,he=3004,contrib=3145,ajuda=None),
     18:dict(sal=2891,fer=3152,d13=3010,he=2917,contrib=2923,ajuda=3146),
     41:dict(sal=2323,fer=2576,d13=2324,he=2577,contrib=3148,ajuda=2578)}
RUBS=[('Folha',k,'fer','Débito',n) for k,n in [(8783,'DIAS FÉRIAS'),(805,'MÉDIA VALOR FÉRIAS'),(806,'MÉDIA HORAS FÉRIAS'),(931,'1/3 DAS FÉRIAS'),(8163,'TROCO FÉRIAS'),(940,'DIFERENÇA DE FÉRIAS'),(8112,'DIFERENÇA DE 1/3 DE FÉRIAS'),(8189,'DIFERENÇA MÉDIA HORA FÉRIAS')]]
RUBS+=[('Rescisão',k,'sal','Débito',n) for k,n in [(9180,'SALDO DE SALÁRIO DIAS'),(9591,'AVISO PRÉVIO'),(9596,'MÉDIA VALOR AVISO PRÉVIO'),(9597,'MÉDIA HORAS AVISO PRÉVIO')]]
RUBS+=[('Rescisão',k,'fer','Débito',n) for k,n in [(28,'FÉRIAS VENCIDAS'),(29,'FÉRIAS PROPORCIONAIS'),(64,'1/3 FÉRIAS RESCISÃO'),(811,'FÉRIAS 1/12 INDENIZADO'),(815,'MÉDIA HR FÉR PROPORCIONAL'),(816,'MÉDIA VL FÉR PROPORCIONAL'),(818,'MÉDIA HR FÉRIAS VENCIDAS'),(819,'MÉDIA VL FÉRIAS VENCIDAS'),(8126,'1/3 FÉRIAS INDENIZADAS RESC'),(8156,'MÉDIA VALOR FÉRIAS 1/12 INDENIZADO'),(8157,'MÉDIA HORAS FÉRIAS 1/12 INDENIZADO'),(8169,'1/3 FÉRIAS PROPORCIONAIS RESCISÃO')]]
RUBS+=[('Rescisão',k,'d13','Débito',n) for k,n in [(8550,'13 SALÁRIO RESCISÃO'),(8551,'MÉDIA HORAS 13º RESCISÃO'),(8552,'MÉDIA VALOR 13º RESCISÃO'),(9592,'13º 1/12 INDENIZADO'),(9600,'MÉDIA VALOR 13º 1/12 INDENIZADO'),(9601,'MÉDIA HORAS 13º 1/12 INDENIZADO')]]
RUBS+=[('Rescisão',k,'he','Débito',n) for k,n in [(302,'HORAS EXTRAS 75%'),(200,'HORAS EXTRAS 100%'),(250,'REFLEXO EXTRAS DSR')]]
RUBS+=[('Rescisão',606,'contrib','Crédito','CONTRIBUIÇÃO ASSISTENCIAL')]
RUBS+=[('Rescisão',k,'ajuda','Crédito',n) for k,n in [(657,'VALE REFEIÇÃO NÃO UTILIZADO'),(275,'VALE REFEIÇÃO NÃO UTILIZADO'),(253,'DESC VALE ALIMENTAÇÃO NÃO UTILIZADO'),(665,'AJUDA DE CUSTO NÃO UTILIZADO'),(511,'DESCONTO AJUDA DE CUSTO HOME OFFICE')]]
r=5
for cc,A in ACC.items():
  for aba,k,g,lado,n in RUBS:
    if A[g] is None: continue
    for c,v in enumerate([cc,CCN[cc],aba,k,n,lado,DES[g],A[g],'',''],1):
      x=w2.cell(r,c,v); x.font=F(); x.border=B; x.alignment=Alignment(horizontal='left' if c in (2,5,10) else 'center')
      if c in (1,2): x.fill=CCF; x.font=F(bold=True)
      if c==8: x.fill=NOVO; x.font=F(bold=True,size=12)
      if c in (9,10): x.fill=EDIT
    r+=1
last2=r-1
w2.cell(r+1,5,'Aba Empresa / Provisões (FGTS e INSS de férias, 13º e rescisão): sem Nº — procurar pela descrição.').font=F(italic=True,color='C00000')
r+=1
for cc,(fg,ins) in {15:(2997,2996),18:(2913,3078),41:(2334,2332)}.items():
  r+=1; w2.cell(r+1,5,f'CC {cc} {CCN[cc]}: FGTS 2886 → {fg}  ·  INSS 2885 → {ins}').font=F()
dv2=DataValidation(type='list',formula1='"Sim,Não existe"',allow_blank=True); w2.add_data_validation(dv2); dv2.add(f'I5:I{last2}')
for c,w in zip('ABCDEFGHIJ',[6,24,11,14,38,9,14,13,12,28]): w2.column_dimensions[c].width=w
w2.freeze_panes='D5'; w2.auto_filter.ref=f'A4:J{last2}'
wb.save('Corrigir_Integracao_Dominio_Matriz.xlsx'); print(last-5,'linhas;',last2-4,'para conferir')
