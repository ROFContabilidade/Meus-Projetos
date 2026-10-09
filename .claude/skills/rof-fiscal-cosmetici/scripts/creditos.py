"""Análise de crédito das entradas da COSMETICI (indústria de cosméticos, Lucro Presumido, PR).

Para cada item de NF-e de entrada decide:
  - a natureza (insumo/embalagem, uso e consumo, ativo, remessa de terceiro, financeiro, devolução);
  - o crédito de ICMS (fornecedor do regime normal: ICMS destacado; fornecedor do Simples Nacional:
    só o vCredICMSSN informado com CSOSN 101/201/900 - LC 123/2006 art. 23 §§ 1º e 2º);
  - o crédito de IPI (só insumo de fornecedor contribuinte que destacou IPI - RIPI art. 226, I);
  - pendências (Simples com pCredSN mas sem valor, CSOSN 101 com 0%, DIFAL de uso e consumo/ativo).
PIS/COFINS: Lucro Presumido é cumulativo (Lei 9.718/98) - não há crédito de entradas.
"""
import collections

from apuracao import vcontabil
from leitores import cfop_entrada

R = lambda x: round(x + 0.0, 2)

# --- natureza por CFOP do fornecedor -------------------------------------------------
CFOP_REMESSA = {  # mercadoria de terceiro / sem transferência de propriedade -> sem crédito
    '5901': 'Remessa para industrialização por encomenda (insumo do cliente)',
    '6901': 'Remessa para industrialização por encomenda (insumo do cliente)',
    '5924': 'Remessa para industrialização por conta e ordem do adquirente (insumo do cliente)',
    '6924': 'Remessa para industrialização por conta e ordem do adquirente (insumo do cliente)',
    '5923': 'Remessa por conta e ordem de terceiros em venda à ordem (a venda vem em outra nota)',
    '6923': 'Remessa por conta e ordem de terceiros em venda à ordem (a venda vem em outra nota)',
    '5915': 'Remessa para conserto', '6915': 'Remessa para conserto',
    '5912': 'Remessa para demonstração', '6912': 'Remessa para demonstração',
    '5908': 'Remessa em comodato', '6908': 'Remessa em comodato',
    '5902': 'Retorno de industrialização', '6902': 'Retorno de industrialização',
    '5925': 'Retorno de industrialização por conta e ordem', '6925': 'Retorno de industrialização por conta e ordem',
}
CFOP_OUTRAS = {'5949', '6949'}
CFOP_DEVOLUCAO_VENDA = {'5201', '5202', '5410', '5411', '6201', '6202', '6410', '6411'}
CFOP_BONIFICACAO = {'5910', '6910', '5911', '6911'}
CFOP_ATIVO_FORN = {'5551', '6551'}

# --- natureza por NCM (indústria de cosméticos) --------------------------------------
NCM_INSUMO = [  # matéria-prima, embalagem, rótulo
    ('13', 'Matéria-prima (extratos vegetais)'), ('15', 'Matéria-prima (óleos e gorduras)'),
    ('17', 'Matéria-prima (açúcares)'), ('2207', 'Matéria-prima (álcool etílico)'),
    ('2508', 'Matéria-prima (argila)'), ('2501', 'Matéria-prima (sal)'), ('2710', 'Matéria-prima (óleo mineral)'),
    ('2712', 'Matéria-prima (vaselina/parafina)'), ('28', 'Matéria-prima (químico inorgânico)'),
    ('29', 'Matéria-prima (químico orgânico)'), ('32', 'Matéria-prima (corantes/pigmentos)'),
    ('3301', 'Matéria-prima (óleos essenciais)'), ('3302', 'Matéria-prima (fragrância/essência)'),
    ('3303', 'Insumo/revenda (perfumaria)'), ('3304', 'Insumo/revenda (cosmético)'), ('3305', 'Insumo/revenda (capilar)'),
    ('3307', 'Insumo/revenda (higiene)'), ('3402', 'Matéria-prima (tensoativo)'), ('3404', 'Matéria-prima (ceras)'),
    ('3502', 'Matéria-prima (proteínas)'), ('3505', 'Matéria-prima (amidos modificados)'),
    ('3824', 'Matéria-prima (preparação química)'), ('3906', 'Matéria-prima (polímero)'), ('3910', 'Matéria-prima (silicone)'),
    ('3912', 'Matéria-prima (derivado de celulose)'), ('3913', 'Matéria-prima (polímero natural)'),
    ('3919', 'Embalagem (rótulo adesivo)'), ('3923', 'Embalagem (frasco/tampa/pote plástico)'),
    ('4819', 'Embalagem (caixa/cartucho)'), ('4821', 'Embalagem (rótulo/etiqueta)'), ('4911', 'Embalagem (rótulo/cartucho impresso)'),
    ('7010', 'Embalagem (frasco de vidro)'), ('7612', 'Embalagem (tubo de alumínio)'), ('7607', 'Embalagem (folha de alumínio)'),
    ('8309', 'Embalagem (tampa metálica)'), ('9616', 'Embalagem (válvula/pulverizador)'), ('8424', 'Embalagem (válvula/gatilho spray)'),
    ('8413', 'Embalagem (válvula pump)'),
]
NCM_USO_CONSUMO = [
    ('0901', 'Uso e consumo (copa)'), ('0902', 'Uso e consumo (copa)'), ('0903', 'Uso e consumo (copa)'),
    ('1701', 'Uso e consumo (copa)'), ('2201', 'Uso e consumo (copa)'), ('4818', 'Uso e consumo (higiene/limpeza)'),
    ('4823', 'Uso e consumo (papel - copa/escritório)'),
    ('3808', 'Uso e consumo (saneante)'), ('3814', 'Uso e consumo (solvente de limpeza)'), ('3822', 'Uso e consumo (reagente de laboratório)'),
    ('3926', 'Uso e consumo (luva/artigo plástico)'), ('3920', 'Uso e consumo (filme stretch - embalagem de transporte)'),
    ('4015', 'Uso e consumo (luva/EPI)'), ('5603', 'Uso e consumo (pano/TNT/EPI)'), ('61', 'Uso e consumo (uniforme/EPI)'),
    ('62', 'Uso e consumo (uniforme/EPI)'), ('63', 'Uso e consumo (panos)'), ('64', 'Uso e consumo (calçado/EPI)'),
    ('65', 'Uso e consumo (EPI)'), ('7608', 'Uso e consumo (ferramenta/limpeza)'), ('73', 'Uso e consumo (ferragens)'),
    ('82', 'Uso e consumo (ferramentas)'), ('8443', 'Uso e consumo (suprimento de impressora)'), ('8533', 'Uso e consumo (peça de manutenção)'),
    ('8536', 'Uso e consumo (material elétrico)'), ('8539', 'Uso e consumo (lâmpadas)'), ('9603', 'Uso e consumo (pincel)'),
    ('9608', 'Uso e consumo (escritório)'),
]
NCM_ATIVO = [('84', 'Possível ativo imobilizado (máquina/equipamento)'), ('85', 'Possível ativo imobilizado (equipamento elétrico)'),
             ('90', 'Possível ativo imobilizado (instrumento)'), ('94', 'Possível ativo imobilizado (móvel)'),
             ('87', 'Possível ativo imobilizado (veículo)')]

CFOP_LEARN = {  # CFOP de entrada aprendido do SPED -> natureza
    '1101': 'insumo', '2101': 'insumo', '1102': 'insumo', '2102': 'insumo', '1122': 'insumo', '2122': 'insumo',
    '1556': 'uso', '2556': 'uso', '1407': 'uso', '2407': 'uso', '1551': 'ativo', '2551': 'ativo', '1406': 'ativo', '2406': 'ativo',
    '1901': 'remessa', '2901': 'remessa', '1924': 'remessa', '2924': 'remessa', '1949': 'outras', '2949': 'outras',
    '1911': 'insumo', '2911': 'insumo', '1910': 'insumo', '2910': 'insumo',
}

CSOSN_COM_CREDITO = {'101', '201', '900'}
CSOSN_DESCR = {'101': 'tributada com permissão de crédito', '102': 'tributada SEM permissão de crédito',
               '103': 'isenção na faixa de receita (sem crédito)', '201': 'com permissão de crédito e com ST',
               '202': 'sem permissão de crédito e com ST', '203': 'isenção na faixa com ST', '300': 'imune', '400': 'não tributada',
               '500': 'ICMS cobrado anteriormente por ST', '900': 'outros'}
ALIQ_INTERNA_PR = 19.5

BASE_LEGAL = [
    ('ICMS - crédito de insumos e embalagens', 'LC 87/1996, art. 20; RICMS/PR (Decreto 7.871/2017), art. 31 e seguintes'),
    ('ICMS - uso e consumo sem crédito', 'LC 87/1996, art. 33, I (crédito de uso e consumo só a partir de 01/01/2033)'),
    ('ICMS - ativo imobilizado (CIAP)', 'LC 87/1996, art. 20, § 5º - crédito em 48 parcelas mensais (bloco G do SPED)'),
    ('ICMS - fornecedor do Simples Nacional', 'LC 123/2006, art. 23, §§ 1º a 6º; Resolução CGSN 140/2018, art. 59 e 60 - '
     'crédito = valor do campo vCredICMSSN (CSOSN 101/201/900), só para mercadoria destinada à industrialização ou comercialização'),
    ('IPI - crédito de insumos', 'RIPI (Decreto 7.212/2010), art. 226, I; sem crédito de IPI de fornecedor do Simples (LC 123/2006, art. 23, caput)'),
    ('IPI - uso e consumo/ativo', 'RIPI, art. 226 - só MP, PI e ME; uso e consumo e ativo não geram crédito'),
    ('ICMS - frete (CT-e)', 'LC 87/1996, art. 20 - crédito do ICMS do frete tomado vinculado a operação tributada (CFOP 1352/2352/1353/2353)'),
    ('DIFAL uso e consumo/ativo', 'LC 87/1996, art. 4º, § 2º, e art. 13, § 1º, II (LC 190/2022); RICMS/PR - base dupla para contribuinte'),
    ('PIS/COFINS', 'Lucro Presumido - regime cumulativo (Lei 9.718/1998, arts. 2º e 3º): sem crédito de entradas'),
]


def _prefixo(ncm, tabela):
    for p, desc in tabela:
        if ncm.startswith(p):
            return desc
    return None


class Credito:
    def __init__(self, apuracao, fornecedores=None, cte_extra=None, overrides=None):
        self.a = apuracao
        self.forn = fornecedores or {}
        self.cte_extra = cte_extra or []
        self.ov = overrides or {}      # {"cnpj|ncm" ou "cnpj": "insumo"|"uso"|"ativo"}
        self.cnpj = apuracao.cnpj

    def natureza(self, n, i):
        """-> (codigo, descricao, origem). codigo: insumo|uso|ativo|remessa|outras|devolucao|financeiro|confirmar"""
        cf = i['cfop']
        ncm = (i['ncm'] or '')[:8]
        key1, key2 = f'{n["emit_cnpj"]}|{ncm}', n['emit_cnpj']
        if key1 in self.ov or key2 in self.ov:
            c = self.ov.get(key1) or self.ov.get(key2)
            return c, f'Definido pelo escritório ({c})', 'config'
        if cf in CFOP_REMESSA:
            return 'remessa', CFOP_REMESSA[cf], f'CFOP {cf}'
        if cf in CFOP_DEVOLUCAO_VENDA or n['finnfe'] == '4':
            return 'devolucao', 'Devolução de venda', f'CFOP {cf}'
        if ncm in ('00000000', '') or 'ANTECIPA' in (i['xprod'] or '').upper():
            return 'financeiro', 'Nota sem mercadoria (antecipação/financeira)', f'CFOP {cf} / NCM {ncm or "-"}'
        if cf in CFOP_ATIVO_FORN:
            return 'ativo', 'Venda de ativo pelo fornecedor', f'CFOP {cf}'
        f = self.forn.get(n['emit_cnpj'])
        if f:
            por_ncm = f.get('ncm', {}).get(ncm)
            cfl = (por_ncm or {}).get('cfop') or f.get('cfop')
            nat = CFOP_LEARN.get(cfl)
            if nat in ('insumo', 'uso', 'ativo') and cf not in CFOP_OUTRAS:
                d = {'insumo': 'Insumo (classificação do SPED anterior)', 'uso': 'Uso e consumo (classificação do SPED anterior)',
                     'ativo': 'Ativo (classificação do SPED anterior)'}[nat]
                return nat, d, f'SPED anterior: CFOP {cfl}'
        for tabela, cod in ((NCM_INSUMO, 'insumo'), (NCM_USO_CONSUMO, 'uso'), (NCM_ATIVO, 'ativo')):
            d = _prefixo(ncm, tabela)
            if d:
                if cf in CFOP_OUTRAS:
                    return 'outras', f'{d} - mas CFOP {cf} (outras saídas: amostra/brinde/remessa)', f'CFOP {cf}'
                if cf in CFOP_BONIFICACAO:
                    return cod, f'{d} - bonificação/amostra', f'NCM {ncm} + CFOP {cf}'
                return cod, d, f'NCM {ncm}'
        if cf in CFOP_OUTRAS:
            return 'outras', f'Outras saídas do fornecedor (CFOP {cf})', f'CFOP {cf}'
        return 'confirmar', 'Natureza não identificada - confirmar', f'NCM {ncm}'

    def analisar(self):
        linhas = []
        for n in self.a.entradas:
            simples = n['emit_crt'] in ('1', '4')
            for i in n['itens']:
                nat, desc, origem = self.natureza(n, i)
                vc = R(vcontabil(i))
                l = {'nota': n, 'item': i, 'natureza': nat, 'natureza_desc': desc, 'origem': origem,
                     'regime': 'Simples Nacional' if simples else ('Normal' if n['emit_crt'] == '3' else f'CRT {n["emit_crt"]}'),
                     'simples': simples, 'vc': vc, 'cred_icms': 0.0, 'cred_sn': 0.0, 'pot_sn': 0.0, 'cred_ipi': 0.0,
                     'difal': 0.0, 'motivo': '', 'acao': '', 'cfop_ent': self._cfop_ent(nat, n, i)}
                credita_merc = nat in ('insumo', 'devolucao')
                # ---- ICMS
                if simples:
                    cs = i['csosn'] or ''
                    if not credita_merc:
                        l['motivo'] = f'Simples (CSOSN {cs}) - {desc}: sem crédito (só mercadoria para industrialização/comercialização)'
                    elif cs in CSOSN_COM_CREDITO and i['vcredsn'] > 0:
                        l['cred_sn'] = R(i['vcredsn'])
                        l['motivo'] = f'Simples CSOSN {cs}: crédito de {i["pcredsn"]:g}% informado na nota (LC 123/06 art. 23 §1º)'
                    elif cs in CSOSN_COM_CREDITO and i['pcredsn'] > 0:
                        l['pot_sn'] = R((i['vprod'] - i['vdesc']) * i['pcredsn'] / 100)
                        l['motivo'] = (f'Simples CSOSN {cs} com {i["pcredsn"]:g}% mas vCredICMSSN zerado: crédito NÃO aproveitável '
                                       f'como está (potencial R$ {l["pot_sn"]:,.2f})')
                        l['acao'] = 'Pedir ao fornecedor nota fiscal complementar/correção com o valor do crédito do Simples'
                    elif cs in CSOSN_COM_CREDITO:
                        l['motivo'] = f'Simples CSOSN {cs} sem percentual de crédito (pCredSN 0%)'
                        l['acao'] = 'Fornecedor marcou "com permissão de crédito" sem informar % - pedir correção'
                    else:
                        l['motivo'] = f'Simples CSOSN {cs} ({CSOSN_DESCR.get(cs, "?")}): sem direito a crédito'
                else:
                    cst = i['cst_icms'] or ''
                    hist = self.forn.get(n['emit_cnpj'], {}).get('ncm', {}).get((i['ncm'] or '')[:8])
                    if credita_merc and i['vicms'] > 0 and hist is not None and not hist.get('icms') and nat != 'devolucao':
                        l['motivo'] = (f'{desc}: no SPED anterior este item do fornecedor foi escriturado SEM crédito '
                                       f'(CFOP {hist.get("cfop")}) - mantido sem crédito')
                        l['acao'] = f'Revisar: se for insumo, o crédito seria R$ {i["vicms"]:,.2f}'
                    elif credita_merc and i['vicms'] > 0 and cst not in ('40', '41', '50', '60'):
                        l['cred_icms'] = R(i['vicms'])
                        l['motivo'] = f'ICMS destacado (CST {cst}) em {desc.lower()}'
                    elif nat == 'ativo' and i['vicms'] > 0:
                        l['motivo'] = f'Ativo: crédito em 48 parcelas pelo CIAP = R$ {R(i["vicms"] / 48):,.2f}/mês (se for imobilizado)'
                        l['acao'] = 'Confirmar se é imobilizado; se sim, lançar no CIAP'
                    elif i['vicms'] > 0:
                        l['motivo'] = f'{desc}: ICMS destacado R$ {i["vicms"]:,.2f} não gera crédito'
                    elif credita_merc:
                        l['motivo'] = f'Sem ICMS destacado (CST {cst})'
                    else:
                        l['motivo'] = desc
                    if nat == 'confirmar' and i['vicms'] > 0:
                        l['acao'] = f'Confirmar se é insumo: crédito potencial R$ {i["vicms"]:,.2f}'
                # ---- IPI
                hist_ipi = self.forn.get(n['emit_cnpj'], {}).get('ncm', {}).get((i['ncm'] or '')[:8])
                if nat == 'insumo' and not simples and i['vipi'] > 0 and not (hist_ipi is not None and not hist_ipi.get('ipi')):
                    l['cred_ipi'] = R(i['vipi'])
                elif nat == 'devolucao':
                    l['cred_ipi'] = R(i['vipidevol'] + i['vipi'])
                # ---- DIFAL (uso e consumo / ativo vindo de outra UF)
                if nat in ('uso', 'ativo') and n['emit_uf'] != self.a.cfg['empresa']['uf'] and not simples:
                    base_sem = vc - i['vicms']
                    base = base_sem / (1 - ALIQ_INTERNA_PR / 100)
                    l['difal'] = max(0.0, R(base * ALIQ_INTERNA_PR / 100 - i['vicms']))
                    l['acao'] = (l['acao'] + '; ' if l['acao'] else '') + f'DIFAL estimado R$ {l["difal"]:,.2f} (base dupla, {ALIQ_INTERNA_PR}%)'
                linhas.append(l)
        self.linhas = linhas
        # ---- CT-e
        cfc = set(self.a.cfg['icms']['cfops_cte_com_credito'])
        cte = []
        vistos = set()
        for c in self.a.ctes:
            cf = cfop_entrada(c['cfop'])
            cte.append({'numero': c['numero'], 'emitente': c['emit_nome'], 'data': c['data'], 'cfop': cf, 'valor': c['vprest'],
                        'icms': c['vicms'], 'credito': R(c['vicms']) if cf in cfc or cf in ('2352', '2353', '1352', '1353') else 0.0,
                        'fonte': 'XML', 'obs': 'Frete de compra/venda tomado pela COSMETICI'})
            vistos.add(c['numero'])
        for x in self.cte_extra:
            if x['numero'] in vistos:
                continue
            cte.append(dict(x, fonte='Relatório SIEG (sem XML na pasta)'))
        self.cte = cte
        return self

    def _cfop_ent(self, nat, n, i):
        cf = cfop_entrada(i['cfop']) if not n['propria'] else i['cfop']
        dentro = cf[:1] == '1'
        mapa = {'insumo': '1101' if dentro else '2101', 'uso': '1556' if dentro else '2556', 'ativo': '1551' if dentro else '2551'}
        return mapa.get(nat, cf)

    def totais(self):
        t = collections.Counter()
        for l in self.linhas:
            t['icms'] += l['cred_icms']; t['sn'] += l['cred_sn']; t['pot_sn'] += l['pot_sn']; t['ipi'] += l['cred_ipi']
            t['difal'] += l['difal']
            if l['natureza'] == 'confirmar':
                t['confirmar'] += l['item']['vicms']
        t['cte_xml'] = sum(c['credito'] for c in self.cte if c['fonte'] == 'XML')
        t['cte_pend'] = sum(c['credito'] for c in self.cte if c['fonte'] != 'XML')
        return {k: R(v) for k, v in t.items()}


# ---------------------------------------------------------------- conferência com relatórios

def conferir_saidas(a, erp=None, sieg=None):
    """XML x relatório do ERP (Cosmos) x relatório SIEG, nota a nota."""
    linhas = []
    xml = {n['numero']: n for n in a.saidas}
    canc = {n['numero'] for n in a.canceladas if n['propria']}
    inut = {x for _, x in a.inutilizadas}
    sieg_s = {}
    for n in (sieg or {}).values():
        if n['emit_cnpj'] == a.cnpj and a.ini <= n['dhemi'] <= a.fim:
            sieg_s[n['numero']] = n
    nums = sorted(set(xml) | set(erp or {}) | set(sieg_s))
    for num in nums:
        x, e, s = xml.get(num), (erp or {}).get(num), sieg_s.get(num)
        vx = R(sum(vcontabil(i) for i in x['itens'])) if x else None
        ix = R(sum(i['vicms'] for i in x['itens'])) if x else None
        ipx = R(sum(i['vipi'] for i in x['itens'])) if x else None
        ve = e['vnf'] if e else None
        vs = R(sum(vcontabil(i) for i in s['itens'])) if s else None
        obs = []
        if x and e is not None and abs(vx - ve) > 0.02:
            obs.append(f'valor XML {vx:,.2f} ≠ ERP {ve:,.2f}')
        if x and e is not None and abs(ix - e['icms']) > 0.02:
            obs.append(f'ICMS XML {ix:,.2f} ≠ ERP {e["icms"]:,.2f}')
        if x and e is not None and abs(ipx - e['ipi']) > 0.02:
            obs.append(f'IPI XML {ipx:,.2f} ≠ ERP {e["ipi"]:,.2f}')
        if x and s is not None and abs(vx - vs) > 0.02:
            obs.append(f'valor XML {vx:,.2f} ≠ SIEG {vs:,.2f}')
        if not x:
            obs.append('cancelada' if num in canc else ('inutilizada' if num in inut else 'SEM XML autorizado'))
        if erp is not None and not e and x:
            obs.append('não está no relatório do ERP')
        if sieg is not None and not s and x:
            obs.append('não está no relatório SIEG')
        linhas.append({'numero': num, 'data': (x or {}).get('dhemi') or (e or {}).get('data'), 'cliente': (x or {}).get('dest_nome') or (e or {}).get('pessoa'),
                       'xml': vx, 'erp': ve, 'sieg': vs, 'icms_xml': ix, 'icms_erp': (e or {}).get('icms'),
                       'ipi_xml': ipx, 'ipi_erp': (e or {}).get('ipi'), 'obs': '; '.join(obs) or 'OK'})
    return linhas


def conferir_entradas(a, sieg=None):
    linhas = []
    xml = {n['chave']: n for n in a.entradas}
    sieg_e = {}
    for ch, n in (sieg or {}).items():
        if n['dest_cnpj'] == a.cnpj and n['emit_cnpj'] != a.cnpj and a.ini <= n['dhemi'] <= a.fim and n['autorizada']:
            sieg_e[ch] = n
    for ch in sorted(set(xml) | set(sieg_e), key=lambda c: ((xml.get(c) or sieg_e.get(c))['dhemi'], c)):
        x, s = xml.get(ch), sieg_e.get(ch)
        n = x or s
        vx = R(sum(vcontabil(i) for i in x['itens'])) if x else None
        vs = R(sum(vcontabil(i) for i in s['itens'])) if s else None
        obs = []
        if x and s and abs(vx - vs) > 0.02:
            obs.append(f'valor XML {vx:,.2f} ≠ SIEG {vs:,.2f}')
        if not x:
            obs.append('no relatório SIEG mas SEM XML na pasta')
        if sieg is not None and not s:
            obs.append('XML sem linha no relatório SIEG')
        linhas.append({'numero': n['numero'], 'data': n['dhemi'], 'fornecedor': n['emit_nome'], 'cnpj': n['emit_cnpj'],
                       'xml': vx, 'sieg': vs, 'chave': ch, 'obs': '; '.join(obs) or 'OK'})
    return linhas
