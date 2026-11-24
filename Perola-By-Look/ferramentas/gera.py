import json,collections,re,unicodedata,datetime as dt
o=json.load(open('out/motor.json'))
def br(v): return f"{v:.2f}".replace('.',',')
def H(s):
    s=unicodedata.normalize('NFKD',s.upper()).encode('ascii','ignore').decode()
    s=re.sub(r'[|]',' ',re.sub(r'\s+',' ',s)).strip()
    s=re.sub(r'\b(REF\.? ?A\.? )','',s)
    s=re.sub(r'(\b[A-Z][A-Z /\.-]{5,40}?) - \1',r'\1',s)
    return s[:150]
def dd(iso): y,m,d=iso.split('-'); return f"{d}/{m}/{y}"
BANCO={'8':'PAGBANK','9':'ITAU'}
APLIC=json.load(open('aplic_itau.json'))['conta'] if __import__('os').path.exists('aplic_itau.json') else 'APLIC_ITAU'
fix=lambda c: APLIC if c=='APLIC_ITAU' else c
evs=[]
for l in o['L']:
    b=l['banco']; d=dd(l['d']); ps=l['partes']
    if len(ps)==1:
        c,v,h=ps[0]; c=fix(c)
        deb,cred=(b,c) if l['entrada'] else (c,b)
        evs.append((l['d'],['|6000|X||||',f"|6100|{d}|{deb}|{cred}|{br(v)}||{H(h+' - '+BANCO[b])}||||"],b,l))
    else:
        if l['entrada']:
            lines=['|6000|D||||',f"|6100|{d}|{b}||{br(l['total'])}||{H(ps[0][2]+' - '+BANCO[b])}||||"]+[f"|6100|{d}||{fix(c)}|{br(v)}||{H(h)}||||" for c,v,h in ps]
        else:
            lines=['|6000|C||||',f"|6100|{d}||{b}|{br(l['total'])}||{H(l['orig']+' - '+BANCO[b])}||||"]+[f"|6100|{d}|{fix(c)}||{br(v)}||{H(h)}||||" for c,v,h in ps]
        evs.append((l['d'],lines,b,l))
for e in o['EX']:
    evs.append((e['d'],['|6000|X||||',f"|6100|{dd(e['d'])}|{e['deb']}|{e['cred']}|{br(e['v'])}||{H(e['h'])}||||"],'-',None))
evs.sort(key=lambda z:(z[0],z[2]))
por=collections.defaultdict(list)
for e in evs: por[e[0][:7]].append(e)
MES=['JANEIRO','FEVEREIRO','MARCO','ABRIL','MAIO','JUNHO','JULHO','AGOSTO','SETEMBRO','OUTUBRO']
arqs=[]
for ym,es in sorted(por.items()):
    m=int(ym[5:]); nome=f"out/PEROLA_49_{m:02d}_{MES[m-1]}_2026.txt"
    with open(nome,'w',encoding='latin-1',newline='\r\n') as f:
        f.write('|0000|30582416000126|\n')
        for e in es:
            for ln in e[1]: f.write(ln+'\n')
    arqs.append(nome)
print('\n'.join(arqs))
