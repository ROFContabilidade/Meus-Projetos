import glob,sys
for f in sorted(glob.glob(sys.argv[1]+'/*/*.txt')):
    L=open(f,encoding='cp1252',newline='').read().split('\r\n'); bad=0; n=0; tipo=None; dd=cc=0
    lotes=[]
    for l in L:
        p=l.split('|')
        if len(p)>2 and p[1]=='6000': lotes.append([p[2],0,0])
        elif len(p)>2 and p[1]=='6100':
            v=float(p[5].replace(',','.')); 
            if p[3]: lotes[-1][1]+=v
            if p[4]: lotes[-1][2]+=v
    bad=sum(1 for t,d,c in lotes if t in 'CD' and abs(d-c)>0.001)
    print(f.split('/')[-1], L[0], len(lotes),'lotes', bad,'desbalanceados')
