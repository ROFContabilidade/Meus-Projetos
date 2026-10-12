"""TXT de importação das notas no Domínio (Escrita Fiscal) no leiaute do SPED Fiscal EFD ICMS/IPI, igual ao arquivo que o Domínio
já aceitou (IMPORTACAO_DOMINIO_MMAAAA.TXT da Kopp Indústria): blocos 0, C (C100/C101/C170/C190), D (D100/D190), E (só E100),
G/H/K vazios, 1 (1010) e 9. Particularidades do Domínio:
  - C170 COD_NAT = código do ACUMULADOR (0400 lista os acumuladores usados) e COD_CTA = conta contábil;
  - COD_PART = CNPJ/CPF do participante (0150 com endereço do XML);
  - TODOS os valores (CST, base, alíquota e valor de ICMS - com o diferimento do PR como o emitente informou -, ST, IPI, PIS,
    COFINS) e os totais do C100 vêm EXATAMENTE do XML; nada é recalculado nem zerado. Só o CFOP é o de entrada (1xxx/2xxx)
    e o acumulador/conta vêm do histórico do Domínio. O crédito (uso e consumo sem crédito etc.) fica pela parametrização do
    acumulador no Domínio;
  - IBS/CBS: o leiaute 020 aceito não tem campo para eles - ficam nas planilhas de conferência;
  - saídas: valores do XML; canceladas COD_SIT 02 e inutilizadas COD_SIT 05 só com número/chave.
Valores exatamente como no XML. NFS-e não fazem parte do SPED ICMS/IPI. CT-e sem XML ficam de fora (pedir o XML)."""
import collections
import hashlib
import re

from apuracao import vcontabil
from leitores import cfop_entrada

R = lambda x: round((x or 0.0) + 0.0, 2)


def m(v, d=2):
    return f'{(v or 0.0):.{d}f}'.replace('.', ',')


def dt8(d):
    return d.strftime('%d%m%Y') if d else ''


def _cod_item(prefixo, cnpj, cprod, xprod):
    h = hashlib.sha1(f'{cnpj}|{cprod or xprod}'.encode()).hexdigest()
    return prefixo + format(int(h[:15], 16), 'X')[:9].upper()


def _cst(i):
    """CST exatamente do XML: origem + CST (2 dígitos) ou o CSOSN do Simples (3 dígitos, como no SPED do Domínio)."""
    if i.get('csosn'):
        return i['csosn']
    return f'{i.get("orig") or "0"}{(i.get("cst_icms") or "00")[-2:]}'


SEM_CREDITO = {'uso'}   # natureza fora da atividade-fim (uso e consumo, material fabril que não entra no cosmético)


def _zerar(x):
    """Compra fora da atividade-fim: mantém CST e valores da nota, zera base/alíquota/valor de ICMS, ST, IPI e PIS/COFINS
    (CST 98), exatamente como no arquivo aceito pelo Domínio (Kopp, 1556/2556/1407)."""
    x.update(bc=0.0, aliq=0.0, icms=0.0, bcst=0.0, aliqst=0.0, st=0.0, cst_ipi='', enq='', bcipi=0.0, aliqipi=0.0, ipi=0.0,
             cst_pis='98', bcpis=0.0, ppis=0.0, pis=0.0, cst_cof='98', bccof=0.0, pcof=0.0, cof=0.0, zerado=True)
    return x


def _credito_sn(i, l):
    """Crédito do Simples (LC 123/06 art. 23): CSOSN 101/201/900 com pCredSN e vCredICMSSN informados no XML e compra da
    atividade-fim (insumo/embalagem). Sem o valor no XML, ou com CSOSN 102/103/300/400/500, não há crédito."""
    return (i.get('csosn') in ('101', '201', '900') and (i.get('vcredsn') or 0) > 0 and (i.get('pcredsn') or 0) > 0
            and l['natureza'] == 'insumo')


def _simples(x, i):
    """Crédito do Simples no C170 com os campos do próprio XML: alíquota = pCredSN, ICMS = vCredICMSSN, base = valor do item."""
    x.update(bc=R(i['vprod'] - i['vdesc']), aliq=i['pcredsn'], icms=i['vcredsn'], credito_sn=True)
    return x


def _xml(i):
    """Valores do item EXATAMENTE como estão no XML - nada é recalculado nem zerado (base, alíquota e valor de ICMS, com o
    diferimento do PR já aplicado pelo emitente no vICMS; ST; IPI; PIS; COFINS)."""
    return {'qtd': i['qtd'], 'vprod': i['vprod'], 'vdesc': i['vdesc'],
            'bc': i['vbc'], 'aliq': i['picms'], 'icms': i['vicms'], 'bcst': i['vbcst'], 'aliqst': i['picmsst'], 'st': i['vst'],
            'cst_ipi': i.get('cst_ipi') or '', 'enq': i.get('cod_enq') or '', 'bcipi': i['vbc_ipi'], 'aliqipi': i['pipi'], 'ipi': i['vipi'],
            'cst_pis': i.get('cst_pis') or '', 'bcpis': i['vbc_pis'], 'ppis': i['ppis'], 'pis': i['vpis'],
            'cst_cof': i.get('cst_cof') or '', 'bccof': i['vbc_cof'], 'pcof': i['pcof'], 'cof': i['vcof'], 'vc': R(vcontabil(i))}


def cst_ipi_entrada(cst, ipi=0.0):
    """CST do IPI na ENTRADA (regra do PVA: CFOP 1/2/3 -> CST_IPI menor que 50). O XML traz o CST de SAÍDA do fornecedor;
    o SPED pede o código de entrada correspondente, como o Domínio gravou em 07 e 08/2026: 50 com IPI creditado -> 00,
    50 sem IPI creditado -> 49, 51..55 -> 01..05, 99 -> 49, sem IPI no XML (ou item zerado de uso e consumo) -> 49.
    Valores de base/alíquota/IPI continuam os do XML."""
    cst = (cst or '').strip()
    if cst in ('51', '52', '53', '54', '55'):
        return f'0{int(cst) - 50}'
    if cst == '50':
        return '00' if (ipi or 0) > 0 else '49'
    if cst and cst < '50':
        return cst
    return '49'


IND_FRT = {'0': '0', '1': '1', '2': '2', '3': '0', '4': '1', '9': '9'}


class Sped:
    def __init__(self, a):
        self.a = a
        self.part, self.unid, self.itens, self.nat = {}, set(), {}, {}
        self.c, self.d, self.pend = [], [], []
        self.e = []   # E110/E111/E113: DIFAL e ICMS antecipado de importado (regra da usuária - já vêm no TXT)

    # ------------------------------------------------------------ cadastros
    def participante(self, doc, end, nome):
        doc = re.sub(r'\D', '', doc or '')
        if not doc or doc in self.part:
            return doc
        end = end or {}
        cnpj, cpf = (doc, '') if len(doc) == 14 else ('', doc)
        self.part[doc] = ['0150', doc, (nome or end.get('nome') or '')[:100], '01058', cnpj, cpf, end.get('ie') or '',
                          end.get('cmun') or '', '', end.get('lgr') or '', end.get('nro') or '', end.get('cpl') or '', end.get('bairro') or '']
        return doc

    def item(self, prefixo, cnpj, i, tipo):
        cod = _cod_item(prefixo, cnpj, i.get('cprod'), i.get('xprod'))
        un = (i.get('un') or 'UN').strip()[:6]
        self.unid.add(un)
        if cod not in self.itens:
            ncm = (i.get('ncm') or '')[:8]
            self.itens[cod] = ['0200', cod, (i.get('xprod') or '')[:200], '', '', un, tipo, ncm, '', ncm[:2] if ncm else '', '', '', '']
        return cod, un

    def natureza(self, cod, descr):
        if cod:
            self.nat.setdefault(str(cod), ['0400', str(cod), (descr or '')[:60]])
        return str(cod or '')

    # ------------------------------------------------------------ C100/C170/C190
    def _c100(self, oper, emit, part, n, sit, itens170, c101=None):
        ser = str(int(n['serie'])) if str(n.get('serie') or '').isdigit() else (n.get('serie') or '')
        if sit == '02' and itens170:   # cancelada de terceiro: o Domínio exige participante, datas e C170 (tudo zerado)
            z = m(0)
            bloco = [['C100', oper, emit, part, '55', sit, ser, str(n['numero']), n['chave'], dt8(n['dhemi']), dt8(n.get('dhsaient') or n['dhemi']),
                      z, '2', z, z, z, '9', z, z, z, z, z, z, z, z, z, z, z, z]]
            c190 = collections.OrderedDict()
            for k, x in enumerate(itens170, 1):
                bloco.append(['C170', str(k), x['cod'], '', m(x['qtd'], 5), x['un'], z, z, '0', x['cst'], x['cfop'], x['nat'],
                              z, z, z, z, z, z, '0', '', '', '', '', '', '98', z, m(0, 4), '', '', z, '98', z, m(0, 4), '', '', z, x['cta'], z])
                c190.setdefault((x['cst'], x['cfop']), 1)
            for cst, cf in c190:
                bloco.append(['C190', cst, cf, z, z, z, z, z, z, z, z, ''])
            self.c.append(bloco)
            return
        if sit in ('02', '05'):
            self.c.append([['C100', oper, emit, '', '55', sit, ser, str(n['numero']), n.get('chave') or '', dt8(n.get('dhemi')) if sit == '05' else '']
                           + [''] * 19])
            return
        t = n['tot']   # totais exatamente do XML (ICMSTot); se algum item foi zerado (uso e consumo), a soma dos C170
        if any(x.get('zerado') or x.get('credito_sn') for x in itens170):
            sm = lambda k: R(sum(x[k] for x in itens170))
            t = {**t, 'vBC': sm('bc'), 'vICMS': sm('icms'), 'vBCST': sm('bcst'), 'vST': sm('st'), 'vIPI': sm('ipi'),
                 'vPIS': sm('pis'), 'vCOFINS': sm('cof')}
        c100 = ['C100', oper, emit, part, '55', sit, ser, str(n['numero']), n['chave'], dt8(n['dhemi']),
                dt8(n.get('dhsaient') or n['dhemi']), m(t.get('vNF')), n.get('ind_pag') if n.get('ind_pag') in ('0', '1') else '2',
                m(t.get('vDesc')), m(0), m(t.get('vProd')), IND_FRT.get(n.get('mod_frete') or '9', '9'), m(t.get('vFrete')),
                m(t.get('vSeg')), m(t.get('vOutro')), m(t.get('vBC')), m(t.get('vICMS')), m(t.get('vBCST')), m(t.get('vST')),
                m(t.get('vIPI')), m(t.get('vPIS')), m(t.get('vCOFINS')), m(0), m(0)]
        bloco = [c100]
        if c101:
            bloco.append(['C101', m(c101[0]), m(c101[1]), m(c101[2])])
        c190 = collections.OrderedDict()
        for k, x in enumerate(itens170, 1):
            if oper == '0':   # entrada: CST do IPI pela tabela de entrada (o valor do IPI segue o XML)
                x = {**x, 'cst_ipi': cst_ipi_entrada(x['cst_ipi'], x['ipi'])}
            bloco.append(['C170', str(k), x['cod'], '', m(x['qtd'], 5), x['un'], m(x['vprod']), m(x['vdesc']), '0', x['cst'], x['cfop'],
                          x['nat'], m(x['bc']), m(x['aliq']), m(x['icms']), m(x['bcst']), m(x['aliqst']), m(x['st']), '0',
                          x['cst_ipi'], x['enq'] if x['cst_ipi'] else '',
                          *(([m(x['bcipi']), m(x['aliqipi']), m(x['ipi'])]) if x['cst_ipi'] else ['', '', '']),
                          x['cst_pis'], m(x['bcpis']), m(x['ppis'], 4), '', '', m(x['pis']),
                          x['cst_cof'], m(x['bccof']), m(x['pcof'], 4), '', '', m(x['cof']), x['cta'], m(0)])
            g = c190.setdefault((x['cst'], x['cfop'], R(x['aliq'])), collections.Counter())
            for kk in ('vc', 'bc', 'icms', 'bcst', 'st', 'ipi'):
                g[kk] += x[kk]
        for (cst, cf, al), g in c190.items():
            bloco.append(['C190', cst, cf, m(al), m(g['vc']), m(g['bc']), m(g['icms']), m(g['bcst']), m(g['st']), m(0), m(g['ipi']), ''])
        self.c.append(bloco)

    def entradas(self, cred, contas):
        cfg = self.a.cfg
        acum = cfg.get('acumuladores_entrada', {})
        por_nota = collections.defaultdict(list)
        for l in cred.linhas:
            por_nota[l['nota']['chave']].append(l)
        for n in sorted(self.a.entradas, key=lambda n: (n['dhemi'], n['numero'])):
            propria = n['emit_cnpj'] == self.a.cnpj
            part = self.participante(n['dest_cnpj'] if propria else n['emit_cnpj'], n['dest_end'] if propria else n['emit_end'],
                                     n['dest_nome'] if propria else n['emit_nome'])
            linhas = por_nota.get(n['chave'], [])
            sem = [l['cfop_ent'] for l in linhas if not (acum.get(l['cfop_ent']) or {}).get('codigo')]
            if sem:
                self.pend.append(('NF-e', n['numero'], n['emit_nome'], f'CFOP de entrada {", ".join(sorted(set(sem)))} sem acumulador no Domínio'))
                continue
            itens = []
            for l in linhas:
                i, cf = l['item'], l['cfop_ent']
                ac = acum[cf]
                tipo = {'insumo': '01', 'uso': '07', 'ativo': '08'}.get(l['natureza'], '99')
                cod, un = self.item('F', n['emit_cnpj'], i, tipo)
                x = {**_xml(i), 'cod': cod, 'un': un, 'cst': _cst(i), 'cfop': cf,
                     'nat': self.natureza(ac['codigo'], ac.get('descricao')),
                     'cta': contas.get((n['chave'], cf), ''), 'vc': R(l['vc'])}
                if l['natureza'] in SEM_CREDITO:
                    x = _zerar(x)
                elif _credito_sn(i, l):
                    x = _simples(x, i)
                itens.append(x)
            self._c100('0', '0' if propria else '1', part, n, '00', itens)
        self.entradas_canceladas()

    def entradas_canceladas(self, chaves=None):
        acum = self.a.cfg.get('acumuladores_entrada', {})
        for n in self.a.canceladas:
            if not n.get('propria') and (chaves is None or n['chave'] in chaves):
                part = self.participante(n['emit_cnpj'], n.get('emit_end'), n['emit_nome'])
                itens = []
                for i in n['itens']:
                    cf = cfop_entrada(i['cfop'])
                    ac = acum.get(cf) or {}
                    cod, un = self.item('F', n['emit_cnpj'], i, '99')
                    itens.append({'cod': cod, 'un': un, 'qtd': i['qtd'], 'cst': _cst(i), 'cfop': cf,
                                  'nat': self.natureza(ac.get('codigo'), ac.get('descricao')), 'cta': ''})
                self._c100('0', '1', part, n, '02', itens)

    def saidas(self):
        cfg = self.a.cfg
        for n in sorted(self.a.saidas, key=lambda n: (n['dhsaient'] or n['dhemi'], n['numero'])):
            part = self.participante(n['dest_cnpj'], n['dest_end'], n['dest_nome'])
            cosmeticon = 'COSMETICON' in (n['dest_nome'] or '').upper()
            itens = []
            for i in n['itens']:
                cf = i['cfop']
                cod_ac, ac = self.a.acum_por_cfop.get(cf, (None, None))
                if cosmeticon and cf in ('5101', '5102', '5401'):
                    cod_ac = '205' if cf == '5401' else '204'
                    ac = cfg['acumuladores_saida'].get(cod_ac)
                if not cod_ac:
                    self.pend.append(('NF-e saída', n['numero'], n['dest_nome'], f'CFOP {cf} sem acumulador'))
                cod, un = self.item('K', self.a.cnpj, i, '04')
                itens.append({**_xml(i), 'cod': cod, 'un': un, 'cst': _cst(i), 'cfop': cf,
                              'nat': self.natureza(cod_ac, (ac or {}).get('descricao')), 'cta': ''})
            t = n['tot']
            c101 = (t.get('vFCPUFDest'), t.get('vICMSUFDest'), t.get('vICMSUFRemet')) if (t.get('vICMSUFDest') or t.get('vFCPUFDest')) else None
            self._c100('1', '0', part, n, '00', itens, c101)
        for n in self.a.canceladas:
            if n.get('propria'):
                self._c100('1', '0', '', n, '02', [])
        for x in self.a.f.get('inut', []):
            for num in range(x['ini'], x['fim'] + 1):
                self._c100('1', '0', '', {'serie': x['serie'], 'numero': num, 'dhemi': x.get('data')}, '05', [])

    # ------------------------------------------------------------ D100/D190
    def ctes(self, cte_xml, cte_sieg, cred):
        acum = self.a.cfg.get('acumuladores_entrada', {})
        rs = dict(cte_sieg or {})
        credito = {c.get('chave'): c for c in cred.cte}
        for ch, x in sorted((cte_xml or {}).items(), key=lambda kv: (kv[1]['data'], kv[1]['numero'])):
            if x['toma_cnpj'] != self.a.cnpj:
                continue
            canc = (ch in rs and not rs[ch]['autorizada']) or not x.get('autorizada', True)
            ser = x['serie'] or ''
            if canc:
                self.d.append([['D100', '0', '1', '', '57', '02', ser, '', str(x['numero']), ch] + [''] * 15])
                continue
            part = self.participante(x['emit_cnpj'], x.get('emit_end'), x['emit_nome'])
            cf = {'5': '1', '6': '2'}.get(x['cfop'][:1], x['cfop'][:1]) + x['cfop'][1:]
            bc, icms = R(x['vbc']), R(x['vicms'])     # exatamente do XML do CT-e
            sem_credito = ch in credito and not credito[ch].get('credito') and icms
            if sem_credito:                           # frete de compra fora da atividade-fim: base e ICMS zerados
                bc = icms = 0.0
            ac = acum.get(cf) or {}
            conta = (ac.get('conta') or {}).get('debito', '') if isinstance(ac.get('conta'), dict) else ''
            cst = '0' + (x.get('cst') or '00')[-2:]
            self.d.append([['D100', '0', '1', part, '57', '00', ser, '', str(x['numero']), ch, dt8(x['data']), dt8(x['data']), '0', '',
                            m(x['vprest']), m(0), '1', m(x['vprest']), m(bc), m(icms), m(0 if bc else x['vprest']), '', conta,
                            x.get('cmun_ini') or '', x.get('cmun_fim') or ''],
                           ['D190', cst, cf, m(0 if sem_credito else x['picms']), m(x['vprest']), m(bc), m(icms), m(0), '']])
        for ch, r in rs.items():
            if r['toma_cnpj'] == self.a.cnpj and ch not in (cte_xml or {}):
                self.pend.append(('CT-e', r['numero'], r['emit_nome'],
                                  'sem XML na pasta - fica fora do arquivo (pedir o XML)' if r['autorizada'] else 'cancelado e sem XML na pasta'))

    # ------------------------------------------------------------ arquivo
    def gerar(self, destino, cab):
        a = self.a
        ini, fim = a.ini.strftime('%d%m%Y'), a.fim.strftime('%d%m%Y')
        L = []
        add = lambda campos: L.append('|' + '|'.join(str(c if c is not None else '') for c in campos) + '|')
        e = cab['0000']
        add(['0000', '020', '0', ini, fim, e['nome'], e['cnpj'], '', e['uf'], e['ie'], e['cod_mun'], '', '', 'A', '0'])
        add(['0001', '0'])
        add(['0002', cab.get('0002', '09')])
        L.append(cab['0005'])
        L.append(cab['0100'])
        for p in sorted(self.part.values(), key=lambda x: x[2]):
            add(p)
        for u in sorted(self.unid):
            add(['0190', u, u])
        for it in self.itens.values():
            add(it)
        for n in sorted(self.nat.values(), key=lambda x: int(x[1])):
            add(n)
        add(['0990', f'{len(L) + 1:09d}'])
        add(['B001', '1']); add(['B990', '000000002'])
        n0 = len(L)
        add(['C001', '0' if self.c else '1'])
        for bloco in self.c:
            for reg in (bloco if isinstance(bloco[0], list) else [bloco]):
                add(reg)
        add(['C990', f'{len(L) - n0 + 1:09d}'])
        n0 = len(L)
        add(['D001', '0' if self.d else '1'])
        for bloco in self.d:
            for reg in bloco:
                add(reg)
        add(['D990', f'{len(L) - n0 + 1:09d}'])
        n0 = len(L)
        add(['E001', '0']); add(['E100', ini, fim])
        for reg in self.e:
            add(reg)
        add(['E990', f'{len(L) - n0 + 1:09d}'])
        for b in ('G', 'H', 'K'):
            add([f'{b}001', '1']); add([f'{b}990', '000000002'])
        add(['1001', '0']); add(['1010'] + ['N'] * 13); add(['1990', '000000003'])
        cont = collections.Counter(x.split('|')[1] for x in L)
        add(['9001', '0'])
        regs = list(dict.fromkeys(x.split('|')[1] for x in L))
        n9900 = len(regs) + 3
        for r in regs:
            add(['9900', r, f'{cont.get(r, 0) + (1 if r == "9001" else 0):09d}'])
        add(['9900', '9900', f'{n9900:09d}']); add(['9900', '9990', '000000001']); add(['9900', '9999', '000000001'])
        add(['9990', f'{n9900 + 3:09d}'])
        add(['9999', f'{len(L) + 1:09d}'])
        with open(destino, 'w', encoding='cp1252', errors='replace', newline='\r\n') as fh:
            fh.write('\n'.join(L) + '\n')
        return L


def _e113(n, valor):
    ser = str(int(n['serie'])) if str(n.get('serie') or '').isdigit() else (n.get('serie') or '')
    return ['E113', re.sub(r'\D', '', n['emit_cnpj']), '55', ser, '', str(n['numero']), dt8(n['dhemi']), '', m(valor), n['chave']]


def ajustes_apuracao(a, cred, sped=None):
    """Bloco E do TXT (regra da usuária, igual ao SPED que o Domínio gerou em 07 e 08/2026):
    - DIFAL do uso e consumo/ativo de outra UF: E111 PR000081 (débito) + E113 por nota;
    - ICMS antecipado de importado a 4%: 8% sobre o valor do produto (= a base do ICMS da nota): E111 PR000080 (débito)
      e PR020212 (crédito do mesmo valor - saldo zero) + E113 por nota;
    - E110 com a apuração do mês (débitos das saídas, créditos das entradas e CT-e, ajustes, saldo e ICMS a recolher)."""
    difal, antec = collections.OrderedDict(), collections.OrderedDict()
    for l in cred.linhas:
        n = l['nota']
        if l.get('difal'):
            difal[n['chave']] = (n, R((difal.get(n['chave']) or (n, 0))[1] + l['difal']))
        if l.get('antecipado'):
            antec[n['chave']] = (n, R((antec.get(n['chave']) or (n, 0))[1] + l['antecipado']))
    td, ta = R(sum(v for _, v in difal.values())), R(sum(v for _, v in antec.values()))
    ic = a.ic
    aj_deb, aj_cred = R(td + ta), ta
    deb, cre = ic['debitos'], ic['creditos']
    if sped is not None:   # débitos e créditos = o que está nas próprias notas do arquivo (C190 / D190), para fechar com o TXT
        num = lambda v: float(v.replace(',', '.')) if v else 0.0
        c190 = [r for b in sped.c for r in (b if isinstance(b[0], list) else [b]) if r[0] == 'C190']
        deb = R(sum(num(r[6]) for r in c190 if r[2][:1] in '567'))
        cre = R(sum(num(r[6]) for r in c190 if r[2][:1] in '123') + sum(num(r[6]) for b in sped.d for r in b if r[0] == 'D190'))
    saldo = R(deb + aj_deb - cre - aj_cred - ic.get('saldo_credor_anterior', 0.0))
    regs = [['E110', m(deb), m(0), m(aj_deb), m(0), m(cre), m(0), m(aj_cred), m(0), m(ic.get('saldo_credor_anterior', 0.0)),
             m(max(saldo, 0)), m(0), m(max(saldo, 0)), m(max(-saldo, 0)), m(0)]]
    if td:
        regs.append(['E111', 'PR000081', '', m(td)])
        regs += [_e113(n, v) for n, v in difal.values()]
    if ta:
        regs.append(['E111', 'PR000080', '', m(ta)])
        regs += [_e113(n, v) for n, v in antec.values()]
        regs.append(['E111', 'PR020212', '', m(ta)])
        regs += [_e113(n, v) for n, v in antec.values()]
    return regs


def gerar_somente_canceladas(a, chaves, cab, destino):
    """TXT só com notas de entrada canceladas pelo fornecedor (para reimportar sem duplicar o resto do mês)."""
    s = Sped(a)
    s.entradas_canceladas(set(chaves))
    return s, s.gerar(destino, cab)


def gerar(a, cred, cte_xml, cte_sieg, contas, cab, destino):
    s = Sped(a)
    s.entradas(cred, contas)
    s.saidas()
    s.ctes(cte_xml, cte_sieg, cred)
    if getattr(a, 'ic', None) and a.cfg.get('sped_importacao_ajustes', True):
        s.e = ajustes_apuracao(a, cred, s)
    linhas = s.gerar(destino, cab)
    return s, linhas


def auditar(linhas, a, cte_xml=None, cred=None):
    """Confere o TXT gerado contra o XML, campo a campo: cada C170 com o item do XML (CST, base, alíquota e valor de ICMS, ST, IPI,
    PIS e COFINS, quantidade, valor, desconto), cada C100 com os totais do XML e cada D100 com o XML do CT-e.
    Devolve (documentos conferidos, itens conferidos, lista de diferenças)."""
    num = lambda x: float(x.replace(',', '.')) if x else 0.0
    notas = {n['chave']: n for n in a.entradas + a.saidas}
    nat = {}
    for l in (cred.linhas if cred else []):
        nat.setdefault(l['nota']['chave'], []).append(l['natureza'])
    zeros = {'vbc': 0, 'picms': 0, 'vicms': 0, 'vbcst': 0, 'picmsst': 0, 'vst': 0, 'vbc_ipi': 0, 'pipi': 0, 'vipi': 0,
             'vbc_pis': 0, 'ppis': 0, 'vpis': 0, 'vbc_cof': 0, 'pcof': 0, 'vcof': 0, 'cst_ipi': '', 'cst_pis': '98', 'cst_cof': '98'}
    dif, docs, itens = [], 0, 0
    atual, k = None, 0
    tot_c100 = [(11, 'vNF'), (13, 'vDesc'), (15, 'vProd'), (17, 'vFrete'), (18, 'vSeg'), (19, 'vOutro'), (20, 'vBC'), (21, 'vICMS'),
                (22, 'vBCST'), (23, 'vST'), (24, 'vIPI'), (25, 'vPIS'), (26, 'vCOFINS')]
    campos = [(4, 'qtd'), (6, 'vprod'), (7, 'vdesc'), (12, 'vbc'), (13, 'picms'), (14, 'vicms'), (15, 'vbcst'), (16, 'picmsst'), (17, 'vst'),
              (21, 'vbc_ipi'), (22, 'pipi'), (23, 'vipi'), (25, 'vbc_pis'), (26, 'ppis'), (29, 'vpis'), (31, 'vbc_cof'), (32, 'pcof'), (35, 'vcof')]
    for l in linhas:
        p = l.split('|')[1:-1]
        if p[0] == 'C100':
            atual, k, entrada = notas.get(p[8]), 0, p[1] == '0'
            if atual and p[5] == '00':
                docs += 1
                if 'uso' in nat.get(atual['chave'], []) or any(i.get('csosn') in ('101', '201', '900') and i.get('vcredsn') for i in atual['itens']):
                    continue   # totais = soma dos itens (conferidos item a item)
                for pos, chave in tot_c100:
                    if abs(num(p[pos]) - (atual['tot'].get(chave) or 0.0)) > 0.005:
                        dif.append(f'NF {p[7]} C100 {chave}: TXT {p[pos]} x XML {atual["tot"].get(chave)}')
        elif p[0] == 'C170' and atual:
            i = atual['itens'][k]
            if k < len(nat.get(atual['chave'], [])) and nat[atual['chave']][k] in SEM_CREDITO:
                i = {**i, **zeros}
            elif k < len(nat.get(atual['chave'], [])) and _credito_sn(i, {'natureza': nat[atual['chave']][k]}):
                i = {**i, 'vbc': R(i['vprod'] - i['vdesc']), 'picms': i['pcredsn'], 'vicms': i['vcredsn']}
            k += 1
            itens += 1
            for pos, chave in campos:
                if abs(num(p[pos]) - (i.get(chave) or 0.0)) > 0.00001:
                    dif.append(f'NF {atual["numero"]} item {k} {chave}: TXT {p[pos]} x XML {i.get(chave)}')
            cst_xml = i.get('csosn') or f'{i.get("orig") or "0"}{(i.get("cst_icms") or "00")[-2:]}'
            for pos, v in ((9, cst_xml), (19, cst_ipi_entrada(i.get('cst_ipi'), i.get('vipi')) if entrada else (i.get('cst_ipi') or '')), (24, i.get('cst_pis') or ''), (30, i.get('cst_cof') or '')):
                if p[pos] != v:
                    dif.append(f'NF {atual["numero"]} item {k} CST: TXT {p[pos]} x XML {v}')
        elif p[0] == 'D100' and p[5] == '00':
            x = (cte_xml or {}).get(p[9])
            if x and cred and any(c.get('chave') == p[9] and not c.get('credito') for c in cred.cte) and x.get('vicms'):
                x = {**x, 'vbc': 0.0, 'vicms': 0.0}
            docs += 1
            for pos, chave in ((14, 'vprest'), (18, 'vbc'), (19, 'vicms')):
                if x and abs(num(p[pos]) - (x.get(chave) or 0.0)) > 0.005:
                    dif.append(f'CT-e {p[8]} {chave}: TXT {p[pos]} x XML {x.get(chave)}')
    return docs, itens, dif
