#!/usr/bin/env python3
"""Conferência mensal de notas da PRUMO COMERCIAL LTDA (empresa 272 no Domínio).

Cruza XML (NF-e e CT-e) x relatórios do Sieg x PLANILHA DE VENDAS PRISMA x relatório
"Acompanhamento de Entradas" do Domínio e gera a planilha colorida por situação.

Uso:
  python3 -I conferencia_prumo.py --xml <pasta com todos os zips extraídos> \
      --dominio Entradas_Domino.xls --sieg-nfe Relatorio_Relatorio_Basico.xlsx \
      --sieg-cte Relatorio_CTe.xlsx --prisma "PLANILHA DE VENDAS PRISMA - SETEMBRO 2026.xlsx" \
      --competencia 09/2026 --saida Conferencia_Notas_09.2026_Prumo.xlsx

Todos os XML podem ficar misturados em --xml (subpastas à vontade): o script
classifica cada um pelo conteúdo (emitente, destinatário, série, tpNF, tomador do CT-e,
eventos de cancelamento) e elimina duplicados pela chave.
"""
import argparse, glob, os, re, subprocess, sys, tempfile
import xml.etree.ElementTree as ET
import numpy as np
import pandas as pd
import openpyxl
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter

PRUMO = '41751764000104'

# ---------------------------------------------------------------- utilidades
def br(v):
    return f'{v:,.2f}'.replace(',', 'X').replace('.', ',').replace('X', '.')

def _s(t):
    return t.split('}')[-1]

def _first(e, name):
    for x in e.iter():
        if _s(x.tag) == name:
            return x

def _tx(e, path):
    cur = e
    for p in path.split('/'):
        if cur is None:
            return ''
        cur = next((c for c in cur if _s(c.tag) == p), None)
    return (cur.text or '') if cur is not None else ''

# ---------------------------------------------------------------- leitura dos XML
def ler_xmls(pasta):
    nfe, cte, ev = {}, {}, []
    for f in glob.glob(os.path.join(pasta, '**', '*.xml'), recursive=True):
        try:
            r = ET.parse(f).getroot()
        except Exception:
            print('XML ilegível:', f, file=sys.stderr); continue
        inf = None if _first(r, 'infCte') is not None else _first(r, 'infNFe')  # CT-e também tem <infNFe> (docs transportados)
        if inf is not None:
            ide = _first(inf, 'ide'); prot = _first(r, 'infProt')
            ch = inf.get('Id', '')[3:]
            d = dict(chave=ch, nNF=int(_tx(ide, 'nNF')), serie=_tx(ide, 'serie'), dhEmi=(_tx(ide, 'dhEmi') or _tx(ide, 'dEmi'))[:10],
                     tpNF=_tx(ide, 'tpNF'), finNFe=_tx(ide, 'finNFe'), natOp=_tx(ide, 'natOp'),
                     emit_cnpj=_tx(inf, 'emit/CNPJ') or _tx(inf, 'emit/CPF'), emit=_tx(inf, 'emit/xNome'), emit_uf=_tx(inf, 'emit/enderEmit/UF'),
                     dest_cnpj=_tx(inf, 'dest/CNPJ') or _tx(inf, 'dest/CPF'), dest=_tx(inf, 'dest/xNome'), dest_uf=_tx(inf, 'dest/enderDest/UF'),
                     cfops=' '.join(sorted({x.text for x in inf.iter() if _s(x.tag) == 'CFOP'})),
                     vNF=float(_tx(inf, 'total/ICMSTot/vNF') or 0), vICMS=float(_tx(inf, 'total/ICMSTot/vICMS') or 0),
                     vFrete=float(_tx(inf, 'total/ICMSTot/vFrete') or 0),
                     cStat=_tx(prot, 'cStat') if prot is not None else '',
                     inutilizada='inutiliza' in os.path.basename(f).lower(),
                     infCpl=_tx(inf, 'infAdic/infCpl').replace('&||&', '').replace('^', ' ').strip()[:200])
            # sem protocolo e com nome de inutilização = número inutilizado
            if not d['cStat'] and not d['inutilizada']:
                d['inutilizada'] = None  # sem protocolo: marcar para revisão
            old = nfe.get(ch)
            if old is None or (not old['cStat'] and d['cStat']):
                nfe[ch] = d
            continue
        ic = _first(r, 'infCte')
        if ic is not None:
            ide = _first(ic, 'ide'); prot = _first(r, 'infProt')
            toma = _tx(ide, 'toma3/toma') or _tx(ide, 'toma4/toma')
            papel = {'0': 'rem', '1': 'exped', '2': 'receb', '3': 'dest'}.get(toma)
            tom_cnpj = _tx(ic, f'{papel}/CNPJ') if papel else _tx(ide, 'toma4/CNPJ')
            cte[ic.get('Id')[3:]] = dict(chave=ic.get('Id')[3:], nCT=_tx(ide, 'nCT'), serie=_tx(ide, 'serie'), dhEmi=_tx(ide, 'dhEmi')[:10],
                                         emit=_tx(ic, 'emit/xNome'), toma=toma, tomador_cnpj=tom_cnpj, vTPrest=float(_tx(ic, 'vPrest/vTPrest') or 0),
                                         cStat=_tx(prot, 'cStat') if prot is not None else '')
            continue
        e = _first(r, 'infEvento')
        if e is not None:
            desc = _first(e, 'descEvento'); xj = _first(e, 'xJust'); xc = _first(e, 'xCorrecao')
            ev.append(dict(chave=_tx(e, 'chNFe') or _tx(e, 'chCTe'), tpEvento=_tx(e, 'tpEvento'), data=_tx(e, 'dhEvento')[:10],
                           desc=(desc.text if desc is not None else ''), just=((xj if xj is not None else xc).text if (xj is not None or xc is not None) else '')))
    return pd.DataFrame(nfe.values()), pd.DataFrame(cte.values()), pd.DataFrame(ev, columns=['chave', 'tpEvento', 'data', 'desc', 'just'])

# ---------------------------------------------------------------- relatório Domínio
def ler_dominio(caminho):
    if caminho.lower().endswith('.xls'):
        out = tempfile.mkdtemp()
        subprocess.run(['soffice', '--headless', '--convert-to', 'xlsx', '--outdir', out, caminho], check=True,
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=180)
        caminho = os.path.join(out, os.path.splitext(os.path.basename(caminho))[0] + '.xlsx')
    d = pd.read_excel(caminho, header=None)
    hdr = d.index[d[0].astype(str).str.strip() == 'Código'][0]
    cols = {str(v).strip(): j for j, v in d.loc[hdr].items() if pd.notna(v)}
    need = ['Data', 'Nota', 'Série', 'Espécie', 'Fornecedor', 'CFOP', 'AC.', 'UF', 'Valor Contábil', 'Tipo', 'Base Cálculo', 'Valor']
    faltam = [c for c in need if c not in cols]
    if faltam:
        sys.exit(f'Relatório do Domínio fora do leiaute "Acompanhamento de Entradas" (faltam {faltam})')
    j = cols
    m = pd.to_numeric(d[0], errors='coerce').notna() & d[j['Nota']].notna()
    c = d[m]
    dom = pd.DataFrame({'cod': c[0].astype(int), 'data': pd.to_datetime(c[j['Data']]).dt.strftime('%Y-%m-%d'),
                        'nota': c[j['Nota']].astype(str).str.replace(r'\.0$', '', regex=True).str.lstrip('0'),
                        'serie': c[j['Série']].fillna('').astype(str).str.replace(r'\.0$', '', regex=True),
                        'esp': c[j['Espécie']].astype(int), 'forn': c[j['Fornecedor']], 'cfop': c[j['CFOP']], 'ac': c[j['AC.']],
                        'uf': c[j['UF']], 'vc': pd.to_numeric(c[j['Valor Contábil']], errors='coerce'), 'tipo': c[j['Tipo']],
                        'icms': pd.to_numeric(c[j['Valor']], errors='coerce')})
    # ICMS de todas as linhas de imposto (linhas de continuação) somado por lançamento
    icms = {}; cur = None
    for i, r in d.iterrows():
        if m.get(i, False):
            cur = int(r[0])
        elif str(r[0]).startswith(('Sub', 'Total')):
            cur = None
        if cur is not None and str(r[j['Tipo']]).strip() == 'ICMS':
            icms[cur] = icms.get(cur, 0) + (pd.to_numeric(r[j['Valor']], errors='coerce') or 0)
    dom['icms_proprio'] = dom.cod.map(icms).fillna(0)
    return dom

# ---------------------------------------------------------------- PRISMA
def ler_prisma(caminho):
    wb = openpyxl.load_workbook(caminho, data_only=True); ws = wb.worksheets[0]
    hdr = None; rows = []
    for r in ws.iter_rows():
        v = [c.value for c in r]
        if v and 'DANFE' in [str(x).strip().upper() for x in v if x is not None]:
            hdr = {str(x).strip().upper(): k for k, x in enumerate(v) if x is not None}; continue
        if hdr and isinstance(v[hdr['DANFE']], (int, float)):
            g = lambda k: v[hdr[k]] if k in hdr else None
            rows.append(dict(danfe=int(v[hdr['DANFE']]), data=g('DATA'), valor=g('VALOR'), cliente=g('CLIENTE'),
                             canc=g('CANC'), dev=g('DEV'), reme=g('REME')))
    return pd.DataFrame(rows)

# ---------------------------------------------------------------- cores / legenda
HDR = PatternFill('solid', fgColor='1F4E78'); GRY = PatternFill('solid', fgColor='EDEDED')
thin = Side(style='thin', color='BFBFBF')
CORES = {
    'NF-e – LANÇADA OK': ('FFFFFF', 'NF-e de fornecedor: XML = Sieg = Domínio (número, série e valor)'),
    'CT-e – LANÇADO OK': ('E2EFDA', 'CT-e com a PRUMO tomadora: Sieg = Domínio (número, série, valor e data)'),
    'AUTORIZADA': ('FFFFFF', 'Nota autorizada e conferida'),
    'AUTORIZADA – REMESSA/RETORNO': ('E4DFEC', 'Autorizada, operação de remessa/retorno (PRISMA marca REME)'),
    'DEVOLUÇÃO (entrada própria)': ('BDD7EE', 'Nota de entrada emitida pela Prumo (devolução/retorno) – autorizada'),
    'AUTORIZADA – VALOR ≠ PRISMA': ('FFF2CC', 'Autorizada, mas o valor do XML difere da PRISMA'),
    'AUTORIZADA – FORA DA PRISMA': ('FFD966', 'Autorizada no XML e não consta na PRISMA do mês'),
    'NF-e – VALOR ≠ DOMÍNIO': ('FFD966', 'NF-e lançada com valor diferente do XML'),
    'ENTRADA PRÓPRIA – SEM XML': ('9DC3E6', 'Entrada emitida pela Prumo, lançada na Domínio, mas o XML não está na pasta'),
    'LANÇADA SEM XML/SIEG': ('9DC3E6', 'Lançada na Domínio sem XML e sem Sieg – conferir'),
    'CANCELADA': ('F4B183', 'Cancelada (evento de cancelamento)'),
    'CANCELADA – LANÇADA COM VALOR ZERO': ('F4B183', 'Cancelada; na Domínio com valor 0,00 – conferir situação "cancelada"'),
    'INUTILIZADA': ('BFBFBF', 'Número inutilizado – nota não existe'),
    'SEM PROTOCOLO – CONFERIR': ('BFBFBF', 'XML sem protocolo de autorização – conferir na SEFAZ'),
    'SERVIÇO TOMADO – NÃO CONFERIDO': ('D9D9D9', 'Espécie 39 (serviço) – fora desta conferência de NF-e/CT-e'),
    'ERRO – CANCELADO LANÇADO COM VALOR': ('FF7C80', 'Documento cancelado lançado na Domínio com valor/crédito – corrigir'),
    'ERRO – INUTILIZADA LANÇADA NA DOMÍNIO': ('C00000', 'Número inutilizado lançado como entrada na Domínio – corrigir'),
    'NÃO LANÇADA NA DOMÍNIO': ('FF0000', 'Documento com XML/Sieg e sem lançamento na Domínio'),
    'NÃO LOCALIZADA': ('FF0000', 'Número sem XML na pasta e sem lançamento – quebra de sequência'),
}
BRANCO_TXT = ('C00000', 'FF0000')
W = {'Chave de acesso': 47, 'Documento': 16, 'Data Domínio': 12, 'Emitente / Fornecedor': 40, 'CFOP XML': 12, 'CFOP Domínio': 12,
     'Acum': 8, 'Valor XML/Sieg': 13, 'Valor Domínio': 13, 'Cód Domínio': 12, 'Série': 6, 'Nota': 10, 'Situação': 38, 'Emissão': 11,
     'Destinatário': 42, 'CFOP': 14, 'Natureza': 30, 'Valor XML': 12, 'Valor': 12, 'PRISMA Cliente': 18, 'PRISMA Valor': 12,
     'PRISMA Marcação': 18, 'Lançada na Domínio (entrada)': 20, 'Observação': 70, 'UF': 5}

def aba_colorida(wb, titulo_aba, df, titulo):
    ws = wb.create_sheet(titulo_aba)
    ws['A1'] = titulo; ws['A1'].font = Font(bold=True, size=13)
    ws['A3'] = 'LEGENDA'; ws['A3'].font = Font(bold=True)
    vcol = next(c for c in ['Valor Domínio', 'Valor XML', 'Valor'] if c in df)
    for j, h in enumerate(['Cor', 'Situação', 'Qtde', vcol, 'O que significa'], 1):
        c = ws.cell(4, j, h); c.font = Font(bold=True, color='FFFFFF'); c.fill = HDR
    r = 5
    for k, (cor, desc) in CORES.items():
        sub = df[df['Situação'] == k]
        if not len(sub):
            continue
        ws.cell(r, 1).fill = PatternFill('solid', fgColor=cor); ws.cell(r, 1).border = Border(left=thin, right=thin, top=thin, bottom=thin)
        c = ws.cell(r, 2, k); c.fill = PatternFill('solid', fgColor=cor); c.font = Font(bold=True, color='FFFFFF' if cor in BRANCO_TXT else '000000')
        ws.cell(r, 3, len(sub)); v = ws.cell(r, 4, float(pd.to_numeric(sub[vcol], errors='coerce').sum())); v.number_format = '#,##0.00'
        ws.cell(r, 5, desc); r += 1
    ws.cell(r, 2, 'TOTAL').font = Font(bold=True); ws.cell(r, 3, len(df)).font = Font(bold=True)
    h = r + 2
    for j, cn in enumerate(df.columns, 1):
        c = ws.cell(h, j, cn); c.font = Font(bold=True, color='FFFFFF'); c.fill = HDR; c.alignment = Alignment(wrap_text=True)
    isit = list(df.columns).index('Situação')
    for i, row in enumerate(df.itertuples(index=False), h + 1):
        cor = CORES[row[isit]][0]; f = PatternFill('solid', fgColor=cor)
        for j, v in enumerate(row, 1):
            if isinstance(v, float) and np.isnan(v):
                v = None
            c = ws.cell(i, j, v); c.border = Border(bottom=thin)
            if isinstance(v, float):
                c.number_format = '#,##0.00'
            if df.columns[j - 1] == 'Chave de acesso':
                c.number_format = '@'
            if cor != 'FFFFFF':
                c.fill = f
            if cor in BRANCO_TXT:
                c.font = Font(color='FFFFFF', bold=True)
    ws.freeze_panes = ws.cell(h + 1, isit + 2)
    ws.auto_filter.ref = f'A{h}:{get_column_letter(len(df.columns))}{h + len(df)}'
    for j, cn in enumerate(df.columns, 1):
        ws.column_dimensions[get_column_letter(j)].width = W.get(cn, 14)

def aba_simples(wb, titulo, df, larg=None):
    ws = wb.create_sheet(titulo)
    for j, c in enumerate(df.columns, 1):
        cell = ws.cell(1, j, c); cell.font = Font(bold=True, color='FFFFFF'); cell.fill = HDR
    for i, row in enumerate(df.itertuples(index=False), 2):
        for j, v in enumerate(row, 1):
            if isinstance(v, float) and np.isnan(v):
                v = None
            c = ws.cell(i, j, v)
            if isinstance(v, float):
                c.number_format = '#,##0.00'
    ws.freeze_panes = 'A2'
    for j, c in enumerate(df.columns, 1):
        ws.column_dimensions[get_column_letter(j)].width = (larg or {}).get(c, min(45, max(10, len(str(c)) + 2)))
    return ws

# ---------------------------------------------------------------- sequência de saídas
def sequencia(notas, serie, canc, cce, dom, prisma=None):
    """notas = NF-e emitidas pela Prumo naquela série (saídas e entradas próprias)."""
    n = notas[notas.serie == serie]
    if not len(n):
        return pd.DataFrame()
    pr = prisma.set_index('danfe') if prisma is not None and len(prisma) else None
    domS = dom[(dom.esp == 36) & (dom.serie == serie)]
    rows = []
    for k in range(n.nNF.min(), n.nNF.max() + 1):
        a = n[n.nNF == k]; dd = domS[domS.nota == str(k)]
        pp = pr.loc[k] if pr is not None and k in pr.index else None
        if isinstance(pp, pd.DataFrame):
            pp = pp.iloc[0]
        r = a.iloc[0] if len(a) else None
        obs = []
        if r is None:
            sit = 'ENTRADA PRÓPRIA – SEM XML' if len(dd) else 'NÃO LOCALIZADA'
            if len(dd):
                obs.append('Lançada na Domínio como entrada; XML não está na pasta')
        else:
            entrada = r.tpNF == '0'
            if r.inutilizada:
                sit = 'ERRO – INUTILIZADA LANÇADA NA DOMÍNIO' if len(dd) and dd.vc.sum() > 0 else 'INUTILIZADA'
            elif r.inutilizada is None:
                sit = 'SEM PROTOCOLO – CONFERIR'
            elif r.chave in canc:
                sit = 'CANCELADA'
                if pp is not None and pd.isna(pp.canc):
                    obs.append('PRISMA não marca CANC')
                if len(dd) and dd.vc.sum() > 0:
                    sit = 'ERRO – CANCELADO LANÇADO COM VALOR'
            elif entrada:
                sit = 'DEVOLUÇÃO (entrada própria)'
                if not len(dd):
                    obs.append('Entrada própria NÃO lançada na Domínio')
            elif pr is not None and pp is None:
                sit = 'AUTORIZADA – FORA DA PRISMA'
            elif pp is not None and abs(r.vNF - float(pp.valor or 0)) > 0.01:
                sit = 'AUTORIZADA – VALOR ≠ PRISMA'
                dif = r.vNF - float(pp.valor or 0)
                obs.append(f'XML {br(r.vNF)} x PRISMA {br(float(pp.valor or 0))} (dif. {br(dif)})' +
                           (' = frete destacado na NF; PRISMA registra só produtos' if abs(dif - r.vFrete) < 0.01 and r.vFrete else ''))
            elif pp is not None and pd.notna(pp.reme):
                sit = 'AUTORIZADA – REMESSA/RETORNO'
            else:
                sit = 'AUTORIZADA'
            if r.chave in cce:
                obs.append(f'{cce[r.chave]} CC-e')
            if r.infCpl and entrada:
                obs.append(r.infCpl[:120])
        rows.append({'Nota': k, 'Chave de acesso': None if r is None else r.chave, 'Situação': sit,
                     'Emissão': None if r is None else r.dhEmi,
                     'Destinatário': (dd.forn.iloc[0] if len(dd) else None) if r is None else r.dest,
                     'CFOP': (str(dd.cfop.iloc[0]) if len(dd) else None) if r is None else r.cfops,
                     'Natureza': None if r is None else r.natOp,
                     'Valor XML': (float(dd.vc.sum()) if len(dd) else None) if r is None else r.vNF,
                     **({'PRISMA Cliente': None if pp is None else pp.cliente, 'PRISMA Valor': None if pp is None else pp.valor,
                         'PRISMA Marcação': None if pp is None else ' / '.join(x for x, y in [('CANC', pp.canc), ('DEV', pp.dev), ('REMESSA', pp.reme)] if pd.notna(y)) or None}
                        if pr is not None else {}),
                     'Lançada na Domínio (entrada)': ('SIM – R$ ' + br(dd.vc.sum())) if len(dd) else None,
                     'Observação': '; '.join(obs)})
    return pd.DataFrame(rows)

# ---------------------------------------------------------------- principal
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--xml', required=True); ap.add_argument('--dominio', required=True)
    ap.add_argument('--sieg-nfe'); ap.add_argument('--sieg-cte'); ap.add_argument('--prisma')
    ap.add_argument('--competencia', required=True); ap.add_argument('--saida', required=True)
    a = ap.parse_args()

    nfe, cte, ev = ler_xmls(a.xml)
    dom = ler_dominio(a.dominio)
    canc = set(ev[ev.tpEvento == '110111'].chave)
    cce = ev[ev.tpEvento == '110110'].chave.value_counts().to_dict()

    proprias = nfe[nfe.emit_cnpj == PRUMO]
    terceiros = nfe[(nfe.emit_cnpj != PRUMO) & (nfe.dest_cnpj == PRUMO)]

    # ---- PRISMA: só a faixa de numeração da série 0 da Prumo (a planilha tem o grupo todo)
    prisma = None; prisma_fora = pd.DataFrame()
    if a.prisma:
        P = ler_prisma(a.prisma)
        s0 = proprias[proprias.serie == '0']
        if len(s0):
            lo, hi = s0.nNF.min() - 20, s0.nNF.max() + 20
            prisma = P[P.danfe.between(lo, hi)]
            mag = len(str(s0.nNF.max()))
            prisma_fora = P[(~P.danfe.between(lo, hi)) & (P.danfe.astype(str).str.len() == mag) &
                            (P.danfe.astype(str).str[0] == str(s0.nNF.max())[0])]

    S0 = sequencia(proprias, '0', canc, cce, dom, prisma)
    S1 = sequencia(proprias, '1', canc, cce, dom, None)

    # ---- ENTRADAS: NF-e terceiros
    sieg_nfe = set()
    if a.sieg_nfe:
        sn = pd.read_excel(a.sieg_nfe, dtype=str)
        sieg_nfe = set(sn['Chave'].dropna())
    d36 = dom[dom.esp == 36].groupby(['nota', 'serie']).agg(cod=('cod', lambda s: ' / '.join(map(str, s))), data=('data', 'first'),
            forn=('forn', 'first'), cfop=('cfop', lambda s: ' / '.join(map(str, s))), ac=('ac', lambda s: ' / '.join(map(str, s))),
            vc=('vc', 'sum'), icms=('icms_proprio', 'sum')).reset_index()
    ent = []
    usados = set()
    for r in terceiros.itertuples():
        m = d36[(d36.nota == str(r.nNF)) & (d36.serie == r.serie)]
        if not len(m):
            m = d36[d36.nota == str(r.nNF)]
        obs = []
        if sieg_nfe and r.chave not in sieg_nfe:
            obs.append('Não consta no relatório do Sieg')
        if r.chave in canc:
            sit = 'ERRO – CANCELADO LANÇADO COM VALOR' if len(m) and m.vc.sum() > 0 else 'CANCELADA'
        elif not len(m):
            sit = 'NÃO LANÇADA NA DOMÍNIO'
        else:
            usados.update(m.index)
            sit = 'NF-e – LANÇADA OK' if abs(r.vNF - m.vc.sum()) <= 0.01 else 'NF-e – VALOR ≠ DOMÍNIO'
            if m.data.iloc[0] != r.dhEmi:
                obs.append(f'Data Domínio {m.data.iloc[0]} x emissão {r.dhEmi}')
        ent.append(dict(Documento='NF-e', Situação=sit, Nota=r.nNF, Série=r.serie, Chave=r.chave, Emissão=r.dhEmi,
                        Data=m.data.iloc[0] if len(m) else None, Emitente=r.emit, UF=r.emit_uf, CFOP_XML=r.cfops,
                        CFOP_Dom=m.cfop.iloc[0] if len(m) else None, Acum=m.ac.iloc[0] if len(m) else None,
                        VXML=r.vNF, VDom=float(m.vc.sum()) if len(m) else None, Obs='; '.join(obs), Cod=m.cod.iloc[0] if len(m) else None,
                        _icms_xml=r.vICMS, _icms_dom=float(m.icms.sum()) if len(m) else None))
    for r in proprias.itertuples():
        m = d36[(d36.nota == str(r.nNF)) & (d36.serie == r.serie)]
        if not len(m):
            continue
        usados.update(m.index)
        if r.inutilizada:
            sit = 'ERRO – INUTILIZADA LANÇADA NA DOMÍNIO' if m.vc.sum() > 0 else 'INUTILIZADA'
        elif r.chave in canc:
            sit = 'ERRO – CANCELADO LANÇADO COM VALOR' if m.vc.sum() > 0 else 'CANCELADA – LANÇADA COM VALOR ZERO'
        else:
            sit = 'DEVOLUÇÃO (entrada própria)'
        ent.append(dict(Documento='NF-e própria', Situação=sit, Nota=r.nNF, Série=r.serie, Chave=r.chave, Emissão=r.dhEmi,
                        Data=m.data.iloc[0], Emitente=m.forn.iloc[0], UF=None, CFOP_XML=r.cfops, CFOP_Dom=m.cfop.iloc[0], Acum=m.ac.iloc[0],
                        VXML=r.vNF, VDom=float(m.vc.sum()), Obs=r.infCpl[:150], Cod=m.cod.iloc[0]))
    for i, m in d36[~d36.index.isin(usados)].iterrows():
        prop = m.serie in ('0', '1') and 'PRUMO' not in str(m.forn).upper() and m.nota.isdigit() and \
            any(abs(int(m.nota) - x) < 2000 for x in proprias[proprias.serie == m.serie].nNF)
        ent.append(dict(Documento='NF-e própria' if prop else 'NF-e', Situação='ENTRADA PRÓPRIA – SEM XML' if prop else 'LANÇADA SEM XML/SIEG',
                        Nota=m.nota, Série=m.serie, Chave=None, Emissão=None, Data=m.data, Emitente=m.forn, UF=None, CFOP_XML=None,
                        CFOP_Dom=m.cfop, Acum=m.ac, VXML=None, VDom=m.vc, Obs='XML não está na pasta', Cod=m.cod))

    # ---- CT-e: somente PRUMO tomadora
    cte_info = ''
    d38 = dom[dom.esp == 38]
    if a.sieg_cte:
        rc = pd.read_excel(a.sieg_cte, dtype=str); rc = rc[rc.Chave.fillna('').str.len() == 44].copy()
        rc['tom'] = (rc.CNPJ_CPF_Tomador == PRUMO) | (rc.CNPJ_CPF_Outro_Tomador == PRUMO)
        rc['canc'] = rc.Status.str.contains('Cancel', na=False) | rc.Chave.isin(canc)
        rc['k'] = rc.Numero.str.lstrip('0'); rc['s'] = rc.Serie.astype(str).str.replace(r'\.0$', '', regex=True)
        rc['v'] = pd.to_numeric(rc.Valor_Transporte, errors='coerce')
        base = rc[rc.tom]
        cte_info = f'{len(base)} CT-e no Sieg com a PRUMO tomadora (os demais {len(rc) - len(base)} têm outro tomador e foram desconsiderados)'
    else:
        base = pd.DataFrame()
        if len(cte):
            c2 = cte[cte.tomador_cnpj == PRUMO]
            base = pd.DataFrame(dict(Chave=c2.chave, k=c2.nCT.str.lstrip('0'), s=c2.serie, Rz_Emit=c2.emit, Dt_Emissao=c2.dhEmi,
                                     v=c2.vTPrest, canc=c2.chave.isin(canc), CFOP=None, Uf_Inicio=None))
        cte_info = f'{len(base)} XML de CT-e com a PRUMO tomadora (sem relatório do Sieg)'
    usados38 = set()
    for r in base.itertuples():
        m = d38[(d38.nota == r.k) & (d38.serie == r.s)]
        usados38.update(m.index)
        if r.canc:
            sit = 'ERRO – CANCELADO LANÇADO COM VALOR' if len(m) and m.vc.sum() > 0 else 'CANCELADA'
        elif not len(m):
            sit = 'NÃO LANÇADA NA DOMÍNIO'
        else:
            sit = 'CT-e – LANÇADO OK' if abs(r.v - m.vc.sum()) <= 0.01 else 'NF-e – VALOR ≠ DOMÍNIO'
        ent.append(dict(Documento='CT-e', Situação=sit, Nota=r.k, Série=r.s, Chave=r.Chave, Emissão=str(r.Dt_Emissao)[:10],
                        Data=m.data.iloc[0] if len(m) else None, Emitente=r.Rz_Emit, UF=getattr(r, 'Uf_Inicio', None), CFOP_XML=getattr(r, 'CFOP', None),
                        CFOP_Dom=str(m.cfop.iloc[0]) if len(m) else None, Acum=str(m.ac.iloc[0]) if len(m) else None, VXML=r.v,
                        VDom=float(m.vc.sum()) if len(m) else None,
                        Obs=(f'Cancelado; Domínio creditou ICMS de R$ {br(m.icms_proprio.sum())}' if r.canc and len(m) else ''),
                        Cod=str(m.cod.iloc[0]) if len(m) else None))
    for i, m in d38[~d38.index.isin(usados38)].iterrows():
        ent.append(dict(Documento='CT-e', Situação='LANÇADA SEM XML/SIEG', Nota=m.nota, Série=m.serie, Chave=None, Emissão=None, Data=m.data,
                        Emitente=m.forn, UF=m.uf, CFOP_XML=None, CFOP_Dom=str(m.cfop), Acum=str(m.ac), VXML=None, VDom=m.vc,
                        Obs='CT-e lançado e não encontrado no Sieg com a Prumo tomadora', Cod=str(m.cod)))
    for m in dom[~dom.esp.isin([36, 38])].itertuples():
        ent.append(dict(Documento=f'Espécie {m.esp}', Situação='SERVIÇO TOMADO – NÃO CONFERIDO', Nota=m.nota, Série=m.serie, Chave=None,
                        Emissão=None, Data=m.data, Emitente=m.forn, UF=m.uf, CFOP_XML=None, CFOP_Dom=str(m.cfop), Acum=str(m.ac),
                        VXML=None, VDom=m.vc, Obs='', Cod=str(m.cod)))
    EN = pd.DataFrame(ent)
    ordem = {'NF-e': 0, 'NF-e própria': 1, 'CT-e': 2}
    EN = EN.assign(_o=EN.Documento.map(ordem).fillna(3)).sort_values(['_o', 'Data', 'Nota'], key=lambda s: s.astype(str)).drop(columns='_o')
    ICMS = EN[EN.Documento == 'NF-e'][['Nota', 'Emitente', 'CFOP_XML', 'VXML', '_icms_xml', '_icms_dom']].copy() if '_icms_xml' in EN else pd.DataFrame()
    EN = EN.drop(columns=[c for c in EN if c.startswith('_')])
    EN.columns = ['Documento', 'Situação', 'Nota', 'Série', 'Chave de acesso', 'Emissão', 'Data Domínio', 'Emitente / Fornecedor', 'UF',
                  'CFOP XML', 'CFOP Domínio', 'Acum', 'Valor XML/Sieg', 'Valor Domínio', 'Observação', 'Cód Domínio']

    # ---- ICMS (informativo)
    if len(ICMS):
        ICMS['Dif'] = (ICMS._icms_xml - ICMS._icms_dom.fillna(0)).round(2)
        ICMS = ICMS[ICMS.Dif.abs() > 0.01]
        def oi(r):
            cf = set(str(r.CFOP_XML).split())
            if cf <= {'5401', '5403', '5405', '6401', '6403', '6404'}:
                return 'Só CFOP de ST – sem crédito do ICMS próprio (ok)'
            if cf & {'5401', '5403', '5405', '6401', '6403', '5655'}:
                return 'Nota mista (tributada + ST) – crédito só da parte tributada (conferir itens)'
            if r._icms_xml == 0:
                return 'XML sem ICMS destacado: se emitente do Simples (CSOSN 101), conferir pCredSN no XML'
            return 'Verificar'
        ICMS['Observação'] = ICMS.apply(oi, axis=1)
        ICMS.columns = ['Nota', 'Emitente', 'CFOP XML', 'Valor', 'ICMS XML', 'ICMS Domínio', 'Diferença', 'Observação']

    # ---- Resumo
    def cnt(df, s):
        return int((df['Situação'] == s).sum()) if len(df) else 0
    def lst(df, s, col='Nota'):
        return ', '.join(map(str, df[df['Situação'] == s][col])) if len(df) else ''
    def val(df, s, col):
        return br(pd.to_numeric(df[df['Situação'] == s][col], errors='coerce').sum())
    R = [('SAÍDAS SÉRIE 0 (sistema próprio)', '', ''),
         ('Faixa analisada', f'{S0.Nota.min()} a {S0.Nota.max()}' if len(S0) else '-', ''),
         ('Autorizadas e conferidas', cnt(S0, 'AUTORIZADA') + cnt(S0, 'AUTORIZADA – REMESSA/RETORNO'), ''),
         ('Canceladas', cnt(S0, 'CANCELADA'), lst(S0, 'CANCELADA')),
         ('Inutilizadas', cnt(S0, 'INUTILIZADA'), lst(S0, 'INUTILIZADA')),
         ('Devoluções / entradas próprias', cnt(S0, 'DEVOLUÇÃO (entrada própria)'), ''),
         ('ERRO: inutilizadas lançadas na Domínio', cnt(S0, 'ERRO – INUTILIZADA LANÇADA NA DOMÍNIO'), lst(S0, 'ERRO – INUTILIZADA LANÇADA NA DOMÍNIO')),
         ('Não localizadas (quebra de sequência)', cnt(S0, 'NÃO LOCALIZADA'), lst(S0, 'NÃO LOCALIZADA')),
         ('Fora da PRISMA', cnt(S0, 'AUTORIZADA – FORA DA PRISMA'), lst(S0, 'AUTORIZADA – FORA DA PRISMA')),
         ('Valor diferente da PRISMA', cnt(S0, 'AUTORIZADA – VALOR ≠ PRISMA'), lst(S0, 'AUTORIZADA – VALOR ≠ PRISMA')),
         ('Linhas da PRISMA fora da faixa da Prumo', len(prisma_fora), '; '.join(f'{r.danfe} {r.cliente} R$ {br(float(r.valor or 0))}' for r in prisma_fora.itertuples())),
         ('', '', ''),
         ('SAÍDAS SÉRIE 1 (Mercado Livre)', '', ''),
         ('Faixa analisada', f'{S1.Nota.min()} a {S1.Nota.max()}' if len(S1) else '-', ''),
         ('Autorizadas', cnt(S1, 'AUTORIZADA'), ''),
         ('Canceladas', cnt(S1, 'CANCELADA'), lst(S1, 'CANCELADA')),
         ('Entradas próprias sem XML', cnt(S1, 'ENTRADA PRÓPRIA – SEM XML'), lst(S1, 'ENTRADA PRÓPRIA – SEM XML')),
         ('Não localizadas (quebra de sequência)', cnt(S1, 'NÃO LOCALIZADA'), lst(S1, 'NÃO LOCALIZADA')),
         ('', '', ''),
         ('ENTRADAS (NF-e + próprias + CT-e só PRUMO tomadora)', '', ''),
         ('NF-e de fornecedores no XML', int((EN.Documento == 'NF-e').sum()), f'{len(sieg_nfe)} chaves no Sieg' if sieg_nfe else 'sem relatório do Sieg'),
         ('NF-e lançadas OK', cnt(EN, 'NF-e – LANÇADA OK'), ''),
         ('NÃO lançadas na Domínio', cnt(EN, 'NÃO LANÇADA NA DOMÍNIO'), lst(EN, 'NÃO LANÇADA NA DOMÍNIO')),
         ('Lançadas sem XML/Sieg', cnt(EN, 'LANÇADA SEM XML/SIEG'), lst(EN, 'LANÇADA SEM XML/SIEG')),
         ('CT-e', cte_info, ''),
         ('CT-e lançados OK', cnt(EN, 'CT-e – LANÇADO OK'), ''),
         ('ERRO: cancelados lançados com valor', cnt(EN, 'ERRO – CANCELADO LANÇADO COM VALOR'),
          lst(EN, 'ERRO – CANCELADO LANÇADO COM VALOR') + f' – R$ {val(EN, "ERRO – CANCELADO LANÇADO COM VALOR", "Valor Domínio")}'),
         ('ERRO: inutilizadas lançadas', cnt(EN, 'ERRO – INUTILIZADA LANÇADA NA DOMÍNIO'),
          lst(EN, 'ERRO – INUTILIZADA LANÇADA NA DOMÍNIO') + f' – R$ {val(EN, "ERRO – INUTILIZADA LANÇADA NA DOMÍNIO", "Valor Domínio")}'),
         ('Total das entradas na planilha x Domínio', br(pd.to_numeric(EN['Valor Domínio'], errors='coerce').sum()), f'Domínio: R$ {br(dom.vc.sum())}')]
    R = pd.DataFrame(R, columns=['Item', 'Quantidade / Valor', 'Observação'])

    wb = Workbook(); wb.remove(wb.active)
    ws = aba_simples(wb, 'Resumo', R, {'Item': 55, 'Quantidade / Valor': 22, 'Observação': 110})
    ws.insert_rows(1, 2); ws['A1'] = f'PRUMO COMERCIAL LTDA (272) – CNPJ 41.751.764/0001-04 – Conferência de notas {a.competencia}'; ws['A1'].font = Font(bold=True, size=12)
    for row in ws.iter_rows(min_row=4):
        t = str(row[0].value or '')
        if t.isupper() and t:
            for c in row: c.fill = GRY; c.font = Font(bold=True)
        if t.startswith(('ERRO', 'NÃO', 'Não localizadas')) and row[1].value not in (0, '0'):
            for c in row: c.fill = PatternFill('solid', fgColor='FF7C80')
        row[2].alignment = Alignment(wrap_text=True, vertical='top')
    if len(S0):
        aba_colorida(wb, 'SAÍDAS Série 0', S0, f'SAÍDAS SÉRIE 0 – notas {S0.Nota.min()} a {S0.Nota.max()} – XML x PRISMA x Domínio')
    if len(S1):
        aba_colorida(wb, 'SAÍDAS Série 1 (ML)', S1.drop(columns=[c for c in S1 if c.startswith('PRISMA')], errors='ignore'),
                     f'SAÍDAS SÉRIE 1 – Mercado Livre – notas {S1.Nota.min()} a {S1.Nota.max()} – XML x Domínio')
    aba_colorida(wb, 'ENTRADAS', EN, 'ENTRADAS – NF-e de fornecedores + notas próprias de entrada + CT-e (somente PRUMO tomadora) – XML / Sieg x Domínio')
    if len(ICMS):
        aba_simples(wb, 'ICMS XML x Domínio', ICMS, {'Emitente': 40, 'Observação': 75})
    aba_simples(wb, 'Domínio Entradas (base)', dom.drop(columns=['icms_proprio']), {'forn': 40})
    wb.save(a.saida)
    print(R.to_string())

if __name__ == '__main__':
    main()
