# -*- coding: utf-8 -*-
"""Ferramentas de apoio do Emissor ROF (todas SÓ LEITURA na Receita; nenhuma emite nota).

Uso (no Prompt/PowerShell, dentro desta pasta):

  python ferramentas_nfse.py certificados
      Lista os certificados A1 instalados no Windows (impressão digital, titular, validade).

  python ferramentas_nfse.py notas-emitidas --thumb <impressão digital> --cnpj <CNPJ> --saida <pasta> [--pdf]
      Baixa pela API (distribuição de DF-e do ADN) TODAS as NFS-e do CNPJ e grava:
        <pasta>\\xml\\*.xml, <pasta>\\indice_notas.csv (uma linha por nota: número, série, DPS, competência,
        valor, tomador, CPF/CNPJ, endereço, e-mail, telefone, descrição) e, com --pdf, os PDFs.
      Serve para: achar a nota modelo de cada cliente, os dados do tomador e a última DPS usada por série.

  python ferramentas_nfse.py por-chave --thumb <impressão digital> --saida <pasta> <chave1> [<chave2> ...]
      Baixa o XML oficial de cada chave e gera o PDF (DANFSe) com QR Code. Substitui o download do portal
      (que pede "Sou humano" a cada nota).

  python ferramentas_nfse.py pdf <arquivo.xml ou pasta>
      Gera o PDF (DANFSe) ao lado de cada XML de NFS-e.

O certificado precisa ser do emitente ou ter procuração eletrônica do emitente (serviço NFS-e).
"""
import base64
import csv
import gzip
import os
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from lxml import etree  # noqa: E402

from rof_nfse import certificado_windows, danfse, regras, transmissao  # noqa: E402

NS = {"n": "http://www.sped.fazenda.gov.br/nfse"}


def _longo(p):
    p = os.path.abspath(p)
    return ("\\\\?\\" + p) if os.name == "nt" and not p.startswith("\\\\?\\") else p


def _cliente(thumb):
    return transmissao.Cliente(certificado_windows.CertificadoWindows(thumb), "1")


def _t(no, xp):
    if no is None:
        return ""
    r = no.xpath(xp, namespaces=NS)
    return (r[0].text or "").strip() if r else ""


def _arg(args, nome, padrao=None):
    return args[args.index(nome) + 1] if nome in args else padrao


def ler_nota(xml):
    doc = etree.fromstring(xml, etree.XMLParser(resolve_entities=False, no_network=True))
    inf = doc.xpath("//n:infNFSe", namespaces=NS)
    if not inf:
        return None
    inf = inf[0]
    tm = (inf.xpath(".//n:DPS//n:toma", namespaces=NS) or [None])[0]
    return {
        "numero": _t(inf, "n:nNFSe"), "serie": _t(inf, ".//n:serie"), "dps": _t(inf, ".//n:nDPS"),
        "competencia": _t(inf, ".//n:dCompet"), "valor": _t(inf, ".//n:vServ"),
        "emitente": _t(inf, ".//n:emit/n:CNPJ") or _t(inf, ".//n:emit/n:CPF"),
        "tomador_doc": _t(tm, "n:CPF") or _t(tm, "n:CNPJ"), "tomador": _t(tm, "n:xNome"),
        "cep": _t(tm, ".//n:CEP"), "logradouro": _t(tm, ".//n:xLgr"), "numero_end": _t(tm, ".//n:nro"),
        "complemento": _t(tm, ".//n:xCpl"), "bairro": _t(tm, ".//n:xBairro"), "cod_mun": _t(tm, ".//n:cMun"),
        "email": _t(tm, "n:email"), "fone": _t(tm, "n:fone"),
        "descricao": _t(inf, ".//n:xDescServ").replace("\n", " / "), "chave": (inf.get("Id") or "")[3:],
    }


def cmd_certificados(_args):
    ps = ("Get-ChildItem Cert:\\CurrentUser\\My | Where-Object { $_.HasPrivateKey } | "
          "ForEach-Object { $_.Thumbprint + ' | ' + $_.NotAfter.ToString('dd/MM/yyyy') + ' | ' + $_.Subject.Split(',')[0] }")
    print(subprocess.run(["powershell", "-NoProfile", "-Command", ps], capture_output=True, text=True).stdout)


def cmd_notas_emitidas(args):
    thumb, cnpj, saida = _arg(args, "--thumb"), regras.so_digitos(_arg(args, "--cnpj", "")), _arg(args, "--saida")
    if not (thumb and cnpj and saida):
        print(__doc__); return 2
    pxml = os.path.join(saida, "xml")
    os.makedirs(_longo(pxml), exist_ok=True)
    cli = _cliente(thumb)
    nsu, notas = 0, []
    while True:
        r = cli._pedir("GET", cli.urls["adn"] + "/contribuintes/DFe/%d?cnpjConsulta=%s&lote=true" % (nsu, cnpj))
        lote = transmissao._pegar(r.json, "LoteDFe") or [] if r.json else []
        if r.status not in (200, 404) or not lote:
            if r.status not in (200, 404):
                print("Resposta HTTP", r.status, r.texto(400))
            break
        for d in lote:
            n = int(transmissao._pegar(d, "NSU"))
            xml = gzip.decompress(base64.b64decode(transmissao._pegar(d, "ArquivoXml")))
            nome = "%06d_%s.xml" % (n, transmissao._pegar(d, "ChaveAcesso") or transmissao._pegar(d, "TipoDocumento"))
            with open(_longo(os.path.join(pxml, nome)), "wb") as f:
                f.write(xml)
            try:
                nt = ler_nota(xml)
            except etree.XMLSyntaxError:
                nt = None
            if nt and nt["emitente"] == cnpj:
                notas.append(nt)
                if "--pdf" in args:
                    with open(_longo(os.path.join(saida, "NFSe %s - %s.pdf" % (nt["numero"], nt["tomador"][:60]))), "wb") as f:
                        f.write(danfse.gerar_pdf(xml))
            nsu = max(nsu, n)
    notas.sort(key=lambda x: (x["competencia"], int(x["numero"] or 0)))
    if notas:
        with open(_longo(os.path.join(saida, "indice_notas.csv")), "w", newline="", encoding="utf-8-sig") as f:
            w = csv.DictWriter(f, fieldnames=list(notas[0].keys()), delimiter=";")
            w.writeheader(); w.writerows(notas)
    series = {}
    for x in notas:
        series[x["serie"]] = max(series.get(x["serie"], 0), int(x["dps"] or 0))
    print("NFS-e do CNPJ:", len(notas), "| última DPS usada por série:", series)
    print("Índice:", os.path.join(saida, "indice_notas.csv"))
    return 0


def cmd_por_chave(args):
    thumb, saida = _arg(args, "--thumb"), _arg(args, "--saida", ".")
    chaves = [a for a in args if a.isdigit() and len(a) == 50]
    if not (thumb and chaves):
        print(__doc__); return 2
    os.makedirs(_longo(saida), exist_ok=True)
    cli = _cliente(thumb)
    for ch in chaves:
        xml, r = cli.consultar_nfse(ch)
        if not xml:
            print(ch, "-> HTTP", r.status, r.texto(300)); continue
        nt = ler_nota(xml)
        base = os.path.join(saida, "NFSe %s - %s" % (nt["numero"], nt["tomador"][:60]))
        with open(_longo(base + ".xml"), "wb") as f:
            f.write(xml)
        with open(_longo(base + ".pdf"), "wb") as f:
            f.write(cli.baixar_danfse(ch) or danfse.gerar_pdf(xml))
        print(ch, "-> NFS-e", nt["numero"], nt["tomador"], "R$", nt["valor"])
    return 0


def cmd_pdf(args):
    if not args:
        print(__doc__); return 2
    alvo = args[0]
    arqs = [os.path.join(alvo, a) for a in os.listdir(_longo(alvo)) if a.lower().endswith(".xml")] if os.path.isdir(_longo(alvo)) else [alvo]
    for a in arqs:
        with open(_longo(a), "rb") as f:
            xml = f.read()
        try:
            pdf = danfse.gerar_pdf(xml)
        except Exception as e:
            print(a, "-> não é NFS-e (%s)" % e); continue
        with open(_longo(os.path.splitext(a)[0] + ".pdf"), "wb") as f:
            f.write(pdf)
        print(os.path.basename(a), "-> PDF gerado")
    return 0


def main():
    args = sys.argv[1:]
    cmds = {"certificados": cmd_certificados, "notas-emitidas": cmd_notas_emitidas, "por-chave": cmd_por_chave, "pdf": cmd_pdf}
    if not args or args[0] not in cmds:
        print(__doc__); return 2
    return cmds[args[0]](args[1:]) or 0


if __name__ == "__main__":
    sys.exit(main())
