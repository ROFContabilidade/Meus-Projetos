"""Classifica o extrato normalizado da Ótica VisouUP pelas regras de references/regras.json.
Uso: python classificar.py ext.csv regras.json saida.csv"""
import csv,json,sys,unicodedata
n=lambda s:unicodedata.normalize('NFKD',s).encode('ascii','ignore').decode().upper()
R=json.load(open(sys.argv[2],encoding='utf-8'))
out=[]
for l in csv.DictReader(open(sys.argv[1],encoding='utf-8-sig'),delimiter=';'):
    v=float(l['valor']);t='C' if v>0 else 'D';d=n(l['descricao'])
    hit=next((r for r in R['regras'] if r['t']==t and any(n(c) in d for c in r['c'])),None)
    l.update(conta=hit['conta'] if hit else '',status=hit['st'] if hit else 'SEM REGRA',obs=hit['obs'] if hit else '')
    out.append(l)
w=csv.DictWriter(open(sys.argv[3],'w',newline='',encoding='utf-8'),fieldnames=list(out[0].keys()),delimiter=';');w.writeheader();w.writerows(out)
import collections;c=collections.Counter(x['status'] for x in out);print(sys.argv[1],dict(c))
for x in out:
    if x['status']=='SEM REGRA': print('  SEM REGRA',x['data'],x['valor'],x['descricao'][:70])
