"""Planilha simples de conferência das ENTRADAS do mês, uma linha por documento:
NF-e dentro do estado, NF-e fora do estado, devoluções/retornos emitidos pela empresa,
serviços tomados (NFS-e) e CT-e. Cada aba tem total e coluna "Conferido".
"""
from collections import Counter, defaultdict
from decimal import Decimal

from openpyxl import Workbook
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter

AZUL = PatternFill('solid', fgColor='1F3864')
CINZA = PatternFill('solid', fgColor='D9E1F2')
VERDE = PatternFill('solid', fgColor='E2EFDA')
AMARELO = PatternFill('solid', fgColor='FFF2CC')
VERMELHO = PatternFill('solid', fgColor='F8CBAD')
FINO = Side(style='thin', color='BFBFBF')
NUM = '#,##0.00'
Z = Decimal('0')

ORDEM_STATUS = {'A LANÇAR': 0, 'CONFERIR': 1}


def _data(v):
    v = str(v or '')
    return f'{v[8:10]}/{v[5:7]}/{v[:4]}' if len(v) >= 10 and v[4] == '-' else v


def _chave_data(v):
    v = _data(v)
    return v[6:10] + v[3:5] + v[:2]


def _cor(status):
    s = str(status or '').upper()
    if s.startswith('A LANÇAR') or s == 'OK':
        return VERDE
    if 'CANCEL' in s or 'NÃO LANÇAR' in s or 'JÁ LANÇADA' in s or 'DOCUMENTO DO FORNECEDOR' in s:
        return CINZA
    if 'CONFERIR' in s or 'PENDENTE' in s or 'DEFINIR' in s:
        return AMARELO
    return VERMELHO


def _aba(wb, titulo, descricao, linhas, colunas, somar, larguras):
    ws = wb.create_sheet(titulo)
    ws.cell(1, 1, titulo).font = Font(bold=True, size=13, color='1F3864')
    ws.cell(2, 1, descricao).font = Font(italic=True, color='595959')
    r0 = 4
    for j, c in enumerate(colunas, 1):
        cel = ws.cell(r0, j, c)
        cel.font = Font(bold=True, color='FFFFFF')
        cel.fill = AZUL
        cel.alignment = Alignment(wrap_text=True, vertical='center', horizontal='center')
    for i, ln in enumerate(linhas, r0 + 1):
        for j, c in enumerate(colunas, 1):
            v = ln.get(c)
            if c == 'Emissão':
                v = _data(v)
            if isinstance(v, Decimal):
                v = float(v)
            cel = ws.cell(i, j, v)
            cel.border = Border(bottom=FINO)
            if isinstance(v, float):
                cel.number_format = NUM
        ws.cell(i, 1).fill = _cor(ln.get('Situação'))
    tot = r0 + len(linhas) + 1
    ws.cell(tot, 1, f'TOTAL ({len(linhas)} documentos)').font = Font(bold=True)
    for c in somar:
        j = colunas.index(c) + 1
        col = get_column_letter(j)
        cel = ws.cell(tot, j, f'=SUBTOTAL(9,{col}{r0 + 1}:{col}{tot - 1})' if linhas else 0)
        cel.font = Font(bold=True)
        cel.number_format = NUM
    for j in range(1, len(colunas) + 1):
        ws.cell(tot, j).fill = CINZA
    ws.freeze_panes = ws.cell(r0 + 1, 3)
    ws.auto_filter.ref = f'A{r0}:{get_column_letter(len(colunas))}{max(r0, tot - 1)}'
    ws.row_dimensions[r0].height = 34
    for j, c in enumerate(colunas, 1):
        ws.column_dimensions[get_column_letter(j)].width = larguras.get(c, max(10, min(len(c) + 2, 16)))
    return ws


def _itens_por_nota(res):
    por = defaultdict(list)
    for it in res['itens']:
        por[(it['Nota'], it['CNPJ'])].append(it)
    return por


def _resumo_itens(its):
    nomes = [str(i['Descrição do item'])[:40] for i in its]
    txt = '; '.join(nomes[:3])
    return txt + (f' (+{len(nomes) - 3} itens)' if len(nomes) > 3 else '')


def gerar(res, saida):
    R = res['regras']
    uf = R.uf
    K = R.cnpj
    notas = res['notas']
    itens = _itens_por_nota(res)
    wb = Workbook()
    ws0 = wb.active
    ws0.title = 'Resumo'

    # ---------------- NF-e de fornecedores
    nfe_in, nfe_out = [], []
    for n in res['notas_terc']:
        x = notas.get(n['Chave'], {})
        its = itens.get((n['Nota'], x.get('emit_cnpj', '')), [])
        cancel = 'CANCELADA' in n['Status']
        st = ('CANCELADA - lançar zerada' if cancel else
              'A LANÇAR' if n['Status'] in ('OK',) else 'CONFERIR')
        fins = Counter(i['Finalidade'] for i in its)
        ln = {
            'Situação': st, 'Emissão': n['Emissão'], 'Nota': n['Nota'], 'Série': x.get('serie', ''),
            'Fornecedor': n['Fornecedor'], 'CNPJ': x.get('emit_cnpj', ''), 'UF': n['UF'],
            'CFOP do fornecedor': ', '.join(sorted({i['CFOP forn.'] for i in its})),
            'CFOP entrada': n['CFOP sugerido'], 'Acumulador': n['Acum. sugerido'],
            'Valor contábil': Z if cancel else x.get('t_vNF', n['Valor NF']),
            'Base ICMS': Z if cancel else sum((i['BC ICMS'] or Z for i in its), Z),
            'ICMS destacado': Z if cancel else n['ICMS destacado'],
            'IPI': Z if cancel else n['IPI destacado'],
            'Crédito ICMS': n['Crédito ICMS sugerido'], 'Crédito IPI': n['Crédito IPI sugerido'],
            'DIFAL': n['DIFAL estimado'],
            'Finalidade': ', '.join(k.replace('_', ' ').lower() for k in fins),
            'Conta contábil': n.get('Contas contábeis sugeridas', ''),
            'Itens': _resumo_itens(its), 'Observação': n['Observações'], 'Chave': n['Chave'], 'Conferido': '',
        }
        (nfe_in if n['UF'] == uf else nfe_out).append(ln)
    for p in res['pendencias']:          # documentos do fornecedor que não geram entrada
        if p['Tipo'] == 'Documento do fornecedor':
            x = notas.get(p['Chave'], {})
            ln = {'Situação': 'NÃO LANÇAR - documento do fornecedor', 'Emissão': x.get('dt_emissao', ''),
                  'Nota': x.get('numero', ''), 'Série': x.get('serie', ''), 'Fornecedor': p['Participante'],
                  'CNPJ': x.get('emit_cnpj', ''), 'UF': x.get('emit_uf', ''), 'Valor contábil': Z,
                  'Observação': p['O que fazer / por quê'], 'Chave': p['Chave'], 'Conferido': ''}
            (nfe_in if x.get('emit_uf') == uf else nfe_out).append(ln)

    col_nfe = ['Situação', 'Emissão', 'Nota', 'Série', 'Fornecedor', 'CNPJ', 'UF', 'CFOP do fornecedor', 'CFOP entrada',
               'Acumulador', 'Valor contábil', 'Base ICMS', 'ICMS destacado', 'IPI', 'Crédito ICMS', 'Crédito IPI',
               'DIFAL', 'Finalidade', 'Conta contábil', 'Itens', 'Observação', 'Chave', 'Conferido']
    som_nfe = ['Valor contábil', 'Base ICMS', 'ICMS destacado', 'IPI', 'Crédito ICMS', 'Crédito IPI', 'DIFAL']
    larg_nfe = {'Situação': 24, 'Fornecedor': 32, 'Finalidade': 18, 'Conta contábil': 34, 'Itens': 50,
                'Observação': 50, 'Chave': 46, 'CNPJ': 16, 'Emissão': 11, 'Nota': 9, 'Série': 6, 'UF': 5}
    ordem = lambda l: (ORDEM_STATUS.get(l['Situação'], 5), _chave_data(l['Emissão']), l['Fornecedor'])
    _aba(wb, f'NF-e dentro do estado ({uf})', f'Notas de fornecedores do {uf} (CFOP 1xxx). Verde = lançar; amarelo = '
         'conferir; cinza = cancelada/não lançar.', sorted(nfe_in, key=ordem), col_nfe, som_nfe, larg_nfe)
    _aba(wb, 'NF-e fora do estado', 'Notas de fornecedores de outros estados (CFOP 2xxx). DIFAL só em uso e consumo.',
         sorted(nfe_out, key=ordem), col_nfe, som_nfe, larg_nfe)

    # ---------------- devoluções / retornos emitidos pela empresa
    dev = []
    for d in res['devol']:
        x = notas.get(d['Chave'], {})
        cancel = d['Status'].startswith('CANCELADA')
        dev.append({'Situação': 'CANCELADA - não lançar' if cancel else ('A LANÇAR' if d['Status'] == 'OK' else 'CONFERIR'),
                    'Emissão': d['Data'], 'Nota': d['Nota'], 'Série': x.get('serie', ''),
                    'Cliente (quem devolveu)': d['Cliente (remetente)'], 'UF': d.get('UF', x.get('dest_uf', '')),
                    'Natureza': d['Natureza'], 'CFOP': d['CFOP XML'], 'Acumulador': d.get('Acum. esperado', ''),
                    'Valor contábil': Z if cancel else d['Valor NF'], 'Base ICMS': d.get('BC ICMS XML'),
                    'ICMS': d.get('ICMS XML'), 'IPI': d.get('IPI XML'),
                    'NF de venda referenciada': d.get('NF de venda referenciada', ''),
                    'Observação': d.get('Observações', ''), 'Chave': d['Chave'], 'Conferido': ''})
    _aba(wb, 'Devoluções e retornos', 'NF-e de ENTRADA emitidas pela própria empresa (devolução de cliente, retorno de '
         'consignação, feira, troca).', sorted(dev, key=lambda l: (l['Situação'] != 'A LANÇAR', int(l['Nota']))),
         ['Situação', 'Emissão', 'Nota', 'Série', 'Cliente (quem devolveu)', 'UF', 'Natureza', 'CFOP', 'Acumulador',
          'Valor contábil', 'Base ICMS', 'ICMS', 'IPI', 'NF de venda referenciada', 'Observação', 'Chave', 'Conferido'],
         ['Valor contábil', 'Base ICMS', 'ICMS', 'IPI'],
         {'Situação': 22, 'Cliente (quem devolveu)': 32, 'Natureza': 34, 'Observação': 40, 'Chave': 46})

    # ---------------- serviços tomados
    sv = []
    for x in res['nfse']:
        st = x['Status']
        sit = ('A LANÇAR' if st == 'A LANÇAR' else 'CONFERIR' if st == 'CONFERIR' else st)
        sv.append({'Situação': sit, 'Emissão': x.get('Data emissão', ''), 'Competência': x['Competência'],
                   'Número': x['Número'], 'Prestador': x['Prestador'], 'CNPJ': x['CNPJ'],
                   'Município': x.get('Município do prestador', x.get('Município ISS', '')),
                   'Serviço (LC 116)': x.get('Serviço (LC 116)', ''), 'Natureza do serviço': x.get('Natureza do serviço', ''),
                   'Acumulador': x.get('Acum. sugerido', ''), 'Valor': x['Valor'],
                   'IRRF': x.get('IRRF retido'), 'PIS/COFINS/CSLL': x.get('CSRF retido'), 'INSS': x.get('INSS retido'),
                   'ISS retido': x.get('ISS retido'), 'Simples Nacional': x.get('Simples Nacional', ''),
                   'Conta contábil': x.get('Conta contábil sugerida', ''), 'Observação': x.get('Alertas', ''),
                   'Conferido': ''})
    _aba(wb, 'Serviços tomados (NFS-e)', 'NFS-e recebidas. Acumulador pelo item da LC 116 + retenções. Retenções vão '
         'para a EFD-Reinf.', sorted(sv, key=lambda l: (ORDEM_STATUS.get(l['Situação'], 5), _chave_data(l['Emissão']))),
         ['Situação', 'Emissão', 'Competência', 'Número', 'Prestador', 'CNPJ', 'Município', 'Serviço (LC 116)',
          'Natureza do serviço', 'Acumulador', 'Valor', 'IRRF', 'PIS/COFINS/CSLL', 'INSS', 'ISS retido',
          'Simples Nacional', 'Conta contábil', 'Observação', 'Conferido'],
         ['Valor', 'IRRF', 'PIS/COFINS/CSLL', 'INSS', 'ISS retido'],
         {'Situação': 30, 'Prestador': 34, 'Município': 18, 'Natureza do serviço': 32, 'Simples Nacional': 22,
          'Conta contábil': 34, 'Observação': 50})

    # ---------------- CT-e
    ct = []
    for c in res.get('cte', []):
        st = c['Status']
        sit = 'A LANÇAR' if st == 'A LANÇAR' else ('CANCELADO - lançar zerado' if 'ZERADO' in st else st)
        ct.append({'Situação': sit, 'Emissão': c['Data'], 'CT-e': c['CT-e'], 'Transportador': c['Transportador'],
                   'CNPJ': c['CNPJ'], 'Trajeto': c['Trajeto'], 'Tomador (quem paga)': c['Tomador (quem paga)'],
                   'Remetente': c['Remetente'], 'Destinatário': c['Destinatário'],
                   'CFOP entrada': c['CFOP de entrada sugerido'], 'Acumulador': c['Acum. sugerido'],
                   'Valor': c['Valor'], 'Base ICMS': c['BC ICMS'], 'ICMS': c['ICMS'],
                   'Crédito ICMS': c['Crédito ICMS sugerido'], 'Observação': c['Observações'], 'Chave': c['Chave'],
                   'Conferido': ''})
    _aba(wb, 'CT-e (fretes)', 'Só lança quando a empresa é a TOMADORA (quem paga o frete).',
         sorted(ct, key=lambda l: (ORDEM_STATUS.get(l['Situação'], 5), _chave_data(l['Emissão']))),
         ['Situação', 'Emissão', 'CT-e', 'Transportador', 'CNPJ', 'Trajeto', 'Tomador (quem paga)', 'Remetente',
          'Destinatário', 'CFOP entrada', 'Acumulador', 'Valor', 'Base ICMS', 'ICMS', 'Crédito ICMS', 'Observação',
          'Chave', 'Conferido'],
         ['Valor', 'Base ICMS', 'ICMS', 'Crédito ICMS'],
         {'Situação': 30, 'Transportador': 30, 'Tomador (quem paga)': 30, 'Remetente': 28, 'Destinatário': 28,
          'Observação': 46, 'Chave': 46})

    # ---------------- resumo
    comp = res['competencia']
    emp = R.r['empresa']
    ws0['A1'] = f'Entradas {comp[5:]}/{comp[:4]} — {emp["nome"]}'
    ws0['A1'].font = Font(bold=True, size=14, color='1F3864')
    ws0['A2'] = 'Uma linha por documento. Marque a coluna "Conferido" ao lançar/conferir no Domínio.'
    ws0['A2'].font = Font(italic=True, color='595959')
    cab = ['Aba', 'Documentos', 'A lançar', 'Conferir', 'Cancelados / não lançar', 'Valor a lançar', 'Crédito ICMS']
    for j, c in enumerate(cab, 1):
        cel = ws0.cell(4, j, c)
        cel.font = Font(bold=True, color='FFFFFF')
        cel.fill = AZUL
    blocos = [(f'NF-e dentro do estado ({uf})', nfe_in, 'Valor contábil', 'Crédito ICMS'),
              ('NF-e fora do estado', nfe_out, 'Valor contábil', 'Crédito ICMS'),
              ('Devoluções e retornos', dev, 'Valor contábil', None),
              ('Serviços tomados (NFS-e)', sv, 'Valor', None),
              ('CT-e (fretes)', ct, 'Valor', 'Crédito ICMS')]
    for i, (nome, ls, cv, cc) in enumerate(blocos, 5):
        lanc = [l for l in ls if l['Situação'] == 'A LANÇAR']
        vals = [nome, len(ls), len(lanc), sum(1 for l in ls if l['Situação'] == 'CONFERIR'),
                sum(1 for l in ls if l['Situação'] not in ('A LANÇAR', 'CONFERIR')),
                float(sum((Decimal(str(l.get(cv) or 0)) for l in ls if l['Situação'] in ('A LANÇAR', 'CONFERIR')), Z)),
                float(sum((Decimal(str(l.get(cc) or 0)) for l in ls), Z)) if cc else None]
        for j, v in enumerate(vals, 1):
            cel = ws0.cell(i, j, v)
            if isinstance(v, float):
                cel.number_format = NUM
    ws0.cell(11, 1, 'Cores da coluna Situação: verde = lançar · amarelo = conferir antes · cinza = cancelada/não lançar.')
    ws0.cell(11, 1).font = Font(italic=True, color='595959')
    for j, w in enumerate([30, 12, 10, 10, 22, 16, 14], 1):
        ws0.column_dimensions[get_column_letter(j)].width = w
    wb.save(saida)
