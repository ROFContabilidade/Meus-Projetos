import json,collections,datetime as dt,re,sys,unicodedata,itertools
sys.path.insert(0,'../tools'); from regras_cosmos import sugerir
def N(s): return unicodedata.normalize('NFKD',s or '').encode('ascii','ignore').decode().upper()
STOP={'LTDA','DE','DA','DO','DOS','E','S','A','SA','COMERCIO','INDUSTRIA','REF','PGTO','PIX','ENVIADO','BOLETO','PAGO','EIRELI','ME','CIA'}
def toks(s): return {t for t in re.findall(r'[A-Z]{3,}',N(s)) if t not in STOP}
def sim(nome,hist):
    a=toks(nome); b=toks(hist)
    if not a or not b: return 0
    # prefix match (bank truncates names)
    sc=0
    for t in a:
        for u in b:
            if t==u or (len(u)>=4 and t.startswith(u)) or (len(t)>=4 and u.startswith(t)): sc+=1; break
    return sc
ents=json.load(open('razao_ents.json'))
for i,e in enumerate(ents): e['i']=i; e['v']=round(e['d']-e['c'],2)
jul=json.load(open('class_Julho.json'))
for z in jul: ents.append(dict(data=z['data'],hist=z['hist']+' '+z['desc'],cp=z['cp'],d=max(z['valor'],0),c=max(-z['valor'],0),v=round(z['valor'],2),i=len(ents),src='jul'))
D=lambda s: dt.datetime.strptime(s,'%d/%m/%Y')
cos=[]
for m in ['01','02','03','04','05','06','07']:
    for c in json.load(open(f'hist/cos{m}.json')): c['mes']=m; c['val']=round(c['ent']-c['sai'],2); cos.append(c)
used=set()
# pass 1: value + date<=7 + best name score, require score>0 or unique
for c in cos:
    cand=[e for e in ents if e['i'] not in used and abs(e['v']-c['val'])<0.005 and abs((D(e['data'])-D(c['data'])).days)<=7]
    if not cand: continue
    sc=sorted(cand,key=lambda e:(-sim(c['nome'],e['hist']),abs((D(e['data'])-D(c['data'])).days)))
    best=sc[0]; s=sim(c['nome'],best['hist'])
    if s>0 or (len(cand)==1 and best['data']==c['data']):
        c['m']=[best['i']]; c['score']=s; used.add(best['i'])
# pass 2: groups of same name & date summing to one razao line
rest=[c for c in cos if 'm' not in c and c['val']<0]
grp=collections.defaultdict(list)
for c in rest: grp[(c['data'],N(c['nome'])[:15])].append(c)
for k,l in grp.items():
    tot=round(sum(c['val'] for c in l),2)
    for n in range(len(l),1,-1):
        done=False
        for comb in itertools.combinations(l,n):
            t=round(sum(c['val'] for c in comb),2)
            cand=[e for e in ents if e['i'] not in used and abs(e['v']-t)<0.005 and abs((D(e['data'])-D(k[0])).days)<=7 and sim(comb[0]['nome'],e['hist'])>0]
            if cand:
                e=cand[0]; used.add(e['i'])
                for c in comb: c['m']=[e['i']]; c['grupo']=f'{n} itens = {-t:.2f}'
                done=True; break
        if done: break
E_by={e['i']:e for e in ents}
out=[]
for c in cos:
    e=E_by[c['m'][0]] if 'm' in c else None
    r=dict(c,cp=e['cp'] if e else None,rz_data=e['data'] if e else None,rz_hist=e['hist'] if e else None,rz_i=e['i'] if e else None,rz_v=e['v'] if e else None)
    obs=N(c['obs'])
    pf=c['pf']
    if pf in (97,4) and 'COMPRA DE' in obs and 'FRETE' not in obs: pf=6
    if pf==34 and 'SERVIC' in obs: pf=81
    if not e: r['sug'],r['nivel'],r['motivo']=None,'SEM PAR','nao encontrado no razao/extrato'
    else: r['sug'],r['nivel'],r['motivo']=sugerir(c['op'],pf,e['cp'],c['obs'],c['nome'])
    out.append(r)
json.dump(out,open('cruz.json','w'),ensure_ascii=False)
st=collections.Counter((r['nivel']) for r in out); print(st)
print('sem par saidas',sum(1 for r in out if r['nivel']=='SEM PAR' and r['val']<0), round(sum(-r['val'] for r in out if r['nivel']=='SEM PAR' and r['val']<0),2))
