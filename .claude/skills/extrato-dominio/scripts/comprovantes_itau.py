#!/usr/bin/env python3
"""Comprovantes de pagamento do Itaú (PDF ou texto) → favorecido de cada pagamento do extrato.

  ler      python comprovantes_itau.py ler Comprovante*.pdf [texto.txt] -o trabalho/comprovantes.csv
           Uma linha por comprovante: tipo (boleto, PIX, QR Code, tributo), data, valor pago, favorecido,
           CPF/CNPJ, valor original, desconto, juros/multa.
  aplicar  python comprovantes_itau.py aplicar trabalho/normalizado.csv -c trabalho/comprovantes.csv \
               -o trabalho/normalizado_nomes.csv
           Casa cada saída do extrato com um comprovante (mesma data e mesmo valor) e reescreve a descrição
           como "SISPAG FORNECEDORES <FAVORECIDO>" (ou "BOLETO PAGO"/"PIX ENVIADO"), para as regras do
           razão modelo reconhecerem o favorecido. Guarda CNPJ e juros no campo documento.

Requer pdfplumber (ou pypdf) para PDF. O texto também pode vir do Google Drive (read_file_content).
"""
import argparse
import csv
import os
import re
import sys
from collections import defaultdict

CAMPOS = ["tipo", "data", "valor", "favorecido", "cpf_cnpj", "valor_documento", "desconto", "juros_multa", "arquivo"]
V = r"([\d.]+,\d{2})"
D = r"(\d{2}/\d{2}/\d{4})"
DOC = r"(\d{2}\.\d{3}\.\d{3}/\d{4}-\d{2}|[\d*.\\/-]{11,20})"


def num(v):
    return round(float(str(v or "0").replace(".", "").replace(",", ".")), 2)


def texto_arquivo(caminho):
    if caminho.lower().endswith(".pdf"):
        try:
            import pdfplumber
            with pdfplumber.open(caminho) as pdf:
                return "\n".join(p.extract_text() or "" for p in pdf.pages)
        except ImportError:
            from pypdf import PdfReader
            return "\n".join(p.extract_text() or "" for p in PdfReader(caminho).pages)
    with open(caminho, encoding="utf-8", errors="replace") as f:
        return f.read()


def extrair(texto, arquivo=""):
    t = re.sub(r"\s+", " ", texto.replace("\\*", "*"))
    regs = []
    # boletos
    for m in re.finditer(r"Beneficiário: (.+?) CPF/CNPJ do beneficiário: .*?Razão Social: .*? " + DOC + r" " + D +
                         r" Valor do boleto \(R\$\); " + V + r" \(-\) Desconto \(R\$\): " + V +
                         r" \(\+\) ?Mora/Multa \(R\$\): " + V + r".{0,160}?\(=\) Valor do pagamento \(R\$\):.{0,120}?"
                         r"\d{2}\.\d{3}\.\d{3}/\d{4}-\d{2} " + V + r".{0,200}?Data de pagamento: ?.{0,120}?" + D, t):
        fav, doc, _venc, vdoc, desc, mora, vpag, dpag = m.groups()
        regs.append({"tipo": "boleto", "data": dpag, "valor": vpag, "favorecido": fav.strip(), "cpf_cnpj": doc,
                     "valor_documento": vdoc, "desconto": desc, "juros_multa": mora})
    # transferências PIX / TED
    for m in re.finditer(r"nome do recebedor: ([^:]{2,60}?) chave: [^:]{0,120}?CPF / CNPJ do recebedor: (\S+) "
                         r".{0,300}?valor: R\$ " + V + r" data da transferência: " + D +
                         r" tipo de pagamento: (.{2,40}?) mensagem", t):
        fav, doc, v, d, tp = m.groups()
        regs.append({"tipo": "PIX" if "PIX" in tp else tp.strip(), "data": d, "valor": v, "favorecido": fav.strip(),
                     "cpf_cnpj": doc, "valor_documento": v, "desconto": "0,00", "juros_multa": "0,00"})
    # PIX QR Code
    for m in re.finditer(r"Comprovante de pagamento QR Code .*?nome do recebedor: (.+?) CPF / CNPJ do recebedor: (\S+)"
                         r".*?desconto: " + V + r".*?juros: " + V + r" multa: " + V + r" valor final: " + V +
                         r".*?Pagamento efetuado em " + D, t):
        fav, doc, desc, juros, multa, v, d = m.groups()
        regs.append({"tipo": "PIX QR Code", "data": d, "valor": v, "favorecido": fav.strip(), "cpf_cnpj": doc,
                     "valor_documento": v, "desconto": desc, "juros_multa": f"{num(juros) + num(multa):.2f}".replace(".", ",")})
    # tributos (municipais, estaduais, federais, concessionárias)
    for m in re.finditer(r"Comprovante de Pagamento (Tributos [A-Za-zçãõé ]+?|DARF[^ ]*|GPS|FGTS[^ ]*|Concessionárias?)"
                         r" .*?Valor do documento: R\$ " + V + r".*?efetuada em " + D, t):
        tp, v, d = m.groups()
        regs.append({"tipo": tp.strip(), "data": d, "valor": v, "favorecido": tp.strip().upper(), "cpf_cnpj": "",
                     "valor_documento": v, "desconto": "0,00", "juros_multa": "0,00"})
    for r in regs:
        r["arquivo"] = os.path.basename(arquivo)
    return regs


def cmd_ler(a):
    regs = []
    for f in a.arquivos:
        regs += extrair(texto_arquivo(f), f)
    # o mesmo comprovante pode aparecer em dois arquivos: remove repetidos
    unicos = {(r["tipo"], r["data"], r["valor"], r["favorecido"]): r for r in regs}
    regs = sorted(unicos.values(), key=lambda r: (r["data"][6:] + r["data"][3:5] + r["data"][:2], r["favorecido"]))
    with open(a.saida, "w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=CAMPOS, delimiter=";", extrasaction="ignore")
        w.writeheader()
        w.writerows(regs)
    tipos = defaultdict(int)
    for r in regs:
        tipos[r["tipo"]] += 1
    print(f"{len(regs)} comprovante(s) -> {a.saida} | " + ", ".join(f"{k}: {v}" for k, v in sorted(tipos.items())))
    print(f"Total pago: {sum(num(r['valor']) for r in regs):,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))


def cmd_aplicar(a):
    with open(a.comprovantes, encoding="utf-8-sig") as f:
        comps = list(csv.DictReader(f, delimiter=";"))
    with open(a.extrato, encoding="utf-8-sig") as f:
        extrato = list(csv.DictReader(f, delimiter=";"))
    livres = defaultdict(list)
    for c in comps:
        livres[(c["data"], num(c["valor"]))].append(c)
    usados = casados = 0
    sem = []
    for l in extrato:
        v = round(-float(l["valor"]), 2)
        if v <= 0:
            continue
        lista = livres.get((l["data"], v))
        if not lista:
            if re.search(r"SISPAG (FORNECEDORES|TRIBUTOS)|^REF A\.?$|^$", l["descricao"].strip()):
                sem.append(l)
            continue
        c = lista.pop(0)
        casados += 1
        prefixo = {"boleto": "BOLETO PAGO", "PIX": "PIX ENVIADO", "PIX QR Code": "PIX QR CODE"}.get(c["tipo"], "SISPAG")
        if c["tipo"].startswith(("Tributos", "DARF", "GPS", "FGTS")):
            prefixo = "SISPAG TRIBUTOS"
        l["descricao"] = f"{prefixo} {c['favorecido']}".strip()
        extras = [c["cpf_cnpj"]] if c["cpf_cnpj"] else []
        if num(c["juros_multa"]) > 0:
            extras.append(f"JUROS/MULTA {c['juros_multa']}")
        l["documento"] = " ".join(extras) or l.get("documento", "")
    for lista in livres.values():
        usados += len(lista)
    with open(a.saida, "w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(extrato[0].keys()), delimiter=";")
        w.writeheader()
        w.writerows(extrato)
    print(f"{casados} pagamento(s) identificados pelos comprovantes -> {a.saida}")
    print(f"Comprovantes sem pagamento no extrato: {usados}")
    print(f"Pagamentos SISPAG ainda sem comprovante: {len(sem)}")
    for l in sem[:40]:
        print(f"  {l['data']} {l['valor']:>12} {l['descricao'][:40]}")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("ler")
    s.add_argument("arquivos", nargs="+")
    s.add_argument("-o", "--saida", required=True)
    s = sub.add_parser("aplicar")
    s.add_argument("extrato")
    s.add_argument("-c", "--comprovantes", required=True)
    s.add_argument("-o", "--saida", required=True)
    a = ap.parse_args()
    return cmd_ler(a) if a.cmd == "ler" else cmd_aplicar(a)


if __name__ == "__main__":
    sys.exit(main())
