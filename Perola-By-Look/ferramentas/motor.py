"""Pérola By Look (49) - refaz lançamentos bancários 01-10/2026 com razão-auxiliar da 506 por NF."""
import json,re,csv,datetime as dt,collections,sys
D=lambda s:dt.datetime.strptime(s,'%d/%m/%Y').date()
def br(v): return f"{v:.2f}".replace('.',',')
# ---------- NFs (razão auxiliar 506) ----------
NF=[]
def addnf(em,nota,forn,cnpj,v,tipo,obs=''):
    NF.append(dict(em=em,nota=nota,forn=forn,root=cnpj[:8],v=round(v,2),aberto=round(v,2),tipo=tipo,obs=obs,pags=[]))
for r in csv.reader(open('base/entradas_2026.csv',encoding='utf-8',errors='ignore')):
    if r and re.match(r'^\d+$',r[0]) and len(r)>20 and re.match(r'\d\d/\d\d/\d{4}',r[1]):
        em=dt.datetime.strptime(r[1],'%m/%d/%Y').date()
        addnf(em,r[5],r[10].strip(),re.sub(r'\D','',r[12]),float(r[19]),'NFS-e' if r[8]=='39' else 'NF-e')
# outubro (relatório de entradas 10/2026, emitido 18/11)
addnf(dt.date(2026,10,8),'225','Modas Carol Ltda','50855064000142',1500,'NF-e')
addnf(dt.date(2026,10,19),'105484','SUL AMERICA PARANA CLINICAS','02866602000909',2.90,'NFS-e')
addnf(dt.date(2026,10,20),'110473','SUL AMERICA PARANA CLINICAS','02866602000909',1273.47,'NFS-e')
addnf(dt.date(2026,10,19),'6393','SINGULAR SOLUCOES EM TECNOLOGIA','27101405000172',185,'NFS-e')
addnf(dt.date(2026,10,8),'336','MICHAEL FASHION CONFECCOES (NAO ESCRITURADA)','54111912000160',1500,'NF-e','XML na pasta, falta escriturar')
# 4º tri 2025 (podem compor o saldo inicial da 506)
for em,n,f,c,v in [((2025,10,2),'18681','KESSEY COMERCIO E CONFEC','00962735000104',1910.37),((2025,10,8),'3088','FASHION LUZ 21 ATACADO','46289572000133',2500),
                   ((2025,11,11),'17558','VICTTORIA DESIGN','30910999000177',1040),((2025,11,29),'17860','VICTTORIA DESIGN','30910999000177',1500),
                   ((2025,11,29),'1482','TITO WILY QUISPE COLQUE','10273009000120',850),((2025,12,17),'18198','VICTTORIA DESIGN','30910999000177',400)]:
    addnf(dt.date(*em),n,f,c,v,'NF-e','2025')
# apelidos de pagamento -> raiz CNPJ do fornecedor da NF
ALIAS=[(r'SUL AMERICA','02866602'),(r'SENFF','03877288'),(r'PAES E BASTOS','29650531'),(r'OLINDA LOPES CALDEIRA','04883162'),
       (r'CHACHAQUE','37985418'),(r'GENILDA','14417585'),(r'AGUIA FASHION','35748808'),(r'LUDY','11934625'),(r'MERCEDES','24990793'),
       (r'MAURICIO','60785672'),(r'NORTE VEST','26000425'),(r'BIG GIRLS','30782979'),(r'PARESCHI','72457054'),(r'VEST BELLAS','28012259'),
       (r'DALANT','01768920'),(r'HANAN','45520949'),(r'JULIA COMERCIAL','04698649'),(r'LUANY','47066492'),(r'SINGULAR','27101405'),
       (r'DAVID ROJAS|MODAS CAROL','50855064'),(r'MICHAEL FASHION','54111912'),(r'VICTTORIA','30910999'),(r'KESSEY','00962735'),
       (r'FASHION LUZ','46289572'),(r'TITO WILY|QUISPE COLQUE','10273009'),(r'CALDEIRA','04883162')]
NFROOTS={n['root'] for n in NF}
def fornecedor(t,docs):
    for d in docs:
        if len(d)==14 and d[:8] in NFROOTS: return d[:8]
    for rx,root in ALIAS:
        if re.search(rx,t): return root
    return None
# ---------- regras sem NF ----------
MERC=r'MODA|FASHION|CONFEC|TEXTIL|TECIDO|ROUPA|VEST|JEANS|CALCADO|COSMETIC|PERFUM|BRILH|ATACADO|VARIEDADES|TRICOT|POLARES|MATEX|QUINZY|GIGA 10|DAMSEL|STUDIO Z|\bC E A\b|PERNAMBUCANAS|LOJAO 10|AFFORD|PALLADIUM|CHARMEH|VALORI|IDELI|QUILL|OUTLET|KT DAHER|REPUBLICA CALC|THAI PRATAS|VILA DAS COMPRAS|DILLYMODAS|CHIQUE MODAS|JHORMAY|ALEY|ODALIZ|CADENA|YANDY|LOUVER|MAJU|JAINA|ALINE GRACE|POP XV|PRATICA LOJA|BRILHANTINA|BIG GIRLS|A9 |ISABELLA CAVALCANTE|AKI TEM|TOP 5|APB\b|HUSKY|CS PRACA ZACARIAS'
FAMILIA=r'GUILHERME LUDOVICO|NADIA DE ARAUJO LUDOVICO|EMERSON LUIZ LUDOVICO'
def docs_of(x):
    ds=set(re.findall(r'\d{14}|\d{11}',re.sub(r'[\./-]','',x['t']+' '+x['doc'])))
    if x['doc']: ds.add(x['doc'])
    return ds
def tipo_pessoa(t,ds):
    if any(len(d)==14 for d in ds): return 'PJ'
    if any(len(d)==11 for d in ds): return 'PF'
    if re.search(r'LTDA|EIRELI|\bME\b|S\.?A\.?$|'+MERC,t): return 'PJ'
    return 'PF'
CNAE=json.load(open('cnae_map.json')) if __import__('os').path.exists('cnae_map.json') else {}
def regra_saida(t,ds,v):
    for d in ds:
        if len(d)==14 and d[:8] in CNAE: return tuple(CNAE[d[:8]])
    if re.search(r'IMOBILIARIA',t): return '320','ALUGUEL'
    if re.search(r'TELEFONICA',t): return '356','TELEFONE/INTERNET'
    if re.search(r'COPEL',t): return '354','ENERGIA ELETRICA'
    if re.search(r'EXCELLENT',t): return '558','SISTEMA'
    if re.search(r'SIMPLES NACIONAL',t): return '479','DAS'
    if re.search(r'\bDARF\b',t): return '191','INSS PRO-LABORE (DARF)'
    if re.search(r'SEFAZ',t): return '512','ICMS ANTECIPADO'
    if re.search(r'CONTABILIDADE|\bRBA\b',t): return '361','HONORARIOS CONTABEIS'
    if re.search(r'IFOOD|CONFEITARIA|PAMONHA',t): return '521','ALIMENTACAO'
    if re.search(r'RICK COSTA',t): return '312','FRETE/EXCURSAO DE COMPRAS'
    if re.search(r'EMBALAGEN',t): return '58','EMBALAGENS'
    if re.search(r'LIMPEZA|PFX UTILIDADES',t): return '360','MATERIAL DE LIMPEZA'
    if re.search(r'POTENCIA PUBLICIDADE',t): return '574','MARKETING'
    if re.search(r'THK|JM SERVICOS',t): return '359','SERVICOS ADMINISTRATIVOS'
    if re.search(r'PAGAMENTO E SERVICOS DE|PAGAMENTOS E SERVICOS DE|MOOZ|MAREE|STAFEBANK|SHPP|CAKTO',t): return '493','PAGAMENTO VIA INTERMEDIADOR (SEM DOCUMENTO)'
    for d in ds:
        if len(d)==14 and d[:8] in CNAE: return CNAE[d[:8]]
    if re.search(FAMILIA,t): return '551','PIX PESSOA LIGADA A SOCIA'
    if re.search(MERC,t): return '470','COMPRA DE MERCADORIA SEM NF'
    tp=tipo_pessoa(t,ds)
    if tp=='PF': return '362','PAGAMENTO PESSOA FISICA SEM NF'
    return '470','COMPRA DE MERCADORIA SEM NF'
# ---------- movimentos ----------
mv=json.load(open('mov_all.json'))
for x in mv: x['d']=D(x['data'])
mv.sort(key=lambda x:(x['d'],x['banco'],x['v']))
# pares de transferencia entre contas proprias (8<->9) mesmo dia/+1
OWN=r'PEROLA BY LOOK|PEROLA C L KUSIAK LTDA|PEROLA CL KUSIAK|30582416000126'
for x in mv:
    if x.get('par') or not re.search(OWN,x['t']+x['doc']): continue
    for y in mv:
        if y is x or y.get('par') or y['banco']==x['banco']: continue
        if abs(y['v']+x['v'])<.01 and abs((y['d']-x['d']).days)<=1 and re.search(OWN,y['t']+y['doc']):
            x['par']=y['banco']; y['par']=x['banco']; break
grp=collections.defaultdict(list)
for x in mv:
    if x['v']<0:
        r=fornecedor(x['t'],docs_of(x))
        if r: grp[(x['d'],r)].append(x)
for (d,r),xs in grp.items():
    if len(xs)>1:
        tot=round(sum(-x['v'] for x in xs),2)
        for n in NF:
            if n['root']==r and abs(n['v']-tot)<0.01 and -40<=(d-n['em']).days<=60:
                for x in xs: x['alvo_nf']=n['nota']
                break
# saldo 188 (pro-labore liquido a pagar)
s188=15707.00
folha=collections.defaultdict(float)
for m,d in [(1,30),(2,27),(3,31),(4,30),(5,30),(6,30),(7,31),(8,31),(9,30),(10,31)]: folha[dt.date(2026,m,d)]+=1442.69
L=[]  # lancamentos: dict(d, lote:'X'|'C'|'D', banco, total, partidas=[(conta,valor,hist)])
pend=[]
def lanc(x,partes,h):
    tot=round(abs(x['v']),2)
    L.append(dict(d=x['d'],banco=x['banco'],entrada=x['v']>0,total=tot,partes=partes,hist=h,orig=x['t'][:60]))
fdates=sorted(folha)
def acum_folha(ate):
    global s188
    while fdates and fdates[0]<=ate: s188+=folha[fdates.pop(0)]
for x in mv:
    acum_folha(x['d'])
    t=x['t']; v=x['v']; a=abs(v); ds=docs_of(x); nm=re.sub(r'\s+',' ',t)[:55]
    if x.get('par'):
        if v<0: lanc(x,[(x['par'],a,f"TRANSF. ENTRE CONTAS PROPRIAS {'PAGBANK->ITAU' if x['banco']=='8' else 'ITAU->PAGBANK'}")],'')
        continue  # entrada do par: nao lanca (o lancamento da saida ja movimenta as duas contas)
    if v>0:
        if re.search(r'RENDIMENTO',t) and 'APLIC AUT' in t: c,h='432','RENDIMENTO APLICACAO AUTOMATICA ITAU'
        elif re.search(r'RENDIMENTO',t): c,h='432','RENDIMENTO DA CONTA'
        elif re.search(r'RESGATE DE CDB',t): c,h='48','RESGATE CDB PAGBANK'
        elif re.search(r'RES APLIC AUT',t): c,h='APLIC_ITAU','RESGATE APLICACAO AUTOMATICA ITAU'
        elif re.search(r'ESTORNO',t) and 'SIMPLES' in t: c,h='479','ESTORNO PAGAMENTO DAS'
        elif re.search(r'PEROLA CRISTINA',t) or re.search(OWN,t): c,h='551','PIX RECEBIDO DA SOCIA'
        elif re.search(FAMILIA,t): c,h='551','PIX RECEBIDO PESSOA LIGADA A SOCIA'
        elif re.search(r'REDE|REDECARD|01425787|VENDAS - DISPONIVEL|SENFF|PAGAMENTO S\.A',t+''.join(ds)): c,h='504','RECEBIMENTO DE CARTOES'
        else: c,h='504','PIX RECEBIDO DE CLIENTE'
        lanc(x,[(c,a,f"{h} - {nm}")],''); continue
    # ---- saidas ----
    if re.search(r'APLICACAO EM CDB',t): lanc(x,[('48',a,'APLICACAO CDB PAGBANK')],''); continue
    if re.search(r'APL APLIC AUT',t): lanc(x,[('APLIC_ITAU',a,'APLICACAO AUTOMATICA ITAU')],''); continue
    if re.search(r'PEROLA CRISTINA',t) or re.search(OWN,t):
        p=round(min(a,max(s188,0)),2); r=round(a-p,2); partes=[]
        if p>0: partes.append(('188',p,f'PAGAMENTO PRO-LABORE - {nm}'))
        if r>0: partes.append(('551',r,f'RETIRADA DA SOCIA - {nm}'))
        s188-=p; lanc(x,partes,''); continue
    root=fornecedor(t,ds)
    if root:
        resto=a; partes=[]
        pre={'02866602':0,'29650531':30}.get(root,20)
        abertas=[n for n in NF if n['root']==root and n['aberto']>0.005 and n['em']<=x['d']+dt.timedelta(days=pre)]
        abertas.sort(key=lambda n:n['em'])
        alvo=x.get('alvo_nf')
        exato=[n for n in abertas if (alvo and n['nota']==alvo) or abs(n['aberto']-a)<0.01]
        if exato: abertas=[exato[0]]+[n for n in abertas if n is not exato[0]]
        for n in abertas:
            if resto<=0.005: break
            q=round(min(resto,n['aberto']),2); n['aberto']=round(n['aberto']-q,2); resto=round(resto-q,2)
            n['pags'].append((x['data'],x['banco'],q)); partes.append(('510' if root=='29650531' else '506',q,f"PAGTO NF {n['nota']} {n['forn'][:30]}"))
        if resto>0.005:
            if root=='02866602':
                ref='12/2025 (SALDO INICIAL 506)' if x['d'].month==1 else '07/2026 - NFS-E A ESCRITURAR'
                partes.append(('506',resto,f'PAGTO NFS-E {ref} SUL AMERICA'))
            elif root=='29650531':
                partes.append(('361',resto,'HONORARIOS CONTABEIS PAES E BASTOS'))
            else:
                partes.append(('470',resto,f'PAGTO ACIMA DA NF - MERCADORIA SEM NF {nm[:30]}'))
        lanc(x,partes,''); continue
    c,h=regra_saida(t,ds,a)
    if c=='479' and abs(a-230.56)<.01:
        lanc(x,[('479',185.12,'DAS 08/2025 PRINCIPAL'),('352',37.02,'MULTA DAS 08/2025'),('372',8.42,'JUROS DAS 08/2025')],''); continue
    lanc(x,[(c,a,f'{h} - {nm}')],'')
# ---------- lancamentos sem banco ----------
EX=[]
for d,v,h in [((2026,2,28),2023.81,'RENDIMENTO CDB PAGBANK ATE 28/02 (VALOR LIQUIDO INFORMADO PELA CLIENTE)'),((2026,3,31),271.78,'RENDIMENTO CDB PAGBANK 03/2026'),
              ((2026,6,5),522.39,'RENDIMENTO CDB 1 PAGBANK ATE O RESGATE DE 05/06'),((2026,6,30),211.34,'RENDIMENTO CDB 2 PAGBANK 04 A 06/2026'),
              ((2026,9,30),179.29,'RENDIMENTO CDB PAGBANK 07 A 09/2026'),((2026,10,31),69.72,'RENDIMENTO CDB PAGBANK 10/2026')]:
    EX.append(dict(d=dt.date(*d),deb='48',cred='432',v=v,h=h))
for n in NF:   # Senff: comissao descontada do repasse de cartao
    if n['root']=='03877288':
        EX.append(dict(d=n['em'],deb='506',cred='504',v=n['v'],h=f"BAIXA NFS-E {n['nota']} SENFF - COMISSAO DESCONTADA DO REPASSE")); n['pags'].append((n['em'].strftime('%d/%m/%Y'),'504',n['v'])); n['aberto']=0
json.dump(dict(L=[{**l,'d':l['d'].isoformat()} for l in L],EX=[{**e,'d':e['d'].isoformat()} for e in EX],NF=[{**n,'em':n['em'].isoformat()} for n in NF],s188=s188),open('out/motor.json','w'),ensure_ascii=False,indent=0,default=str)
print('lancamentos',len(L),'extras',len(EX),'s188 final',round(s188,2))
