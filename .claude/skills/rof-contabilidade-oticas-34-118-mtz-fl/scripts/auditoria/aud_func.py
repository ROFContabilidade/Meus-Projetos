import csv,sys,glob,re,openpyxl
from collections import defaultdict
S=sys.argv[1]
fol=list(csv.DictReader(open(S+'/dados/folha_full.csv'),delimiter=';'))
emp={f['cpf']:f['nome'] for f in fol if f['tipo']=='empregado'}
key={c:' '.join(n.split()[:2]) for c,n in emp.items()}
def comp_ant(m,a): return (12,a-1) if m==1 else (m-1,a)
dev=defaultdict(float)  # (cpf,mes pagamento) -> devido
for f in fol:
    if f['tipo']!='empregado': continue
    m,a=int(f['competencia'][:2]),int(f['competencia'][3:])
    if a==2026: dev[(f['cpf'],m)]+=float(f['adiantamento'])
    nm,na=(1,a+1) if m==12 else (m+1,a)
    if na==2026 and nm<=9: dev[(f['cpf'],nm)]+=float(f['liquido'])
pago=defaultdict(float); porconta=defaultdict(lambda:defaultdict(float))
for f in sorted(glob.glob(S+'/saida/*/Conferencia_*.xlsx')):
    for r in openpyxl.load_workbook(f,read_only=True)['Matriz'].iter_rows(min_row=2,values_only=True):
        if r[8]=='OMITIDO' or r[4]>=0: continue
        d=re.sub(r'[.\-/]','',(r[2] or '')+' '+str(r[3] or '')).upper()
        cpf=next((c for c in emp if c in d),None) or next((c for c,k in key.items() if k in (r[2] or '').upper()),None)
        if not cpf: continue
        m=int(r[0][3:5]); conta=r[5]
        porconta[cpf][conta]+=-r[4]
        if conta in('187','5','542'): pago[(cpf,m)]+=-r[4]
print('empregado | devido 01-09 (adiant.+líquido anterior) | pago 187+5+542 | diferença | por conta')
T=[0,0]
for c,n in emp.items():
    dv=sum(v for (cc,m),v in dev.items() if cc==c); pg=sum(v for (cc,m),v in pago.items() if cc==c); T[0]+=dv; T[1]+=pg
    print(f'{n[:28]:28} | {dv:10.2f} | {pg:10.2f} | {pg-dv:10.2f} | {dict((k,round(v,2)) for k,v in porconta[c].items())}')
print('TOTAL',round(T[0],2),round(T[1],2),round(T[1]-T[0],2))
print('\nmês a mês (todos): mês | devido | pago')
for m in range(1,10):
    print(m, round(sum(v for (c,mm),v in dev.items() if mm==m),2), round(sum(v for (c,mm),v in pago.items() if mm==m),2))
