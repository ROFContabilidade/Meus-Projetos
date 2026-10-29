#!/usr/bin/env python3
"""Aplica o padrão ROF de leitura de arquivos (kit-rof/leitura_arquivos.md) às skills.

Para cada skill rof-*:
  - insere a seção "Leitura de Arquivos" no SKILL.md, antes da primeira seção "## ";
  - acrescenta a mesma seção ao references/padrao_rof.md, se existir;
  - copia scripts/ler_documento.py.
Não altera nada se a seção já existir (pode rodar de novo sem duplicar).

Uso:
  python kit-rof/aplicar_leitura.py <pasta_das_skills> <pasta_saida> [--zip]
  (pasta_saida igual a pasta_das_skills = atualizar no lugar)
"""
import os
import re
import shutil
import sys

KIT = os.path.dirname(os.path.abspath(__file__))
MARCA = "Leitura de Arquivos (padrão ROF"
SECAO = open(os.path.join(KIT, "leitura_arquivos.md"), encoding="utf-8").read().strip() + "\n\n"
SCRIPT = os.path.join(KIT, "scripts", "ler_documento.py")


def inserir(texto):
    if MARCA in texto:
        return texto, False
    corpo_inicio = 0
    m = re.match(r"---\n.*?\n---\n", texto, re.S)  # frontmatter
    if m:
        corpo_inicio = m.end()
    h2 = re.search(r"^## ", texto[corpo_inicio:], re.M)
    pos = corpo_inicio + h2.start() if h2 else len(texto)
    return texto[:pos] + SECAO + texto[pos:], True


def aplicar(origem, destino):
    if os.path.abspath(origem) != os.path.abspath(destino):
        shutil.copytree(origem, destino, dirs_exist_ok=True)
    alterou = []
    skill_md = os.path.join(destino, "SKILL.md")
    with open(skill_md, encoding="utf-8") as f:
        novo, mudou = inserir(f.read())
    if mudou:
        with open(skill_md, "w", encoding="utf-8") as f:
            f.write(novo)
        alterou.append("SKILL.md")
    padrao = os.path.join(destino, "references", "padrao_rof.md")
    if os.path.exists(padrao):
        with open(padrao, encoding="utf-8") as f:
            texto = f.read()
        if MARCA not in texto:
            with open(padrao, "a", encoding="utf-8") as f:
                f.write("\n\n" + SECAO.replace("## ", "## 99. ", 1))
            alterou.append("padrao_rof.md")
    os.makedirs(os.path.join(destino, "scripts"), exist_ok=True)
    alvo = os.path.join(destino, "scripts", "ler_documento.py")
    if not os.path.exists(alvo) or open(alvo, "rb").read() != open(SCRIPT, "rb").read():
        shutil.copy2(SCRIPT, alvo)
        alterou.append("scripts/ler_documento.py")
    return alterou


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print(__doc__)
        sys.exit(2)
    raiz, saida = sys.argv[1], sys.argv[2]
    gerar_zip = "--zip" in sys.argv
    for nome in sorted(os.listdir(raiz)):
        origem = os.path.join(raiz, nome)
        if not (nome.startswith("rof-") and os.path.isfile(os.path.join(origem, "SKILL.md"))):
            continue
        destino = os.path.join(saida, nome)
        mudancas = aplicar(origem, destino)
        if gerar_zip:
            shutil.make_archive(os.path.join(saida, "_zips", nome), "zip", saida, nome)
        print(f"{nome}: {', '.join(mudancas) or 'já estava atualizada'}")
