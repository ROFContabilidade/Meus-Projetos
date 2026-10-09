"""Leitura dos relatórios 'Acompanhamento de Entradas/Saídas' exportados do
Domínio Escrita Fiscal em Excel: uma linha por nota com acumulador, CFOP e as
linhas de imposto (ICMS, IPI, ISS, ICMSA...)."""
import datetime as dt
from decimal import Decimal

import pandas as pd


def _num(v):
    if v is None or (isinstance(v, float) and pd.isna(v)):
        return Decimal('0')
    if isinstance(v, str):
        v = v.strip().replace('.', '').replace(',', '.')
        try:
            return Decimal(v).quantize(Decimal('0.01'))
        except Exception:
            return Decimal('0')
    return Decimal(str(v)).quantize(Decimal('0.01'))


def parse_acompanhamento(path, sheet):
    df = pd.read_excel(path, sheet_name=sheet, header=None)
    hdr_row = next(i for i, r in df.iterrows()
                   if 'Código' in r.values and 'Nota' in r.values and 'CFOP' in r.values)
    cols = {}
    for j, v in df.iloc[hdr_row].items():
        if isinstance(v, str):
            cols.setdefault(v.strip(), j)
    c = lambda name: cols[name]
    notas, cur = [], None
    for i in range(hdr_row + 1, len(df)):
        r = df.iloc[i]
        cod, data = r[c('Código')], r[c('Data')]
        if isinstance(data, (dt.datetime, pd.Timestamp)) and not pd.isna(cod):
            cur = {'codigo': int(cod), 'data': data.date().isoformat(), 'nota': str(int(r[c('Nota')])),
                   'serie': str(r[c('Série')]).replace('.0', ''), 'especie': str(r[c('Espécie')]).replace('.0', ''),
                   'participante': str(r[c('Fornecedor') if 'Fornecedor' in cols else c('Cliente')]),
                   'cfop': str(int(r[c('CFOP')])), 'acumulador': str(int(r[c('AC.')])),
                   'uf': r[c('UF')], 'valor_contabil': _num(r[c('Valor Contábil')]), 'impostos': {}}
            notas.append(cur)
        elif isinstance(r[c('Código')], str) and r[c('Código')].startswith(('Sub-total', 'Total')):
            cur = None
            continue
        tipo = r[c('Tipo')]
        if cur is not None and isinstance(tipo, str) and tipo.strip():
            linha = {'base': _num(r[c('Base Cálculo')]), 'aliq': _num(r[c('Alíq.')]),
                     'valor': _num(r[c('Valor')]), 'isentas': _num(r[c('Isentas')]),
                     'outras': _num(r[c('Outras')])}
            cur['impostos'].setdefault(tipo.strip(), []).append(linha)
    return notas
