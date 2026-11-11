#!/usr/bin/env python3
"""Gera a planilha (e o PDF) de demonstrações + índices no padrão ROF aprovado para licitações.

Uso:
  python3 gerar_demonstracoes.py dados.json --socio "NOME DO SÓCIO" -o "Empresa_Demonstracoes"
      [--dre-anterior dados_ano_anterior.json] [--contador "RENATA AMADO BASTOS"] [--cargo-contador Contadora]
      [--crc "PR-000000/O-0"] [--cargo-socio "Sócio-Administrador"] [--pl-minimo 46337.30] [--sem-pdf]

Saída: <o>.xlsx e <o>.pdf (o PDF precisa do LibreOffice; sem ele, exporte o PDF pelo Excel).
Abas: Balanço Patrimonial · DRE · DLPA · Índices (componentes e índices lado a lado, anos anterior | atual).
Os arquivos são para o cliente apresentar: sem fonte, sem finalidade, sem notas e sem fórmula.
A análise interna (saldos invertidos, PL mínimo) sai só no terminal.
"""
import argparse, json, os, re, shutil, subprocess, sys, unicodedata
from openpyxl import Workbook
from openpyxl.styles import Font, Alignment, PatternFill, Border, Side

F = 'Arial'
NUM = '[$-416]#,##0.00;(#,##0.00);"-"'
IDX = '[$-416]0.00;-0.00;"-"'
thin = Side(style='thin', color='999999')
HEAD = PatternFill('solid', fgColor='1F3864'); SUB = PatternFill('solid', fgColor='D9E1F2'); TOT = PatternFill('solid', fgColor='F2F2F2')

def norm(s):
    return unicodedata.normalize('NFKD', s).encode('ascii', 'ignore').decode().upper()

def titulo(s):
    pequenas = {'a', 'e', 'o', 'de', 'da', 'do', 'das', 'dos', 'com', 'para', 'por', 'em', 'ou', 'no', 'na'}
    sig = {'ISS', 'PIS', 'COFINS', 'INSS', 'FGTS', 'IRPJ', 'CSLL', 'IRRF', 'IOF', 'ICMS', 'IPI', 'DAS', 'IR'}
    out = []
    for i, w in enumerate(s.lower().split()):
        if w.upper() in sig: out.append(w.upper())
        elif i and w in pequenas: out.append(w)
        else: out.append(w[:1].upper() + w[1:])
    return ' '.join(out)

def fmt_cnpj(c):
    c = re.sub(r'\D', '', c)
    return f'{c[:2]}.{c[2:5]}.{c[5:8]}/{c[8:12]}-{c[12:]}' if len(c) == 14 else c

def cab(ws, row, cols, left=(1,)):
    for i, c in enumerate(cols, 1):
        if c is None: continue
        x = ws.cell(row=row, column=i, value=c); x.font = Font(name=F, bold=True, color='FFFFFF'); x.fill = HEAD
        x.alignment = Alignment(horizontal='left' if i in left else 'center', vertical='center')
    ws.row_dimensions[row].height = 22

def linha(ws, r, rotulo, vals, estilo=None, recuo=0, fmt=NUM, col0=1):
    b = estilo in ('grp', 'tot', 'sub')
    c = ws.cell(row=r, column=col0, value=rotulo); c.font = Font(name=F, bold=b); c.alignment = Alignment(indent=recuo)
    for j, v in enumerate(vals, col0 + 1):
        x = ws.cell(row=r, column=j, value=v); x.number_format = fmt; x.font = Font(name=F, bold=b)
    for j in range(col0, col0 + len(vals) + 1):
        cc = ws.cell(row=r, column=j); cc.border = Border(bottom=thin)
        if estilo in ('grp', 'tot'): cc.fill = SUB if estilo == 'grp' else TOT

def assinaturas(ws, r, a):
    r += 4
    nome_c = a.contador + (f' — CRC {a.crc}' if a.crc else '')
    for t, b in (('_______________________________________', False), (nome_c, True), (a.cargo_contador, False)):
        ws.cell(row=r, column=1, value=t).font = Font(name=F, bold=b); r += 1
    r += 4
    for t, b in (('_______________________________________', False), (a.socio, True), (a.cargo_socio, False)):
        ws.cell(row=r, column=1, value=t).font = Font(name=F, bold=b); r += 1

def montar_balanco(ws, d, a):
    e = d['empresa']
    ws.cell(row=1, column=1, value=e['nome']).font = Font(name=F, bold=True, size=13)
    ws.cell(row=2, column=1, value=f"CNPJ: {fmt_cnpj(e['cnpj'])}").font = Font(name=F, size=10)
    ws.cell(row=4, column=1, value='BALANÇO PATRIMONIAL').font = Font(name=F, bold=True, size=12)
    cab(ws, 6, ['Conta', d['data_atual'], d['data_anterior']])
    bp = d['balanco']
    filhos = {}
    for x in bp: filhos.setdefault(x['sup'], []).append(x)
    linhas_ref = {}
    r = 7
    def folhas(x):
        """contas a listar sob um grupo de nível 3: analíticas, sem repetir o próprio grupo"""
        out = []
        def desce(n):
            fs = filhos.get(n['cod'], [])
            if not fs: out.append(n); return
            for f in fs: desce(f)
        for f in filhos.get(x['cod'], []): desce(f)
        if len(out) == 1 and norm(out[0]['descr']) == norm(x['descr']): return []
        return out
    for n1 in filhos.get('', []):
        nome1 = n1['descr'].upper()
        linha(ws, r, nome1, ['', ''], 'grp'); r += 1
        tem_pnc = any('NAO CIRCULANTE' in norm(x['descr']).replace('-', ' ') or 'EXIGIVEL' in norm(x['descr'])
                      for x in filhos.get(n1['cod'], []))
        for n2 in filhos.get(n1['cod'], []):
            if n1['grp'] == 'P' and not tem_pnc and 'PATRIMONIO' in norm(n2['descr']):
                linha(ws, r, 'PASSIVO NÃO CIRCULANTE', ['', ''], 'sub', 1); r += 1
                linha(ws, r, 'Total do Passivo Não Circulante', [0, 0], 'tot', 1); r += 1
            linha(ws, r, n2['descr'].upper().replace('NÃO-', 'NÃO '), ['', ''], 'sub', 1); r += 1
            pl = 'PATRIMONIO' in norm(n2['descr'])
            for n3 in filhos.get(n2['cod'], []):
                fs = [] if pl else folhas(n3)
                if fs:
                    for f in fs:
                        linha(ws, r, titulo(f['descr']), [f['atual'], f['anterior']], None, 3); r += 1
                    linha(ws, r, titulo(n3['descr']), [n3['atual'], n3['anterior']], 'sub', 2); r += 1
                else:
                    linha(ws, r, titulo(n3['descr']), [n3['atual'], n3['anterior']], None, 3); r += 1
            linha(ws, r, 'Total do ' + titulo(n2['descr']).replace('Não-', 'Não '), [n2['atual'], n2['anterior']], 'tot', 1)
            linhas_ref[n2['cod']] = r; r += 1
        rot = 'TOTAL DO ATIVO' if n1['grp'] == 'A' else 'TOTAL DO PASSIVO E PATRIMÔNIO LÍQUIDO'
        linha(ws, r, rot, [n1['atual'], n1['anterior']], 'grp'); r += 2
    assinaturas(ws, r - 1, a)
    ws.column_dimensions['A'].width = 55; ws.column_dimensions['B'].width = 18; ws.column_dimensions['C'].width = 18

def montar_dre(ws, d, ant, a):
    ws.cell(row=1, column=1, value='DEMONSTRAÇÃO DO RESULTADO DO EXERCÍCIO').font = Font(name=F, bold=True, size=12)
    anos = [d['exercicio']] + ([ant['exercicio']] if ant else [])
    cab(ws, 3, ['Descrição'] + anos)
    mapa_ant = {norm(x['descr']): x['valor'] for x in ant['dre']} if ant else {}
    r = 4
    for x in d['dre']:
        total = x['tipo'] == 'T'
        estilo = 'grp' if x['nivel'] <= 2 or 'LIQUID' in norm(x['descr']) or 'BRUTA' in norm(x['descr']) else ('tot' if total else None)
        vals = [x['valor']] + ([mapa_ant.get(norm(x['descr']), 0)] if ant else [])
        linha(ws, r, x['descr'].upper() if total else titulo(x['descr']), vals, estilo, 0 if total else 1); r += 1
    assinaturas(ws, r, a)
    ws.column_dimensions['A'].width = 55
    for c in 'BC': ws.column_dimensions[c].width = 18

def montar_dlpa(ws, d, a):
    ws.cell(row=1, column=1, value='DEMONSTRAÇÃO DE LUCROS OU PREJUÍZOS ACUMULADOS').font = Font(name=F, bold=True, size=12)
    cab(ws, 3, ['Descrição', d['exercicio']])
    pl = [x for x in d['balanco'] if x['nivel'] == 2 and 'PATRIMONIO' in norm(x['descr'])]
    lp = [x for x in d['balanco'] if pl and x['sup'] == pl[0]['cod'] and ('LUCRO' in norm(x['descr']) or 'PREJU' in norm(x['descr']))]
    ini = round(sum(x['anterior'] for x in lp), 2); fim = round(sum(x['atual'] for x in lp), 2)
    lucro = d.get('lucro_liquido') or 0
    outras = round(fim - ini - lucro, 2)
    r = 4
    linha(ws, r, f"Saldo em {d['data_anterior']}", [ini], 'tot'); r += 1
    linha(ws, r, '(+) Lucro Líquido do Exercício' if lucro >= 0 else '(−) Prejuízo do Exercício', [lucro]); r += 1
    linha(ws, r, '(−) Lucros Distribuídos', [outras]); r += 1
    linha(ws, r, f"Saldo em {d['data_atual']}", [fim], 'grp'); r += 1
    assinaturas(ws, r, a)
    ws.column_dimensions['A'].width = 55; ws.column_dimensions['B'].width = 18
    return ini, fim, lucro, outras

def montar_indices(ws, d, a):
    ws.cell(row=1, column=1, value='ÍNDICES DE LIQUIDEZ E SOLVÊNCIA').font = Font(name=F, bold=True, size=12)
    ano_ant, ano_at = d['data_anterior'][-4:], d['data_atual'][-4:]
    cab(ws, 3, ['Componente', ano_ant, ano_at, None, 'Índice', ano_ant, ano_at], left=(1, 5))
    c = d['componentes']; cr = {}; r = 4
    for rot, k in [('Ativo Circulante', 'ac'), ('Estoques', 'estoques'), ('Realizável a Longo Prazo', 'rlp'),
                   ('Ativo Total', 'at'), ('Passivo Circulante', 'pc'), ('Exigível a Longo Prazo', 'elp'),
                   ('Patrimônio Líquido', 'pl')]:
        linha(ws, r, rot, [c[k]['anterior'], c[k]['atual']]); cr[k] = r; r += 1
    g = lambda col, k: f'{col}{cr[k]}'
    idx = [('Liquidez Geral', lambda s: f'=IF(({g(s,"pc")}+{g(s,"elp")})=0,"-",({g(s,"ac")}+{g(s,"rlp")})/({g(s,"pc")}+{g(s,"elp")}))'),
           ('Liquidez Corrente', lambda s: f'=IF({g(s,"pc")}=0,"-",{g(s,"ac")}/{g(s,"pc")})'),
           ('Liquidez Seca', lambda s: f'=IF({g(s,"pc")}=0,"-",({g(s,"ac")}-{g(s,"estoques")})/{g(s,"pc")})'),
           ('Solvência Geral', lambda s: f'=IF(({g(s,"pc")}+{g(s,"elp")})=0,"-",{g(s,"at")}/({g(s,"pc")}+{g(s,"elp")}))')]
    ir = 4
    for rot, fn in idx:
        for col, v in ((5, rot), (6, fn('B')), (7, fn('C'))):
            x = ws.cell(row=ir, column=col, value=v); x.font = Font(name=F, bold=True); x.fill = TOT
            x.border = Border(bottom=thin)
            if col > 5: x.number_format = IDX
        ir += 1
    assinaturas(ws, r, a)
    for col, w in zip('ABCDEFG', (30, 16, 16, 3, 22, 12, 12)): ws.column_dimensions[col].width = w
    ws.page_setup.orientation = 'landscape'

def indices_py(c, q):
    def div(n, dd): return None if abs(dd) < 0.005 else n / dd
    pc, elp = c['pc'][q], c['elp'][q]
    return {'LG': div(c['ac'][q] + c['rlp'][q], pc + elp), 'LC': div(c['ac'][q], pc),
            'LS': div(c['ac'][q] - c['estoques'][q], pc), 'SG': div(c['at'][q], pc + elp)}

def soffice():
    for cand in ('soffice', 'libreoffice', r'C:\Program Files\LibreOffice\program\soffice.exe'):
        p = shutil.which(cand) or (cand if os.path.exists(cand) else None)
        if p: return p
    return None

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('dados'); ap.add_argument('-o', '--out', required=True)
    ap.add_argument('--socio', required=True); ap.add_argument('--cargo-socio', default='Sócio-Administrador')
    ap.add_argument('--contador', default='RENATA AMADO BASTOS'); ap.add_argument('--cargo-contador', default='Contadora')
    ap.add_argument('--crc', default=''); ap.add_argument('--dre-anterior')
    ap.add_argument('--pl-minimo', type=float); ap.add_argument('--sem-pdf', action='store_true')
    a = ap.parse_args()
    d = json.load(open(a.dados, encoding='utf-8'))
    ant = json.load(open(a.dre_anterior, encoding='utf-8')) if a.dre_anterior else None
    wb = Workbook()
    ws = wb.active; ws.title = 'Balanço Patrimonial'; montar_balanco(ws, d, a)
    montar_dre(wb.create_sheet('DRE'), d, ant, a)
    ini, fim, lucro, outras = montar_dlpa(wb.create_sheet('DLPA'), d, a)
    montar_indices(wb.create_sheet('Índices'), d, a)
    for s in wb.worksheets:
        s.sheet_view.showGridLines = False
        s.page_setup.paperSize = 9; s.page_setup.fitToWidth = 1; s.page_setup.fitToHeight = 1
        s.sheet_properties.pageSetUpPr.fitToPage = True; s.print_options.horizontalCentered = True
    xlsx = a.out + '.xlsx'; wb.save(xlsx); print('Planilha:', xlsx)

    # ---------- análise interna (só no terminal, não vai para o cliente)
    c = d['componentes']
    print('\nÍNDICES', d['data_anterior'], '|', d['data_atual'])
    i0, i1 = indices_py(c, 'anterior'), indices_py(c, 'atual')
    f = lambda v: '-' if v is None else f'{v:.2f}'.replace('.', ',')
    for k, n in (('LG', 'Liquidez Geral'), ('LC', 'Liquidez Corrente'), ('LS', 'Liquidez Seca'), ('SG', 'Solvência Geral')):
        print(f'  {n:18} {f(i0[k]):>8} | {f(i1[k]):>8}')
    alertas = []
    for k in ('ac', 'pc', 'pl'):
        for q in ('anterior', 'atual'):
            if c[k][q] < 0: alertas.append(f'{k.upper()} negativo em {d["data_" + q]}: {c[k][q]:,.2f}')
    for x in d['balanco']:
        if x['tipo'] == 'D':
            for q in ('anterior', 'atual'):
                redutora = x['descr'].strip().startswith('(-)') or 'DEPRECIA' in norm(x['descr']) or 'AMORTIZA' in norm(x['descr'])
                if x[q] < 0 and not redutora:
                    lado = 'credor no Ativo' if x['grp'] == 'A' else 'devedor no Passivo'
                    alertas.append(f'Saldo {lado}: {x["descr"]} em {d["data_" + q]} = {x[q]:,.2f}')
    if abs(outras) >= 0.005:
        alertas.append(f'DLPA: movimentação de lucros além do resultado = {outras:,.2f} (lançada como "Lucros Distribuídos": confirmar natureza)')
    if a.pl_minimo:
        for q in ('anterior', 'atual'):
            alertas.append(f'PL {d["data_" + q]} = {c["pl"][q]:,.2f} ' + ('>=' if c['pl'][q] >= a.pl_minimo else '<') + f' mínimo {a.pl_minimo:,.2f}')
    if not ant:
        alertas.append(f'DRE só de {d["exercicio"]}: para os 2 exercícios, rode também a ECD do ano anterior e use --dre-anterior')
    print('\nALERTAS (para a contadora, não vão no arquivo):')
    for x in alertas or ['nenhum']: print('  -', x)

    if a.sem_pdf: return
    so = soffice()
    if not so:
        print('\nPDF não gerado: LibreOffice não encontrado. Abra a planilha no Excel e use Arquivo > Exportar > PDF (pasta de trabalho inteira).')
        return
    outdir = os.path.dirname(os.path.abspath(xlsx))
    subprocess.run([so, '--headless', '--convert-to', 'pdf', '--outdir', outdir, xlsx],
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=180)
    pdf = a.out + '.pdf'
    print('PDF:', pdf if os.path.exists(pdf) else 'falhou (exporte pelo Excel)')

if __name__ == '__main__':
    main()
