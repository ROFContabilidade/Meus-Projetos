import pdfplumber,re,sys,json
def num(s): return float(s.replace('.','').replace(',','.'))
def itau(path,mes):
    out=[]
    pdf=pdfplumber.open(path)
    for p in pdf.pages:
        ws=p.extract_words(keep_blank_chars=False)
        # header x positions
        hx={}
        for w in ws:
            if w['text'] in('Lançamentos','Razão','CNPJ/CPF','Valor','Saldo') and w['text'] not in hx: hx[w['text']]=w['x0']
        xL=80; xR=223; xC=359
        xV=xC+80; xS=hx.get('Saldo',None)
        anchors=[w for w in ws if re.match(r'\d\d/\d\d/\d{4}$',w['text']) and w['x0']<xL]
        for a in anchors:
            t=a['top']; near=[w for w in ws if abs(w['top']-t)<=7.5 and w['x0']>a['x1']]
            near.sort(key=lambda w:(round(w['top']),w['x0']))
            lanc=' '.join(w['text'] for w in near if xL<=w['x0']<xR)
            nome=' '.join(w['text'] for w in near if xR<=w['x0']<xC)
            doc=' '.join(w['text'] for w in near if xC<=w['x0']<xC+75 and re.search(r'\d',w['text']) and not re.match(r'-?[\d\.]+,\d\d$',w['text']))
            nums=[w for w in near if re.match(r'-?[\d\.]+,\d\d$',w['text']) and abs(w['top']-t)<2]
            if 'SALDO' in lanc.upper() or not nums: continue
            nums.sort(key=lambda w:w['x0'])
            v=num(nums[0]['text'])
            if a['text'][3:5]!=mes: continue
            out.append(dict(data=a['text'],banco='9',hist=lanc,nome=nome,doc=doc,v=v))
    return out
