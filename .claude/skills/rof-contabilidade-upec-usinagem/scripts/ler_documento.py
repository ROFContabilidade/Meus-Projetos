#!/usr/bin/env python3
"""Padrão ROF de leitura de arquivos (economia de tokens).

Ordem de prioridade para cada documento:
  1. MD   (.md)                       -> ler direto
  2. Estruturado (.ofx, .xml)         -> ler direto ou pelo script da skill
  3. Planilha (.xlsx, .xls, .csv)     -> ler pelo script da skill (ou converter para MD)
  4. PDF  (.pdf)                      -> NUNCA abrir como imagem: converter para MD
                                         (o .md fica salvo ao lado do PDF e vale nos próximos meses)
  5. Nada funcionou                   -> parar e avisar a Rosangela

Uso:
  python ler_documento.py escolher <pasta>        lista o que ler, na ordem, e o que ignorar
  python ler_documento.py converter <arquivo.pdf> converte para MD (markitdown > pdftotext > pdfplumber)
"""
import os
import shutil
import subprocess
import sys

PRIORIDADE = {
    ".md": (1, "MD"),
    ".ofx": (2, "ESTRUTURADO"),
    ".xml": (2, "ESTRUTURADO"),
    ".xlsx": (3, "PLANILHA"),
    ".xls": (3, "PLANILHA"),
    ".csv": (3, "PLANILHA"),
    ".pdf": (4, "PDF"),
}
MIN_CARACTERES = 50  # menos que isso = PDF escaneado (imagem), sem texto


def _markitdown(pdf):
    exe = shutil.which("markitdown")
    if exe:
        r = subprocess.run([exe, pdf], capture_output=True, text=True, timeout=300)
        return r.stdout if r.returncode == 0 else ""
    try:
        from markitdown import MarkItDown
        return MarkItDown().convert(pdf).text_content
    except Exception:
        return ""


def _pdftotext(pdf):
    exe = shutil.which("pdftotext")
    if not exe:
        return ""
    r = subprocess.run([exe, "-layout", pdf, "-"], capture_output=True, text=True, timeout=300)
    return r.stdout if r.returncode == 0 else ""


def _pdfplumber(pdf):
    try:
        import pdfplumber
    except ImportError:
        return ""
    paginas = []
    with pdfplumber.open(pdf) as doc:
        for i, p in enumerate(doc.pages, 1):
            paginas.append(f"## Página {i}\n\n{p.extract_text() or ''}")
    return "\n\n".join(paginas)


def converter(pdf):
    """Converte o PDF em MD ao lado do arquivo. Retorna o caminho do .md ou None."""
    destino = os.path.splitext(pdf)[0] + ".md"
    if os.path.exists(destino) and os.path.getmtime(destino) >= os.path.getmtime(pdf):
        print(f"OK (já convertido): {destino}")
        return destino
    for nome, func in (("markitdown", _markitdown), ("pdftotext", _pdftotext), ("pdfplumber", _pdfplumber)):
        try:
            texto = func(pdf)
        except Exception:
            texto = ""
        if len(texto.strip()) >= MIN_CARACTERES:
            with open(destino, "w", encoding="utf-8") as f:
                f.write(f"<!-- convertido de {os.path.basename(pdf)} por {nome} -->\n\n{texto}")
            print(f"OK ({nome}): {destino}")
            return destino
    print(
        f"AVISAR A ROSANGELA: não foi possível converter '{pdf}' em texto "
        "(provavelmente PDF escaneado/imagem). Não ler o PDF direto; ver junto com ela."
    )
    return None


def escolher(pasta):
    """Agrupa arquivos pelo nome (sem extensão) e indica qual ler de cada grupo."""
    grupos = {}
    for raiz, _, arquivos in os.walk(pasta):
        for a in arquivos:
            ext = os.path.splitext(a)[1].lower()
            if ext in PRIORIDADE:
                chave = os.path.join(raiz, os.path.splitext(a)[0])
                grupos.setdefault(chave, []).append(os.path.join(raiz, a))
    for chave in sorted(grupos):
        opcoes = sorted(grupos[chave], key=lambda p: PRIORIDADE[os.path.splitext(p)[1].lower()][0])
        melhor = opcoes[0]
        tipo = PRIORIDADE[os.path.splitext(melhor)[1].lower()][1]
        acao = "CONVERTER (ler_documento.py converter)" if tipo == "PDF" else "LER"
        print(f"{acao} [{tipo}] {melhor}")
        for outro in opcoes[1:]:
            print(f"   ignorar {outro}")


if __name__ == "__main__":
    if len(sys.argv) != 3 or sys.argv[1] not in ("escolher", "converter"):
        print(__doc__)
        sys.exit(2)
    if sys.argv[1] == "escolher":
        escolher(sys.argv[2])
    else:
        sys.exit(0 if converter(sys.argv[2]) else 1)
