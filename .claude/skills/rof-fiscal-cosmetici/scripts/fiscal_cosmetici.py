"""Automação fiscal da COSMETICI - linha de comando.

Apurar um mês (gera planilha + TXT do Domínio):
  python fiscal_cosmetici.py apurar --mes 2026-09 --xml <pasta|zip|xml> [...] \
      [--sieg-produtos Relatorio_Detalhamento_Produtos.xlsx] [--sieg-cte Relatorio_CTe.xlsx] \
      [--sped SpedEFD-...-set.2026.txt] [--nfse RelatorioNFS_ABRASF_...xlsx] [--saida Cosmetici/Fiscal/2026-09] [--gravar-faturamento]

Aprender a classificação das entradas (CFOP/crédito por fornecedor e NCM) com um SPED já transmitido:
  python fiscal_cosmetici.py aprender --sped SpedEFD-...-ago.2026.txt

Faturamento (e PIS/COFINS de conferência) de um mês já fechado, pelo SPED transmitido:
  python fiscal_cosmetici.py faturamento-sped --sped SpedEFD-...-jul.2026.txt [--gravar]

Config padrão: Cosmetici/Fiscal/config/cosmetici.json e fornecedores.json (na raiz do repositório).
"""
import argparse
import collections
import json
import os
import sys

AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, AQUI)

import leitores  # noqa: E402
import planilha  # noqa: E402
import planilha_creditos  # noqa: E402
from creditos import Credito, conferir_entradas, conferir_saidas  # noqa: E402
import txt_dominio  # noqa: E402
from apuracao import Apuracao, faturamento_sped  # noqa: E402

RAIZ = os.path.abspath(os.path.join(AQUI, '..', '..', '..', '..'))
CONFIG = os.path.join(RAIZ, 'Cosmetici', 'Fiscal', 'config')


def carregar(nome, padrao=None):
    p = os.path.join(CONFIG, nome)
    if not os.path.exists(p):
        return padrao
    with open(p, encoding='utf-8') as fh:
        return json.load(fh)


def salvar(nome, dados):
    with open(os.path.join(CONFIG, nome), 'w', encoding='utf-8') as fh:
        json.dump(dados, fh, ensure_ascii=False, indent=2)
        fh.write('\n')


def cmd_aprender(args):
    s = leitores.ler_sped(args.sped)
    forn = carregar('fornecedores.json', {})
    novos = 0
    por_forn = collections.defaultdict(lambda: {'cfops': collections.Counter(), 'icms': False, 'ipi': False, 'ncm': {}})
    for d in s['docs']:
        if d['ind_oper'] != '0' or d['ind_emit'] != '1' or not d['cnpj'] or d['cod_sit'] not in ('00', '01'):
            continue
        f = por_forn[d['cnpj']]
        f['nome'] = d['nome']
        for x in d['c190']:
            f['cfops'][x['cfop']] += x['vl_opr']
            f['icms'] |= x['vl_icms'] > 0
            f['ipi'] |= x['vl_ipi'] > 0
        for it in d['c170']:
            ncm = (s['itens'].get(it['cod_item'], {}).get('ncm') or '')[:8]
            if ncm:
                f['ncm'][ncm] = {'cfop': it['cfop'], 'icms': it['vl_icms'] > 0, 'ipi': it['vl_ipi'] > 0}
    for cnpj, f in por_forn.items():
        if cnpj not in forn:
            novos += 1
        antigo = forn.get(cnpj, {})
        ncm = dict(antigo.get('ncm', {}))
        ncm.update(f['ncm'])
        forn[cnpj] = {'nome': f['nome'], 'cfop': f['cfops'].most_common(1)[0][0], 'icms': f['icms'], 'ipi': f['ipi'],
                      'ncm': ncm, 'ultimo_sped': f'{s["periodo"][0][2:4]}/{s["periodo"][0][4:]}'}
    salvar('fornecedores.json', dict(sorted(forn.items(), key=lambda kv: kv[1]['nome'] or '')))
    print(f'{len(por_forn)} fornecedores no SPED ({novos} novos). Total no cadastro: {len(forn)}.')


def cmd_faturamento_sped(args):
    cfg = carregar('cosmetici.json')
    s = leitores.ler_sped(args.sped)
    r = faturamento_sped(s, cfg)
    mes = f'{s["periodo"][0][4:]}-{s["periodo"][0][2:4]}'
    print(f'{mes}: vendas {r["venda"]:,.2f} + industrialização {r["industrializacao"]:,.2f} - devoluções {r["devolucoes"]:,.2f} '
          f'- ST {r["st"]:,.2f} - IPI {r["ipi"]:,.2f} = {r["liquido"]:,.2f} | PIS {r["pis"]:,.2f} | COFINS {r["cofins"]:,.2f}')
    if args.gravar:
        cfg.setdefault('faturamento_mensal', {})[mes] = {'valor': r['liquido'], 'origem': f'SPED {os.path.basename(args.sped)}'}
        cfg['faturamento_mensal'] = dict(sorted(cfg['faturamento_mensal'].items()))
        salvar('cosmetici.json', cfg)
        print('Gravado no config.')


def fontes_da_pasta(pasta):
    """Pasta do mês organizada pela rotina (ou qualquer pasta): acha XML/ZIP, relatórios SIEG e o SPED."""
    xml, prod, cte, sped = [], [], [], []
    for raiz, _, arqs in os.walk(pasta):
        for a in sorted(arqs):
            c, al = os.path.join(raiz, a), a.lower()
            if al.endswith(('.xml', '.zip')):
                xml.append(c)
            elif al.endswith('.xlsx') and al.startswith('relatorio_detalhamento_produtos'):
                prod.append(c)
            elif al.endswith('.xlsx') and al.startswith('relatorio_cte'):
                cte.append(c)
            elif al.endswith('.txt') and al.startswith('spedefd'):
                sped.append(c)
    sped.sort(key=lambda c: ('substituto' in c.lower(), c))
    return xml, prod, cte, (sped[-1] if sped else None)


def nfse_da_pasta(pasta):
    return [os.path.join(r, a) for r, _, arqs in os.walk(pasta) for a in sorted(arqs)
            if a.lower().startswith('relatorionfs_abrasf') and a.lower().endswith('.xlsx')]


def carregar_registro(args):
    arqs = list(getattr(args, 'registro_saidas', None) or [])
    if args.pasta:
        arqs += [os.path.join(r, a) for r, _, aa in os.walk(args.pasta) for a in sorted(aa)
                 if a.lower().endswith('.pdf') and 'saida' in a.lower()]
    return [x for p in arqs for x in leitores.ler_registro_saidas_erp(p)]


def carregar_nfse(args):
    arqs = list(args.nfse or []) + (nfse_da_pasta(args.pasta) if args.pasta else [])
    return [s for p in arqs for s in leitores.ler_relatorio_nfse_abrasf(p)]


def cmd_apurar(args):
    cfg = carregar('cosmetici.json')
    if args.pasta:
        x, p, c, s = fontes_da_pasta(args.pasta)
        args.xml = (args.xml or []) + x
        args.sieg_produtos = (args.sieg_produtos or []) + p
        args.sieg_cte = (args.sieg_cte or []) + c
        args.sped = args.sped or s
        print(f'Pasta {args.pasta}: {len(x)} XML/ZIP, {len(p)} relatório(s) de produtos, {len(c)} de CT-e, SPED: {os.path.basename(s) if s else "-"}')
    forn = carregar('fornecedores.json', {})
    fontes = leitores.ler_xmls(args.xml or [])
    for p in args.sieg_produtos or []:
        for ch, n in leitores.ler_sieg_produtos(p).items():
            fontes['nfe'].setdefault(ch, n)
    for p in args.sieg_cte or []:
        for ch, c in leitores.ler_sieg_cte(p).items():
            fontes['cte'].setdefault(ch, c)
    sped = leitores.ler_sped(args.sped) if args.sped else None
    fontes['nfse'] = carregar_nfse(args)
    fontes['registro_saidas'] = carregar_registro(args)
    a = Apuracao(cfg, args.mes, fontes, forn, sped).executar()

    saida = args.saida or os.path.join(RAIZ, 'Cosmetici', 'Fiscal', args.mes)
    os.makedirs(saida, exist_ok=True)
    mm = f'{args.mes[5:]}-{args.mes[:4]}'
    xlsx = os.path.join(saida, f'Apuracao_Fiscal_Cosmetici_{mm}.xlsx')
    planilha.gerar(a, xlsx)
    txt = os.path.join(saida, f'Lancamentos_Fiscais_Cosmetici_{mm}.txt')
    lanc, sem_conta = txt_dominio.gerar(a, txt)

    print(f'== COSMETICI {mm} ==')
    print(f'XML lidos: {len(fontes["nfe"])} NF-e, {len(fontes["eventos"])} eventos, {len(fontes["inut"])} inutilizações, {len(fontes["cte"])} CT-e'
          + (f', {len(fontes["erros"])} com erro' if fontes['erros'] else ''))
    print(f'Saídas {len(a.saidas)} | canceladas {len(a.canceladas)} | entradas {len(a.entradas)} | CT-e tomados {len(a.ctes)} | '
          f'fora do mês {len(a.fora_periodo)}')
    print(f'Faturamento líquido: {a.fat["liquido"]:>14,.2f}')
    for nome, guia, v, venc in a.guias():
        print(f'  {nome:<14}{guia:<34}{v:>14,.2f}  venc. {venc:%d/%m/%Y}')
    if not a.ir['fechamento']:
        situacao = f'faltam {", ".join(a.ir["faltam"])}' if a.ir['faltam'] else 'trimestre em andamento'
        print(f'  IRPJ/CSLL {a.ir["trimestre"]} até este mês: receita {a.ir["receita"]:,.2f} ({situacao})')
    if a.conf:
        print('Conferência com o SPED:')
        for rot, v1, v2 in a.conf:
            print(f'  {rot:<26}{v1:>14,.2f}{(v2 if v2 is not None else float("nan")):>14,.2f}  dif {0 if v2 is None else v1 - v2:,.2f}')
    cont = collections.Counter(d[0] for d in a.div)
    print(f'Divergências: {dict(cont)} | observações: {len(a.obs)}')
    print(f'Planilha: {xlsx}')
    if lanc:
        print(f'TXT Domínio: {txt} ({len(lanc)} lançamentos)')
    if sem_conta:
        print('Sem conta no config (fora do TXT): ' + ', '.join(f'{i} {v:,.2f}' for i, v in sem_conta))
    if args.gravar_faturamento:
        cfg.setdefault('faturamento_mensal', {})[args.mes] = {'valor': a.fat['liquido'], 'origem': f'apuração automática ({len(a.saidas)} NF-e)'}
        cfg['faturamento_mensal'] = dict(sorted(cfg['faturamento_mensal'].items()))
        salvar('cosmetici.json', cfg)
        print('Faturamento do mês gravado no config.')
    return a


def cmd_creditos(args):
    cfg = carregar('cosmetici.json')
    forn = carregar('fornecedores.json', {})
    xml, prod, cte_rel, _ = fontes_da_pasta(args.pasta) if args.pasta else ([], [], [], None)
    fontes = leitores.ler_xmls((args.xml or []) + xml)
    sieg = {}
    for p in (args.sieg_produtos or []) + prod:
        sieg.update(leitores.ler_sieg_produtos(p))
    fontes['nfse'] = carregar_nfse(args)
    fontes['registro_saidas'] = carregar_registro(args)
    a = Apuracao(cfg, args.mes, fontes, forn).executar()
    extra = []
    if args.cte_json:
        with open(args.cte_json, encoding='utf-8') as fh:
            extra = json.load(fh)['cte']
        for x in extra:
            x['data'] = leitores.dt.date.fromisoformat(x['data'])
    c = Credito(a, forn, extra, cfg.get('natureza_entradas', {})).analisar()
    erp = leitores.ler_relatorio_faturamento_erp(args.relatorio_erp) if args.relatorio_erp else None
    cs = conferir_saidas(a, erp, sieg or None)
    ce = conferir_entradas(a, sieg or None)
    saida = args.saida or os.path.join(RAIZ, 'Cosmetici', 'Fiscal', args.mes)
    os.makedirs(saida, exist_ok=True)
    destino = os.path.join(saida, f'Creditos_Entradas_Cosmetici_{args.mes[5:]}-{args.mes[:4]}.xlsx')
    import revisao
    planilha_creditos.gerar(c, cs, ce, destino, revisao.analisar_nfse(fontes.get('nfse'), cfg.get('acumuladores_servicos')))
    t = c.totais()
    print(f'== Créditos COSMETICI {args.mes} ==  entradas {len(a.entradas)} notas / {len(c.linhas)} itens')
    for k, rot in [('icms', 'ICMS NF-e regime normal'), ('sn', 'ICMS Simples (vCredICMSSN)'), ('cte_xml', 'ICMS CT-e com XML'),
                   ('cte_pend', 'ICMS CT-e sem XML (pendente)'), ('pot_sn', 'Simples potencial (valor zerado)'),
                   ('confirmar', 'ICMS a confirmar'), ('ipi', 'IPI'), ('difal', 'DIFAL estimado')]:
        print(f'  {rot:<34}{t.get(k, 0):>12,.2f}')
    print(f'Saídas conferidas: {sum(x["obs"] == "OK" for x in cs)} OK de {len(cs)} | entradas: {sum(x["obs"] == "OK" for x in ce)} OK de {len(ce)}')
    for x in cs + ce:
        if x['obs'] != 'OK':
            print('  ', x['numero'], x['obs'])
    print(f'Planilha: {destino}')
    return c


def cmd_saidas(args):
    import planilha_saidas
    cfg = carregar('cosmetici.json')
    xml = list(args.xml or [])
    if args.pasta:
        xml += fontes_da_pasta(args.pasta)[0]
    a = Apuracao(cfg, args.mes, leitores.ler_xmls(xml), carregar('fornecedores.json', {})).executar()
    saida = args.saida or os.path.join(RAIZ, 'Cosmetici', 'Fiscal', args.mes)
    os.makedirs(saida, exist_ok=True)
    destino = os.path.join(saida, f'Relacao_Saidas_Cosmetici_{args.mes[5:]}-{args.mes[:4]}.xlsx')
    conf = planilha_saidas.conferencia_erp(os.path.join(saida, f'Cruzamento_Relatorios_ERP_x_XML_{args.mes[5:]}-{args.mes[:4]}.xlsx'))
    rows = planilha_saidas.gerar(a, destino, conf)
    cont = collections.Counter(r['situacao'] for r in rows)
    print(f'Saídas {args.mes}: {dict(cont)} | planilha: {destino}')
    return rows


def _fontes_entradas(args):
    """XML de NF-e/CT-e/NFS-e e relatórios SIEG das entradas -> (apuração, SIEG produtos, SIEG CT-e, ABRASF, NFS-e XML, fontes)."""
    import glob
    cfg = carregar('cosmetici.json')
    xml = list(args.xml or [])
    prod, cte_rel = list(args.sieg_produtos or []), list(args.sieg_cte or [])
    nfse_rel, nfse_xml = list(args.nfse or []), list(args.nfse_xml or [])
    if args.pasta:
        x, p, c, _ = fontes_da_pasta(args.pasta)
        xml += [a for a in x if not a.lower().endswith('.xml') or '<NFSe' not in open(a, 'rb').read(400).decode('latin-1', 'ignore')]
        prod += p; cte_rel += c; nfse_rel += nfse_da_pasta(args.pasta)
        nfse_xml += [a for a in glob.glob(os.path.join(args.pasta, '**', '*.xml'), recursive=True)
                     if b'sped.fazenda.gov.br/nfse' in open(a, 'rb').read(600)]
    fontes = leitores.ler_xmls(xml)
    a = Apuracao(cfg, args.mes, fontes, carregar('fornecedores.json', {})).executar()
    sp = {}
    for p in prod:
        sp.update(leitores.ler_sieg_produtos(p))
    sc = {}
    for c in cte_rel:
        sc.update(leitores.ler_sieg_cte(c))
    rn = [s for p in nfse_rel for s in leitores.ler_relatorio_nfse_abrasf(p)]
    xn = [n for n in (leitores.ler_nfse_nacional(p) for p in nfse_xml) if n]
    return a, sp, sc, rn, xn, fontes


def cmd_entradas(args):
    import planilha_entradas
    a, sp, sc, rn, xn, fontes = _fontes_entradas(args)
    saida = args.saida or os.path.join(RAIZ, 'Cosmetici', 'Fiscal', args.mes)
    os.makedirs(saida, exist_ok=True)
    destino = os.path.join(saida, f'Relacao_Entradas_Cosmetici_{args.mes[5:]}-{args.mes[:4]}.xlsx')
    r = planilha_entradas.gerar(a, carregar('fornecedores.json', {}), fontes['cte'], sc, xn, destino, sp or None, rn or None)
    for k in ('todas', 'dentro', 'fora', 'cte', 'nfse'):
        print(f'{k}: {len(r[k])}')
    print('NFS-e com retenção:', [(x['numero'], x['emitente'][:20], x['tem_ret']) for x in r['nfse'] if x['tem_ret'] != 'Não'])
    print(f'Planilha: {destino}')


def cmd_contabil(args):
    """Lançamentos contábeis das entradas no leiaute TXT do Domínio (rascunho para conferência)."""
    import lancamentos_contabeis as lc
    a, _, sc, _, xn, fontes = _fontes_entradas(args)
    forn = carregar('fornecedores.json', {})
    if args.lancamentos_escrita:
        n = sum(lc.aprender(lc.ler_escrita(p), forn) for p in args.lancamentos_escrita)
        salvar('fornecedores.json', forn)
        print(f'Aprendido do Domínio: {n} lançamentos com conta por fornecedor')
    cred = Credito(a, forn, [], a.cfg.get('natureza_entradas', {})).analisar()
    lanc, pend = lc.montar(a, cred, fontes['cte'], sc, xn, forn)
    saida = args.saida or os.path.join(RAIZ, 'Cosmetici', 'Fiscal', args.mes)
    os.makedirs(saida, exist_ok=True)
    mm = f'{args.mes[5:]}-{args.mes[:4]}'
    txt = os.path.join(saida, f'Lancamentos_Contabeis_Entradas_Cosmetici_{mm}_RASCUNHO.txt')
    xlsx = os.path.join(saida, f'Lancamentos_Contabeis_Entradas_Cosmetici_{mm}.xlsx')
    linhas = lc.gerar_txt(a.cnpj, lanc, txt)
    lc.gerar_planilha(lanc, pend, xlsx, f'COSMETICI {args.mes[5:]}/{args.mes[:4]} - lançamentos contábeis das entradas')
    tot = sum(v for x in lanc for _, b in x['blocos'] for d, _, v, _ in b if d)
    print(f'Lançamentos: {len(lanc)} documentos, {linhas} linhas no TXT, débitos {tot:,.2f} | pendentes: {len(pend)}')
    for x in pend:
        print('  pendente:', x['doc'], x['numero'], x['nome'][:30], f'{x["valor"]:,.2f}', '-', x['motivo'])
    print(f'TXT: {txt}\nPlanilha: {xlsx}')


def cmd_importacao(args):
    """TXT de importação das notas na Escrita Fiscal do Domínio (leiaute SPED EFD ICMS/IPI aceito pelo Domínio)."""
    import lancamentos_contabeis as lc
    import sped_importacao
    a, _, sc, _, xn, fontes = _fontes_entradas(args)
    forn = carregar('fornecedores.json', {})
    cred = Credito(a, forn, [], a.cfg.get('natureza_entradas', {})).analisar()
    lanc, _ = lc.montar(a, cred, fontes['cte'], sc, xn, forn)
    contas = {(x['chave'], x['cfop']): next(ln[0] for _, b in x['blocos'] for ln in b if ln[0]) for x in lanc if x['doc'] == 'NF-e'}
    saida = args.saida or os.path.join(RAIZ, 'Cosmetici', 'Fiscal', args.mes)
    os.makedirs(saida, exist_ok=True)
    destino = os.path.join(saida, f'IMPORTACAO_DOMINIO_{args.mes[5:]}{args.mes[:4]}.TXT')
    s, linhas = sped_importacao.gerar(a, cred, fontes['cte'], sc, contas, a.cfg['sped_cabecalho'], destino)
    docs, itens, dif = sped_importacao.auditar(linhas, a, fontes['cte'])
    print(f'Conferência TXT x XML: {docs} documentos, {itens} itens, {len(dif)} diferenças')
    for d in dif[:30]:
        print('  DIFERENÇA', d)
    cont = collections.Counter(x.split('|')[1] for x in linhas)
    print('Registros:', ', '.join(f'{k} {v}' for k, v in cont.items() if k in ('0150', '0200', '0400', 'C100', 'C170', 'C190', 'D100')))
    for p in s.pend:
        print('  fora do arquivo:', *p)
    print(f'TXT: {destino}')
    return s, linhas


def cmd_cruzar_entradas(args):
    import cruzamento_entradas
    a, sp, sc, rn, xn, fontes = _fontes_entradas(args)
    saida = args.saida or os.path.join(RAIZ, 'Cosmetici', 'Fiscal', args.mes)
    os.makedirs(saida, exist_ok=True)
    destino = os.path.join(saida, f'Cruzamento_Entradas_Relatorios_x_XML_{args.mes[5:]}-{args.mes[:4]}.xlsx')
    ln, lc, ls = cruzamento_entradas.gerar(a, sp, fontes['cte'], sc, xn, rn, destino)
    li = cruzamento_entradas.nfe_itens(a, sp)
    for nome, lin, col in (('NF-e', ln, 18), ('NF-e itens', li, 18), ('CT-e', lc, 15), ('NFS-e', ls, 24)):
        print(f'{nome}: {len(lin)} | ' + ', '.join(f'{k}: {v}' for k, v in collections.Counter(str(x[col])[:45] for x in lin).items()))
    print(f'Planilha: {destino}')


def main(argv=None):
    p = argparse.ArgumentParser(description='Automação fiscal COSMETICI')
    sub = p.add_subparsers(dest='cmd', required=True)
    ap = sub.add_parser('apurar')
    ap.add_argument('--mes', required=True, help='AAAA-MM')
    ap.add_argument('--pasta', help='pasta do mês (ex.: a MM_AAAA organizada pela rotina) - acha XML, ZIP, relatórios SIEG e SPED')
    ap.add_argument('--xml', nargs='*', help='pastas, ZIPs ou XML (saídas, entradas, eventos, CT-e - pode misturar)')
    ap.add_argument('--sieg-produtos', nargs='*', help='Relatorio_Detalhamento_Produtos.xlsx (SIEG)')
    ap.add_argument('--sieg-cte', nargs='*', help='Relatorio_CTe.xlsx (SIEG)')
    ap.add_argument('--sped', help='SPED Fiscal do mesmo mês (para conferência)')
    ap.add_argument('--nfse', nargs='*', help='RelatorioNFS_ABRASF_*.xlsx (NFS-e tomadas - confere retenções)')
    ap.add_argument('--registro-saidas', nargs='*', help='Registro de Saídas do ERP (Saidas Cosmetici.pdf ou .txt)')
    ap.add_argument('--saida', help='pasta de saída')
    ap.add_argument('--gravar-faturamento', action='store_true', help='grava o faturamento do mês no config (IRPJ/CSLL)')
    ap.set_defaults(func=cmd_apurar)
    al = sub.add_parser('aprender')
    al.add_argument('--sped', required=True)
    al.set_defaults(func=cmd_aprender)
    fs = sub.add_parser('faturamento-sped')
    fs.add_argument('--sped', required=True)
    fs.add_argument('--gravar', action='store_true')
    fs.set_defaults(func=cmd_faturamento_sped)
    cr = sub.add_parser('creditos', help='análise de crédito das entradas + conferência XML x relatórios')
    cr.add_argument('--mes', required=True)
    cr.add_argument('--pasta')
    cr.add_argument('--xml', nargs='*')
    cr.add_argument('--sieg-produtos', nargs='*')
    cr.add_argument('--relatorio-erp', help='Relatório de Faturamento do ERP (PDF)')
    cr.add_argument('--cte-json', help='CT-e sem XML transcritos do relatório SIEG')
    cr.add_argument('--nfse', nargs='*', help='RelatorioNFS_ABRASF_*.xlsx (NFS-e tomadas)')
    cr.add_argument('--registro-saidas', nargs='*', help='Registro de Saídas do ERP (Saidas Cosmetici.pdf ou .txt)')
    cr.add_argument('--saida')
    cr.set_defaults(func=cmd_creditos)
    ce = sub.add_parser('cruzar-entradas', help='XML de NF-e/CT-e/NFS-e x relatórios SIEG (produtos, CT-e, NFS-e ABRASF)')
    ce.add_argument('--mes', required=True)
    ce.add_argument('--pasta')
    ce.add_argument('--xml', nargs='*')
    ce.add_argument('--sieg-produtos', nargs='*')
    ce.add_argument('--sieg-cte', nargs='*')
    ce.add_argument('--nfse', nargs='*', help='RelatorioNFS_ABRASF_*.xlsx')
    ce.add_argument('--nfse-xml', nargs='*', help='XML das NFS-e (padrão nacional)')
    ce.add_argument('--saida')
    ce.set_defaults(func=cmd_cruzar_entradas)
    en = sub.add_parser('entradas', help='relação das notas de entrada: todas, NF-e dentro/fora do estado, CT-e, NFS-e com retenções')
    for arg in ('--pasta', '--saida'):
        en.add_argument(arg)
    en.add_argument('--mes', required=True)
    for arg in ('--xml', '--sieg-produtos', '--sieg-cte', '--nfse', '--nfse-xml'):
        en.add_argument(arg, nargs='*')
    en.set_defaults(func=cmd_entradas)
    co = sub.add_parser('contabil', help='lançamentos contábeis das entradas (TXT Domínio |0000|/|6000|/|6100|), rascunho')
    for arg in ('--pasta', '--saida'):
        co.add_argument(arg)
    co.add_argument('--mes', required=True)
    for arg in ('--xml', '--sieg-produtos', '--sieg-cte', '--nfse', '--nfse-xml'):
        co.add_argument(arg, nargs='*')
    co.add_argument('--lancamentos-escrita', nargs='*', help='Lançamentos.xls (Lançamentos gerados pela Escrita) para aprender as contas')
    co.set_defaults(func=cmd_contabil)
    im = sub.add_parser('importacao', help='TXT de importação das notas no Domínio (leiaute SPED EFD ICMS/IPI)')
    for arg in ('--pasta', '--saida'):
        im.add_argument(arg)
    im.add_argument('--mes', required=True)
    for arg in ('--xml', '--sieg-produtos', '--sieg-cte', '--nfse', '--nfse-xml'):
        im.add_argument(arg, nargs='*')
    im.set_defaults(func=cmd_importacao)
    sa = sub.add_parser('saidas', help='relação das notas de saída do mês (XML, canceladas, inutilizadas, sugestão de importação)')
    sa.add_argument('--mes', required=True)
    sa.add_argument('--pasta')
    sa.add_argument('--xml', nargs='*')
    sa.add_argument('--saida')
    sa.set_defaults(func=cmd_saidas)
    args = p.parse_args(argv)
    return args.func(args)


if __name__ == '__main__':
    main()
