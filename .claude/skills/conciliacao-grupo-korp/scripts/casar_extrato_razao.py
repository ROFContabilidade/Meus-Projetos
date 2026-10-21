import pickle,collections,itertools
ext,raz,tot=pickle.load(open('data.pkl','rb'))
pool=collections.defaultdict(list)
for r in raz: pool[(r['d'],r['sv'])].append(r)
um=[]
for e in ext:
    k=(e['d'],e['sv'])
    if pool[k]: r=pool[k].pop(0); r['ext']=e; e['lin']=[r]
    else: um.append(e)
resto=[r for v in pool.values() for r in v]
print('unmatched ext',len(um),'resto raz',len(resto))
rat=[];byd=collections.defaultdict(list)
for e in um: byd[e['d']].append(e)
falt=[]
for d,es in byd.items():
    cand=[r for r in resto if r['d']==d]
    if len(es)==1 and cand and round(sum(x['sv'] for x in cand),2)==es[0]['sv']:
        es[0]['lin']=cand
        for r in cand: r['ext']=es[0]; resto.remove(r)
        continue
    for e in es:
        cand=[r for r in resto if r['d']==d]; ach=None
        if len(cand)<=16:
            for n in range(1,len(cand)+1):
                for c in itertools.combinations(cand,n):
                    if round(sum(x['sv'] for x in c),2)==e['sv']: ach=c;break
                if ach:break
        if ach:
            e['lin']=list(ach)
            for r in ach: r['ext']=e; resto.remove(r)
        else: falt.append(e)
print('falt',len(falt),'resto',len(resto))
print('--EXTRATO sem razão')
for e in falt: print(e['d'],e['sv'],e['desc'],e['inf'])
print('--RAZÃO sem extrato')
for r in resto: print(r['d'],r['n'],r['sv'],r['obs'][:70],r['cc'])
pickle.dump((ext,raz,falt,resto),open('res.pkl','wb'))
