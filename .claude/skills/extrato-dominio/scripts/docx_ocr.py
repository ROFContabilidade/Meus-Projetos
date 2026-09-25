#!/usr/bin/env python3
"""Comprovantes em Word (.docx) feitos a partir de PDF: cada pedaço de texto é uma imagem.

  python docx_ocr.py Comprovante_1.docx [Comprovante_2.docx ...] -o trabalho/

Faz OCR (tesseract, por) de cada imagem na ordem do documento e grava <arquivo>.txt, com
"=====PAGINA=====" entre as páginas. A ordem dos campos pode sair trocada: use o texto para achar
favorecido, juros/mora e valores, conferindo sempre com o relatório de pagamentos do Itaú.
Requer tesseract-ocr e tesseract-ocr-por.
"""
import argparse
import os
import re
import subprocess
import tempfile
import zipfile
from concurrent.futures import ThreadPoolExecutor
from io import BytesIO

from PIL import Image, ImageOps


def ocr_docx(caminho, pasta_tmp, processos=4):
    z = zipfile.ZipFile(caminho)
    rels = {}
    for m in re.finditer(r"<Relationship [^>]*>", z.read("word/_rels/document.xml.rels").decode()):
        t = m.group(0)
        rels[re.search(r'Id="([^"]+)"', t)[1]] = re.search(r'Target="([^"]+)"', t)[1]
    doc = z.read("word/document.xml").decode("utf-8")
    toks = [("img", m[1]) if m[1] else ("pg", None)
            for m in re.finditer(r'r:embed="(rId\d+)"|<w:sectPr|w:type="page"', doc)]

    def um(k):
        n, (tipo, rid) = k
        if tipo != "img":
            return n, "\n=====PAGINA=====\n"
        im = Image.open(BytesIO(z.read("word/" + rels[rid].lstrip("/")))).convert("L")
        if im.width < 8 or im.height < 8:
            return n, ""
        im = ImageOps.expand(im.resize((im.width * 3, im.height * 3), Image.LANCZOS), border=20, fill=255)
        f = os.path.join(pasta_tmp, f"{n:05d}.png")
        im.save(f)
        out = subprocess.run(["tesseract", f, "-", "-l", "por", "--psm", "6"], capture_output=True, text=True,
                             env=dict(os.environ, OMP_THREAD_LIMIT="1")).stdout.strip()
        return n, out

    with ThreadPoolExecutor(processos) as ex:
        res = sorted(ex.map(um, enumerate(toks)))
    return "\n".join(t for _, t in res if t)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("arquivos", nargs="+")
    ap.add_argument("-o", "--saida", default=".")
    a = ap.parse_args()
    os.makedirs(a.saida, exist_ok=True)
    for arq in a.arquivos:
        with tempfile.TemporaryDirectory() as tmp:
            texto = ocr_docx(arq, tmp)
        destino = os.path.join(a.saida, os.path.splitext(os.path.basename(arq))[0] + ".txt")
        open(destino, "w", encoding="utf-8").write(texto)
        print(f"{arq}: {texto.count('=====PAGINA=====')} página(s) -> {destino}")


if __name__ == "__main__":
    main()
