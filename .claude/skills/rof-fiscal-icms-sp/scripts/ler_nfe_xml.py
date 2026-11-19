"""Lê XML de NF-e (modelo 55, leiaute 4.00) - avulsos, em pastas ou dentro de ZIP - e grava um JSON por item.

python3 -I ler_nfe_xml.py <pasta|arquivos|zip> --saida notas.json
"""
import json, os, re, sys, zipfile, io
import xml.etree.ElementTree as ET


def ln(tag):
    return tag.split('}', 1)[-1]


def filho(el, nome):
    if el is None:
        return None
    for c in el:
        if ln(c.tag) == nome:
            return c
    return None


def caminho(el, *nomes):
    for n in nomes:
        el = filho(el, n)
        if el is None:
            return None
    return el


def txt(el, *nomes):
    e = caminho(el, *nomes)
    return (e.text or '').strip() if e is not None and e.text else ''


def num(v):
    try:
        return float(v)
    except (TypeError, ValueError):
        return 0.0


def achar_todos(el, nome):
    return [e for e in el.iter() if ln(e.tag) == nome]


def bloco_icms(imp):
    """Retorna (grupo, dict) do grupo ICMSxx / ICMSSNxxx do item."""
    icms = filho(imp, 'ICMS')
    if icms is None or len(icms) == 0:
        return '', {}
    g = icms[0]
    return ln(g.tag), {ln(c.tag): (c.text or '').strip() for c in g}


def ler_xml(conteudo, origem):
    root = ET.fromstring(conteudo)
    infs = achar_todos(root, 'infNFe')
    if not infs:
        return None
    inf = infs[0]
    chave = re.sub(r'\D', '', inf.get('Id', ''))
    ide, emit, dest, tot = (filho(inf, x) for x in ('ide', 'emit', 'dest', 'total'))
    icmstot = filho(tot, 'ICMSTot')
    prot = achar_todos(root, 'infProt')
    cstat = txt(prot[0], 'cStat') if prot else ''
    eventos = [txt(e, 'tpEvento') for e in achar_todos(root, 'infEvento')]
    transp = filho(inf, 'transp')
    nota = {
        'arquivo': origem, 'chave': chave, 'modelo': txt(ide, 'mod'), 'serie': txt(ide, 'serie'), 'numero': txt(ide, 'nNF'),
        'emissao': (txt(ide, 'dhEmi') or txt(ide, 'dEmi'))[:10], 'saida_entrada': (txt(ide, 'dhSaiEnt') or '')[:10],
        'natureza': txt(ide, 'natOp'), 'tpNF': txt(ide, 'tpNF'), 'idDest': txt(ide, 'idDest'),
        'indFinal': txt(ide, 'indFinal'), 'finNFe': txt(ide, 'finNFe'),
        'protocolo_cStat': cstat, 'eventos': eventos,
        'emit_cnpj': txt(emit, 'CNPJ') or txt(emit, 'CPF'), 'emit_nome': txt(emit, 'xNome'),
        'emit_uf': txt(emit, 'enderEmit', 'UF'), 'emit_municipio': txt(emit, 'enderEmit', 'xMun'),
        'emit_ie': txt(emit, 'IE'), 'emit_iest': txt(emit, 'IEST'), 'emit_crt': txt(emit, 'CRT'),
        'dest_cnpj': txt(dest, 'CNPJ') or txt(dest, 'CPF'), 'dest_nome': txt(dest, 'xNome'),
        'dest_uf': txt(dest, 'enderDest', 'UF'), 'dest_municipio': txt(dest, 'enderDest', 'xMun'),
        'dest_ie': txt(dest, 'IE'), 'dest_indIEDest': txt(dest, 'indIEDest'),
        'modFrete': txt(transp, 'modFrete'),
        'vProd': num(txt(icmstot, 'vProd')), 'vNF': num(txt(icmstot, 'vNF')), 'vBC': num(txt(icmstot, 'vBC')),
        'vICMS': num(txt(icmstot, 'vICMS')), 'vST': num(txt(icmstot, 'vST')), 'vIPI': num(txt(icmstot, 'vIPI')),
        'vFrete': num(txt(icmstot, 'vFrete')), 'vDesc': num(txt(icmstot, 'vDesc')),
        'vICMSUFDest': num(txt(icmstot, 'vICMSUFDest')), 'vFCPUFDest': num(txt(icmstot, 'vFCPUFDest')),
        'infCpl': txt(inf, 'infAdic', 'infCpl'), 'infAdFisco': txt(inf, 'infAdic', 'infAdFisco'),
        'itens': [],
    }
    for det in [c for c in inf if ln(c.tag) == 'det']:
        prod, imp = filho(det, 'prod'), filho(det, 'imposto')
        grupo, ic = bloco_icms(imp)
        ipi = filho(imp, 'IPI')
        ipitrib = filho(ipi, 'IPITrib') if ipi is not None else None
        ufd = filho(imp, 'ICMSUFDest')
        it = {
            'nItem': det.get('nItem'), 'codigo': txt(prod, 'cProd'), 'descricao': txt(prod, 'xProd'),
            'ncm': txt(prod, 'NCM'), 'cest': txt(prod, 'CEST'), 'cfop': txt(prod, 'CFOP'), 'unid': txt(prod, 'uCom'),
            'qtd': num(txt(prod, 'qCom')), 'vProd': num(txt(prod, 'vProd')), 'vFrete': num(txt(prod, 'vFrete')),
            'vSeg': num(txt(prod, 'vSeg')), 'vDesc': num(txt(prod, 'vDesc')), 'vOutro': num(txt(prod, 'vOutro')),
            'icms_grupo': grupo, 'orig': ic.get('orig', ''), 'cst': ic.get('CST', ''), 'csosn': ic.get('CSOSN', ''),
            'modBC': ic.get('modBC', ''), 'vBC': num(ic.get('vBC')), 'pICMS': num(ic.get('pICMS')),
            'vICMS': num(ic.get('vICMS')), 'pRedBC': num(ic.get('pRedBC')),
            'vBCST': num(ic.get('vBCST')), 'pICMSST': num(ic.get('pICMSST')), 'vICMSST': num(ic.get('vICMSST')),
            'pMVAST': num(ic.get('pMVAST')), 'pCredSN': num(ic.get('pCredSN')), 'vCredICMSSN': num(ic.get('vCredICMSSN')),
            'vBCSTRet': num(ic.get('vBCSTRet')), 'vICMSSTRet': num(ic.get('vICMSSTRet')),
            'vIPI': num(txt(ipitrib, 'vIPI')) if ipitrib is not None else 0.0,
            'ufdest_vBC': num(txt(ufd, 'vBCUFDest')), 'ufdest_pInt': num(txt(ufd, 'pICMSUFDest')),
            'ufdest_pInter': num(txt(ufd, 'pICMSInter')), 'ufdest_v': num(txt(ufd, 'vICMSUFDest')),
            'tem_ICMSUFDest': ufd is not None, 'infAdProd': txt(det, 'infAdProd'),
        }
        nota['itens'].append(it)
    return nota


def arquivos(entradas):
    for e in entradas:
        if os.path.isdir(e):
            for raiz, _, fs in os.walk(e):
                for f in sorted(fs):
                    yield from arquivos([os.path.join(raiz, f)])
        elif e.lower().endswith('.zip'):
            with zipfile.ZipFile(e) as z:
                for n in z.namelist():
                    if n.lower().endswith('.xml'):
                        yield f'{e}::{n}', z.read(n)
        elif e.lower().endswith('.xml'):
            with open(e, 'rb') as fh:
                yield e, fh.read()


def main():
    args = sys.argv[1:]
    saida = 'notas.json'
    if '--saida' in args:
        i = args.index('--saida'); saida = args[i + 1]; del args[i:i + 2]
    notas, erros = [], []
    for nome, conteudo in arquivos(args):
        try:
            n = ler_xml(conteudo, nome)
            if n is None:
                erros.append(f'{nome}: não é NF-e (sem infNFe) - CT-e/evento/NFS-e? ler à parte')
            else:
                notas.append(n)
        except ET.ParseError as ex:
            erros.append(f'{nome}: XML inválido ({ex})')
    json.dump({'notas': notas, 'erros_leitura': erros}, open(saida, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print(f'{len(notas)} NF-e lidas, {sum(len(n["itens"]) for n in notas)} itens -> {saida}')
    for e in erros:
        print('  ATENÇÃO:', e)


if __name__ == '__main__':
    main()
