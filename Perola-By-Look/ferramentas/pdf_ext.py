import re,sys,json
def num(s): return float(s.replace('.','').replace(',','.'))
def pagbank(path,mes):
    out=[]
    for l in open(path,encoding='utf-8'):
        m=re.match(r'\s*(\d\d/\d\d/\d{4})\s+(.+?)\s+(-?)R\$ ([\d\.]+,\d\d)\s*$',l)
        if not m or 'Saldo do dia' in m.group(2): continue
        if m.group(1)[3:5]!=mes: continue
        v=num(m.group(4))*(-1 if m.group(3) else 1)
        out.append(dict(data=m.group(1),banco='8',hist=m.group(2).strip(),nome='',doc='',v=round(v,2)))
    return out
def itau(path,mes):
    L=open(path,encoding='utf-8').read().split('\n')
    hdr=next(i for i,l in enumerate(L) if 'Razão Social' in l and 'CNPJ/CPF' in l)
    h=L[hdr]; cR=h.index('Razão Social'); cC=h.index('CNPJ/CPF'); cL=h.index('Lançamentos')
    anchors=[];  # (idx, data, value or None, saldo)
    rx=re.compile(r'^\s*(\d\d/\d\d/\d{4})\s')
    for i,l in enumerate(L):
        if i<=hdr: continue
        m=rx.match(l)
        if not m: continue
        nums=re.findall(r'-?[\d\.]+,\d\d',l[cC:] if len(l)>cC else '')
        anchors.append(i)
    rows=[]
    prev_after=0
    for k,i in enumerate(anchors):
        l=L[i]
        nxt=anchors[k+1] if k+1<len(anchors) else min(i+3,len(L))
        prv=anchors[k-1] if k>0 else hdr
        gap_before=[j for j in range(prv+1,i) if L[j].strip()]
        before=gap_before[prev_after:]
        gap_after=[j for j in range(i+1,nxt) if L[j].strip()]
        after=gap_after[:len(before)]
        prev_after=len(after)
        def col(s,a,b): return s[a:b].strip() if len(s)>a else ''
        lines=[L[j] for j in before]+[l]+[L[j] for j in after]
        lanc=' '.join(col(s,cL,cR) for s in lines if col(s,cL,cR))
        nome=' '.join(col(s,cR,cC) for s in lines if col(s,cR,cC))
        tail=l[cC:] if len(l)>cC else ''
        doc=re.search(r'[\d\.\-/]{11,}',tail); doc=doc.group(0) if doc else ''
        rest=tail.replace(doc,'') if doc else tail
        vals=re.findall(r'-?[\d\.]+,\d\d',rest)
        if 'SALDO' in lanc.upper() or not vals: continue
        dt=rx.match(l).group(1)
        if dt[3:5]!=mes: continue
        rows.append(dict(data=dt,banco='9',hist=lanc,nome=nome,doc=doc,v=num(vals[0])))
    return rows
if __name__=='__main__':
    allm=[]
    for m in ['01','02','03','04','05','06']:
        a=itau(f'ext16/{m}_itau.txt',m); b=pagbank(f'ext16/{m}_pagbank.txt',m)
        for x in a+b: x['mes']=m
        allm+=a+b
    json.dump(allm,open('mov16.json','w'),ensure_ascii=False)
    import collections
    s=collections.defaultdict(lambda:[0,0,0])
    for x in allm: k=(x['mes'],x['banco']); s[k][0]+=1; s[k][1]+=max(x['v'],0); s[k][2]+=-min(x['v'],0)
    for k in sorted(s): print(k,s[k][0],round(s[k][1],2),round(s[k][2],2))
