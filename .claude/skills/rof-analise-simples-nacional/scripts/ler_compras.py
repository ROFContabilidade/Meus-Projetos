"""Soma o Acompanhamento de Entradas do Domínio por mês e acumulador. Gera compras.json.

Uso: python ler_compras.py Entradas*.xls [NF_Entrada.xlsx] -o compras.json
Mercadorias = acumuladores 101 a 105; fretes (CT-e) = 300/301. Retorno de remessa (124/224), devoluções (128/228)
e serviços (80x) ficam separados."""
import argparse, collections, json, datetime, openpyxl, xlrd
from comum import abrir_xls, linhas

def somar(caminho, res):
    if caminho.lower().endswith('.xlsx'):
        wb = openpyxl.load_workbook(caminho, read_only=True, data_only=True)
        ws = wb['Entradas'] if 'Entradas' in wb.sheetnames else wb.active
        rows = (list(r) for r in ws.iter_rows(values_only=True)); xls = False
    else:
        rows = linhas(abrir_xls(caminho).sheet_by_index(0)); xls = True
    h = None
    for v in rows:
        if 'AC.' in v and 'Valor Contábil' in v:
            dcol = v.index('Data Entrada') if 'Data Entrada' in v else v.index('Data')
            h = (dcol, v.index('AC.'), v.index('Valor Contábil')); continue
        if not h or len(v) <= max(h): continue
        d, ac, val = v[h[0]], v[h[1]], v[h[2]]
        if not isinstance(ac, (int, float)) or not isinstance(val, (int, float)) or not isinstance(v[0], (int, float)): continue
        if xls and isinstance(d, float): d = xlrd.xldate_as_datetime(d, 0)
        if not isinstance(d, datetime.datetime): continue
        res[d.strftime('%m/%Y')][int(ac)] += val

if __name__ == '__main__':
    ap = argparse.ArgumentParser(); ap.add_argument('arquivos', nargs='+'); ap.add_argument('-o', default='compras.json')
    a = ap.parse_args(); res = collections.defaultdict(collections.Counter)
    for f in a.arquivos: somar(f, res)
    out = {}
    for m in sorted(res, key=lambda x: x[3:] + x[:2]):
        c = res[m]
        out[m] = {'mercadorias': sum(v for k, v in c.items() if 101 <= k <= 105), 'fretes': c[300] + c[301], 'por_acumulador': dict(c)}
        print(m, 'mercadorias', round(out[m]['mercadorias'], 2), 'fretes', round(out[m]['fretes'], 2))
    json.dump(out, open(a.o, 'w'), ensure_ascii=False, indent=1)
