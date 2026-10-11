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


def _c190(grupos, vl_doc=None):
    if vl_doc is not None and grupos:
        dif = Decimal(str(vl_doc)) - sum((g['opr'] for g in grupos.values()), Z)
        if dif and abs(dif) <= Decimal('0.10'):           # arredondamento do emissor
            max(grupos.values(), key=lambda g: g['opr'])['opr'] += dif
    out = []
    for (cst, cfop, aliq), g in sorted(grupos.items()):
        out.append(linha('C190', cst, cfop, v(aliq), v(g['opr']), v(g['bc']), v(g['icms']), v(g['bcst']),
                         v(g['st']), v(0), v(g['ipi']), ''))
    return out


def _novo():
    return defaultdict(lambda: dict(opr=Z, bc=Z, icms=Z, bcst=Z, st=Z, ipi=Z))


def _vl_item(it):
    return (it['vProd'] - it['vDesc'] + it['vFrete'] + it['vSeg'] + it['vOutro'] + it['vIPI'] + it['vICMSST'])


def c100_cancelado(oper, emit, mod, serie, num, chave):
    f = ['C100', oper, emit, '', mod, '02', str(int(serie)) if str(serie).isdigit() else serie, str(int(num)), chave]
    return linha(*(f + [''] * 20))


def gerar(res, saida, cabecalho, nfse_planilha=None):
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

    # ------------------------------------------------ NF-e de fornecedores (C100 0|1 + C170)
    itens = defaultdict(list)
    for it in res['itens']:
        itens[(it['Nota'], it['CNPJ'])].append(it)
    for nr in res['notas_terc']:
        n = notas.get(nr['Chave'])
        if not n:
            continue
        if 'CANCELADA' in nr['Status']:
            C.append(c100_cancelado('0', '1', '55', n['serie'], n['numero'], n['chave']))
            conf.append(('NF-e fornecedor', n['numero'], n['emit_nome'], 'CANCELADA (COD_SIT 02)', Z, Z, ''))
            continue
        cls = {str(i['Item']): i for i in itens[(n['numero'], n['emit_cnpj'])]}
        cod_p = part_nfe(n, 'emit')
        filhos, grupos = [], _novo()
        tot_bc = tot_icms = tot_ipi = Z
        acs = set()
        for it in n['itens']:
            c = cls.get(str(it['nItem']), {})
            cfop = str(c.get('CFOP sugerido') or '')
            ac = str(c.get('Acum. sugerido') or '')
            acs.add(ac)
            cred = Decimal(str(c.get('Crédito ICMS sugerido') or 0))
            cred_ipi = Decimal(str(c.get('Crédito IPI sugerido') or 0))
            if cred and it['vCredICMSSN'] and not it['vICMS']:          # Simples: crédito pelo pCredSN
                bc, aliq = it['vProd'], it['pCredSN']
            elif cred:
                bc, aliq = it['vBC_ICMS'], it['pICMS']
            else:
                bc, aliq = Z, it['pICMS']
            cst = (it['orig'] or '0') + (it['CST_ICMS'] or '90')
            cod_item = f'{n["emit_cnpj"][:8]}-{it["cProd"]}'[:60]
            u = un(it['uCom'])
            fin = str(c.get('Finalidade') or '')
            prod.setdefault(cod_item, linha('0200', cod_item, it['xProd'][:120], '', '', u,
                                            FIN_TIPO.get(fin, '99'), it['NCM'], '', it['NCM'][:2], '', '', it['CEST']))
            if ac:
                nat.setdefault(ac, linha('0400', ac, ac_nome(ac)))
            filhos.append(linha('C170', it['nItem'], cod_item, '', v(it['qCom'], 5), u, v(it['vProd']), v(it['vDesc']),
                                '0', cst, cfop, ac, v(bc), v(aliq), v(cred), v(it['vBCST']), v(it['pICMSST']),
                                v(it['vICMSST']), '0', '00' if cred_ipi else '49', '', v(it['vBC_IPI'] if cred_ipi else 0),
                                v(it['pIPI'] if cred_ipi else 0), v(cred_ipi), '98', v(0), v(0, 4), '', '', v(0),
                                '98', v(0), v(0, 4), '', '', v(0), conta(c.get('Conta contábil sugerida')), v(0)))
            g = grupos[(cst, cfop, aliq if cred else Z)]
            g['opr'] += _vl_item(it)
            g['bc'] += bc
            g['icms'] += cred
            g['bcst'] += it['vBCST']
            g['st'] += it['vICMSST']
            g['ipi'] += cred_ipi
            tot_bc += bc
            tot_icms += cred
            tot_ipi += cred_ipi
        C.append(linha('C100', '0', '1', cod_p, '55', '00', str(int(n['serie'])), str(int(n['numero'])), n['chave'],
                       dt(n['dt_emissao']), dt(n['dt_saida_ent'] or n['dt_emissao']), v(n['t_vNF']), '1',
                       v(n['t_vDesc']), v(0), v(n['t_vProd']), n['modFrete'] or '9', v(n['t_vFrete']), v(n['t_vSeg']),
                       v(n['t_vOutro']), v(tot_bc), v(tot_icms), v(n['t_vBCST']), v(n['t_vST']), v(tot_ipi),
                       v(0), v(0), v(0), v(0)))
        C += filhos + _c190(grupos, n['t_vNF'])
        conf.append(('NF-e fornecedor', n['numero'], n['emit_nome'], ', '.join(sorted(a for a in acs if a)),
                     n['t_vNF'], tot_icms, ''))

    # ------------------------------------------------ notas próprias: devoluções (entrada) e saídas
    def propria(n, oper, cancel, rotulo):
        if cancel:
            C.append(c100_cancelado(oper, '0', '55', n['serie'], n['numero'], n['chave']))
            conf.append((rotulo, n['numero'], n['dest_nome'], 'CANCELADA (COD_SIT 02)', Z, Z, ''))
            return
        cod_p = part_nfe(n, 'dest')
        grupos = _novo()
        for it in n['itens']:
            g = grupos[((it['orig'] or '0') + (it['CST_ICMS'] or '90'), it['CFOP'], it['pICMS'] if it['vICMS'] else Z)]
            g['opr'] += _vl_item(it)
            g['bc'] += it['vBC_ICMS'] if it['vICMS'] else Z
            g['icms'] += it['vICMS']
            g['bcst'] += it['vBCST']
            g['st'] += it['vICMSST']
            g['ipi'] += it['vIPI']
        C.append(linha('C100', oper, '0', cod_p, '55', '00', str(int(n['serie'])), str(int(n['numero'])), n['chave'],
                       dt(n['dt_emissao']), dt(n['dt_saida_ent'] or n['dt_emissao']), v(n['t_vNF']),
                       '1' if oper == '1' else '0', v(n['t_vDesc']), v(0), v(n['t_vProd']), n['modFrete'] or '9',
                       v(n['t_vFrete']), v(n['t_vSeg']), v(n['t_vOutro']), v(n['t_vBC']), v(n['t_vICMS']),
                       v(n['t_vBCST']), v(n['t_vST']), v(n['t_vIPI']), v(n['t_vPIS']), v(n['t_vCOFINS']), v(0), v(0)))
        C.extend(_c190(grupos, n['t_vNF']))
        cfops = sorted({it['CFOP'] for it in n['itens']})
        conf.append((rotulo, n['numero'], n['dest_nome'], ', '.join(cfops), n['t_vNF'], n['t_vICMS'], ''))

    for d in res['devol']:
        n = notas.get(d['Chave'])
        if n:
            propria(n, '0', d['Status'].startswith('CANCELADA'), 'Devolução/retorno (própria)')
    for s in res['saidas']:
        n = notas.get(s['Chave'])
        if n:
            propria(n, '1', s['Status'].startswith('CANCELADA'), 'Saída')

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
        if 'CANCEL' in st.upper():
            D.append(linha('D100', '0', '1', '', '57', '02', str(int(ch[22:25])), '', str(int(ch[25:34])), ch,
                           *([''] * 15)))
            conf.append(('CT-e', str(c['CT-e']), c['Transportador'], 'CANCELADO (COD_SIT 02)', Z, Z, ''))
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
        cred = Decimal(str(c.get('Crédito ICMS sugerido') or 0))
        val = Decimal(str(c['Valor']))
        cst = ('0' + str(c.get('CST') or '90'))[-3:] if cred else '090'
        aliq = (x.findtext('.//pICMS') or '0') if (x is not None and cred) else '0'
        g = (lambda t: (x.findtext(t) or '') if x is not None else '')
        D.append(linha('D100', '0', '1', cod_p, '57', '00', str(int(ch[22:25])), '', str(int(ch[25:34])), ch,
                       dt(c['Data']), dt(c['Data']), '0', '', v(val), v(0), '1', v(val),
                       v(c['BC ICMS'] if cred else 0), v(cred), v(0 if cred else val), '', '', g('.//cMunIni'),
                       g('.//cMunFim')))
        D.append(linha('D190', cst, cfop, v(Decimal(aliq)), v(val), v(c['BC ICMS'] if cred else 0), v(cred), v(0), ''))
        conf.append(('CT-e', str(c['CT-e']), c['Transportador'], ac, val, cred, ''))

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
