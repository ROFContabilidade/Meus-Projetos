"""Leitura dos arquivos da pasta de entrada: XML NF-e/NFC-e, PDF (PGDAS-D e outros), OFX, planilhas (PDV, ficha)."""
import os, re, zipfile, tempfile, subprocess, csv
import xml.etree.ElementTree as ET

NS = "{http://www.portalfiscal.inf.br/nfe}"


def _num(s):
    try:
        return float(s)
    except (TypeError, ValueError):
        return 0.0


def br_num(s):
    """'1.234.567,89' -> 1234567.89"""
    s = s.strip().replace("R$", "").replace(" ", "")
    if "," in s:
        s = s.replace(".", "").replace(",", ".")
    try:
        return float(s)
    except ValueError:
        return None


def inventario(pasta):
    """Lista todos os arquivos (abre ZIPs numa pasta temporária)."""
    arquivos = []
    for raiz, _, nomes in os.walk(pasta):
        for n in nomes:
            p = os.path.join(raiz, n)
            if n.lower().endswith(".zip"):
                destino = tempfile.mkdtemp(prefix="zip_")
                try:
                    with zipfile.ZipFile(p) as z:
                        for m in z.namelist():
                            if ".." in m or m.startswith("/"):
                                continue
                            z.extract(m, destino)
                    arquivos += inventario(destino)
                except zipfile.BadZipFile:
                    arquivos.append(p)
            else:
                arquivos.append(p)
    return arquivos


# ---------------------------------------------------------------- NF-e / NFC-e
def ler_xml(caminho):
    """Retorna ('nfe', dict) | ('evento', dict) | (None, None)."""
    try:
        root = ET.parse(caminho).getroot()
    except ET.ParseError:
        return None, None
    tag = root.tag.replace(NS, "")
    if tag in ("procEventoNFe", "evento", "envEvento"):
        tp = root.find(f".//{NS}tpEvento")
        ch = root.find(f".//{NS}chNFe")
        if tp is not None and ch is not None:
            return "evento", {"tipo": tp.text, "chave": ch.text}
        return None, None
    inf = root.find(f".//{NS}infNFe")
    if inf is None:
        return None, None
    g = lambda base, path: (base.find(path).text if base is not None and base.find(path) is not None else "")
    ide, emit, dest = inf.find(f"{NS}ide"), inf.find(f"{NS}emit"), inf.find(f"{NS}dest")
    nota = {
        "arquivo": os.path.basename(caminho),
        "chave": (inf.get("Id") or "").replace("NFe", ""),
        "modelo": g(ide, f"{NS}mod"),
        "data": g(ide, f"{NS}dhEmi")[:10] or g(ide, f"{NS}dEmi")[:10],
        "tpNF": g(ide, f"{NS}tpNF"),
        "emit_doc": g(emit, f"{NS}CNPJ") or g(emit, f"{NS}CPF"),
        "emit_pf": bool(g(emit, f"{NS}CPF")) and not g(emit, f"{NS}CNPJ"),
        "emit_nome": g(emit, f"{NS}xNome"),
        "emit_uf": g(emit, f"{NS}enderEmit/{NS}UF"),
        "emit_crt": g(emit, f"{NS}CRT"),
        "dest_doc": g(dest, f"{NS}CNPJ") or g(dest, f"{NS}CPF"),
        "dest_pj": bool(g(dest, f"{NS}CNPJ")),
        "itens": [],
    }
    for det in inf.findall(f"{NS}det"):
        prod, imp = det.find(f"{NS}prod"), det.find(f"{NS}imposto")
        vicms = 0.0
        if imp is not None:
            for el in imp.iter():
                if el.tag == f"{NS}vICMS":
                    vicms += _num(el.text)
        nota["itens"].append({
            "ncm": g(prod, f"{NS}NCM"), "cfop": g(prod, f"{NS}CFOP"), "desc": g(prod, f"{NS}xProd"),
            "valor": _num(g(prod, f"{NS}vProd")) - _num(g(prod, f"{NS}vDesc")),
            "vicms": vicms,
        })
    return "nfe", nota


# ---------------------------------------------------------------- PDF
def texto_pdf(caminho):
    try:
        return subprocess.run(["pdftotext", "-layout", caminho, "-"], capture_output=True, text=True, timeout=60).stdout
    except Exception:
        return ""


NUM = r"([\d\.]+,\d{2})"


def ler_pgdas(texto):
    """Extrai PA, receita do PA (RPA) e RBT12 de um extrato/declaração do PGDAS-D."""
    if not re.search(r"PGDAS|Simples Nacional|RBT12", texto, re.I):
        return None
    pa = re.search(r"Per[ií]odo de Apura[cç][aã]o(?: \(PA\))?:?\s*(\d{2}/\d{4})", texto, re.I)
    rpa = re.search(r"Receita Bruta do PA \(RPA\)[^\d]*" + NUM, texto, re.I)
    rbt = re.search(r"\(RBT12\)[^\d]*" + NUM, texto, re.I)
    total = re.search(r"Total (?:do D[eé]bito Exig[ií]vel|Geral da Empresa)[^\d]*" + NUM, texto, re.I)
    cnpj = re.search(r"CNPJ(?: B[aá]sico| Matriz)?:?\s*([\d\./-]{8,18})", texto)
    if not (pa or rpa or rbt):
        return None
    return {
        "pa": pa.group(1) if pa else None,
        "rpa": br_num(rpa.group(1)) if rpa else None,
        "rbt12": br_num(rbt.group(1)) if rbt else None,
        "das": br_num(total.group(1)) if total else None,
        "cnpj": re.sub(r"\D", "", cnpj.group(1)) if cnpj else None,
    }


# ---------------------------------------------------------------- OFX
def ler_ofx(caminho):
    txt = open(caminho, encoding="latin-1", errors="ignore").read()
    cred = deb = 0.0
    datas = []
    for bloco in re.findall(r"<STMTTRN>(.*?)</STMTTRN>", txt, re.S | re.I) or re.split(r"<STMTTRN>", txt, flags=re.I)[1:]:
        v = re.search(r"<TRNAMT>\s*([-\d\.,]+)", bloco, re.I)
        d = re.search(r"<DTPOSTED>\s*(\d{8})", bloco, re.I)
        if not v:
            continue
        val = float(v.group(1).replace(",", "."))
        if val >= 0:
            cred += val
        else:
            deb += -val
        if d:
            datas.append(d.group(1))
    return {"creditos": cred, "debitos": deb, "meses": sorted({x[:6] for x in datas})}


# ---------------------------------------------------------------- Planilhas
def linhas_planilha(caminho):
    """Retorna lista de linhas (listas de valores) de xlsx/xls/csv."""
    ext = caminho.lower().rsplit(".", 1)[-1]
    if ext == "csv":
        raw = open(caminho, encoding="utf-8-sig", errors="ignore").read()
        sep = ";" if raw.count(";") > raw.count(",") else ","
        return [r for r in csv.reader(raw.splitlines(), delimiter=sep)]
    if ext in ("xlsx", "xlsm"):
        from openpyxl import load_workbook
        wb = load_workbook(caminho, data_only=True, read_only=True)
        out = []
        for ws in wb.worksheets:
            out += [list(r) for r in ws.iter_rows(values_only=True)]
        return out
    if ext == "xls":
        try:
            import pandas as pd
            out = []
            for _, df in pd.read_excel(caminho, sheet_name=None, header=None).items():
                out += df.values.tolist()
            return out
        except Exception:
            return []
    return []


def ler_ficha(caminho):
    """FICHA_ESTUDO.xlsx: coluna A = campo, coluna B = valor."""
    ficha = {}
    for r in linhas_planilha(caminho):
        if r and r[0] and len(r) > 1 and r[1] not in (None, ""):
            ficha[str(r[0]).strip()] = r[1]
    return ficha


def ler_pdv(caminho):
    """Relatório de vendas por produto: procura colunas de descrição e valor total."""
    linhas = linhas_planilha(caminho)
    for i, r in enumerate(linhas[:30]):
        cab = [str(c or "").strip().lower() for c in r]
        idesc = next((j for j, c in enumerate(cab) if any(k in c for k in ("produto", "descri", "item"))), None)
        ival = next((j for j, c in enumerate(cab) if any(k in c for k in ("valor total", "total", "vlr", "valor", "faturamento"))), None)
        incm = next((j for j, c in enumerate(cab) if "ncm" in c), None)
        if idesc is not None and ival is not None and idesc != ival:
            itens = []
            for row in linhas[i + 1:]:
                if len(row) <= max(idesc, ival) or row[idesc] in (None, ""):
                    continue
                v = row[ival]
                if isinstance(v, str):
                    v = br_num(v)
                if not isinstance(v, (int, float)) or v <= 0:
                    continue
                desc = str(row[idesc])
                if desc.strip().lower().startswith("total"):
                    continue
                ncm = str(row[incm]).replace(".", "") if incm is not None and len(row) > incm and row[incm] else ""
                itens.append({"desc": desc, "valor": float(v), "ncm": ncm})
            if itens:
                return itens
    return None
