#!/usr/bin/env python3
"""Aplica as regras de leitura do kit ROF às skills.

Seções (inseridas no SKILL.md antes da primeira seção "## " da skill, e no fim do
references/padrao_rof.md, se existir):
  - leitura_arquivos.md  -> todas as skills rof-* e extrato-dominio
  - leitura_extratos.md  -> skills de contabilidade que leem extratos
                            (rof-contabilidade*, exceto folha-korp, e extrato-dominio)
Scripts:
  - copia scripts/ler_documento.py;
  - scripts/extrato_dominio.py passa a ler o _extrato.md (patches/extrato_md.py);
  - scripts/gerar_skill_empresa.py (extrato-dominio) passa a gerar skills novas já com tudo isso.
Não duplica nada se rodar de novo.

Uso:
  python kit-rof/aplicar_leitura.py <pasta_das_skills> <pasta_saida> [--zip]
  (pasta_saida igual a pasta_das_skills = atualizar no lugar)
"""
import hashlib
import os
import re
import shutil
import sys

KIT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(KIT, "patches"))
import extrato_md  # noqa: E402

SCRIPT = os.path.join(KIT, "scripts", "ler_documento.py")
SECOES = {  # arquivo -> marca que identifica a seção já inserida
    "leitura_arquivos.md": "Leitura de Arquivos (padrão ROF",
    "leitura_extratos.md": "Leitura de extratos (Conversor de extratos ROF)",
}
NAO_LEEM_EXTRATO = {"rof-contabilidade-folha-korp"}
SEM_LEITURA = {"rof-sincronizar-pastas"}  # só copia pastas, não lê documentos


def ler(caminho):
    with open(caminho, encoding="utf-8") as f:
        return f.read()


def gravar(caminho, texto):
    with open(caminho, "w", encoding="utf-8") as f:
        f.write(texto)


def secoes_da_skill(nome):
    secoes = ["leitura_arquivos.md"]
    if (nome.startswith("rof-contabilidade") and nome not in NAO_LEEM_EXTRATO) or nome == "extrato-dominio":
        secoes.append("leitura_extratos.md")
    return secoes


def texto_secao(arquivo):
    return ler(os.path.join(KIT, arquivo)).strip() + "\n\n"


def inserir(texto, arquivo):
    """Insere a seção antes da primeira seção "## " que não seja do kit."""
    if SECOES[arquivo] in texto:
        return texto, False
    inicio = 0
    m = re.match(r"---\n.*?\n---\n", texto, re.S)  # frontmatter
    if m:
        inicio = m.end()
    pos = len(texto)
    for h2 in re.finditer(r"^## .*$", texto[inicio:], re.M):
        if not any(marca in h2.group(0) for marca in SECOES.values()):
            pos = inicio + h2.start()
            break
    return texto[:pos] + texto_secao(arquivo) + texto[pos:], True


def corrigir_gerador(codigo):
    """gerar_skill_empresa.py: skills novas nascem com as seções e o ler_documento.py."""
    if "leitura_extratos.md" in codigo:
        return codigo
    ancora = '          "## Dados da Empresa\\n",\n'
    scripts = 'for sc in ("extrato_dominio.py", '
    if ancora not in codigo or scripts not in codigo:
        raise ValueError("gerar_skill_empresa.py com estrutura diferente: não alterado")
    codigo = codigo.replace(ancora,
        '          *[(BASE / "references" / ref).read_text(encoding="utf-8").strip() + "\\n"\n'
        '            for ref in ("leitura_arquivos.md", "leitura_extratos.md") if (BASE / "references" / ref).exists()],\n'
        + ancora, 1)
    return codigo.replace(scripts, 'for sc in ("ler_documento.py", "extrato_dominio.py", ', 1)


def aplicar(origem, destino, nome):
    if os.path.abspath(origem) != os.path.abspath(destino):
        shutil.copytree(origem, destino, dirs_exist_ok=True)
    alterou = []
    skill_md = os.path.join(destino, "SKILL.md")
    padrao = os.path.join(destino, "references", "padrao_rof.md")
    for arquivo in secoes_da_skill(nome):
        texto, mudou = inserir(ler(skill_md), arquivo)
        if mudou:
            gravar(skill_md, texto)
            alterou.append(f"SKILL.md+{arquivo}")
        if os.path.exists(padrao) and SECOES[arquivo] not in ler(padrao):
            gravar(padrao, ler(padrao).rstrip("\n") + "\n\n" + texto_secao(arquivo))
            alterou.append(f"padrao_rof.md+{arquivo}")
    scripts = os.path.join(destino, "scripts")
    os.makedirs(scripts, exist_ok=True)
    alvo = os.path.join(scripts, "ler_documento.py")
    if not os.path.exists(alvo) or ler(alvo) != ler(SCRIPT):
        shutil.copy2(SCRIPT, alvo)
        alterou.append("ler_documento.py")
    motor = os.path.join(scripts, "extrato_dominio.py")
    if os.path.exists(motor) and "def ler_extrato_md(" not in ler(motor):
        md5 = hashlib.md5(open(motor, "rb").read()).hexdigest()
        if md5 != extrato_md.ORIGINAL_MD5:
            alterou.append("ATENCAO: extrato_dominio.py de versão diferente, NÃO alterado")
        else:
            gravar(motor, extrato_md.aplicar(ler(motor)))
            alterou.append("extrato_dominio.py lê _extrato.md")
    gerador = os.path.join(scripts, "gerar_skill_empresa.py")
    if os.path.exists(gerador):
        novo = corrigir_gerador(ler(gerador))
        if novo != ler(gerador):
            gravar(gerador, novo)
            for arquivo in SECOES:
                shutil.copy2(os.path.join(KIT, arquivo), os.path.join(destino, "references", arquivo))
            alterou.append("gerar_skill_empresa.py gera skills novas com as regras")
    return alterou


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print(__doc__)
        sys.exit(2)
    raiz, saida = sys.argv[1], sys.argv[2]
    gerar_zip = "--zip" in sys.argv
    for nome in sorted(os.listdir(raiz)):
        origem = os.path.join(raiz, nome)
        if nome in SEM_LEITURA or not ((nome.startswith("rof-") or nome == "extrato-dominio")
                                       and os.path.isfile(os.path.join(origem, "SKILL.md"))):
            continue
        mudancas = aplicar(origem, os.path.join(saida, nome), nome)
        if gerar_zip:
            shutil.make_archive(os.path.join(saida, "_zips", nome), "zip", saida, nome)
        print(f"{nome}: {', '.join(mudancas) or 'já estava atualizada'}")
