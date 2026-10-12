import json,re,sys,collections,unicodedata
sys.path.insert(0,'../tools'); import classif
from classif import norm
ents=json.load(open('razao_ents.json'))
namecp=collections.defaultdict(collections.Counter)
for e in ents: namecp[norm(e['hist'])][e['cp']]+=1
def by_name(n):
    n=norm(n); c=collections.Counter()
    for h,cnt in namecp.items():
        if h.startswith(n[:20]) or (' - '+n[:20]) in h: c.update(cnt)
    return c
# ERP july
erp=[]
t=open('Relatorio de conferencia 07.26.txt').read()
for m in re.finditer(r'(\d{2}/\d{2}/26)\s+(\d{2}/\d{2}/26)\s+(.+?)\s{2,}(\d+)\s+(\d+)\s+(\d+)\s+([\d.,]+)\s+([\d.,]+)\s+(-?[\d.,]+)\s*\n(.*)',t):
    v=lambda s: float(s.replace('.','').replace(',','.'))
    erp.append(dict(data=m.group(2)[:6]+'2026',nome=m.group(3).strip(),cat=int(m.group(5)),ent=v(m.group(7)),sai=v(m.group(8)),obs=m.group(10).strip(),used=False))
CAT={6:'506',9:'506',4:'506',78:'506',133:'506',103:'493',97:'312',11:'320',56:'626',122:'375',87:'357',86:'642',45:'362',47:'640',14:'555',12:'355',124:'350',156:'350',172:'362',170:'362',181:'362',81:'362',53:'362',33:'362',84:'362',94:'362',182:'362',42:'365'}
RULES=[ (r'^APL APLIC AUT','11','APLICACAO AUTOMATICA ITAU (APLIC AUT MAIS)'),
        (r'^RES APLIC AUT','11','RESGATE APLICACAO AUTOMATICA ITAU (APLIC AUT MAIS)'),
        (r'^REND(IMENTO)? (PAGO|BRUTO)','432','RENDIMENTO APLICACAO AUTOMATICA ITAU'),
        (r'^TAR','626',None),(r'^IOF','625',None),(r'^JUROS','375',None),
        (r'^PGTO MIN-ITAUCARD','357',None),
        (r'^(MOV TIT COB|REDE |PIX QRS|PIX TRANSF|TED 448|TED 363|SISPAG O\.S\.)','504',None),
      ]
SPECIAL={ # nome fragment (bank) -> (cp, nota)
 'FIQUE BEM CO':('506','FIQUE BEM = mesmo CNPJ da GULA COSMETICOS (30.415.972/0001-08); seguido padrao GULA (506)'),
 'PROJETANDO A':('506','4 PIX de 22.600,00 e 3 estornos (EST PROJETAND) - resta 1 pagamento liquido de 22.600,00; fornecedor nao identificado'),
 'EST PROJETAND':('506','estorno de PIX enviado a PROJETANDO'),
 'DEV PIX NUTRI.COM':('506','devolucao do PIX enviado a NUTRI.COM no mesmo dia'),
 'NUTRI.COM TE':('506','PIX devolvido no mesmo dia (DEV PIX)'),
 'AKG ADM DE I':('320','AKG ADMINISTRACAO E IMOVEIS - locacao Barracao 42'),
 'MELO CRUZ':('320','MELO & CRUZ - aluguel (razao jan-jun usou 506/362)'),
 'CONDOMINIO E':('364','condominio - sem historico; confirmar conta'),
 'BANCO SOFISA':('506','boleto Banco Sofisa sem identificacao do cedente'),
 'COSMETICON C':('664',None),
 'MARCELO HENR':('362','MARCELO HENRIQUE MAZZONI - TXT jun/26 usou 362'),
 'BOLETO PAGO ITAU UNIBANC':('357','ERP: utilizacao de cartao de credito (razao jan-jun usou 364 uma vez)'),
}
def classify(x,mes):
    d=norm(x['desc']); v=x['valor']; nota=''; hist=None; cp=None; how=''
    # ERP match (debitos/creditos por data+valor)
    e=None
    cands=[c for c in erp if not c['used'] and c['data']==x['data'] and abs((c['sai'] if v<0 else c['ent'])-abs(v))<0.005]
    fr=classif.frag(x['desc'])[1]
    for c in cands:
        if norm(c['nome']).startswith(fr[:10]): e=c; break
    if not e and len(cands)==1:
        others=[y for y in MOV if y is not x and y['data']==x['data'] and abs(y['valor']-v)<0.005]
        if not others: e=cands[0]
    if e: e['used']=True
    for pat,acc,h in RULES:
        if re.match(pat,d): cp=acc; hist=h or x['desc']; how='regra'; break
    if not cp:
        for k,(acc,n) in SPECIAL.items():
            if k in d: cp=acc; nota=n or ''; how='especial'; hist=x['desc']; break
    if not cp:
        c2,h2,how2=classif.classify(x['desc'],v)
        if how2=='razao-exato': cp,hist,how=c2,x['desc'],how2
    if not cp and e:
        c=by_name(e['nome'])
        if c: cp=c.most_common(1)[0][0]; how='erp-nome->razao'
        elif e['cat'] in CAT: cp=CAT[e['cat']]; how='erp-categoria'
    if not cp:
        c2,h2,how2=classif.classify(x['desc'],v)
        if c2: cp,hist,how=c2,h2,how2
    if not cp:
        if v>0: cp='504'; how='padrao-credito'; nota='credito sem referencia - tratado como recebimento de cliente (504)'
        else: cp='506'; how='padrao-debito'; nota='pagamento sem referencia - tratado como fornecedor (506)'
    if cp in ('187','25','511','512','659','492'):
        nota=(nota+'; ' if nota else '')+f'razao jan-jun usava conta {cp} (folha); empresa sem folha desde 03/26 -> 362 servicos de terceiros'; cp='362'
    if e: hist=e['nome']
    if not hist or hist==x['desc']: hist=x['desc']
    hist=re.sub(r'\s+',' ',hist).strip()
    return cp,hist.upper(),how,nota,(e['nome']+' / '+e['obs'][:60]) if e else ''
def run(mes,arq):
    global MOV
    mov=json.load(open(f'ext_{mes}.json'))['mov']; MOV=mov; res=[]
    for x in mov:
        cp,h,how,nota,erpinfo=classify(x,mes); res.append(dict(x,cp=cp,hist=h,how=how,nota=nota,erp=erpinfo))
    json.dump(res,open(arq,'w'),ensure_ascii=False,indent=0); return res
if __name__=='__main__':
    for mes in sys.argv[1:]:
        r=run(mes,f'class_{mes}.json')
        print(mes,collections.Counter(z['how'] for z in r))
