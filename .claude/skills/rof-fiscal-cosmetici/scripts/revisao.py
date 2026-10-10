"""Revisão automática das operações do mês: os cruzamentos que a contadora refazia à mão.

Cada verificação devolve divergências no formato da apuração (gravidade, tipo, documento, descrição, valor)
e alimenta o checklist da planilha (aba Checklist). Nada aqui altera valores da apuração: só aponta.

- Industrialização por encomenda (5124/6124) x retorno simbólico (5902/6902): insumo devolvido com CFOP de
  industrialização (em duplicidade com o retorno), industrialização sem insumo do encomendante, retorno que cita
  a nota de industrialização errada.
- Destinatário contribuinte (com IE) tratado como consumidor final (indIEDest 9 / indFinal 1) e mesmo CNPJ com
  UF diferente no mês.
- CFOP de revenda (5102/6102) em produto com IPI destacado (produção própria = 5101/5401).
- 5124 interna tributada x demais 5124 internas com diferimento (CST 51).
- Produto de saída sem grupo de IPI.
- Remessas recebidas para industrialização sem retorno no mês (estoque de terceiros).
- NFS-e tomadas: retenção de IRRF e PIS/COFINS/CSLL.
"""
import collections
import re

from apuracao import vcontabil

R = lambda x: round(x + 0.0, 2)

CFOP_INDUSTRIALIZACAO = {'5124', '6124', '5125', '6125'}
CFOP_RETORNO = {'5902', '6902', '5903', '6903'}
CFOP_REMESSA_RECEBIDA = {'5901', '6901', '5924', '6924', '5923', '6923'}
CFOP_REVENDA = {'5102', '6102'}
CFOP_PRODUTO = {'5101', '5102', '5401', '5403', '5405', '6101', '6102', '6401', '6403', '6404', '5124', '6124'}
CST_PIS_SEM_RECEITA = {'07', '08', '09', '49', '70', '71', '72', '73', '74', '75', '98', '99'}

# NFS-e: código do serviço (LC 116/03, 4 dígitos) -> (IRRF %, CSRF %, observação)
# IRRF 1,5% serviços profissionais (RIR/2018 art. 714); 1% limpeza, conservação, segurança, vigilância e
# mão de obra (art. 716); CSRF 4,65% (Lei 10.833/2003 art. 30; IN SRF 459/2004).
RETENCAO_NFSE = {
    '0401': (1.5, 4.65, 'medicina'), '0402': (1.5, 4.65, 'análises clínicas'), '0408': (1.5, 4.65, 'fisioterapia/fonoaudiologia'),
    '0410': (1.5, 4.65, 'nutrição'), '0412': (1.5, 4.65, 'odontologia'), '0416': (1.5, 4.65, 'psicologia'),
    '0201': (1.5, 4.65, 'pesquisa e desenvolvimento'), '0701': (1.5, 4.65, 'engenharia/arquitetura'),
    '0802': (1.5, 4.65, 'ensino e treinamento'), '1701': (1.5, 4.65, 'assessoria/consultoria'),
    '1703': (1.5, 4.65, 'planejamento/organização'), '1714': (1.5, 4.65, 'advocacia'), '1716': (1.5, 4.65, 'auditoria'),
    '1719': (1.5, 4.65, 'contabilidade'), '1720': (1.5, 4.65, 'consultoria econômica'), '1721': (1.5, 4.65, 'estatística'),
    '0710': (1.0, 4.65, 'limpeza'), '1102': (1.0, 4.65, 'vigilância/segurança'), '1705': (1.0, 4.65, 'mão de obra'),
    '1401': (0.0, 4.65, 'manutenção de máquinas/equipamentos'), '1402': (0.0, 4.65, 'assistência técnica'),
    '0705': (0.0, 4.65, 'reparação/conservação de imóveis'),
}
RETENCAO_CONFIRMAR = {'0421': 'atendimento médico móvel', '0713': 'dedetização (conservação?)', '1722': 'cobrança'}

BASE = {
    'ind': 'RICMS/PR (industrialização por encomenda: 5124 pela industrialização + 5902 retorno simbólico do insumo); '
           'Lei 10.147/2000 (5124 fora do monofásico: 0,65%/3%)',
    'final': 'LC 87/96 art. 6º e RICMS/PR Anexo IX (ST nas saídas para revenda); Ajuste SINIEF 07/05 (indIEDest/indFinal); '
             'LC 87/96 art. 13 §2º (IPI fora da base só entre contribuintes)',
    'revenda': 'Tabela CFOP (Ajuste SINIEF 07/01): 5101 produção do estabelecimento, 5102 mercadoria de terceiros; RIPI art. 35',
    'ipi': 'RIPI/2010 (Decreto 7.212) - grupo IPI obrigatório para produto industrializado (NT 2016.002)',
    'csrf': 'Lei 10.833/2003 art. 30 e 31 §3º (dispensa até R$ 10); RIR/2018 art. 714 e 716; IN SRF 459/2004',
}


def _norm(s):
    return re.sub(r'\W+', '', (s or '').upper())


def _refs_nf(txt):
    """Números de NF citados no texto (infCpl)."""
    return {int(x) for x in re.findall(r'(?:NF-?E?S?|NOTAS?\s+FISCA\w*)\s*(?:N[º°O.]*)?\s*:?\s*(\d{2,9})', (txt or '').upper())}


def _nf_industrializacao(txt):
    m = re.findall(r'INDUSTRIALIZA\w*\s+EFETUADA\s+NA\S*\s+(?:NF-?E?\s*)?(\d{2,9})', (txt or '').upper())
    return {int(x) for x in m}


def _doc(n):
    return f'NF {n["numero"]}/{n["serie"]} {n["dhemi"]:%d/%m} {n["dest_nome"] or ""}'.strip()


def revisar_saidas(a):
    div, obs = [], []
    saidas = a.saidas
    por_num = {n['numero']: n for n in saidas}
    por_dest = collections.defaultdict(list)
    for n in saidas:
        por_dest[n['dest_cnpj']].append(n)
    remessas_de = collections.defaultdict(list)
    for n in a.entradas:
        if any(i['cfop'] in CFOP_REMESSA_RECEBIDA for i in n['itens']):
            remessas_de[n['emit_cnpj']].append(n)

    # 1) insumo do encomendante devolvido com CFOP de industrialização
    retornos = [(m, i) for m in saidas for i in m['itens'] if i['cfop'] in CFOP_RETORNO]
    tot_dup = 0.0
    for n in saidas:
        for i in n['itens']:
            if i['cfop'] in CFOP_INDUSTRIALIZACAO and i['cst_icms'] in ('40', '41') and (i['cst_pis'] in CST_PIS_SEM_RECEITA or not i['cst_pis']):
                vc = R(vcontabil(i))
                dup = [m for m, j in retornos if m['dest_cnpj'] == n['dest_cnpj'] and _norm(j['xprod']) == _norm(i['xprod'])
                       and abs(vcontabil(j) - vc) < 0.01]
                extra = f' - o mesmo item foi devolvido também na NF {", ".join(str(m["numero"]) for m in dup)} ({dup[0]["itens"][0]["cfop"]})' if dup else ''
                div.append(('ALTA', 'Industrialização x retorno', _doc(n),
                            f'Item {i["n_item"]} ({i["xprod"]}) é insumo do cliente (CST {i["cst_icms"]}, PIS {i["cst_pis"]}) com CFOP {i["cfop"]} '
                            f'de industrialização{extra}. Retorno de insumo é 5902/6902; como está, R$ {vc:,.2f} entra no acumulador de '
                            f'industrialização e na base do PIS/COFINS e do IRPJ/CSLL', vc))
                tot_dup += vc
    if tot_dup:
        obs.append(f'Insumo de cliente emitido com CFOP 5124/6124 soma R$ {tot_dup:,.2f} (aba Divergências, "Industrialização x retorno"). '
                   f'Está na base do PIS/COFINS (0,65%/3% = R$ {R(tot_dup*0.0065):,.2f} + R$ {R(tot_dup*0.03):,.2f}) e do IRPJ/CSLL. '
                   f'Se a contadora confirmar que é retorno em duplicidade, tirar da base e pedir ao cliente a regularização (CC-e do CFOP não '
                   f'altera valores - Ajuste SINIEF 01/07; senão, nota de entrada/anulação conforme RICMS/PR).')

    # 2) industrialização sem insumo do encomendante (sem referência, sem retorno e sem remessa no mês)
    for n in saidas:
        itens = [i for i in n['itens'] if i['cfop'] in CFOP_INDUSTRIALIZACAO and i['cst_icms'] not in ('40', '41')]
        if not itens:
            continue
        tem_ret = any(i['cfop'] in CFOP_RETORNO for m in por_dest[n['dest_cnpj']] for i in m['itens'])
        if _refs_nf(n['infcpl']) or tem_ret or remessas_de.get(n['dest_cnpj']):
            continue
        vc = R(sum(vcontabil(i) for i in itens))
        liq = R(vc - sum(i['vicms'] for i in itens))
        div.append(('MÉDIA', 'Industrialização sem insumo', _doc(n),
                    f'CFOP {"/".join(sorted({i["cfop"] for i in itens}))} sem nota de remessa citada, sem retorno 5902/6902 e sem remessa recebida '
                    f'do cliente no mês. Confirmar o insumo enviado pelo encomendante; se não houve, é venda (5101/6101): PIS/COFINS '
                    f'monofásico 2,2%/10,3% em vez de 0,65%/3% (diferença ~R$ {R(liq*(0.022+0.103-0.0065-0.03)):,.2f}) e IPI tributado', vc))

    # 3) retorno simbólico citando a nota de industrialização errada
    nums = [n['numero'] for n in saidas]
    for n in saidas:
        if not any(i['cfop'] in CFOP_RETORNO for i in n['itens']):
            continue
        for x in _nf_industrializacao(n['infcpl']):
            alvo = por_num.get(x)
            if alvo is None and not (min(nums) <= x <= max(nums)):
                continue
            ok = alvo is not None and alvo['dest_cnpj'] == n['dest_cnpj'] and any(i['cfop'] in CFOP_INDUSTRIALIZACAO for i in alvo['itens'])
            if not ok:
                quem = f'que é de {alvo["dest_nome"]} (CFOP {"/".join(sorted({i["cfop"] for i in alvo["itens"]}))})' if alvo else 'que não existe no mês'
                certa = [m['numero'] for m in por_dest[n['dest_cnpj']] if any(i['cfop'] in CFOP_INDUSTRIALIZACAO for i in m['itens'])]
                div.append(('BAIXA', 'Industrialização x retorno', _doc(n),
                            f'Informações complementares citam a industrialização na NF {x}, {quem}'
                            + (f'; a do cliente é a NF {", ".join(map(str, certa))}' if certa else '') + ' - corrigir por CC-e', None))

    # 4) contribuinte com IE tratado como consumidor final / CNPJ com UF diferente
    for cnpj, ns in por_dest.items():
        if not cnpj or len(cnpj) != 14:
            continue
        ies = {n['dest_ie'] for n in ns if n['dest_ie']}
        contrib = [n for n in ns if n.get('ind_ie_dest') == '1']
        final = [n for n in ns if (n.get('ind_ie_dest') == '9' or n.get('ind_final') == '1')
                 and any(i['cfop'] in CFOP_PRODUTO - CFOP_INDUSTRIALIZACAO for i in n['itens'])]
        if final and (ies or contrib):
            vprod = R(sum(i['vprod'] - i['vdesc'] for n in final for i in n['itens']))
            st_antes = R(sum(i['vst'] for n in contrib for i in n['itens']))
            cfs = sorted({i['cfop'] for n in final for i in n['itens']})
            div.append(('ALTA', 'Contribuinte como consumidor final', f'{ns[0]["dest_nome"]} ({cnpj}, IE {", ".join(sorted(ies)) or "-"})',
                        f'{len(final)} nota(s) com indIEDest=9/indFinal=1 (NF {", ".join(str(n["numero"]) for n in final)}; CFOP {", ".join(cfs)}), '
                        f'sem ICMS-ST, ICMS cheio e IPI na base do ICMS'
                        + (f'; nas {len(contrib)} nota(s) do mês como contribuinte houve ST de R$ {st_antes:,.2f}' if contrib else '')
                        + '. Se o cliente revende, a ST não foi retida - confirmar o cadastro/finalidade com o cliente', vprod))
        ufs = {n['dest_uf'] for n in ns if n['dest_uf']}
        if len(ufs) > 1:
            div.append(('ALTA', 'Destinatário x UF', f'{ns[0]["dest_nome"]} ({cnpj})',
                        'Mesmo CNPJ com endereço em UFs diferentes no mês: ' + '; '.join(
                            f'{u}: NF {", ".join(str(n["numero"]) for n in ns if n["dest_uf"] == u)}' for u in sorted(ufs))
                        + ' - CFOP 6xxx e DIFAL dependem da UF; conferir o cadastro', None))

    # 5) CFOP de revenda com IPI destacado
    for n in saidas:
        itens = [i for i in n['itens'] if i['cfop'] in CFOP_REVENDA and i['vipi'] > 0]
        if itens:
            div.append(('MÉDIA', 'CFOP revenda x produção', _doc(n),
                        f'{len(itens)} item(ns) com CFOP {"/".join(sorted({i["cfop"] for i in itens}))} (mercadoria de terceiros) e IPI destacado - '
                        f'produto fabricado pela COSMETICI sai com 5101/6101 (ou 5401 com ST). Conferir CFOP e natureza "{n["natop"] or ""}"',
                        R(sum(vcontabil(i) for i in itens))))

    # 6) 5124 interna tributada enquanto as demais têm diferimento
    uf = a.cfg['empresa']['uf']
    internas = [(n, i) for n in saidas for i in n['itens'] if i['cfop'] == '5124' and i['cst_icms'] not in ('40', '41')]
    csts = collections.Counter(i['cst_icms'] for _, i in internas)
    if csts.get('51') and csts.get('00'):
        for n in {id(n): n for n, i in internas if i['cst_icms'] == '00'}.values():
            v = R(sum(i['vicms'] for i in n['itens'] if i['cfop'] == '5124' and i['cst_icms'] == '00'))
            div.append(('MÉDIA', 'Diferimento 5124', _doc(n),
                        f'5124 para {n["dest_uf"] or uf} com CST 00 (ICMS R$ {v:,.2f}) enquanto {csts["51"]} itens 5124 do mês saíram com '
                        f'diferimento (CST 51). Conferir se o diferimento se aplica a este cliente', v))

    # 7a) mesmo produto (cProd) com NCM ou IPI diferente nas vendas do mês
    trat = collections.defaultdict(lambda: collections.defaultdict(list))
    for n in saidas:
        for i in n['itens']:
            if i['cfop'] in CFOP_PRODUTO - CFOP_INDUSTRIALIZACAO:
                trat[i['cprod'] or _norm(i['xprod'])][(i['ncm'], i['cst_ipi'], i['pipi'])].append(n['numero'])
    for cod, t in trat.items():
        if len(t) > 1:
            nome = next(i['xprod'] for n in saidas for i in n['itens'] if (i['cprod'] or _norm(i['xprod'])) == cod)
            div.append(('MÉDIA', 'Produto com tratamento diferente', f'{nome} (cód. {cod})',
                        'Mesmo produto vendido no mês com NCM/IPI diferentes: ' + '; '.join(
                            f'NCM {k[0]} IPI CST {k[1] or "-"} {k[2]:g}% (NF {", ".join(map(str, sorted(set(v))))})' for k, v in t.items())
                        + ' - conferir o cadastro do produto (IPI a menor se a alíquota correta for a maior)', None))

    # 7b) PIS/COFINS informado no XML das industrializações x apuração (0,65%/3%)
    ind = [(n, i) for n in saidas for i in n['itens'] if i['cfop'] in CFOP_INDUSTRIALIZACAO and i['cst_pis'] in ('02', '04')]
    if ind:
        vc = R(sum(vcontabil(i) for _, i in ind))
        vp = R(sum(i['vpis'] for _, i in ind))
        vco = R(sum(i['vcof'] for _, i in ind))
        div.append(('BAIXA', 'PIS/COFINS no XML', f'{len({n["numero"] for n, _ in ind})} notas 5124/6124',
                    f'O XML informa PIS/COFINS monofásico (CST 02, {ind[0][1]["ppis"]:g}%) em R$ {vc:,.2f} de industrialização '
                    f'(PIS R$ {vp:,.2f} / COFINS R$ {vco:,.2f}); a apuração usa 0,65%/3% sobre a industrialização, como nos DARFs pagos. '
                    f'Na encomenda de produto monofásico a alíquota concentrada é do encomendante (Lei 11.051/2004, art. 10) - '
                    f'corrigir o cadastro fiscal do ERP (CST 01) e confirmar o entendimento com a contadora', None))

    # 7) produto sem grupo de IPI
    for n in saidas:
        itens = [i for i in n['itens'] if i['cfop'] in CFOP_PRODUTO and i['cst_icms'] not in ('40', '41') and not i['cst_ipi']]
        if itens:
            div.append(('BAIXA', 'Grupo IPI', _doc(n), f'{len(itens)} item(ns) de produto (CFOP {"/".join(sorted({i["cfop"] for i in itens}))}) '
                        f'sem grupo de IPI (CST) - conferir o cadastro do produto no ERP', None))
    return div, obs


def remessas_sem_retorno(a):
    """Remessas para industrialização recebidas no mês e não citadas em nenhum retorno do mês (estoque de terceiros)."""
    citadas = set()
    devolvidos = set()
    for n in a.saidas:
        if any(i['cfop'] in CFOP_RETORNO | CFOP_INDUSTRIALIZACAO for i in n['itens']):
            citadas |= _refs_nf(n['infcpl'])
        for i in n['itens']:
            if i['cfop'] in CFOP_RETORNO:
                devolvidos.add((n['dest_cnpj'], _norm(i['xprod'])[:20], R(vcontabil(i))))
    out = []
    for n in a.entradas:
        cfs = {i['cfop'] for i in n['itens']} & CFOP_REMESSA_RECEBIDA
        mesmo_item = all((n['emit_cnpj'], _norm(i['xprod'])[:20], R(vcontabil(i))) in devolvidos for i in n['itens'])
        if cfs and n['numero'] not in citadas and not mesmo_item:
            out.append(('BAIXA', 'Remessa sem retorno', f'NF {n["numero"]} {n["dhemi"]:%d/%m} {n["emit_nome"]}',
                        f'Remessa {"/".join(sorted(cfs))} recebida e ainda sem retorno citado no mês - fica no estoque de terceiros (controle)'
                        + (f'. {n["infcpl"].split("//")[-1].split("|")[0].strip()[:100]}' if re.search(r'CLIENTE|\bOS\b', (n['infcpl'] or '').upper()) else ''),
                        R(sum(vcontabil(i) for i in n['itens']))))
    return out


def revisar_nfse(lista):
    div = []
    for s in lista or []:
        doc = f'NFS-e {s["numero"]} {s["data"] or ""} {s["prestador"]}'
        cod = s['cod_servico']
        if s['cancelada']:
            continue
        base = s['base'] if s['base'] is not None else s['valor']
        retido = R(s['valor'] - s['liquido'] - s['desconto'] - s['iss_retido'])
        if s['simples']:
            if retido > 0.05:
                div.append(('BAIXA', 'NFS-e retenções', doc, f'Prestador do Simples com R$ {retido:,.2f} descontado - conferir (Simples não sofre IRRF/CSRF)', retido))
            continue
        if cod in RETENCAO_CONFIRMAR:
            div.append(('BAIXA', 'NFS-e retenções', doc, f'Serviço {cod} ({RETENCAO_CONFIRMAR[cod]}) de R$ {s["valor"]:,.2f}: confirmar se há '
                        f'retenção de IRRF/CSRF; descontado R$ {retido:,.2f}', None))
            continue
        if cod not in RETENCAO_NFSE:
            continue
        pir, pcs, desc = RETENCAO_NFSE[cod]
        ir = R(base * pir / 100)
        cs = R(base * pcs / 100)
        ir = ir if ir > 10 else 0.0
        cs = cs if cs > 10 else 0.0
        esperado = R(ir + cs)
        if esperado - retido > 0.05:
            div.append(('MÉDIA', 'NFS-e retenções', doc,
                        f'Serviço {cod} ({desc}) de R$ {s["valor"]:,.2f}, prestador fora do Simples: reter IRRF {pir:g}% R$ {ir:,.2f} + '
                        f'PIS/COFINS/CSLL 4,65% R$ {cs:,.2f} = R$ {esperado:,.2f}; descontado na nota R$ {retido:,.2f} '
                        f'(diferença R$ {R(esperado-retido):,.2f}). Conferir pagamento e DARF 1708/5952', R(esperado - retido)))
    return div


# ------------------------------------------------------------------ checklist

CHECKLIST = [
    ('Saídas', 'Numeração sequencial (buraco sem cancelamento/inutilização)', ['Numeração'], 'Ajuste SINIEF 07/05'),
    ('Saídas', 'ICMS e IPI recalculados (BC x alíquota) e CST x valor', ['ICMS recalculado', 'IPI recalculado', 'CST x valor'], 'LC 87/96 art. 13; RIPI art. 190'),
    ('Saídas', 'CFOP x UF do destinatário e alíquota interestadual', ['CFOP x UF', 'Alíquota interestadual', 'Destinatário x UF'], 'Res. Senado 22/89 e 13/12'),
    ('Saídas', 'CFOP com/sem ST x ST destacada', ['ST'], 'RICMS/PR Anexo IX'),
    ('Saídas', 'Contribuinte com IE tratado como consumidor final', ['Contribuinte como consumidor final'], BASE['final']),
    ('Saídas', 'CFOP de revenda (5102) em produto de fabricação própria', ['CFOP revenda x produção'], BASE['revenda']),
    ('Saídas', 'Industrialização 5124/6124 x retorno 5902/6902 x remessa do cliente', ['Industrialização x retorno', 'Industrialização sem insumo'], BASE['ind']),
    ('Saídas', 'Diferimento nas 5124 internas', ['Diferimento 5124'], 'RICMS/PR (diferimento)'),
    ('Saídas', 'Grupo de IPI nos produtos', ['Grupo IPI'], BASE['ipi']),
    ('Saídas', 'Mesmo produto com NCM/IPI diferentes no mês', ['Produto com tratamento diferente'], 'TIPI (Decreto 11.158/2022); RIPI art. 189'),
    ('Saídas', 'PIS/COFINS informado no XML x apuração', ['PIS/COFINS no XML'], 'Lei 10.147/2000; Lei 11.051/2004 art. 10'),
    ('Saídas', 'XML x Registro de Saídas do ERP (nota a nota: UF, CFOP, valores, ICMS, IPI, ST)', ['XML x Registro ERP'], 'Ajuste SINIEF 02/09 (EFD)'),
    ('Saídas', 'NCM x PIS/COFINS monofásico', ['PIS/COFINS monofásico'], 'Lei 10.147/2000'),
    ('Entradas', 'Fornecedor sem histórico (insumo x uso e consumo)', ['Fornecedor sem histórico'], 'LC 87/96 art. 20 e 33, I'),
    ('Entradas', 'Notas desconhecidas/manifestadas', ['Manifestação'], 'Ajuste SINIEF 07/05'),
    ('Entradas', 'Remessas recebidas sem retorno (estoque de terceiros)', ['Remessa sem retorno'], 'RICMS/PR (industrialização por encomenda)'),
    ('CT-e', 'Crédito do frete segue a natureza da NF-e transportada', ['CT-e sem crédito'], 'LC 87/96 art. 20 e 33, I'),
    ('Serviços', 'NFS-e tomadas: retenção de IRRF e PIS/COFINS/CSLL', ['NFS-e retenções'], BASE['csrf']),
    ('SPED', 'XML x SPED (notas faltando de um lado ou do outro)', ['SPED x XML'], 'Guia Prático EFD ICMS/IPI'),
]


def checklist(a, extras=None):
    """[(área, verificação, resultado, status, base legal)] - status OK / VERIFICAR / NÃO EXECUTADO."""
    cont = collections.defaultdict(collections.Counter)
    for g, tipo, *_ in a.div:
        cont[tipo][g] += 1
    linhas = []
    for area, desc, tipos, base in CHECKLIST:
        c = collections.Counter()
        for t in tipos:
            c.update(cont.get(t, {}))
        if tipos == ['NFS-e retenções'] and not a.f.get('nfse'):
            linhas.append((area, desc, 'Relatório de NFS-e não informado (--nfse)', 'NÃO EXECUTADO', base))
            continue
        if tipos == ['XML x Registro ERP'] and not a.f.get('registro_saidas'):
            linhas.append((area, desc, 'Registro de Saídas do ERP não informado (--registro-saidas)', 'NÃO EXECUTADO', base))
            continue
        if tipos == ['SPED x XML'] and not a.sped:
            linhas.append((area, desc, 'SPED do mês ainda não existe', 'NÃO EXECUTADO', base))
            continue
        if sum(c.values()):
            res = ', '.join(f'{v} {k}' for k, v in sorted(c.items(), key=lambda kv: ['ALTA', 'MÉDIA', 'BAIXA'].index(kv[0])))
            linhas.append((area, desc, res + ' (aba Divergências)', 'VERIFICAR' if c.get('ALTA') or c.get('MÉDIA') else 'INFORMATIVO', base))
        else:
            linhas.append((area, desc, 'Nenhuma ocorrência', 'OK', base))
    return linhas + list(extras or [])


def conferir_registro_saidas(a, reg):
    """Registro de Saídas do ERP (lista de dicts de leitores.ler_registro_saidas_erp) x XML, nota a nota."""
    if not reg:
        return []
    div = []
    xs = {n['numero']: n for n in a.saidas}
    canc = {n['numero'] for n in a.canceladas if n.get('propria')}
    por_num = {r['numero']: r for r in reg}
    for k, r in sorted(por_num.items()):
        n = xs.get(k)
        if n is None:
            if not r.get('cancelada') and k not in canc:
                div.append(('ALTA', 'XML x Registro ERP', f'NF {k}', 'Nota no Registro de Saídas do ERP sem XML autorizado no mês', r['vc']))
            continue
        it = [i for i in n['itens'] if i['cfop'] not in CFOP_RETORNO]
        x = {'uf': n['dest_uf'], 'cfop': '/'.join(sorted({i['cfop'] for i in it})), 'vc': R(sum(vcontabil(i) for i in it)),
             'bc_icms': R(sum(i['vbc'] for i in it)), 'icms': R(sum(i['vicms'] for i in it)), 'st': R(sum(i['vst'] for i in it)),
             'ipi': R(sum(i['vipi'] for i in it))}
        d = []
        if r['uf'] and x['uf'] != r['uf']:
            d.append(f'UF no XML {x["uf"]} x ERP {r["uf"]}')
        if r['cfop'] and r['cfop'] not in x['cfop'].split('/'):
            d.append(f'CFOP no XML {x["cfop"]} x ERP {r["cfop"]}')
        for c, rot in (('vc', 'valor contábil'), ('bc_icms', 'base ICMS'), ('icms', 'ICMS'), ('ipi', 'IPI')):
            if r.get(c) is not None and abs(x[c] - r[c]) > 0.01:
                d.append(f'{rot} XML {x[c]:,.2f} x ERP {r[c]:,.2f}')
        if r.get('outras_icms') is not None and x['st'] and abs(x['st'] - r['outras_icms']) > 0.01:
            d.append(f'ST XML {x["st"]:,.2f} x ERP {r["outras_icms"]:,.2f}')
        if d:
            div.append(('ALTA' if any(t.startswith(('UF', 'CFOP', 'ICMS', 'IPI')) for t in d) else 'MÉDIA', 'XML x Registro ERP',
                        _doc(n), '; '.join(d), None))
    sem = [n for k, n in xs.items() if k not in por_num]
    so_ret = [n for n in sem if {i['cfop'] for i in n['itens']} <= CFOP_RETORNO]
    outras = [n for n in sem if n not in so_ret]
    for n in outras:
        div.append(('ALTA', 'XML x Registro ERP', _doc(n), 'Nota com XML autorizado que não está no Registro de Saídas do ERP', n['vnf']))
    if so_ret:
        v = R(sum(vcontabil(i) for n in so_ret for i in n['itens']))
        div.append(('BAIXA', 'XML x Registro ERP', f'{len(so_ret)} notas de retorno 5902/6902',
                    f'O Registro de Saídas do ERP não lista as notas de retorno simbólico (R$ {v:,.2f}); no livro/SPED elas entram '
                    f'(C100/C190 com CFOP 5902/6902, sem débito) - conferir no Domínio', v))
    return div
