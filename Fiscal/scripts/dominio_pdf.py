"""Lê o relatório "Acompanhamento de Entradas/Saídas" do Domínio salvo em PDF.

Serve quando o escritório só tem o relatório em PDF. Cada lançamento vira um
dicionário com os mesmos campos de dominio_relatorios.parse_acompanhamento
(menos os impostos), mais o CNPJ/CPF do participante.
"""
import re
import subprocess
from decimal import Decimal

CAB = re.compile(r'^\s*(\d+)\s+(\d\d/\d\d/\d{4})\s+(\d\d/\d\d/\d{4})\s+(\S+)\s+(\S+)\s+(\d{2})\s+(\d+)\s+(.*)$')
DOC = re.compile(r'(\d{2}\.\d{3}\.\d{3}/\d{4}-\d{2}|\d{3}\.\d{3}\.\d{3}-\d{2})')
CFOP = re.compile(r'(\d)-(\d{3})\s+(\d+)\s+([A-Z]{2})\s+([\d.]+,\d\d)')
PERIODO = re.compile(r'Período:\s+(\d\d/\d\d/\d{4})\s+até\s+(\d\d/\d\d/\d{4})')


def _texto(path):
    if path.lower().endswith('.pdf'):
        return subprocess.run(['pdftotext', '-layout', path, '-'], capture_output=True, text=True, check=True).stdout
    return open(path, encoding='utf-8').read()


def _dec(s):
    return Decimal(s.replace('.', '').replace(',', '.'))


def parse_acompanhamento_pdf(path):
    txt = _texto(path)
    m = PERIODO.search(txt)
    periodo = (m.group(1), m.group(2)) if m else None
    regs, atual = [], None

    def fecha():
        if not atual:
            return
        bloco = ' '.join(atual['_linhas'])
        d = DOC.search(bloco)
        c = CFOP.search(bloco)
        atual['cnpj'] = re.sub(r'\D', '', d.group(1)) if d else ''
        if c:
            atual.update(cfop=c.group(1) + c.group(2), acumulador=c.group(3), uf=c.group(4),
                         valor_contabil=_dec(c.group(5)))
        nome = DOC.sub(' ', atual['_resto'])
        nome = re.sub(r'^\d{2}\.\d{3}\.\d{3}\s+', '', nome)
        atual['participante'] = re.sub(r'\s+', ' ', nome).strip()
        del atual['_linhas'], atual['_resto']
        if c:
            regs.append(atual)

    for ln in txt.splitlines():
        m = CAB.match(ln)
        if m:
            fecha()
            atual = dict(codigo=m.group(1), data=m.group(2), entrada=m.group(3), nota=m.group(4).lstrip('0'),
                         serie=m.group(5), especie=m.group(6), cod_participante=m.group(7),
                         _resto=m.group(8), _linhas=[m.group(8)])
        elif atual is not None:
            if ln.strip().startswith('Total') or 'Página:' in ln:
                fecha()
                atual = None
            elif ln.strip():
                atual['_linhas'].append(ln)
    fecha()
    return periodo, regs
