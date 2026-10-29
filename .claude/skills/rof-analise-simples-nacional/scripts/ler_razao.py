"""Lê o Razão do Domínio (contas de banco + 504 Clientes) e soma os recebimentos de clientes por mês e banco.

Uso: python ler_razao.py Razao.xlsx -o recebimentos.json [--clientes 504]
Recebimento = débito em conta de banco com contrapartida na conta de clientes. Separa transferências da própria
empresa/sócios (histórico com o nome/CNPJ da empresa ou --excluir), Reserva Stone e fundos."""
import argparse, collections, datetime, json, openpyxl, xlrd
from comum import abrir_xls

def ler_linhas(caminho):
    if caminho.lower().endswith('.xlsx'):
        for r in openpyxl.load_workbook(caminho, read_only=True, data_only=True).active.iter_rows(values_only=True):
            yield list(r)
    else:
        s = abrir_xls(caminho).sheet_by_index(0)
        for r in range(s.nrows):
            v = [c.value for c in s.row(r)]
            if isinstance(v[0], float) and v[0] > 30000: v[0] = xlrd.xldate_as_datetime(v[0], 0)
            yield v

def categoria(h, proprios):
    H = h.upper()
    if any(p in H for p in proprios): return 'transf_propria_socio'
    if 'RESERVA STONE' in H or 'DINHEIRO GUARDADO' in H or 'DINHEIRO RESGATADO' in H: return 'aplicacao'
    if 'FIDC' in H or 'FUNDO' in H or 'EMPREST' in H: return 'fundos_emprestimos'
    return 'clientes'

if __name__ == '__main__':
    ap = argparse.ArgumentParser(); ap.add_argument('razao'); ap.add_argument('-o', default='recebimentos.json')
    ap.add_argument('--clientes', type=int, default=504)
    ap.add_argument('--excluir', nargs='*', default=[], help='nomes/CNPJ da empresa e dos sócios (maiúsculas)')
    a = ap.parse_args()
    cols = None; conta = nome = None; bancos = {}
    res = collections.defaultdict(lambda: collections.defaultdict(float)); qtd = collections.Counter()
    for v in ler_linhas(a.razao):
        v = v + [None] * 16
        if 'Cta.C.Part.' in v and 'Débito' in v:
            cols = {k: v.index(k) for k in ['Data', 'Histórico', 'Cta.C.Part.', 'Débito', 'Crédito']}; continue
        if v[0] == 'Conta:':
            conta = int(v[1]); nome = next((x for x in v[3:] if isinstance(x, str) and x.strip()), str(conta)); continue
        if not cols or not isinstance(v[cols['Data']], datetime.datetime): continue
        if conta == a.clientes or 'BANCO' not in nome.upper() and 'STONE' not in nome.upper() and 'PAGAMENTOS' not in nome.upper() and 'PAGSEGURO' not in nome.upper(): continue
        if v[cols['Cta.C.Part.']] != a.clientes or not v[cols['Débito']]: continue
        bancos[conta] = nome
        m = v[cols['Data']].strftime('%m/%Y'); cat = categoria(str(v[cols['Histórico']]), [x.upper() for x in a.excluir])
        res[m][f'{conta}|{cat}'] += v[cols['Débito']]
        if cat == 'clientes': qtd[m] += 1
    out = {'bancos': bancos, 'meses': {m: dict(d) for m, d in res.items()}, 'quantidade': dict(qtd)}
    json.dump(out, open(a.o, 'w'), ensure_ascii=False, indent=1)
    for m in sorted(res, key=lambda x: x[3:] + x[:2]):
        cli = sum(x for k, x in res[m].items() if k.endswith('|clientes'))
        print(m, 'clientes', round(cli, 2), 'lançamentos', qtd[m])
