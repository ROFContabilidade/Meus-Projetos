#!/usr/bin/env python3
"""Restaura a configuração de uma empresa a partir do pacote da skill dela (.skill).

O repositório é público e a pasta `empresas/` não vai para o GitHub. Por isso cada conversa
nova começa vazia: a usuária anexa o pacote `rof-contabilidade-<empresa>.skill` entregue no
fim do mês anterior (ou indica onde ele está no Drive dela) e este script devolve os arquivos
para `empresas/`, com os nomes usados pelos outros scripts.

Uso:
  python restaurar_empresa.py rof-contabilidade-kopp-industria.skill [--cnpj 00.000.000/0000-00]
Grava empresas/<código>-<nome>.json e, se existirem no pacote, empresas/<código>-<nome>-folha.csv,
-folha-encargos.csv, -entradas.csv e -impostos.csv. Com --cnpj, confere se o pacote é da empresa
informada antes de gravar. No fim imprime o comando para gerar a skill atualizada.
"""
import argparse, json, os, re, sys, zipfile

RAIZ = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))
EMPRESAS = os.path.join(RAIZ, "empresas")
ARQUIVOS = {"folha.csv": "-folha.csv", "folha-encargos.csv": "-folha-encargos.csv",
            "entradas.csv": "-entradas.csv", "impostos.csv": "-impostos.csv"}


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("pacote")
    ap.add_argument("--cnpj")
    a = ap.parse_args()

    z = zipfile.ZipFile(a.pacote)
    nomes = z.namelist()
    base = next((n.split("/")[0] for n in nomes if n.endswith("/references/empresa.json")), None)
    if not base:
        sys.exit("O pacote não tem references/empresa.json: não é uma skill de empresa do padrão ROF.")
    emp = json.loads(z.read(f"{base}/references/empresa.json").decode("utf-8"))
    if a.cnpj and re.sub(r"\D", "", a.cnpj) != re.sub(r"\D", "", str(emp.get("cnpj", ""))):
        sys.exit(f"O pacote é da empresa {emp.get('razao_social')} (CNPJ {emp.get('cnpj')}), não do CNPJ {a.cnpj}.")

    prefixo = f"{emp.get('codigo_empresa', '')}-{base.replace('rof-contabilidade-', '')}".strip("-")
    os.makedirs(EMPRESAS, exist_ok=True)
    gravados = {}
    destino = os.path.join(EMPRESAS, prefixo + ".json")
    open(destino, "wb").write(z.read(f"{base}/references/empresa.json"))
    gravados["json"] = destino
    for origem, sufixo in ARQUIVOS.items():
        n = f"{base}/references/{origem}"
        if n in nomes:
            destino = os.path.join(EMPRESAS, prefixo + sufixo)
            open(destino, "wb").write(z.read(n))
            gravados[origem] = destino

    rel = {k: os.path.relpath(v, RAIZ) for k, v in gravados.items()}
    print(f"Empresa: {emp.get('razao_social')} | CNPJ {emp.get('cnpj')} | código {emp.get('codigo_empresa')}")
    for v in rel.values():
        print("  restaurado:", v)
    for s in emp.get("saldos_conferidos", [])[-3:]:
        print(f"  saldo conferido {s.get('data')} {s.get('banco')}: {s.get('saldo')}")
    if emp.get("meses_lancados"):
        print("  meses lançados:", emp["meses_lancados"])
    cmd = [f"python3 .claude/skills/extrato-dominio/scripts/gerar_skill_empresa.py {rel['json']}"]
    for chave, opc in (("folha.csv", "--folha"), ("entradas.csv", "--entradas"), ("impostos.csv", "--impostos")):
        if chave in rel:
            cmd.append(f"{opc} {rel[chave]}")
    cmd.append(f"--nome {base.replace('rof-contabilidade-', '')} -o <scratchpad>/skills_empresas")
    print("Gerar a skill atualizada no fim do mês:\n  " + " ".join(cmd))


if __name__ == "__main__":
    main()
