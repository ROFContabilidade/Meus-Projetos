import re,json,sys
NUM=r'-?\d{1,3}(?:\.\d{3})*,\d{2}'
def v(s): return float(s.replace('.','').replace(',','.'))
def parse(path):
    out=[];cur=None
    for ln in open(path,encoding='utf-8'):
        ln=ln.rstrip('\n')
        m=re.match(r'^\s*\\?-?\s*-?\s*(\d{2}/\d{2}/\d{2})[\s-]+(\d{2}/\d{2}/\d{2})[\s-]+(.+?)[\s-]+(\d{2,3})[\s-]+(\d{1,3})[\s-]+(\d{1,3})[\s-]+('+NUM+r')[\s-]+('+NUM+r')[\s-]+('+NUM+r')',ln)
        if m:
            cur=dict(dl=m.group(1),data=m.group(2)[:6]+'2026',nome=re.sub(r'[\s-]+',' ',m.group(3)).strip(),op=int(m.group(4)),pf=int(m.group(5)),pr=int(m.group(6)),ent=v(m.group(7)),sai=v(m.group(8)),obs='')
            out.append(cur); continue
        if cur and ln.strip() and not ln.strip().startswith('---') and not re.search(r'Cosmos ERP|Extrato Da Conta|Grupo Neg|Empresa:|Conta:|Dt\. Lancto|COSMETICI$|Data:',ln):
            if len(cur['obs'])<200: cur['obs']=(cur['obs']+' '+ln.strip()).strip()
        if re.search(r'^-{10,}',ln.strip()): cur=None
    return out
if __name__=='__main__':
    for p in sys.argv[1:]:
        o=parse(p); json.dump(o,open(p.replace('.txt','.json'),'w'),ensure_ascii=False)
        print(p,len(o),'ent',round(sum(x['ent'] for x in o),2),'sai',round(sum(x['sai'] for x in o),2))
