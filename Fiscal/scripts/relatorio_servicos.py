"""Relatório das NFS-e de serviços tomados do mês, para análise das retenções.

Abas: Resumo · Todas as notas · Com retenção (com o que recolher: DARF, EFD-Reinf, guia municipal)
· Sem retenção (com alerta quando a retenção era esperada). Uma linha por NFS-e.
Fonte: linhas de NFS-e da conferência (classificação LC 116, acumulador, conta, retenções) + planilha
"Recebidas - Completa" da NFS-e nacional (ISS, descrição, chave).
"""
from decimal import Decimal

import pandas as pd
from openpyxl import Workbook
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter

Z = Decimal('0')
AZUL = PatternFill('solid', fgColor='1F3864')
VERM = PatternFill('solid', fgColor='FFC7CE')
VERDE = PatternFill('solid', fgColor='E2EFDA')
AMAR = PatternFill('solid', fgColor='FFF2CC')
CINZA = PatternFill('solid', fgColor='D9D9D9')
FINO = Border(bottom=Side(style='thin', color='BFBFBF'))
NUM = '#,##0.00'
# CSRF 4,65% = PIS 0,65 + COFINS 3,00 + CSLL 1,00
CSRF = (('PIS retido', Decimal('0.65')), ('COFINS retido', Decimal('3.00')), ('CSLL retido', Decimal('1.00')))


def D(x):
    try:
        return Decimal(str(x)) if str(x) not in ('', 'nan', 'None', '-') else Z
    except Exception:
        return Z


def _fonte(path):
    if not path:
        return {}
    s = pd.read_excel(path, dtype=str)
    out = {}
    for _, r in s.iterrows():
        num = str(r.get('Número NFS-e', '')).replace('.0', '')
        doc = ''.join(ch for ch in str(r.get('CNPJ/CPF Prestador', '')).replace('.0', '') if ch.isdigit())
        out[(num, doc.lstrip('0'))] = r
    return out


def _linha(x, src, cfg):
    num = str(x['Número']).replace('.0', '')
    num = int(num) if num.isdigit() else num
    doc = ''.join(ch for ch in str(x['CNPJ']) if ch.isdigit())
    r = src.get((str(num), doc.lstrip('0')))
    g = (lambda k: r.get(k, '') if r is not None else '')
    irrf, csrf, inss, iss = (D(x.get(k)) for k in ('IRRF retido', 'CSRF retido', 'INSS retido', 'ISS retido'))
    partes = {}
    resto = csrf
    for i, (nome, p) in enumerate(CSRF):
        v = resto if i == len(CSRF) - 1 else (csrf * p / Decimal('4.65')).quantize(Decimal('0.01'))
        partes[nome] = v
        resto -= v
    total = irrf + csrf + inss + iss
    valor = D(x['Valor'])
    item = str(x.get('Serviço (LC 116)') or '')
    tipos = [t for t, v in (('IRRF', irrf), ('PIS/COFINS/CSLL', csrf), ('INSS', inss), ('ISS', iss)) if v]
    darf_ir = cfg.get('darf_irrf_por_item', {}).get(item, '1708')
    rec = []
    if irrf:
        rec.append(f'IRRF DARF {darf_ir}')
    if csrf:
        rec.append('PIS/COFINS/CSLL DARF 5952')
    if inss:
        rec.append('INSS retido (DCTFWeb, R-2010)')
    if iss:
        rec.append('ISS retido: guia do município')
    eventos = (['R-4020'] if (irrf or csrf) else []) + (['R-2010'] if inss else [])
    sit = str(x['Status'])
    return {
        'Situação': sit, 'Retenção': 'SIM - ' + ', '.join(tipos) if tipos else 'NÃO',
        'Emissão': x.get('Data emissão', ''), 'Competência': x.get('Competência', ''), 'Número': num,
        'Prestador': x['Prestador'], 'CNPJ/CPF': doc, 'Simples Nacional': x.get('Simples Nacional', '') or g('Simples Nacional'),
        'Município (ISS)': x.get('Município ISS', '') or g('Município de Incidência'),
        'Item LC 116': item, 'Descrição do serviço': str(g('Descrição do Serviço') or '')[:120],
        'Natureza': x.get('Natureza do serviço', ''), 'Acumulador': x.get('Acum. sugerido', ''),
        'Nome do acumulador': x.get('Acumulador sugerido (nome)', ''), 'Conta contábil': x.get('Conta contábil sugerida', ''),
        'Valor do serviço': valor, 'Alíquota ISS %': D(g('Alíquota ISSQN (%)')), 'Valor ISS': D(g('Valor do ISSQN (R$)')),
        'ISS retido': iss, 'IRRF retido': irrf, **partes, 'INSS retido': inss, 'Total retido': total,
        'Valor líquido a pagar': valor - total, 'Recolher': ' · '.join(rec),
        'EFD-Reinf': ', '.join(eventos) + (' (período = mês do pagamento)' if eventos else ''),
        'Alertas': x.get('Alertas', '') or '', 'Chave NFS-e': str(g('Chave NFS-e') or ''),
    }


def _aba(wb, titulo, sub, linhas, cols, soma, larg, cor):
    ws = wb.create_sheet(titulo)
    ws['A1'] = titulo
    ws['A1'].font = Font(bold=True, size=13, color='1F3864')
    ws['A2'] = sub
    ws['A2'].font = Font(italic=True, color='595959')
    for j, c in enumerate(cols, 1):
        x = ws.cell(4, j, c)
        x.font = Font(bold=True, color='FFFFFF')
        x.fill = AZUL
        x.alignment = Alignment(wrap_text=True, horizontal='center', vertical='center')
    for i, l in enumerate(linhas, 5):
        f = cor(l)
        for j, c in enumerate(cols, 1):
            v = l.get(c)
            x = ws.cell(i, j, float(v) if isinstance(v, Decimal) else v)
            x.border = FINO
            if isinstance(v, Decimal):
                x.number_format = NUM
            if f and j <= 2:
                x.fill = f
            if c in ('IRRF retido', 'PIS retido', 'COFINS retido', 'CSLL retido', 'INSS retido', 'ISS retido',
                     'Total retido') and v:
                x.font = Font(bold=True, color='9C0006')
    t = 5 + len(linhas)
    ws.cell(t, 1, f'TOTAL ({len(linhas)} notas)').font = Font(bold=True)
    for c in soma:
        j = cols.index(c) + 1
        L = get_column_letter(j)
        x = ws.cell(t, j, f'=SUBTOTAL(9,{L}5:{L}{t - 1})' if linhas else 0)
        x.font = Font(bold=True)
        x.number_format = NUM
    for j in range(1, len(cols) + 1):
        ws.cell(t, j).fill = PatternFill('solid', fgColor='D9E1F2')
    ws.row_dimensions[4].height = 32
    ws.freeze_panes = 'C5'
    ws.auto_filter.ref = f'A4:{get_column_letter(len(cols))}{max(4, t - 1)}'
    for j, c in enumerate(cols, 1):
        ws.column_dimensions[get_column_letter(j)].width = larg.get(c, 12)
    return ws


def gerar(res, saida, nfse_planilha=None):
    cfg = res['regras'].r.get('servicos', {})
    src = _fonte(nfse_planilha)
    todas = [_linha(x, src, cfg) for x in res['nfse']]
    ordem = lambda l: (not l['Situação'].startswith(('A LANÇAR', 'CONFERIR')), l['Retenção'] == 'NÃO',
                       l['Emissão'][6:] + l['Emissão'][3:5] + l['Emissão'][:2], l['Prestador'])
    todas.sort(key=ordem)
    com = [l for l in todas if l['Retenção'] != 'NÃO']
    sem = [l for l in todas if l['Retenção'] == 'NÃO']
    for l in todas:
        l['Serviço'] = f"{l['Item LC 116']} {l['Natureza']}".strip()[:45]
        l['Guia'] = l['Recolher'].replace(' DARF ', ' ').replace('PIS/COFINS/CSLL', 'CSRF')
        l['Observação'] = l['Alertas'] if l['Situação'].startswith(('A LANÇAR', 'CONFERIR')) else l['Situação']
    larg = {'Situação': 14, 'Retenção': 20, 'Prestador': 36, 'CNPJ/CPF': 16, 'Serviço': 34, 'Guia': 26,
            'Observação': 44, 'Número': 9, 'Emissão': 11, 'Acumulador': 11}
    # só as retenções que existem no mês (sem colunas zeradas)
    ret = [c for c in ('IRRF retido', 'PIS retido', 'COFINS retido', 'CSLL retido', 'INSS retido', 'ISS retido')
           if any(l[c] for l in todas)]
    cor = lambda l: (CINZA if not l['Situação'].startswith(('A LANÇAR', 'CONFERIR'))
                     else VERM if l['Retenção'] != 'NÃO' else VERDE)
    for l in todas:
        l['Situação'] = 'Lançar' if l['Situação'].startswith(('A LANÇAR', 'CONFERIR')) else 'Não lançar'
    comp = res['competencia']
    emp = res['regras'].r['empresa']['nome']
    wb = Workbook()
    r = wb.active
    r.title = 'Resumo'
    r['A1'] = f'Serviços tomados {comp[5:]}/{comp[:4]} — {emp}'
    r['A1'].font = Font(bold=True, size=14, color='1F3864')
    r['A2'] = 'Vermelho = com retenção · verde = sem retenção · cinza = não lançar.'
    r['A2'].font = Font(italic=True, color='595959')
    lanc = [l for l in todas if l['Situação'] == 'Lançar']
    nomes = {'IRRF retido': 'IRRF', 'PIS retido': 'PIS', 'COFINS retido': 'COFINS', 'CSLL retido': 'CSLL',
             'INSS retido': 'INSS', 'ISS retido': 'ISS'}
    cab = ['', 'Notas', 'Valor'] + [nomes[c] for c in ret] + ['Total retido']
    for j, c in enumerate(cab, 1):
        x = r.cell(4, j, c)
        x.font = Font(bold=True, color='FFFFFF')
        x.fill = AZUL
    soma = lambda ls, k: float(sum((l[k] for l in ls), Z))
    grupos = [('Com retenção', [l for l in lanc if l['Retenção'] != 'NÃO'], VERM),
              ('Sem retenção', [l for l in lanc if l['Retenção'] == 'NÃO'], VERDE),
              ('Total a lançar', lanc, None),
              ('Não lançar', [l for l in todas if l['Situação'] != 'Lançar'], CINZA)]
    for i, (nome, ls, f) in enumerate(grupos, 5):
        vals = [nome, len(ls), soma(ls, 'Valor do serviço')] + [soma(ls, c) for c in ret] + [soma(ls, 'Total retido')]
        for j, v in enumerate(vals, 1):
            x = r.cell(i, j, v)
            if isinstance(v, float):
                x.number_format = NUM
            if f and j == 1:
                x.fill = f
            if nome.startswith('Total'):
                x.font = Font(bold=True)
    r.cell(10, 1, 'Guias a recolher (vencem dia 20 do mês seguinte ao pagamento)').font = Font(bold=True, color='1F3864')
    guias = {}
    for l in lanc:
        darf = cfg.get('darf_irrf_por_item', {}).get(l['Item LC 116'], '1708')
        for k, nome in ((('IRRF retido',), f'IRRF - DARF {darf}'),
                        (('PIS retido', 'COFINS retido', 'CSLL retido'), 'PIS/COFINS/CSLL - DARF 5952'),
                        (('INSS retido',), 'INSS retido - DCTFWeb'), (('ISS retido',), 'ISS retido - guia do município')):
            v = sum((l[c] for c in k), Z)
            if v:
                guias[nome] = guias.get(nome, Z) + v
    for i, (nome, v) in enumerate(sorted(guias.items()), 11):
        r.cell(i, 1, nome)
        x = r.cell(i, 3, float(v))
        x.number_format = NUM
    if not guias:
        r.cell(11, 1, 'Nenhuma retenção no mês.')
    else:
        r.cell(11 + len(guias), 1, 'Informar na EFD-Reinf (R-4020) no mês do pagamento.').font = Font(italic=True, color='595959')
    r.column_dimensions['A'].width = 40
    for L in 'BCDEFGHI':
        r.column_dimensions[L].width = 12
    r.column_dimensions['C'].width = 14

    _aba(wb, 'Todas as notas', 'Todas as NFS-e do mês.', todas,
         ['Situação', 'Retenção', 'Emissão', 'Número', 'Prestador', 'CNPJ/CPF', 'Serviço', 'Acumulador',
          'Valor do serviço', 'Total retido', 'Valor líquido a pagar', 'Observação'],
         ['Valor do serviço', 'Total retido', 'Valor líquido a pagar'], larg, cor)
    _aba(wb, 'Com retenção', 'Notas com imposto retido: valores e guia de cada uma.',
         [l for l in com if l['Situação'] == 'Lançar'],
         ['Emissão', 'Número', 'Prestador', 'CNPJ/CPF', 'Serviço', 'Valor do serviço'] + ret +
         ['Total retido', 'Valor líquido a pagar', 'Guia'],
         ['Valor do serviço'] + ret + ['Total retido', 'Valor líquido a pagar'], larg, lambda l: VERM)
    _aba(wb, 'Sem retenção', 'Notas sem imposto retido. Observação só aparece se a retenção era esperada.', sem,
         ['Situação', 'Emissão', 'Número', 'Prestador', 'CNPJ/CPF', 'Serviço', 'Acumulador', 'Valor do serviço',
          'Observação'], ['Valor do serviço'], larg,
         lambda l: CINZA if l['Situação'] != 'Lançar' else (AMAR if l['Observação'] else VERDE))
    wb.save(saida)
    return len(todas), len(com), len(sem)
