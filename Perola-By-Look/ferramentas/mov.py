import re,glob,json,collections,unicodedata
def num(s): return float(s.replace('.','').replace(',','.')) if ',' in s else float(s)
def norm(h):
    h=unicodedata.normalize('NFKD',h.upper()).encode('ascii','ignore').decode()
    h=re.sub(r'^(REF\.? ?A\.?|REF)\s*','',h)
    h=re.sub(r'(PIX ENVIADO|PAGAMENTOS PIX QR-CODE|PAGAMENTOS|QR CODE PIX ENVIADO|PIX RECEBIDO|PAGAMENTO DE CONTA|BOLETO PAGO|PIX ENVIADO -)\s*[-/]?\s*','',h)
    h=re.sub(r'[\d\./-]{5,}','',h); h=re.sub(r'\s+',' ',h).strip(' -/')
    return h[:40]
def load():
    out=[]
    for f in sorted(glob.glob('ext/[01][0-9]_*.md')):
        m,b=f.split('/')[-1][:-3].split('_',1)
        if b=='emps': continue
        for l in open(f,encoding='utf-8'):
            p=l.rstrip('\n').split('|')
            if not re.match(r'\d\d/\d\d/\d{4}$',p[0]): continue
            if 'SALDO' in p[1].upper() or 'Saldo do dia' in p[1]: continue
            val=p[3] if len(p)>=5 else p[2]
            if not val: continue
            if p[0][3:5]!=m: continue
            out.append(dict(mes=m,banco='9' if b=='itau' else '8',data=p[0],hist=p[1],doc=p[2] if len(p)>=5 else '',v=num(val),k=norm(p[1])))
    return out
