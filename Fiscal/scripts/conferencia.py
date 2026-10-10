"""Conferência fiscal mensal: lê os XML das notas item a item, sugere CFOP de
entrada e acumulador conforme as regras da empresa e compara com o que foi
escriturado no SPED Fiscal (gabarito final) e nos relatórios de acompanhamento
do Domínio (retrato da importação, antes das correções manuais).

Modo pré-importação (mês ainda aberto, sem SPED): basta não informar --sped e
os relatórios do mês. O robô classifica cada item para lançar, confere as notas
próprias e a completude com a lista da SEFAZ, e usa --historico (relatório de
Acompanhamento do Domínio de meses anteriores, em PDF ou Excel) para mostrar
como cada fornecedor costuma ser lançado e se a nota já foi lançada antes.

Uso:
  python3 conferencia.py --regras <regras.json> --xml <pasta com XML extraídos>
      --sped <SPED.txt> --dom-entradas <xlsx> --dom-saidas <xlsx>
      [--sefaz <xlsx> --sefaz-aba <aba>] [--nfse-recebidas <xlsx> --dom-servicos <xls>]
      [--erp-notas <xlsx> --erp-aba <aba>] --competencia 2026-08 --saida <arquivo.xlsx>
  pré-importação:
  python3 conferencia.py --regras <regras.json> --xml <pasta> --sefaz <lista NF-e.xlsx> <lista CT-e.xlsx>
      --historico <Entradas jan-ago.pdf> [--nfse-recebidas <xlsx>] [--erp-notas <xlsx>]
      --competencia 2026-09 --saida <arquivo.xlsx>
"""
import argparse
import glob
import json
import os
import re
import sys
import unicodedata
from collections import Counter, defaultdict
from decimal import Decimal

import pandas as pd

sys.path.insert(0, os.path.dirname(__file__))
from dominio_pdf import parse_acompanhamento_pdf, parse_resumo_acumuladores  # noqa: E402
from dominio_relatorios import parse_acompanhamento  # noqa: E402
from nfe_xml import is_nfe_xml, parse_nfe  # noqa: E402
from sped_efd import parse_sped  # noqa: E402

Z = Decimal('0')
CENT = Decimal('0.01')
COMPRA = {'101', '102', '103', '104', '105', '106', '107', '108', '109', '110', '111', '116', '117',
          '118', '120', '122', '401', '402', '403', '404', '405', '251', '252', '253', '254', '255',
          '256', '257'}
COMPRA_ST = {'401', '402', '403', '404', '405'}
CST_ST = {'10', '30', '60', '70', '201', '202', '203', '500'}
CST_ISENTA = {'30', '40'}       # coluna "Isentas" do Domínio (CST 41 vai em Outras)
CST_EXIGE_CBENEF = {'20', '30', '40', '41', '50', '51', '53', '70', '90'}
REGIME = {'1': 'Simples', '2': 'Simples (excesso)', '3': 'Normal', '4': 'MEI'}


def q(v):
    return Decimal(v).quantize(CENT)


# ---------------------------------------------------------------- regras
class Regras:
    def __init__(self, path):
        self.r = json.load(open(path, encoding='utf-8'))
        self.cnpj = self.r['empresa']['cnpj']
        self.uf = self.r['empresa']['uf']
        self.ncm = sorted(self.r['finalidade_por_ncm'], key=lambda x: -len(x['prefixo']))
        self.vendas = defaultdict(Counter)    # 1ª palavra do item vendido -> Counter(sufixo do CFOP)
        self.catalogo = dict(self.r['acumuladores'])

    def carregar_catalogo(self, path):
        cat = parse_resumo_acumuladores(path)
        self.catalogo.update(cat)
        for k, v in cat.items():
            self.r['acumuladores'].setdefault(k, v)

    def aprender_vendas(self, notas):
        """Perfil de venda da empresa: como ela fatura cada tipo de item (produção x revenda)."""
        for n in notas:
            if n['emit_cnpj'] == self.cnpj and n['tpNF'] == '1' and not n['cancelada']:
                for it in n['itens']:
                    if it['CFOP'][1:] in ('101', '102'):
                        self.vendas[palavra(it['xProd'])][it['CFOP'][1:]] += 1

    def perfil_venda(self, item):
        cfg = self.r.get('perfil_venda')
        if not cfg or item['NCM'][:2] not in cfg['capitulos']:
            return None
        c = self.vendas.get(palavra(item['xProd']))
        tot = sum(c.values()) if c else 0
        if tot < cfg['minimo_saidas']:
            return None
        for suf, fin, txt in (('102', 'REVENDA', 'revenda (x102)'), ('101', 'INSUMO', 'produção própria (x101)')):
            if c[suf] / tot >= cfg['proporcao']:
                return fin, (f'A Kopp vende "{palavra(item["xProd"])}" como {txt} em {c[suf]} de {tot} saídas '
                             'com CFOP de venda: o item comprado segue a mesma natureza')
        return None

    def ac_nome(self, ac):
        return self.r['acumuladores'].get(str(ac), '') if ac else ''

    def finalidade(self, nota, item):
        for rg in self.r.get('finalidade_por_item', []):
            if rg['cnpj'] == nota['emit_cnpj'] and item['NCM'].startswith(rg.get('ncm', '')) \
                    and rg.get('cProd', item['cProd']) == item['cProd']:
                self._ultima = rg
                return rg['finalidade'], rg['motivo'], 'item'
        for rg in self.r.get('finalidade_por_descricao', []):
            if rg['contem'].upper() in item['xProd'].upper() and rg['finalidade'] == 'SEGUE_NOTA':
                # ex.: taxa de entrega cobrada como item -> mesma finalidade dos demais itens
                outros = [i for i in nota['itens'] if rg['contem'].upper() not in i['xProd'].upper()]
                if outros:
                    fin, _, origem = self.finalidade(nota, outros[0])
                    return fin, f'{rg["motivo"]} ({fin.lower()})', origem
                continue
            if rg['contem'].upper() in item['xProd'].upper():
                self._ultima = rg
                return rg['finalidade'], rg['motivo'], 'descrição'
        f = self.r['finalidade_por_fornecedor'].get(nota['emit_cnpj'])
        if f:
            self._ultima = f
            return f['finalidade'], f['motivo'], 'fornecedor'
        for rg in self.ncm:
            if item['NCM'].startswith(rg['prefixo']):
                self._ultima = rg
                return rg['finalidade'], rg['motivo'], 'NCM'
        self._ultima = {}
        return 'PENDENTE', 'Sem regra para este fornecedor/NCM', '-'

    def conta(self, nota, item, finalidade):
        """Conta contábil de débito sugerida e de onde ela veio."""
        import re
        rg = getattr(self, '_ultima', {}) or {}
        if rg.get('conta'):
            return rg['conta'], 'regra'
        if finalidade == 'USO_CONSUMO' and any(item['NCM'].startswith(p) for p in self.r.get('conta_por_ncm_limpeza', [])):
            return '360 3.2.2.04.007 MATERIAL DE HIGIENE E LIMPEZA', 'NCM (limpeza)'
        chave = re.sub(r'[^A-Z ]', '', nota['emit_nome'].upper())[:12]
        hist = self.r.get('conta_por_fornecedor_razao', {})
        if chave in hist and finalidade in ('USO_CONSUMO', 'INSUMO', 'EMBALAGEM', 'FERRAMENTA', 'ATIVO'):
            estoque = ' 1.1.5.' in hist[chave]
            if estoque == (finalidade in ('INSUMO', 'EMBALAGEM', 'FERRAMENTA')):
                return hist[chave], 'razão 4T2025'
            padrao = self.r.get('contas_padrao', {}).get(finalidade, '')
            return padrao, f'padrão da finalidade (no razão 4T2025 ia para {hist[chave]})'
        if finalidade in self.r.get('contas_padrao', {}):
            return self.r['contas_padrao'][finalidade], 'padrão da finalidade'
        return '', ''

    def ignorar(self, nota):
        for rg in self.r.get('ignorar_documentos', []):
            if rg['cnpj_emitente'] == nota['emit_cnpj'] and rg.get('tpNF', nota['tpNF']) == nota['tpNF']:
                return rg['motivo']
        return None

    def classificar_entrada(self, nota, item):
        """Finalidade, CFOP/acumulador sugeridos e créditos de um item de compra."""
        suf = item['CFOP'][1:]
        escopo = 'interna' if nota['emit_uf'] == self.uf else 'interestadual'
        icms_item = item['vICMS'] + item['vCredICMSSN']   # CSOSN 101 dá crédito pelo pCredSN
        out = {'escopo': escopo, 'alertas': [], 'difal': Z}
        if suf in self.r['outras_operacoes']:
            op = self.r['outras_operacoes'][suf]
            m = op.get(escopo) or {}
            credita = suf in ('124', '125')   # industrialização por encomenda: custo de produção
            fin_910 = None
            if suf == '910':                   # bonificação de insumo/embalagem com destaque gera crédito
                fin_910 = self.finalidade(nota, item)[0]
                credita = fin_910 in ('INSUMO', 'EMBALAGEM', 'FERRAMENTA', 'REVENDA')
            out.update(finalidade='OUTRA OPERAÇÃO', motivo=op['descr'], origem_regra='CFOP fornecedor',
                       cfop=m.get('cfop', ''), ac=m.get('ac'),
                       cred_icms=icms_item if credita else Z, cred_ipi=item['vIPI'] if credita else Z)
            if not m.get('ac'):
                out['alertas'].append(f'Sem acumulador cadastrado para CFOP {m.get("cfop")}')
            if fin_910 and fin_910 != 'PENDENTE':
                out['conta'], out['origem_conta'] = self.conta(nota, item, fin_910)
            return out
        if suf not in COMPRA:
            out.update(finalidade='PENDENTE', motivo=f'CFOP do fornecedor {item["CFOP"]} sem regra',
                       origem_regra='-', cfop='', ac=None, cred_icms=Z, cred_ipi=Z)
            return out
        fin, motivo, origem = self.finalidade(nota, item)
        if origem in ('fornecedor', 'NCM', '-'):
            pv = self.perfil_venda(item)
            if pv and pv[0] != fin:
                fin, motivo, origem = pv[0], pv[1], 'perfil de venda'
                self._ultima = {}
        tem_st = suf in COMPRA_ST or item['CST_ICMS'] in CST_ST
        out.update(finalidade=fin, motivo=motivo, origem_regra=origem)
        out['conta'], out['origem_conta'] = self.conta(nota, item, fin)
        if fin == 'PENDENTE':
            out.update(cfop='', ac=None, cred_icms=Z, cred_ipi=Z)
            return out
        tab = self.r['compras_com_st'] if tem_st and fin in self.r['compras_com_st'] else self.r['compras']
        m = tab[fin].get(escopo) or {}
        regra = self.r['compras'][fin]
        out['cfop'], out['ac'] = m.get('cfop', ''), m.get('ac')
        if not out['ac']:
            out['alertas'].append(f'Sem acumulador cadastrado para {fin} {escopo} (CFOP {out["cfop"]})')
        out['cred_icms'] = icms_item if regra.get('credito_icms') is True else Z
        out['cred_ipi'] = item['vIPI'] if regra.get('credito_ipi') else Z
        if regra.get('alerta'):
            out['alertas'].append(regra['alerta'])
        if regra.get('difal') and escopo == 'interestadual':
            out['difal'] = self.difal_base_dupla(item)
        return out

    def difal_base_dupla(self, item):
        """DIFAL de uso e consumo/ativo por base dupla (PR): tira o ICMS da origem,
        põe o ICMS interno "por dentro" e desconta o ICMS da origem."""
        inter = item['pICMS'] or (Decimal('4') if item['orig'] in ('1', '2', '3', '8') else Decimal('12'))
        aliq = Decimal(str(self.r['empresa']['aliq_interna_icms']))
        if aliq <= inter:
            return Z
        valor = item['vProd'] + item['vFrete'] + item['vSeg'] + item['vOutro'] - item['vDesc'] + item['vIPI']
        icms_origem = item['vICMS'] if item['vICMS'] else valor * inter / 100
        base = (valor - icms_origem) / (1 - aliq / 100)
        return q(base * aliq / 100 - icms_origem)


# ---------------------------------------------------------------- carga
def carregar_xmls(pasta):
    notas, origem, erros = {}, defaultdict(set), []
    arquivos = [f for f in glob.glob(os.path.join(pasta, '**', '*'), recursive=True)
                if f.lower().endswith('.xml')]
    for f in sorted(arquivos):
        if not is_nfe_xml(f):
            continue
        n = parse_nfe(f)
        if 'erro' in n:
            erros.append(n)
            continue
        if not n.get('chave') or not n.get('numero'):
            continue                   # evento/documento que não é NF-e completa (ex.: cancelamento de CT-e)
        origem[n['chave']].add(os.path.relpath(f, pasta).split(os.sep)[0])
        atual = notas.get(n['chave'])
        if atual is None or (n['eventos'] and not atual['eventos']):
            notas[n['chave']] = n      # prefere a versão que traz eventos (cancelamento)
    return notas, origem, erros


def palavra(txt):
    t = unicodedata.normalize('NFKD', str(txt).upper()).encode('ascii', 'ignore').decode()
    m = re.search(r'[A-Z]{3,}', t)
    return m.group(0) if m else ''


def item_lc116(cod):
    """'171401 - Advocacia' -> (17, 14)."""
    m = re.match(r'\s*(\d{2})(\d{2})', str(cod))
    return (int(m.group(1)), int(m.group(2))) if m else None


def classificar_servico(R, r, cnpj, hist_cont):
    """Acumulador, natureza e conta de uma NFS-e tomada, a partir do item da LC 116 e das retenções."""
    cfg = R.r.get('servicos', {})
    item = item_lc116(r.get('Cód. Tributação Nacional'))
    num = lambda c: Decimal(str(r.get(c) or 0)) if not pd.isna(r.get(c)) else Z
    ir, cs, inss = num('IRRF (R$)'), num('Contrib. Sociais Ret. (R$)'), num('Contrib. Previd. Ret. (R$)')
    iss_ret = 'Não Retido' not in str(r.get('Retenção ISSQN', 'Não Retido'))
    out = {'item': f'{item[0]:02d}.{item[1]:02d}' if item else '', 'alertas': [], 'ac': '', 'ac_nome': ''}
    iss_val = num('Valor do ISSQN (R$)') if iss_ret else Z
    out['valores'] = {'IRRF': q(ir), 'CSRF': q(cs), 'INSS': q(inss), 'ISS': q(iss_val)}
    out['ret'] = ', '.join(x for x, v in (('IRRF', ir), ('CSRF', cs), ('INSS', inss), ('ISS', iss_ret)) if v) or 'nenhuma'
    nat = cfg.get('natureza_por_item', {})
    n = nat.get(out['item']) or nat.get(out['item'][:2]) or {}
    out['natureza'] = n.get('natureza', str(r.get('Cód. Tributação Nacional', ''))[9:70])
    # acumulador pelo catálogo: "SERVIÇOS TOMADOS 17.09 - IRRF/CSRL"
    cand = []
    for cod, nome in R.catalogo.items():
        m = re.search(r'S\w+ TO\w+\s+(\d+)\.(\d+)(.*)$', nome)
        if item and m and (int(m.group(1)), int(m.group(2))) == item:
            suf = m.group(3).upper()
            ok = (('IRRF' in suf) == bool(ir), ('CSR' in suf) == bool(cs), ('ISS' in suf) == iss_ret)
            cand.append((sum(ok), all(ok[:2]), hist_cont.get(cod, 0), cod, nome))
    cand.sort(reverse=True)
    # regra do escritório: o item da LC 116 na descrição do acumulador decide; as retenções só
    # escolhem entre acumuladores do mesmo item (ex.: 17.01, 17.01 - IRRF, 17.01 - IRRF/CSRL)
    if cand:
        out['ac'], out['ac_nome'] = cand[0][3], cand[0][4]
        if not cand[0][1]:
            out['alertas'].append(f'Retenções da nota ({out["ret"]}) não constam no acumulador {cand[0][3]} '
                                  f'({cand[0][4]}): conferir a retenção ou criar o acumulador do item com ela')
    elif item:
        out['alertas'].append(f'Não há acumulador para o item {out["item"]} da LC 116 no Domínio: criar')
    # retenção esperada (prestador fora do Simples)
    simples = str(r.get('Simples Nacional', ''))
    esp = cfg.get('retencao_esperada', {}).get(out['item'])
    vs = Decimal(str(r.get('Valor do Serviço (R$)') or 0))
    dispensa = cfg.get('retencao_dispensada', {}).get(cnpj)
    if dispensa:
        out['natureza'] += ' — retenção: ' + dispensa
    elif esp and 'Não Optante' in simples:
        falta = []
        if 'IRRF' in esp and not ir and vs * Decimal('0.015') > 10:
            falta.append(f'IRRF 1,5% ≈ {q(vs * Decimal("0.015"))}')
        if 'CSRF' in esp and not cs and vs * Decimal('0.0465') > 10:
            falta.append(f'CSRF 4,65% ≈ {q(vs * Decimal("0.0465"))}')
        if falta:
            out['alertas'].append(f'Prestador não optante do Simples, serviço {out["item"]}, falta retenção: '
                                  f'confirmar {" e ".join(falta)}' + (' (enquadramento a confirmar)' if 'confirmar' in esp else ''))
    # conta contábil
    chave = re.sub(r'[^A-Z ]', '', unicodedata.normalize('NFKD', str(r.get('Nome Prestador', '')).upper())
                   .encode('ascii', 'ignore').decode()).strip()[:20]
    razao = cfg.get('conta_por_prestador_razao', {}).get(chave)
    if n.get('conta'):
        out['conta'], out['origem_conta'] = n['conta'], 'natureza do serviço'
        if razao and razao.split()[0] != n['conta'].split()[0]:
            out['alertas'].append(f'No razão 2025 este prestador foi para {razao}; pela natureza do serviço o certo é {n["conta"]}')
    elif razao:
        out['conta'], out['origem_conta'] = razao, 'razão 4T2025'
    else:
        out['conta'], out['origem_conta'] = cfg.get('conta_padrao', ''), 'padrão de serviços'
    return out


def carregar_sefaz(paths, aba):
    out = {}
    for path in ([paths] if isinstance(paths, str) else paths):
        df = pd.read_excel(path, sheet_name=aba, header=None)
        hdr = next(i for i, r in df.iterrows() if 'CHAVE DA NOTA' in [str(v).strip() for v in r.values])
        df.columns = [str(c).strip() for c in df.iloc[hdr]]
        df = df.iloc[hdr + 1:].dropna(subset=['CHAVE DA NOTA'])
        out.update({str(r['CHAVE DA NOTA']).strip(): r for _, r in df.iterrows()})
    return out


def carregar_historico(paths):
    """Lançamentos de meses anteriores no Domínio (PDF ou Excel do Acompanhamento).
    Devolve {cnpj: Counter((espécie, cfop, acumulador))} e o conjunto (cnpj, nota)."""
    por_cnpj, lancadas, periodos = defaultdict(Counter), {}, []
    for path in paths or []:
        if path.lower().endswith('.pdf') or path.lower().endswith('.txt'):
            periodo, regs = parse_acompanhamento_pdf(path)
            periodos.append(periodo)
        else:
            regs = parse_acompanhamento(path, 0)
        for r in regs:
            cnpj = r.get('cnpj', '')
            if not cnpj:
                continue
            por_cnpj[cnpj][(r['especie'], r['cfop'], r['acumulador'])] += 1
            lancadas[(cnpj, r['nota'].lstrip('0'))] = r
    return por_cnpj, lancadas, periodos


def fmt_hist(cont, especies):
    itens = [(k, v) for k, v in cont.most_common() if k[0] in especies]
    return '; '.join(f'{cf}/ac {ac} ×{v}' for (_, cf, ac), v in itens)


def casar_dominio(dom, xmls_por_num):
    """Liga as linhas do relatório do Domínio ao XML. Uma nota com dois CFOPs
    vira duas linhas no relatório: agrupa por número antes de comparar o valor."""
    grupos = defaultdict(list)
    for d in dom:
        grupos[(d['nota'], d['serie'], d['participante'])].append(d)
    for (num, _, _), linhas in grupos.items():
        total = sum((d['valor_contabil'] for d in linhas), Z)
        best = None
        for n in xmls_por_num.get(num, []):
            dif = abs(n['t_vNF'] - total)
            if best is None or dif < best[0]:
                best = (dif, n)
        cand = xmls_por_num.get(num, [])
        if best and (best[0] <= Decimal('1.00') or len(cand) == 1):
            for d in linhas:
                d['chave'] = best[1]['chave']


def imposto(linhas, tipo, campo):
    return sum((l[campo] for d in linhas for l in d['impostos'].get(tipo, [])), Z)


def valor_item(it):
    return it['vProd'] + it['vFrete'] + it['vSeg'] + it['vOutro'] - it['vDesc'] + it['vIPI'] + it['vICMSST']


def colunas_dominio(itens):
    """Base/ICMS/Isentas/Outras como o Domínio distribui: tributado -> base e o
    restante (IPI, redução) em Outras; CST 30/40/41 -> Isentas; demais -> Outras."""
    base = icms = ise = outras = Z
    for it in itens:
        v = valor_item(it)
        if it['vBC_ICMS'] or it['vICMS']:
            base += it['vBC_ICMS']
            icms += it['vICMS']
            outras += v - it['vBC_ICMS']
        elif it['CST_ICMS'] in CST_ISENTA:
            ise += v
        else:
            outras += v
    return q(base), q(icms), q(ise), q(outras)


# ---------------------------------------------------------------- análise
def analisar(a):
    R = Regras(a.regras)
    K = R.cnpj
    comp = a.competencia
    notas, origem, erros = carregar_xmls(a.xml)
    pre = not a.sped          # mês aberto: ainda não há SPED nem lançamento no Domínio
    sped = parse_sped(a.sped) if a.sped else {'docs': [], 'naturezas': {}, 'ajustes_e111': [],
                                               'participantes': {}, 'produtos': {}}
    dom_e = parse_acompanhamento(a.dom_entradas, a.dom_entradas_aba) if a.dom_entradas else []
    dom_s = parse_acompanhamento(a.dom_saidas, a.dom_saidas_aba) if a.dom_saidas else []
    sefaz = carregar_sefaz(a.sefaz, a.sefaz_aba) if a.sefaz else {}
    hist, ja_lancadas, periodos_hist = carregar_historico(a.historico)
    for cat in a.acumuladores or []:
        R.carregar_catalogo(cat)
    R.aprender_vendas(notas.values())
    chaves_arquivo = set()
    for f in glob.glob(os.path.join(a.xml, '**', '*.xml'), recursive=True):
        chaves_arquivo.update(re.findall(r'\d{44}', os.path.basename(f)))

    por_num = defaultdict(list)
    for n in notas.values():
        por_num[n['numero'].lstrip('0')].append(n)
    casar_dominio([d for d in dom_e if d['especie'] in ('36', '55')], por_num)
    casar_dominio([d for d in dom_s if d['especie'] in ('36', '55')], por_num)
    dom_por_chave = defaultdict(list)
    for d in dom_e + dom_s:
        if d.get('chave'):
            dom_por_chave[d['chave']].append(d)
    sped_por_chave = {d['chave']: d for d in sped['docs'] if d['chave']}
    nat = sped['naturezas']
    e113 = defaultdict(list)
    for aj in sped['ajustes_e111']:
        for doc in aj['docs']:
            if doc['chave']:
                e113[doc['chave']].append((aj['codigo'], aj['descr'], doc['valor']))

    itens_rows, notas_rows, pend, dev_rows, sai_rows = [], [], [], [], []

    def pendencia(gravidade, tipo, nota, msg, valor=None, participante=None):
        pend.append({'Gravidade': gravidade, 'Tipo': tipo,
                     'Nota': f"{nota['numero']}/{nota['serie']}" if isinstance(nota, dict) else str(nota or ''),
                     'Participante': participante if participante is not None else (
                         (nota['emit_nome'] if nota['emit_cnpj'] != K else nota['dest_nome'])
                         if isinstance(nota, dict) else ''),
                     'Valor': valor if valor is not None else (nota['t_vNF'] if isinstance(nota, dict) else None),
                     'O que fazer / por quê': msg,
                     'Chave': nota['chave'] if isinstance(nota, dict) else ''})

    # ======================== 1. entradas de terceiros (item a item)
    terceiros = [n for n in notas.values() if n['emit_cnpj'] != K and n['dest_cnpj'] == K]
    for n in sorted(terceiros, key=lambda x: (x['dt_emissao'], x['emit_nome'])):
        sp = sped_por_chave.get(n['chave'])
        dm = dom_por_chave.get(n['chave'], [])
        motivo_ign = R.ignorar(n)
        if motivo_ign:
            extra = ''
            if sp:
                extra = f' Está no SPED como C100 IND_OPER={sp["ind_oper"]} COD_SIT={sp["cod_sit"]}: confirmar se deve constar.'
            pendencia('INFO', 'Documento do fornecedor', n, motivo_ign + '.' + extra)
            continue
        canc_sefaz = 'CANCEL' in str(sefaz.get(n['chave'], {}).get('STATUS', '')).upper()
        if n['cancelada'] or canc_sefaz:
            quando = ', '.join(e['data'] for e in n['eventos'] if e['tp'] == '110111') or 'lista da SEFAZ'
            prot = ', '.join(e.get('prot', '') for e in n['eventos'] if e['tp'] == '110111' and e.get('prot'))
            if R.r.get('entradas_canceladas') == 'lancar_zerada':
                # regra do escritório: lança como CANCELADA, tudo zerado (valor contábil, base, alíquota, ICMS, IPI, crédito)
                zero = {k: Z for k in ('Valor produto', 'Frete', 'Desconto', 'BC ICMS', 'Alíq. ICMS', 'ICMS destacado',
                                       'Crédito SN (CSOSN 101)', 'ICMS-ST', 'IPI destacado', 'Crédito ICMS sugerido',
                                       'Crédito IPI sugerido', 'DIFAL estimado')}
                cfs, acs = set(), set()
                for it in n['itens']:
                    cl = R.classificar_entrada(n, it)
                    cfs.add(cl['cfop']); acs.add(str(cl.get('ac') or ''))
                    itens_rows.append({'Status': 'CANCELADA - LANÇAR ZERADA', 'Emissão': n['dt_emissao'],
                                       'Nota': n['numero'], 'Série': n['serie'], 'Fornecedor': n['emit_nome'],
                                       'CNPJ': n['emit_cnpj'], 'UF': n['emit_uf'], 'Item': int(it['nItem']),
                                       'Cód. produto': it['cProd'], 'Descrição do item': it['xProd'], 'NCM': it['NCM'],
                                       'CFOP forn.': it['CFOP'], 'CST/CSOSN': it['orig'] + it['CST_ICMS'], 'Qtd': it['qCom'],
                                       **zero, 'Finalidade': cl['finalidade'], 'Por quê': 'Nota cancelada pelo emitente',
                                       'Regra usada': cl.get('origem_regra', ''), 'CFOP sugerido': cl['cfop'],
                                       'Acum. sugerido': cl.get('ac') or '', 'Acumulador sugerido (nome)': R.ac_nome(cl.get('ac')),
                                       'Conta contábil sugerida': '', 'Origem da conta': '', 'Alertas': ''})
                notas_rows.append({'Status': 'CANCELADA - LANÇAR ZERADA', 'Emissão': n['dt_emissao'], 'Nota': n['numero'],
                                   'Fornecedor': n['emit_nome'], 'UF': n['emit_uf'], 'Natureza (fornecedor)': n['natOp'],
                                   'Valor NF': Z, 'ICMS destacado': Z, 'IPI destacado': Z,
                                   'CFOP sugerido': ', '.join(sorted(x for x in cfs if x)),
                                   'Acum. sugerido': ', '.join(sorted(x for x in acs if x)),
                                   'Crédito ICMS sugerido': Z, 'Crédito IPI sugerido': Z, 'DIFAL estimado': Z,
                                   'Contas contábeis sugeridas': '', 'Histórico do fornecedor no Domínio': '',
                                   'Observações': f'Cancelada pelo emitente em {quando} (protocolo {prot or "lista SEFAZ"}). '
                                                  f'Valor original R$ {n["t_vNF"]}: lançar com situação CANCELADA, '
                                                  'valor contábil, base, alíquota, ICMS, IPI e crédito zerados.',
                                   'Chave': n['chave']})
                pendencia('INFO', 'Cancelada pelo fornecedor', n,
                          f'NF-e cancelada pelo emitente ({quando}, protocolo {prot or "lista SEFAZ"}): lançar como '
                          f'CANCELADA com todos os valores zerados, sem crédito (valor original R$ {n["t_vNF"]}).', valor=Z)
                continue
            pendencia('ALTA' if (sp or dm) else 'INFO', 'Cancelada pelo fornecedor', n,
                      f'NF-e cancelada pelo emitente ({quando}): NÃO lançar.'
                      + (' Está lançada no SPED/Domínio: excluir.' if (sp or dm) else ''))
            continue
        anterior = ja_lancadas.get((n['emit_cnpj'], n['numero'].lstrip('0')))
        if anterior and pre:
            pendencia('INFO', 'Já lançada', n, f'Nota já lançada no Domínio em {anterior["entrada"]} '
                      f'({anterior["cfop"]}/ac {anterior["acumulador"]}). Não lançar de novo.')
            continue
        if not n['dt_emissao'].startswith(comp) and not sp and not dm:
            if not pre or n['dt_emissao'][:7] > comp:
                pendencia('INFO', 'Fora da competência', n, f'Emitida em {n["dt_emissao"]}: entra no mês seguinte.')
                continue
        hist_txt = fmt_hist(hist.get(n['emit_cnpj'], Counter()), ('36', '55', '22', '38', '37'))
        sp_itens = {it['n']: it for it in (sp['itens'] if sp else [])}
        sug_cfop, sug_ac, sts = set(), set(), []
        cred_icms = cred_ipi = difal = Z
        acertou_antes = acertou_final = 0
        for it in n['itens']:
            c = R.classificar_entrada(n, it)
            spi = sp_itens.get(it['nItem'])
            fin_cfop, fin_ac = (spi['cfop'], spi['cod_nat']) if spi else ('', '')
            imp_cfop, imp_ac = (dm[0]['cfop'], dm[0]['acumulador']) if dm else ('', '')
            st = []
            if not sp and not dm and not pre:
                st.append('NÃO ESCRITURADA')
            elif spi:
                if c['cfop'] and c['cfop'] != fin_cfop:
                    st.append('CFOP')
                if c.get('ac') and str(c['ac']) != str(fin_ac):
                    st.append('ACUMULADOR')
            if c['finalidade'] == 'PENDENTE':
                st.append('FINALIDADE A DEFINIR')
            elif pre and c['cfop'] and not c.get('ac'):
                st.append('SEM ACUMULADOR NA REGRA')
                pendencia('VERIFICAR', 'Acumulador', n,
                          f'Item {it["nItem"]} "{it["xProd"]}": CFOP {c["cfop"]} ({c["motivo"]}) sem acumulador '
                          'definido nas regras. Informar o acumulador do Domínio para esta operação.',
                          valor=it['vProd'])
            status = 'OK' if not st else ' / '.join(st)
            sts.append(status)
            corrigido = bool(spi and dm and (fin_cfop, fin_ac) != (imp_cfop, imp_ac))
            sug_cfop.add(c['cfop'])
            sug_ac.add(str(c.get('ac') or ''))
            cred_icms += c['cred_icms']
            cred_ipi += c['cred_ipi']
            difal += c['difal']
            itens_rows.append({
                'Status': status, 'Emissão': n['dt_emissao'], 'Nota': n['numero'], 'Série': n['serie'],
                'Fornecedor': n['emit_nome'], 'CNPJ': n['emit_cnpj'], 'UF': n['emit_uf'],
                'Regime forn.': REGIME.get(n['emit_crt'], n['emit_crt']),
                'Item': int(it['nItem']), 'Cód. produto': it['cProd'], 'Descrição do item': it['xProd'],
                'NCM': it['NCM'], 'CFOP forn.': it['CFOP'], 'CST/CSOSN': it['orig'] + it['CST_ICMS'],
                'Qtd': it['qCom'], 'Valor produto': it['vProd'], 'Frete': it['vFrete'], 'Desconto': it['vDesc'],
                'BC ICMS': it['vBC_ICMS'], 'Alíq. ICMS': it['pICMS'], 'ICMS destacado': it['vICMS'],
                'Crédito SN (CSOSN 101)': it['vCredICMSSN'], 'ICMS-ST': it['vICMSST'],
                'IPI destacado': it['vIPI'], 'CST PIS': it['CST_PIS'],
                'Finalidade': c['finalidade'], 'Por quê': c['motivo'], 'Regra usada': c['origem_regra'],
                'CFOP sugerido': c['cfop'], 'Acum. sugerido': c.get('ac') or '',
                'Acumulador sugerido (nome)': R.ac_nome(c.get('ac')),
                'Crédito ICMS sugerido': c['cred_icms'], 'Crédito IPI sugerido': c['cred_ipi'],
                'DIFAL estimado': c['difal'],
                'Conta contábil sugerida': c.get('conta', ''), 'Origem da conta': c.get('origem_conta', ''),
                'Histórico do fornecedor no Domínio': hist_txt,
                'CFOP final (SPED)': fin_cfop, 'Acum. final (SPED)': fin_ac,
                'Acumulador final (nome)': R.ac_nome(fin_ac) or nat.get(str(fin_ac), ''),
                'ICMS creditado (SPED)': spi['vl_icms'] if spi else None,
                'IPI creditado (SPED)': spi['vl_ipi'] if spi else None,
                'CFOP na importação': imp_cfop, 'Acum. na importação': imp_ac,
                'Corrigido à mão?': 'sim' if corrigido else '',
                'Alertas': ' | '.join(c['alertas']),
            })
            if c['finalidade'] == 'PENDENTE':
                pendencia('VERIFICAR', 'Finalidade do item', n,
                          f'Item {it["nItem"]} "{it["xProd"]}" (NCM {it["NCM"]}): {c["motivo"]}. '
                          + ('' if pre else f'No SPED ficou {fin_cfop}/ac {fin_ac}. ')
                          + (f'Histórico do fornecedor: {hist_txt}. ' if pre and hist_txt else '')
                          + 'Definir a finalidade para virar regra.',
                          valor=it['vProd'])
            if corrigido:
                acertou_antes += (c['cfop'], str(c.get('ac'))) == (imp_cfop, imp_ac)
                acertou_final += (c['cfop'], str(c.get('ac'))) == (fin_cfop, fin_ac)
        # ---- nível nota
        sp_icms = sum((i['vl_icms'] for i in sp['itens']), Z) if sp else Z
        sp_ipi = sum((i['vl_ipi'] for i in sp['itens']), Z) if sp else Z
        aj = e113.get(n['chave'], [])
        aj_txt = '; '.join(f'{cod} {valor}' for cod, _, valor in aj)
        obs = []
        st_n = 'OK' if all(s == 'OK' for s in sts) else 'DIVERGENTE'
        if sp and abs(sp_icms - cred_icms) > CENT:
            obs.append(f'Crédito ICMS no SPED {sp_icms} x sugerido {cred_icms}')
            st_n = 'DIVERGENTE'
        if sp and abs(sp_ipi - cred_ipi) > CENT:
            obs.append(f'Crédito IPI no SPED {sp_ipi} x sugerido {cred_ipi}')
            st_n = 'DIVERGENTE'
        aj_difal = sum((v for cod, descr, v in aj if 'DIFERENCIAL' in (descr or '').upper() or cod in R.r.get('codigos_difal', [])), Z)
        if difal and not aj:
            obs.append(f'DIFAL estimado {difal} e nenhum ajuste E113 para esta nota')
        elif difal and aj_difal and abs(aj_difal - difal) > Decimal('0.10'):
            obs.append(f'DIFAL lançado {aj_difal} x calculado {difal}')
        elif aj_difal and not difal:
            obs.append(f'DIFAL lançado {aj_difal} numa nota classificada como {", ".join(sorted(x for x in sug_ac if x))}')
        if not dm and not sp and not pre:
            st_n = 'NÃO ESCRITURADA'
            pendencia('ALTA', 'Nota não escriturada', n, 'XML destinado à Kopp, sem lançamento no Domínio/SPED.')
        sugeridos = ({(cf, ac) for cf, ac in zip(sug_cfop, sug_ac) if cf and ac}
                     if len(sug_cfop) == 1 == len(sug_ac) else set())
        usados = {(cf, ac) for (_, cf, ac) in hist.get(n['emit_cnpj'], {})}
        so_outras = all(r['Finalidade'] == 'OUTRA OPERAÇÃO' for r in itens_rows
                        if r['Nota'] == n['numero'] and r['CNPJ'] == n['emit_cnpj'])
        confirmado = R.r.get('confirmado_contra_historico', {}).get(n['emit_cnpj'])
        if confirmado:
            obs.append(confirmado)
        if pre and usados and sugeridos and not (sugeridos & usados) and not so_outras and not confirmado:
            obs.append(f'Sugestão {", ".join(f"{cf}/ac {ac}" for cf, ac in sugeridos)} difere do histórico ({hist_txt})')
            if st_n == 'OK':
                st_n = 'CONFERIR HISTÓRICO'
            pendencia('VERIFICAR', 'Classificação x histórico', n,
                      f'Robô sugere {", ".join(f"{cf}/ac {ac}" for cf, ac in sugeridos)}; nos meses anteriores este '
                      f'fornecedor foi lançado como {hist_txt}. Por quê: '
                      + '; '.join(sorted({r['Por quê'] for r in itens_rows if r['Nota'] == n['numero']
                                          and r['CNPJ'] == n['emit_cnpj']})) + '. Decidir qual vale e virar regra.')
        if pre and not usados:
            obs.append('Fornecedor sem lançamento no histórico do Domínio (primeira compra?)')
        meus = [r for r in itens_rows if r['Nota'] == n['numero'] and r['CNPJ'] == n['emit_cnpj']]
        corr = any(r['Corrigido à mão?'] for r in meus)
        difs = [r for r in meus if r['Status'] not in ('OK', 'FINALIDADE A DEFINIR', 'NÃO ESCRITURADA')]
        if not pre and (difs or (obs and st_n == 'DIVERGENTE')):
            txt = []
            for r in difs:
                txt.append(f'Item {r["Item"]} "{r["Descrição do item"][:40]}": no SPED {r["CFOP final (SPED)"]}/ac '
                           f'{r["Acum. final (SPED)"]} ({r["Acumulador final (nome)"]}); sugiro {r["CFOP sugerido"]}/ac '
                           f'{r["Acum. sugerido"]} — {r["Finalidade"]}: {r["Por quê"]}')
            txt += [o for o in obs if not o.startswith('DIFAL lançado') or not difs]
            pendencia('VERIFICAR', 'Classificação da entrada', n, ' · '.join(txt))
        notas_rows.append({
            'Status': st_n, 'Emissão': n['dt_emissao'], 'Nota': n['numero'], 'Fornecedor': n['emit_nome'],
            'UF': n['emit_uf'], 'Natureza (fornecedor)': n['natOp'], 'Valor NF': n['t_vNF'],
            'ICMS destacado': n['t_vICMS'], 'IPI destacado': n['t_vIPI'],
            'CFOP sugerido': ', '.join(sorted(x for x in sug_cfop if x)),
            'Acum. sugerido': ', '.join(sorted(x for x in sug_ac if x)),
            'Crédito ICMS sugerido': cred_icms, 'Crédito IPI sugerido': cred_ipi, 'DIFAL estimado': difal,
            'CFOP final (SPED)': ', '.join(sorted({i['cfop'] for i in sp['itens']})) if sp else '',
            'Acum. final (SPED)': ', '.join(sorted({i['cod_nat'] for i in sp['itens']})) if sp else '',
            'Crédito ICMS (SPED)': sp_icms if sp else None, 'Crédito IPI (SPED)': sp_ipi if sp else None,
            'DIFAL lançado (E113)': aj_difal, 'Ajustes E113 (SPED)': aj_txt,
            'CFOP na importação': dm[0]['cfop'] if dm else '', 'Acum. na importação': dm[0]['acumulador'] if dm else '',
            'Crédito ICMS na importação': imposto(dm, 'ICMS', 'valor') if dm else None,
            'Corrigido à mão?': 'sim' if corr else '',
            'Contas contábeis sugeridas': ', '.join(sorted({r['Conta contábil sugerida'] for r in meus if r['Conta contábil sugerida']})),
            'Histórico do fornecedor no Domínio': hist_txt,
            'Observações': ' | '.join(obs), 'Chave': n['chave'],
        })

    # ======================== 2. entradas emitidas pela própria empresa
    for n in sorted((n for n in notas.values() if n['emit_cnpj'] == K and n['tpNF'] == '0'
                     and n['dt_emissao'].startswith(comp)), key=lambda x: int(x['numero'])):
        dm = dom_por_chave.get(n['chave'], [])
        sp = sped_por_chave.get(n['chave'])
        cfops = Counter(it['CFOP'] for it in n['itens'])
        cfop = cfops.most_common(1)[0][0]
        esperado = R.r['devolucoes_proprias'].get(cfop, {}).get('ac')
        st, obs = [], []
        if n['cancelada']:
            if dm and sum((d['valor_contabil'] for d in dm), Z) != Z:
                st.append('CANCELADA NA SEFAZ, LANÇADA COM VALOR')
            if not pre and (not sp or sp['cod_sit'] not in ('02', '03')):
                st.append('SPED SEM COD_SIT 02')
            dev_rows.append({'Status': 'CANCELADA - OK' if not st else ' / '.join(st), 'Data': n['dt_emissao'],
                             'Nota': n['numero'], 'Cliente (remetente)': n['dest_nome'], 'Natureza': n['natOp'],
                             'CFOP XML': ', '.join(cfops), 'Valor NF': n['t_vNF'], 'Chave': n['chave'],
                             'Observações': 'Cancelada em ' + ', '.join(e['data'] for e in n['eventos'] if e['tp'] == '110111')})
            continue
        if pre:
            sem_ac = [c for c in cfops if not R.r['devolucoes_proprias'].get(c, {}).get('ac')]
            if sem_ac:
                st.append('CFOP SEM ACUMULADOR NA REGRA')
                obs.append(f'CFOP {", ".join(sem_ac)} sem acumulador definido: decidir antes de importar')
        elif not dm:
            st.append('NÃO ESTÁ NO DOMÍNIO')
        else:
            if {d['cfop'] for d in dm} != set(cfops):
                st.append('CFOP')
            if esperado and any(d['acumulador'] != esperado for d in dm if d['cfop'] == cfop):
                st.append('ACUMULADOR')
        if sp and sp['vl_icms'] != n['t_vICMS']:
            st.append('ICMS')
            obs.append(f'ICMS XML {n["t_vICMS"]} x SPED {sp["vl_icms"]}')
        cst00_sem_icms = [it for it in n['itens'] if it['CST_ICMS'] in ('00', '20') and not it['vICMS']]
        if cst00_sem_icms:
            com_base = sum((it['vBC_ICMS'] for it in cst00_sem_icms), Z)
            obs.append(f'{len(cst00_sem_icms)} item(ns) com CST {cst00_sem_icms[0]["CST_ICMS"]} (tributado) e ICMS zero'
                       + (f'; base {com_base} preenchida sem imposto' if com_base else ''))
        if n['finNFe'] == '4' and not n['refs']:
            obs.append('Devolução sem NF referenciada')
        dev_rows.append({
            'Status': 'OK' if not st else ' / '.join(st), 'Data': n['dt_emissao'], 'Nota': n['numero'],
            'Cliente (remetente)': n['dest_nome'], 'UF': n['dest_uf'], 'Natureza': n['natOp'],
            'Finalidade NF': {'1': 'Normal', '4': 'Devolução'}.get(n['finNFe'], n['finNFe']),
            'CFOP XML': ', '.join(cfops), 'CST ICMS': ', '.join(sorted({it['CST_ICMS'] for it in n['itens']})),
            'Acum. esperado': esperado or '', 'CFOP Domínio': ', '.join(d['cfop'] for d in dm),
            'Acum. Domínio': ', '.join(d['acumulador'] for d in dm), 'Valor NF': n['t_vNF'],
            'BC ICMS XML': n['t_vBC'], 'ICMS XML': n['t_vICMS'], 'IPI XML': n['t_vIPI'],
            'BC ICMS SPED': sp['vl_bc_icms'] if sp else None, 'ICMS SPED': sp['vl_icms'] if sp else None,
            'NF de venda referenciada': ', '.join(r[25:34].lstrip('0') for r in n['refs']),
            'Observações': ' | '.join(obs), 'Chave': n['chave'],
        })
    for d in dev_rows:
        if pre and 'SEM ACUMULADOR' in d['Status']:
            pendencia('VERIFICAR', 'Acumulador', d['Nota'], d['Observações'], valor=d['Valor NF'],
                      participante=d['Cliente (remetente)'])
    n_cst = sum(1 for d in dev_rows if 'tributado) e ICMS zero' in d.get('Observações', ''))
    if n_cst:
        pendencia('VERIFICAR', 'Cadastro do ERP', 'várias',
                  f'{n_cst} NF-e de devolução emitidas pela Kopp saem com CST 00/20 (tributado) e ICMS zero, algumas '
                  'com base preenchida. O Domínio importa base sem imposto. Ajustar a operação de devolução no ERP '
                  'para repetir o CST/cBenef da venda original (40 + PR810067 quando o produto é isento).',
                  participante='ERP Kopp')

    # ======================== 3. saídas próprias
    for n in sorted((n for n in notas.values() if n['emit_cnpj'] == K and n['tpNF'] == '1'
                     and n['dt_emissao'].startswith(comp)), key=lambda x: int(x['numero'])):
        dm = dom_por_chave.get(n['chave'], [])
        sp = sped_por_chave.get(n['chave'])
        cfops = Counter(it['CFOP'] for it in n['itens'])
        st, obs = [], []
        if n['cancelada']:
            if dm and sum((d['valor_contabil'] for d in dm), Z) != Z:
                st.append('CANCELADA NA SEFAZ, LANÇADA COM VALOR')
            if not pre and (not sp or sp['cod_sit'] not in ('02', '03')):
                st.append('SPED SEM COD_SIT 02')
            sai_rows.append({'Status': 'CANCELADA - OK' if not st else ' / '.join(st), 'Data': n['dt_emissao'],
                             'Nota': n['numero'], 'Cliente': n['dest_nome'], 'UF': n['dest_uf'], 'Natureza': n['natOp'],
                             'CFOP XML': ', '.join(cfops), 'Valor NF': n['t_vNF'], 'Chave': n['chave'],
                             'Observações': 'Cancelada em ' + ', '.join(e['data'] for e in n['eventos'] if e['tp'] == '110111')})
            continue
        base, icms, ise, outras = colunas_dominio(n['itens'])
        csts = Counter(it['CST_ICMS'] for it in n['itens'])
        sem_cbenef = [it['nItem'] for it in n['itens'] if it['CST_ICMS'] in CST_EXIGE_CBENEF and not it['cBenef']]
        if sem_cbenef:
            cst_sem = sorted({it['CST_ICMS'] for it in n['itens'] if it['nItem'] in sem_cbenef})
            msg = f'cBenef ausente nos itens {",".join(sem_cbenef)} (CST {",".join(cst_sem)}, CFOP {",".join(cfops)})'
            if any(c[1:] in ('915', '916') for c in cfops):
                msg += ': remessa/retorno de conserto costuma ser suspensão (CST 50 + cBenef). Conferir o cadastro da operação no ERP'
            obs.append(msg)
            st.append('cBenef')
        ac_sug = {c: R.r['saidas'].get(c, {}).get('ac') for c in cfops}
        if pre:
            sem_ac = [c for c, ac in ac_sug.items() if not ac]
            if sem_ac:
                st.append('CFOP SEM ACUMULADOR NA REGRA')
                obs.append(f'CFOP {", ".join(sem_ac)} sem acumulador definido: decidir antes de importar')
        elif not dm:
            st.append('NÃO ESTÁ NO DOMÍNIO')
        else:
            for d in dm:
                esp = R.r['saidas'].get(d['cfop'], {}).get('ac')
                if esp and d['acumulador'] != esp:
                    st.append('ACUMULADOR')
                    obs.append(f'CFOP {d["cfop"]} no acumulador {d["acumulador"]} (esperado {esp})')
            if {d['cfop'] for d in dm} != set(cfops):
                st.append('CFOP')
                obs.append(f'CFOP XML {sorted(cfops)} x Domínio {sorted(d["cfop"] for d in dm)}')
            d_base, d_icms = imposto(dm, 'ICMS', 'base'), imposto(dm, 'ICMS', 'valor')
            d_ise, d_out = imposto(dm, 'ICMS', 'isentas'), imposto(dm, 'ICMS', 'outras')
            if abs(d_icms - icms) > CENT or abs(d_base - base) > CENT:
                st.append('ICMS')
                obs.append(f'BC/ICMS XML {base}/{icms} x Domínio {d_base}/{d_icms}')
            elif abs(d_ise - ise) > Decimal('0.05') or abs(d_out - outras) > Decimal('0.05'):
                st.append('ISENTAS/OUTRAS')
                obs.append(f'Isentas/Outras pelo XML {ise}/{outras} x Domínio {d_ise}/{d_out}')
            if abs(imposto(dm, 'IPI', 'valor') - n['t_vIPI']) > CENT:
                st.append('IPI')
                obs.append(f'IPI XML {n["t_vIPI"]} x Domínio {imposto(dm, "IPI", "valor")}')
        if sp and (abs(sp['vl_icms'] - icms) > CENT):
            st.append('ICMS SPED')
            obs.append(f'ICMS SPED {sp["vl_icms"]} x XML {icms}')
        if st:
            pendencia('VERIFICAR', 'Saída', n, ' | '.join(obs))
        sai_rows.append({
            'Status': 'OK' if not st else ' / '.join(dict.fromkeys(st)), 'Data': n['dt_emissao'], 'Nota': n['numero'],
            'Cliente': n['dest_nome'], 'UF': n['dest_uf'], 'Natureza': n['natOp'],
            'CFOP XML': ', '.join(f'{k}({v})' if len(cfops) > 1 else k for k, v in cfops.items()),
            'CST ICMS (itens)': ', '.join(f'{k}({v})' for k, v in sorted(csts.items())),
            'Acum. sugerido': ', '.join(f'{c}→{ac or "?"}' for c, ac in ac_sug.items()),
            'CFOP Domínio': ', '.join(d['cfop'] for d in dm), 'Acum. Domínio': ', '.join(d['acumulador'] for d in dm),
            'Valor NF': n['t_vNF'], 'BC ICMS XML': base, 'ICMS XML': icms, 'Isentas XML': ise, 'Outras XML': outras,
            'IPI XML': n['t_vIPI'],
            'BC ICMS Domínio': imposto(dm, 'ICMS', 'base') if dm else None,
            'ICMS Domínio': imposto(dm, 'ICMS', 'valor') if dm else None,
            'Isentas Domínio': imposto(dm, 'ICMS', 'isentas') if dm else None,
            'Outras Domínio': imposto(dm, 'ICMS', 'outras') if dm else None,
            'IPI Domínio': imposto(dm, 'IPI', 'valor') if dm else None,
            'Observações': ' | '.join(obs), 'Chave': n['chave'],
        })

    # ======================== 4. completude de NF-e
    compl = []
    for ch in sorted(set(sefaz) | {k for k, n in notas.items() if n['emit_cnpj'] != K}):
        n = notas.get(ch)
        if n and not n['dt_emissao'].startswith(comp):
            continue
        sp = sped_por_chave.get(ch)
        modelo = ch[20:22]
        tem = {'XML': bool(n) or ch in chaves_arquivo, 'SPED': bool(sp), 'Domínio': bool(dom_por_chave.get(ch)),
               'Lista SEFAZ': ch in sefaz}
        if pre:
            del tem['SPED'], tem['Domínio']
        if all(tem.values()):
            continue
        emit = n['emit_nome'] if n else str(sefaz.get(ch, {}).get('EMITENTE', ''))
        if modelo == '57' and tem['SPED'] and not tem['XML']:
            sit = 'CT-e: escriturado (D100); XML do CT-e não estava na pasta'
        elif n and R.ignorar(n):
            sit = 'Documento do fornecedor (não gera entrada)'
        elif ch in sefaz and 'CANCEL' in str(sefaz[ch].get('STATUS', '')).upper():
            if tem.get('SPED') or tem.get('Domínio'):
                sit = 'Cancelada na SEFAZ mas ESCRITURADA'
            else:
                continue
        else:
            sit = 'Falta em: ' + ', '.join(k for k, v in tem.items() if not v)
        compl.append({'Situação': sit, 'Modelo': modelo, 'Número': ch[25:34].lstrip('0'), 'Emitente': emit,
                      'Valor': n['t_vNF'] if n else (sp['vl_doc'] if sp else sefaz.get(ch, {}).get('VALOR')),
                      **{k: 'sim' if v else 'NÃO' for k, v in tem.items()}, 'Chave': ch})

    # ======================== 5. numeração própria
    lacunas = []
    erp = {}
    if a.erp_notas:
        x = pd.read_excel(a.erp_notas, sheet_name=a.erp_aba)
        x['n'] = pd.to_numeric(x['Nº Nota'], errors='coerce')
        for _, r in x.dropna(subset=['n']).drop_duplicates('n').iterrows():
            erp[(str(int(r['Série'])) if not pd.isna(r['Série']) else '', int(r['n']))] = r
    proprias = defaultdict(dict)
    for n in notas.values():
        if n['emit_cnpj'] == K and n['modelo'] == '55':
            proprias[n['serie']][int(n['numero'])] = n
    dom_por_num = defaultdict(list)
    for d in dom_e + dom_s:
        dom_por_num[d['nota']].append(d)
    sped_proprio = {(d['serie'].lstrip('0') or '0', int(d['numero'])): d for d in sped['docs']
                    if d['reg'] == 'C100' and d['ind_emit'] == '0' and d['numero'].isdigit()}
    for serie, nums in proprias.items():
        mes = [x for x, n in nums.items() if n['dt_emissao'].startswith(comp)]
        if not mes:
            continue
        # faixa contínua do mês: ignora números isolados (ex.: nota antiga autorizada no mês)
        mes.sort()
        blocos, atual = [], [mes[0]]
        for x in mes[1:]:
            if x - atual[-1] > 30:
                blocos.append(atual)
                atual = [x]
            else:
                atual.append(x)
        blocos.append(atual)
        principal = max(blocos, key=len)
        faixa = [x for x in range(principal[0], principal[-1] + 1)]
        for x in faixa:
            if x in nums:
                continue
            ds = [d for d in dom_por_num.get(str(x), []) if d['especie'] in ('36', '55')]
            spd = sped_proprio.get((serie.lstrip('0') or '0', x))
            e = erp.get((serie, x))
            sit_erp = str(e['Situação']) if e is not None and not pd.isna(e['Situação']) else ''
            if 'INUTILIZ' in sit_erp.upper():
                sit = 'Inutilizada (ERP)'
                sit += '; Domínio com valor zero' if ds else ''
                if pre:
                    sit += ': informar no SPED com COD_SIT 05'
                    grav = 'INFO'
                else:
                    sit += '; FORA DO SPED (inutilizada vai no C100 com COD_SIT 05)' if not spd else ''
                    grav = 'VERIFICAR' if not spd else 'INFO'
            elif ds and all(d['valor_contabil'] == Z for d in ds):
                sit, grav = 'Domínio com valor zero, sem XML' + ('' if spd else ' e fora do SPED'), 'VERIFICAR'
            elif ds:
                sit, grav = 'No Domínio com valor, mas sem XML na pasta', 'ALTA'
            elif spd:
                sit, grav = f'Só no SPED (COD_SIT {spd["cod_sit"]}), sem XML', 'VERIFICAR'
            elif e is not None:
                sit, grav = f'No ERP ({sit_erp or "sem situação"}), sem XML na pasta: pedir o XML ao cliente', 'ALTA'
            else:
                sit, grav = ('Número sem XML, fora do ERP, do Domínio e do SPED: confirmar na SEFAZ se foi '
                             'rejeitada (precisa inutilizar) ou se o XML ficou fora do download'), 'VERIFICAR'
            lacunas.append({'Série': serie, 'Número': x, 'Situação': sit, 'Gravidade': grav,
                            'Situação no ERP': sit_erp,
                            'Cliente (ERP/Domínio)': (str(e['Cliente']) if e is not None else
                                                      (ds[0]['participante'] if ds else '')),
                            'Valor no ERP': e['Total Líquido'] if e is not None else None,
                            'Domínio': ', '.join(f"{d['cfop']}/ac {d['acumulador']} valor {d['valor_contabil']}" for d in ds),
                            'SPED COD_SIT': spd['cod_sit'] if spd else ''})
    inut = [l for l in lacunas if l['Situação'].startswith('Inutilizada') and 'FORA DO SPED' in l['Situação']]
    if inut:
        pendencia('VERIFICAR', 'SPED', 'várias',
                  f'{len(inut)} numerações inutilizadas ({", ".join(str(l["Número"]) for l in inut)}) não constam no '
                  'SPED. Pelo Guia Prático, numeração inutilizada é informada no C100 com COD_SIT 05.',
                  participante='SPED Fiscal')
    soltas = [l for l in lacunas if l['Situação'].startswith('Número sem XML')]
    if soltas:
        pendencia('VERIFICAR', 'Numeração', 'várias',
                  f'{len(soltas)} números da série 1 não aparecem em nenhuma fonte (XML, ERP, Domínio, SPED): '
                  + ', '.join(str(l['Número']) for l in soltas)
                  + '. Ficam entre devoluções/remessas para troca. Consultar na SEFAZ se foram rejeitados '
                  '(inutilizar) ou se faltaram no download.', participante='Kopp')
    if erp:
        series_nfe = {n['serie'].lstrip('0') for n in notas.values() if n['emit_cnpj'] == K and n['modelo'] == '55'}
        sem_chave = [(k, r) for k, r in erp.items() if k[0] not in series_nfe
                     and (pd.isna(r.get('Chave NFE')) or str(r.get('Chave NFE'))[20:22] not in ('55', '65'))]
        if sem_chave:
            tot = sum(float(r['Total Líquido'] or 0) for _, r in sem_chave)
            pendencia('VERIFICAR', 'ERP x fiscal', 'série ' + ', '.join(sorted({k[0] for k, _ in sem_chave})),
                      f'{len(sem_chave)} documentos "Nota de Venda" no relatório do ERP fora da série de NF-e '
                      f'(série {", ".join(sorted({k[0] for k, _ in sem_chave}))}: nenhuma NF-e emitida nela; não inutilizar como NF-e) '
                      f'(total R$ {tot:,.2f}): '
                      + ', '.join(str(k[1]) for k, _ in sorted(sem_chave, key=lambda t: t[0][1]))
                      + '. Confirmar se são documentos internos (pedido/romaneio) ou vendas sem nota fiscal.',
                      valor=q(Decimal(str(tot))), participante='ERP Kopp')

    # ======================== 6. NFS-e tomadas (lista nacional x Domínio)
    nfse_rows = []
    if a.nfse_recebidas and (a.dom_servicos or pre):
        lst = pd.read_excel(a.nfse_recebidas, sheet_name=a.nfse_aba).dropna(subset=['Número NFS-e'])
        dsv = (parse_acompanhamento(a.dom_servicos, a.dom_servicos_aba) if a.dom_servicos else []) \
            + [d for d in dom_e if d['especie'] == '39']
        usados = set()
        for _, r in lst.iterrows():
            num = str(int(r['Número NFS-e']))
            val = q(Decimal(str(r['Valor do Serviço (R$)'])))
            hit = None
            for i, d in enumerate(dsv):
                if d['nota'] == num and i not in usados and (hit is None or abs(d['valor_contabil'] - val) <= CENT):
                    hit = i
            if hit is not None:
                usados.add(hit)
            d = dsv[hit] if hit is not None else None
            canc = 'Cancel' in str(r['Situação NFS-e'])
            cnpj_p = re.sub(r'\D', '', str(r['CNPJ/CPF Prestador']).split('.')[0] if isinstance(
                r['CNPJ/CPF Prestador'], float) else str(r['CNPJ/CPF Prestador']))
            cnpj_p = cnpj_p.zfill(14) if len(cnpj_p) > 11 or cnpj_p.zfill(14) in hist else cnpj_p.zfill(11)
            antes = ja_lancadas.get((cnpj_p, num))
            if pre:
                st = ('OK (cancelada, não lançar)' if canc else
                      f'JÁ LANÇADA em {antes["entrada"]}' if antes else 'A LANÇAR')
            elif d and canc:
                st = 'CANCELADA E LANÇADA'
            elif canc:
                st = 'OK (cancelada, não lançada)'
            elif not d:
                st = 'NÃO LANÇADA'
            elif abs(d['valor_contabil'] - val) > CENT:
                st = 'VALOR DIFERENTE'
            else:
                st = 'OK'
            nfse_rows.append({'Status': st, 'Número': num, 'Competência': r['Competência'],
                              'Prestador': r['Nome Prestador'], 'CNPJ': cnpj_p,
                              'Município ISS': r['Município de Incidência'], 'Valor': val,
                              'Situação NFS-e': r['Situação NFS-e'],
                              'IRRF na nota': q(Decimal(str(r.get('IRRF (R$)') or 0))),
                              'Acum. histórico (prestador)': fmt_hist(hist.get(cnpj_p, Counter()), ('39',)),
                              'Data Domínio': d['data'] if d else '', 'Acum. Domínio': d['acumulador'] if d else '',
                              'CFOP Domínio': d['cfop'] if d else '', 'Valor Domínio': d['valor_contabil'] if d else None})
            hcont = Counter({ac: v for (esp, _, ac), v in hist.get(cnpj_p, Counter()).items() if esp == '39'})
            sv = classificar_servico(R, r, cnpj_p, hcont)
            if pre and st == 'A LANÇAR' and (sv['alertas'] or not sv['ac'] or (hcont and sv['ac'] not in hcont)):
                st = 'CONFERIR'
            nfse_rows[-1].update({
                'Status': st, 'Serviço (LC 116)': sv['item'], 'Natureza do serviço': sv['natureza'],
                'Retenções na nota': sv['ret'], 'Acum. sugerido': sv['ac'], 'Acumulador sugerido (nome)': sv['ac_nome'],
                'Conta contábil sugerida': sv['conta'], 'Origem da conta': sv['origem_conta'],
                'Alertas': ' | '.join(sv['alertas']),
                'Data emissão': pd.to_datetime(r.get('Data Geração')).strftime('%d/%m/%Y') if not pd.isna(r.get('Data Geração')) else '',
                'Município do prestador': r.get('Município de Incidência', ''),
                'Simples Nacional': r.get('Simples Nacional', ''),
                **{f'{k} retido': v for k, v in sv['valores'].items()}})
            if pre and st == 'CONFERIR':
                txt = []
                if sv['ac'] and hcont and sv['ac'] not in hcont:
                    txt.append(f'Pelo item {sv["item"]} e retenções ({sv["ret"]}) o acumulador é {sv["ac"]} '
                               f'({sv["ac_nome"]}); no histórico o prestador foi lançado em '
                               f'{", ".join(f"{k} ×{v}" for k, v in hcont.most_common())}')
                txt += sv['alertas']
                if not sv['ac'] and not sv['alertas']:
                    txt.append('Sem acumulador sugerido')
                pendencia('VERIFICAR', 'NFS-e tomada', num, ' · '.join(txt), valor=val, participante=r['Nome Prestador'])
            mm, aa = comp[5:7], comp[:4]
            outra_comp = str(r['Competência']) != f'{mm}/{aa}'
            if pre and st in ('A LANÇAR', 'CONFERIR') and outra_comp:
                if R.r.get('servicos', {}).get('outra_competencia') == 'apontar':
                    nfse_rows[-1]['Status'] = f'NÃO LANÇAR - competência {r["Competência"]}'
                    pendencia('INFO', 'NFS-e de outra competência', num,
                              f'Competência {r["Competência"]}, não lançada no Domínio até {periodos_hist[-1][1] if periodos_hist else "o mês anterior"}. '
                              'Apontada, não lançar (regra do escritório).', valor=val, participante=r['Nome Prestador'])
                else:
                    pendencia('VERIFICAR', 'NFS-e tomada', num,
                              f'Competência {r["Competência"]} e não aparece no histórico do Domínio: lançar em '
                              f'{mm}/{aa} ou no mês da competência?', valor=val, participante=r['Nome Prestador'])
            if st == 'NÃO LANÇADA':
                pendencia('VERIFICAR' if outra_comp else 'ALTA', 'NFS-e tomada', num,
                          f'NFS-e na lista nacional (competência {r["Competência"]}) sem lançamento neste mês no Domínio.'
                          + (' Conferir se foi lançada no mês da competência.' if outra_comp else ''),
                          valor=val, participante=r['Nome Prestador'])
            elif st in ('VALOR DIFERENTE', 'CANCELADA E LANÇADA'):
                pendencia('VERIFICAR', 'NFS-e tomada', num,
                          f'{st}: lista nacional R$ {val} ({r["Situação NFS-e"]}) x Domínio R$ {d["valor_contabil"]}.',
                          valor=val, participante=r['Nome Prestador'])

    # ======================== 7. auditoria: CT-e, remessas, ERP x XML, coerência
    import auditoria as au
    cte_rows, cte_pend = au.analisar_cte(au.carregar_cte(a.xml), R, sefaz, hist, set(sped_por_chave))
    for g, t, num, msg, _ in cte_pend:
        pendencia(g, t, num, msg, participante='')
    for c_ in cte_rows:
        if c_['Status'] == 'A LANÇAR' and c_['Observações']:
            pendencia('VERIFICAR', 'CT-e', c_['CT-e'], c_['Observações'], valor=c_['Valor'], participante=c_['Transportador'])
    anteriores = {}
    for pasta in a.xml_anteriores or []:
        anteriores.update(carregar_xmls(pasta)[0])
    rem_rows = au.remessa_retorno(notas, anteriores, K)
    grupos = defaultdict(list)
    for r_ in rem_rows:
        grupos[(r_['Status'], r_['Parceiro'], r_['Operação'])].append(r_)
    for (st_, parc, op), rs in grupos.items():
        txt = '; '.join(f'{r_["Item"]} remetido {r_["Remetido"]:g} / retornado {r_["Retornado"]:g}' for r_ in rs[:6])
        if st_.startswith('RETORNO MAIOR'):
            pendencia('VERIFICAR', 'Remessa x retorno', ', '.join(sorted({r_['Retornos'] for r_ in rs})),
                      f'{op} com {parc}: retorno maior que a remessa ({len(rs)} item(ns)) — possível nota de retorno '
                      f'em duplicidade, não lançar as duas sem confirmar. {txt}. Remessa(s): {rs[0]["Remessas"]}',
                      participante=parc)
        elif st_.startswith('REMESSA NÃO'):
            pendencia('INFO', 'Remessa x retorno', ', '.join(sorted({r_['Retornos'] for r_ in rs})),
                      f'{op} com {parc}: retorno de {len(rs)} item(ns) sem a remessa nos XML carregados '
                      f'(remessa de mês anterior?). {txt}', participante=parc)
        else:
            pendencia('INFO', 'Remessa x retorno', rs[0]['Remessas'],
                      f'{op} com {parc}: {len(rs)} item(ns) ainda não retornaram. {txt}', participante=parc)
    erp_rows = au.erp_x_xml(a.erp_notas, a.erp_aba, notas) if a.erp_notas else []
    for e_ in erp_rows:
        if e_['Status'] == 'NÃO É NF-e':
            continue                     # entra na pendência da série sem NF-e (ERP x fiscal)
        pendencia('ALTA' if e_['Status'] == 'SEM XML' else 'VERIFICAR', 'ERP x XML', f'{e_["Número"]}/{e_["Série"]}',
                  ('Nota autorizada (com chave no relatório do ERP) sem XML na pasta: pedir o XML e lançar. '
                   if e_['Status'] == 'SEM XML' else 'Relatório do ERP diverge do XML (vale o XML): ') + e_['Divergências'],
                  participante=e_['Cliente'])
    coer = au.coerencia_proprias(notas, K)
    cst00 = defaultdict(list)
    for c_ in coer:
        if c_['Tipo'].startswith('CST 00'):
            cst00[c_['CFOP']].append(c_)
        else:
            pendencia('INFO', 'Nota própria', c_['Nota'], f'{c_["Tipo"]}: {c_["Detalhe"]}', valor=c_['Valor'], participante='Kopp')
    aceito = R.r.get('saidas_icms_zero_9021') == 'aceito'
    for cf, cs in cst00.items():
        if aceito:
            pendencia('INFO', 'ICMS zero (isenção 9021)', f'{len(cs)} notas',
                      f'CFOP {cf}: {len(cs)} nota(s) de implantes com ICMS zero, aceito (isenção item 67 Anexo V RICMS-PR, '
                      f'Conv. ICMS 126/10). Só o código está como CST 00; o usual é CST 40 + PR810067.',
                      valor=sum((c_['Valor'] for c_ in cs), Z), participante='ERP Kopp')
            continue
        pendencia('VERIFICAR', 'Cadastro do ERP', f'{len(cs)} notas', f'CFOP {cf}: {len(cs)} nota(s) com itens em CST 00 '
                  f'(tributado) sem base e sem ICMS (ex.: {", ".join(c_["Nota"] for c_ in cs[:5])}). Se o produto é isento, '
                  'o correto é CST 40 + cBenef, como nas vendas; se é tributado, falta o imposto.',
                  valor=sum((c_['Valor'] for c_ in cs), Z), participante='ERP Kopp')
    res_aud = dict(cte=cte_rows, remessas=rem_rows, erp_xml=erp_rows, coerencia=coer)

    return dict(**res_aud, pre=pre, periodos_hist=periodos_hist, hist=hist, regras=R, competencia=comp, notas=notas, erros=erros, sped=sped, dom_e=dom_e, dom_s=dom_s,
                sefaz=sefaz, itens=itens_rows, notas_terc=notas_rows, devol=dev_rows, saidas=sai_rows,
                completude=compl, lacunas=lacunas, nfse=nfse_rows, pendencias=pend, origem=origem)


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--regras', required=True)
    p.add_argument('--xml', required=True)
    p.add_argument('--sped')
    p.add_argument('--dom-entradas')
    p.add_argument('--dom-entradas-aba', default='Entradas')
    p.add_argument('--dom-saidas')
    p.add_argument('--dom-saidas-aba', default='Saídas')
    p.add_argument('--sefaz', nargs='+')
    p.add_argument('--historico', nargs='*', default=[])
    p.add_argument('--xml-anteriores', nargs='*', default=[],
                   help='pastas de XML de meses anteriores (para casar remessa x retorno)')
    p.add_argument('--acumuladores', nargs='*', default=[],
                   help='"Resumo por acumulador" do Domínio em PDF: catálogo com o nome de cada acumulador')
    p.add_argument('--sefaz-aba', default=0)
    p.add_argument('--nfse-recebidas')
    p.add_argument('--nfse-aba', default='Relação')
    p.add_argument('--dom-servicos')
    p.add_argument('--dom-servicos-aba', default='Entradas')
    p.add_argument('--erp-notas')
    p.add_argument('--erp-aba', default=0)
    p.add_argument('--competencia', required=True)
    p.add_argument('--saida', required=True)
    a = p.parse_args()
    res = analisar(a)
    import auditoria as au
    res['checklist'] = au.checklist(res)
    from planilha import gravar_planilha
    gravar_planilha(res, a.saida)
    print('Planilha gerada:', a.saida)


if __name__ == '__main__':
    main()
