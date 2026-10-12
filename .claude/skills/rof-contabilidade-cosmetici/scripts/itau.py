import re,sys,json
AMT=r'\d{1,3}(?:\.\d{3})*,\d{2}-?'
def num(s):
    neg=s.endswith('-'); v=float(s.rstrip('-').replace('.','').replace(',','.')); return -v if neg else v
def parse(path, year):
    lines=open(path,encoding='utf-8').read().split('\n')
    out=[]; cur=None; started=False; saldo_ant=None; checks=[]
    for ln in lines:
        if 'Saldo anterior' in ln:
            m=re.search(r'(\d{2}/\d{2})\s+Saldo anterior\s+('+AMT+')',ln); saldo_ant=num(m.group(2)); started=True; run=saldo_ant; continue
        if not started: continue
        if re.search(r'Saldo final|totalizador de aplica|Conta Corrente \| Aplica|Notas explicativas|^\s*Aviso',ln,re.I): break
        m=re.match(r'^(.*?)(?:(\d{2}/\d{2})\s{2,})?(\S.*?)\s{2,}('+AMT+r')(?:\s{2,}('+AMT+r'))?\s*$',ln)
        if not m: continue
        pre,dt,desc,a1,a2=m.groups()
        # handle sidebar: date could be in pre
        md=re.search(r'(\d{2}/\d{2})\s*$',pre or '')
        if not dt and md: dt=md.group(1)
        if dt: cur=dt
        desc=desc.strip()
        # strip sidebar text glued before date
        if re.search(r'\d{2}/\d{2}\s{2,}',desc):
            mm=re.search(r'(\d{2}/\d{2})\s{2,}(.*)$',desc); cur=mm.group(1); desc=mm.group(2)
        parts=re.split(r'\s{2,}',desc)
        if len(parts)>1 and re.match(r'^([A-Z] = |pela Bolsa|Para demais|Explicativas)',parts[0]): desc=parts[-1]
        if re.match(r'(SALDO APLIC AUT|SALDO TOTAL|SALDO EM C/C|SALDO FINAL)',desc.upper()):
            continue
        if desc.startswith('data ') or desc.startswith('(cr'): continue
        v=num(a1); run=round(run+v,2)
        out.append(dict(data=f"{cur}/{year}",desc=desc,valor=v))
        if a2:
            checks.append((cur,desc,num(a2),run))
    return saldo_ant,out,checks
if __name__=='__main__':
    sa,out,ch=parse(sys.argv[1],sys.argv[2])
    print('saldo_ant',sa,'n',len(out),'net',round(sum(o['valor'] for o in out),2))
    bad=[c for c in ch if abs(c[2]-c[3])>0.005 and abs(c[2]-1.0)>0.005]
    print('checks',len(ch),'bad',len(bad))
    for b in bad[:15]: print(b)
    json.dump(dict(saldo_ant=sa,mov=out),open(sys.argv[3],'w'),ensure_ascii=False,indent=0)
