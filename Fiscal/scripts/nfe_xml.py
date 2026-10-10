"""Leitura detalhada de XML de NF-e (modelo 55/65), item por item.

Aceita nfeProc, NFeLog (download DF-e da SEFAZ) ou NFe solta. Devolve um dict
por nota com cabeçalho, totais, referências e a lista de itens com todos os
tributos (ICMS, ICMS-ST, FCP, DIFAL, IPI, PIS, COFINS, IBS/CBS).
"""
import re
import xml.etree.ElementTree as ET
from decimal import Decimal


def _strip_ns(root):
    for el in root.iter():
        if isinstance(el.tag, str) and '}' in el.tag:
            el.tag = el.tag.split('}', 1)[1]
    return root


def _t(el, path, default=''):
    if el is None:
        return default
    x = el.find(path)
    return x.text.strip() if x is not None and x.text else default


def _d(el, path):
    v = _t(el, path)
    return Decimal(v) if v else Decimal('0')


def _icms(imp):
    """Achata o grupo ICMSxx/ICMSSNxxx em um dict."""
    g = imp.find('ICMS') if imp is not None else None
    if g is None or len(g) == 0:
        return {}
    sub = g[0]
    out = {'grupo': sub.tag}
    for c in sub:
        out[c.tag] = c.text.strip() if c.text else ''
    out['CST'] = out.get('CST') or out.get('CSOSN', '')
    return out


def _tax_group(imp, name):
    g = imp.find(name) if imp is not None else None
    if g is None:
        return {}
    out = {}
    for sub in g.iter():
        if sub is g:
            continue
        if len(sub) == 0 and sub.text:
            out.setdefault(sub.tag, sub.text.strip())
    return out


def parse_nfe(path):
    try:
        root = _strip_ns(ET.parse(path).getroot())
    except ET.ParseError as e:
        return {'erro': f'XML inválido: {e}', 'arquivo': path}
    inf = root.find('.//infNFe')
    if inf is None:
        return {'erro': 'sem infNFe (não é NF-e?)', 'arquivo': path, 'raiz': root.tag}
    chave = inf.get('Id', '')[3:]
    ide, emit, dest = inf.find('ide'), inf.find('emit'), inf.find('dest')
    tot = inf.find('total/ICMSTot')
    prot = root.find('.//protNFe/infProt')
    nota = {
        'arquivo': path,
        'chave': chave,
        'modelo': _t(ide, 'mod'), 'serie': _t(ide, 'serie'), 'numero': _t(ide, 'nNF'),
        'dt_emissao': (_t(ide, 'dhEmi') or _t(ide, 'dEmi'))[:10],
        'dt_saida_ent': _t(ide, 'dhSaiEnt')[:10],
        'tpNF': _t(ide, 'tpNF'),          # 0 entrada, 1 saída
        'finNFe': _t(ide, 'finNFe'),      # 1 normal, 2 compl., 3 ajuste, 4 devolução
        'natOp': _t(ide, 'natOp'), 'idDest': _t(ide, 'idDest'),
        'indFinal': _t(ide, 'indFinal'),
        'emit_cnpj': _t(emit, 'CNPJ') or _t(emit, 'CPF'), 'emit_nome': _t(emit, 'xNome'),
        'emit_uf': _t(emit, 'enderEmit/UF'), 'emit_ie': _t(emit, 'IE'), 'emit_crt': _t(emit, 'CRT'),
        'dest_cnpj': _t(dest, 'CNPJ') or _t(dest, 'CPF'), 'dest_nome': _t(dest, 'xNome'),
        'dest_uf': _t(dest, 'enderDest/UF'), 'dest_indIE': _t(dest, 'indIEDest'),
        'refs': [r.text for r in inf.findall('ide/NFref/refNFe') if r.text],
        'cStat': _t(prot, 'cStat'), 'xMotivo': _t(prot, 'xMotivo'),
        'infCpl': _t(inf, 'infAdic/infCpl'),
        'modFrete': _t(inf, 'transp/modFrete'),
    }
    for k in ('vBC', 'vICMS', 'vICMSDeson', 'vFCP', 'vBCST', 'vST', 'vFCPST', 'vProd', 'vFrete',
              'vSeg', 'vDesc', 'vII', 'vIPI', 'vIPIDevol', 'vPIS', 'vCOFINS', 'vOutro', 'vNF',
              'vICMSUFDest', 'vFCPUFDest'):
        nota['t_' + k] = _d(tot, k)
    itens = []
    for det in inf.findall('det'):
        p, imp = det.find('prod'), det.find('imposto')
        icms = _icms(imp)
        ipi, pis, cof = _tax_group(imp, 'IPI'), _tax_group(imp, 'PIS'), _tax_group(imp, 'COFINS')
        difal = _tax_group(imp, 'ICMSUFDest')
        D = lambda dct, k: Decimal(dct.get(k) or '0')
        itens.append({
            'nItem': det.get('nItem'),
            'cProd': _t(p, 'cProd'), 'xProd': _t(p, 'xProd'), 'NCM': _t(p, 'NCM'),
            'CEST': _t(p, 'CEST'), 'cBenef': _t(p, 'cBenef'), 'CFOP': _t(p, 'CFOP'),
            'uCom': _t(p, 'uCom'), 'qCom': _d(p, 'qCom'), 'vUnCom': _d(p, 'vUnCom'),
            'vProd': _d(p, 'vProd'), 'vFrete': _d(p, 'vFrete'), 'vSeg': _d(p, 'vSeg'),
            'vDesc': _d(p, 'vDesc'), 'vOutro': _d(p, 'vOutro'), 'indTot': _t(p, 'indTot'),
            'xPed': _t(p, 'xPed'),
            'orig': icms.get('orig', ''), 'CST_ICMS': icms.get('CST', ''), 'grupo_ICMS': icms.get('grupo', ''),
            'modBC': icms.get('modBC', ''), 'pRedBC': D(icms, 'pRedBC'),
            'vBC_ICMS': D(icms, 'vBC'), 'pICMS': D(icms, 'pICMS'), 'vICMS': D(icms, 'vICMS'),
            'vBCST': D(icms, 'vBCST'), 'pICMSST': D(icms, 'pICMSST'), 'vICMSST': D(icms, 'vICMSST'),
            'pMVAST': D(icms, 'pMVAST'),
            'vBCSTRet': D(icms, 'vBCSTRet'), 'vICMSSTRet': D(icms, 'vICMSSTRet'),
            'vFCP': D(icms, 'vFCP'), 'vFCPST': D(icms, 'vFCPST'),
            'pCredSN': D(icms, 'pCredSN'), 'vCredICMSSN': D(icms, 'vCredICMSSN'),
            'vICMSDeson': D(icms, 'vICMSDeson'), 'motDesICMS': icms.get('motDesICMS', ''),
            'vICMSDif': D(icms, 'vICMSDif'),
            'CST_IPI': ipi.get('CST', ''), 'cEnq': ipi.get('cEnq', ''),
            'vBC_IPI': D(ipi, 'vBC'), 'pIPI': D(ipi, 'pIPI'), 'vIPI': D(ipi, 'vIPI'),
            'CST_PIS': pis.get('CST', ''), 'vPIS': D(pis, 'vPIS'), 'pPIS': D(pis, 'pPIS'),
            'CST_COFINS': cof.get('CST', ''), 'vCOFINS': D(cof, 'vCOFINS'), 'pCOFINS': D(cof, 'pCOFINS'),
            'vICMSUFDest': D(difal, 'vICMSUFDest'), 'vFCPUFDest': D(difal, 'vFCPUFDest'),
            'pICMSInter': D(difal, 'pICMSInter'),
            'infAdProd': _t(det, 'infAdProd'),
        })
    nota['itens'] = itens
    # eventos anexados ao XML (download DF-e da SEFAZ traz cancelamento/CC-e junto)
    eventos = []
    for ret in root.iter('retEvento'):
        ie = ret.find('infEvento')
        if ie is not None and _t(ie, 'cStat') in ('135', '136', '155'):
            eventos.append({'tp': _t(ie, 'tpEvento'), 'desc': _t(ie, 'xEvento'),
                            'data': _t(ie, 'dhRegEvento')[:10], 'prot': _t(ie, 'nProt')})
    for ev in root.iter('evento'):
        ie = ev.find('infEvento')
        if ie is not None and _t(ie, 'tpEvento') == '110110':
            corr = _t(ie, 'detEvento/xCorrecao')
            for e in eventos:
                if e['tp'] == '110110' and not e.get('correcao'):
                    e['correcao'] = corr
    nota['eventos'] = eventos
    nota['cancelada'] = any(e['tp'] in ('110111', '110112') for e in eventos)
    nota['situacao'] = 'CANCELADA' if nota['cancelada'] else ('AUTORIZADA' if nota['cStat'] in ('100', '150') else nota['cStat'])
    return nota


def is_nfe_xml(path):
    with open(path, 'rb') as f:
        head = f.read(4000).decode('utf8', 'ignore')
    return bool(re.search(r'<(\w+:)?infNFe\b', head))
