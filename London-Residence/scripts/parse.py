import subprocess,re,json,sys,glob
S=sys.argv[1]; out=[]  # S = pasta que contém a subpasta extratos/ (PDFs do Sicredi, um por mês, em ordem 01.pdf, 02.pdf...)
num=lambda s: float(s.replace('.','').replace(',','.'))
for f in sorted(glob.glob(S+'/extratos/*.pdf')):
    t=subprocess.run(['pdftotext','-layout',f,'-'],capture_output=True,text=True).stdout
    t=t.split('Lançamentos Futuros')[0].split('Saldo da conta')[0]
    prev=None
    for line in t.splitlines():
        m=re.match(r'\s*SALDO ANTERIOR\s+([\d.,-]+)',line)
        if m: prev=num(m.group(1)); start=prev; continue
        m=re.match(r'(\d\d/\d\d/\d{4})\s+(.*?)\s{2,}(\S+)?\s+(-?[\d.]+,\d\d)\s+(-?[\d.]+,\d\d)\s*$',line)
        if m:
            d,desc,doc,v,s=m.groups(); v=num(v); s=num(s)
            ok=abs(prev+v-s)<0.005; prev=s
            out.append(dict(data=d,desc=desc.strip(),doc=doc or '',valor=v,saldo=s,ok=ok,arq=f[-6:]))
        elif re.match(r'\d\d/\d\d/\d{4}',line): print('UNPARSED',f,line)
json.dump(out,open(sys.argv[2] if len(sys.argv)>2 else S+'/lanc.json','w'),ensure_ascii=False,indent=0)
print(len(out),'lanc; bad',sum(not x['ok'] for x in out), 'first',out[0]['data'],'last',out[-1]['data'],out[-1]['saldo'])
for x in out:
    if not x['ok']: print('BAD',x)
