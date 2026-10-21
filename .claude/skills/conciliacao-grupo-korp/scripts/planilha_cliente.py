import pickle,collections,datetime
import openpyxl
from openpyxl.styles import Font,PatternFill,Alignment,Border,Side
from openpyxl.utils import get_column_letter as L
ext,raz,falt,resto=pickle.load(open('res.pkl','rb'))
M=['Janeiro','Fevereiro','Março','Abril','Maio','Junho','Julho','Agosto','Setembro','Outubro']
INI=333723.41
wb=openpyxl.Workbook()
NAVY=PatternFill('solid',fgColor='1F3864'); thin=Side(style='thin',color='BBBBBB')
def hdr(ws,row=1):
    for c in ws[row]:
        if c.value is not None:
            c.font=Font(bold=True,color='FFFFFF'); c.fill=NAVY; c.alignment=Alignment(wrap_text=True,vertical='center',horizontal='center')
def widths(ws,w):
    for i,x in enumerate(w,1): ws.column_dimensions[L(i)].width=x
# ---------- mensal
wm=wb.active; wm.title='Resumo mensal'
wm.append(['Mês','Saldo inicial','Entradas no extrato','Saídas no extrato','Saldo final EXTRATO','Débitos no razão','Créditos no razão','Saldo final RAZÃO','Diferença acumulada (razão − extrato)','Diferença do mês','Situação do mês'])
saldo=INI; rsal=INI
rows=[]
for i,m in enumerate(M,1):
    em=[e for e in ext if e['d'].month==i]; rm=[r for r in raz if r['d'].month==i]
    ent=round(sum(e['sv'] for e in em if e['sv']>0),2); sai=round(-sum(e['sv'] for e in em if e['sv']<0),2)
    deb=round(sum(r['deb'] for r in rm),2); cred=round(sum(r['cred'] for r in rm),2)
    sf=round(saldo+ent-sai,2); rf=round(rsal+deb-cred,2)
    rows.append((m+('/2026 (até 20/10)' if i==10 else '/2026'),saldo,ent,sai,sf,deb,cred,rf))
    saldo=sf; rsal=rf
for k,(m,si,ent,sai,sf,deb,cred,rf) in enumerate(rows,2):
    wm.append([m,si,ent,sai,f'=B{k}+C{k}-D{k}',deb,cred,f'=B{k}+F{k}-G{k}' if k==2 else f'=H{k-1}+F{k}-G{k}',f'=H{k}-E{k}',f'=ROUND((F{k}-G{k})-(C{k}-D{k}),2)',f'=IF(ABS(J{k})<0.005,"Conciliado","DIVERGENTE")'])
wm['B2']=INI
for k in range(3,12): wm[f'B{k}']=f'=E{k-1}'
n=len(rows)+2
wm.append(['TOTAL DO PERÍODO',INI,f'=SUM(C2:C{n-1})',f'=SUM(D2:D{n-1})',f'=E{n-1}',f'=SUM(F2:F{n-1})',f'=SUM(G2:G{n-1})',f'=H{n-1}',f'=H{n}-E{n}',f'=SUM(J2:J{n-1})',f'=IF(ABS(J{n})<0.005,"Conciliado","DIVERGENTE")'])
hdr(wm); widths(wm,[24,16,18,18,20,18,18,20,22,18,16]); wm.row_dimensions[1].height=36
for row in wm.iter_rows(min_row=2):
    for c in row[1:10]: c.number_format='#,##0.00;[Red]-#,##0.00'
    for c in row: c.border=Border(bottom=thin)
for c in wm[wm.max_row]: c.font=Font(bold=True)
red=PatternFill('solid',fgColor='F8CBAD'); grn=PatternFill('solid',fgColor='C6EFCE')
for k in range(2,wm.max_row+1):
    pass
from openpyxl.formatting.rule import CellIsRule,FormulaRule
wm.conditional_formatting.add(f'K2:K{wm.max_row}',CellIsRule(operator='equal',formula=['"DIVERGENTE"'],fill=red))
wm.conditional_formatting.add(f'K2:K{wm.max_row}',CellIsRule(operator='equal',formula=['"Conciliado"'],fill=grn))
wm.freeze_panes='B2'
# ---------- diferenças
wd=wb.create_sheet('Diferenças')
wd.append(['Nº','Mês','Data','Onde está','N. Lanc (razão)','Histórico','Valor (R$)','Quanto o razão fica ACIMA do extrato (R$)','Conta sugerida (plano Korp)','O que fazer'])
diffs=[]
T=[r for r in resto if 'TED TRANSFERENCIA' in r['obs']]
for r in sorted(T,key=lambda x:x['d']):
    diffs.append((r['d'],'Só no RAZÃO',int(r['n']),r['obs'],abs(r['sv']),r['sv'],'1.1.1.2.5 - Transferência de recursos (2872)',
      'Lançado a DÉBITO na conta Sicredi (entrada), mas o extrato Sicredi não tem esse movimento. Conferir no extrato do Itaú-DCK: se a TED saiu do Sicredi, falta no extrato/lançamento invertido; se entrou do Itaú, ajustar a descrição. Estornar ou corrigir o lançamento.'))
for e in sorted([e for e in falt if 'TARIFA' in (e['desc'] or '')],key=lambda x:x['d']):
    diffs.append((e['d'],'Só no EXTRATO',None,f"{e['desc']} - {e['inf']}",abs(e['sv']),-e['sv'],'3.1.3.3.1.1 - Despesas Bancárias (2698)','Tarifa de cobrança debitada no extrato e não lançada: o saldo do razão fica maior que o do banco. Lançar D 2698 / C 2871.'))
diffs.sort(key=lambda x:(x[0],x[1]))
for i,(d,onde,nl,h,v,ef,conta,acao) in enumerate(diffs,1):
    wd.append([i,M[d.month-1],d,onde,nl if nl else 'NÃO LANÇADO',h,v,None,conta,acao])
    k=wd.max_row
    wd[f'H{k}']= f'=G{k}'
k=wd.max_row
wd.append(['','','','','','TOTAL (razão acima do extrato)','',f'=SUM(H2:H{k})','',''])
wd.append(['','','','','','Conferência: diferença do Resumo mensal','','=\'Resumo mensal\'!I'+str(n),'',''])
wd.append(['','','','','','Diferença não explicada','',f'=ROUND(H{k+1}-H{k+2},2)','',''])
hdr(wd); widths(wd,[5,12,12,15,16,62,14,26,38,80]); wd.row_dimensions[1].height=40
for row in wd.iter_rows(min_row=2):
    for c in row: c.alignment=Alignment(wrap_text=True,vertical='top'); c.border=Border(bottom=thin)
    row[2].number_format='dd/mm/yyyy'; row[6].number_format='#,##0.00'; row[7].number_format='#,##0.00;[Red]-#,##0.00'
for r_ in range(k+1,k+4):
    for c in wd[r_]: c.font=Font(bold=True)
for r_ in range(2,k+1):
    wd[f'D{r_}'].fill=PatternFill('solid',fgColor='FFE699' if wd[f'D{r_}'].value=='Só no RAZÃO' else 'BDD7EE')
wd.freeze_panes='A2'
# ---------- por mês das diferenças (resumo)
# ---------- agrupamentos conferidos
wg=wb.create_sheet('Lançamentos agrupados')
wg.append(['Data','Movimentos no extrato','Linhas no razão','Valor líquido extrato','Valor líquido razão','Diferença','Situação','Descrição dos movimentos do extrato'])
de=collections.defaultdict(list); dr=collections.defaultdict(list)
for e in falt:
    if 'TARIFA' not in (e['desc'] or ''): de[e['d']].append(e)
for r in resto:
    if 'TED TRANSFERENCIA' not in r['obs']: dr[r['d']].append(r)
for d in sorted(set(de)|set(dr)):
    se=round(sum(x['sv'] for x in de[d]),2); sr=round(sum(x['sv'] for x in dr[d]),2)
    if len(de[d])==0 or len(dr[d])==0: continue
    desc='; '.join(f"{x['desc'][:30]} ({x['sv']:,.2f})" for x in de[d][:6])+(' ...' if len(de[d])>6 else '')
    wg.append([d,len(de[d]),len(dr[d]),se,sr,None,None,desc]); k=wg.max_row
    wg[f'F{k}']=f'=E{k}-D{k}'; wg[f'G{k}']=f'=IF(ABS(F{k})<0.005,"Fecha no dia","Ver aba Diferenças")'
hdr(wg); widths(wg,[12,14,12,18,18,14,20,100]); wg.row_dimensions[1].height=36
for row in wg.iter_rows(min_row=2):
    row[0].number_format='dd/mm/yyyy'
    for c in row[3:6]: c.number_format='#,##0.00;[Red]-#,##0.00'
    for c in row: c.alignment=Alignment(wrap_text=True,vertical='top'); c.border=Border(bottom=thin)
# ---------- linhas do extrato x razão contadas
wr=wb.create_sheet('Resumo')
nm=len(ext); nr=len(raz)
tot_dif=round(rsal-saldo,2)
lines=[['DCK SERVIÇOS DE T.I. LTDA - EPP - CNPJ 13.645.287/0001-59 (Domínio 144)'],['Conferência extrato × razão - conta 2871 Banco Sicredi - 02/01/2026 a 20/10/2026'],[],
['Saldo inicial (01/01/2026)',INI],['Saldo final do extrato (20/10/2026)',saldo],['Saldo final do razão (20/10/2026)',rsal],['Diferença (razão acima do extrato)',tot_dif],[],
['Movimentos no extrato',nm],['Lançamentos no razão',nr],['Meses conciliados',sum(1 for r_ in rows if True)],[],
['Resultado'],['Janeiro a maio e setembro fecham movimento a movimento. As diferenças do mês estão em junho, julho, agosto e outubro; a diferença de junho a agosto segue acumulada no saldo do razão até outubro.'],
['1) TEDs "SIC/DCK para ITAU-DCK" lançadas no razão sem movimento no extrato Sicredi: 22/06 (500,00), 10/07 (400.000,00 e 150.000,00), 17/07 (400.000,00) e 17/08 (400.000,00) = 1.350.500,00.'],
['2) Tarifas de cobrança de outubro (COB) cobradas no extrato e não lançadas no razão: 275,22.'],
['Total explicado: 1.350.775,22 (ver aba Diferenças). Diferença não explicada: 0,00.'],[],
['Abas'],['Resumo mensal','Saldos e totais de cada mês, extrato × razão'],['Diferenças','Cada divergência com data, valor, conta sugerida e o que fazer'],['Lançamentos agrupados','Dias em que um movimento do extrato (lote CNAB, fatura de cartão) está dividido em várias linhas no razão e fecha no dia']]
for l in lines: wr.append(l)
wr['A1'].font=Font(bold=True,size=13); wr['A2'].font=Font(bold=True)
for r_ in (4,5,6,7): wr[f'B{r_}'].number_format='#,##0.00'
for r_ in (13,19): wr[f'A{r_}'].font=Font(bold=True)
wr.column_dimensions['A'].width=60; wr.column_dimensions['B'].width=70
wr['B7']='=ROUND(B6-B5,2)'
wb.move_sheet('Resumo',offset=-3)
wb.save('Validacao_DCK_Sicredi_Jan-Out_2026.xlsx')
print(len(diffs),round(sum(d[5] if d[1]=='Só no RAZÃO' else -d[4] for d in diffs),2))
for r in rows: print(r[0],r[4],r[7],round(r[7]-r[4],2))
