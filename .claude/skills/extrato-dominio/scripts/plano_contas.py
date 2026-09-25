#!/usr/bin/env python3
"""Converte o plano de contas exportado do Domínio (.xls ou .csv) em JSON {codigo_reduzido: nome}.

O .xls que o Domínio exporta às vezes tem offsets internos inconsistentes, e o xlrd e o
LibreOffice recusam abrir. Por isso há aqui um leitor BIFF8 mínimo e tolerante.
Requer: pip install olefile (só para .xls).

Uso: python plano_contas.py Contas.xls -o contas.json [--todas]
     (--todas inclui as contas sintéticas "S"; por padrão só analíticas, que recebem lançamento)
"""
import argparse, csv, json, re, struct, sys
from collections import defaultdict

def ler_xls(caminho):
    import olefile
    d = olefile.OleFileIO(caminho).openstream('Workbook').read()
    recs = []; i = 0
    while i + 4 <= len(d):
        t, l = struct.unpack_from('<HH', d, i); recs.append((t, d[i+4:i+4+l])); i += 4 + l
    # SST com CONTINUE
    sst = []
    for k, (t, b) in enumerate(recs):
        if t != 0x00FC: continue
        chunks = [b]; j = k + 1
        while j < len(recs) and recs[j][0] == 0x003C: chunks.append(recs[j][1]); j += 1
        ci, off = 0, 8; total = struct.unpack_from('<I', b, 4)[0]
        def need(n):
            nonlocal ci, off
            if off + n > len(chunks[ci]) and off >= len(chunks[ci]): ci += 1; off = 0
        for _ in range(total):
            need(3)
            c = chunks[ci]; n = struct.unpack_from('<H', c, off)[0]; fl = c[off+2]; off += 3
            rt = sz = 0
            if fl & 8: rt = struct.unpack_from('<H', chunks[ci], off)[0]; off += 2
            if fl & 4: sz = struct.unpack_from('<I', chunks[ci], off)[0]; off += 4
            s = ''; wide = fl & 1; rest = n
            while rest:
                c = chunks[ci]
                if off >= len(c): ci += 1; off = 0; c = chunks[ci]; wide = c[0] & 1; off = 1
                w = 2 if wide else 1
                take = min(rest, (len(c) - off) // w)
                seg = c[off:off+take*w]
                s += seg.decode('utf-16-le' if wide else 'latin-1'); off += take*w; rest -= take
            off += 4*rt + sz
            while ci < len(chunks) and off > len(chunks[ci]): off -= len(chunks[ci]); ci += 1
            sst.append(s)
        break
    def rk(v):
        if v & 2: x = struct.unpack('<i', struct.pack('<I', v))[0] >> 2
        else: x = struct.unpack('<d', struct.pack('<Q', (v & 0xFFFFFFFC) << 32))[0]
        return x / 100 if v & 1 else x
    # cada aba começa com um registro BOF (0x0809); o primeiro BOF é o bloco global do arquivo
    nomes, abas, cells, bofs = [], [], None, 0
    for t, b in recs:
        if t == 0x0085:  # BOUNDSHEET: nome da aba
            n, fl = b[6], b[7]
            nomes.append(b[8:8 + 2 * n].decode('utf-16-le') if fl & 1 else b[8:8 + n].decode('latin-1'))
        elif t == 0x0809:
            bofs += 1
            if bofs > 1:
                cells = defaultdict(dict)
                abas.append((nomes[len(abas)] if len(abas) < len(nomes) else f"Aba{len(abas) + 1}", cells))
        elif cells is None:
            continue
        elif t == 0x00FD:
            r, c, _, k = struct.unpack_from('<HHHI', b); cells[r][c] = sst[k]
        elif t == 0x0203:
            r, c, _ = struct.unpack_from('<HHH', b); cells[r][c] = struct.unpack_from('<d', b, 6)[0]
        elif t == 0x027E:
            r, c, _, v = struct.unpack_from('<HHHI', b); cells[r][c] = rk(v)
        elif t == 0x00BD:  # MULRK: várias células numéricas na mesma linha
            r, c0 = struct.unpack_from('<HH', b)
            for i in range((len(b) - 6) // 6):
                cells[r][c0 + i] = rk(struct.unpack_from('<I', b, 4 + 6 * i + 2)[0])
        elif t == 0x0204:
            r, c, _, n = struct.unpack_from('<HHHH', b); fl = b[8]
            cells[r][c] = b[9:9+2*n].decode('utf-16-le') if fl & 1 else b[9:9+n].decode('latin-1')
    return abas


def linhas_planilha(caminho):
    if caminho.lower().endswith(".xls"):
        try:
            import olefile  # noqa: F401
        except ImportError:
            raise SystemExit("Instale o olefile: pip install olefile")
        for nome, cells in ler_xls(caminho):
            yield ["#ABA", nome]
            for r in sorted(cells):
                mx = max(cells[r])
                yield [(str(int(x)) if isinstance(x, float) and x.is_integer() else str(x)).strip()
                       for x in (cells[r].get(c, "") for c in range(mx + 1))]
    else:
        with open(caminho, encoding="utf-8-sig", errors="replace") as f:
            for row in csv.reader(f, delimiter=";"):
                yield [c.strip() for c in row]


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("arquivo")
    p.add_argument("-o", "--saida", default="contas.json")
    p.add_argument("--todas", action="store_true")
    a = p.parse_args()
    contas = {}
    for row in linhas_planilha(a.arquivo):
        if not row or not row[0].isdigit():
            continue
        classif = next((c for c in row[1:] if re.fullmatch(r"\d+(\.\d+)*", c)), "")
        sintetica = "S" in row[1:5]
        textos = [c for c in row[1:] if c and c != "S" and c != classif and not re.fullmatch(r"[\d.,]+", c)]
        if not textos or (sintetica and not a.todas):
            continue
        contas[row[0]] = f"{classif} {textos[0]}".strip()
    with open(a.saida, "w", encoding="utf-8") as f:
        json.dump(contas, f, ensure_ascii=False, indent=1)
    print(f"{len(contas)} contas gravadas em {a.saida}")


if __name__ == "__main__":
    main()
