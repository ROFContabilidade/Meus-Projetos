import json,re,collections,unicodedata
def norm(s):
    s=unicodedata.normalize('NFKD',s).encode('ascii','ignore').decode().upper()
    s=re.sub(r'^REF\.? ?A ','',s.strip()); s=re.sub(r'\s+',' ',s); return s
def key(desc):
    d=norm(desc)
    d=re.sub(r'\d{2}/\d{2}S?$','',d).strip()          # MOV TIT COB DISP 01/07S
    d=re.sub(r'(PIX (QRS|TRANSF) .{0,9}?)\d{2}/\d{2}$',r'\1',d).strip()
    return d
def frag(desc):
    d=norm(desc)
    m=re.match(r'(PIX ENVIADO|BOLETO PAGO|SISPAG|PIX TRANSF|PIX QRS) (.*)$',d)
    return (m.group(1),m.group(2).strip()) if m else (None,d)
ents=json.load(open('razao_ents.json'))
june=json.load(open('ext_Junho.json'))['mov']
# 1) june bank->razao by date+value
bykey=collections.defaultdict(collections.Counter); hist_of={}
pool=collections.defaultdict(list)
for e in ents:
    if e['data'].endswith('/06/2026'): pool[(e['data'],round(e['d']-e['c'],2))].append(e)
for m in june:
    l=pool.get((m['data'],round(m['valor'],2)))
    if l:
        e=l.pop(0); k=key(m['desc']); bykey[k][e['cp']]+=1; hist_of.setdefault(k,collections.Counter())[e['hist']]+=1
# 2) razao hist that look like bank desc
for e in ents:
    k=key(e['hist']); bykey[k][e['cp']]+=1
# names list for fragment matching
names=collections.defaultdict(collections.Counter)
for e in ents:
    h=norm(e['hist']); names[h][e['cp']]+=1
def classify(desc,valor):
    k=key(desc)
    if k in bykey:
        cp=bykey[k].most_common(1)[0][0]
        h=hist_of[k].most_common(1)[0][0] if k in hist_of else desc
        return cp,h,'razao-exato'
    tipo,nm=frag(desc)
    if tipo in ('PIX ENVIADO','BOLETO PAGO','SISPAG') and len(nm)>=5:
        # bank keys with same fragment
        c=collections.Counter()
        for kk,cnt in bykey.items():
            if kk.endswith(nm) or (frag(kk)[1]==nm): c.update(cnt)
        cand=[(h,cnt) for h,cnt in names.items() if h.startswith(nm[:min(len(nm),12)])]
        for h,cnt in cand: c.update(cnt)
        if c:
            cp=c.most_common(1)[0][0]; hh=cand[0][0] if cand else desc
            return cp,hh,'razao-nome'+('' if len(c)==1 else ' (varias contas: '+','.join(f"{a}x{b}" for a,b in c.most_common())+')')
    return None,desc,'sem-referencia'
