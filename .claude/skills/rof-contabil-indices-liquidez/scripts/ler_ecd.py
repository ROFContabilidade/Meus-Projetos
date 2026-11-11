#!/usr/bin/env python3
"""Lê uma ECD (SPED Contábil, leiaute 9 ou posterior) e grava um JSON com:
- empresa (nome, CNPJ, exercício)
- balanço de abertura e de encerramento do exercício (J100), com sinal
- DRE do exercício (J150), somando os blocos J005 (trimestres, semestres) quando houver mais de um
- componentes dos índices (AC, Estoques, RLP, AT, PC, ELP, PL) nas duas datas

Uso: python3 ler_ecd.py <arquivo_ECD.txt> -o dados.json
Sinal: no Ativo, saldo devedor = positivo; no Passivo/PL, saldo credor = positivo.
Na DRE: credor (receita) = positivo; devedor (custo/despesa) = negativo.
"""
import argparse, json, re, sys, unicodedata

def norm(s):
    s = unicodedata.normalize('NFKD', s).encode('ascii', 'ignore').decode().upper()
    return re.sub(r'[^A-Z ]', ' ', s)

def num(v):
    return float(v.replace('.', '').replace(',', '.')) if v else 0.0

def ler(caminho):
    linhas = []
    with open(caminho, 'rb') as f:
        for raw in f:
            if not raw.startswith(b'|'):
                continue
            try:
                t = raw.decode('utf-8')
            except UnicodeDecodeError:
                t = raw.decode('latin-1')
            linhas.append(t.rstrip('\r\n').split('|'))
    return linhas

def sinal_bp(grp, valor, dc):
    if grp == 'A':
        return valor if dc == 'D' else -valor
    return valor if dc == 'C' else -valor

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('ecd'); ap.add_argument('-o', '--out', default='dados.json')
    a = ap.parse_args()
    L = ler(a.ecd)
    emp = {}
    blocos = []   # cada J005: {'ini','fim','j100':[...],'j150':[...]}
    for f in L:
        reg = f[1]
        if reg == '0000':
            emp = {'nome': f[5], 'cnpj': f[6], 'inicio': f[3], 'fim': f[4]}
        elif reg == 'I010':
            emp['leiaute'] = f[3]
        elif reg == 'J005':
            blocos.append({'ini': f[2], 'fim': f[3], 'j100': [], 'j150': []})
        elif reg == 'J100' and blocos:
            blocos[-1]['j100'].append(dict(cod=f[2], tipo=f[3], nivel=int(f[4] or 0), sup=f[5], grp=f[6],
                                           descr=f[7], vi=num(f[8]), dci=f[9], vf=num(f[10]), dcf=f[11]))
        elif reg == 'J150' and blocos:
            blocos[-1]['j150'].append(dict(ordem=f[2], cod=f[3], tipo=f[4], nivel=int(f[5] or 0), sup=f[6],
                                           descr=f[7], vi=num(f[8]), dci=f[9], vf=num(f[10]), dcf=f[11]))
    if not blocos:
        sys.exit('ECD sem registro J005/J100 (demonstrações não encontradas).')
    try:
        if float(emp.get('leiaute', '9')) < 9:
            print('AVISO: leiaute anterior ao 9.00; confira o J100/J150 manualmente.', file=sys.stderr)
    except ValueError:
        pass

    # ---- Balanço: abertura = saldo inicial do 1º bloco; encerramento = saldo final do último
    prim, ult = blocos[0], blocos[-1]
    def dt(d): return f'{d[:2]}/{d[2:4]}/{d[4:]}'
    abertura = {x['cod']: sinal_bp(x['grp'], x['vi'], x['dci']) for x in prim['j100']}
    encerra = {x['cod']: sinal_bp(x['grp'], x['vf'], x['dcf']) for x in ult['j100']}
    # estrutura: a do último bloco + contas que só existiam no primeiro
    estrutura, vistos = [], set()
    for x in ult['j100'] + prim['j100']:
        if x['cod'] not in vistos:
            vistos.add(x['cod']); estrutura.append(x)
    # reordena: filhos logo após o pai, na ordem em que aparecem
    filhos = {}
    for x in estrutura:
        filhos.setdefault(x['sup'], []).append(x)
    ordenada = []
    def visita(sup):
        for x in filhos.get(sup, []):
            ordenada.append(x); visita(x['cod'])
    visita('')
    for x in estrutura:          # órfãos (pai ausente), se houver
        if x not in ordenada:
            ordenada.append(x)
    bp = []
    for x in ordenada:
        v1, v0 = encerra.get(x['cod'], 0.0), abertura.get(x['cod'], 0.0)
        if abs(v1) < 0.005 and abs(v0) < 0.005:
            continue
        bp.append(dict(cod=x['cod'], tipo=x['tipo'], nivel=x['nivel'], sup=x['sup'], grp=x['grp'],
                       descr=x['descr'].strip(), atual=round(v1, 2), anterior=round(v0, 2)))

    # ---- Componentes dos índices
    def acha(pred, nivel=None):
        return [x for x in bp if pred(norm(x['descr'])) and (nivel is None or x['nivel'] == nivel)]
    def soma(lst, campo): return round(sum(x[campo] for x in lst), 2)
    n2 = [x for x in bp if x['nivel'] == 2]
    AC = [x for x in n2 if x['grp'] == 'A' and 'NAO' not in norm(x['descr']) and 'CIRCULANTE' in norm(x['descr'])]
    ANC = [x for x in n2 if x['grp'] == 'A' and x not in AC]
    PC = [x for x in n2 if x['grp'] == 'P' and 'NAO' not in norm(x['descr']) and 'CIRCULANTE' in norm(x['descr'])
          and 'PATRIMONIO' not in norm(x['descr'])]
    PL = [x for x in n2 if x['grp'] == 'P' and 'PATRIMONIO' in norm(x['descr'])]
    PNC = [x for x in n2 if x['grp'] == 'P' and x not in PC and x not in PL]
    at = [x for x in bp if x['nivel'] == 1 and x['grp'] == 'A']
    cod_ac = {x['cod'] for x in AC}; cod_anc = {x['cod'] for x in ANC}
    est = [x for x in bp if x['sup'] in cod_ac and 'ESTOQUE' in norm(x['descr'])]
    # RLP: filhos do ANC que não sejam investimento, imobilizado, intangível ou diferido
    fixo = ('INVESTIMENT', 'IMOBILIZAD', 'INTANGIVE', 'DIFERID')
    rlp = [x for x in bp if x['sup'] in cod_anc and not any(k in norm(x['descr']) for k in fixo)]
    comp = {}
    for nome, lst in [('ac', AC), ('estoques', est), ('rlp', rlp), ('at', at), ('pc', PC), ('elp', PNC), ('pl', PL)]:
        comp[nome] = {'atual': soma(lst, 'atual'), 'anterior': soma(lst, 'anterior'),
                      'contas': [x['descr'] for x in lst]}

    # ---- DRE: soma do saldo final de cada bloco (trimestres/semestres) por código.
    # Linhas que só aparecem num bloco posterior entram logo depois da linha que as precede naquele bloco.
    dre_val, dre_info, seq = {}, {}, []
    for b in blocos:
        ant = None
        for x in sorted(b['j150'], key=lambda y: int(y['ordem'] or 0)):
            v = x['vf'] if x['dcf'] == 'C' else -x['vf']
            dre_val[x['cod']] = dre_val.get(x['cod'], 0.0) + v
            if x['cod'] not in dre_info:
                dre_info[x['cod']] = x
                seq.insert(seq.index(ant) + 1 if ant in seq else len(seq), x['cod'])
            ant = x['cod']
    dre = [dict(cod=c, tipo=dre_info[c]['tipo'], nivel=dre_info[c]['nivel'], descr=dre_info[c]['descr'].strip(),
                valor=round(dre_val[c], 2)) for c in seq if abs(dre_val[c]) >= 0.005]
    lucro = None
    for d in dre:
        if d['nivel'] == 1:
            lucro = d['valor']

    saida = dict(empresa=emp, data_atual=dt(ult['fim']), data_anterior=dt(prim['ini']),
                 exercicio=emp['fim'][4:], blocos=len(blocos), balanco=bp, componentes=comp,
                 dre=dre, lucro_liquido=lucro)
    # data_anterior: o saldo inicial do 1º bloco é o encerramento do exercício anterior
    d = prim['ini']; saida['data_anterior'] = f'31/12/{int(d[4:]) - 1}' if d[:4] == '0101' else dt(d)
    with open(a.out, 'w', encoding='utf-8') as f:
        json.dump(saida, f, ensure_ascii=False, indent=1)
    print(json.dumps({k: saida[k] for k in ('empresa', 'data_atual', 'data_anterior', 'blocos', 'lucro_liquido')},
                     ensure_ascii=False))
    print(json.dumps(comp, ensure_ascii=False, indent=1))

if __name__ == '__main__':
    main()
