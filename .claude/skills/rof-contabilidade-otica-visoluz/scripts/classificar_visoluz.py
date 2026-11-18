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
BANCO = "8"  # padrão; --banco troca (9 = Itaú da matriz até 28/07/2026)


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
    ap.add_argument("--banco", default="8", help="conta contábil do banco do extrato")
    ap.add_argument("--manter", default="", help="contas do razão que ficam como estão (coluna cp_razao do extrato), ex.: 531,188,539 (Reinf)")
    ap.add_argument("--receita", help="pagamentos_receita.csv (data;receita;pa;principal;multa;juros;total): separa principal/multa/juros")
    ap.add_argument("--saldo-506", help="saldo CREDOR da 506 no início do mês (positivo)")
    ap.add_argument("--notas-506", help="CSV data;valor dos lançamentos da 506 que não são banco (NF = positivo/crédito; devolução = negativo)")
    ap.add_argument("--saida-csv", required=True)
    ap.add_argument("--saida-txt", required=True)
    a = ap.parse_args()

    global BANCO
    BANCO = a.banco
    manter = {c for c in a.manter.split(",") if c}
    guias = []
    if a.receita:
        guias = [g for g in csv.DictReader(open(a.receita, encoding="utf-8-sig"), delimiter=";")]
    regras = json.loads(Path(a.regras).read_text(encoding="utf-8"))
    cnpj = regras["cnpj"]
    pl_liq = Decimal(regras["socia"]["pro_labore_liquido"])

    folha = list(csv.DictReader(open(a.folha, encoding="utf-8"), delimiter=";"))
    emp = {f["cpf"]: f["nome"] for f in folha if f["tipo"] == "empregado"}
    emp_nome = {" ".join(norm(n).split()[:2]): c for c, n in emp.items()}  # Itaú não traz CPF no histórico
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
        if cpf is None:
            cpf = next((c for k, c in emp_nome.items() if k in d), None)
        partidas = None  # lista [(conta, valor)] para lote múltiplo
        c506 = False
        conta, status, obs = None, "SEM PROVA", ""

        guia = None
        if v < 0 and guias and any(k in d for k in ("RECEITA FEDERAL", "DARF", "SIMPLES NACIONAL", "TRIB COD BARRAS")):
            guia = next((g for g in guias if Decimal(g["total"]) == -v), None)
        # 0) Contas mantidas como no razão (ex.: sócia declarada na Reinf)
        if m.get("cp_razao") in manter:
            conta, status, obs = m["cp_razao"], "PROVADO", "Mantido como no razão (já declarado na EFD-Reinf)"
        elif guia:
            guias.remove(guia)
            nome = "parcelamento do Simples" if guia["receita"] == "1124" else "DAS"
            ps = [("479", Decimal(guia["principal"])), ("352", Decimal(guia["multa"])), ("372", Decimal(guia["juros"]))]
            ps = [x for x in ps if x[1]]
            conta, status, obs = "+".join(c for c, _ in ps), "PROVADO", f"{nome} (receita {guia['receita']}, PA {guia['pa']}), relatório de pagamentos da Receita"
            partidas = ps if len(ps) > 1 else None
            if not partidas: conta = "479"
        # 1) Empregados da folha (por CPF no PIX ou nome no Itaú)
        elif v < 0 and cpf in emp:
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
                    c506 = bool(r.get("controle_506"))
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
                      "historico": "REF. A " + d_hist[:150], "partidas": partidas, "c506": c506})

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
    chave = lambda dt: (dt[6:], dt[3:5], dt[:2])
    saida.sort(key=lambda s: chave(s["data"]))

    # Controle da 506: só baixa até o saldo de notas registradas; excedente vai para 470
    saldo506 = None
    if a.saldo_506 is not None:
        saldo506 = Decimal(a.saldo_506)
        notas = []
        if a.notas_506:
            notas = sorted(((n["data"], Decimal(n["valor"])) for n in csv.DictReader(open(a.notas_506, encoding="utf-8-sig"), delimiter=";")),
                           key=lambda x: chave(x[0]))
        exc = regras["controle_506"]["excedente"]; i = 0
        for s_ in saida:
            while i < len(notas) and chave(notas[i][0]) <= chave(s_["data"]):
                saldo506 += notas[i][1]; i += 1
            if not s_.get("c506"):
                continue
            pag = -Decimal(s_["valor"])
            base = s_["partidas"][0][1] if s_["partidas"] else pag
            disp = max(saldo506, Decimal("0"))
            if base <= disp:
                saldo506 -= base
                continue
            resto = base - disp
            outros = s_["partidas"][1:] if s_["partidas"] else []
            novas = ([("506", disp)] if disp else []) + [(exc, resto)] + outros
            saldo506 -= disp
            if len(novas) == 1:
                s_["conta"], s_["partidas"] = exc, None
            else:
                s_["partidas"] = novas; s_["conta"] = "+".join(c for c, _ in novas)
            s_["obs"] += f" | 506 sem saldo de notas: {br(resto)} em {exc}"
        while i < len(notas):
            saldo506 += notas[i][1]; i += 1

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
          f"{len(pendentes_filial)} PIX matriz→filial sem origem | {tot}"
          + (f" | saldo 506 no fim: {br(saldo506)}{' C' if saldo506 >= 0 else ' D'}" if saldo506 is not None else ""))


if __name__ == "__main__":
    main()
