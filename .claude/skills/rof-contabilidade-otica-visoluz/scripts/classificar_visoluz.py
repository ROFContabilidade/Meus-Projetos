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
            val = -v
            if (cpf, val) in liq_ant:
                conta, status, obs = "187", "PROVADO", f"Salário líquido {comp_anterior(a.comp)} (folha)"
            elif (cpf, val) in adi_mes:
                conta, status, obs = "5", "PROVADO", f"Adiantamento {a.comp} (folha lança D25/C5; banco zera o caixa)"
            elif val >= 300 and 15 <= int(m["data"][:2]) <= 25:
                conta, status, obs = "5", "PROVAVEL", f"PIX na janela do adiantamento (dia 15-25) com valor diferente da folha {a.comp}"
            elif val >= Decimal(regras["empregado_limite_salario"]):
                conta, status, obs = "187", "PROVAVEL", "PIX a empregado sem par exato na folha: baixa de salários a pagar"
            else:
                conta, status, obs = regras["empregado_pequeno_conta"], "PROVAVEL", "PIX pequeno a empregado: vale/alimentação"
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

    with open(a.saida_csv, "w", newline="", encoding="utf-8-sig") as f:
        w = csv.writer(f, delimiter=";")
        w.writerow(["data", "descricao", "valor", "debito", "credito", "status", "obs", "id"])
        for s in saida:
            v = Decimal(s["valor"])
            deb, cred = (BANCO, s["conta"]) if v > 0 else (s["conta"], BANCO)
            w.writerow([s["data"], s["descricao"], br(v) if v > 0 else "-" + br(v), deb, cred, s["status"], s["obs"], s["id"]])

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
            deb, cred = (BANCO, s["conta"]) if v > 0 else (s["conta"], BANCO)
            linhas += ["|6000|X||||", f"|6100|{dt}|{deb}|{cred}|{br(v)}||{h}||||"]
    Path(a.saida_txt).write_bytes(("\r\n".join(linhas) + "\r\n").encode("cp1252", errors="replace"))

    tot = {}
    for s in saida:
        tot[s["status"]] = tot.get(s["status"], 0) + 1
    ent = sum(Decimal(s["valor"]) for s in saida if Decimal(s["valor"]) > 0)
    sai = sum(Decimal(s["valor"]) for s in saida if Decimal(s["valor"]) < 0)
    print(f"{a.comp}: {len(saida)} movimentos | entradas {br(ent)} | saídas {br(sai)} | {tot}")


if __name__ == "__main__":
    main()
