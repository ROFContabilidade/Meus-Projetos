import csv,json,re,datetime,collections,sys,unicodedata
sys.path.insert(0,'tools')
def U(s): return unicodedata.normalize('NFKD',(s or '').upper()).encode('ascii','ignore').decode()
def d(s,fmt): return datetime.datetime.strptime(s,fmt).date()
# NFs do Domínio
nfs=[]
for r in csv.reader(open('base/entradas_2026.csv',encoding='utf-8',errors='ignore')):
    if r and re.match(r'^\d+$',r[0]) and len(r)>20 and re.match(r'\d\d/\d\d/\d{4}',r[1]):
        nfs.append(dict(cod=r[0],em=d(r[1],'%m/%d/%Y'),nota=r[5],esp=r[8],forn=U(r[10]),cnpj=re.sub(r'\D','',r[12]),cfop=r[16],ac=r[17],uf=r[18],v=float(r[19])))
# Michael Fashion (XML, não escriturada)
nfs.append(dict(cod='XML',em=datetime.date(2026,10,8),nota='336',esp='36',forn='MICHAEL FASHION CONFECCOES LTDA',cnpj='54111912000160',cfop='2102',ac='-',uf='SP',v=1500.0))
# pagamentos
pg=[]
for r in json.load(open('dl/razao.json')):
    if r['conta'] in('8','9') and r['c']>0:
        pg.append(dict(src='razao',banco=r['conta'],data=d(r['data'],'%d/%m/%Y'),hist=U(r['hist']),doc='',v=round(r['c'],2),cp=r['cp']))
for x in json.load(open('mov.json')):
    if x['v']<0: pg.append(dict(src='ext',banco=x['banco'],data=d(x['data'],'%d/%m/%Y'),hist=U(x['hist']),doc=re.sub(r'\D','',x.get('doc','')),v=round(-x['v'],2),cp=''))
STOP=set('LTDA EIRELI ME EPP CONFECCOES CONFECCAO MODAS MODA COMERCIAL COMERCIO FASHION SERVICOS SERVICO SAUDE DE DA DO DOS DAS E S.A. SA INSTITUICAO PAGAMENTO FEMININA VESTUARIO CIA PARANA CLINICAS'.split())
def toks(n): return [t for t in re.findall(r'[A-Z]{4,}',n) if t not in STOP]
for p in pg:
    p['cnpjs']=set(re.findall(r'\d{14}',re.sub(r'[\./-]','',p['hist']+' '+p['doc'])))
def cand(nf):
    tk=toks(nf['forn']); out=[]
    for p in pg:
        if p.get('used'): continue
        dd=(p['data']-nf['em']).days
        if dd<-45 or dd>120: continue
        if nf['cnpj'][:8] in ''.join(p['cnpjs']) or (tk and sum(t in p['hist'] for t in tk)>=min(2,len(tk))):
            out.append(p)
    return out
res=[]
for nf in sorted(nfs,key=lambda n:n['em']):
    cs=sorted(cand(nf),key=lambda p:p['data'])
    hit=None
    for p in cs:
        if abs(p['v']-nf['v'])<0.02: hit=[p];break
    if not hit:
        # soma de 2-3 pagamentos
        import itertools
        for k in (2,3):
            for comb in itertools.combinations(cs[:10],k):
                if abs(sum(p['v'] for p in comb)-nf['v'])<0.02: hit=list(comb);break
            if hit:break
    if not hit:
        vs=[p for p in pg if not p.get('used') and abs(p['v']-nf['v'])<0.02 and -5<=(p['data']-nf['em']).days<=75 and not re.search(r'SUL AMERICA|SENFF|COPEL|TELEFONICA|IMOBILIARIA|EXCELLENT|SIMPLES|DARF',p['hist'])]
        if len(vs)>=1: hit=[vs[0]]; hit[0]['porvalor']=1
    if hit:
        for p in hit:p['used']=1
    res.append((nf,hit,cs))
json.dump([dict(nf={k:str(v) for k,v in nf.items()},pag=[{k:str(v) for k,v in p.items() if k!='cnpjs'} for p in (h or [])],cand=[{k:str(v) for k,v in p.items() if k!='cnpjs'} for p in c]) for nf,h,c in res],open('nf_pag.json','w'),ensure_ascii=False,indent=0)
for nf,h,c in res:
    st=('PAGO-v' if h and h[0].get('porvalor') else 'PAGO') if h else ('PARCIAL?' if c else 'SEM PAGTO')
    pinfo='; '.join(f"{p['data']:%d/%m} b{p['banco']} {p['v']:.2f} cp={p['cp'] or 'a lançar'}" for p in (h or c[:3]))
    print(f"{nf['em']:%d/%m} {nf['esp']} {nf['nota']:>7} {nf['forn'][:30]:30} {nf['v']:9.2f} AC{nf['ac']} | {st:9} | {pinfo[:120]}")
