"""Automação fiscal da COSMETICI - linha de comando.

Apurar um mês (gera planilha + TXT do Domínio):
  python fiscal_cosmetici.py apurar --mes 2026-09 --xml <pasta|zip|xml> [...] \
      [--sieg-produtos Relatorio_Detalhamento_Produtos.xlsx] [--sieg-cte Relatorio_CTe.xlsx] \
      [--sped SpedEFD-...-set.2026.txt] [--saida Cosmetici/Fiscal/2026-09] [--gravar-faturamento]

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
    args = p.parse_args(argv)
    return args.func(args)


if __name__ == '__main__':
    main()
