"""Cruzamentos de auditoria que rodam junto com a conferência:

- CT-e: papel da empresa (tomadora ou não), CFOP de entrada, acumulador e crédito;
- remessa x retorno (conserto, industrialização, exposição): quantidade devolvida
  não pode passar da enviada;
- relatório de notas do ERP x XML: situação, chave, valor, base, ICMS, IPI e CFOP;
- coerência fiscal das notas próprias: CST tributado sem imposto, total da nota;
- checklist: cada verificação feita, quantos documentos e o resultado.
"""
import glob
import os
import re
import unicodedata
from collections import Counter, defaultdict
from decimal import Decimal

import pandas as pd

Z = Decimal('0')
TOL = Decimal('0.05')


def _d(v):
    if v is None or (isinstance(v, float) and pd.isna(v)) or str(v).strip() in ('', 'nan'):
        return Z
    return Decimal(str(v)).quantize(Decimal('0.01'))


def _nome(s):
    return re.sub(r'[^A-Z0-9]', '', unicodedata.normalize('NFKD', str(s).upper()).encode('ascii', 'ignore').decode())


# ------------------------------------------------------------------ CT-e
def carregar_cte(pasta):
    ctes, eventos = {}, defaultdict(list)
    for f in glob.glob(os.path.join(pasta, '**', '*.xml'), recursive=True):
        t = open(f, encoding='utf-8', errors='ignore').read()
        if '<infCte' not in t and 'procEventoCTe' not in t and 'eventoCTe' not in t:
            continue
        ch = re.search(r'<chCTe>(\d{44})</chCTe>', t)
        tp = re.search(r'<tpEvento>(\d+)</tpEvento>', t)
        if tp and ch and '<infCte' not in t:
            st = re.search(r'<cStat>(\d+)</cStat>', t[t.find('retEvento'):] if 'retEvento' in t else t)
            if not st or st.group(1) in ('135', '136'):
                eventos[ch.group(1)].append(tp.group(1))
            continue
        g = lambda tag, txt=t: (re.search(f'<{tag}>([^<]*)</{tag}>', txt) or [None, ''])[1]

        def parte(tag):
            m = re.search(f'<{tag}>(.*?)</{tag}>', t, re.S)
            if not m:
                return '', ''
            doc = re.search(r'<(?:CNPJ|CPF)>(\d+)</', m.group(1))
            return (doc.group(1) if doc else ''), g('xNome', m.group(1))
        chave = (re.search(r'Id="CTe(\d{44})"', t) or [None, ''])[1]
        papeis = {p: parte(p) for p in ('rem', 'exped', 'receb', 'dest')}
        toma = g('toma')
        if toma == '' and '<toma4>' in t:
            tomador = parte('toma4')
        else:
            tomador = papeis.get({'0': 'rem', '1': 'exped', '2': 'receb', '3': 'dest'}.get(toma, ''), ('', ''))
        ctes[chave] = dict(chave=chave, numero=g('nCT'), serie=g('serie'), data=g('dhEmi')[:10], cfop=g('CFOP'),
                           emit_cnpj=parte('emit')[0], emit_nome=parte('emit')[1], uf_ini=g('UFIni'), uf_fim=g('UFFim'),
                           valor=_d(g('vTPrest')), cst=g('CST'), vbc=_d(g('vBC')), vicms=_d(g('vICMS')),
                           tomador=tomador, papeis=papeis)
    for ch, evs in eventos.items():
        if ch in ctes:
            ctes[ch]['cancelado'] = '110111' in evs
    return ctes


def analisar_cte(ctes, R, sefaz, hist):
    K, uf = R.cnpj, R.uf
    cfg = R.r.get('cte', {})
    linhas, pend = [], []
    for ch, c in sorted(ctes.items(), key=lambda x: x[1]['data']):
        canc = c.get('cancelado') or 'CANCEL' in str(sefaz.get(ch, {}).get('STATUS', '')).upper()
        papel = [p for p, (doc, _) in c['papeis'].items() if doc == K]
        toma_kopp = c['tomador'][0] == K
        ent = ('1' if c['uf_ini'] == uf else '2') + cfg.get('cfop_sufixo', '352')
        hcont = Counter({ac: v for (esp, cf, ac), v in hist.get(c['emit_cnpj'], Counter()).items()})
        ac = cfg.get('ac_com_icms', '304') if c['vicms'] else cfg.get('ac_sem_icms', cfg.get('ac_com_icms', '304'))
        if canc:
            st, obs = 'CANCELADO - não lançar', 'Cancelado (evento/lista SEFAZ)'
        elif not toma_kopp:
            st, obs = 'NÃO LANÇAR - Kopp não é tomadora', (f'Kopp aparece como {", ".join(papel) or "-"}; '
                                                           f'quem paga o frete é {c["tomador"][1] or c["tomador"][0]}')
        else:
            st, obs = 'A LANÇAR', ''
            if hcont and ac not in hcont:
                obs = f'Histórico do transportador: {", ".join(f"ac {k} ×{v}" for k, v in hcont.most_common())}'
        linhas.append({'Status': st, 'CT-e': c['numero'], 'Data': c['data'], 'Transportador': c['emit_nome'],
                       'CNPJ': c['emit_cnpj'], 'CFOP do CT-e': c['cfop'], 'Trajeto': f'{c["uf_ini"]}→{c["uf_fim"]}',
                       'Remetente': c['papeis']['rem'][1], 'Destinatário': c['papeis']['dest'][1],
                       'Tomador (quem paga)': c['tomador'][1] or c['tomador'][0], 'Valor': c['valor'],
                       'CST': c['cst'], 'BC ICMS': c['vbc'], 'ICMS': c['vicms'],
                       'CFOP de entrada sugerido': ent if st == 'A LANÇAR' else '',
                       'Acum. sugerido': ac if st == 'A LANÇAR' else '',
                       'Crédito ICMS sugerido': c['vicms'] if st == 'A LANÇAR' else Z,
                       'Observações': obs, 'Chave': ch})
    for ch in sefaz:
        if ch[20:22] == '57' and ch not in ctes and 'CANCEL' not in str(sefaz[ch].get('STATUS', '')).upper():
            pend.append(('ALTA', 'CT-e', ch[25:34].lstrip('0'), 'CT-e na lista da SEFAZ sem XML na pasta.'))
    return linhas, pend


# ------------------------------------------------------------------ remessa x retorno
PARES = {'915': ('916',), '901': ('902',), '914': ('914',)}


def remessa_retorno(notas, notas_anteriores, K):
    """Compara, por parceiro (CNPJ) e item, o que a empresa remeteu (conserto, industrialização,
    exposição) com o que voltou. Só avalia os retornos do mês; as remessas vêm do mês e dos anteriores.
    Retorno maior que a remessa = possível documento em duplicidade."""
    todas = {**notas_anteriores, **notas}
    env, ret = defaultdict(Counter), defaultdict(Counter)
    docs, nomes = defaultdict(lambda: {'rem': set(), 'ret': set()}), {}
    for n in todas.values():
        if n['cancelada'] or not n.get('numero'):
            continue
        own = n['emit_cnpj'] == K
        do_mes = n['chave'] in notas
        for it in n['itens']:
            suf = it['CFOP'][1:]
            if own and n['tpNF'] == '1' and suf in PARES:
                k = (n['dest_cnpj'], suf)
                nomes[k] = n['dest_nome']
                env[k][_nome(it['xProd'])[:24]] += it['qCom']
                docs[k]['rem'].add(n['numero'])
            elif do_mes and suf in ('916', '902', '914') and (not own or n['tpNF'] == '0'):
                base = {'916': '915', '902': '901', '914': '914'}[suf]
                k = (n['emit_cnpj'] if not own else n['dest_cnpj'], base)
                nomes.setdefault(k, n['emit_nome'] if not own else n['dest_nome'])
                ret[k][_nome(it['xProd'])[:24]] += it['qCom']
                docs[k]['ret'].add(n['numero'])
    linhas = []
    for k in sorted(set(env) | set(ret)):
        if not ret[k] and not any(n['chave'] in notas for n in todas.values()
                                  if n['numero'] in docs[k]['rem'] and n['emit_cnpj'] == K):
            continue                                  # remessa antiga sem movimento no mês
        for item in sorted(set(env[k]) | set(ret[k])):
            e, r = env[k][item], ret[k][item]
            if e == r:
                continue
            if r > e and e == 0:
                st = 'REMESSA NÃO ENCONTRADA (anterior ao período carregado?)'
            elif r > e:
                st = 'RETORNO MAIOR QUE A REMESSA'
            else:
                st = 'AINDA NÃO RETORNOU'
            linhas.append({'Status': st, 'Parceiro': nomes.get(k, k[0]), 'CNPJ': k[0],
                           'Operação': {'915': 'Conserto', '901': 'Industrialização', '914': 'Exposição/feira'}[k[1]],
                           'Item': item, 'Remetido': e, 'Retornado': r, 'Diferença': r - e,
                           'Remessas': ', '.join(sorted(docs[k]['rem'])), 'Retornos': ', '.join(sorted(docs[k]['ret']))})
    return linhas


# ------------------------------------------------------------------ ERP x XML
def erp_x_xml(erp_path, aba, notas):
    x = pd.read_excel(erp_path, sheet_name=aba, dtype={'Chave NFE': str})
    linhas = []
    for _, r in x.iterrows():
        ch = str(r.get('Chave NFE') or '').strip()
        if not ch or ch == 'nan':
            continue
        num = str(r['Nº Nota']).split('.')[0]
        n = notas.get(ch)
        dif = []
        if not n:
            dif.append('chave do ERP sem XML na pasta')
        else:
            pares = (('Valor', _d(r['Total Líquido']), n['t_vNF']), ('Base ICMS', _d(r['Base Icms']), n['t_vBC']),
                     ('ICMS', _d(r['Valor Icms']), n['t_vICMS']), ('IPI', _d(r['Valor IPI']), n['t_vIPI']))
            dif += [f'{k}: ERP {a} x XML {b}' for k, a, b in pares if abs(a - b) > TOL]
            cf_erp = {s.split('.')[0].strip() for s in str(r['CFOP Itens']).split(',') if s.strip() and s != 'nan'}
            cf_xml = {it['CFOP'] for it in n['itens']}
            if cf_erp and cf_erp != cf_xml:
                dif.append(f'CFOP: ERP {sorted(cf_erp)} x XML {sorted(cf_xml)}')
            if ('Cancel' in str(r['Situação'])) != n['cancelada']:
                dif.append(f'Situação: ERP {r["Situação"]} x XML {"cancelada" if n["cancelada"] else "autorizada"}')
        if dif:
            linhas.append({'Status': 'SEM XML' if not n else 'DIVERGENTE', 'Série': r['Série'], 'Número': num,
                           'Cliente': str(r['Cliente']).strip(), 'Data': str(r['Data Emissão'])[:10],
                           'Divergências': ' | '.join(dif), 'Chave': ch})
    return linhas


# ------------------------------------------------------------------ coerência das notas próprias
def coerencia_proprias(notas, K):
    linhas = []
    for n in notas.values():
        if n['emit_cnpj'] != K or n['cancelada'] or not n.get('numero'):
            continue
        saida = n['tpNF'] == '1'
        soma = sum((it['vProd'] + it['vFrete'] + it['vSeg'] + it['vOutro'] - it['vDesc'] + it['vIPI'] + it['vICMSST']
                    for it in n['itens']), Z)
        if abs(soma - n['t_vNF']) > TOL:
            linhas.append({'Tipo': 'Total da nota ≠ soma dos itens', 'Nota': n['numero'], 'CFOP': '',
                           'Detalhe': f'itens {soma} x total {n["t_vNF"]}', 'Valor': n['t_vNF']})
        cst00 = [it for it in n['itens'] if saida and it['CST_ICMS'] == '00' and not it['vICMS']]
        for cf in sorted({it['CFOP'] for it in cst00}):
            its = [it for it in cst00 if it['CFOP'] == cf]
            linhas.append({'Tipo': 'CST 00 (tributado) sem base/ICMS', 'Nota': n['numero'], 'CFOP': cf,
                           'Detalhe': f'{len(its)} item(ns), NCM {", ".join(sorted({i["NCM"][:4] for i in its}))}',
                           'Valor': sum((i['vProd'] for i in its), Z)})
    return linhas


# ------------------------------------------------------------------ checklist
def checklist(res):
    pend = res['pendencias']
    pc = Counter(p['Tipo'] for p in pend)
    itens, notas_t = res['itens'], res['notas_terc']
    fin = Counter(i['Finalidade'] for i in itens)
    ck = []

    def add(area, verificacao, base, achados, obs=''):
        ck.append({'Área': area, 'Verificação': verificacao, 'Base conferida': base,
                   'Achados': achados, 'Resultado': 'OK' if not achados else 'VER ABAS', 'Observação': obs})
    nt = len(res['notas'])
    add('Arquivos', 'Todos os XML lidos sem erro', f'{nt} NF-e', len(res['erros']))
    add('Arquivos', 'Lista da SEFAZ (NF-e e CT-e) x XML na pasta', f'{len(res["sefaz"])} chaves',
        sum(1 for c in res['completude'] if 'Falta' in c['Situação']))
    add('Entradas', 'Nota cancelada pelo fornecedor fora do lançamento', f'{len(notas_t)} notas',
        0, f'{pc["Cancelada pelo fornecedor"]} cancelada(s) separada(s) como "não lançar"')
    add('Entradas', 'Finalidade de cada item (atividade da empresa, NCM, fornecedor, perfil de venda)',
        f'{len(itens)} itens', fin.get('PENDENTE', 0))
    add('Entradas', 'CFOP de entrada x CFOP do fornecedor x UF de origem', f'{len(itens)} itens',
        sum(1 for i in itens if not i['CFOP sugerido'] and i['Finalidade'] != 'PENDENTE'))
    add('Entradas', 'Acumulador para cada CFOP sugerido', f'{len(itens)} itens',
        sum(1 for i in itens if i['CFOP sugerido'] and not i['Acum. sugerido']))
    add('Entradas', 'Crédito ICMS: CST/CSOSN (101 pelo vCredICMSSN; 102/103/500 sem crédito), finalidade',
        f'{len(itens)} itens', 0)
    add('Entradas', 'DIFAL base dupla em uso e consumo interestadual', f'{sum(1 for i in itens if i["DIFAL estimado"])} itens', 0)
    add('Entradas', 'Conta contábil por item', f'{len(itens)} itens',
        sum(1 for i in itens if not i['Conta contábil sugerida'] and i['Finalidade'] not in ('OUTRA OPERAÇÃO',)))
    add('Entradas', 'Classificação x histórico do Domínio', f'{len(notas_t)} notas', pc['Classificação x histórico'])
    add('CT-e', 'Tomador do frete, CFOP 1352/2352, acumulador e crédito', f'{len(res.get("cte", []))} CT-e',
        sum(1 for c in res.get('cte', []) if c['Status'] == 'A LANÇAR' and not c['Acum. sugerido']))
    add('Remessas', 'Retorno x remessa (conserto, industrialização, feira) por item', 'remessas do mês e do anterior',
        sum(1 for r in res.get('remessas', []) if r['Status'].startswith('RETORNO MAIOR')),
        f'{sum(1 for r in res.get("remessas", []) if r["Status"] == "AINDA NÃO RETORNOU")} item(ns) ainda fora')
    add('Saídas', 'CST x ICMS (tributado com imposto, isento com cBenef)', f'{len(res["saidas"])} notas',
        sum(1 for c in res.get('coerencia', []) if c['Tipo'].startswith('CST')))
    add('Saídas', 'Acumulador para cada CFOP de saída', f'{len(res["saidas"])} notas',
        sum(1 for s in res['saidas'] if 'SEM ACUMULADOR' in s['Status']))
    add('Saídas', 'Relatório do ERP x XML (situação, valor, base, ICMS, IPI, CFOP)', 'relatório do ERP',
        len(res.get('erp_xml', [])))
    add('Saídas', 'Total da nota = soma dos itens', f'{len(res["saidas"]) + len(res["devol"])} notas',
        sum(1 for c in res.get('coerencia', []) if c['Tipo'].startswith('Total')))
    add('Devoluções', 'CFOP, acumulador e CST das entradas emitidas pela empresa', f'{len(res["devol"])} notas',
        sum(1 for d in res['devol'] if d['Status'] not in ('OK', 'CANCELADA - OK')))
    add('Numeração', 'Sequência própria x XML x ERP (inutilizar / sem XML)', 'séries emitidas', len(res['lacunas']))
    add('Serviços', 'NFS-e: item LC 116 → acumulador, retenções, conta, competência', f'{len(res["nfse"])} NFS-e',
        sum(1 for x in res['nfse'] if x['Status'] == 'CONFERIR'))
    return ck
