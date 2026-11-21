import json,csv,re,sys
from collections import defaultdict
S=sys.argv[1]
fis=json.load(open(S+'/fiscal/fiscal.json'))
VENDA={'5102','6102','5405','6108','5101'}
out=[]
for emp,rz in (('34','razao34_long.csv'),('118','razao118_long.csv')):
    R=list(csv.DictReader(open(S+'/dados/'+rz),delimiter=';'))
    print(f'\n===== {emp}: mês | sistema autorizadas (venda) | Domínio saídas venda | Faturamento rel. | razão 408 líquido | 504 outros (não banco, não 408)')
    for m in range(1,10):
        mm=f'{m:02d}'; d=fis.get(f'{emp}-{mm}',{})
        sis=[x for x in d.get('sai_sis',[]) if x['cfop'] in VENDA]
        aut=[x for x in sis if x['autorizada']]
        dom=[x for x in d.get('sai_dom',[]) if x['cfop'] in VENDA]
        fat=d.get('fat') or {}
        ft=next((v[-1] for k,v in fat.items() if k in('Faturamento','Faturamento_Matriz','Faturamento_Filial') and (emp=='34' or k!='Faturamento_Matriz')),None)
        if emp=='34' and 'Faturamento_Matriz' in fat: ft=fat['Faturamento_Matriz'][-1]
        r408=[r for r in R if r['conta']=='408' and r['data'][3:5]==mm]
        v408=sum(float(r['credito'])-float(r['debito']) for r in r408)
        lb={r['lote'] for r in R if r['conta'] in('8','9')}
        o504=[r for r in R if r['conta']=='504' and r['data'][3:5]==mm and r['cp'] not in('408','8','9') and r['lote'] not in lb]
        print(f'  {mm} | {sum(x["valor"] for x in aut):10.2f} ({len(aut)}) | {sum(x["valor"] for x in dom):10.2f} ({len(dom)}) | {ft if ft is not None else "-":>10} | {v408:10.2f} ({len(r408)}) | {sum(float(r["debito"])-float(r["credito"]) for r in o504):10.2f} {[ (r["cp"],r["historico"][:40]) for r in o504][:3]}')
        nd={x['nota'] for x in dom}; ns={x['nota'] for x in aut}
        n408={re.search(r'DATA (\d+)',r['historico']).group(1) for r in r408 if re.search(r'DATA (\d+)',r['historico'])}
        for x in aut:
            if x['nota'] not in nd: out.append((emp,mm,'NF-e de venda AUTORIZADA não escriturada no Domínio',x['data'],x['nota'],x['nome'],x['valor'],x['status']))
            elif x['nota'] not in n408: out.append((emp,mm,'Escriturada no fiscal mas sem lançamento na 408 (contábil)',x['data'],x['nota'],x['nome'],x['valor'],''))
        for x in dom:
            if x['nota'] not in ns: 
                s=[y for y in sis if y['nota']==x['nota']]
                out.append((emp,mm,'Escriturada no Domínio mas não autorizada no emissor',x['data'],x['nota'],x['nome'],x['valor'],s[0]['status'] if s else 'não consta no emissor'))
        for x in [x for x in sis if not x['autorizada']]:
            if x['nota'] not in nd: out.append((emp,mm,'Nota do emissor NÃO autorizada (rejeitada/cancelada) - conferir se foi reemitida',x['data'],x['nota'],x['nome'],x['valor'],x['status']))
print()
for o in out: print(o)
json.dump(out,open(S+'/fiscal/aud_saidas.json','w'),ensure_ascii=False)
