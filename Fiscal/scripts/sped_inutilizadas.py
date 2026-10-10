"""Gera um TXT no leiaute do SPED Fiscal (EFD ICMS/IPI) só com NF-e próprias
inutilizadas (C100 com COD_SIT 05), para importar no Domínio.

O cabeçalho (0000, 0005, 0100) é copiado do SPED de um mês anterior da empresa;
o período passa a ser o da competência informada.

Uso:
  python3 sped_inutilizadas.py --sped-base SPED_mes_anterior.txt --lista Inutilizadas.xlsx
      --competencia 2026-09 --saida EFD_inutilizadas_092026.txt [--sem-data]
"""
import argparse
import calendar
from collections import Counter

import pandas as pd

CAMPOS_C100 = 29          # REG ... VL_COFINS_ST


def c100_inutilizada(serie, numero, data):
    f = [''] * CAMPOS_C100
    f[0], f[1], f[2], f[4], f[5] = 'C100', '1', '0', '55', '05'
    f[6], f[7] = f'{int(serie):03d}', str(int(numero))
    f[9] = data or ''        # DT_DOC: o Guia Prático deixa vazio; o escritório quer a data de emissão
    return '|' + '|'.join(f) + '|'


def gerar(sped_base, lista, competencia, saida, com_data=True):
    base = open(sped_base, encoding='latin-1').read().splitlines()
    pega = {ln.split('|')[1]: ln for ln in base if ln.startswith('|') and ln.split('|')[1] in ('0000', '0005', '0100')}
    ano, mes = int(competencia[:4]), int(competencia[5:7])
    ini, fim = f'01{mes:02d}{ano}', f'{calendar.monthrange(ano, mes)[1]:02d}{mes:02d}{ano}'
    r0 = pega['0000'].split('|')
    r0[4], r0[5] = ini, fim
    df = pd.read_excel(lista, sheet_name=0, header=2).sort_values(['Série', 'Número'])
    linhas = [ '|'.join(r0), '|0001|0|', pega['0005'], pega['0100'] ]
    linhas.append(f'|0990|{len(linhas) + 1}|')
    bloco_c = ['|C001|0|'] + [
        c100_inutilizada(r['Série'], r['Número'],
                         pd.to_datetime(r['Data de emissão'], dayfirst=True).strftime('%d%m%Y') if com_data else '')
        for _, r in df.iterrows()]
    bloco_c.append(f'|C990|{len(bloco_c) + 1}|')
    linhas += bloco_c
    for b in ('D', 'E', 'G', 'H', 'K', '1'):
        linhas += [f'|{b}001|1|', f'|{b}990|2|']
    cont = Counter(ln.split('|')[1] for ln in linhas)
    bloco9 = ['|9001|0|'] + [f'|9900|{reg}|{n}|' for reg, n in cont.items()]
    bloco9 += ['|9900|9001|1|', '|9900|9900|PLACEHOLDER|', '|9900|9990|1|', '|9900|9999|1|']
    n9900 = sum(1 for x in bloco9 if x.startswith('|9900|'))
    bloco9 = [x.replace('PLACEHOLDER', str(n9900)) for x in bloco9]
    bloco9.append(f'|9990|{len(bloco9) + 2}|')
    linhas += bloco9
    linhas.append(f'|9999|{len(linhas) + 1}|')
    with open(saida, 'w', encoding='latin-1', newline='\r\n') as f:
        f.write('\n'.join(linhas) + '\n')
    return len(df), linhas


if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('--sped-base', required=True)
    p.add_argument('--lista', required=True)
    p.add_argument('--competencia', required=True)
    p.add_argument('--saida', required=True)
    p.add_argument('--sem-data', action='store_true', help='deixa DT_DOC vazio, como no Guia Prático')
    a = p.parse_args()
    n, _ = gerar(a.sped_base, a.lista, a.competencia, a.saida, not a.sem_data)
    print(f'{n} notas inutilizadas -> {a.saida}')
