import glob,collections,re
def num(s): return float(s.replace(',','.'))
saldo={'8':6807.60,'9':1739.00}; mes=collections.defaultdict(lambda:collections.Counter())
erros=0; contas=collections.Counter()
for f in sorted(glob.glob('out/PEROLA_49_*.txt')):
    lote=None; ln=[]
    def fecha():
        global erros
        if not lote: return
        if lote=='X':
            for l in ln:
                _,_,d,deb,cred,v,*r=l.split('|'); v=num(v)
                for c,s in((deb,1),(cred,-1)): mes[(d[3:5],c)]['m']+=s*v; contas[c]+=s*v
        else:
            first=ln[0].split('|'); tot=num(first[5]); soma=sum(num(l.split('|')[5]) for l in ln[1:])
            if abs(tot-soma)>.005: erros+=1; print('LOTE DESBALANCEADO',f,first)
            for i,l in enumerate(ln):
                p=l.split('|'); d=p[2]; deb,cred,v=p[3],p[4],num(p[5])
                if deb: mes[(d[3:5],deb)]['m']+=v; contas[deb]+=v
                if cred: mes[(d[3:5],cred)]['m']-=v; contas[cred]-=v
    for l in open(f,encoding='latin-1'):
        l=l.rstrip('\r\n')
        if l.startswith('|6000|'): fecha(); lote=l.split('|')[2]; ln=[]
        elif l.startswith('|6100|'): ln.append(l)
    fecha()
for b in '89':
    s=saldo[b]
    for m in ['01','02','03','04','05','06','07','08','09','10']:
        s+=mes[(m,b)]['m']; print(b,m,round(s,2))
print('erros',erros)
for c,v in sorted(contas.items(),key=lambda z:-abs(z[1])): print(f"{c:>10} {v:12.2f}")
