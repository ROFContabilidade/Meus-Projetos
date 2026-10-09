"""TXT de lançamentos para importar no Domínio (mesmo leiaute dos extratos da COSMETICI).

|0000|CNPJ|
|6000|X||||
|6100|DD/MM/AAAA|CONTA_DEBITO|CONTA_CREDITO|VALOR||HISTORICO||||

Só entram os impostos com conta de débito e de crédito preenchidas em contas_dominio (config).
"""


def _valor(v):
    return f'{v:.2f}'.replace('.', ',')


def lancamentos(a):
    """Lista de (imposto, data, débito, crédito, valor, histórico) e lista de impostos sem conta no config."""
    contas = a.cfg['contas_dominio']
    mes_txt = f'{a.mes[5:]}/{a.mes[:4]}'
    valores = [('pis', a.pc['pis']), ('cofins', a.pc['cofins']), ('ipi', a.ip['recolher']),
               ('icms', a.ic['recolher']), ('icms_st', a.st['recolher_pr'])]
    if a.ir['fechamento']:
        valores += [('irpj', a.ir['irpj']), ('csll', a.ir['csll'])]
    out, sem_conta = [], []
    for imp, v in valores:
        if not v:
            continue
        c = contas.get(imp, {})
        if not c.get('debito') or not c.get('credito'):
            sem_conta.append((imp, v))
            continue
        hist = c['historico'].format(mes=mes_txt, trimestre=a.ir['trimestre'])
        out.append((imp, a.fim, c['debito'], c['credito'], v, hist))
    return out, sem_conta


def gerar(a, destino):
    lanc, sem_conta = lancamentos(a)
    if not lanc:
        return lanc, sem_conta
    linhas = [f'|0000|{a.cnpj}|']
    for _, data, d, c, v, h in lanc:
        linhas.append('|6000|X||||')
        linhas.append(f'|6100|{data:%d/%m/%Y}|{d}|{c}|{_valor(v)}||{h}||||')
    with open(destino, 'w', encoding='cp1252', newline='\r\n') as fh:
        fh.write('\n'.join(linhas) + '\n')
    return lanc, sem_conta
