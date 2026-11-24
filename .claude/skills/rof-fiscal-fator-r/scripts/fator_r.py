#!/usr/bin/env python3
"""Fator R do Simples Nacional - cálculo mês a mês, comparação Anexo III x V e pró-labore mínimo.

Uso:
  python3 fator_r.py --receitas receitas.csv --folhas folhas.csv --mes 2026-12
  python3 fator_r.py --simular --receita-mensal 8000 [--folha-mensal 0]

CSV: uma linha por mês, "AAAA-MM;valor" (aceita vírgula decimal). Cabeçalho opcional.
Base: LC 123/2006, art. 18, §§ 1º, 1º-A, 2º, 5º-J, 5º-K, 5º-M e 24 a 26 (redação LC 155/2016).
"""
import argparse
import csv
import sys

# (limite RBT12, alíquota nominal, parcela a deduzir)
ANEXO_III = [(180000, .06, 0), (360000, .112, 9360), (720000, .135, 17640),
             (1800000, .16, 35640), (3600000, .21, 125640), (4800000, .33, 648000)]
ANEXO_V = [(180000, .155, 0), (360000, .18, 4500), (720000, .195, 9900),
           (1800000, .205, 17100), (3600000, .23, 62100), (4800000, .305, 540000)]
LIMITE = 0.28


def num(s):
    s = str(s).strip().replace('R$', '').replace(' ', '')
    if ',' in s:
        s = s.replace('.', '').replace(',', '.')
    return float(s)


def ler(caminho):
    dados = {}
    with open(caminho, encoding='utf-8-sig') as f:
        for linha in csv.reader(f, delimiter=';'):
            if len(linha) < 2 or not linha[0].strip()[:4].isdigit():
                continue
            dados[linha[0].strip()[:7]] = num(linha[1])
    return dados


def mes_anterior(m, n=1):
    a, mm = int(m[:4]), int(m[5:7])
    for _ in range(n):
        mm -= 1
        if mm == 0:
            a, mm = a - 1, 12
    return f'{a:04d}-{mm:02d}'


def aliquota(tabela, rbt12):
    if rbt12 <= 0:
        return tabela[0][1]
    for lim, nom, pd in tabela:
        if rbt12 <= lim:
            return (rbt12 * nom - pd) / rbt12
    return None  # acima de 4,8 mi: fora do Simples


def brl(v):
    return 'R$ ' + f'{v:,.2f}'.replace(',', 'X').replace('.', ',').replace('X', '.')


def analisar(rbt12, folha12, receita_mes, meses_base=12):
    fr = folha12 / rbt12 if rbt12 else 0
    a3, a5 = aliquota(ANEXO_III, rbt12), aliquota(ANEXO_V, rbt12)
    if a3 is None:
        print('RBT12 acima de R$ 4.800.000,00 - fora do Simples Nacional.')
        return
    anexo = 'III' if fr >= LIMITE else 'V'
    falta12 = max(0.0, LIMITE * rbt12 - folha12)
    print(f'RBT12 (base {meses_base} meses): {brl(rbt12)}')
    print(f'Folha 12 meses:             {brl(folha12)}')
    print(f'Fator R:                    {fr:.2%}  -> Anexo {anexo}')
    print(f'Alíquota efetiva Anexo III: {a3:.4%}  DAS do mês: {brl(receita_mes * a3)}')
    print(f'Alíquota efetiva Anexo V:   {a5:.4%}  DAS do mês: {brl(receita_mes * a5)}')
    print(f'Diferença mensal (V - III): {brl(receita_mes * (a5 - a3))}')
    print(f'Pró-labore mínimo p/ 28% (sem outra folha): {brl(LIMITE * rbt12 / 12)} por mês')
    if falta12 > 0.005:
        print(f'ALERTA: faltam {brl(falta12)} de folha nos 12 meses para chegar a 28%.')
    elif fr < 0.30:
        print('ALERTA: Fator R entre 28% e 30% - risco de cair no Anexo V em mês de receita alta.')
    print('Lembrete: somar ao custo o INSS de 11% do sócio e o IRRF do pró-labore; '
          'distribuição de lucros e aluguéis não entram na folha (§26).')


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--receitas')
    p.add_argument('--folhas')
    p.add_argument('--mes', help='período de apuração AAAA-MM')
    p.add_argument('--simular', action='store_true')
    p.add_argument('--receita-mensal', type=float)
    p.add_argument('--folha-mensal', type=float, default=0.0)
    a = p.parse_args()

    if a.simular:
        if not a.receita_mensal:
            sys.exit('Informe --receita-mensal')
        analisar(a.receita_mensal * 12, a.folha_mensal * 12, a.receita_mensal)
        return

    if not (a.receitas and a.folhas and a.mes):
        sys.exit('Informe --receitas, --folhas e --mes (ou use --simular)')
    rec, fol = ler(a.receitas), ler(a.folhas)
    meses = [mes_anterior(a.mes, i) for i in range(1, 13)]
    com_dados = [m for m in meses if m in rec]
    if not com_dados:
        # 1º mês de atividade (art. 18, §2º): receita do próprio mês x 12
        r_mes, f_mes = rec.get(a.mes, 0), fol.get(a.mes, 0)
        print('Início de atividade: usando o próprio mês x 12 (conferir regra CGSN vigente).')
        analisar(r_mes * 12, f_mes * 12, r_mes, 1)
        return
    n = len(com_dados)
    rbt = sum(rec[m] for m in com_dados)
    fol12 = sum(fol.get(m, 0) for m in com_dados)
    if n < 12:
        print(f'Início de atividade: {n} meses anteriores - proporcionalizando para 12 (art. 18, §2º).')
        rbt, fol12 = rbt / n * 12, fol12 / n * 12
    print(f'Período de apuração {a.mes}: base {com_dados[-1]} a {com_dados[0]}')
    analisar(rbt, fol12, rec.get(a.mes, 0), n)


if __name__ == '__main__':
    main()
