import json,csv,sys,re
from collections import defaultdict
S=sys.argv[1]; fis=json.load(open(S+'/fiscal/fiscal.json'))
out=[]
for emp,rz in (('34','razao34_long.csv'),('118','razao118_long.csv')):
    R=list(csv.DictReader(open(S+'/dados/'+rz),delimiter=';'))
    B={'8','9'} if emp=='34' else {'8'}
    lb={r['lote'] for r in R if r['conta'] in B}
    print(f'\n===== {emp}: mês | NF-e recebidas (SEFAZ) | escrituradas Domínio | razão 506 créditos (notas) | 55 estoque D | diferença Domínio x 506')
    for m in range(1,10):
        mm=f'{m:02d}'; d=fis.get(f'{emp}-{mm}',{})
        nfe=[x for x in d.get('ent_nfe',[]) if 'cancel' not in x['status'].lower()]
        dom=d.get('ent_dom',[])
        domn=defaultdict(float)
        for x in dom: domn[x['nota']]+=x['valor']
        nfen=defaultdict(float)
        for x in nfe: nfen[x['nota']]+=x['valor']
        c506=sum(float(r['credito'])-float(r['debito']) for r in R if r['conta']=='506' and r['data'][3:5]==mm and r['lote'] not in lb and r['cp'] not in B)
        e55=sum(float(r['debito'])-float(r['credito']) for r in R if r['conta']=='55' and r['data'][3:5]==mm)
        tdom=sum(domn.values())
        print(f'  {mm} | {sum(nfen.values()):10.2f} ({len(nfen)}) | {tdom:10.2f} ({len(domn)}) | {c506:10.2f} | {e55:10.2f} | {tdom-c506:10.2f}')
        for k,v in nfen.items():
            if k not in domn:
                x=next(y for y in nfe if y['nota']==k); out.append((emp,mm,'NF-e recebida NÃO escriturada',x['data'],k,x['nome'][:40],round(v,2),x['status']))
            elif abs(domn[k]-v)>0.05: out.append((emp,mm,'Valor diferente (SEFAZ x Domínio)','',k,next(y['nome'] for y in nfe if y['nota']==k)[:40],round(v,2),f'Domínio {domn[k]:.2f}'))
        if nfen:
            for k,v in domn.items():
                if k not in nfen:
                    x=next(y for y in dom if y['nota']==k); out.append((emp,mm,'Escriturada sem estar na consulta SEFAZ do mês',x['data'],k,x['nome'][:40],round(v,2),'CFOP '+x['cfop']))
print()
for o in out: print(o)
json.dump(out,open(S+'/fiscal/aud_entradas.json','w'),ensure_ascii=False)
