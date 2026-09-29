import openpyxl,re,sys,pickle
from collections import defaultdict
def num(x):
    if isinstance(x,(int,float)): return float(x)
    return float(str(x).replace('.','').replace(',','.'))
def parse(path):
    wb=openpyxl.load_workbook(path,data_only=True)
    # usar a aba do extrato (o arquivo do Drive pode ter abas extras, ex.: fechamento colado pela usuária)
    ws=next((w for w in wb if w.title.strip().lower().startswith('extrato')), wb.worksheets[0])
    cc=None; emp=None; mode=None
    E=defaultdict(lambda: defaultdict(float))   # (cc,emp) -> {(cod,nome,PD):valor}
    CCS={}; enc=defaultdict(dict); resumo={}
    for r in ws.iter_rows(values_only=True):
        v=[c for c in r if c not in (None,'')]
        if not v: continue
        s0=str(v[0])
        if s0.startswith('C.Custo:'):
            m=re.match(r'C\.Custo:\s*(\d+)\s*-\s*(.*)',s0); cc=int(m.group(1)); CCS[cc]=m.group(2).strip(); mode='emp'; continue
        if s0=='Empr.:': emp=v[2].strip(); mode='emp'; continue
        if s0.startswith('Resumo por Rubricas do Centro'): mode='rescc'; continue
        if s0.startswith('Totais por'): mode='tot'; continue
        if s0=='Resumo por Rubrica': mode='resger'; cc=None; continue
        if s0 in('Segurados:','Empresa:','RAT:','Terceiros:','Total INSS:') and mode!='resger' and cc is not None and isinstance(v[1],(int,float)):
            enc[cc][s0[:-1]]=v[1]
        if s0=='Valor Total do IRRF:' and cc is not None: enc[cc]['IRRF']=v[1]
        if s0=='Salário contribuição contribuintes:' and cc is not None and len(v)>3: enc[cc]['FGTS']=v[3]
        if s0=='Segurados:' and len(v)>3 and cc is not None: pass
        if s0=='Empresa:' and len(v)>3 and cc is not None and 'FGTS' in str(v[2]): pass
        # rubric rows: [cod,nome,ref,valor,P/D, cod,nome,ref,valor,P/D]
        i=0
        while i+4<len(v)+0 and isinstance(v[i],int) and isinstance(v[i+1],str) and i+4<len(v) and v[i+4] in('P','D','I'):
            key=(v[i],v[i+1].strip(),v[i+4])
            if mode=='emp' and cc is not None and emp: E[(cc,emp)][key]+=num(v[i+3])
            elif mode=='resger': resumo[key]=num(v[i+3])
            i+=5
        if s0=='Valor do FGTS:' : pass
    return CCS,E,enc,resumo
if __name__=='__main__':
    CCS,E,enc,res=parse(sys.argv[1]); pickle.dump((CCS,dict((k,dict(x)) for k,x in E.items()),dict(enc),res),open(sys.argv[2],'wb'))
    print(CCS)
    tp=sum(v for x in E.values() for (c,n,pd),v in x.items() if pd=='P'); td=sum(v for x in E.values() for (c,n,pd),v in x.items() if pd=='D')
    print('P',round(tp,2),'D',round(td,2)); print('resumo P',round(sum(v for k,v in res.items() if k[2]=='P'),2),'D',round(sum(v for k,v in res.items() if k[2]=='D'),2))
    for k,v in enc.items(): print(k,v)
