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
    __slots__ = ('pag', 'toks', 'ocr')

    def __init__(self, pag, toks, ocr=False):
        self.pag, self.toks, self.ocr = pag, toks, ocr   # toks: [(texto, x0, x1)] com x de 0 a 1

    @property
    def texto(self):
        return ' '.join(t for t, _, _ in self.toks)


def agrupa_linhas(palavras, largura):
    """[(x0,y0,x1,y1,texto)] -> lista de linhas [(texto,x0,x1)], agrupando pela altura na pagina."""
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
    return [sorted(ln['w'], key=lambda w: w[1]) for ln in linhas]


COLS = {
    'data': {'data', 'dt', 'date'},
    'hist': {'historico', 'descricao', 'lancamento', 'lancamentos', 'detalhe', 'detalhes', 'movimentacao'},
    'doc': {'documento', 'doc', 'doc.', 'docto', 'docto.', 'nº', 'n.doc', 'ndoc', 'numero', 'ref', 'ref.'},
    'cred': {'credito', 'creditos', 'entrada', 'entradas', 'deposito', 'depositos', '(+)'},
    'deb': {'debito', 'debitos', 'saida', 'saidas', 'retirada', 'retiradas', '(-)'},
    'valor': {'valor', 'valores', 'valor(r$)', 'montante'},
    'saldo': {'saldo', 'saldo(r$)'},
}


def cabecalho_colunas(ln):
    """Linha 'Data Historico Docto Credito Debito Saldo' -> {coluna: centro x}; None se nao for."""
    achou = {}
    for t, x0, x1 in ln.toks:
        k = norm(t).strip(':')
        for col, nomes in COLS.items():
            if k in nomes and col not in achou:
                achou[col] = (x0 + x1) / 2
    if 'data' in achou and ('hist' in achou or 'doc' in achou) and achou.keys() & {'valor', 'cred', 'deb', 'saldo'}:
        return achou
    return None


# ----------------------------------------------------------------- cabecalho/rodape repetido e avisos

RE_PAGINA = re.compile(r'^(p[aá]g(ina|\.)?|folha)\s*:?\s*\d+\s*(de|/)\s*\d+$|^\d+\s*(de|/)\s*\d+$'
                       r'|^p[aá]gina\b.{0,12}$', re.I)
RE_AVISO = re.compile(r'ouvidoria|\bsac\b|0800|deficiente (auditivo|de fala)|fale conosco|central de atendimento'
                      r'|www\.|https?://|@\w+\.com|atendimento (24|ao cliente)|portal de privacidade', re.I)


def chave_rep(txt):
    k = norm(txt)
    return re.sub(r'\d', '#', k) if RE_PAGINA.match(k) or 'pagina' in k or 'emitido em' in k or 'impresso em' in k else k


def repetidas(paginas):
    """Linhas que aparecem em mais da metade das paginas (cabecalho/rodape)."""
    if len(paginas) < 2:
        return set()
    cont = Counter()
    for linhas in paginas:
        cont.update({chave_rep(ln.texto) for ln in linhas})
    return {k for k, n in cont.items() if n > len(paginas) / 2}


def e_aviso(txt):
    return bool(RE_PAGINA.match(norm(txt)) or RE_AVISO.search(txt))


# ----------------------------------------------------------------- OCR (Windows)

def pasta_imagens(arq):
    h = hashlib.sha1(str(arq).encode('utf-8')).hexdigest()[:8]
    p = Path(tempfile.gettempdir()) / 'ROF-Extratos-OCR' / f'{Path(arq).stem[:60]}-{h}'
    p.mkdir(parents=True, exist_ok=True)
    return p


def ler_tsv_ocr(p):
    """Formato do ocr_windows.ps1: uma linha por linha do extrato; palavras separadas por TAB,
    cada palavra 'x0 x1 texto' (x de 0 a 1)."""
    linhas = []
    for row in p.read_text(encoding='utf-8-sig').splitlines():
        toks = []
        for w in row.split('\t'):
            partes = w.split(' ', 2)
            if len(partes) == 3:
                toks.append((partes[2], float(partes[0]), float(partes[1])))
        if toks:
            linhas.append(toks)
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
            pal, larg = [], 1
            for row in out.splitlines()[1:]:
                c = row.split('\t')
                if len(c) == 12 and c[0] == '1':
                    larg = int(c[8])
                if len(c) == 12 and c[0] == '5' and c[11].strip():
                    x, y, w, h = map(int, c[6:10])
                    pal.append((x, y, x + w, y + h, c[11].strip()))
            res[p] = agrupa_linhas(pal, larg)
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
        paginas.append([Linha(i, toks) for toks in agrupa_linhas(pal, pg.rect.width or 1)])
    n = len(doc)
    doc.close()
    rep = repetidas(paginas)
    escaneadas = []
    for i, linhas in enumerate(paginas, 1):
        proprio = ''.join(ln.texto for ln in linhas if chave_rep(ln.texto) not in rep and not e_aviso(ln.texto))
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
            for toks in res.get(p, []):
                ln = Linha(p, toks, ocr=True)
                cru += len(ln.texto) + 1
                if not repete(ln.texto, base, rep):
                    novas.append(ln)
            if novas:
                paginas[p - 1] = [Linha(p, ln.toks, ocr=False) for ln in paginas[p - 1]] + novas
            else:
                info['sem_texto'].append(p)
        rep = repetidas(paginas)       # de novo, agora com o cabecalho lido pelo OCR
    return paginas, rep, info, cru


def repete(txt, base, rep):
    """Linha do OCR que so rele o cabecalho/rodape (ou o texto que a pagina ja tinha)."""
    k = chave_rep(txt)
    if k in rep:
        return True
    for b in list(base) + list(rep):
        kb = chave_rep(b) if b not in rep else b
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
        if j >= 2 and toks[j - 1][0] in ('C', 'D', '-', '+', '*', '€'):   # OCR costuma ler 'C' como '€'
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
            elif j >= 1 and toks[j - 1][0] in ('-', '+'):
                sinal = -1 if toks[j - 1][0] == '-' else 1
                j -= 1
        vals.insert(0, (num, sinal, x))
        i = j
    return vals, toks[:i]


def separa_doc(resto, cols):
    if len(resto) < 2:
        return resto, ''
    t, x0, x1 = resto[-1]
    if not re.match(r'^\d[\d./-]{2,}$', t) or le_valor(t):
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
    for m in re.finditer(r'(\d{2}/\d{2}/\d{4})\s*(?:a|à|ate|até|-|–)\s*(\d{2}/\d{2}/\d{4})', texto, re.I):
        a, b = data_dmy(m[1]), data_dmy(m[2])
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


def dados_conta(texto):
    t = texto[:6000]
    banco = next((f'{n} ({c})' for c, n, p in BANCOS if re.search(p, t, re.I)), '?')
    ag = re.search(r'ag(?:[eê]ncia|\.)?\s*(?:n[ºo°.]*)?\s*[:\-]?\s*(\d{3,5}(?:-[\dxX])?)\b', t, re.I)
    conta = re.search(r'conta(?:\s*corrente|\s*pagamento|\s*poupan[cç]a)?\s*(?:n[ºo°.]*)?\s*[:\-]?\s*([\d.]{3,15}-?[\dxX]?)\b', t, re.I)
    tit = re.search(r'(?:titular|cliente|nome|correntista|associado)\s*[:\-]\s*([^\n|]{3,70})', t, re.I)
    return {'banco': banco, 'ag': ag[1] if ag else '?', 'conta': conta[1] if conta else '?',
            'titular': re.split(r'\s{2,}|\s(?:cpf|cnpj|ag[eê]ncia|conta)\b', tit[1].strip(), flags=re.I)[0] if tit else ''}


def montar_tabela(paginas, rep, texto_todo):
    """Linhas do PDF -> (lancamentos, fora_da_tabela, saldo_ini, saldo_fin, linhas_com_valor)."""
    periodo = achar_periodo(texto_todo)
    anos = Counter(re.findall(r'\b\d{2}/\d{2}/(\d{4})\b', texto_todo))
    ano_f = ano_por_periodo(periodo, anos.most_common(1)[0][0] if anos else None)
    rows, fora = [], []
    saldo_ini = saldo_fin = None
    cols = None
    data_atual = None
    secao = None
    pend = []
    com_valor = 0
    vistos_rep = set()
    seq = [ln for linhas in paginas for ln in linhas]
    for idx, ln in enumerate(seq):
        k = chave_rep(ln.texto)
        c = cabecalho_colunas(ln)
        if c:
            cols = c
            continue
        data, resto = tira_data(ln.toks, ano_f)
        vals, resto = tira_valores(resto)
        if k in rep or (e_aviso(ln.texto) and not vals):
            if k in rep and k not in vistos_rep and not e_aviso(ln.texto):
                vistos_rep.add(k)
                fora.append(ln)         # cabecalho repetido: guarda so a primeira vez
            continue
        hist_toks, doc = separa_doc(resto, cols) if vals else (resto, '')
        hist = ' '.join(t for t, _, _ in hist_toks).strip(' -|')
        h = norm(hist)
        if data:
            data_atual = data
        if pend and pend[-1][0] != idx - 1:
            fora.extend(p for _, p in pend)
            pend = []
        if not vals:
            if not hist:
                continue
            if data:                                   # 1a linha de um lancamento com valor na linha de baixo
                fora.extend(p for _, p in pend)
                pend = [(idx, ln)]
                continue
            if pend and len(pend) < 2:
                pend.append((idx, ln))
                continue
            prox = seq[idx + 1] if idx + 1 < len(seq) else None
            if prox and prox.pag == ln.pag:
                pd, pr = tira_data(prox.toks, ano_f)
                if not pd and tira_valores(pr)[0] and not RE_SALDO.match(norm(prox.texto)):
                    fora.extend(p for _, p in pend)
                    pend = [(idx, ln)]
                    continue
            if rows and rows[-1]['ln_idx'] == idx - 1 and rows[-1]['pag'] == ln.pag and len(hist) <= 80:
                rows[-1]['hist'] += ' ' + hist          # continuacao do historico anterior
                rows[-1]['ln_idx'] = idx
                continue
            fora.extend(p for _, p in pend)
            pend = []
            if any(ch.isalnum() for ch in ln.texto):
                fora.append(ln)
            continue
        com_valor += 1
        if pend:
            pre = [' '.join(t for t, _, _ in tira_data(p.toks, ano_f)[1]) for _, p in pend]
            hist = (' '.join(pre) + ' ' + hist).strip()
            h = norm(hist)
            pend = []
        valor, sinal, saldo = atribui_valores(vals, cols)
        if RE_TOTAL.match(h):
            if re.search(r'entrada|credito|recebid', h):
                secao = 1
            elif re.search(r'saida|debito|pago|gasto', h):
                secao = -1
            fora.append(ln)
            continue
        if RE_SALDO.match(h):
            v = saldo or (com_sinal(valor, sinal) if valor and valor != 'X' else None)
            if v is None:
                fora.append(ln)
            elif re.search(r'anterior|inicial', h) and saldo_ini is None:
                saldo_ini = v
            elif re.search(r'\bfinal\b|\batual\b', h):
                saldo_fin = v
            elif re.search(r'\bdo dia\b|^saldo em\b|^saldo$|^saldo [\d/]+$|^s a l d o', h) and data_atual:
                rows.append({'data': data or data_atual, 'hist': hist, 'doc': doc, 'valor': None, 'sinal': None,
                             'saldo': v, 'pag': ln.pag, 'ocr': ln.ocr, 'ln_idx': idx, 'tipo': 's', 'secao': None})
            else:
                fora.append(ln)
            continue
        if valor in ('X', None) or not (data or data_atual) or not hist:
            fora.append(ln)
            continue
        rows.append({'data': data or data_atual, 'hist': hist, 'doc': doc, 'valor': valor, 'sinal': sinal,
                     'saldo': saldo, 'pag': ln.pag, 'ocr': ln.ocr, 'ln_idx': idx, 'tipo': 't', 'secao': secao})
    fora.extend(p for _, p in pend)
    return rows, fora, saldo_ini, saldo_fin, com_valor, periodo


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
    return crono


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
        prim = next((r for r in crono if r['saldo']), None)
        if prim and prim['tipo'] == 't' and prim['sinal']:
            saldo_ini = fmt(dec(prim['saldo']) - prim['sinal'] * dec(prim['valor']))
            obs_ini = ' (calc. pela 1ª linha)'
        elif prim and prim['tipo'] == 's':
            idx = crono.index(prim)
            if all(r['tipo'] == 's' for r in crono[:idx + 1]):
                saldo_ini, obs_ini = prim['saldo'], ' (1º saldo)'
    if saldo_fin is None:
        ult = next((r for r in reversed(crono) if r['saldo']), None)
        saldo_fin = ult['saldo'] if ult else None
    quebra = None
    if saldo_ini is not None:
        run = dec(saldo_ini)
        for r in crono:
            if r['tipo'] == 't' and r['sinal']:
                run += r['sinal'] * dec(r['valor'])
            if r['saldo'] and dec(r['saldo']) is not None and run != dec(r['saldo']):
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
            if e_aviso(ln.texto) or (k in rep and k in vistos):
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


def converter_pdf(arq):
    paginas, rep, info, cru = ler_pdf(arq)
    texto_todo = '\n'.join(ln.texto for linhas in paginas for ln in linhas)
    conta = dados_conta(texto_todo)
    rows, fora, si, sf, com_valor, periodo = montar_tabela(paginas, rep, texto_todo)
    crono = completa_sinais(rows, si)
    n_ocr = len(info['ocr'])
    metodo = 'OCR' if n_ocr == info['paginas'] else ('texto do PDF + OCR' if n_ocr else 'texto do PDF')
    ocr_txt = ''
    if n_ocr:
        ocr_txt = f' | OCR: {n_ocr} pág. (p{",".join(map(str, info["ocr"]))}; imagens: {info["imagens"]})'
    obs = []
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
    if fora:
        obs_tab.append(f'{len(fora)} linha(s) fora da tabela no fim')
    cab = cabecalho_md(Path(arq).name, conta, periodo_texto(periodo, rows), arq, n_pag, metodo, ocr_txt, saldos,
                       obs + obs_tab)
    out = cab + [''] + tab
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
        saldos = conferir(rows, si, sf)
        tab, obs = tabela_md(rows)
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


def varrer(stats=False):
    entrada = ler_config().get('entrada') or str(AQUI.parent / '01 - Entrada')
    if not os.path.isdir(entrada):
        registrar(entrada, 'ERRO: pasta de entrada não encontrada')
        msg(f'Pasta de entrada não encontrada: {entrada}')
        return
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
        for raiz, dirs, arqs in os.walk(entrada):
            dirs[:] = [d for d in dirs if not d.startswith(('.', '_', '~'))]
            for a in sorted(arqs):
                p = Path(raiz) / a
                if p.suffix.lower() not in EXTS or a.startswith(('~$', '.')):
                    continue
                if p.with_name(p.stem + '_extrato.md').exists():
                    continue
                try:
                    mt = p.stat().st_mtime
                except OSError:
                    continue
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
                    msg(f'{a}: ERRO: {e}')
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
