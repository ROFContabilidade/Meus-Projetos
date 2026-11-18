"""Lê o Razão do Domínio em PDF (pdftotext -layout razao.pdf razao.txt) e gera CSV conta;nome;data;lote;historico;cpart;deb;cred.
Uso: python razao_pdf.py razao.txt razao.csv"""
import sys,re,csv
L=open(sys.argv[1],encoding='utf-8').read().split('\n')
num=lambda s:float(s.replace('.','').replace(',','.'))
sv=lambda s:(num(s[:-1])*(1 if s[-1]=='D' else -1)) if s[-1] in 'DC' else num(s)
rx=re.compile(r'^(\d\d/\d\d/\d{4})\s+(\d+)\s+(.*?)\s{2,}(\d+)\s+([\d.]+,\d\d)\s+([\d.]+,\d\d[DC]?)\s+([\d.]+,\d\d[DC]?)\s*$')
out=[];acc=None;prev=0.0;bad=0
for l in L:
    m=re.match(r'Conta:\s+(\d+) - (\S+)\s+(.*)',l)
    if m:
        if m.group(1)!=acc: acc=m.group(1);nm=m.group(3).strip();prev=None
        continue
    m=re.match(r'\s+SALDO ANTERIOR\s+([\d.]+,\d\d[DC]?)',l)
    if m and prev is None: prev=sv(m.group(1));continue
    m=rx.match(l)
    if m:
        d,lo,h,cp,v,s,_=m.groups();v=num(v);s2=sv(s)
        deb=v if abs(prev+v-s2)<0.02 else 0;cred=0 if deb else v
        if not deb and abs(prev-v-s2)>0.02: bad+=1
        out.append([acc,nm,d,lo,h.strip(),cp,deb,cred]);prev=s2;continue
    if re.match(r'^\d\d/\d\d/\d{4}',l): print('NOMATCH',l[:150])
    elif out and re.match(r'^\s{15,30}\S',l) and 'Total' not in l and 'SALDO' not in l and out[-1][0]==acc: out[-1][4]+=' '+l.strip()
w=csv.writer(open(sys.argv[2],'w',newline=''),delimiter=';');w.writerow(['conta','nome','data','lote','historico','cpart','deb','cred']);w.writerows(out);print(len(out),'bad',bad)
