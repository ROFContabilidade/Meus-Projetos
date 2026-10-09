"""Apuração fiscal mensal da COSMETICI (Lucro Presumido, indústria de cosméticos - PR).

Lê os XML/relatórios do mês, aplica as regras do config e devolve um dicionário com:
saídas por acumulador, faturamento, PIS/COFINS, IRPJ/CSLL do trimestre, ICMS, ICMS-ST, IPI,
lista de notas, divergências da conferência e (se houver SPED do mês) o confronto com o SPED.

Uso pela linha de comando: ver fiscal_cosmetici.py.
"""
import calendar
import collections
import datetime as dt

from leitores import cfop_entrada

R = lambda x: round(x + 0.0, 2)
EVENTO_CANCELAMENTO = '110111'
EVENTOS_DESCONHECIMENTO = {'210220': 'Desconhecimento da operação', '210240': 'Operação não realizada'}


def vcontabil(i):
    return i['vprod'] - i['vdesc'] + i['vfrete'] + i['vseg'] + i['voutro'] + i['vipi'] + i['vst'] + i['vfcpst'] + i['vipidevol']


def _mes(mes):
    a, m = map(int, mes.split('-'))
    return dt.date(a, m, 1), dt.date(a, m, calendar.monthrange(a, m)[1])


class Apuracao:
    def __init__(self, cfg, mes, fontes, fornecedores=None, sped=None):
        self.cfg = cfg
        self.mes = mes
        self.ini, self.fim = _mes(mes)
        self.cnpj = cfg['empresa']['cnpj']
        self.f = fontes
        self.forn = fornecedores or {}
        self.sped = sped
        self.div = []           # divergências: (gravidade, tipo, documento, descrição, valor)
        self.obs = []           # observações para a contadora
        self.acum_por_cfop = {c: (cod, a) for cod, a in cfg['acumuladores_saida'].items() for c in a['cfops']}
        self.tol = cfg['conferencia']['tolerancia']

    # ------------------------------------------------------------ separação das notas
    def separar(self):
        canc = {e['chave'] for e in self.f['eventos'] if e['tp'] == EVENTO_CANCELAMENTO}
        self.cce = [e for e in self.f['eventos'] if e['tp'] == '110110']
        self.desconhecidas = {e['chave']: EVENTOS_DESCONHECIMENTO[e['tp']] for e in self.f['eventos'] if e['tp'] in EVENTOS_DESCONHECIMENTO}
        self.saidas, self.entradas, self.canceladas, self.fora_periodo, self.terceiros = [], [], [], [], []
        for n in self.f['nfe'].values():
            n['cancelada'] = n['chave'] in canc or not n['autorizada']
            propria = n['emit_cnpj'] == self.cnpj
            if not propria and n['dest_cnpj'] != self.cnpj:
                self.terceiros.append(n)
                continue
            n['tipo'] = 'S' if propria and n['tpnf'] == '1' else 'E'
            n['propria'] = propria
            if not (self.ini <= n['dhemi'] <= self.fim):
                self.fora_periodo.append(n)
                continue
            if n['cancelada']:
                self.canceladas.append(n)
                continue
            (self.saidas if n['tipo'] == 'S' else self.entradas).append(n)
        self.saidas.sort(key=lambda n: (n['serie'], n['numero']))
        self.entradas.sort(key=lambda n: (n['dhemi'], n['emit_nome'] or '', n['numero']))
        canc_cte = set()
        self.ctes = []
        for c in self.f['cte'].values():
            if not c['autorizada'] or c['chave'] in canc_cte:
                continue
            if self.ini <= c['data'] <= self.fim and c['toma_cnpj'] == self.cnpj:
                self.ctes.append(c)
        self.ctes.sort(key=lambda c: (c['data'], c['numero']))

    # ------------------------------------------------------------ saídas
    def resumo_saidas(self):
        res = collections.OrderedDict()
        for n in self.saidas:
            for i in n['itens']:
                cod, a = self.acum_por_cfop.get(i['cfop'], ('???', {'descricao': f'CFOP {i["cfop"]} SEM ACUMULADOR', 'grupo': 'outros'}))
                if cod == '???':
                    self.div.append(('ALTA', 'CFOP sem acumulador', self._doc(n), f'Item {i["n_item"]} CFOP {i["cfop"]} não está no config (acumuladores_saida)', vcontabil(i)))
                r = res.setdefault(cod, collections.Counter(descricao=0))
                r['vc'] += vcontabil(i); r['bc'] += i['vbc']; r['icms'] += i['vicms']; r['ipi'] += i['vipi']
                r['bcst'] += i['vbcst']; r['st'] += i['vst'] + i['vfcpst']
                r['_grupo'] = a['grupo']; r['_desc'] = a['descricao']
        out = []
        for cod in sorted(res):
            r = res[cod]
            out.append({'acumulador': cod, 'descricao': r['_desc'], 'grupo': r['_grupo'], 'vc': R(r['vc']), 'bc': R(r['bc']),
                        'icms': R(r['icms']), 'outras': R(r['vc'] - r['bc']), 'ipi': R(r['ipi']), 'bcst': R(r['bcst']), 'st': R(r['st'])})
        self.acumuladores = out
        return out

    def _tot(self, grupo, campo):
        return R(sum(a[campo] for a in self.acumuladores if a['grupo'] == grupo))

    # ------------------------------------------------------------ devoluções de venda (entradas)
    def devolucoes(self):
        cf = set(self.cfg['cfops_devolucao_venda'])
        dev = collections.Counter()
        self.notas_devolucao = []
        for n in self.entradas:
            itens = [i for i in n['itens'] if (i['cfop'] if n['propria'] else cfop_entrada(i['cfop'])) in cf]
            if not itens:
                continue
            self.notas_devolucao.append(n)
            for i in itens:
                dev['vc'] += vcontabil(i); dev['icms'] += i['vicms']; dev['ipi'] += i['vipi'] + i['vipidevol']
                dev['st'] += i['vst'] + i['vfcpst']
        self.dev = {k: R(v) for k, v in dev.items()}
        for k in ('vc', 'icms', 'ipi', 'st'):
            self.dev.setdefault(k, 0.0)
        return self.dev

    # ------------------------------------------------------------ faturamento e PIS/COFINS
    def faturamento(self):
        vendas, indus = self._tot('venda', 'vc'), self._tot('industrializacao', 'vc')
        st_total = R(sum(a['st'] for a in self.acumuladores))
        ipi_total = R(sum(a['ipi'] for a in self.acumuladores))
        self.fat = {'vendas': vendas, 'industrializacao': indus, 'bruto': R(vendas + indus), 'devolucoes': self.dev['vc'],
                    'st': st_total, 'ipi': ipi_total}
        self.fat['liquido'] = R(vendas + indus - self.dev['vc'] - st_total - ipi_total)
        return self.fat

    def pis_cofins(self):
        pc = self.cfg['pis_cofins']
        base_ind = R(self._tot('industrializacao', 'vc') - self._tot('industrializacao', 'icms'))
        base_ven = R(self._tot('venda', 'vc') - self._tot('venda', 'icms') - self.fat['ipi'] - self.fat['st'])
        dev_liq = R(self.dev['vc'] - self.dev['icms'] - self.dev['ipi'] - self.dev['st'])
        if pc['deduzir_devolucoes']:
            base_ven = R(base_ven - dev_liq)
        ai, av = pc['aliquotas_industrializacao'], pc['aliquotas_vendas']
        r = {'base_industrializacao': base_ind, 'base_vendas': base_ven, 'devolucoes_liquidas': dev_liq,
             'deduziu_devolucoes': pc['deduzir_devolucoes'],
             'pis_ind': R(base_ind * ai['pis']), 'pis_ven': R(base_ven * av['pis']),
             'cofins_ind': R(base_ind * ai['cofins']), 'cofins_ven': R(base_ven * av['cofins'])}
        r['pis'] = R(r['pis_ind'] + r['pis_ven'])
        r['cofins'] = R(r['cofins_ind'] + r['cofins_ven'])
        if dev_liq and not pc['deduzir_devolucoes']:
            r['pis_alt'] = R(r['pis'] - R(dev_liq * av['pis']))
            r['cofins_alt'] = R(r['cofins'] - R(dev_liq * av['cofins']))
            self.obs.append(f'Devoluções de venda de R$ {dev_liq:,.2f} (líquidas de ICMS/IPI/ST) NÃO foram deduzidas da base do PIS/COFINS, '
                            f'como na planilha de 08/2026. Se deduzir (Lei 9.718/98, art. 3º, §2º, I - vendas canceladas), PIS = R$ {r["pis_alt"]:,.2f} '
                            f'e COFINS = R$ {r["cofins_alt"]:,.2f}. Confirmar com a contadora (config: pis_cofins.deduzir_devolucoes).')
        self.pc = r
        return r

    def irpj_csll(self):
        c = self.cfg['irpj_csll']
        a, m = map(int, self.mes.split('-'))
        tri = (m - 1) // 3 + 1
        meses = [f'{a}-{x:02d}' for x in range(3 * tri - 2, 3 * tri + 1)]
        hist = dict(self.cfg.get('faturamento_mensal', {}))
        hist[self.mes] = {'valor': self.fat['liquido'], 'origem': 'esta apuração'}
        linhas = [(mm, hist.get(mm, {}).get('valor'), hist.get(mm, {}).get('origem', 'FALTA')) for mm in meses if mm <= self.mes]
        falta = [mm for mm, v, _ in linhas if v is None]
        receita = R(sum(v for _, v, _ in linhas if v is not None))
        base_csll = R(receita * c['presuncao_csll'])
        base_irpj = R(receita * c['presuncao_irpj'])
        excedente = max(0.0, R(base_irpj - c['limite_adicional_trimestre']))
        r = {'trimestre': f'{tri}º trimestre/{a}', 'meses': linhas, 'faltam': falta, 'fechamento': m % 3 == 0 and not falta,
             'receita': receita, 'base_csll': base_csll, 'csll': R(base_csll * c['aliquota_csll']),
             'base_irpj': base_irpj, 'irpj_normal': R(base_irpj * c['aliquota_irpj']), 'base_adicional': R(excedente),
             'irpj_adicional': R(excedente * c['adicional_irpj'])}
        r['irpj'] = R(r['irpj_normal'] + r['irpj_adicional'])
        if falta:
            self.obs.append(f'IRPJ/CSLL do {r["trimestre"]}: falta o faturamento de {", ".join(falta)} (config: faturamento_mensal). '
                            'O cálculo do trimestre está parcial.')
        self.ir = r
        return r

    # ------------------------------------------------------------ créditos das entradas
    def _regra_entrada(self, n, i):
        """Devolve (cfop_entrada, credita_icms, credita_ipi, origem_da_regra)."""
        if n['propria']:
            cf = i['cfop']
        else:
            cf = cfop_entrada(i['cfop'])
        f = self.forn.get(n['emit_cnpj'] or '')
        if f and not n['propria']:
            por_ncm = f.get('ncm', {}).get(i['ncm'][:8])
            if por_ncm:
                return por_ncm['cfop'], por_ncm['icms'], por_ncm['ipi'], 'aprendido (fornecedor+NCM)'
            return f['cfop'], f['icms'], f['ipi'], 'aprendido (fornecedor)'
        ci = cf in self.cfg['icms']['cfops_entrada_com_credito_padrao']
        cp = cf in self.cfg['ipi']['cfops_entrada_com_credito']
        return cf, ci, cp, 'regra padrão (fornecedor novo)'

    def entradas_creditos(self):
        linhas = []
        novos = set()
        for n in self.entradas:
            for i in n['itens']:
                cf, ci, cp, orig = self._regra_entrada(n, i)
                cred_icms = R(i['vicms']) if ci else 0.0
                cred_ipi = R(i['vipi'] + i['vipidevol']) if cp else 0.0
                if orig.startswith('regra') and not n['propria'] and (i['vicms'] or i['vipi']):
                    novos.add((n['emit_cnpj'], n['emit_nome']))
                linhas.append({'nota': n, 'item': i, 'cfop': cf, 'vc': R(vcontabil(i)), 'cred_icms': cred_icms,
                               'cred_ipi': cred_ipi, 'regra': orig, 'icms_destacado': R(i['vicms']), 'ipi_destacado': R(i['vipi'])})
        for cnpj, nome in sorted(novos, key=lambda x: x[1] or ''):
            self.div.append(('MÉDIA', 'Fornecedor sem histórico', f'{nome} ({cnpj})',
                             'Crédito de ICMS/IPI pela regra padrão do CFOP - confirmar se é insumo (1101/2101) ou uso e consumo (1556/2556)', None))
        for ch, motivo in self.desconhecidas.items():
            n = self.f['nfe'].get(ch)
            self.div.append(('ALTA', 'Manifestação', self._doc(n) if n else ch, f'Nota manifestada como "{motivo}" - não escriturar', None))
        self.ent = linhas
        cte = []
        cf_cte = set(self.cfg['icms']['cfops_cte_com_credito'])
        for c in self.ctes:
            cf = cfop_entrada(c['cfop'])
            cred = R(c['vicms']) if cf in cf_cte and c['vicms'] else 0.0
            cte.append({'cte': c, 'cfop': cf, 'cred_icms': cred})
        self.cte_cred = cte
        return linhas, cte

    # ------------------------------------------------------------ ICMS, ST e IPI
    def icms(self):
        aj = self.cfg['icms'].get('ajustes', {}).get(self.mes, [])
        deb = R(sum(a['icms'] for a in self.acumuladores))
        cred_nfe = R(sum(l['cred_icms'] for l in self.ent))
        cred_cte = R(sum(l['cred_icms'] for l in self.cte_cred))
        aj_deb = R(sum(x['valor'] for x in aj if x['tipo'] == 'debito'))
        aj_cred = R(sum(x['valor'] for x in aj if x['tipo'] == 'credito'))
        sld_ant = R(self.cfg['icms'].get('saldo_credor_anterior', {}).get(self.mes, 0.0))
        saldo = R(deb + aj_deb - cred_nfe - cred_cte - aj_cred - sld_ant)
        self.ic = {'debitos': deb, 'creditos_nfe': cred_nfe, 'creditos_cte': cred_cte, 'creditos': R(cred_nfe + cred_cte),
                   'ajustes_debito': aj_deb, 'ajustes_credito': aj_cred, 'ajustes': aj, 'saldo_credor_anterior': sld_ant,
                   'recolher': max(0.0, saldo), 'saldo_credor': max(0.0, -saldo)}
        return self.ic

    def icms_st(self):
        por_uf = collections.Counter()
        for n in self.saidas:
            for i in n['itens']:
                if i['vst'] or i['vfcpst']:
                    por_uf[n['dest_uf'] or '??'] += i['vst'] + i['vfcpst']
        devol = R(self.dev['st'])
        uf = self.cfg['empresa']['uf']
        self.st = {'por_uf': {k: R(v) for k, v in sorted(por_uf.items())}, 'devolucoes': devol,
                   'recolher_pr': R(por_uf.get(uf, 0.0) - devol), 'total': R(sum(por_uf.values()) - devol)}
        return self.st

    def ipi(self):
        deb = R(sum(a['ipi'] for a in self.acumuladores))
        cred = R(sum(l['cred_ipi'] for l in self.ent))
        sld = R(deb - cred)
        self.ip = {'debitos': deb, 'creditos': cred, 'recolher': max(0.0, sld), 'saldo_credor': max(0.0, -sld)}
        return self.ip

    # ------------------------------------------------------------ conferência dos XML
    def _doc(self, n):
        return f'NF {n["numero"]}/{n["serie"]} {n["dhemi"]:%d/%m} {(n["dest_nome"] if n.get("tipo") == "S" else n["emit_nome"]) or ""}'.strip()

    def conferir(self):
        cc = self.cfg['conferencia']
        uf = self.cfg['empresa']['uf']
        aliq_uf = {u: float(a) for a, ufs in cc['aliquota_interestadual'].items() for u in ufs}
        mono = tuple(cc['ncm_monofasico_prefixos'])
        t = self.tol
        grupo = lambda cf: self.acum_por_cfop.get(cf, (None, {'grupo': None}))[1]['grupo']
        nao_mono_vendas = collections.Counter()
        for n in self.saidas:
            d = self._doc(n)
            for i in n['itens']:
                it = f'item {i["n_item"]} ({i["xprod"] or ""})'[:70]
                cf = i['cfop']
                if i['vbc'] and i['cst_icms'] not in ('40', '41', '50', '51', '60') and abs(R(i['vbc'] * i['picms'] / 100) - i['vicms']) > t:
                    self.div.append(('ALTA', 'ICMS recalculado', d, f'{it}: BC {i["vbc"]:,.2f} x {i["picms"]}% = {R(i["vbc"]*i["picms"]/100):,.2f} ≠ destacado {i["vicms"]:,.2f}', i['vicms']))
                if i['cst_icms'] in ('00', '10', '20', '70') and not i['vicms'] and grupo(cf) in ('venda', 'industrializacao'):
                    self.div.append(('MÉDIA', 'CST x valor', d, f'{it}: CST {i["cst_icms"]} sem ICMS destacado (CFOP {cf})', None))
                if i['cst_icms'] in ('40', '41', '50') and i['vicms']:
                    self.div.append(('ALTA', 'CST x valor', d, f'{it}: CST {i["cst_icms"]} com ICMS destacado {i["vicms"]:,.2f}', i['vicms']))
                if cf[:1] == '5' and n['dest_uf'] and n['dest_uf'] != uf:
                    self.div.append(('ALTA', 'CFOP x UF', d, f'{it}: CFOP {cf} (dentro do estado) para {n["dest_uf"]}', None))
                if cf[:1] == '6' and n['dest_uf'] == uf:
                    self.div.append(('ALTA', 'CFOP x UF', d, f'{it}: CFOP {cf} (fora do estado) para {uf}', None))
                if cf[:1] == '6' and i['picms'] and n['dest_uf'] in aliq_uf and (n.get('ind_ie_dest') in (None, '1')):
                    esperado = 4.0 if i['orig'] in cc['origens_importado_4'] else aliq_uf[n['dest_uf']]
                    if abs(i['picms'] - esperado) > 0.001:
                        self.div.append(('ALTA', 'Alíquota interestadual', d, f'{it}: {i["picms"]}% para {n["dest_uf"]} (origem {i["orig"]}) - esperado {esperado:g}%', i['vicms']))
                if i['vbc_ipi'] and abs(R(i['vbc_ipi'] * i['pipi'] / 100) - i['vipi']) > t:
                    self.div.append(('ALTA', 'IPI recalculado', d, f'{it}: BC {i["vbc_ipi"]:,.2f} x {i["pipi"]}% ≠ IPI {i["vipi"]:,.2f}', i['vipi']))
                if cf in ('5401', '5403', '6401', '6403') and not i['vst']:
                    self.div.append(('MÉDIA', 'ST', d, f'{it}: CFOP {cf} (com ST) sem ICMS-ST destacado', None))
                if cf in ('5101', '5102', '6101', '6102') and i['vst']:
                    self.div.append(('MÉDIA', 'ST', d, f'{it}: CFOP {cf} (sem ST) com ICMS-ST de {i["vst"]:,.2f} - conferir CFOP (5401/5403/5405)', i['vst']))
                e_mono = i['ncm'].startswith(mono)
                if grupo(cf) == 'venda':
                    if e_mono and i['cst_pis'] and i['cst_pis'] != '02':
                        self.div.append(('BAIXA', 'PIS/COFINS monofásico', d, f'{it}: NCM {i["ncm"]} monofásico com CST PIS {i["cst_pis"]} na nota (esperado 02)', None))
                    if not e_mono:
                        nao_mono_vendas[i['ncm']] += vcontabil(i) - i['vicms'] - i['vipi'] - i['vst']
        if nao_mono_vendas:
            tot = R(sum(nao_mono_vendas.values()))
            ncms = ', '.join(f'{k} (R$ {v:,.2f})' for k, v in nao_mono_vendas.most_common())
            self.obs.append(f'Vendas de NCM fora da lista monofásica (Lei 10.147/2000, art. 1º, I, b) somam R$ {tot:,.2f} e estão na base de 2,2%/10,3%, '
                            f'como na planilha de 08/2026: {ncms}. Se forem tributadas a 0,65%/3%, a diferença é PIS R$ {R(tot*(0.022-0.0065)):,.2f} '
                            f'e COFINS R$ {R(tot*(0.103-0.03)):,.2f} a menor. Confirmar com a contadora.')
        # numeração das notas próprias
        por_serie = collections.defaultdict(set)
        for n in self.saidas + self.canceladas + [x for x in self.entradas if x['propria']]:
            if n['propria']:
                por_serie[n['serie']].add(n['numero'])
        inut = collections.defaultdict(set)
        for i in self.f['inut']:
            inut[str(int(i['serie']))].update(range(i['ini'], i['fim'] + 1))
        self.inutilizadas = sorted((s, x) for s, xs in inut.items() for x in xs)
        for s, nums in por_serie.items():
            if not nums:
                continue
            faltam = sorted(set(range(min(nums), max(nums) + 1)) - nums - inut[str(int(s))])
            for x in faltam:
                self.div.append(('ALTA', 'Numeração', f'NF {x}/{s}', 'Número sem XML no período (nem cancelada nem inutilizada) - pedir o XML', None))
        for n in self.fora_periodo:
            if n.get('tipo') == 'S':
                self.div.append(('BAIXA', 'Fora do período', self._doc(n), f'Emitida em {n["dhemi"]:%d/%m/%Y} - não entra neste mês', n['vnf']))
        for e in self.cce:
            n = self.f['nfe'].get(e['chave'])
            if n and self.ini <= (e['data'] or self.ini) <= self.fim:
                self.div.append(('BAIXA', 'Carta de correção', self._doc(n), (e['correcao'] or '')[:200], None))
        return self.div

    # ------------------------------------------------------------ confronto com o SPED
    def confrontar_sped(self):
        s = self.sped
        if not s:
            self.conf = None
            return None
        ch_sped_s = {d['chave'] for d in s['docs'] if d['ind_oper'] == '1' and d['cod_sit'] in ('00', '01', '06', '07', '08')}
        ch_sped_e = {d['chave'] for d in s['docs'] if d['ind_oper'] == '0' and d['cod_sit'] in ('00', '01', '06', '07', '08')}
        ch_xml_s = {n['chave'] for n in self.saidas}
        ch_xml_e = {n['chave'] for n in self.entradas}
        for ch in sorted(ch_sped_s - ch_xml_s):
            self.div.append(('ALTA', 'SPED x XML', ch, 'Saída escriturada no SPED sem XML autorizado no mês', None))
        for ch in sorted(ch_xml_s - ch_sped_s):
            self.div.append(('ALTA', 'SPED x XML', ch, 'Saída com XML que não está no SPED', None))
        doc_sped = {d['chave']: d for d in s['docs']}
        for ch in sorted(ch_xml_e - ch_sped_e):
            n = self.f['nfe'][ch]
            self.div.append(('MÉDIA', 'SPED x XML', self._doc(n), 'Entrada com XML que não está no SPED do mês (lançada em outro mês?)', n['vnf']))
        for ch in sorted(ch_sped_e - ch_xml_e):
            d = doc_sped[ch]
            self.div.append(('MÉDIA', 'SPED x XML', f'NF {d["numero"]} {d["nome"] or ""}', 'Entrada no SPED sem XML no mês (pedir o XML)', d['vl_doc']))
        e110, e520 = s['e110'] or {}, s['e520'] or {}
        st_pr = s['e210'].get(self.cfg['empresa']['uf'], {})
        cred_cte = R(sum(x['vl_icms'] for d in s['cte'] for x in d['d190']))
        cred_ent = R(sum(x['vl_icms'] for d in s['docs'] if d['ind_oper'] == '0' for x in d['c190']))
        self.conf = [
            ('ICMS - débitos', self.ic['debitos'], e110.get('tot_debitos')),
            ('ICMS - créditos NF-e', self.ic['creditos_nfe'], cred_ent),
            ('ICMS - créditos CT-e', self.ic['creditos_cte'], cred_cte),
            ('ICMS - a recolher', self.ic['recolher'], e110.get('icms_recolher')),
            ('ICMS-ST PR - a recolher', self.st['recolher_pr'], st_pr.get('icms_recol_st')),
            ('IPI - débitos', self.ip['debitos'], e520.get('debitos')),
            ('IPI - créditos', self.ip['creditos'], e520.get('creditos')),
            ('IPI - a recolher', self.ip['recolher'], e520.get('sd')),
        ]
        return self.conf

    def executar(self):
        self.separar()
        self.resumo_saidas()
        self.devolucoes()
        self.faturamento()
        self.pis_cofins()
        self.irpj_csll()
        self.entradas_creditos()
        self.icms()
        self.icms_st()
        self.ipi()
        self.conferir()
        self.confrontar_sped()
        ordem = {'ALTA': 0, 'MÉDIA': 1, 'BAIXA': 2}
        self.div.sort(key=lambda d: (ordem[d[0]], d[1], d[2]))
        return self

    # ------------------------------------------------------------ guias
    def guias(self):
        a, m = map(int, self.mes.split('-'))
        prox = dt.date(a + (m == 12), m % 12 + 1, 1)
        dia = lambda d: dt.date(prox.year, prox.month, min(d, calendar.monthrange(prox.year, prox.month)[1]))
        pc, ic, ir = self.cfg['pis_cofins'], self.cfg['icms'], self.cfg['irpj_csll']
        g = [
            ('PIS', f'DARF {pc["codigo_darf"]["pis"]}', self.pc['pis'], dia(pc['vencimento_dia'])),
            ('COFINS', f'DARF {pc["codigo_darf"]["cofins"]}', self.pc['cofins'], dia(pc['vencimento_dia'])),
            ('IPI', f'DARF {self.cfg["ipi"]["codigo_darf"]}', self.ip['recolher'], dia(self.cfg['ipi']['vencimento_dia'])),
            ('ICMS próprio', f'GR-PR {ic["codigo_receita_pr"]}', self.ic['recolher'], dia(ic['vencimento_dia'])),
            ('ICMS-ST (PR)', f'GR-PR {ic["codigo_receita_st_pr"]}', self.st['recolher_pr'], dia(ic['vencimento_dia_st'])),
        ]
        if self.ir['fechamento']:
            ult = dt.date(prox.year, prox.month, calendar.monthrange(prox.year, prox.month)[1])
            while ult.weekday() > 4:
                ult -= dt.timedelta(days=1)
            g.append(('IRPJ', f'DARF {ir["codigo_darf"]["irpj"]} ({self.ir["trimestre"]})', self.ir['irpj'], ult))
            g.append(('CSLL', f'DARF {ir["codigo_darf"]["csll"]} ({self.ir["trimestre"]})', self.ir['csll'], ult))
        return g


def faturamento_sped(sped, cfg):
    """Faturamento do mês pelo SPED Fiscal (mesma regra da apuração): C190 de saída por grupo de CFOP."""
    grupo = {c: a['grupo'] for a in cfg['acumuladores_saida'].values() for c in a['cfops']}
    dev = set(cfg['cfops_devolucao_venda'])
    t = collections.Counter()
    for d in sped['docs']:
        if d['cod_sit'] not in ('00', '01', '06', '07', '08'):
            continue
        for x in d['c190']:
            if d['ind_oper'] == '1':
                g = grupo.get(x['cfop'])
                if g in ('venda', 'industrializacao'):
                    t[g] += x['vl_opr']
                    t['icms_' + g] += x['vl_icms']
                t['st'] += x['vl_st']
                t['ipi'] += x['vl_ipi']
            elif x['cfop'] in dev:
                t['devolucoes'] += x['vl_opr']
    r = {k: R(t[k]) for k in ('venda', 'industrializacao', 'devolucoes', 'st', 'ipi')}
    r['liquido'] = R(r['venda'] + r['industrializacao'] - r['devolucoes'] - r['st'] - r['ipi'])
    pc = cfg['pis_cofins']
    ai, av = pc['aliquotas_industrializacao'], pc['aliquotas_vendas']
    bi = R(r['industrializacao'] - t['icms_industrializacao'])
    bv = R(r['venda'] - t['icms_venda'] - r['ipi'] - r['st'])
    r['pis'] = R(R(bi * ai['pis']) + R(bv * av['pis']))
    r['cofins'] = R(R(bi * ai['cofins']) + R(bv * av['cofins']))
    return r
