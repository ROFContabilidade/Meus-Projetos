import sys,pickle
from collections import Counter
def parse(path):
    raw=open(path,'rb').read(); L=raw.decode('cp1252').split('\r\n')
    ents=[]; i=1
    while i<len(L):
        if L[i][:2]=='02' and i+1<len(L) and L[i+1][:2]=='03':
            l02,l03=L[i],L[i+1]; i+=2; cc=[]
            while i<len(L) and L[i][:2]=='05': cc.append((L[i][9:16],L[i][16:23],int(L[i][23:38]))); i+=1
            ents.append(dict(l02=l02,l03=l03,seq=int(l03[2:9]),d=l03[9:16],c=l03[16:23],v=int(l03[23:38]),h=l03[45:557].strip(),e=l03[557:564],date=l02[10:20],cc=cc))
        else: i+=1
    return L,ents
if __name__=='__main__':
    L,ents=parse(sys.argv[1])
    print(repr(L[0]), Counter((l[:2],len(l)) for l in L))
    print(Counter(e['e'] for e in ents), Counter(e['date'] for e in ents))
    for e in ents:
        if e['e']=='0000145': print(e['seq'],e['date'][:5],e['d'][3:],e['c'][3:],f"{e['v']/100:10.2f}",e['h'][:34], 'CC' if e['cc'] else '')
