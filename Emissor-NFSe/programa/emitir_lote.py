# -*- coding: utf-8 -*-
"""Emissão em lote pelo Emissor ROF, a partir de um arquivo JSON com a lista de notas.

Uso:
    python emitir_lote.py lote.json --thumb <impressao digital do certificado no Windows> [--so-conferir]

- Usa o certificado A1 instalado no Windows (sem senha, sem exportar a chave).
- Emite uma nota por vez, na ordem do arquivo, com as mesmas conferências da tela.
- PARA no primeiro resultado que não seja AUTORIZADA (rejeição, incerteza, bloqueio).
- Grava o resultado de cada nota em <lote>_resultado.json e no Histórico do programa.
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from rof_nfse import certificado_windows, dados, emissao  # noqa: E402


def main():
    args = sys.argv[1:]
    if not args:
        print(__doc__)
        return 2
    arq = args[0]
    thumb = args[args.index("--thumb") + 1] if "--thumb" in args else ""
    so_conferir = "--so-conferir" in args
    with open(arq, "r", encoding="utf-8") as f:
        lote = json.load(f)
    cfg = dados.carregar_config()
    print("Ambiente:", "PRODUÇÃO" if str(cfg["ambiente"]) == "1" else "Produção Restrita (teste)", "| série", cfg["serie"])
    cert = None if so_conferir else certificado_windows.CertificadoWindows(thumb)
    saida = []
    for i, item in enumerate(lote, 1):
        nota = item["nota"]
        rotulo = "%d/%d %s R$ %s" % (i, len(lote), nota["tomador"]["nome"], nota["valor"])
        if so_conferir:
            r = emissao.conferir(nota, cfg)
            erros = [x["msg"] for x in r["itens"] if x["nivel"] == "erro"]
            print(rotulo, "->", "OK" if r["ok"] else "ERRO: " + " | ".join(erros))
            saida.append({"linha": item.get("linha"), "ok": r["ok"], "erros": erros})
            continue
        try:
            r = emissao.emitir(nota, cfg, cert, "EMITIR")
        except Exception as e:  # erro do programa/certificado: para o lote com a mensagem, sem quebrar
            r = {"situacao": "ERRO_PROGRAMA", "msg": "%s: %s (confira no Histórico/servidor se a DPS virou nota "
                 "antes de repetir)" % (type(e).__name__, e)}
        resumo = {"linha": item.get("linha"), "tomador": nota["tomador"]["nome"], "valor": nota["valor"],
                  "situacao": r.get("situacao"), "n_nfse": r.get("n_nfse"), "chave": r.get("chave"),
                  "msg": r.get("msg"), "erros": r.get("erros"), "divergencias": r.get("divergencias"),
                  "arquivos": r.get("arquivos")}
        saida.append(resumo)
        print(rotulo, "->", r.get("situacao"), r.get("n_nfse") or "", r.get("chave") or "", r.get("msg") or "")
        if r.get("erros"):
            print("   erros:", json.dumps(r["erros"], ensure_ascii=False))
        if r.get("situacao") != "AUTORIZADA":
            print("PAREI: resultado diferente de AUTORIZADA.")
            break
    with open(os.path.splitext(arq)[0] + "_resultado.json", "w", encoding="utf-8") as f:
        json.dump(saida, f, ensure_ascii=False, indent=2)
    return 0


if __name__ == "__main__":
    sys.exit(main())
