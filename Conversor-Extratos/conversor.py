#!/usr/bin/env python3
"""ROF - Conversor de extratos bancarios (PDF / OFX / CSV / XLSX) -> <nome>_extrato.md enxuto.

Tudo roda no computador: nada e enviado para internet. O OCR e o do proprio Windows
(ocr_windows.ps1: Windows.Data.Pdf + Windows.Media.Ocr). O original nunca e alterado.

Uso:
  python conversor.py                 varre a pasta de entrada (config.json) e converte o que falta
  python conversor.py arq1.pdf ...    converte esses arquivos agora (se o .md existir, grava "(2)")
  opcoes: --oculto (sem mensagens, para a tarefa agendada)  --stats (mostra tempo/tamanhos)
"""
import csv
import datetime as dt
import difflib
import hashlib
import html
import io
import json
import os
import re
import subprocess
import sys
import tempfile
import time
import unicodedata
from collections import Counter
from decimal import Decimal, InvalidOperation
from pathlib import Path

AQUI = Path(__file__).resolve().parent
EXTS = {'.pdf', '.ofx', '.csv', '.xlsx', '.xlsm', '.xls'}
MIN_CHARS_TEXTO = 80          # pagina com menos texto proprio que isso vai para o OCR
LOG = AQUI / 'conversor.log'
ESTADO = AQUI / 'estado.json'  # arquivos que deram erro (nao tenta de novo ate o arquivo mudar)
OCULTO = False


def msg(*a):
    if not OCULTO:
        print(*a, flush=True)


# ----------------------------------------------------------------- utilidades

def sem_acento(s):
    return ''.join(c for c in unicodedata.normalize('NFD', s) if unicodedata.category(c) != 'Mn')


def norm(s):
    return re.sub(r'\s+', ' ', sem_acento(s).lower()).strip()


RE_VALOR = re.compile(r'^\(?([-+])?(?:R\$)?([-+])?((?:\d{1,3}(?:\.\d{3})+|\d+),\d{2})\)?([-+*])?([CD])?$')


def le_valor(tok):
    """'1.500,00' / '45,90-' / '45,90D' / '(45,90)' / '-R$45,90' -> (texto sem sinal, sinal +1/-1/None)."""
    m = RE_VALOR.match(tok)
    if not m:
        return None
    s1, s2, num, s3, cd = m.groups()
    sinal = None
    if '-' in (s1, s2, s3) or cd == 'D' or (tok.startswith('(') and tok.endswith(')')):
        sinal = -1
    elif '+' in (s1, s2, s3) or cd == 'C':
        sinal = 1
    return num, sinal


def dec(txt):
    """'1.500,00' / '-45,90' -> Decimal (so para somar e conferir; o texto original e o que sai)."""
    try:
        return Decimal(txt.replace('.', '').replace(',', '.'))
    except (InvalidOperation, AttributeError):
        return None


def fmt(d):
    s = f'{abs(d):,.2f}'.replace(',', '#').replace('.', ',').replace('#', '.')
    return ('-' if d < 0 else '') + s


def com_sinal(num, sinal):
    return ('-' if sinal == -1 else '') + num


MESES = {m: i + 1 for i, m in enumerate('jan fev mar abr mai jun jul ago set out nov dez'.split())}


def data_dmy(s):
    """'03/10/2026' -> date (aceita dd/mm/aa)."""
    m = re.match(r'^(\d{2})[/.-](\d{2})[/.-](\d{2}|\d{4})$', s)
    if not m:
        return None
    d, mo, a = int(m[1]), int(m[2]), int(m[3])
    a += 2000 if a < 100 else 0
    try:
        return dt.date(a, mo, d)
    except ValueError:
        return None


def ler_texto_bytes(b):
    """Decodifica OFX/CSV: UTF-8 se for valido, senao Windows-1252 (charset de muitos bancos)."""
    if b.startswith(b'\xef\xbb\xbf'):
        t = b[3:].decode('utf-8', errors='replace')
    else:
        try:
            t = b.decode('utf-8')
        except UnicodeDecodeError:
            try:
                t = b.decode('cp1252')
            except UnicodeDecodeError:
                t = b.decode('latin-1')
    if re.search('[ÃÂ][\u0080-¿‘-›]', t):   # UTF-8 lido como 1252 pelo banco ("Ã§")
        try:
            t = t.encode('cp1252').decode('utf-8')
        except (UnicodeEncodeError, UnicodeDecodeError):
            pass
    return t


# ----------------------------------------------------------------- linhas e colunas

class Linha:
    __slots__ = ('pag', 'toks', 'ocr', 'y', 'h')

    def __init__(self, pag, toks, ocr=False, y=0.0, h=0.01):
        # toks: [(texto, x0, x1)] com x de 0 a 1; y = centro da linha e h = altura, de 0 a 1 na pagina
        self.pag, self.toks, self.ocr, self.y, self.h = pag, toks, ocr, y, h

    @property
    def texto(self):
        return ' '.join(t for t, _, _ in self.toks)


def agrupa_linhas(palavras, largura, altura):
    """[(x0,y0,x1,y1,texto)] -> [(toks, y, h)], agrupando as palavras pela altura na pagina."""
    pal = sorted(palavras, key=lambda w: ((w[1] + w[3]) / 2, w[0]))
    linhas = []
    for x0, y0, x1, y1, t in pal:
        c, h = (y0 + y1) / 2, max(y1 - y0, 1)
        if linhas and abs(c - linhas[-1]['c']) <= 0.5 * min(h, linhas[-1]['h']):
            ln = linhas[-1]
            ln['w'].append((t, x0 / largura, x1 / largura))
            ln['c'] = (ln['c'] * (len(ln['w']) - 1) + c) / len(ln['w'])
        else:
            linhas.append({'c': c, 'h': h, 'w': [(t, x0 / largura, x1 / largura)]})
    return [(sorted(ln['w'], key=lambda w: w[1]), ln['c'] / altura, ln['h'] / altura) for ln in linhas]


COLS = {
    'data': {'data', 'dt', 'date'},
    'hist': {'historico', 'descricao', 'lancamento', 'lancamentos', 'detalhe', 'detalhes', 'movimentacao'},
    'doc': {'documento', 'doc', 'doc.', 'docto', 'docto.', 'nº', 'n.doc', 'ndoc', 'numero', 'ref', 'ref.', 'id'},
    'cred': {'credito', 'creditos', 'entrada', 'entradas', 'deposito', 'depositos', '(+)'},
    'deb': {'debito', 'debitos', 'saida', 'saidas', 'retirada', 'retiradas', '(-)'},
    'valor': {'valor', 'valores', 'valor(r$)', 'montante'},
    'saldo': {'saldo', 'saldo(r$)'},
}


def cabecalho_colunas(ln):
    """Linha 'Data Historico Docto Credito Debito Saldo' -> {coluna: centro x}; None se nao for."""
    achou, outros, ult, esq, fim_ant = {}, [], None, [], 0.0
    for t, x0, x1 in ln.toks:
        k = norm(t).strip(':')
        if k in ('(r$)', 'r$', '(rs)') and ult:          # 'Valor (R$)': a coluna e o conjunto
            c, a0 = ult
            achou[c] = (a0 + x1) / 2
            continue
        col = next((c for c, nomes in COLS.items() if k in nomes and c not in achou), None)
        if col:
            achou[col], ult = (x0 + x1) / 2, (col, x0)
            esq.append((x0, col))
        elif esq and esq[-1][1].startswith('_') and x0 - fim_ant < 0.02:
            pass                                          # continua a coluna anterior
        else:
            outros.append((x0 + x1) / 2)
            esq.append((x0, f'_{len(outros)}'))
            ult = None
        fim_ant = x1
    if 'data' in achou and ('hist' in achou or 'doc' in achou) and achou.keys() & VCOLS:
        achou['_outros'] = outros
        achou['_esq'] = sorted(esq)
        return achou
    return None


VCOLS = {'valor', 'cred', 'deb', 'saldo'}


def coluna_de(x, cols):
    cands = [(abs(v - x), k) for k, v in cols.items() if not k.startswith('_')] + \
        [(abs(v - x), '_') for v in cols.get('_outros', [])]
    return min(cands)[1] if cands else None


def extrai_valores(toks, cols):
    """Com cabecalho de colunas: pega os valores pela coluna (mesmo no meio da linha, ex.: Stone com
    a contraparte depois do saldo). Sem cabecalho: valores no fim da linha."""
    if not cols or not (cols.keys() & VCOLS):
        return tira_valores(toks)
    vals, texto, i = [], [], 0
    while i < len(toks):
        t, x0, x1 = toks[i]
        v = le_valor(t)
        if v and coluna_de((x0 + x1) / 2, cols) in VCOLS:
            num, sinal = v
            esq = x0
            while texto and texto[-1][0] in ('R$', '-', '+', '-R$', '+R$', 'R$-') and esq - texto[-1][2] < 0.012:
                tk, esq, _ = texto.pop()
                if '-' in tk:
                    sinal = -1
                elif '+' in tk:
                    sinal = 1
            if i + 1 < len(toks) and toks[i + 1][0] in ('C', 'D', '€'):
                sinal = -1 if toks[i + 1][0] == 'D' else 1
                i += 1
            vals.append((num, sinal, (x0 + x1) / 2))
        else:
            texto.append(toks[i])
        i += 1
    if not vals:
        return tira_valores(toks)
    return vals[:3], texto


# ----------------------------------------------------------------- cabecalho/rodape repetido e avisos

RE_PAGINA = re.compile(r'^(p[aá]g(ina|\.)?|folha)\s*:?\s*\d+\s*(de|/)\s*\d+$|^\d+\s*(de|/)\s*\d+$'
                       r'|^p[aá]gina\b.{0,12}$', re.I)
RE_AVISO = re.compile(r'ouvidoria|\bsac\b|0800|deficiente (auditivo|de fala)|fale conosco|central de atendimento'
                      r'|www\.|https?://|@\w+\.com|atendimento (24|ao cliente)|portal de privacidade', re.I)


def chave_rep(txt):
    k = norm(txt)
    return re.sub(r'\d', '#', k) if RE_PAGINA.match(k) or 'pagina' in k or 'emitido em' in k or 'impresso em' in k else k


def repetidas(paginas):
    """Cabecalho/rodape: a mesma linha, NA MESMA ALTURA da pagina, em mais da metade das paginas.
    (So o texto nao basta: "Pagamento com QR Pix" se repete em todas as paginas e e lancamento.)"""
    if len(paginas) < 2:
        return set()
    cont = Counter()
    for linhas in paginas:
        cont.update({(chave_rep(ln.texto), round(ln.y * 40) + d) for ln in linhas for d in (-1, 0, 1)})
    return {k for k, n in cont.items() if n > len(paginas) / 2}


def e_rep(ln, rep):
    return (chave_rep(ln.texto), round(ln.y * 40)) in rep


def e_aviso(txt):
    return bool(RE_PAGINA.match(norm(txt)) or RE_AVISO.search(txt))


# ----------------------------------------------------------------- OCR (Windows)

def pasta_imagens(arq):
    h = hashlib.sha1(str(arq).encode('utf-8')).hexdigest()[:8]
    p = Path(tempfile.gettempdir()) / 'ROF-Extratos-OCR' / f'{Path(arq).stem[:60]}-{h}'
    p.mkdir(parents=True, exist_ok=True)
    return p


def ler_tsv_ocr(p):
    """Formato do ocr_windows.ps1: uma linha por linha do extrato, '#y h' e as palavras separadas por TAB,
    cada palavra 'x0 x1 texto' (tudo de 0 a 1 na pagina)."""
    linhas = []
    for i, row in enumerate(p.read_text(encoding='utf-8-sig').splitlines()):
        toks, y, h = [], i * 0.012, 0.01
        for w in row.split('\t'):
            if w.startswith('#'):
                y, h = (float(v) for v in w[1:].split())
                continue
            partes = w.split(' ', 2)
            if len(partes) == 3:
                toks.append((partes[2], float(partes[0]), float(partes[1])))
        if toks:
            linhas.append((toks, y, h))
    return linhas


def ocr_paginas(arq, pags, pasta):
    """OCR das paginas (1 = primeira). Devolve ({pag: [linhas]}, erro)."""
    if os.environ.get('ROF_OCR_TESTE') == 'tesseract':   # so para testar fora do Windows
        return _ocr_tesseract(arq, pags, pasta), None
    if os.name != 'nt':
        return {}, 'OCR do Windows indisponivel neste computador'
    cmd = ['powershell.exe', '-NoProfile', '-NonInteractive', '-ExecutionPolicy', 'Bypass',
           '-File', str(AQUI / 'ocr_windows.ps1'), '-Pdf', str(arq),
           '-Paginas', ','.join(map(str, pags)), '-Saida', str(pasta)]
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8', errors='replace',
                           timeout=120 + 60 * len(pags), creationflags=0x08000000)
    except Exception as e:  # noqa: BLE001
        return {}, f'OCR falhou: {e}'
    res = {p: ler_tsv_ocr(pasta / f'p{p}.tsv') for p in pags if (pasta / f'p{p}.tsv').exists()}
    erro = None if r.returncode == 0 else ('OCR: ' + (r.stderr or r.stdout).strip().splitlines()[-1][:200]
                                           if (r.stderr or r.stdout).strip() else f'OCR saiu com codigo {r.returncode}')
    return res, erro


def _ocr_tesseract(arq, pags, pasta):
    import pymupdf
    res = {}
    with pymupdf.open(arq) as doc:
        for p in pags:
            png = pasta / f'p{p}.png'
            doc[p - 1].get_pixmap(dpi=200).save(png)
            out = subprocess.run(['tesseract', str(png), '-', '-l', 'por', 'tsv'], capture_output=True, text=True).stdout
            pal, larg, alt = [], 1, 1
            for row in out.splitlines()[1:]:
                c = row.split('\t')
                if len(c) == 12 and c[0] == '1':
                    larg, alt = int(c[8]), int(c[9])
                if len(c) == 12 and c[0] == '5' and c[11].strip():
                    x, y, w, h = map(int, c[6:10])
                    pal.append((x, y, x + w, y + h, c[11].strip()))
            res[p] = agrupa_linhas(pal, larg, alt)
    return res


# ----------------------------------------------------------------- PDF

def ler_pdf(arq):
    try:
        import pymupdf
    except ImportError:
        import fitz as pymupdf
    doc = pymupdf.open(arq)
    if doc.needs_pass and not doc.authenticate(''):
        raise RuntimeError('PDF protegido por senha')
    paginas, cru = [], 0
    for i, pg in enumerate(doc, 1):
        pal = [w[:5] for w in pg.get_text('words')]
        cru += len(pg.get_text())
        paginas.append([Linha(i, toks, y=y, h=h) for toks, y, h in agrupa_linhas(pal, pg.rect.width or 1, pg.rect.height or 1)])
    n = len(doc)
    doc.close()
    rep = repetidas(paginas)
    escaneadas = []
    for i, linhas in enumerate(paginas, 1):
        proprio = ''.join(ln.texto for ln in linhas if not e_rep(ln, rep) and not e_aviso(ln.texto))
        bons = sum(1 for c in proprio if c.isalnum() or c in ',.-/')
        if bons < MIN_CHARS_TEXTO:     # escaneada: decide pelo texto, nunca pelo numero de imagens
            escaneadas.append(i)
    info = {'paginas': n, 'ocr': escaneadas, 'erro_ocr': None, 'imagens': None, 'sem_texto': []}
    if escaneadas:
        pasta = pasta_imagens(arq)
        info['imagens'] = str(pasta)
        res, info['erro_ocr'] = ocr_paginas(arq, escaneadas, pasta)
        for p in escaneadas:
            base = [ln.texto for ln in paginas[p - 1]]
            novas = []
            for toks, y, h in res.get(p, []):
                ln = Linha(p, arruma_ocr(toks), ocr=True, y=y, h=h)
                cru += len(ln.texto) + 1
                if not repete(ln, base, rep):
                    novas.append(ln)
            if novas:   # camada de texto sem mapa de fonte vira lixo ("?@ABC8@D"): fica so o OCR
                paginas[p - 1] = [ln for ln in paginas[p - 1] if not lixo(ln.texto)] + novas
            else:
                info['sem_texto'].append(p)
        rep = repetidas(paginas)       # de novo, agora com o cabecalho lido pelo OCR
    return paginas, rep, info, cru


def arruma_ocr(toks):
    """Numeros que o OCR quebra ou le torto: '1.' '500,00' / '1 500,00' / '1.500, 00' / '1.500.00' / 'l.5OO,00'."""
    def limpa(t):
        if sum(c.isdigit() for c in t) >= 2 and re.fullmatch(r'[-+(R$]*[\dOoIl|SB.,]+[)CD-]?', t):
            t = t.translate(str.maketrans({'O': '0', 'o': '0', 'I': '1', 'l': '1', '|': '1', 'S': '5', 'B': '8'}))
        return t

    def decimal_br(t):
        m = re.fullmatch(r'([-+(]?(?:R\$)?-?)([\d.,]+?)([.,])(\d{2})(\)?[CD-]?)', t)
        if not m or not re.fullmatch(r'\d{1,3}([.,]?\d{3})*|\d+', m[2]):
            return t
        inteiro = re.sub(r'[.,]', '', m[2])
        milhar = f'{int(inteiro):,}'.replace(',', '.') if m[2] != inteiro else inteiro
        return f'{m[1]}{milhar},{m[4]}{m[5]}'

    out = []
    for t, x0, x1 in toks:
        t = limpa(t)
        if out:
            a, ax0, ax1 = out[-1]
            junto = None
            if re.fullmatch(r'-?(R\$)?-?\d{1,3}[.,]?', a) and (a[-1] in '.,' or x0 - ax1 < 0.012) and re.fullmatch(r'[.,]?\d{3}([.,]\d{3})*[.,]\s?\d{2}[CD-]?', t):
                junto = a.rstrip('.,') + '.' + t.lstrip('.,')                # '1.' + '500,00'
            elif re.fullmatch(r'-?(R\$)?-?[\d.]*\d[.,]', a) and re.fullmatch(r'\d{2}[CD-]?', t):
                junto = a[:-1] + ',' + t                                       # '1.500,' + '00'
            data_re = r'\d{2}/\d{2}(/\d{2}|/\d{4})?'
            if not junto and len(out) == 1 and re.fullmatch(r'[\d/]+', a) and re.fullmatch(r'[\d/]+', t) \
                    and re.fullmatch(data_re, a + t) and not re.fullmatch(data_re, t):
                junto = a + t                                    # data no inicio da linha: '1' + '3/10/2026'
            if junto and x0 - ax1 < 0.03:
                out[-1] = (junto, ax0, x1)
                continue
        out.append((t, x0, x1))
    return [(decimal_br(t) if re.search(r'\d[.,]\d{2}\)?[CD-]?$', t) else t, x0, x1) for t, x0, x1 in out]


def lixo(txt):
    t = txt.replace(' ', '')
    return not t or sum(c in '!"#$%&\'()*+;<=>?@[\\]^_`{|}~' for c in t) / len(t) > 0.15


def repete(ln, base, rep):
    """Linha do OCR que so rele o cabecalho/rodape (ou o texto que a pagina ja tinha)."""
    k = chave_rep(ln.texto)
    if e_rep(ln, rep):
        return True
    outros = [chave_rep(b) for b in base]
    if ln.y < 0.15 or ln.y > 0.85:          # topo/rodape: compara tambem com o cabecalho das outras paginas
        outros += [t for t, _ in rep]
    for kb in outros:
        if abs(len(kb) - len(k)) <= max(3, len(k) // 5) and difflib.SequenceMatcher(None, k, kb).ratio() >= 0.85:
            return True
    return False


# ----------------------------------------------------------------- montar a tabela a partir das linhas

RE_SALDO = re.compile(r'^(saldo|s a l d o)\b')
RE_TOTAL = re.compile(r'^(total|subtotal|soma|resumo)\b')


def tira_data(toks, ano_padrao):
    """Data no inicio da linha -> (dd/mm/aaaa, resto dos tokens)."""
    if not toks:
        return None, toks
    t0 = toks[0][0]
    m = re.match(r'^(\d{2})[/.-](\d{2})(?:[/.-](\d{2}|\d{4}))?$', t0)
    m2 = re.match(r'^(\d{2})/([A-Za-z]{3})(?:/(\d{2}|\d{4}))?$', t0)
    usados = 1
    if m:
        d, mo, a = m[1], int(m[2]), m[3]
    elif m2 and norm(m2[2]) in MESES:
        d, mo, a = m2[1], MESES[norm(m2[2])], m2[3]
    elif re.match(r'^\d{1,2}$', t0) and len(toks) > 3 and norm(toks[1][0]) == 'de' and norm(toks[2][0]) in MESES_EXT \
            and norm(toks[3][0]) == 'de' and len(toks) > 4 and re.match(r'^\d{4}$', toks[4][0]):
        d, mo, a, usados = f'{int(t0):02d}', MESES_EXT[norm(toks[2][0])], toks[4][0], 5
    elif re.match(r'^\d{2}$', t0) and len(toks) > 1 and norm(toks[1][0]).strip('.') in MESES:
        d, mo, a = t0, MESES[norm(toks[1][0]).strip('.')], None
        usados = 2
        if len(toks) > 2 and re.match(r'^\d{4}$', toks[2][0]):
            a, usados = toks[2][0], 3
    else:
        return None, toks
    if not (1 <= int(d) <= 31 and 1 <= mo <= 12):
        return None, toks
    if a is None:
        a = ano_padrao(mo) if ano_padrao else None
    elif len(a) == 2:
        a = '20' + a
    data = f'{d}/{mo:02d}' + (f'/{a}' if a else '')
    resto = toks[usados:]
    if resto and re.match(r'^\d{2}[/.-]\d{2}([/.-]\d{2,4})?$', resto[0][0]) and resto[0][0][:5] == data[:5]:
        resto = resto[1:]          # segunda data igual (data do movimento/contabil)
    return data, resto


def tira_valores(toks):
    """Valores no fim da linha -> ([(num, sinal, centro_x)], resto). Aceita 'R$', '-', 'C'/'D' soltos."""
    vals, i = [], len(toks)
    while i > 0 and len(vals) < 3:
        j, suf = i, None
        if j >= 2 and toks[j - 1][0] in ('C', 'D', '-', '+', '*', '€') and \
                (toks[j - 1][0] not in '-+' or toks[j - 1][1] - toks[j - 2][2] < 0.012):  # OCR le 'C' como '€'
            suf, j = toks[j - 1][0].replace('€', 'C'), j - 1
        v = le_valor(toks[j - 1][0])
        if not v:
            break
        num, sinal = v
        if suf in ('D', '-'):
            sinal = -1
        elif suf in ('C', '+'):
            sinal = 1
        x = (toks[j - 1][1] + toks[j - 1][2]) / 2
        j -= 1
        for _ in range(2):              # '- R$ 45,90' / 'R$ 45,90' / '- 45,90'
            if j >= 1 and toks[j - 1][0] == 'R$':
                j -= 1
            elif j >= 1 and toks[j - 1][0] in ('-', '+', '-R$', '+R$') and toks[j][1] - toks[j - 1][2] < 0.012:
                sinal = -1 if '-' in toks[j - 1][0] else 1
                j -= 1
        vals.insert(0, (num, sinal, x))
        i = j
    return vals, toks[:i]


def separa_doc(resto, cols):
    if len(resto) < 2:
        return resto, ''
    t, x0, x1 = resto[-1]
    if not re.match(r'^\d[\d./-]{2,}$', t) or le_valor(t) or re.match(r'^\d{2}/\d{2}(/\d{2,4})?$', t):
        return resto, ''
    if cols and 'doc' in cols and 'hist' in cols:
        c = (x0 + x1) / 2
        if abs(c - cols['doc']) > abs(c - cols['hist']):
            return resto, ''
    return resto[:-1], t


def atribui_valores(vals, cols):
    """-> (valor, sinal, saldo) usando as colunas do cabecalho quando houver."""
    if cols:
        alvo = {k: cols[k] for k in ('valor', 'cred', 'deb', 'saldo') if k in cols}
        if alvo:
            pos = {}
            for num, sinal, x in vals:
                k = min(alvo, key=lambda c: abs(alvo[c] - x))
                if k in pos:
                    pos = None
                    break
                pos[k] = (num, sinal)
            if pos:
                saldo = pos.get('saldo')
                saldo_txt = com_sinal(*saldo) if saldo else None
                mov = [(k, v) for k, v in pos.items() if k != 'saldo']
                if len(mov) == 1:
                    k, (num, sinal) = mov[0]
                    if sinal is None and k == 'deb':
                        sinal = -1
                    elif sinal is None and k == 'cred':
                        sinal = 1
                    return num, sinal, saldo_txt
                if not mov and saldo:
                    return None, None, saldo_txt
    if len(vals) == 1:
        return vals[0][0], vals[0][1], None
    if len(vals) == 2:
        return vals[0][0], vals[0][1], com_sinal(vals[1][0], vals[1][1])
    return 'X', None, None          # 3 valores sem cabecalho: nao arrisca


def ano_por_periodo(periodo, ano_comum):
    def f(mes):
        if periodo:
            ini, fim = periodo
            if ini.year != fim.year:
                return str(ini.year if mes >= ini.month else fim.year)
            return str(fim.year)
        return ano_comum
    return f


MESES_EXT = {m: i + 1 for i, m in enumerate('janeiro fevereiro marco abril maio junho julho agosto setembro outubro '
                                                'novembro dezembro'.split())}


def achar_periodo(texto):
    t = sem_acento(texto)
    m = re.search(r'(\d{1,2}) de ([a-z]+) de (\d{4})\s*(?:a|ate|-)\s*(\d{1,2}) de ([a-z]+) de (\d{4})', t, re.I)
    if m and m[2].lower() in MESES_EXT and m[5].lower() in MESES_EXT:
        try:
            return (dt.date(int(m[3]), MESES_EXT[m[2].lower()], int(m[1])),
                    dt.date(int(m[6]), MESES_EXT[m[5].lower()], int(m[4])))
        except ValueError:
            pass
    for m in re.finditer(r'(\d{2}[/-]\d{2}[/-]\d{4})\s*(?:a|à|al|ate|até|e|-|–)\s*(\d{2}[/-]\d{2}[/-]\d{4})', texto, re.I):
        a, b = data_dmy(m[1].replace('-', '/')), data_dmy(m[2].replace('-', '/'))
        if a and b and a <= b:
            return a, b
    return None


BANCOS = [  # (codigo, nome, padrao no texto)
    ('001', 'Banco do Brasil', r'banco do brasil'), ('033', 'Santander', r'santander'),
    ('104', 'Caixa', r'caixa econ[oô]mica|\bcaixa\b'), ('237', 'Bradesco', r'bradesco'),
    ('341', 'Itaú', r'ita[uú]'), ('748', 'Sicredi', r'sicredi'), ('756', 'Sicoob', r'sicoob'),
    ('260', 'Nubank', r'nu ?pagamentos|nubank|nu financeira'), ('077', 'Inter', r'banco inter\b|\binter\b'),
    ('336', 'C6 Bank', r'\bc6\b'), ('323', 'Mercado Pago', r'mercado ?pago'), ('133', 'Cresol', r'cresol'),
    ('085', 'Ailos/Viacredi', r'viacredi|ailos'), ('364', 'Efí', r'\befi\b|ef[ií] s\.?a|gerencianet'),
    ('208', 'BTG Pactual', r'btg'), ('290', 'PagBank', r'pagbank|pagseguro'), ('197', 'Stone', r'\bstone\b'),
    ('403', 'Cora', r'\bcora\b'), ('041', 'Banrisul', r'banrisul'), ('422', 'Safra', r'safra'),
    ('633', 'Rendimento', r'banco rendimento'), ('136', 'Unicred', r'unicred'), ('380', 'PicPay', r'picpay'),
    ('461', 'Asaas', r'asaas'), ('212', 'Original', r'banco original'), ('655', 'Neon/Votorantim', r'\bneon\b'),
]
NOME_BANCO = {c: n for c, n, _ in BANCOS}


def acha_banco(t):
    achados = [(m.start(), f'{n} ({c})') for c, n, p in BANCOS for m in [re.search(p, t, re.I)] if m]
    return min(achados)[1] if achados else None


def dados_conta(texto, topo=''):
    """topo = cabecalho/rodape repetido + inicio da 1a pagina: o banco do extrato aparece ali; no corpo
    aparecem os bancos das contrapartes (Pix para Itau, Mercado Pago...)."""
    t = texto[:6000]
    banco = acha_banco(topo) or acha_banco(t) or '?'
    ag = re.search(r'ag(?:[eê]ncia|\.)?\s*(?:n[ºo°.]*)?\s*[:\-]?\s*(\d{3,5}(?:-[\dxX])?)\b', t, re.I)
    conta = re.search(r'conta(?:\s*corrente|\s*pagamento|\s*poupan[cç]a)?\s*(?:n[ºo°.]*)?\s*[:\-]?\s*([\d.]{3,15}-?[\dxX]?)\b', t, re.I)
    tit = re.search(r'(?:titular|cliente|nome|correntista|associado)\s*[:\-]\s*([^\n|]{3,70})', t, re.I)
    return {'banco': banco, 'ag': ag[1] if ag else '?', 'conta': conta[1] if conta else '?',
            'titular': re.split(r'\s{2,}|\s(?:cpf|cnpj|ag[eê]ncia|conta)\b', tit[1].strip(), flags=re.I)[0] if tit else ''}


def coluna_texto(x0, cols):
    """Coluna de uma palavra de texto pela borda esquerda dos titulos do cabecalho."""
    esq = cols.get('_esq', []) if cols else []
    nome = esq[0][1] if esq else ''
    for xe, c in esq:
        if x0 >= xe - 0.01:
            nome = c
    return nome


def montar_tabela(paginas, rep, texto_todo):
    """Linhas do PDF -> (lancamentos, fora_da_tabela, saldo_ini, saldo_fin, linhas_com_valor, periodo).
    Cada linha com valor e um lancamento; as linhas de texto sem valor vao para o lancamento mais proximo
    na pagina (acima ou abaixo), assim funciona com historico em 2 ou 3 linhas antes ou depois do valor."""
    periodo = achar_periodo(texto_todo)
    anos = Counter(re.findall(r'\b\d{2}/\d{2}/(\d{4})\b', texto_todo))
    ano_f = ano_por_periodo(periodo, anos.most_common(1)[0][0] if anos else None)
    fora, vistos_rep, itens, cols, topo_pag = [], set(), [], None, {}
    for ln in (ln for linhas in paginas for ln in linhas):
        k = chave_rep(ln.texto)
        c = cabecalho_colunas(ln)
        if c:
            cols = c
            topo_pag[ln.pag] = ln.y
            continue
        data, resto = tira_data(ln.toks, ano_f)
        vals, resto = extrai_valores(resto, cols)
        if e_rep(ln, rep) or (e_aviso(ln.texto) and not vals):
            if e_rep(ln, rep) and k not in vistos_rep and not e_aviso(ln.texto):
                vistos_rep.add(k)
                fora.append(ln)         # cabecalho repetido: guarda so a primeira vez
            continue
        txt = ' '.join(t for t, _, _ in resto).strip(' -|')
        if vals:
            itens.append({'k': 'V', 'ln': ln, 'data': data, 'vals': vals, 'resto': resto, 'cols': cols, 'anexo': []})
        elif data and not txt:
            itens.append({'k': 'D', 'data': data})
        elif txt and any(ch.isalnum() for ch in txt):
            itens.append({'k': 'T', 'ln': ln, 'data': data, 'resto': resto})
    # linhas de texto -> lancamento mais proximo na mesma pagina
    vs = [i for i, it in enumerate(itens) if it['k'] == 'V']
    gaps = {}
    for a, b in zip(vs, vs[1:]):
        la, lb = itens[a]['ln'], itens[b]['ln']
        if la.pag == lb.pag and lb.y > la.y:
            gaps.setdefault(la.pag, []).append(lb.y - la.y)
    for i, it in enumerate(itens):
        if it['k'] != 'T':
            continue
        ln, melhor = it['ln'], None
        g = sorted(gaps.get(ln.pag, [0]))
        limite = max(2.2 * ln.h, 0.75 * g[len(g) // 2])
        if ln.pag in topo_pag and ln.y < topo_pag[ln.pag]:
            fora.append(ln)             # acima do cabecalho das colunas: dados da conta, nao lancamento
            continue
        ant = next((j for j in reversed(vs) if j < i), None)
        prx = next((j for j in vs if j > i), None)
        for j in (ant, prx):
            if j is None or itens[j]['ln'].pag != ln.pag:
                continue
            v = itens[j]['ln']
            d = abs(v.y - ln.y)
            if d <= max(limite, 2.2 * v.h) and (melhor is None or d < melhor[0]):
                melhor = (d, j)
        if melhor:
            itens[melhor[1]]['anexo'].append(it)
        else:
            fora.append(ln)
    rows, saldo_ini, saldo_fin, data_atual, secao = [], None, None, None, None
    for it in itens:
        if it['k'] in 'DT' and it['data']:
            data_atual = it['data']
        if it['k'] == 'D':
            continue
        if it['k'] != 'V':
            continue
        ln, cols = it['ln'], it['cols']
        data = it['data'] or next((a['data'] for a in it['anexo'] if a['data']), None)
        if data:
            data_atual = data
        resto, doc = separa_doc(it['resto'], cols)
        partes = [(tok, ln.y) for tok in resto] + [(tok, a['ln'].y) for a in it['anexo'] for tok in a['resto']]
        if cols and cols.get('_esq'):
            ordem = {c: n for n, (_, c) in enumerate(cols['_esq'])}
            if 'doc' in ordem and not doc:
                docs = [t for (t, x0, _), _ in partes if coluna_texto(x0, cols) == 'doc' and re.match(r'^\d[\d./-]{2,}$', t)]
                if len(docs) == 1:
                    doc = docs[0]
                    partes = [p for p in partes if p[0][0] != doc]
            partes.sort(key=lambda p: (ordem.get(coluna_texto(p[0][1], cols), 0), p[1], p[0][1]))
            grupos, ult = [], None
            for (t, x0, _), _ in partes:
                c = coluna_texto(x0, cols)
                if c != ult:
                    grupos.append([])
                    ult = c
                grupos[-1].append(t)
            hist = ' / '.join(' '.join(g) for g in grupos)
        else:
            partes.sort(key=lambda p: (p[1], p[0][1]))
            hist = ' '.join(t for (t, _, _), _ in partes)
        hist = re.sub(r'\s+', ' ', hist).strip(' -|/')
        h = norm(hist)
        proprio = ' '.join(t for t, _, _ in resto).strip(' -|/')
        if proprio and (RE_TOTAL.match(norm(proprio)) or RE_SALDO.match(norm(proprio))):
            fora.extend(a['ln'] for a in it['anexo'])     # linha de saldo/total: nao junta texto vizinho
            hist, h = proprio, norm(proprio)
        valor, sinal, saldo = atribui_valores(it['vals'], cols)
        ocr = ln.ocr or any(a['ln'].ocr for a in it['anexo'])
        if RE_TOTAL.match(h):
            if re.search(r'entrada|credito|recebid', h):
                secao = 1
            elif re.search(r'saida|debito|pago|gasto', h):
                secao = -1
            fora.append(ln)
            fora.extend(a['ln'] for a in it['anexo'])
            continue
        if RE_SALDO.match(h):
            v = saldo or (com_sinal(valor, sinal) if valor and valor != 'X' else None)
            if v is None:
                fora.append(ln)
            elif re.search(r'anterior|inicial', h) and saldo_ini is None:
                saldo_ini = v
            elif re.search(r'\bfinal\b|\batual\b', h):
                saldo_fin = v
            elif (data or data_atual) and not re.search(r'invest|poup|aplic|limite|bloq|cdb|fundo|cheque', h):
                rows.append({'data': data or data_atual, 'hist': hist, 'doc': doc, 'valor': None, 'sinal': None,
                             'saldo': v, 'pag': ln.pag, 'ocr': ocr, 'tipo': 's', 'secao': None})
            else:
                fora.append(ln)
            continue
        if valor in ('X', None) or not (data or data_atual) or not hist:
            fora.append(ln)
            fora.extend(a['ln'] for a in it['anexo'])
            continue
        rows.append({'data': data or data_atual, 'hist': hist, 'doc': doc, 'valor': valor, 'sinal': sinal,
                     'saldo': saldo, 'pag': ln.pag, 'ocr': ocr, 'tipo': 't', 'secao': secao})
    return rows, fora, saldo_ini, saldo_fin, len(vs), periodo


def chave_data(s):
    m = re.match(r'(\d{2})/(\d{2})(?:/(\d{4}))?', s or '')
    return (int(m[3] or 0), int(m[2]), int(m[1])) if m else (0, 0, 0)


def completa_sinais(rows, saldo_ini):
    """Sinal que o extrato nao mostra: secao (entradas/saidas) ou diferenca do saldo da linha."""
    t = [r for r in rows if r['tipo'] == 't']
    desc = len(t) >= 2 and chave_data(t[0]['data']) > chave_data(t[-1]['data'])
    crono = list(reversed(rows)) if desc else list(rows)
    ant = dec(saldo_ini) if saldo_ini else None
    for r in crono:
        if r['tipo'] == 't' and r['sinal'] is None:
            if r['secao']:
                r['sinal'] = r['secao']
            elif ant is not None and r['saldo'] and dec(r['saldo']) is not None:
                v, s = dec(r['valor']), dec(r['saldo'])
                if v is None:
                    pass
                elif ant + v == s:
                    r['sinal'] = 1
                elif ant - v == s:
                    r['sinal'] = -1
        if r['saldo'] and dec(r['saldo']) is not None:
            ant = dec(r['saldo'])
        elif ant is not None and r['tipo'] == 't' and r['sinal']:
            ant += r['sinal'] * dec(r['valor'])
    if any(r['sinal'] == -1 for r in t):      # extrato que so marca a saida ("-R$ 120,00"): o resto e entrada
        for r in t:
            if r['sinal'] is None:
                r['sinal'] = 1
    return crono


RE_APLIC_AUT = re.compile(r'^(apl|res)\.? aplic aut')


def ajusta_saldos(rows):
    """Itau com aplicacao automatica: o saldo que fecha e o 'SALDO TOTAL DISPONIVEL DIA' (conta + aplicacao);
    'SALDO MOVIMENTACAO CONTA' vira informativo e APL/RES APLIC AUT (conta <-> aplicacao) nao entram no Confere."""
    if not any('total disponivel' in norm(r['hist']) for r in rows if r['tipo'] == 's'):
        return False
    for r in rows:
        h = norm(r['hist'])
        if r['tipo'] == 's' and 'movimentacao conta' in h:
            r['tipo'] = 'i'
        elif r['tipo'] == 't' and RE_APLIC_AUT.match(h):
            r['tipo'] = 'a'
    return True


def reordena_saldo_dia(rows):
    """Inter: o 'Saldo do dia' vem antes dos lancamentos do dia mas e o saldo do FIM do dia -> vai para depois."""
    i = 0
    while i < len(rows):
        r = rows[i]
        if r['tipo'] == 's':
            j = i + 1
            while j < len(rows) and rows[j]['data'] == r['data'] and rows[j]['tipo'] == 't':
                j += 1
            dia = rows[i + 1:j]
            com_saldo = [x for x in dia if x['saldo']]
            if dia and com_saldo and com_saldo[-1]['saldo'] == r['saldo'] and dia[0]['saldo'] != r['saldo']:
                rows[i:j] = dia + [r]
                i = j
                continue
        i += 1
    return rows


def conferir(rows, saldo_ini, saldo_fin, crono=None):
    """-> (creditos, qtd, debitos, qtd, saldo_ini, saldo_fin, texto_confere)."""
    t = [r for r in rows if r['tipo'] == 't']
    cred = sum((dec(r['valor']) for r in t if r['sinal'] == 1), Decimal(0))
    deb = sum((dec(r['valor']) for r in t if r['sinal'] == -1), Decimal(0))
    nc, nd = sum(r['sinal'] == 1 for r in t), sum(r['sinal'] == -1 for r in t)
    sem = sum(r['sinal'] is None for r in t)
    crono = crono or rows
    obs_ini = ''
    if saldo_ini is None:
        prim = next((r for r in crono if r['saldo'] and r['tipo'] in 'st'), None)
        if prim and prim['tipo'] == 't' and prim['sinal']:
            saldo_ini = fmt(dec(prim['saldo']) - prim['sinal'] * dec(prim['valor']))
            obs_ini = ' (calc. pela 1ª linha)'
        elif prim and prim['tipo'] == 's':
            antes = crono[:crono.index(prim)]
            if all(r['tipo'] == 's' or r['sinal'] for r in antes):
                soma = sum((r['sinal'] * dec(r['valor']) for r in antes if r['tipo'] == 't'), Decimal(0))
                saldo_ini = fmt(dec(prim['saldo']) - soma)
                obs_ini = ' (calc. pelo 1º saldo do dia)' if soma else ' (1º saldo)'
    if saldo_fin is None:
        ult = next((r for r in reversed(crono) if r['saldo'] and r['tipo'] in 'st'), None)
        saldo_fin = ult['saldo'] if ult else None
    quebra = None
    if saldo_ini is not None:
        run = dec(saldo_ini)
        for r in crono:
            if r['tipo'] == 't' and r['sinal']:
                run += r['sinal'] * dec(r['valor'])
            if r['tipo'] in 'st' and r['saldo'] and dec(r['saldo']) is not None and run != dec(r['saldo']):
                quebra = quebra or r
                run = dec(r['saldo'])
    if sem:
        conf = f'NÃO ({sem} lançamento(s) sem sinal identificado)'
    elif saldo_ini is None or saldo_fin is None:
        conf = 'n/d (sem saldo ' + ('inicial' if saldo_ini is None else 'final') + ' no extrato)'
    else:
        dif = dec(saldo_ini) + cred - deb - dec(saldo_fin)
        conf = 'sim' if dif == 0 else f'NÃO (diferença de R$ {fmt(dif)})'
    if quebra and not conf.startswith('sim'):
        conf += f'; saldo da linha não fecha em {quebra["data"]} {quebra["hist"][:40]}'
    return cred, nc, deb, nd, (saldo_ini + obs_ini if saldo_ini else None), saldo_fin, conf


# ----------------------------------------------------------------- saida .md

def linha_tabela(r, tem_doc, tem_saldo, tem_ocr):
    hist = r['hist'].replace('|', '/')
    if r['tipo'] == 't' and r['sinal'] is None:
        hist += ' (sinal?)'
    if r['tipo'] == 'a':
        hist += ' (aplic. automática: fora do Confere)'
    campos = [r['data'], hist]
    if tem_doc:
        campos.append(r['doc'])
    campos.append(com_sinal(r['valor'], r['sinal']) if r['valor'] else '')
    if tem_saldo:
        campos.append(r['saldo'] or '')
    s = '|'.join(campos)
    if tem_ocr and r['ocr']:
        s += f'|[OCR p{r["pag"]}]'
    return s


def cabecalho_md(nome, conta, periodo_txt, origem, n_pag, metodo, ocr_txt, saldos, obs):
    agora = dt.datetime.now().strftime('%d/%m/%Y %H:%M')
    tit = f' | Titular: {conta["titular"]}' if conta.get('titular') else ''
    try:
        base = Path(ler_config().get('entrada') or AQUI.parent).resolve().parent
        origem = Path(origem).resolve().relative_to(base)
    except (ValueError, OSError):
        pass
    out = [f'# Extrato - {nome}',
           f'Banco: {conta["banco"]} | Ag: {conta["ag"]} | Conta: {conta["conta"]}{tit} | Período: {periodo_txt}',
           f'Origem: {origem} | {n_pag} | método: {metodo}{ocr_txt} | gerado em {agora}']
    if saldos:
        cred, nc, deb, nd, si, sf, conf = saldos
        out.append(f'Saldo inicial: {si or "?"} | Créditos: {fmt(cred)} ({nc}) | Débitos: -{fmt(deb)} ({nd}) | '
                   f'Saldo final: {sf or "?"} | Confere: {conf}')
    out += [f'Obs: {o}' for o in obs]
    return out


def periodo_texto(periodo, rows):
    if periodo:
        return f'{periodo[0]:%d/%m/%Y} a {periodo[1]:%d/%m/%Y}'
    ds = sorted((r['data'] for r in rows if r['data']), key=chave_data)
    return f'{ds[0]} a {ds[-1]}' if ds else '?'


def tabela_md(rows):
    tem_doc = any(r['doc'] for r in rows)
    tem_saldo = any(r['saldo'] for r in rows)
    tem_ocr = any(r['ocr'] for r in rows)
    todo_ocr = tem_ocr and all(r['ocr'] for r in rows)
    tem_ocr = tem_ocr and not todo_ocr       # tudo por OCR: avisa uma vez em vez de marcar cada linha
    head = 'data|histórico' + ('|doc' if tem_doc else '') + '|valor' + ('|saldo' if tem_saldo else '')
    obs = []
    if not tem_doc:
        obs.append('sem coluna doc (o extrato não traz nº de documento)')
    if not tem_saldo:
        obs.append('sem coluna saldo (o extrato não traz saldo por linha)')
    if todo_ocr:
        obs.append('todas as linhas foram lidas por OCR; conferir na imagem da página se o valor parecer errado')
    if tem_ocr:
        obs.append('[OCR pN] = linha lida por OCR na página N; conferir na imagem se o valor parecer errado')
    return [head] + [linha_tabela(r, tem_doc, tem_saldo, tem_ocr) for r in rows], obs


def texto_por_pagina(paginas, rep, info):
    out, vistos = [], set()
    for i, linhas in enumerate(paginas, 1):
        tag = ' [OCR]' if i in info.get('ocr', []) else ''
        out.append(f'## Página {i}{tag}')
        n = 0
        for ln in linhas:
            k = chave_rep(ln.texto)
            if e_aviso(ln.texto) or (e_rep(ln, rep) and k in vistos):
                continue
            vistos.add(k)
            out.append(ln.texto)
            n += 1
        if i in info.get('sem_texto', []) or n == 0:
            out.append('(OCR sem texto: abrir a imagem da página)' if tag else '(página sem texto)')
    return out


def so_cabecalho(ln, conta, periodo):
    """Linha fora da tabela que so repete banco/agencia/conta/periodo ja escritos no cabecalho do .md."""
    if len(ln.texto) > 100 or tira_valores(ln.toks)[0]:
        return False
    ja = ' '.join([conta['ag'], conta['conta'], conta['titular']] +
                  ([f'{periodo[0]:%d/%m/%Y}', f'{periodo[1]:%d/%m/%Y}'] if periodo else []))
    nums = re.findall(r'\d[\d./-]*\d|\d', ln.texto)
    if nums:
        return all(n in ja for n in nums)
    return bool(re.search(r'extrato|' + re.escape(conta['banco'].split(' (')[0]), ln.texto, re.I)) and conta['banco'] != '?'


def saldo_resumo(texto, rotulo):
    """Valor logo depois do rotulo, na mesma linha (resumo do topo do extrato)."""
    m = re.search(rotulo + r'\s*:?\s*(?:R\$)?\s*(-?)\s*(?:R\$)?\s*((?:\d{1,3}(?:\.\d{3})+|\d+),\d{2})(\s?[CD]\b)?', texto, re.I)
    if not m:
        return None
    neg = m[1] == '-' or (m[3] or '').strip() == 'D'
    return ('-' if neg else '') + m[2]


def converter_pdf(arq):
    paginas, rep, info, cru = ler_pdf(arq)
    texto_todo = '\n'.join(ln.texto for linhas in paginas for ln in linhas)
    topo = '\n'.join([ln.texto for linhas in paginas for ln in linhas if e_rep(ln, rep)] +
                     [ln.texto for ln in (paginas[0][:8] if paginas else [])])
    conta = dados_conta(texto_todo, topo)
    rows, fora, si, sf, com_valor, periodo = montar_tabela(paginas, rep, texto_todo)
    si = saldo_resumo(texto_todo, r'saldo (?:anterior|inicial)') or si
    sf = saldo_resumo(texto_todo, r'saldo final(?: do per[ií]odo)?') or sf
    reordena_saldo_dia(rows)
    aplic = ajusta_saldos(rows)
    fora_per = []
    if periodo:     # ex.: Bradesco com "Ultimos lancamentos" do mes seguinte depois do total
        dentro = lambda r: (lambda d: d is None or periodo[0] <= d <= periodo[1])(data_dmy(r['data']))  # noqa: E731
        fora_per = [r for r in rows if not dentro(r)]
        rows = [r for r in rows if dentro(r)]
    crono = completa_sinais(rows, si)
    n_ocr = len(info['ocr'])
    metodo = 'OCR' if n_ocr == info['paginas'] else ('texto do PDF + OCR' if n_ocr else 'texto do PDF')
    ocr_txt = ''
    if n_ocr:
        ocr_txt = f' | OCR: {n_ocr} pág. (p{",".join(map(str, info["ocr"]))}; imagens: {info["imagens"]})'
    obs = ['aplicação automática: o Confere usa o SALDO TOTAL DISPONÍVEL (conta + aplicação); APL/RES APLIC AUT ficam fora da soma'] if aplic else []
    if info['erro_ocr']:
        obs.append(info['erro_ocr'])
    for p in info['sem_texto']:
        obs.append(f'p{p} [OCR] sem texto: abrir a imagem da página ({Path(info["imagens"]) / f"p{p}.png"})')
    fora_valor = sum(1 for ln in fora if tira_valores(tira_data(ln.toks, None)[1])[0])
    t = [r for r in rows if r['tipo'] == 't']
    seguro = t and fora_valor <= max(3, 0.25 * com_valor)
    n_pag = f'{info["paginas"]} página(s)'
    if not seguro:
        obs.insert(0, 'tabela NÃO montada com segurança (layout não reconhecido): texto limpo por página abaixo')
        cab = cabecalho_md(Path(arq).name, conta, periodo_texto(periodo, rows), arq, n_pag, metodo, ocr_txt, None, obs)
        return cab + [''] + texto_por_pagina(paginas, rep, info), cru, len(t), 'texto por página'
    saldos = conferir(rows, si, sf, crono)
    tab, obs_tab = tabela_md(rows)
    fora = [ln for ln in fora if any(ch.isalnum() for ch in ln.texto) and not so_cabecalho(ln, conta, periodo)]
    if fora_per:
        obs_tab.append(f'{len(fora_per)} lançamento(s) fora do período no fim')
    if fora:
        obs_tab.append(f'{len(fora)} linha(s) fora da tabela no fim')
    cab = cabecalho_md(Path(arq).name, conta, periodo_texto(periodo, rows), arq, n_pag, metodo, ocr_txt, saldos,
                       obs + obs_tab)
    out = cab + [''] + tab
    if fora_per:
        out += ['## Fora do período (não entram no Confere)'] + tabela_md(fora_per)[0][1:]
    if fora:
        out += ['## Fora da tabela'] + [f'p{ln.pag}{" [OCR]" if ln.ocr else ""}|{ln.texto}' for ln in fora]
    return out, cru, len(t), saldos[-1]


# ----------------------------------------------------------------- OFX

def ofx_tag(bloco, tag):
    m = re.search(rf'<{tag}>([^<\r\n]*)', bloco, re.I)
    return html.unescape(m[1]).strip() if m else ''


def ofx_data(s):
    m = re.match(r'(\d{4})(\d{2})(\d{2})', s or '')
    return f'{m[3]}/{m[2]}/{m[1]}' if m else ''


def ofx_valor(s):
    s = s.strip().replace(' ', '')
    if ',' in s and '.' in s:
        s = s.replace('.', '').replace(',', '.') if s.rfind(',') > s.rfind('.') else s.replace(',', '')
    else:
        s = s.replace(',', '.')
    d = Decimal(s)
    if d.as_tuple().exponent > -2:
        d = d.quantize(Decimal('0.01'))   # so completa as casas ("45.9" -> 45,90); nao arredonda
    return d


def converter_ofx(arq):
    bruto = Path(arq).read_bytes()
    txt = ler_texto_bytes(bruto)
    blocos = re.findall(r'<(?:STMTRS|CCSTMTRS)>(.*?)</(?:STMTRS|CCSTMTRS)>', txt, re.S | re.I) or [txt]
    org = ofx_tag(txt, 'ORG')
    out, total, conf_all = [], 0, []
    for bloco in blocos:
        bank = ofx_tag(bloco, 'BANKID').lstrip('0').zfill(3) if ofx_tag(bloco, 'BANKID') else ''
        banco = f'{NOME_BANCO.get(bank, org or "?")} ({bank})' if bank else (org or 'cartão' if 'CCACCTFROM' in bloco.upper() else '?')
        conta = {'banco': banco, 'ag': ofx_tag(bloco, 'BRANCHID') or '?', 'conta': ofx_tag(bloco, 'ACCTID') or '?',
                 'titular': ''}
        trs = re.findall(r'<STMTTRN>(.*?)(?=</STMTTRN>|<STMTTRN>|</BANKTRANLIST>)', bloco, re.S | re.I)
        rows, si = [], None
        for b in trs:
            memo, name = ofx_tag(b, 'MEMO'), ofx_tag(b, 'NAME')
            hist = memo if (not name or norm(name) in norm(memo)) else (f'{memo} {name}' if memo else name)
            hist = re.sub(r'\s+', ' ', hist).strip()
            v = ofx_valor(ofx_tag(b, 'TRNAMT') or '0')
            fitid = ofx_tag(b, 'FITID')
            doc = next((x for x in (ofx_tag(b, 'CHECKNUM'), ofx_tag(b, 'REFNUM')) if x and x != fitid), '')
            data = ofx_data(ofx_tag(b, 'DTPOSTED'))
            if RE_SALDO.match(norm(hist)):
                if re.search(r'anterior|inicial', norm(hist)) and not rows and si is None:
                    si = fmt(v)
                else:
                    rows.append({'data': data, 'hist': hist, 'doc': doc, 'valor': None, 'sinal': None, 'saldo': fmt(v),
                                 'pag': 0, 'ocr': False, 'tipo': 's'})
                continue
            rows.append({'data': data, 'hist': hist, 'doc': doc, 'valor': fmt(abs(v)).replace('.', ''),
                         'sinal': -1 if v < 0 else 1, 'saldo': None, 'pag': 0, 'ocr': False, 'tipo': 't'})
        ledger = re.search(r'<LEDGERBAL>(.*?)(?:</LEDGERBAL>|<AVAILBAL>|$)', bloco, re.S | re.I)
        sf = fmt(ofx_valor(ofx_tag(ledger[1], 'BALAMT'))) if ledger and ofx_tag(ledger[1], 'BALAMT') else None
        saldos = list(conferir(rows, si, sf))
        if si is None and sf is not None:
            cred, deb = saldos[0], saldos[2]
            saldos[4] = fmt(dec(sf) - cred + deb) + ' (calc.: final − lançamentos)'
            saldos[6] = 'n/d (o OFX não traz saldo inicial)'
        a, b = ofx_data(ofx_tag(bloco, 'DTSTART')), ofx_data(ofx_tag(bloco, 'DTEND'))
        per = f'{a} a {b}' if a and b else periodo_texto(None, rows)
        tab, obs = tabela_md(rows)
        cab = cabecalho_md(Path(arq).name, conta, per, arq, 'OFX', 'OFX', '', saldos, obs)
        if len(blocos) > 1:
            cab[0] = f'# Extrato - {Path(arq).name} - conta {conta["conta"]}'
        out += ([''] if out else []) + cab + [''] + tab
        total += sum(r['tipo'] == 't' for r in rows)
        conf_all.append(saldos[6])
    return out, len(txt), total, '; '.join(conf_all)


# ----------------------------------------------------------------- CSV / XLSX

def valor_planilha(v):
    """Celula -> texto com virgula decimal, sem mudar os digitos."""
    if v is None or v == '':
        return None
    if isinstance(v, (int, float)):
        return fmt(Decimal(str(v))).replace('.', '')
    s = str(v).strip().replace('R$', '').replace(' ', '')
    if not s:
        return None
    neg = s.startswith('-') or s.endswith('-') or (s.startswith('(') and s.endswith(')')) or s.upper().endswith('D')
    s = s.strip('-+()').rstrip('CDcd')
    if re.match(r'^\d{1,3}(\.\d{3})*,\d{1,2}$|^\d+,\d{1,2}$', s):
        num = s
    elif re.match(r'^\d{1,3}(,\d{3})*\.\d{1,2}$|^\d+\.\d{1,2}$', s):
        num = s.replace(',', '').replace('.', ',')
    elif re.match(r'^\d+$', s):
        num = s + ',00'
    else:
        return 'X' + str(v)
    if re.search(r',\d$', num):
        num += '0'
    return ('-' if neg else '') + num


def data_planilha(v):
    if isinstance(v, (dt.datetime, dt.date)):
        return v.strftime('%d/%m/%Y')
    s = str(v or '').strip()[:10]
    m = re.match(r'^(\d{4})-(\d{2})-(\d{2})$', s)
    if m:
        return f'{m[3]}/{m[2]}/{m[1]}'
    m = re.match(r'^(\d{1,2})[/.-](\d{1,2})[/.-](\d{2,4})$', s)
    if m:
        a = m[3] if len(m[3]) == 4 else '20' + m[3]
        return f'{int(m[1]):02d}/{int(m[2]):02d}/{a}'
    return None


def mapa_colunas(cab):
    m = {}
    for i, c in enumerate(cab):
        k = norm(str(c or '')).replace('(r$)', '').strip(' :')
        if not k:
            continue
        if 'data' in m and k.startswith('data'):
            continue
        if k.startswith('data') or k in ('date', 'dt', 'dia'):
            m['data'] = i
        elif k.startswith('saldo') or k == 'balance':
            m.setdefault('saldo', i)
        elif k.startswith(('credito', 'entrada')):
            m.setdefault('cred', i)
        elif k.startswith(('debito', 'saida')):
            m.setdefault('deb', i)
        elif k.startswith(('valor', 'amount', 'montante', 'quantia')):
            m.setdefault('valor', i)
        elif k.startswith(('doc', 'n doc', 'nº doc', 'numero', 'num doc')):
            m.setdefault('doc', i)
        elif k in ('tipo', 'd/c', 'c/d', 'natureza'):
            m.setdefault('tipo', i)
        elif k.startswith(('hist', 'descri', 'lancamento', 'memo', 'detalhe', 'estabelecimento', 'title', 'titulo',
                           'favorecido', 'complemento')):
            m.setdefault('hist', []).append(i)
    return m if 'data' in m and m.keys() & {'valor', 'cred', 'deb'} else None


def tabela_planilha(linhas):
    """Linhas de celulas -> (rows, si, sf, fora) ou None se nao achar cabecalho."""
    for ih, cab in enumerate(linhas[:40]):
        m = mapa_colunas(cab)
        if m:
            break
    else:
        return None
    rows, fora, si, sf = [], [], None, None
    cel = lambda r, k: r[m[k]] if k in m and m[k] < len(r) else None  # noqa: E731
    for r in linhas[ih + 1:]:
        if not any(str(c or '').strip() for c in r):
            continue
        data = data_planilha(cel(r, 'data'))
        hist = ' '.join(str(r[i]).strip() for i in m.get('hist', []) if i < len(r) and r[i] not in (None, ''))
        hist = re.sub(r'\s+', ' ', hist)
        doc = str(cel(r, 'doc') or '').strip()
        doc = doc[:-2] if doc.endswith('.0') else doc
        saldo = valor_planilha(cel(r, 'saldo'))
        if saldo and saldo.startswith('X'):        # anotacao feita na coluna do saldo ("OK", "NF 64140")
            hist = f'{hist} / {str(cel(r, "saldo")).strip()}'
            saldo = None
        val = None
        for k, s in (('valor', 0), ('cred', 1), ('deb', -1)):
            v = valor_planilha(cel(r, k))
            if v and v.strip('-') not in ('0,00',):
                val = v if s == 0 else (v.lstrip('-') if s == 1 else '-' + v.lstrip('-'))
                break
        tipo = norm(str(cel(r, 'tipo') or ''))
        if val and not val.startswith('-') and tipo in ('d', 'debito', 'saida'):
            val = '-' + val
        if RE_SALDO.match(norm(hist)) and (saldo or val):
            v = saldo or val
            if re.search(r'anterior|inicial', norm(hist)) and not rows:
                si = v
            elif re.search(r'final|atual', norm(hist)):
                sf = v
            else:
                rows.append({'data': data or '', 'hist': hist, 'doc': doc, 'valor': None, 'sinal': None, 'saldo': v,
                             'pag': 0, 'ocr': False, 'tipo': 's'})
            continue
        if not data or not val or val.startswith('X') or (saldo or '').startswith('X'):
            fora.append('|'.join(str(c) for c in r if c not in (None, '')))
            continue
        rows.append({'data': data, 'hist': hist, 'doc': doc, 'valor': val.lstrip('-'), 'sinal': -1 if val.startswith('-') else 1,
                     'saldo': saldo, 'pag': 0, 'ocr': False, 'tipo': 't'})
    return rows, si, sf, fora


def converter_planilha(arq):
    ext = Path(arq).suffix.lower()
    folhas = []
    if ext == '.csv':
        txt = ler_texto_bytes(Path(arq).read_bytes())
        amostra = txt[:5000]
        try:
            dialeto = csv.Sniffer().sniff(amostra, delimiters=';,\t|')
        except csv.Error:
            dialeto = csv.excel
            dialeto.delimiter = ';' if amostra.count(';') >= amostra.count(',') else ','
        folhas.append(('', list(csv.reader(io.StringIO(txt), dialeto))))
        cru = len(txt)
    else:
        if ext == '.xls':
            try:
                import xlrd
            except ImportError:
                raise RuntimeError('arquivo .xls antigo: abra no Excel e salve como .xlsx (ou instale xlrd)')
            wb = xlrd.open_workbook(arq)
            for sh in wb.sheets():
                linhas = []
                for i in range(sh.nrows):
                    row = []
                    for c in sh.row(i):
                        row.append(dt.datetime(*xlrd.xldate_as_tuple(c.value, wb.datemode)) if c.ctype == 3 else c.value)
                    linhas.append(row)
                folhas.append((sh.name, linhas))
        else:
            import openpyxl
            wb = openpyxl.load_workbook(arq, read_only=True, data_only=True)
            for ws in wb.worksheets:
                folhas.append((ws.title, [list(r) for r in ws.iter_rows(values_only=True)]))
        cru = sum(len('\t'.join(str(c) for c in r if c is not None)) + 1 for _, ls in folhas for r in ls)
    out, total, confs = [], 0, []
    usadas = [(n, ls) for n, ls in folhas if any(any(c not in (None, '') for c in r) for r in ls)]
    for nome, linhas in usadas:
        texto = '\n'.join(' '.join(str(c) for c in r if c not in (None, '')) for r in linhas[:40])
        conta = dados_conta(texto)
        res = tabela_planilha(linhas)
        sufixo = f' - aba {nome}' if len(usadas) > 1 else ''
        if not res or not any(r['tipo'] == 't' for r in res[0]):
            cab = cabecalho_md(Path(arq).name + sufixo, conta, '?', arq, f'{len(linhas)} linha(s)', ext[1:].upper(), '',
                               None, ['tabela NÃO montada com segurança (colunas não reconhecidas): conteúdo abaixo'])
            corpo = ['|'.join('' if c is None else str(c) for c in r).rstrip('|') for r in linhas]
            out += ([''] if out else []) + cab + [''] + [c for c in corpo if c.strip('|')]
            confs.append('texto')
            continue
        rows, si, sf, fora = res
        reordena_saldo_dia(rows)
        aplic = ajusta_saldos(rows)
        saldos = conferir(rows, si, sf)
        tab, obs = tabela_md(rows)
        if aplic:
            obs.insert(0, 'aplicação automática: o Confere usa o SALDO TOTAL DISPONÍVEL (conta + aplicação); APL/RES APLIC AUT ficam fora da soma')
        if fora:
            obs.append(f'{len(fora)} linha(s) fora da tabela no fim')
        cab = cabecalho_md(Path(arq).name + sufixo, conta, periodo_texto(achar_periodo(texto), rows), arq,
                           f'{len(linhas)} linha(s)', ext[1:].upper(), '', saldos, obs)
        out += ([''] if out else []) + cab + [''] + tab + ((['## Fora da tabela'] + fora) if fora else [])
        total += sum(r['tipo'] == 't' for r in rows)
        confs.append(saldos[6])
    return out, cru, total, '; '.join(confs)


# ----------------------------------------------------------------- arquivo, log, varredura

def destino_md(arq):
    p = Path(arq)
    alvo = p.with_name(p.stem + '_extrato.md')
    n = 2
    while alvo.exists():
        alvo = p.with_name(f'{p.stem}_extrato ({n}).md')
        n += 1
    return alvo


def registrar(arq, resultado):
    try:
        if LOG.exists() and LOG.stat().st_size > 1_000_000:
            linhas = LOG.read_text(encoding='utf-8', errors='replace').splitlines()
            LOG.write_text('\n'.join(linhas[len(linhas) // 2:]) + '\n', encoding='utf-8')
        with LOG.open('a', encoding='utf-8') as f:
            f.write(f'{dt.datetime.now():%d/%m/%Y %H:%M}|{arq}|{resultado}\n')
    except OSError:
        pass


def converter(arq, stats=False):
    arq = Path(arq).resolve()
    t0 = time.time()
    ext = arq.suffix.lower()
    if ext == '.pdf':
        linhas, cru, n, conf = converter_pdf(arq)
    elif ext == '.ofx':
        linhas, cru, n, conf = converter_ofx(arq)
    elif ext in ('.csv', '.xlsx', '.xlsm', '.xls'):
        linhas, cru, n, conf = converter_planilha(arq)
    else:
        raise RuntimeError(f'tipo de arquivo não suportado: {ext}')
    md = '\n'.join(linhas) + '\n'
    alvo = destino_md(arq)
    tmp = alvo.with_name(alvo.name + '.tmp')
    tmp.write_text(md, encoding='utf-8')
    os.replace(tmp, alvo)
    seg = time.time() - t0
    conf_curto = conf.split(';')[0] if conf else ''
    res = f'ok {n} lanç. | confere: {conf_curto} | {seg:.1f}s -> {alvo.name}'
    registrar(arq, res)
    msg(f'{arq.name}: {res}')
    if stats:
        red = 100 * (1 - len(md) / cru) if cru else 0
        msg(f'   texto cru: {cru} caracteres | .md: {len(md)} caracteres | {red:.0f}% menor')
    return {'arquivo': str(arq), 'md': str(alvo), 'lancamentos': n, 'confere': conf, 'segundos': round(seg, 2),
            'cru': cru, 'md_chars': len(md)}


def ler_config():
    try:
        return json.loads((AQUI / 'config.json').read_text(encoding='utf-8-sig'))
    except (OSError, ValueError):
        return {}


PASTAS_DRIVE = [  # pastas dos clientes no Google Drive: so as subpastas "Extrato" (ver LEIA-ME)
    r'G:\Meu Drive\Trabalho ROF\Contabilidade\Arquivos RENATA Dominio',
    r'G:\Meu Drive\Trabalho ROF\Contabilidade\Arquivos ROF Dominio',
    r'G:\Meu Drive\Trabalho ROF\Contabilidade\Arquivos PROTECTION Dominio\25 - Cosmetici',
]
DESDE_PADRAO = '2026-09-01'


def acha_pasta(p):
    """O Google Drive pode montar em outra letra (G:, H:, I:...): procura a mesma pasta nas outras letras."""
    if os.path.isdir(p) or os.name != 'nt' or not re.match(r'^[A-Za-z]:\\', p):
        return p if os.path.isdir(p) else None
    for letra in 'DEFGHIJKLMNOPQRSTUVWXYZ':
        q = letra + p[1:]
        if os.path.isdir(q):
            return q
    return None


# o que NAO e extrato dentro das pastas "Extrato" dos clientes (visto no Drive em 29/10/2026)
RE_PASTA_NAO = re.compile(r'comprova|contas? pagas|pagamento|nota|\bnfs?\b|boleto|guia|folha|recibo|despesa|controle|'
                          r'historico|relatorio|conciliacao|lancamento')
RE_ARQ_NAO = re.compile(r'comprov|relatorio|relato_rio|conferencia|balancete|lancamento|retirada|conciliacao|controle|'
                        r'faltante|pro ?labore|prolabore|pagamento|folha|guia|darf|\bdas\b|inss|fgts|\bnfs?\b|nota|'
                        r'recibo|boleto|aluguel|condominio|planilha|repasse|assistencia|funeral|parcela|emprestimo|'
                        r'fatura|devolucao|financeiro|imposto|tributo|holerite|\bvt\b|rescisao|ferias')


def eh_extrato_drive(rel_parts, nome):
    """Arquivo das pastas do Drive que deve ser convertido: dentro de uma pasta que comeca com 'Extrato'
    (sem subpasta de comprovantes, notas...) e com nome que nao seja de relatorio/planilha/comprovante."""
    partes = [norm(p) for p in rel_parts]
    i = next((n for n, p in enumerate(partes) if p.startswith('extrato')), None)
    if i is None or any(RE_PASTA_NAO.search(p) for p in partes[i + 1:]):
        return False
    base = norm(Path(nome).stem).replace('_', ' ')
    if base.startswith('extrato'):      # "Extrato_Lancamentos_3918..." e extrato; so barra o que e claramente outra coisa
        return not re.search(r'comprov|relatorio|conciliacao|controle|faltante|balancete|retirada', base)
    return not RE_ARQ_NAO.search(base)


def mes_da_pasta(rel_parts):
    """'09_2026' no caminho -> date(2026, 9, 1)."""
    for p in rel_parts:
        m = re.fullmatch(r'(\d{2})[_.-](\d{4})', p.strip())
        if m and 1 <= int(m[1]) <= 12:
            return dt.date(int(m[2]), int(m[1]), 1)
    return None


def candidatos(stats_cfg):
    """(arquivo, mtime) a converter: tudo da pasta de entrada + o que estiver em subpastas 'Extrato'
    das pastas do Drive, alterado desde a data 'desde' (para nao converter o historico inteiro)."""
    cfg = stats_cfg
    entrada = cfg.get('entrada') or str(AQUI.parent / '01 - Entrada')
    raizes = [(entrada, False)] + [(p, True) for p in cfg.get('pastas_drive', PASTAS_DRIVE)]
    try:
        desde = dt.datetime.fromisoformat(cfg.get('desde', DESDE_PADRAO)).timestamp()
    except ValueError:
        desde = 0
    for raiz0, so_extrato in raizes:
        raiz = acha_pasta(raiz0)
        if not raiz:
            msg(f'Pasta não encontrada (Google Drive aberto?): {raiz0}')
            continue
        for pasta, dirs, arqs in os.walk(raiz):
            dirs[:] = [d for d in dirs if not d.startswith(('.', '_', '~'))]
            rel = Path(pasta).relative_to(raiz).parts
            if so_extrato and not any(norm(parte).startswith('extrato') for parte in rel):
                continue
            mes = mes_da_pasta(rel)
            if so_extrato and mes and mes < dt.date.fromtimestamp(desde):
                continue
            for a in sorted(arqs):
                p = Path(pasta) / a
                if p.suffix.lower() not in EXTS or a.startswith(('~$', '.')):
                    continue
                if so_extrato and not eh_extrato_drive(rel, a):
                    continue
                if p.with_name(p.stem + '_extrato.md').exists():
                    continue
                try:
                    mt = p.stat().st_mtime
                except OSError:
                    continue
                if so_extrato and mt < desde:
                    continue
                yield p, mt


def limpar(apagar=False):
    """Acha os _extrato.md que o conversor criou nas pastas do Drive para arquivos que NAO sao extrato
    (comprovantes, balancetes, planilhas...). Sem apagar=True so lista. So apaga .md que comecam com '# Extrato - '."""
    cfg = ler_config()
    achados, refazer = [], []
    for raiz0 in cfg.get('pastas_drive', PASTAS_DRIVE):
        raiz = acha_pasta(raiz0)
        if not raiz:
            continue
        for pasta, dirs, arqs in os.walk(raiz):
            rel = Path(pasta).relative_to(raiz).parts
            for a in arqs:
                m = re.fullmatch(r'(.+)_extrato( \(\d+\))?\.md', a)
                if not m:
                    continue
                origs = [x for x in arqs if Path(x).stem == m[1] and Path(x).suffix.lower() in EXTS]
                nome_orig = origs[0] if origs else m[1] + '.pdf'
                md = Path(pasta) / a
                try:
                    with md.open(encoding='utf-8', errors='replace') as f:
                        cab = [f.readline() for _ in range(8)]
                except OSError:
                    continue
                if not cab[0].startswith('# Extrato - '):
                    continue                     # .md que nao foi o conversor que fez
                if not eh_extrato_drive(rel, nome_orig):
                    achados.append(md)           # nao e extrato
                elif origs and any('Confere: NÃO' in c or 'NÃO montada' in c for c in cab):
                    refazer.append(md)           # extrato que a versao anterior leu errado: apaga para converter de novo
    for md in achados:
        msg(f'  {md}')
    for md in refazer:
        msg(f'  (refazer) {md}')
    msg(f'{len(achados)} .md de documentos que não são extrato e {len(refazer)} de extratos para converter de novo.')
    if apagar:
        n = 0
        for md in achados + refazer:
            try:
                md.unlink()
                n += 1
            except OSError as e:
                msg(f'  não apagou {md.name}: {e}')
        registrar('limpeza', f'apagados {n} .md de documentos que não são extrato')
        msg(f'Apagados: {n} (no Google Drive vão para a Lixeira).')
    return achados + refazer


def varrer(stats=False):
    cfg = ler_config()
    trava = AQUI / 'conversor.lock'
    try:
        if trava.exists() and time.time() - trava.stat().st_mtime < 3600:
            msg('Outra conversão já está rodando.')
            return
        trava.write_text(str(os.getpid()))
    except OSError:
        return
    try:
        try:
            estado = json.loads(ESTADO.read_text(encoding='utf-8'))
        except (OSError, ValueError):
            estado = {}
        feitos = 0
        for p, mt in candidatos(cfg):
            if time.time() - mt < 20:           # ainda baixando/salvando
                continue
            if estado.get(str(p)) == mt:         # ja deu erro nesta versao do arquivo
                continue
            try:
                converter(p, stats)
                estado.pop(str(p), None)
                feitos += 1
            except Exception as e:  # noqa: BLE001
                estado[str(p)] = mt
                registrar(p, f'ERRO: {e}')
                msg(f'{p.name}: ERRO: {e}')
            try:
                trava.write_text(str(os.getpid()))   # avisa que ainda esta rodando
            except OSError:
                pass
        ESTADO.write_text(json.dumps(estado, ensure_ascii=False, indent=0), encoding='utf-8')
        if not feitos:
            msg('Nada novo para converter.')
    finally:
        try:
            trava.unlink()
        except OSError:
            pass


def main(argv):
    global OCULTO
    OCULTO = '--oculto' in argv
    stats = '--stats' in argv
    arqs = [a for a in argv if not a.startswith('--')]
    if '--limpar' in argv:
        limpar(apagar='--apagar' in argv)
        return 0
    if not arqs:
        varrer(stats)
        return 0
    erros = 0
    for a in arqs:
        try:
            converter(a, stats)
        except Exception as e:  # noqa: BLE001
            erros += 1
            registrar(a, f'ERRO: {e}')
            msg(f'{Path(a).name}: ERRO: {e}')
    return 1 if erros else 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
