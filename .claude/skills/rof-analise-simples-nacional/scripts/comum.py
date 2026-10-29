"""Funções comuns: abrir .xls do Domínio (conserta BIFF inválido via LibreOffice) e formatos."""
import os, subprocess, tempfile, xlrd

def abrir_xls(caminho):
    try:
        return xlrd.open_workbook(caminho)
    except Exception:
        out = tempfile.mkdtemp()
        subprocess.run(['soffice', '--headless', '--convert-to', 'xls:MS Excel 97', '--outdir', out, caminho],
                       capture_output=True, timeout=180)
        return xlrd.open_workbook(os.path.join(out, os.path.basename(caminho)))

def linhas(sheet):
    for r in range(sheet.nrows):
        yield [c.value for c in sheet.row(r)]
