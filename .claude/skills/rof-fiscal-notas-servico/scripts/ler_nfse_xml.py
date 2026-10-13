"""Lê XML de NFS-e (Padrão Nacional - nfse.gov.br - e ABRASF/municipais) e gera JSON com uma nota por item.

python ler_nfse_xml.py <arquivo.xml|pasta> [...] --saida notas.json

Campos que não forem encontrados ficam vazios: completar à mão no JSON (ou ler o PDF) e apontar a lacuna.
Notas em PDF: extrair com `pdftotext -layout arquivo.pdf -` e preencher o mesmo JSON manualmente.
"""
import json, os, re, sys
import xml.etree.ElementTree as ET


def ln(tag):
    return tag.rsplit('}', 1)[-1]


def achar(el, *caminhos):
    """Primeiro texto encontrado. Caminho = nomes de tags separados por '/', '//' no início = qualquer nível."""
    if el is None:
        return ''
    for cam in caminhos:
        partes = cam.split('/')
        nos = [el]
        for i, p in enumerate(partes):
            novos = []
            for n in nos:
                novos += [x for x in n.iter() if ln(x.tag) == p and x is not n] if i == 0 else [x for x in n if ln(x.tag) == p]
            nos = novos
            if not nos:
                break
        for n in nos:
            if n.text and n.text.strip():
                return n.text.strip()
    return ''


def num(v):
    if v in ('', None):
        return None
    v = str(v).strip()
    if ',' in v and '.' in v: v = v.replace('.', '').replace(',', '.')
    elif ',' in v: v = v.replace(',', '.')
    try: return float(v)
    except ValueError: return None


def bloco(el, *nomes):
    for x in el.iter():
        if ln(x.tag) in nomes:
            return x
    return None


def nota_nacional(inf, arq):
    """infNFSe do Padrão Nacional (Sefin Nacional / ADN)."""
    dps = bloco(inf, 'infDPS')
    dps = inf if dps is None else dps
    prest = bloco(dps, 'prest'); toma = bloco(dps, 'toma'); serv = bloco(dps, 'serv'); val = bloco(dps, 'valores')
    emit = bloco(inf, 'emit')
    trib_mun = bloco(dps, 'tribMun'); trib_fed = bloco(dps, 'tribFed')
    vals_nfse = bloco(inf, 'valores')  # valores calculados da NFS-e (fora da DPS)
    ib = bloco(inf, 'IBSCBS')
    n = {
        'arquivo': os.path.basename(arq), 'layout': 'NFS-e Nacional',
        'numero': achar(inf, 'nNFSe'), 'chave': (inf.get('Id') or '').replace('NFS', ''),
        'serie_dps': achar(dps, 'serie'), 'numero_dps': achar(dps, 'nDPS'),
        'data_emissao': achar(inf, 'dhProc') or achar(dps, 'dhEmi'), 'competencia': achar(dps, 'dCompet'),
        'situacao': achar(inf, 'cStat'),
        'prestador_cnpj': (achar(prest, 'CNPJ', 'CPF') if prest is not None else '') or (achar(emit, 'CNPJ', 'CPF') if emit is not None else ''),
        'prestador_nome': achar(emit, 'xNome') if emit is not None else '',
        'prestador_regime_sn': achar(dps, 'opSimpNac'),  # 1 não optante, 2 MEI, 3 ME/EPP
        'prestador_reg_ap_sn': achar(dps, 'regApTribSN'),
        'tomador_doc': (achar(toma, 'CNPJ', 'CPF', 'NIF') if toma is not None else ''),
        'tomador_nome': (achar(toma, 'xNome') if toma is not None else ''),
        'tomador_municipio': (achar(toma, 'cMun') if toma is not None else ''),
        'municipio_prestacao': achar(inf, 'xLocPrestacao') or achar(dps, 'cLocPrestacao'),
        'municipio_incidencia': achar(inf, 'xLocIncid') or achar(inf, 'cLocIncid'),
        'item_lc116': achar(serv, 'cTribNac') if serv is not None else '',
        'trib_municipal': achar(serv, 'cTribMun') if serv is not None else '',
        'atividade': achar(inf, 'xTribNac') or achar(inf, 'xTribMun'),
        'nbs': achar(serv, 'cNBS') if serv is not None else '',
        'descricao': achar(serv, 'xDescServ') if serv is not None else '',
        'info_complementar': achar(dps, 'xInfComp') or achar(inf, 'xOutInf'),
        'valor_servico': num(achar(val, 'vServ')) if val is not None else None,
        'desconto_incond': num(achar(val, 'vDescIncond')) if val is not None else None,
        'deducoes': num(achar(val, 'vDR')) if val is not None else None,
        'base_iss': num(achar(vals_nfse, 'vBC')) if vals_nfse is not None else None,
        'aliquota_iss': num(achar(vals_nfse, 'pAliqAplic')) if vals_nfse is not None else num(achar(trib_mun, 'pAliq')),
        'valor_iss': num(achar(vals_nfse, 'vISSQN')) if vals_nfse is not None else None,
        'trib_issqn': achar(trib_mun, 'tribISSQN') if trib_mun is not None else '',  # 1 tributável 2 imunidade 3 exportação 4 não incidência
        'iss_retido': achar(trib_mun, 'tpRetISSQN') if trib_mun is not None else '',  # 1 não retido 2 retido tomador 3 retido intermediário
        'irrf': num(achar(trib_fed, 'vRetIRRF')) if trib_fed is not None else None,
        'csll': num(achar(trib_fed, 'vRetCSLL')) if trib_fed is not None else None,
        'pis': num(achar(trib_fed, 'piscofins/vPis', 'vPis')) if trib_fed is not None else None,
        'cofins': num(achar(trib_fed, 'piscofins/vCofins', 'vCofins')) if trib_fed is not None else None,
        'pis_cofins_retido': achar(trib_fed, 'tpRetPisCofins') if trib_fed is not None else '',
        'inss': num(achar(trib_fed, 'vRetCP')) if trib_fed is not None else None,
        'valor_liquido': num(achar(vals_nfse, 'vLiq')) if vals_nfse is not None else None,
        'ibs_cbs': (f"CBS {achar(ib, 'vCBS')} / IBS {achar(ib, 'vIBSTot', 'vIBS')}" if ib is not None else ''),
        'substituida': achar(dps, 'chSubstda'),
    }
    n['iss_retido'] = {'1': 'Não', '2': 'Sim (tomador)', '3': 'Sim (intermediário)'}.get(n['iss_retido'], n['iss_retido'])
    n['prestador_regime_sn'] = {'1': 'Não optante', '2': 'MEI', '3': 'ME/EPP Simples'}.get(n['prestador_regime_sn'], n['prestador_regime_sn'])
    return n


def nota_abrasf(inf, arq):
    """InfNfse / InfDeclaracaoPrestacaoServico (ABRASF 1.0/2.0x e variações municipais)."""
    prest = bloco(inf, 'PrestadorServico', 'Prestador', 'IdentificacaoPrestador')
    toma = bloco(inf, 'TomadorServico', 'Tomador')
    serv = bloco(inf, 'Servico')
    val = bloco(serv if serv is not None else inf, 'Valores')
    val = inf if val is None else val
    ret = achar(inf, 'IssRetido')
    n = {
        'arquivo': os.path.basename(arq), 'layout': 'ABRASF/municipal',
        'numero': achar(inf, 'Numero'), 'chave': achar(inf, 'CodigoVerificacao'),
        'serie_dps': achar(inf, 'IdentificacaoRps/Serie'), 'numero_dps': achar(inf, 'IdentificacaoRps/Numero'),
        'data_emissao': achar(inf, 'DataEmissao'), 'competencia': achar(inf, 'Competencia'),
        'situacao': '',
        'prestador_cnpj': achar(prest, 'Cnpj', 'Cpf') if prest is not None else '',
        'prestador_nome': achar(prest, 'RazaoSocial', 'NomeFantasia') if prest is not None else '',
        'prestador_regime_sn': {'1': 'ME/EPP Simples', '2': 'Não optante'}.get(achar(inf, 'OptanteSimplesNacional'), achar(inf, 'OptanteSimplesNacional')),
        'prestador_reg_ap_sn': achar(inf, 'RegimeEspecialTributacao'),
        'tomador_doc': achar(toma, 'Cnpj', 'Cpf') if toma is not None else '',
        'tomador_nome': achar(toma, 'RazaoSocial') if toma is not None else '',
        'tomador_municipio': achar(toma, 'CodigoMunicipio') if toma is not None else '',
        'municipio_prestacao': achar(serv, 'CodigoMunicipio') if serv is not None else '',
        'municipio_incidencia': achar(serv, 'MunicipioIncidencia') if serv is not None else '',
        'item_lc116': achar(serv, 'ItemListaServico') if serv is not None else '',
        'trib_municipal': achar(serv, 'CodigoTributacaoMunicipio') if serv is not None else '',
        'atividade': achar(serv, 'CodigoCnae') if serv is not None else '',
        'nbs': achar(serv, 'CodigoNbs') if serv is not None else '',
        'descricao': achar(serv, 'Discriminacao') if serv is not None else '',
        'info_complementar': achar(inf, 'OutrasInformacoes', 'InformacoesComplementares'),
        'valor_servico': num(achar(val, 'ValorServicos')),
        'desconto_incond': num(achar(val, 'DescontoIncondicionado')),
        'deducoes': num(achar(val, 'ValorDeducoes')),
        'base_iss': num(achar(inf, 'BaseCalculo')),
        'aliquota_iss': num(achar(inf, 'Aliquota')),
        'valor_iss': num(achar(inf, 'ValorIss')),
        'trib_issqn': achar(inf, 'ExigibilidadeISS', 'NaturezaOperacao'),
        'iss_retido': {'1': 'Sim', '2': 'Não'}.get(ret, ret),
        'irrf': num(achar(val, 'ValorIr')), 'csll': num(achar(val, 'ValorCsll')),
        'pis': num(achar(val, 'ValorPis')), 'cofins': num(achar(val, 'ValorCofins')),
        'pis_cofins_retido': '', 'inss': num(achar(val, 'ValorInss')),
        'valor_liquido': num(achar(inf, 'ValorLiquidoNfse')),
        'ibs_cbs': '', 'substituida': achar(inf, 'NfseSubstituida'),
    }
    # Algumas prefeituras mandam a alíquota como fração (0.02) em vez de percentual (2)
    if n['aliquota_iss'] is not None and 0 < n['aliquota_iss'] < 0.3:
        n['aliquota_iss'] = round(n['aliquota_iss'] * 100, 4)
    return n


def ler(arq):
    raiz = ET.parse(arq).getroot()
    notas = []
    nac = [x for x in raiz.iter() if ln(x.tag) == 'infNFSe']
    for inf in nac:
        notas.append(nota_nacional(inf, arq))
    if not nac:
        for comp in [x for x in raiz.iter() if ln(x.tag) in ('CompNfse', 'ComplNfse')] or [raiz]:
            inf = bloco(comp, 'InfNfse')
            if inf is None:
                continue
            n = nota_abrasf(inf, arq)
            if bloco(comp, 'NfseCancelamento') is not None:
                n['situacao'] = 'Cancelada'
            notas.append(n)
    if not notas:
        print(f'AVISO: layout não reconhecido em {arq} - ler manualmente', file=sys.stderr)
    return notas


if __name__ == '__main__':
    args = sys.argv[1:]
    saida = None
    if '--saida' in args:
        i = args.index('--saida'); saida = args[i + 1]; del args[i:i + 2]
    arqs = []
    for a in args:
        if os.path.isdir(a):
            for r, _, fs in os.walk(a):
                arqs += [os.path.join(r, f) for f in fs if f.lower().endswith('.xml')]
        else:
            arqs.append(a)
    notas = []
    for a in sorted(arqs):
        try:
            notas += ler(a)
        except ET.ParseError as e:
            print(f'ERRO lendo {a}: {e}', file=sys.stderr)
    out = json.dumps(notas, ensure_ascii=False, indent=1)
    if saida:
        open(saida, 'w', encoding='utf-8').write(out); print(f'{len(notas)} nota(s) -> {saida}')
    else:
        print(out)
