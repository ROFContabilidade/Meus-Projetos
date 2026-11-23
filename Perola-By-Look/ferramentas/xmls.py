import zipfile,sys,re,glob,os
import xml.etree.ElementTree as ET
def strip(t):
    for e in t.iter():
        if '}' in e.tag: e.tag=e.tag.split('}')[1]
    return t
def f(e,p):
    if e is None: return ''
    x=e.find(p); return x.text.strip() if x is not None and x.text else ''
seen=set()
for z in sorted(sys.argv[1:]):
    zf=zipfile.ZipFile(z)
    for n in zf.namelist():
        if not n.lower().endswith('.xml'): continue
        try: r=strip(ET.fromstring(zf.read(n)))
        except Exception as ex: print(z,n,'ERRO',ex); continue
        key=os.path.basename(n)
        dup='(dup)' if key in seen else ''; seen.add(key)
        inf=r.find('.//infNFe')
        if inf is not None:
            em=inf.find('emit'); de=inf.find('dest')
            itens=inf.findall('det')
            cf=sorted({f(d,'prod/CFOP') for d in itens})
            prods='; '.join(f(d,'prod/xProd')[:25] for d in itens[:3])
            dups=' '.join(f(d,'dVenc')+'='+f(d,'vDup') for d in inf.findall('cobr/dup'))
            pag=','.join(f(d,'tPag')+':'+f(d,'vPag') for d in inf.findall('pag/detPag'))
            print(f"NFe|{os.path.basename(z)}|{f(inf,'ide/dhEmi')[:10]}|{f(inf,'ide/nNF')}|{f(em,'CNPJ') or f(em,'CPF')}|{f(em,'xNome')[:35]}|{f(em,'enderEmit/UF')}|dest={f(de,'CNPJ')}|mod={f(inf,'ide/mod')}|tpNF={f(inf,'ide/tpNF')}|v={f(inf,'total/ICMSTot/vNF')}|ST={f(inf,'total/ICMSTot/vST')}|CFOP={','.join(cf)}|{len(itens)}it|{prods}|dup:{dups}|pag:{pag}{dup}")
            continue
        ns=r.find('.//infNFSe')
        if ns is not None:
            dps=ns.find('.//infDPS')
            pr=dps.find('prest') if dps is not None else None
            em=ns.find('emit')
            serv=dps.find('serv') if dps is not None else None
            vals=dps.find('valores') if dps is not None else None
            trib=vals.find('trib') if vals is not None else None
            ret=[]
            for tag in ['vRetIRRF','vRetCSLL','vRetCP','vRetPisCofins' ,'vPis','vCofins']:
                x=r.find('.//'+tag)
                if x is not None and x.text: ret.append(tag+'='+x.text)
            issret=f(r,'.//tpRetISSQN')
            print(f"NFSe|{os.path.basename(z)}|{f(dps,'dhEmi')[:10] if dps is not None else ''}|{f(ns,'nNFSe')}|{f(em,'CNPJ') or f(em,'CPF')}|{f(em,'xNome')[:35]}|toma={f(dps,'toma/CNPJ') if dps is not None else ''}|cTrib={f(serv,'cServ/cTribNac') if serv is not None else ''}|{f(serv,'cServ/xDescServ')[:60] if serv is not None else ''}|v={f(vals,'vServPrest/vServ') if vals is not None else ''}|vLiq={f(ns,'valores/vLiq')}|issRet={issret}|{' '.join(ret)}{dup}")
            continue
        print('OUTRO',z,n,r.tag)
