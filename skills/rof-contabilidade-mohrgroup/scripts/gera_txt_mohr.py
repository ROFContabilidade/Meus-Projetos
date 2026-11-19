#!/usr/bin/env python3
"""MOHR GROUP (1005) — CSV classificado (3 bancos) -> TXT Domínio único + planilha de retiradas dos sócios.

Uso:
  python gera_txt_mohr.py classificado.csv --empresa ../references/empresa.json --competencia MM/AAAA \
      --saldos "6=ini:fim;8=ini:fim;9=ini:fim" -o MOHR_MM_AAAA.txt [--previa]

CSV (separador ;, UTF-8): data;banco;descricao;valor;conta[;partidas][;status]
  valor    com sinal (entrada +, saída -), vírgula ou ponto decimal
  banco    conta contábil do banco (6, 8 ou 9)
  conta    contrapartida. Especiais:
             SOCIO:E / SOCIO:S  pagamento a Emerson / Sueli -> 188 até o líquido do pró-labore, excedente 539/548
             IGNORAR            aplicação/resgate Auto Mais (fora do TXT; o saldo avisa se não zerar)
             6 / 8 / 9          transferência própria: lançada só pela saída (D destino / C origem)
  partidas várias contrapartidas no mesmo movimento: "479=500,00+372=12,30" (soma = valor) -> lote C/D
  status   CONFIRMADO ou PROVÁVEL entram; qualquer outro bloqueia (salvo --previa)

Regras: um movimento do banco = um lançamento; mais de uma contrapartida -> |6000|C| (saída) ou |6000|D| (entrada).
O TXT só é gravado se o saldo de cada banco fechar (extrato e efeito do TXT). Histórico = texto do extrato.
Saídas extras: retiradas_socios_AAAAMM_mohrgroup.xlsx e <saida>_visao_socios.txt (para planilha_socios.py / planilha_socio_mes.py
do cérebro: 188 vira 188E/188S para separar os sócios; NÃO importar este arquivo no Domínio).
"""
import argparse, csv, json, re, sys
from collections import defaultdict
from datetime import datetime
from decimal import Decimal, ROUND_HALF_UP

BANCOS = {"6", "8", "9"}
OK = {"CONFIRMADO", "PROVÁVEL", "PROVAVEL", ""}


def dec(s):
    s = str(s or "0").strip().replace("R$", "").replace(" ", "")
    if "," in s:
        s = s.replace(".", "").replace(",", ".")
    return Decimal(s)


def brl(v):
    return f"{abs(v):.2f}".replace(".", ",")


def limpa(t):
    return re.sub(r"\s+", " ", str(t or "").replace("|", "/")).strip()


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("csv")
    ap.add_argument("--empresa", required=True)
    ap.add_argument("--competencia", required=True)
    ap.add_argument("--saldos", required=True, help='"6=ini:fim;8=ini:fim;9=ini:fim"')
    ap.add_argument("-o", "--saida", required=True)
    ap.add_argument("--previa", action="store_true", help="grava mesmo com pendência (TXT marcado PREVIA)")
    a = ap.parse_args()

    emp = json.load(open(a.empresa, encoding="utf-8"))
    cnpj = re.sub(r"\D", "", emp["cnpj"])
    socios = {s["chave"]: s for s in emp["socios"]}
    liq = Decimal(str(emp["pro_labore"]["liquido"]))
    saldos = {}
    for p in a.saldos.split(";"):
        b, v = p.split("=")
        i, f = v.split(":")
        saldos[b.strip()] = (dec(i), dec(f))

    linhas = list(csv.DictReader(open(a.csv, encoding="utf-8-sig"), delimiter=";"))
    for n, l in enumerate(linhas):
        l["_n"], l["_v"] = n, dec(l["valor"])
        l["_d"] = datetime.strptime(l["data"].strip(), "%d/%m/%Y")
        l["conta"] = (l.get("conta") or "").strip().upper()
    linhas.sort(key=lambda l: (l["_d"], l["_n"]))

    erros, avisos = [], []
    lotes = []                      # (data, tipo, [(deb, cred, valor, hist)])
    efeito = defaultdict(Decimal)   # efeito do TXT em cada banco
    extrato = defaultdict(Decimal)
    ignorado = defaultdict(Decimal)
    usado = defaultdict(Decimal)    # pró-labore já coberto por sócio
    mov_socio = []                  # (chave, data, hist, valor, conta, banco)

    for l in linhas:
        b, v, c, d = l["banco"].strip(), l["_v"], l["conta"], l["data"].strip()
        h = limpa(l["descricao"])
        extrato[b] += v
        st = (l.get("status") or "").strip().upper()
        if st not in OK:
            erros.append(f"{d} {brl(v)} {h[:50]}: status {st}")
        if b not in BANCOS:
            erros.append(f"{d} {h[:50]}: banco '{b}' inválido")
            continue
        if v == 0:
            continue
        if c == "IGNORAR":
            ignorado[b] += v
            continue
        partidas = (l.get("partidas") or "").strip()
        if c.startswith("SOCIO:"):
            k = c.split(":")[1]
            s = socios.get(k)
            if not s or v > 0:
                erros.append(f"{d} {h[:50]}: SOCIO só para saída e chave E/S")
                continue
            tot = -v
            pl = min(tot, max(liq - usado[k], Decimal(0)))
            usado[k] += pl
            ret = tot - pl
            parts = [(s["conta_pro_labore"], pl), (s["conta_socio"], ret)]
            parts = [(ct, x) for ct, x in parts if x > 0]
            for ct, x in parts:
                mov_socio.append((k, d, h, x, ct, b))
        elif partidas:
            parts = []
            for p in partidas.split("+"):
                ct, x = p.split("=")
                parts.append((ct.strip(), dec(x)))
            if sum(x for _, x in parts) != abs(v):
                erros.append(f"{d} {brl(v)} {h[:50]}: partidas somam {brl(sum(x for _, x in parts))}")
                continue
        elif not c:
            erros.append(f"{d} {brl(v)} {h[:50]}: sem conta")
            continue
        else:
            if c in BANCOS:  # transferência própria
                if v > 0:
                    par = [o for o in linhas if o["banco"].strip() == c and o["conta"] == b and o["_v"] == -v
                           and abs((o["_d"] - l["_d"]).days) <= 3]
                    if not par:
                        erros.append(f"{d} {brl(v)} {h[:50]}: entrada de transferência sem a saída no banco {c}")
                    continue
                par = [o for o in linhas if o["banco"].strip() == c and o["conta"] == b and o["_v"] == -v
                       and abs((o["_d"] - l["_d"]).days) <= 3]
                if not par:
                    avisos.append(f"{d} {brl(v)} {h[:50]}: transferência para o banco {c} sem a entrada no extrato dele")
            parts = [(c, abs(v))]
        if len(parts) == 1:
            ct, x = parts[0]
            if v < 0:
                lotes.append((d, "X", [(ct, b, x, h)]))
            else:
                lotes.append((d, "X", [(b, ct, x, h)]))
        elif v < 0:
            lotes.append((d, "C", [("", b, -v, h)] + [(ct, "", x, h) for ct, x in parts]))
        else:
            lotes.append((d, "D", [(b, "", v, h)] + [("", ct, x, h) for ct, x in parts]))
        for deb, cred, x, _ in lotes[-1][2]:
            if deb in BANCOS:
                efeito[deb] += x
            if cred in BANCOS:
                efeito[cred] -= x

    print("Conferência de saldo por banco:")
    for b in sorted(set(saldos) | set(extrato)):
        if b not in saldos:
            erros.append(f"banco {b}: saldo inicial/final não informado")
            continue
        i, f = saldos[b]
        dif_ext = i + extrato[b] - f
        dif_txt = i + efeito[b] - f
        print(f"  {b}: ini {i:.2f} | extrato {i + extrato[b]:.2f} | TXT {i + efeito[b]:.2f} | final {f:.2f}"
              f" | dif extrato {dif_ext:.2f} | dif TXT {dif_txt:.2f}")
        if dif_ext:
            erros.append(f"banco {b}: extrato não fecha ({dif_ext:.2f}) — falta ou sobra movimento no CSV")
        if dif_txt and not dif_ext:
            msg = f"banco {b}: TXT não fecha ({dif_txt:.2f})"
            if ignorado[b]:
                msg += f"; Auto Mais ignorada não zerou ({ignorado[b]:.2f}) — lançar o líquido na conta 11"
            erros.append(msg)

    for k, s in socios.items():
        if usado[k] < liq:
            avisos.append(f"{s['nome']}: pró-labore pago {brl(usado[k])} < líquido {brl(liq)} — 188 fica em aberto")

    for t in avisos:
        print("AVISO:", t)
    if erros:
        print("\nPENDÊNCIAS:")
        for t in erros:
            print("  -", t)
        if not a.previa:
            sys.exit("TXT NÃO gravado. Resolva as pendências (ou use --previa para conferência).")

    lotes.sort(key=lambda x: datetime.strptime(x[0], "%d/%m/%Y"))
    out = [f"|0000|{cnpj}|"]
    visao = list(out)
    for d, tipo, ps in lotes:
        out.append(f"|6000|{tipo}||||")
        for deb, cred, x, h in ps:
            out.append(f"|6100|{d}|{deb}|{cred}|{brl(x)}||{h}||||")
    # visão para as planilhas do cérebro: cada parte do sócio como D conta / C banco (188 -> 188E/188S)
    for k, d, h, x, ct, bnk in mov_socio:
        ct2 = f"188{k}" if ct == "188" else ct
        visao.append("|6000|X||||")
        visao.append(f"|6100|{d}|{ct2}|{bnk}|{brl(x)}||{h}||||")
    for l in linhas:
        if l["conta"] in ("539", "548") and l["_v"] > 0:
            visao.append("|6000|X||||")
            visao.append(f"|6100|{l['data'].strip()}|{l['banco'].strip()}|{l['conta']}|{brl(l['_v'])}||{limpa(l['descricao'])}||||")
    saida = a.saida if not erros else a.saida.replace(".txt", "_PREVIA.txt")
    open(saida, "w", encoding="cp1252", errors="replace", newline="").write("\r\n".join(out) + "\r\n")
    base = saida.rsplit(".", 1)[0]
    open(base + "_visao_socios.txt", "w", encoding="cp1252", errors="replace", newline="").write("\r\n".join(visao) + "\r\n")
    import os
    mm, aa = a.competencia.split("/")
    xlsx = os.path.join(os.path.dirname(saida) or ".", f"retiradas_socios_{aa}{mm}_mohrgroup.xlsx")
    planilha(xlsx, emp, a.competencia, socios, liq, mov_socio, linhas)
    print(f"\nTXT: {saida} ({len(lotes)} lançamentos; lotes C/D: {sum(1 for x in lotes if x[1] != 'X')})")
    print(f"Planilha: {xlsx} | visão sócios: {base}_visao_socios.txt")


def planilha(caminho, emp, comp, socios, liq, movs, linhas):
    from openpyxl import Workbook
    from openpyxl.styles import Font, PatternFill
    neg, azul = Font(bold=True), PatternFill("solid", fgColor="DDEBF7")
    sm = Decimal(str(emp["pro_labore"]["salario_minimo_2026"]))
    inss = (sm * Decimal(emp["pro_labore"]["inss_pct"]) / 100).quantize(Decimal("0.01"), ROUND_HALF_UP)
    wb = Workbook()
    ws = wb.active
    ws.title = "Parâmetros"
    for r in [["RETIRADAS DOS SÓCIOS — " + emp["razao_social"]], [f"CNPJ {emp['cnpj']} · Domínio {emp['codigo_dominio']} · Competência {comp}"], [],
              ["Salário mínimo vigente", float(sm)], ["INSS 11%", float(inss)], ["Pró-labore líquido", float(liq)]]:
        ws.append(r)
    ws["A1"].font = neg
    resumo = []
    for k, s in socios.items():
        sh = wb.create_sheet(s["nome"].split()[0].title())
        sh.append([f"{s['nome']} — CPF {s['cpf']}"])
        sh["A1"].font = neg
        sh.append(["Data", "Histórico", "Débito", "Crédito (banco)", "Valor", "Tipo"])
        for c in sh[2]:
            c.font, c.fill = neg, azul
        pl = ret = dev = Decimal(0)
        for kk, d, h, x, ct, bnk in movs:
            if kk != k:
                continue
            tipo = "Pró-labore" if ct == "188" else "Retirada"
            sh.append([d, h, ct, bnk, float(x), tipo])
            if ct == "188":
                pl += x
            else:
                ret += x
        for l in linhas:
            if l["conta"] == s["conta_socio"] and l["_v"] > 0:
                sh.append([l["data"].strip(), limpa(l["descricao"]), l["banco"].strip(), s["conta_socio"], float(-l["_v"]), "Devolução / aporte"])
                dev += l["_v"]
        sh.append([])
        sh.append(["", "Pró-labore reconhecido (188)", "", "", float(pl)])
        sh.append(["", f"Retiradas ({s['conta_socio']})", "", "", float(ret)])
        sh.append(["", "Devoluções / aportes", "", "", float(dev)])
        sh.append(["", "INSS a recolher (191)", "", "", float(inss)])
        if pl < liq:
            sh.append(["", "Pró-labore em aberto na 188", "", "", float(liq - pl)])
        sh.column_dimensions["B"].width = 60
        resumo.append([s["nome"], float(pl), float(ret), float(dev), float(ret - dev), float(inss)])
    r = wb.create_sheet("Resumo", 1)
    r.append(["Sócio", "Pró-labore (188)", "Retiradas", "Devoluções", "Retirada líquida", "INSS (191)"])
    for c in r[1]:
        c.font, c.fill = neg, azul
    for x in resumo:
        r.append(x)
    r.append(["TOTAL"] + [sum(x[i] for x in resumo) for i in range(1, 6)])
    r.column_dimensions["A"].width = 28
    o = wb.create_sheet("Observações")
    for t in [f"Pró-labore = 1 salário mínimo nacional (R$ {brl(sm)} em 2026) por sócio; INSS 11% retido (Lei 8.212/91, art. 21 e 30, §4º).",
              "Ordem de cobertura: em ordem de data nos 3 bancos, cada pagamento ao sócio cobre primeiro o pró-labore líquido (188); o excedente é retirada (539 Emerson / 548 Sueli).",
              "PIX que cruza o limite = um único lançamento em lote C (188 + 539/548), decisão Rosangela/Elen 13/11/2026.",
              "Retirada acima do pró-labore é antecipação de lucros: compensar com lucros apurados no fechamento; acima de R$ 50 mil/mês por sócio, ver Lei 15.270/2025.",
              "Simples Nacional Anexo I: CPP patronal está no DAS; só o INSS do sócio (11%) vai para a 191."]:
        o.append([t])
    o.column_dimensions["A"].width = 140
    wb.save(caminho)


if __name__ == "__main__":
    main()
