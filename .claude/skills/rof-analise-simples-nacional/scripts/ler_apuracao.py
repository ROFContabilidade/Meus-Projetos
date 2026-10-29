"""Lê os relatórios 'Produtos monofásicos/subst. trib.' do Domínio (um por mês) e gera apuracao.json.

Uso: python ler_apuracao.py MES1.xls MES2.xls ... -o apuracao.json
Para cada mês: RPA, RBT12, DAS e as seções (anexo, tabela, receita, alíquota, situação e alíquota de cada tributo)."""
import argparse, json, xlrd
from comum import abrir_xls, linhas

TRIB = ['IRPJ', 'CSLL', 'COFINS', 'PIS', 'CPP', 'ICMS']

def ler(caminho):
    s = abrir_xls(caminho).sheet_by_index(0)
    info = {'arquivo': caminho, 'secoes': []}
    sec = None
    for v in linhas(s):
        v = [x for x in v if str(x).strip() != '']
        if not v: continue
        k = str(v[0])
        if k == 'Período:': info['competencia'] = xlrd.xldate_as_datetime(v[1], 0).strftime('%m/%Y')
        elif k.startswith('Regime de Compet'): info['rpa'] = v[1]
        elif k.startswith('ao período de apuração (RBT12)'): info['rbt12'] = v[1]
        elif k == 'Anexo:': sec = {'anexo': v[1]}; info['secoes'].append(sec)
        elif k == 'Seção:' and sec is not None: sec['secao'] = v[1]
        elif k == 'Tabela:' and sec is not None: sec['tabela'] = v[1]
        elif k.startswith('Receita Tributada Total') and sec is not None: sec.update(receita=v[1], aliquota=v[3], das=v[5])
        elif k == 'Situação:' and sec is not None: sec['situacao'] = dict(zip(TRIB, v[1:7]))
        elif k == 'Alíquota:' and sec is not None and 'situacao' in sec and 'aliq_trib' not in sec:
            sec['aliq_trib'] = dict(zip(TRIB, v[1:7]))
        elif k == 'Valor:' and sec is not None and 'valor' not in sec: sec['valor'] = dict(zip(TRIB, v[1:7]))
        elif k.startswith('Simples Nacional a recolher'): info['das'] = v[1]
    # aba 'Anexo': receita mês a mês dos 12 meses anteriores (base do RBT12)
    wb = abrir_xls(caminho)
    for sh in wb.sheets():
        if sh.name.startswith('Anexo'):
            hist = []
            for v in linhas(sh):
                if isinstance(v[0], float) and v[0] > 30000:
                    vals = [x for x in v[1:] if isinstance(x, float)]
                    if vals: hist.append((xlrd.xldate_as_datetime(v[0], 0).strftime('%m/%Y'), vals[0]))
            info['historico_12m'] = hist
    mono = [x for x in info['secoes'] if x.get('situacao', {}).get('COFINS') == 'Trib. Monof.']
    norm = [x for x in info['secoes'] if x.get('situacao', {}).get('COFINS') == 'Tributado']
    info['receita_monofasica'] = sum(x.get('receita', 0) for x in mono)
    info['receita_normal'] = info.get('rpa', 0) - info['receita_monofasica']
    # alíquota de PIS+COFINS (% da receita) que deixa de ser zerada em 2027 – tirada da seção tributada normal do mês
    ref = norm[0] if norm else None
    info['aliq_pis_cofins'] = (ref['aliq_trib']['PIS'] + ref['aliq_trib']['COFINS']) if ref else None
    return info

if __name__ == '__main__':
    ap = argparse.ArgumentParser(); ap.add_argument('arquivos', nargs='+'); ap.add_argument('-o', default='apuracao.json')
    a = ap.parse_args()
    meses = sorted((ler(f) for f in a.arquivos), key=lambda x: x['competencia'][3:] + x['competencia'][:2])
    json.dump(meses, open(a.o, 'w'), ensure_ascii=False, indent=1, default=str)
    for m in meses:
        print(m['competencia'], 'RPA', m.get('rpa'), 'mono', round(m['receita_monofasica'], 2), 'DAS', m.get('das'), 'PIS+COFINS %', m['aliq_pis_cofins'])
