#!/usr/bin/env python3
"""Ótica Visoluz (empresa 34): extrato Sicredi normalizado -> classificado + TXT Domínio.

Uso:
  python classificar_visoluz.py --extrato norm07.csv --folha folha.csv --comp 07/2026 \
      --saida-csv classificado_07.csv --saida-txt 34_OTICA_VISOLUZ_2026-07.txt

- norm*.csv: saída do `extrato_dominio.py ler` do rof-analista (data;descricao;documento;valor;id).
- folha.csv: competencia;nome;cpf;tipo;adiantamento;liquido (gerado do Extrato Mensal da folha).
- Regras: references/regras.json (padrões -> conta, status e observação).
Status: PROVADO (documento), PROVAVEL (padrão/decisão), SEM PROVA (vai para perguntas).
"""
import argparse, csv, json, re, unicodedata
from decimal import Decimal
from pathlib import Path

AQUI = Path(__file__).resolve().parent
BANCO = "8"


def norm(s):
    s = unicodedata.normalize("NFKD", s or "")
    return re.sub(r"\s+", " ", "".join(c for c in s if not unicodedata.combining(c))).strip().upper()


def br(v):
    return f"{abs(v):.2f}".replace(".", ",")


def comp_anterior(comp):
    m, a = int(comp[:2]), int(comp[3:])
    m, a = (12, a - 1) if m == 1 else (m - 1, a)
    return f"{m:02d}/{a}"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--extrato", required=True)
    ap.add_argument("--folha", required=True)
    ap.add_argument("--comp", required=True, help="MM/AAAA do extrato")
    ap.add_argument("--regras", default=str(AQUI.parent / "references" / "regras.json"))
    ap.add_argument("--filial", help="extrato normalizado da filial 118 (Itaú 98896-9): gera os espelhos C 544 dos pagamentos feitos pela filial por conta da matriz")
    ap.add_argument("--saida-csv", required=True)
    ap.add_argument("--saida-txt", required=True)
    a = ap.parse_args()

    regras = json.loads(Path(a.regras).read_text(encoding="utf-8"))
    cnpj = regras["cnpj"]
    pl_liq = Decimal(regras["socia"]["pro_labore_liquido"])

    folha = list(csv.DictReader(open(a.folha, encoding="utf-8"), delimiter=";"))
    emp = {f["cpf"]: f["nome"] for f in folha if f["tipo"] == "empregado"}
    liq_ant = {(f["cpf"], Decimal(f["liquido"])) for f in folha
               if f["competencia"] == comp_anterior(a.comp) and f["tipo"] == "empregado"}
    adi_mes = {(f["cpf"], Decimal(f["adiantamento"])) for f in folha
               if f["competencia"] == a.comp and f["tipo"] == "empregado"}

    def classe_empregado(cpf, val, dia):
        if (cpf, val) in liq_ant:
            return "187", "PROVADO", f"Salário líquido {comp_anterior(a.comp)} (folha)"
        if (cpf, val) in adi_mes:
            return "5", "PROVADO", f"Adiantamento {a.comp} (folha lança D25/C5; banco zera o caixa)"
        if val >= 300 and 15 <= dia <= 25:
            return "5", "PROVAVEL", f"PIX na janela do adiantamento (dia 15-25) com valor diferente da folha {a.comp}"
        if val >= Decimal(regras["empregado_limite_salario"]):
            return "187", "PROVAVEL", "PIX a empregado sem par exato na folha: baixa de salários a pagar"
        return regras["empregado_pequeno_conta"], "PROVAVEL", "PIX pequeno a empregado: vale/alimentação"

    movs = list(csv.DictReader(open(a.extrato, encoding="utf-8-sig"), delimiter=";"))
    pl_pago = Decimal("0")
    saida = []
    for m in movs:
        v = Decimal(m["valor"])
        d = norm(m["descricao"])
        d_hist = re.sub(r"\s*/\s*[A-Z0-9_.]+$", "", d)
        cpf = (re.search(r"PIX (\d{11})\b", d) or [None, None])[1]
        partidas = None  # lista [(conta, valor)] para lote múltiplo
        conta, status, obs = None, "SEM PROVA", ""

        # 1) Empregados da folha (por CPF no PIX)
        if v < 0 and cpf in emp:
            conta, status, obs = classe_empregado(cpf, -v, int(m["data"][:2]))
        # 2) Sócia: pró-labore líquido primeiro (188), excedente 531
        elif cpf == regras["socia"]["cpf"]:
            if v < 0:
                falta = max(pl_liq - pl_pago, Decimal("0"))
                p188 = min(falta, -v)
                pl_pago += p188
                resto = -v - p188
                if p188 and resto:
                    partidas = [("188", p188), ("531", resto)]
                    conta, status, obs = "188+531", "PROVAVEL", "Pró-labore líquido + retirada (conta corrente da sócia)"
                elif p188:
                    conta, status, obs = "188", "PROVAVEL", "Pró-labore líquido"
                else:
                    conta, status, obs = "531", "PROVAVEL", "Retirada da sócia (conta corrente/adiantamento)"
            else:
                conta, status, obs = "531", "PROVAVEL", "Devolução/aporte da sócia"
        else:
            for r in regras["regras"]:
                if r.get("sinal") == "+" and v < 0 or r.get("sinal") == "-" and v > 0:
                    continue
                if any(p in d for p in r["contem"]):
                    conta, status, obs = r["conta"], r["status"], r.get("obs", "")
                    if "partidas" in r:  # ex.: boleto com nota + juros
                        base = Decimal(r["partidas"]["valor_nota"])
                        if abs(v) > base:
                            partidas = [(r["conta"], base), (r["partidas"]["conta_dif"], abs(v) - base)]
                    fixas = r.get("partidas_por_valor", {}).get(f"{abs(v):.2f}")
                    if fixas:  # guia com principal/multa/juros conhecidos (relatório de pagamentos)
                        partidas = [(c, Decimal(x)) for c, x in fixas]
                        conta = "+".join(c for c, _ in fixas)
                    if "rendimento" in r and abs(v) % 100:
                        partidas = [(r["conta"], abs(v) - abs(v) % 100), (r["rendimento"], abs(v) % 100)]
                    break
        if conta is None:
            conta, status, obs = (regras["padrao_entrada"] if v > 0 else regras["padrao_saida"]), "SEM PROVA", "Sem regra: confirmar"

        saida.append({**m, "conta": conta, "status": status, "obs": obs,
                      "historico": "REF. A " + d_hist[:150], "partidas": partidas})

    pendentes_filial = []
    if a.filial:
        for m in csv.DictReader(open(a.filial, encoding="utf-8-sig"), delimiter=";"):
            v = Decimal(m["valor"]); d = norm(m["descricao"])
            doc = re.sub(r"\D", "", m.get("documento") or "")
            conta = None
            if v < 0 and doc in emp:
                conta, status, obs = classe_empregado(doc, -v, int(m["data"][:2]))
            elif v < 0 and "METROCAR" in d:
                conta, status, obs = "530", "PROVAVEL", "Vale-transporte dos empregados da matriz pago pela filial"
            elif v < 0 and ("CEF MATRIZ" in d or "FGTS" in d):
                conta, status, obs = "192", "PROVAVEL", "FGTS da matriz pago pela filial (conferir competência no relatório de encargos)"
            elif v > 0 and doc == cnpj:
                pendentes_filial.append(m)
                continue
            if conta:
                saida.append({**m, "valor": str(v), "conta": conta, "status": status, "banco": "544",
                              "obs": "PAGO PELA FILIAL (Itaú 98896-9; na 118: D 152) - " + obs,
                              "historico": "REF. A PAGO PELA FILIAL 0002-74 - " + re.sub(r"\s*/\s*", " ", d)[:120], "partidas": None})
    saida.sort(key=lambda s: (s["data"][6:], s["data"][3:5], s["data"][:2]))

    with open(a.saida_csv, "w", newline="", encoding="utf-8-sig") as f:
        w = csv.writer(f, delimiter=";")
        w.writerow(["data", "descricao", "valor", "debito", "credito", "status", "obs", "id"])
        for s in saida:
            v = Decimal(s["valor"])
            bco = s.get("banco", BANCO)
            deb, cred = (bco, s["conta"]) if v > 0 else (s["conta"], bco)
            w.writerow([s["data"], s["descricao"], br(v) if v > 0 else "-" + br(v), deb, cred, s["status"], s["obs"], s["id"]])
        for m in pendentes_filial:
            w.writerow([m["data"], "FILIAL RECEBEU DO CNPJ DA MATRIZ (conta de origem desconhecida): " + m["descricao"], br(Decimal(m["valor"])), "544", "?", "NAO LANCADO", "Falta o extrato da conta da matriz que enviou", ""])


    linhas = [f"|0000|{cnpj}|"]
    for s in saida:
        v = Decimal(s["valor"]); dt = s["data"]; h = s["historico"]
        if s["partidas"]:
            if v < 0:
                linhas += ["|6000|C||||", f"|6100|{dt}||{BANCO}|{br(v)}||{h}||||"]
                linhas += [f"|6100|{dt}|{c}||{br(x)}||{h}||||" for c, x in s["partidas"]]
            else:
                linhas += ["|6000|D||||", f"|6100|{dt}|{BANCO}||{br(v)}||{h}||||"]
                linhas += [f"|6100|{dt}||{c}|{br(x)}||{h}||||" for c, x in s["partidas"]]
        else:
            bco = s.get("banco", BANCO)
            deb, cred = (bco, s["conta"]) if v > 0 else (s["conta"], bco)
            linhas += ["|6000|X||||", f"|6100|{dt}|{deb}|{cred}|{br(v)}||{h}||||"]
    Path(a.saida_txt).write_bytes(("\r\n".join(linhas) + "\r\n").encode("cp1252", errors="replace"))

    tot = {}
    for s in saida:
        tot[s["status"]] = tot.get(s["status"], 0) + 1
    banco = [s for s in saida if s.get("banco", BANCO) == BANCO]
    ent = sum(Decimal(s["valor"]) for s in banco if Decimal(s["valor"]) > 0)
    sai = sum(Decimal(s["valor"]) for s in banco if Decimal(s["valor"]) < 0)
    esp = sum(-Decimal(s["valor"]) for s in saida if s.get("banco") == "544")
    print(f"{a.comp}: {len(banco)} movimentos Sicredi | entradas {br(ent)} | saídas {br(sai)} | "
          f"{len(saida) - len(banco)} espelhos pagos pela filial (C 544) {br(esp)} | "
          f"{len(pendentes_filial)} PIX matriz→filial sem origem | {tot}")


if __name__ == "__main__":
    main()
