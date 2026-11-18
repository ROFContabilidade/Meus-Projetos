"""Gera o TXT único do mês (leiaute Domínio |0000|/|6000|/|6100|) da Ótica VisouUP (118).
Uso: python gerar_txt.py classificado.csv regras.json saida.txt [--split ID=conta:valor,conta:valor]
Um movimento do banco = um lote. Split = lote C (saída) ou D (entrada) com várias partidas."""
import csv,json,sys,re
from decimal import Decimal as D
R=json.load(open(sys.argv[2],encoding='utf-8'));B=R['conta_banco']
split={}
for a in sys.argv[4:]:
    if a.startswith('--split='):
        k,v=a[8:].split('=');split[k]=[(p.split(':')[0],D(p.split(':')[1])) for p in v.split(',')]
f=lambda x:f"{x:.2f}".replace('.',',')
lim=lambda s:re.sub(r'\s+',' ',s.replace('|','/')).strip()[:200]
out=[f"|0000|{R['cnpj']}|"];soma={};ent=sai=D(0)
def add(c,v): soma[c]=soma.get(c,D(0))+v
for l in csv.DictReader(open(sys.argv[1],encoding='utf-8'),delimiter=';'):
    v=D(l['valor']);dt=l['data'];h=lim(R['prefixo']+l['descricao'])
    if not l['conta']: sys.exit(f"sem conta: {l}")
    if v>0: ent+=v
    else: sai+=-v
    if l['id'] in split:
        parts=split[l['id']];assert sum(p[1] for p in parts)==abs(v),(l['id'],v)
        if v<0:
            out+=['|6000|C||||',f"|6100|{dt}||{B}|{f(-v)}||{h}||||"]+[f"|6100|{dt}|{c}||{f(x)}||{h}||||" for c,x in parts]
            add(B,v);[add(c,x) for c,x in parts]
        else:
            out+=['|6000|D||||',f"|6100|{dt}|{B}||{f(v)}||{h}||||"]+[f"|6100|{dt}||{c}|{f(x)}||{h}||||" for c,x in parts]
            add(B,v);[add(c,-x) for c,x in parts]
        continue
    d,c=(l['conta'],B) if v<0 else (B,l['conta'])
    out+=['|6000|X||||',f"|6100|{dt}|{d}|{c}|{f(abs(v))}||{h}||||"];add(d,abs(v));add(c,-abs(v))
open(sys.argv[3],'w',encoding='cp1252',errors='replace',newline='').write('\r\n'.join(out)+'\r\n')
print(sys.argv[3],'lotes',out.count('|6000|X||||')+out.count('|6000|C||||')+out.count('|6000|D||||'),'entradas',f(ent),'saidas',f(sai),'liquido banco',f(soma[B]))
for k in sorted(soma,key=lambda x:int(x)):
    if k!=B: print('  ',k.rjust(4),f(soma[k]))
