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
