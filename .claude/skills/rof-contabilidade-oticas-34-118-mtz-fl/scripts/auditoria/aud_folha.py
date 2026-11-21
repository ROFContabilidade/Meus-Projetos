import csv,sys,glob,re,openpyxl,json
from collections import defaultdict
S=sys.argv[1]; R=list(csv.DictReader(open(S+'/dados/razao34_long.csv'),delimiter=';'))
lb={r['lote'] for r in R if r['conta'] in('8','9','6')}
fol=defaultdict(lambda:defaultdict(float))
for r in R:
    if r['lote'] in lb: continue
    fol[r['conta']][r['data'][3:5]]+=float(r['debito'])-float(r['credito'])
# pagamentos nos TXT (34, inclui espelhos da filial)
pag=defaultdict(lambda:defaultdict(float)); linhas=[]
for f in sorted(glob.glob(S+'/saida/*/Conferencia_*.xlsx')):
    for r in openpyxl.load_workbook(f,read_only=True)['Matriz'].iter_rows(min_row=2,values_only=True):
        if r[8]=='OMITIDO': continue
        v=r[4]; m=r[0][3:5]
        parts=[p.split('=') for p in r[7].split('; ')] if r[7] else [[r[5] if v<0 else r[6], str(abs(v))]]
        for c,x in parts:
            x=float(str(x).replace(',','.')); pag[c][m]+= x if v<0 else -x
        linhas.append(dict(data=r[0],desc=r[2],valor=v,deb=r[5],cred=r[6],part=r[7]))
saldo_ini={'5':0.0,'187':-10629.56,'188':0.0,'192':-16654.59,'191':-15868.37,'541':-1464.61,'532':-2013.31}
print('conta | mês: folha (D-C) | pago TXT (D) | saldo acumulado (C = a pagar)')
res={}
for c,nome in (('5','Caixa (adiantamento)'),('187','Salários a pagar'),('188','Pró-labore a pagar'),('192','FGTS a recolher'),('191','INSS a recolher'),('541','Consignado (Créd. Trabalhador)'),('532','IRRF folha')):
    s=saldo_ini[c]; print(f'== {c} {nome} (saldo 31/12/2025: {s:.2f})')
    for m in [f'{i:02d}' for i in range(1,10)]:
        s+=fol[c][m]+pag[c][m]; print(f'   {m}: {fol[c][m]:10.2f} | {pag[c][m]:10.2f} | {s:10.2f}')
    res[c]=s
json.dump({'res':res},open(S+'/fiscal/aud_folha_res.json','w'))
