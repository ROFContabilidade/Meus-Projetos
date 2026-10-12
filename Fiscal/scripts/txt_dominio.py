"""TXT de importação no Domínio, no leiaute do SPED Fiscal (EFD ICMS/IPI), com TODAS as notas do mês:
NF-e de entrada (já classificadas), devoluções/retornos emitidos pela empresa, NF-e de saída,
CT-e com a empresa tomadora, NFS-e tomadas e numerações inutilizadas.

Segue o modelo que o Domínio aceita (EFD exportado por ERP, ex. Ectas 08/2026):
- COD_PART = CNPJ/CPF do participante; série sem zeros à esquerda; contadores com 9 dígitos;
- NFS-e tomada = C100 modelo 01, CFOP 1933/2933, CST 090, sem chave;
- C170 só nas notas de terceiros (NF-e de fornecedor e NFS-e), com COD_NAT = código do acumulador
  (0400 com o nome do acumulador) e COD_CTA = conta contábil reduzida;
- notas próprias (saídas e devoluções) só com C100 + C190: o acumulador sai da configuração
  CFOP -> acumulador da importação no Domínio;
- cancelada: C100/D100 com COD_SIT 02 só com série, número e chave; inutilizada: COD_SIT 05.
"""
import calendar
import glob
import hashlib
import os
import re
import xml.etree.ElementTree as ET
from collections import Counter, OrderedDict, defaultdict
from decimal import Decimal

import pandas as pd

Z = Decimal('0')
FIN_TIPO = {'REVENDA': '00', 'INSUMO': '01', 'EMBALAGEM': '02', 'FERRAMENTA': '10', 'USO_CONSUMO': '07',
            'ATIVO': '08'}


def v(x, casas=2):
    x = Decimal(str(x or 0))
    return f'{x:.{casas}f}'.replace('.', ',')


def dt(d):
    d = str(d or '')
    if re.match(r'\d{4}-\d\d-\d\d', d):
        return d[8:10] + d[5:7] + d[:4]
    if re.match(r'\d\d/\d\d/\d{4}', d):
        return d[:2] + d[3:5] + d[6:10]
    return ''


def linha(*campos):
    return '|' + '|'.join('' if c is None else str(c).replace('|', '/').replace('\n', ' ').strip()
                          for c in campos) + '|'


def conta(txt):
    m = re.match(r'\s*(\d+)', str(txt or ''))
    return m.group(1) if m else ''


def _sem_ns(root):
    for el in root.iter():
        if '}' in el.tag:
            el.tag = el.tag.split('}', 1)[1]
    return root


def _end(el):
    g = lambda p: (el.findtext(p) or '').strip() if el is not None else ''
    return dict(end=g('xLgr'), num=g('nro'), compl=g('xCpl'), bairro=g('xBairro'), mun=g('cMun'), pais=g('cPais'))


class Participantes:
    def __init__(self):
        self.p = OrderedDict()

    def add(self, doc, nome, ie='', end=None):
        doc = re.sub(r'\D', '', str(doc or ''))
        end = end or {}
        cod = doc or ('EXT' + re.sub(r'\W', '', str(nome))[:20].upper())
        if cod not in self.p:
            pais = end.get('pais') or '1058'
            self.p[cod] = linha('0150', cod, str(nome)[:100], pais.zfill(5),
                                doc if len(doc) == 14 else '', doc if len(doc) == 11 else '',
                                re.sub(r'\D', '', ie or '') if ie and ie.upper() != 'ISENTO' else '',
                                end.get('mun', '') if pais in ('1058', '01058') else '', '',
                                (end.get('end') or 'NAO INFORMADO')[:60], end.get('num', '')[:10],
                                end.get('compl', '')[:60], end.get('bairro', '')[:60])
        return cod


def _xml(n):
    try:
        return _sem_ns(ET.parse(n['arquivo']).getroot())
    except Exception:
        return None


def _novo():
    return defaultdict(lambda: dict(opr=Z, bc=Z, icms=Z, bcst=Z, st=Z, ipi=Z))


def _cst(it):
    """CST do ICMS como o Domínio aceita: CSOSN (Simples) vai sem a origem; CST normal = origem + CST."""
    c = it['CST_ICMS'] or '90'
    return c if len(c) == 3 else (it['orig'] or '0') + c


def cod_produto(prefixo, *partes):
    """Código de produto com até 10 caracteres (o Domínio corta em 14), estável de um mês para o outro."""
    h = int(hashlib.sha1('|'.join(str(p) for p in partes).encode()).hexdigest(), 16)
    b36 = ''
    while h and len(b36) < 9:
        h, r = divmod(h, 36)
        b36 = '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ'[r] + b36
    return prefixo + b36


def _pis_cofins(it, do_xml):
    """Campos de PIS e COFINS do C170. Notas próprias: CST e valores do XML (o Domínio recusa 98 na saída);
    notas de terceiros: 98 zerado, como no modelo (empresa do Lucro Presumido não credita)."""
    out = []
    for cst, val, aliq in ((it['CST_PIS'], it['vPIS'], it['pPIS']), (it['CST_COFINS'], it['vCOFINS'], it['pCOFINS'])):
        if do_xml and cst:
            bc = (val * 100 / aliq).quantize(Decimal('0.01')) if aliq else Z
            out += [cst, v(bc), v(aliq, 4), '', '', v(val)]
        else:
            out += ['98', v(0), v(0, 4), '', '', v(0)]
    return out


def _rateio(total, pesos):
    """Rateia `total` pelos pesos (2 casas); a sobra de arredondamento vai para o último item."""
    soma = sum(pesos, Z)
    if not total or not soma:
        return [Z] * len(pesos)
    partes = [(total * p / soma).quantize(Decimal('0.01')) for p in pesos]
    partes[-1] += total - sum(partes, Z)
    return partes


def gerar(res, saida, cabecalho, nfse_planilha=None, excluir=()):
    R = res['regras']
    K = R.cnpj
    comp = res['competencia']
    ano, mes = int(comp[:4]), int(comp[5:7])
    ini, fim = f'01{mes:02d}{ano}', f'{calendar.monthrange(ano, mes)[1]:02d}{mes:02d}{ano}'
    notas = res['notas']
    base = open(cabecalho, encoding='latin-1').read().splitlines()
    pega = {ln.split('|')[1]: ln for ln in base if ln.startswith('|') and ln.split('|')[1] in ('0000', '0002', '0005', '0100')}
    uf_cod = pega['0000'].split('|')[11][:2]          # COD_MUN da empresa -> código da UF
    part = Participantes()
    unid, prod, nat = OrderedDict(), OrderedDict(), OrderedDict()
    C, D = [], []
    conf = []           # resumo para a planilha de confronto

    def ac_nome(a):
        return (R.ac_nome(a) or str(R.r.get('acumuladores', {}).get(str(a), '')) or f'ACUMULADOR {a}').split(' (')[0][:60]

    def un(u):
        u = (str(u or 'UN').strip() or 'UN')[:6]
        unid.setdefault(u, linha('0190', u, u))
        return u

    def part_nfe(n, papel):
        x = _xml(n)
        el = x.find(f'.//{papel}') if x is not None else None
        e = _end(el.find('enderEmit' if papel == 'emit' else 'enderDest')) if el is not None else {}
        doc = n['emit_cnpj'] if papel == 'emit' else n['dest_cnpj']
        nome = n['emit_nome'] if papel == 'emit' else n['dest_nome']
        ie = (el.findtext('IE') or '') if el is not None else ''
        if not doc and el is not None:
            doc = el.findtext('idEstrangeiro') or ''
            e['pais'] = e.get('pais') or ''
        return part.add(doc, re.sub(r'\s*\(\d+\)$', '', nome), ie, e)

    canc_fora = R.r.get('txt_importacao', {}).get('canceladas', 'no_txt') == 'lancar_manual'
    manual = []

    def nfe(n, oper, emit, cod_p, info, cancel, rotulo, nome):
        if str(n['numero']).lstrip('0') in excluir:      # vai pelo XML à parte, fora do TXT
            return
        if cancel and canc_fora:
            manual.append((rotulo, n['numero'], nome, n['chave'], dt(n['dt_emissao']),
                           ', '.join(sorted({info(it)['cfop'] for it in n['itens']})),
                           ', '.join(sorted({info(it)['ac'] for it in n['itens']} - {''}))))
            return
        """C100 + C170 + C190 de uma NF-e. info(it) devolve a classificação do item.
        O valor de cada linha do C190 é montado como o Domínio confere: item - desconto + rateio de frete,
        seguro e outras pelo valor do item + IPI + ST."""
        ser, num = str(int(n['serie'])), str(int(n['numero']))
        d1, d2 = dt(n['dt_emissao']), dt(n['dt_saida_ent'] or n['dt_emissao'])
        linhas_it, grupos = [], _novo()
        infos = [info(it) for it in n['itens']]
        vl_item = [Z if cancel else it['vProd'] + (it['vIPI'] if f['ipi_no_custo'] else Z)
                   for it, f in zip(n['itens'], infos)]
        desc = [Z if cancel else it['vDesc'] for it in n['itens']]
        tot = dict(merc=sum(vl_item, Z), desc=sum(desc, Z), frt=Z if cancel else n['t_vFrete'],
                   seg=Z if cancel else n['t_vSeg'], out=Z if cancel else n['t_vOutro'],
                   ipi=sum((f['ipi'] for f in infos), Z) if not cancel else Z,
                   st=Z if cancel else sum((it['vICMSST'] for it in n['itens']), Z))
        vl_doc = Z if cancel else n['t_vNF']
        resid = vl_doc - (tot['merc'] - tot['desc'] + tot['frt'] + tot['seg'] + tot['out'] + tot['ipi'] + tot['st'])
        if resid and abs(resid) <= Decimal('1.00'):        # arredondamento do emissor -> outras despesas
            tot['out'] += resid
        fr, sg, ot = (_rateio(tot[k], vl_item) for k in ('frt', 'seg', 'out'))
        tot_bc = tot_icms = Z
        for k, (it, f) in enumerate(zip(n['itens'], infos)):
            u = un(it['uCom'])
            prod.setdefault(f['cod'], linha('0200', f['cod'], it['xProd'][:120], '', '', u, f['tipo'], it['NCM'], '',
                                            it['NCM'][:2], '', '', ''))
            if f['ac']:
                nat.setdefault(f['ac'], linha('0400', f['ac'], ac_nome(f['ac'])))
            bc, aliq, icms = (Z, Z, Z) if cancel else (f['bc'], f['aliq'], f['icms'])
            ipi = Z if cancel else f['ipi']
            st = Z if cancel else it['vICMSST']
            com_ipi = bool(ipi) or f['ipi_cst'] in ('50', '00')
            linhas_it.append(linha(
                'C170', it['nItem'], f['cod'], '', v(it['qCom'], 5), u, v(vl_item[k]), v(desc[k]), '0', f['cst'],
                f['cfop'], f['ac'], v(bc), v(aliq), v(icms), v(0 if cancel else it['vBCST']),
                v(0 if cancel else it['pICMSST']), v(st), '0',
                f['ipi_cst'] if com_ipi else '', '', v(f['ipi_bc']) if com_ipi and not cancel else '',
                v(f['ipi_aliq']) if com_ipi and not cancel else '', v(ipi) if com_ipi else '',
                *_pis_cofins(it, f['pis_xml'] and not cancel), f['conta'], v(0)))
            g = grupos[(f['cst'], f['cfop'], aliq if icms else Z)]
            g['opr'] += vl_item[k] - desc[k] + fr[k] + sg[k] + ot[k] + ipi + st
            g['bc'] += bc
            g['icms'] += icms
            g['bcst'] += Z if cancel else it['vBCST']
            g['st'] += st
            g['ipi'] += ipi
            tot_bc += bc
            tot_icms += icms
        C.append(linha('C100', oper, emit, cod_p, '55', '02' if cancel else '00', ser, num, n['chave'], d1, d2,
                       v(vl_doc), '1' if oper == '1' or emit == '1' else '0', v(tot['desc']), v(0), v(tot['merc']),
                       n['modFrete'] or '9', v(tot['frt']), v(tot['seg']), v(tot['out']), v(tot_bc), v(tot_icms),
                       v(0 if cancel else n['t_vBCST']), v(tot['st']), v(tot['ipi']),
                       v(0 if cancel or emit == '1' else n['t_vPIS']), v(0 if cancel or emit == '1' else n['t_vCOFINS']),
                       v(0), v(0)))
        C.extend(linhas_it)
        for (cst, cfop, aliq), g in sorted(grupos.items()):
            C.append(linha('C190', cst, cfop, v(aliq), v(g['opr']), v(g['bc']), v(g['icms']), v(g['bcst']),
                           v(g['st']), v(0), v(g['ipi']), ''))
        acs = sorted({f['ac'] for f in infos if f['ac']})
        conf.append((rotulo, n['numero'], nome, ('CANCELADA (COD_SIT 02) - ' if cancel else '') + ', '.join(acs),
                     vl_doc, tot_icms, '' if not resid or abs(resid) > Decimal('1.00') else
                     f'arredondamento {v(resid)} em outras despesas'))

    # ------------------------------------------------ NF-e de fornecedores
    itens = defaultdict(list)
    for it in res['itens']:
        itens[(it['Nota'], it['CNPJ'])].append(it)
    for nr in res['notas_terc']:
        n = notas.get(nr['Chave'])
        if not n:
            continue
        cls = {str(i['Item']): i for i in itens[(n['numero'], n['emit_cnpj'])]}

        def info_terc(it, n=n, cls=cls):
            c = cls.get(str(it['nItem']), {})
            cred = Decimal(str(c.get('Crédito ICMS sugerido') or 0))
            cred_ipi = Decimal(str(c.get('Crédito IPI sugerido') or 0))
            if cred and it['vCredICMSSN'] and not it['vICMS']:          # Simples: crédito pelo pCredSN
                bc, aliq = it['vProd'], it['pCredSN']
            elif cred:
                bc, aliq = it['vBC_ICMS'], it['pICMS']
            else:
                bc, aliq = Z, Z
            return dict(cfop=str(c.get('CFOP sugerido') or ''), ac=str(c.get('Acum. sugerido') or ''),
                        cst=_cst(it), bc=bc, aliq=aliq, icms=cred,
                        ipi=cred_ipi, ipi_cst='00' if cred_ipi else '', ipi_bc=it['vBC_IPI'], ipi_aliq=it['pIPI'],
                        ipi_no_custo=bool(it['vIPI']) and not cred_ipi, pis_xml=False,   # IPI sem crédito -> custo
                        conta=conta(c.get('Conta contábil sugerida')),
                        tipo=FIN_TIPO.get(str(c.get('Finalidade') or ''), '99'),
                        cod=cod_produto('F', n['emit_cnpj'], it['cProd'], it['uCom']))
        nfe(n, '0', '1', part_nfe(n, 'emit'), info_terc, 'CANCELADA' in nr['Status'], 'NF-e fornecedor', n['emit_nome'])

    # ------------------------------------------------ notas próprias: devoluções (entrada) e saídas
    def info_propria(ac_cfop):
        def f(it):
            ipi_cst = it['CST_IPI'] or ('50' if it['vIPI'] else '')
            return dict(cfop=it['CFOP'], ac=ac_cfop.get(it['CFOP'], ''), cst=_cst(it),
                        bc=it['vBC_ICMS'] if it['vICMS'] else Z, aliq=it['pICMS'] if it['vICMS'] else Z,
                        icms=it['vICMS'], ipi=it['vIPI'], ipi_cst=ipi_cst if it['vIPI'] else '',
                        ipi_bc=it['vBC_IPI'], ipi_aliq=it['pIPI'], ipi_no_custo=False, conta='', pis_xml=True,
                        tipo='00' if it['CFOP'][1:] in ('102', '202', '411') else '04',
                        cod=cod_produto('K', it['cProd'], it['uCom']))
        return f

    for d in res['devol']:
        n = notas.get(d['Chave'])
        if n:
            ac = {c: str(R.r['devolucoes_proprias'].get(c, {}).get('ac') or d.get('Acum. esperado') or '')
                  for c in {it['CFOP'] for it in n['itens']}}
            nfe(n, '0', '0', part_nfe(n, 'dest'), info_propria(ac), d['Status'].startswith('CANCELADA'),
                'Devolução/retorno (própria)', n['dest_nome'])
    for s in res['saidas']:
        n = notas.get(s['Chave'])
        if n:
            ac = dict(p.split('→') for p in str(s.get('Acum. sugerido', '')).split(', ') if '→' in p)
            if s['Status'].startswith('CANCELADA') and not ac:
                ac = {c: str((R.r.get('saidas', {}).get(c) or {}).get('ac', '') if isinstance(R.r.get('saidas', {}).get(c), dict)
                             else R.r.get('saidas', {}).get(c, '')) for c in {it['CFOP'] for it in n['itens']}}
            nfe(n, '1', '0', part_nfe(n, 'dest'), info_propria(ac), s['Status'].startswith('CANCELADA'), 'Saída',
                n['dest_nome'])

    # ------------------------------------------------ inutilizadas
    for l in res['lacunas']:
        if not l['Situação'].startswith(('Inutilizar', 'Inutilizada')):
            continue
        m = re.search(r'(\d{4}-\d\d-\d\d|\d\d/\d\d/\d{4})', l['Situação'])
        f = ['C100', '1', '0', '', '55', '05', str(int(l['Série'])), str(int(l['Número'])), '', dt(m.group(1)) if m else '']
        C.append(linha(*(f + [''] * 19)))
        conf.append(('Inutilizada', str(l['Número']), '', 'COD_SIT 05', Z, Z, ''))

    # ------------------------------------------------ NFS-e tomadas: C100 modelo 01, CFOP 1933/2933
    if nfse_planilha:
        src = pd.read_excel(nfse_planilha, dtype=str)
        # a chave vem como número no Excel: os 7 primeiros dígitos (município do emissor) sobrevivem
        src['Chave NFS-e'] = src['Chave NFS-e'].map(lambda c: f'{Decimal(c):f}' if c and 'e' in str(c).lower() else str(c))
        src['num'] = src['Número NFS-e'].str.replace(r'\.0$', '', regex=True)
        src['doc'] = src['CNPJ/CPF Prestador'].str.replace(r'\.0$', '', regex=True).str.replace(r'\D', '', regex=True)
        for x in res['nfse']:
            if x['Status'] not in ('A LANÇAR', 'CONFERIR'):
                continue
            num = str(x['Número']).replace('.0', '')
            doc = re.sub(r'\D', '', str(x['CNPJ']))
            r = src[(src['num'] == num) & (src['doc'].str.zfill(len(doc)) == doc)]
            ch = str(r['Chave NFS-e'].iloc[0]) if len(r) else ''
            mun = ch[:7] if ch[:7].isdigit() else ''
            cod_p = part.add(doc, x['Prestador'], '', {'mun': mun})
            cfop = '1933' if not mun or mun[:2] == uf_cod else '2933'
            item = str(x.get('Serviço (LC 116)') or '')
            cod_item = 'S' + item.replace('.', '')
            u = un('UN')
            prod.setdefault(cod_item, linha('0200', cod_item, f'SERVICO {item} {x.get("Natureza do serviço", "")}'[:120],
                                            '', '', u, '09', '', '', '', item, '', ''))
            ac = str(x.get('Acum. sugerido') or '')
            if ac:
                nat.setdefault(ac, linha('0400', ac, ac_nome(ac)))
            val = Decimal(str(x['Valor']))
            data = dt(x.get('Data emissão'))
            C.append(linha('C100', '0', '1', cod_p, '01', '00', '1', num, '', data, data, v(val), '0', '', '',
                           v(val), '1', '', '', '', '0', '0', '0', '0', '', v(0), v(0), v(0), v(0)))
            C.append(linha('C170', '001', cod_item, '', v(1, 5), u, v(val), '', '0', '090', cfop, ac, '', v(0), '',
                           v(0), v(0), v(0), '0', '49', '', '', v(0), '', '98', '', v(0, 4), '', '', '', '98', '',
                           v(0, 4), '', '', '', conta(x.get('Conta contábil sugerida')), ''))
            C.append(linha('C190', '090', cfop, v(0), v(val), '0', '0', '0', '0', '0', '0', ''))
            ret = ', '.join(k for k in ('IRRF', 'CSRF', 'INSS', 'ISS') if x.get(f'{k} retido'))
            conf.append(('NFS-e tomada', num, x['Prestador'], ac, val, Z, ret))

    # ------------------------------------------------ CT-e (D100/D190)
    xml_cte = {}
    if res.get('xml_dir'):
        for f in glob.glob(os.path.join(res['xml_dir'], '**', '*.xml'), recursive=True):
            m = re.search(r'(\d{44})', os.path.basename(f))
            if m and m.group(1)[20:22] == '57' and 'canc' not in f.lower():
                xml_cte.setdefault(m.group(1), f)
    for c in res.get('cte', []):
        st = c['Status']
        if 'NÃO LANÇAR' in st.upper() or 'não lançar' in st:
            continue
        ch = c['Chave']
        canc = 'CANCEL' in st.upper()
        if canc and canc_fora:
            manual.append(('CT-e', str(c['CT-e']), c['Transportador'], ch, dt(c['Data']),
                           str(c['CFOP de entrada sugerido']), str(c.get('Acum. sugerido') or '')))
            continue
        x = None
        if ch in xml_cte:
            try:
                x = _sem_ns(ET.parse(xml_cte[ch]).getroot())
            except Exception:
                x = None
        em = x.find('.//emit') if x is not None else None
        cod_p = part.add(c['CNPJ'], c['Transportador'], (em.findtext('IE') or '') if em is not None else '',
                         _end(em.find('enderEmit')) if em is not None else {})
        ac = str(c.get('Acum. sugerido') or '')
        cfop = str(c['CFOP de entrada sugerido'])
        cred = Z if canc else Decimal(str(c.get('Crédito ICMS sugerido') or 0))
        val = Z if canc else Decimal(str(c['Valor']))
        cst = ('0' + str(c.get('CST') or '90'))[-3:] if cred else '090'
        aliq = (x.findtext('.//pICMS') or '0') if (x is not None and cred) else '0'
        g = (lambda t: (x.findtext(t) or '') if x is not None else '')
        D.append(linha('D100', '0', '1', cod_p, '57', '02' if canc else '00', str(int(ch[22:25])), '', str(int(ch[25:34])), ch,
                       dt(c['Data']), dt(c['Data']), '0', '', v(val), v(0), '1', v(val),
                       v(c['BC ICMS'] if cred else 0), v(cred), v(0 if cred else val), '', '', g('.//cMunIni'),
                       g('.//cMunFim')))
        D.append(linha('D190', cst, cfop, v(Decimal(aliq)), v(val), v(c['BC ICMS'] if cred else 0), v(cred), v(0), ''))
        conf.append(('CT-e', str(c['CT-e']), c['Transportador'], ('CANCELADO (COD_SIT 02) - ' if canc else '') + ac,
                     val, cred, ''))

    # ------------------------------------------------ montagem
    r0 = pega['0000'].split('|')
    r0[4], r0[5] = ini, fim
    b0 = ['|'.join(r0), '|0001|0|'] + [pega[k] for k in ('0002', '0005', '0100') if k in pega]
    b0 += list(part.p.values()) + list(unid.values()) + list(prod.values()) + list(nat.values())
    b0.append(linha('0990', f'{len(b0) + 1:09d}'))
    bc = ['|C001|0|'] + C
    bc.append(linha('C990', f'{len(bc) + 1:09d}'))
    bd = ['|D001|0|' if D else '|D001|1|'] + D
    bd.append(linha('D990', f'{len(bd) + 1:09d}'))
    resto = ['|B001|1|', '|B990|000000002|']
    be = ['|E001|0|', linha('E100', ini, fim), '|E990|000000003|']
    outros = []
    for b in ('G', 'H', 'K'):
        outros += [f'|{b}001|1|', f'|{b}990|000000002|']
    b1 = ['|1001|0|', '|1010|N|N|N|N|N|N|N|N|N|N|N|N|N|', '|1990|000000003|']
    linhas = b0 + resto + bc + bd + be + outros + b1
    cont = Counter(ln.split('|')[1] for ln in linhas)
    b9 = ['|9001|0|'] + [linha('9900', reg, f'{q:09d}') for reg, q in cont.items()]
    b9 += [linha('9900', '9001', '000000001'), '|9900|9900|PLACEHOLDER|', linha('9900', '9990', '000000001'),
           linha('9900', '9999', '000000001')]
    n9900 = sum(1 for x in b9 if x.startswith('|9900|'))
    b9 = [x.replace('PLACEHOLDER', f'{n9900:09d}') for x in b9]
    b9.append(linha('9990', f'{len(b9) + 2:09d}'))
    linhas += b9
    linhas.append(linha('9999', f'{len(linhas) + 1:09d}'))
    with open(saida, 'w', encoding='latin-1', errors='replace', newline='\r\n') as f:
        f.write('\n'.join(linhas) + '\n')
    res['txt_manual'] = manual
    return linhas, conf


def planilha(conf, res, saida):
    """Confronto do TXT: uma linha por documento e a tabela CFOP -> acumulador das notas próprias
    (saídas e devoluções não levam C170, então o Domínio aplica o acumulador pela configuração de CFOP)."""
    from openpyxl import Workbook
    from openpyxl.styles import Font, PatternFill
    from openpyxl.utils import get_column_letter
    AZ = PatternFill('solid', fgColor='1F3864')
    VM = PatternFill('solid', fgColor='FFC7CE')
    CZ = PatternFill('solid', fgColor='D9D9D9')
    wb = Workbook()
    ws = wb.active
    ws.title = 'Resumo do TXT'
    grupos = Counter(c[0] for c in conf)
    ws.append(['Documento', 'Quantidade', 'Valor', 'Crédito ICMS'])
    for g in grupos:
        ls = [c for c in conf if c[0] == g]
        ws.append([g, len(ls), float(sum((Decimal(str(c[4])) for c in ls), Z)),
                   float(sum((Decimal(str(c[5])) for c in ls), Z))])
    ws.append(['TOTAL', len(conf), float(sum((Decimal(str(c[4])) for c in conf), Z)),
               float(sum((Decimal(str(c[5])) for c in conf), Z))])
    ws2 = wb.create_sheet('Documentos no TXT')
    ws2.append(['Documento', 'Número', 'Participante', 'Acumulador / CFOP / situação', 'Valor', 'Crédito ICMS',
                'Retenção'])
    for c in conf:
        ws2.append([c[0], c[1], c[2], c[3], float(c[4]), float(c[5]), c[6]])
        if 'CANCEL' in str(c[3]):
            for cel in ws2[ws2.max_row]:
                cel.fill = VM
        elif c[0] == 'Inutilizada':
            for cel in ws2[ws2.max_row]:
                cel.fill = CZ
        elif c[6]:
            for cel in ws2[ws2.max_row]:
                cel.font = Font(bold=True, color='9C0006')
    if res.get('txt_manual'):
        wsm = wb.create_sheet('Canceladas - lançar à mão')
        wsm.append(['Documento', 'Número', 'Participante', 'Chave', 'Data', 'CFOP', 'Acumulador'])
        for m in res['txt_manual']:
            wsm.append(list(m[:4]) + [f'{m[4][:2]}/{m[4][2:4]}/{m[4][4:]}'] + list(m[5:]))
            for cel in wsm[wsm.max_row]:
                cel.fill = VM
    ws3 = wb.create_sheet('CFOP x acumulador (próprias)')
    ws3.append(['Tipo', 'CFOP', 'Acumulador', 'Nome', 'Notas'])
    R = res['regras']
    cont = Counter()
    for s in res['saidas']:
        if not s['Status'].startswith('CANCELADA'):
            for p in str(s.get('Acum. sugerido', '')).split(', '):
                if '→' in p:
                    cont[('Saída',) + tuple(p.split('→'))] += 1
    for d in res['devol']:
        if not d['Status'].startswith('CANCELADA'):
            cont[('Devolução/retorno', str(d['CFOP XML']), str(d.get('Acum. esperado', '')))] += 1
    for (t, cf, ac), q in sorted(cont.items()):
        ws3.append([t, cf, ac, (R.ac_nome(ac) or '').split(' (')[0], q])
    for w in wb.worksheets:
        for cel in w[1]:
            cel.font = Font(bold=True, color='FFFFFF')
            cel.fill = AZ
        for j in range(1, w.max_column + 1):
            w.column_dimensions[get_column_letter(j)].width = 16 if j != 3 else 42
        for row in w.iter_rows(min_row=2):
            for cel in row:
                if isinstance(cel.value, float):
                    cel.number_format = '#,##0.00'
    wb.save(saida)
