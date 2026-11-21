import openpyxl,sys,os,glob,re,datetime,json
from collections import defaultdict
F=sys.argv[1]
def n(x):
    if x is None: return None
    if isinstance(x,(int,float)): return float(x)
    s=str(x).strip().replace('R$','').strip()
    if re.fullmatch(r'-?[\d.]+,\d+',s): s=s.replace('.','').replace(',','.')
    try: return float(s)
    except: return None
def num(x): return re.sub(r'\D','',str(x or '')).lstrip('0')
def dt(x):
    if isinstance(x,datetime.datetime): return x.strftime('%d/%m/%Y')
    m=re.match(r'(\d\d/\d\d/\d{4})',str(x or '')); return m.group(1) if m else None
def header(ws,keys):
    for i,r in enumerate(ws.iter_rows(values_only=True)):
        cells=[str(c or '').strip().upper() for c in r]
        if all(any(k in c for c in cells) for k in keys): return i,cells
    return None,None
def col(cells,*names):
    for nm in names:
        for j,c in enumerate(cells):
            if c==nm: return j
    for nm in names:
        for j,c in enumerate(cells):
            if nm in c: return j
def dominio(ws):  # Acompanhamento de saídas/entradas
    i,h=header(ws,['DATA','NOTA','CFOP','VALOR CONT'])
    if i is None: return []
    cd,cn,cc,cv=col(h,'DATA'),col(h,'NOTA','NÚMERO'),col(h,'CFOP'),col(h,'VALOR CONTÁBIL','VALOR CONT')
    cp=col(h,'CLIENTE','FORNECEDOR'); ca=col(h,'AC.')
    out=[]
    for r in list(ws.iter_rows(values_only=True))[i+1:]:
        if len(r)<=cv: continue
        d=dt(r[cd]); v=n(r[cv])
        if d and v is not None and isinstance(r[0],(int,float)):
            out.append(dict(data=d,nota=num(r[cn]),cfop=str(r[cc]),ac=str(r[ca]) if ca is not None else '',nome=str(r[cp] or ''),valor=v))
    return out
def sistema(ws): # relatorio analitico saídas
    i,h=header(ws,['NOTA','FAVORECIDO','VALOR','STATUS'])
    if i is None: return []
    out=[]
    for r in list(ws.iter_rows(values_only=True))[i+1:]:
        r=list(r)+[None]*14
        d=dt(r[col(h,'DATA')]); v=n(r[col(h,'VALOR')])
        if not d or v is None: continue
        st=' '.join(str(c) for c in r[col(h,'CHAVE DE ACESSO'):] if c is not None)
        out.append(dict(data=d,nota=num(r[col(h,'NOTA')]),modelo=str(r[col(h,'MODELO')]),nome=str(r[col(h,'FAVORECIDO')]),cfop=str(r[col(h,'CFOP')]),valor=v,
                        autorizada='100 - Autorizado' in st, cancelada='Cancel' in st or '101' in st[:4], status=st[:70]))
    return out
def consulta(ws): # NF-e consultadas (recebidas)
    i,h=header(ws,['NÚMERO','EMITENTE','VALOR'])
    if i is None: i,h=header(ws,['NUMERO','EMITENTE','VALOR'])
    if i is None: return []
    out=[]
    for r in list(ws.iter_rows(values_only=True))[i+1:]:
        r=list(r)+[None]*8
        v=n(r[col(h,'VALOR')]); d=dt(r[col(h,'DATA')]) if col(h,'DATA') is not None else None
        if v is None or not num(r[col(h,'NÚMERO','NUMERO')]): continue
        stc=col(h,'STATUS'); st=str(r[stc] or '') if stc is not None else ''
        ch=col(h,'CHAVE'); chave=str(r[ch] or '') if ch is not None else ''
        out.append(dict(data=d,nota=num(r[col(h,'NÚMERO','NUMERO')]),nome=str(r[col(h,'EMITENTE')] or ''),valor=v,status=st,chave=chave))
    return out
def fat_total(wb):
    for ws in wb.worksheets:
        if ws.title.upper().startswith('FATURAMENTO') and 'M' not in ws.title.upper().replace('FATURAMENTO','')[:3].replace('_',''):
            pass
    tot={}
    for ws in wb.worksheets:
        if 'FAT' in ws.title.upper():
            for r in ws.iter_rows(values_only=True):
                if r and str(r[0]).strip()=='Totais': tot[ws.title]=[x for x in r[1:] if isinstance(x,(int,float))]
    return tot
res={}
for emp in ('34','118'):
    for m in range(1,10):
        mm=f'{m:02d}'; d={}
        p=glob.glob(f'{F}/{emp}_FAT_{mm}.xlsx')
        if p:
            wb=openpyxl.load_workbook(p[0],data_only=True)
            d['sai_dom']=[x for ws in wb.worksheets if ws.title.startswith('Sa') for x in dominio(ws)]
            d['sai_sis']=[x for ws in wb.worksheets if 'ANALITICO' in ws.title for x in sistema(ws)]
            d['fat']=fat_total(wb)
        if emp=='34' and mm=='01':
            wb=openpyxl.load_workbook(f'{F}/34_SAI_01.xlsx',data_only=True); d['sai_dom_xls']=[x for ws in wb.worksheets for x in dominio(ws)]
        p=glob.glob(f'{F}/{emp}_ENT_{mm}*.xlsx')
        p=[x for x in p if not x.endswith('05.xlsx') or emp!='34'] if emp=='34' and mm=='05' else p
        if p:
            wb=openpyxl.load_workbook(sorted(p)[-1],data_only=True)
            d['ent_dom']=[x for ws in wb.worksheets if ws.title=='Entradas' for x in dominio(ws)]
            d['ent_nfe']=[x for ws in wb.worksheets if ws.title in('download_excel','NFe','Recebidas') for x in consulta(ws)]
        res[f'{emp}-{mm}']=d
json.dump(res,open(F+'/fiscal.json','w'),ensure_ascii=False)
for k,d in res.items():
    print(k,'sai_dom',len(d.get('sai_dom',[])),round(sum(x['valor'] for x in d.get('sai_dom',[])),2),
          '| sis',len(d.get('sai_sis',[])),'| fat',d.get('fat'),'| ent_dom',len(d.get('ent_dom',[])),round(sum(x['valor'] for x in d.get('ent_dom',[])),2),
          '| nfe',len(d.get('ent_nfe',[])),round(sum(x['valor'] for x in d.get('ent_nfe',[])),2))
