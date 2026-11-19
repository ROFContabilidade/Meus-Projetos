#!/usr/bin/env python3
"""Motor único das Óticas 34 (matriz) e 118 (filial): banco -> classificação -> TXT Domínio + conferência, com travas.

Subcomandos
  razao-xls  Razão.csv (Domínio .xls convertido pelo LibreOffice, separador ;) -> razão longo (conta;data;lote;historico;cp;debito;credito)
  razao-pdf  Razão.txt (texto do PDF do Domínio, pdfplumber)                     -> razão longo
  periodo    roda os meses em ordem, encadeando saldos de banco, 506 e 544:
             python rotina_mes.py periodo --fontes fontes.json --saida DIR [--previa]

fontes.json (caminhos relativos ao próprio arquivo):
  {"saldos_iniciais": {"34": {"8": -862.44, "9": 0, "506": 1169.09}, "118": {"8": 0, "506": 1016.00}},   # 506 = saldo CREDOR
   "razao": {"34": "razao34_long.csv", "118": "razao118_long.csv"},  # para notas da 506 e lotes com várias partidas
   "folha": "folha.csv", "receita": "receita.csv",
   "meses": {"01/2026": {"34": {"8": "razao", "9": "razao"}, "118": {"8": "razao"}},
             "07/2026": {"34": {"8": "34_07.md"}, "118": {"8": "118_07.md"}}}}
  "razao" = movimentos do banco tirados do razão (01-06, que já fecham com os extratos); "*.md" = _extrato.md do Conversor ROF.

Sem --previa, o TXT só é gravado se TODAS as travas passarem (HANDOFF, seção 5.2). Com --previa grava PREVIA_*.txt para revisão.
Regras: references/regras.json (estab, conta @lógica) + contas_logicas.json + estabelecimentos.json + planos.
"""
import argparse, csv, json, re, sys, unicodedata
from collections import defaultdict
from decimal import Decimal as D
from pathlib import Path

AQUI = Path(__file__).resolve().parent
REF = AQUI.parent / "references"
Z = D("0")
EMPRESAS = ("34", "118")
ITAU_34_INATIVO = (2026, 7, 28)  # conta 9 da 34 inativa no Domínio a partir de 28/07/2026


# ---------------------------------------------------------------- utilidades
def norm(s):
    s = unicodedata.normalize("NFKD", s or "")
    return re.sub(r"\s+", " ", "".join(c for c in s if not unicodedata.combining(c))).strip().upper()


def dig(s):
    return re.sub(r"\D", "", s or "")


def br(v):
    return f"{abs(v):.2f}".replace(".", ",")


def num_br(s):
    s = (s or "").strip()
    return D(s.replace(".", "").replace(",", ".")) if s else None


def chave(dt):
    return (dt[6:10], dt[3:5], dt[:2])


def tupla(dt):
    return (int(dt[6:10]), int(dt[3:5]), int(dt[:2]))


def comp_anterior(comp):
    m, a = int(comp[:2]), int(comp[3:])
    m, a = (12, a - 1) if m == 1 else (m - 1, a)
    return f"{m:02d}/{a}"


def iso(comp):
    return f"{comp[3:]}-{comp[:2]}"


# ---------------------------------------------------------------- conversores de razão
def cmd_razao_xls(a):
    def n(s):
        s = (s or "").strip().rstrip("cd").replace(",", "")
        return D(s) if s else Z
    out, conta = [], None
    for r in csv.reader(open(a.entrada, encoding="utf-8", errors="replace"), delimiter=";"):
        r += [""] * 15
        if r[0] == "Conta:":
            conta = r[1]
        elif re.match(r"\d\d/\d\d/\d{4}", r[0]):
            out.append([conta, r[0], r[1], r[2].strip(), r[7], f"{n(r[8]):.2f}", f"{n(r[9]):.2f}"])
    _grava_longo(a.saida, out)


def cmd_razao_pdf(a):
    def n(s):
        return (-1 if s.endswith("C") else 1) * D(s.rstrip("DC").replace(".", "").replace(",", "."))
    rx = re.compile(r"^(\d\d/\d\d/\d{4}) (\d+) (.*?) ?(\S+) ([\d.]+,\d\d) ([\d.]+,\d\d[DC]?) ([\d.]+,\d\d[DC]?)$")
    out, conta, prev, cur = [], None, None, None
    for l in open(a.entrada, encoding="utf-8").read().splitlines():
        m = re.match(r"^Conta: (\d+) - ", l)
        if m:
            if m.group(1) != conta:
                conta, prev = m.group(1), None
            cur = None
            continue
        if l.startswith("SALDO ANTERIOR"):
            prev = n(l.split()[-1]); continue
        m = rx.match(l)
        if m:
            dt, lo, h, cp, v, _, se = m.groups()
            v, se = n(v), n(se)
            deb = se - prev if prev is not None else v
            cur = [conta, dt, lo, h, cp, f"{v:.2f}" if deb > 0 else "0.00", f"{v:.2f}" if deb < 0 else "0.00"]
            out.append(cur); prev = se
        elif cur and not re.match(r"^(Total do mês|Empresa:|C\.N\.P\.J|Período|RAZÃO|Data Lote|SALDO|Conta:|\d\d/)", l):
            cur[3] += " " + l.strip()
        else:
            cur = None
    _grava_longo(a.saida, out)


def _grava_longo(saida, out):
    with open(saida, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f, delimiter=";")
        w.writerow(["conta", "data", "lote", "historico", "cp", "debito", "credito"])
        w.writerows(out)
    print(f"{len(out)} linhas -> {saida}")


# ---------------------------------------------------------------- leitura das fontes
def ler_md(path):
    """_extrato.md do Conversor ROF -> (movimentos, saldo_inicial, saldo_final)."""
    txt = Path(path).read_text(encoding="utf-8")
    cab = re.search(r"Saldo inicial: ([-\d.,]+) \|.*Saldo final: ([-\d.,]+)", txt)
    si, sf = num_br(cab.group(1)), num_br(cab.group(2))
    movs, dentro = [], False
    for l in txt.splitlines():
        if l.startswith("data|"):
            dentro = True; continue
        if l.startswith("## "):
            dentro = False
        if not dentro or "|" not in l:
            continue
        p = l.split("|")
        if len(p) < 5 or not re.match(r"\d\d/\d\d/\d{4}", p[0]) or not p[3].strip():
            continue
        movs.append({"data": p[0], "descricao": p[1], "documento": p[2], "valor": num_br(p[3]), "cp_razao": "", "lote": ""})
    movs = [m for _, m in sorted(enumerate(movs), key=lambda x: (chave(x[1]["data"]), x[0]))]
    return movs, si, sf


def ler_razao(path):
    return list(csv.DictReader(open(path, encoding="utf-8"), delimiter=";"))


def movs_razao(razao, conta, comp, bancos):
    """Movimentos de banco do razão no mês. Lote banco↔banco (8↔9) aparece uma vez só (pela conta 8)."""
    movs = []
    for r in razao:
        if r["conta"] != conta or r["data"][3:] != comp:
            continue
        v = D(r["debito"]) - D(r["credito"])
        mv = {"data": r["data"], "descricao": r["historico"], "documento": "", "valor": v, "cp_razao": r["cp"], "lote": r["lote"]}
        if r["cp"] in bancos and r["cp"] != conta and conta != "8":
            mv["omitir"] = "lote 8↔9 do razão: lançado uma vez só, pela conta 8"  # entra no saldo, não no TXT
        movs.append(mv)
    return movs


def partidas_lote(razao, lote, data, bancos):
    """Contrapartidas reais de um lote do razão com várias partidas (cp vazio)."""
    ps = []
    for r in razao:
        if r["lote"] == lote and r["data"] == data and r["conta"] not in bancos:
            ps.append((r["conta"], D(r["debito"]) - D(r["credito"])))
    return ps


# ---------------------------------------------------------------- classificador
class Motor:
    def __init__(self, fontes_path, saida, previa):
        self.base = Path(fontes_path).resolve().parent
        self.f = json.loads(Path(fontes_path).read_text(encoding="utf-8"))
        self.saida = Path(saida); self.saida.mkdir(parents=True, exist_ok=True)
        self.previa = previa
        self.est = json.loads((REF / "estabelecimentos.json").read_text(encoding="utf-8"))
        self.logicas = json.loads((REF / "contas_logicas.json").read_text(encoding="utf-8"))
        self.regras = json.loads((REF / "regras.json").read_text(encoding="utf-8"))
        self.planos = {e: {r["codigo"]: r for r in csv.DictReader(open(REF / f"plano_{e}.csv", encoding="utf-8"), delimiter=";")}
                       for e in EMPRESAS}
        self.razao = {e: ler_razao(self.base / p) for e, p in self.f["razao"].items()}
        self.folha = list(csv.DictReader(open(self.base / self.f["folha"], encoding="utf-8"), delimiter=";"))
        self.guias = list(csv.DictReader(open(self.base / self.f["receita"], encoding="utf-8-sig"), delimiter=";"))
        # favorecidos achados no extrato original quando o razão não traz o nome (empresa;banco;data;valor;favorecido;fonte)
        self.ident = {(r["empresa"], r["banco"], r["data"], D(r["valor"])): r for r in
                      csv.DictReader(open(REF / "identificados.csv", encoding="utf-8"), delimiter=";")} if (REF / "identificados.csv").exists() else {}
        pj = self.est["pj"]
        self.socia_cpf = pj["socia"]["cpf"]
        self.pl_liq = D(pj["socia"]["pro_labore_liquido"])
        self.reinf = self.est["reinf_travado"]["34"]
        si = self.f["saldos_iniciais"]
        self.saldo = {e: {k: D(str(v)) for k, v in si[e].items() if k != "506"} for e in EMPRESAS}
        self.s506 = {e: D(str(si[e].get("506", 0))) for e in EMPRESAS}
        self.s544 = {e: Z for e in EMPRESAS}
        self.pend_544 = []  # pernas que faltam (acumulado): {"empresa_faltando", "valor" (efeito na 544 dela), ...}
        self.usadas_guias = set()
        self.resumo = []

    # -- contas lógicas
    def cod(self, conta, emp):
        if conta and conta.startswith("@"):
            return self.logicas.get(conta, {}).get(emp, conta)  # sem código: fica o @, a trava (c) pega
        return conta

    # -- folha
    def preparar_folha(self, comp):
        emp = {f["cpf"]: f["nome"] for f in self.folha if f["tipo"] == "empregado"}
        self.emp = emp
        self.adm = {f["cpf"]: f["admissao"] for f in self.folha if f["tipo"] == "empregado" and f.get("admissao")}
        self.emp_nome = {" ".join(norm(n).split()[:2]): c for c, n in emp.items()}
        ant = comp_anterior(comp)
        self.liq_ant = {(f["cpf"], D(f["liquido"])) for f in self.folha if f["competencia"] == ant and f["tipo"] == "empregado"}
        self.adi_mes = {(f["cpf"], D(f["adiantamento"])) for f in self.folha if f["competencia"] == comp and f["tipo"] == "empregado"}

    def acha_empregado(self, d, doc):
        for c in re.findall(r"\b\d{11}\b", doc + " " + d.replace(".", "").replace("-", "")):
            if c in self.emp:
                return c
        for k, c in self.emp_nome.items():
            if re.search(r"\b" + re.escape(k) + r"\b", d):
                return c
        return None

    def classe_empregado(self, cpf, val, dia, comp):
        lim = D(self.regras.get("empregado_limite_salario", "200.00"))
        if (cpf, val) in self.liq_ant:
            return "@salarios_pagar", "PROVADO", f"Salário líquido {comp_anterior(comp)} (folha)"
        if (cpf, val) in self.adi_mes:
            return "@caixa", "PROVADO", f"Adiantamento {comp} (folha lança D25/C5; banco zera o caixa)"
        if val >= 300 and 15 <= dia <= 25:
            return "@caixa", "PROVAVEL", "PIX na janela do adiantamento (dia 15-25) com valor diferente da folha"
        if val >= lim:
            return "@salarios_pagar", "PROVAVEL", "PIX a empregado sem par exato na folha: baixa de salários a pagar"
        return "@va", "PROVAVEL", "PIX pequeno a empregado: VA/VR (542)"

    def eh_socia(self, d, doc):
        return (self.socia_cpf in dig(doc) or self.socia_cpf in d.replace(".", "").replace("-", "")
                or re.search(r"\bADRIANA RODRIGUES( DE PAULA)?\b", d) is not None)

    # -- regra
    def regra(self, emp, d, doc, v):
        dd = dig(doc) + " " + d.replace(".", "").replace("/", "").replace("-", "")
        for r in self.regras["regras"]:
            if emp not in r.get("estab", EMPRESAS):
                continue
            if r.get("sinal") == "+" and v < 0 or r.get("sinal") == "-" and v > 0:
                continue
            if any(re.search(r"(?<![A-Z0-9])" + re.escape(p), d) for p in r["contem"]) or any(x in dd for x in r.get("doc", [])):
                return r
        return None

    def classificar(self, emp, banco, m, comp, pl):
        """Devolve dict com conta (lógica ou código), status, obs, partidas, c506, ligacao, espelho."""
        idf = self.ident.get((emp, banco, m["data"], m["valor"]))
        if idf and not m.get("identificado"):
            m["descricao"] += " " + idf["favorecido"]; m["identificado"] = idf["fonte"]
        v = m["valor"]; d = norm(m["descricao"]); doc = m.get("documento", "")
        c = {"conta": None, "status": "SEM PROVA", "obs": "", "partidas": None, "c506": False, "ligacao": None, "espelho": None}
        travado = emp == "34" and iso(comp) in self.reinf
        # 0) Reinf travada: o que era 531 no razão, ou PIX da sócia, fica exatamente como no razão
        if travado and m.get("lote") and (m["cp_razao"] == "531" or self.eh_socia(d, doc)):
            if m["cp_razao"]:
                c.update(conta=m["cp_razao"], status="PROVADO", obs="Mantido como no razão (EFD-Reinf já declarada)")
            else:
                ps = partidas_lote(self.razao[emp], m["lote"], m["data"], {"8", "9"})
                c.update(conta="+".join(x for x, _ in ps), partidas=[(x, abs(y)) for x, y in ps], status="PROVADO",
                         obs="Mantido como no razão, lote com várias partidas (EFD-Reinf já declarada)")
            return c
        # 1) Guia da Receita (principal / multa / juros)
        if v < 0 and any(k in d for k in ("RECEITA FEDERAL", "DARF", "SIMPLES NACIONAL", "TRIB COD BARRAS")) and emp == "34":
            g = next((g for i, g in enumerate(self.guias) if i not in self.usadas_guias and D(g["total"]) == -v
                      and g["data"][3:] == comp), None) or \
                next((g for i, g in enumerate(self.guias) if i not in self.usadas_guias and D(g["total"]) == -v), None)
            if g:
                self.usadas_guias.add(self.guias.index(g))
                ps = [(x, D(g[k])) for x, k in (("@simples", "principal"), ("@multa", "multa"), ("@juros", "juros")) if D(g[k])]
                nome = "parcelamento do Simples" if g["receita"] == "1124" else "DAS"
                c.update(conta="+".join(x for x, _ in ps), partidas=ps if len(ps) > 1 else None, status="PROVADO",
                         obs=f"{nome} (receita {g['receita']}, PA {g['pa']}), relatório de pagamentos da Receita")
                if len(ps) == 1: c["conta"] = ps[0][0]
                return c
        # 2) Sócia
        if self.eh_socia(d, doc):
            if v < 0 and emp == "34":
                falta = max(self.pl_liq - pl[0], Z); p188 = min(falta, -v); pl[0] += p188; resto = -v - p188
                if p188 and resto:
                    c.update(conta="@pro_labore_pagar+@socia", partidas=[("@pro_labore_pagar", p188), ("@socia", resto)],
                             status="PROVAVEL", obs="Pró-labore líquido + retirada (conta corrente da sócia)")
                elif p188:
                    c.update(conta="@pro_labore_pagar", status="PROVAVEL", obs="Pró-labore líquido")
                else:
                    c.update(conta="@socia", status="PROVAVEL", obs="Retirada da sócia (conta corrente)")
            else:
                c.update(conta="@socia", status="PROVAVEL", obs="Retirada/devolução da sócia")
            return c
        # 3) Empregados da matriz
        cpf = self.acha_empregado(d, doc) if v < 0 else None
        if (cpf and cpf in self.adm and tupla(m["data"]) < tupla(self.adm[cpf])
                and (cpf, -v) not in self.liq_ant and (cpf, -v) not in self.adi_mes):  # valor igual ao da folha: vale a folha
            c.update(conta="@terceiros", status="PROVADO",
                     obs=f"PIX a {self.emp[cpf]} ANTES da admissão ({self.adm[cpf]}): pessoa física sem vínculo → 362 (alerta trabalhista/INSS)")
            return c
        if cpf:
            conta, st, ob = self.classe_empregado(cpf, -v, int(m["data"][:2]), comp)
            if emp == "34":
                c.update(conta=conta, status=st, obs=ob)
            else:
                c.update(conta="@ligacao", status=st, obs="Empregado da matriz pago pela filial: " + ob,
                         espelho=conta, ligacao="espelho")
            return c
        # 4) Regras
        r = self.regra(emp, d, doc, v)
        if r:
            c.update(conta=r["conta"], status=r["status"], obs=r.get("obs", ""), c506=bool(r.get("controle_506")),
                     ligacao=r.get("ligacao"), espelho=r.get("espelho_34") or r.get("espelho_118"))
            if r.get("espelho_34"): c["ligacao"] = "espelho"
            if r.get("espelho_118"): c["ligacao"] = "espelho_rev"
            if r.get("proprio"): c["ligacao"] = "proprio"
            if "partidas" in r:
                base = D(r["partidas"]["valor_nota"])
                if abs(v) > base:
                    c["partidas"] = [(r["conta"], base), (r["partidas"]["conta_dif"], abs(v) - base)]
            if r["conta"] == "@terceiros":
                if re.search(r"\b\d{14}\b", d) or re.search(r"\d{2}\.\d{3}\.\d{3}/\d{4}-\d{2}", doc):
                    c.update(conta="@fornecedores", c506=True, status="PROVAVEL",
                             obs="Pagamento a CNPJ sem regra: 506 até o saldo de notas, excedente 470 (Rosangela 18/11/2026)")
                elif re.fullmatch(r"(REF\.? A )?(PIX ENVIADO|PAGAMENTOS? PIX( QR-CODE)?)", d):
                    c.update(status="SEM PROVA", obs="Favorecido não aparece no histórico do razão: conferir no extrato")
            if "rendimento" in r and abs(v) % 100:
                c["partidas"] = [(r["conta"], abs(v) - abs(v) % 100), (r["rendimento"], abs(v) % 100)]
            return c
        # 5) Pagamento a CNPJ sem regra (boleto, PIX): 506 até o saldo de notas; excedente 470 (Rosangela 18/11/2026)
        if v < 0 and (re.search(r"\b\d{14}\b", d) or re.search(r"\d{2}\.\d{3}\.\d{3}/\d{4}-\d{2}", doc)):
            c.update(conta="@fornecedores", c506=True, status="PROVAVEL",
                     obs="Pagamento a CNPJ sem regra: 506 até o saldo de notas, excedente 470 (Rosangela 18/11/2026)")
            return c
        # 6) Sem regra: fica a conta do razão (se houver) para revisão
        if m.get("cp_razao"):
            c.update(conta=m["cp_razao"], status="SEM PROVA", obs="Sem regra: mantida a conta do razão, revisar")
        else:
            c.update(conta="@clientes" if v > 0 else "@diversas", status="SEM PROVA", obs="Sem regra: confirmar")
        return c

    # ------------------------------------------------------------ mês
    def mes(self, comp):
        self.preparar_folha(comp)
        fm = self.f["meses"][comp]
        lanc = {e: [] for e in EMPRESAS}       # lançamentos (linhas do TXT)
        bancos_chk = []                         # trava (a)
        pend = []                               # pendências do mês
        for emp in EMPRESAS:
            pl = [Z]
            for banco, fonte in fm.get(emp, {}).items():
                if fonte == "razao":
                    movs = movs_razao(self.razao[emp], banco, comp, {"8", "9"} if emp == "34" else {"8"})
                    si = self.saldo[emp].get(banco, Z)
                    # saldo de referência = saldo do razão no fim do mês (já conciliado com o extrato)
                    ref = si + sum((D(r["debito"]) - D(r["credito"])) for r in self.razao[emp]
                                   if r["conta"] == banco and r["data"][3:] == comp)
                    ref_si = si
                else:
                    movs, ref_si, ref = ler_md(self.base / fonte)
                    si = self.saldo[emp].get(banco, Z)
                for i, m in enumerate(movs):
                    m["id"] = f"{emp}-{banco}-{iso(comp)}-{i + 1:03d}"
                    m["banco"] = banco; m["emp"] = emp
                    m.update(self.classificar(emp, banco, m, comp, pl))
                    if m.get("omitir"): m["omitido"] = m.pop("omitir")
                    lanc[emp].append(m)
                sf = si + sum(m["valor"] for m in movs)
                bancos_chk.append({"empresa": emp, "banco": banco, "fonte": fonte, "saldo_inicial": si, "ref_inicial": ref_si,
                                   "entradas": sum(m["valor"] for m in movs if m["valor"] > 0),
                                   "saidas": sum(m["valor"] for m in movs if m["valor"] < 0),
                                   "saldo_final": sf, "ref_final": ref, "ok": si == ref_si and sf == ref})
                self.saldo[emp][banco] = sf

        self.parear_proprias(lanc["34"], pend)
        self.parear_ligacao(lanc, pend, comp)
        espelhos = self.gerar_espelhos(lanc)
        espelhos_rev = self.gerar_espelhos_rev(lanc)
        for emp in EMPRESAS:
            for m in lanc[emp]:
                for k in ("conta", "espelho"):
                    alvo = emp if k == "conta" else ("118" if m.get("ligacao") == "espelho_rev" else "34")
                    if m.get(k): m[k] = "+".join(self.cod(x, alvo) for x in m[k].split("+"))
                if m.get("partidas"):
                    m["partidas"] = [(self.cod(x, emp), y) for x, y in m["partidas"]]
        for e in espelhos:
            e["conta"] = self.cod(e["conta"], "34")
        lanc["34"] += espelhos
        for e in espelhos_rev:
            e["conta"] = self.cod(e["conta"], "118")
        lanc["118"] += espelhos_rev
        for emp in EMPRESAS:
            lanc[emp].sort(key=lambda m: chave(m["data"]))
            self.controle_506(emp, lanc[emp], comp)
        travas = self.travas(comp, lanc, bancos_chk, pend)
        self.gravar(comp, lanc, bancos_chk, travas, pend)

    # -- transferências entre contas da própria matriz (Itaú 9 ↔ Sicredi 8): uma vez só
    def parear_proprias(self, l34, pend):
        sic = [m for m in l34 if m["banco"] == "8" and m.get("ligacao") == "proprio"]
        ita = [m for m in l34 if m["banco"] == "9"]
        for s in sic:
            par = next((t for t in ita if not t.get("par") and t["data"] == s["data"] and t["valor"] == -s["valor"]
                        and t["valor"] < 0), None)
            if par:
                par["par"] = s["id"]; s["par"] = par["id"]
                s.update(conta="@itau_matriz", status="PROVADO", obs="Transferência Itaú 0098929-8 → Sicredi (mesmo CNPJ; uma vez só)")
            elif s.get("cp_razao") == "9":
                s.update(conta="@itau_matriz", status="PROVADO", obs="Transferência entre contas da matriz (lote 8↔9 do razão)")
            else:
                s.update(conta="@clientes", status="PROVAVEL", ligacao=None,
                         descricao="RECEBIMENTO CARTAO DE TODOS (repasse da conta digital do convenio) " + s["descricao"],
                         obs="Repasse da conta digital do Cartão de Todos (conta transitória no CNPJ 0001-93, sem saldo): "
                             "recebimento de cliente (Rosangela/cliente 19/11/2026). Guardar o relatório de repasses (Lei 9.430 art. 42)")
        # Itaú → Sicredi pelo lado do Itaú: some do TXT (o Sicredi já lançou)
        for t in ita:
            if t.get("par"):
                t["omitido"] = "transferência já lançada pelo Sicredi"
            elif t["valor"] < 0 and t.get("cp_razao") == "8":
                pass
        # Sicredi → Itaú (lote 8↔9 do razão vindo pela conta 8)
        for s in l34:
            if s["banco"] == "8" and s.get("cp_razao") == "9" and not s.get("par") and s.get("ligacao") != "proprio":
                s.update(conta="@itau_matriz", status="PROVADO", obs="Transferência entre contas da matriz (lote 8↔9 do razão)",
                         c506=False, ligacao=None, espelho=None, partidas=None)
        # Itaú: PIX ao próprio CNPJ sem par no Sicredi
        for t in ita:
            d = norm(t["descricao"])
            if not t.get("par") and t["valor"] < 0 and ("OTICA VISOLUZ" in d or "24026777000193" in dig(d)):
                pend.append({"tipo": "Itaú → próprio CNPJ sem par no Sicredi", "empresa": "34", "data": t["data"],
                             "valor": t["valor"], "descricao": t["descricao"], "acao": "Conferir destino (conta sem extrato?)"})
                t.update(conta="@conta_sem_extrato", status="SEM PROVA", obs="Itaú → conta do próprio CNPJ sem extrato")

    # -- ligação 34 ↔ 118 (mesma data e valor; SISPAG da filial com a ligação dentro do lote)
    def parear_ligacao(self, lanc, pend, comp):
        l34 = [m for m in lanc["34"] if m.get("ligacao") == "transferencia" and not m.get("omitido")]
        l118 = [m for m in lanc["118"] if m.get("ligacao") in ("transferencia", "matriz_sem_extrato")]
        for a in l34:
            par = next((b for b in l118 if not b.get("par") and b["data"] == a["data"] and b["valor"] == -a["valor"]), None)
            if par:
                a["par"] = par["id"]; par["par"] = a["id"]
                par["status"] = a["status"] = "PROVADO"
                par["obs"] = a["obs"] = "Transferência matriz↔filial pareada (mesma data e valor)"
                continue
            # entrada na matriz vinda da filial dentro de um lote SISPAG da filial
            if a["valor"] > 0:
                sis = next((b for b in lanc["118"] if not b.get("par") and b["data"] == a["data"] and b["valor"] < 0
                            and "SISPAG" in norm(b["descricao"]) and -b["valor"] >= a["valor"]), None)
                if sis and -sis["valor"] == a["valor"]:
                    sis["par"] = a["id"]; a["par"] = sis["id"]
                    sis.update(conta="@ligacao", partidas=None, c506=False, ligacao="transferencia", status="PROVAVEL",
                               obs="SISPAG com o mesmo valor da entrada no Sicredi da matriz no mesmo dia: transferência à matriz")
                    a.update(status="PROVAVEL", obs="Transferência da filial (SISPAG de mesmo valor no Itaú da filial)")
                    continue
                if sis:
                    resto = -sis["valor"] - a["valor"]
                    sis["par"] = a["id"]; a["par"] = sis["id"]
                    sis.update(conta="@ligacao+@fornecedores", partidas=[("@ligacao", a["valor"]), ("@fornecedores", resto)],
                               status="PROVAVEL", c506=True, ligacao="transferencia",
                               obs=f"Lote SISPAG com {br(a['valor'])} para a matriz (entrada no Sicredi no mesmo dia); "
                                   f"restante {br(resto)} fornecedor. Conferir no relatório SISPAG (pendência 2)")
                    a.update(status="PROVAVEL", obs="Transferência da filial dentro de lote SISPAG (pendência 2)")
                    pend.append({"tipo": "Ligação dentro de lote SISPAG", "empresa": "118", "data": a["data"], "valor": a["valor"],
                                 "descricao": sis["descricao"], "acao": "Confirmar pelo relatório SISPAG do Itaú (pendência 2)",
                                 "informativo": True})
                    continue
            pend.append({"tipo": "Transferência da matriz sem par na filial", "empresa": "34", "data": a["data"], "valor": a["valor"],
                         "descricao": a["descricao"], "acao": "Achar o movimento na filial", "falta_118": a["valor"]})
        for b in l118:
            if b.get("par"):
                continue
            if b["valor"] > 0:
                b["obs"] = "PIX do CNPJ 0001-93 por conta da matriz SEM EXTRATO: na 34 entra D 544 / C <conta> quando o extrato chegar"
                pend.append({"tipo": "Matriz → filial por conta sem extrato", "empresa": "118", "data": b["data"], "valor": b["valor"],
                             "descricao": b["descricao"], "acao": "Pendência 1: extrato da conta da matriz", "falta_34": b["valor"]})
            else:
                pend.append({"tipo": "Transferência da filial sem par na matriz", "empresa": "118", "data": b["data"], "valor": b["valor"],
                             "descricao": b["descricao"], "acao": "Achar a entrada na matriz", "falta_34": b["valor"]})

    # -- espelhos: a filial pagou despesa/obrigação da matriz -> 34 D <conta> / C 544
    def gerar_espelhos(self, lanc):
        out = []
        for m in lanc["118"]:
            if m.get("ligacao") == "espelho" and m.get("espelho"):
                out.append({"data": m["data"], "descricao": "PAGO PELA FILIAL: " + m["descricao"], "documento": m.get("documento", ""),
                            "valor": m["valor"], "banco": "@ligacao", "emp": "34", "id": m["id"] + "-E34", "par": m["id"],
                            "conta": m["espelho"], "status": m["status"], "partidas": None, "c506": False, "ligacao": "espelho_34",
                            "obs": "Espelho do pagamento feito pela filial (118 D 544 / C 8): " + m["obs"], "espelho_de": m["id"]})
                m["par"] = m["id"] + "-E34"
        return out

    def gerar_espelhos_rev(self, lanc):
        """A matriz pagou despesa da FILIAL: 34 D 544 / C banco; 118 D <conta> / C 544."""
        out = []
        for m in lanc["34"]:
            if m.get("ligacao") == "espelho_rev" and m.get("espelho"):
                out.append({"data": m["data"], "descricao": "PAGO PELA MATRIZ: " + m["descricao"], "documento": m.get("documento", ""),
                            "valor": m["valor"], "banco": "@ligacao", "emp": "118", "id": m["id"] + "-E118", "par": m["id"],
                            "conta": m["espelho"], "status": m["status"], "partidas": None, "c506": False, "ligacao": "espelho_118",
                            "obs": "Espelho do pagamento feito pela matriz (34 D 544 / C banco): " + m["obs"], "espelho_de": m["id"]})
                m["par"] = m["id"] + "-E118"
        return out

    # -- 506 nunca devedora (por empresa)
    def controle_506(self, emp, lan, comp):
        bancos = {"8", "9"} if emp == "34" else {"8"}
        lotes_banco = {r["lote"] for r in self.razao[emp] if r["conta"] in bancos}
        notas = sorted(((r["data"], D(r["credito"]) - D(r["debito"])) for r in self.razao[emp]
                        if r["conta"] == "506" and r["data"][3:] == comp and r["lote"] not in lotes_banco and r["cp"] not in bancos),
                       key=lambda x: chave(x[0]))
        exc = self.cod("@cmv", emp); f506 = self.cod("@fornecedores", emp)
        s = self.s506[emp]; i = 0
        for m in lan:
            while i < len(notas) and chave(notas[i][0]) <= chave(m["data"]):
                s += notas[i][1]; i += 1
            if m.get("omitido") or m["valor"] >= 0:
                continue
            ps = m["partidas"] or [(m["conta"], -m["valor"])]
            if not any(c == f506 for c, _ in ps):
                continue
            novas = []
            for c, x in ps:
                if c != f506:
                    novas.append((c, x)); continue
                disp = max(s, Z); baixa = min(x, disp); s -= baixa
                if baixa: novas.append((f506, baixa))
                if x - baixa:
                    novas.append((exc, x - baixa)); m["obs"] += f" | 506 sem saldo de notas: {br(x - baixa)} em {exc}"
            m["partidas"] = novas if len(novas) > 1 else None
            m["conta"] = "+".join(c for c, _ in novas)
        while i < len(notas):
            s += notas[i][1]; i += 1
        self.s506[emp] = s

    # ------------------------------------------------------------ travas
    def travas(self, comp, lanc, bancos_chk, pend):
        t = []
        # (a) bancos
        for b in bancos_chk:
            t.append(("a", f"{b['empresa']} banco {b['banco']} fecha com o extrato/razão", b["ok"],
                      f"SI {br(b['saldo_inicial'])} (ref {br(b['ref_inicial'])}) | SF {'-' if b['saldo_final'] < 0 else ''}{br(b['saldo_final'])} "
                      f"(ref {'-' if b['ref_final'] < 0 else ''}{br(b['ref_final'])})"))
        # 544
        for emp in EMPRESAS:
            for m in lanc[emp]:
                if m.get("omitido"): continue
                for c, x in self.pernas(m, emp):
                    if c == "544": self.s544[emp] += x
        dif = self.s544["34"] + self.s544["118"]
        for p in pend:
            if "falta_34" in p: self.pend_544.append(("34", p["falta_34"], p))
            if "falta_118" in p: self.pend_544.append(("118", p["falta_118"], p))
        expl = -sum(x for _, x, _ in self.pend_544)  # pernas que faltam: dif + faltas = 0
        ok_b = dif == expl
        t.append(("b", "544(34) + 544(118) = 0 ou diferença explicada pelas pendências", ok_b,
                  f"544 34 {br(self.s544['34'])}{'D' if self.s544['34'] >= 0 else 'C'} | 544 118 {br(self.s544['118'])}"
                  f"{'D' if self.s544['118'] >= 0 else 'C'} | soma {'-' if dif < 0 else ''}{br(dif)} | explicado por pendências "
                  f"{'-' if expl < 0 else ''}{br(expl)}" + ("" if dif == 0 else " (só zera quando as pendências forem resolvidas)")))
        # (c) códigos
        for emp in EMPRESAS:
            ruins = defaultdict(int)
            for m in lanc[emp]:
                if m.get("omitido"): continue
                for c, _ in self.pernas(m, emp):
                    p = self.planos[emp].get(c)
                    if not p or p["tipo"] != "A": ruins[c] += 1
            t.append(("c", f"{emp}: todo código existe como analítica no plano", not ruins,
                      "; ".join(f"{c} ({n} lanç.)" + (" = conta 545 cotas Sicredi não criada" if c == "545" else "")
                                + (" = conta da matriz sem extrato (pendência 1)" if c == "@conta_sem_extrato" else "")
                                for c, n in ruins.items()) or "ok"))
            # Itaú 34 inativo
            if emp == "34":
                tarde = [m for m in lanc[emp] if not m.get("omitido") and tupla(m["data"]) >= ITAU_34_INATIVO
                         and any(c == "9" for c, _ in self.pernas(m, emp))]
                t.append(("c", "34: nada na conta 9 (Itaú inativo) a partir de 28/07/2026", not tarde, f"{len(tarde)} lanç."))
        # (d) CNPJ
        for emp in EMPRESAS:
            cnpj = self.est["estabelecimentos"][emp]["cnpj"]
            t.append(("d", f"{emp}: |0000| com o CNPJ {cnpj} e nome do arquivo com o código {emp}", cnpj[:8] == "24026777"
                      and (emp == "34") == cnpj.endswith("000193"), self.nome_txt(emp, comp)))
        # (e) duplicidade
        vistos = defaultdict(list)
        for emp in EMPRESAS:
            for m in lanc[emp]:
                if m.get("omitido"): continue
                vistos[re.sub(r"-E(34|118)$", "", m["id"])].append((emp, m.get("ligacao")))
        dup = [k for k, v in vistos.items() if len(v) > 1 and not all(l in ("espelho", "espelho_34", "espelho_rev", "espelho_118") for _, l in v)]
        t.append(("e", "Nenhum movimento nos dois TXT fora as pernas da ligação", not dup, ", ".join(dup) or "ok"))
        # (f) 506
        for emp in EMPRESAS:
            t.append(("f", f"{emp}: 506 nunca devedora", self.s506[emp] >= 0,
                      f"saldo {br(self.s506[emp])}{'C' if self.s506[emp] >= 0 else 'D'}"))
        # (g) Reinf
        if iso(comp) in self.reinf:
            liq = Z
            for m in lanc["34"]:
                if m.get("omitido") or m["banco"] not in ("8", "9"): continue
                for c, x in self.pernas(m, "34"):
                    if c == "531": liq += x
            dec = D(self.reinf[iso(comp)])
            t.append(("g", f"34: 531 líquido do mês = declarado na EFD-Reinf ({br(dec)})", liq == dec,
                      f"lançado {'-' if liq < 0 else ''}{br(liq)} | declarado {'-' if dec < 0 else ''}{br(dec)}"))
        return t

    def pernas(self, m, emp):
        """(conta, valor com sinal: + débito, - crédito) de cada perna não-banco e do banco."""
        v = m["valor"]; bco = self.cod(m["banco"], emp)
        out = [(bco, v)]
        if m.get("partidas"):
            out += [(c, -x if v > 0 else x) for c, x in m["partidas"]]
        else:
            out += [(m["conta"], -v)]
        return out

    # ------------------------------------------------------------ saídas
    def nome_txt(self, emp, comp):
        return self.est["estabelecimentos"][emp]["txt"].replace("<AAAA-MM>", iso(comp))

    def txt(self, emp, lan):
        cnpj = self.est["estabelecimentos"][emp]["cnpj"]
        L = [f"|0000|{cnpj}|"]
        for m in lan:
            if m.get("omitido"): continue
            v = m["valor"]; dt = m["data"]; bco = self.cod(m["banco"], emp)
            h = re.sub(r"^REF\.? A\s+", "", re.sub(r"\s*/\s*[A-Z0-9_.]+$", "", norm(m["descricao"])))
            h = ("REF. A " + h)[:200].replace("|", " ")
            if m.get("partidas"):
                if v < 0:
                    L += ["|6000|C||||", f"|6100|{dt}||{bco}|{br(v)}||{h}||||"] + [f"|6100|{dt}|{c}||{br(x)}||{h}||||" for c, x in m["partidas"]]
                else:
                    L += ["|6000|D||||", f"|6100|{dt}|{bco}||{br(v)}||{h}||||"] + [f"|6100|{dt}||{c}|{br(x)}||{h}||||" for c, x in m["partidas"]]
            else:
                deb, cred = (bco, m["conta"]) if v > 0 else (m["conta"], bco)
                L += ["|6000|X||||", f"|6100|{dt}|{deb}|{cred}|{br(v)}||{h}||||"]
        return ("\r\n".join(L) + "\r\n").encode("cp1252", errors="replace")

    def gravar(self, comp, lanc, bancos_chk, travas, pend):
        from openpyxl import Workbook
        from openpyxl.styles import Font, PatternFill
        ok = all(x[2] for x in travas)
        pasta = self.saida / iso(comp); pasta.mkdir(exist_ok=True)
        for emp in EMPRESAS:
            nome = self.nome_txt(emp, comp)
            for velho in (pasta / nome, pasta / ("PREVIA_" + nome)):
                if velho.exists(): velho.unlink()
            if ok:
                (pasta / nome).write_bytes(self.txt(emp, lanc[emp]))
            elif self.previa:
                (pasta / ("PREVIA_" + nome)).write_bytes(self.txt(emp, lanc[emp]))
        wb = Workbook(); ws = wb.active; ws.title = "Resumo-Travas"
        neg = Font(bold=True); verm = PatternFill("solid", fgColor="F4CCCC"); verde = PatternFill("solid", fgColor="D9EAD3")
        ws.append([f"Óticas 34 + 118 - competência {comp}", "", "TXT liberado" if ok else "TXT BLOQUEADO pelas travas"])
        ws["A1"].font = neg
        ws.append([])
        ws.append(["Trava", "Descrição", "Resultado", "Detalhe"]); [setattr(c, "font", neg) for c in ws[3]]
        for t in travas:
            ws.append([t[0], t[1], "OK" if t[2] else "FALHOU", t[3]])
            ws.cell(ws.max_row, 3).fill = verde if t[2] else verm
        ws.append([]); ws.append(["Empresa", "Banco", "Fonte", "Saldo inicial", "Entradas", "Saídas", "Saldo final", "Referência final"])
        for b in bancos_chk:
            ws.append([b["empresa"], b["banco"], b["fonte"], float(b["saldo_inicial"]), float(b["entradas"]), float(b["saidas"]),
                       float(b["saldo_final"]), float(b["ref_final"])])
        ws.append([]); ws.append(["Status (34/118)", "Qtde"])
        cont = defaultdict(int)
        for emp in EMPRESAS:
            for m in lanc[emp]:
                if not m.get("omitido"): cont[(emp, m["status"])] += 1
        for k, n in sorted(cont.items()): ws.append([f"{k[0]} {k[1]}", n])
        for emp, aba in (("34", "Matriz"), ("118", "Filial")):
            w = wb.create_sheet(aba)
            w.append(["data", "banco", "histórico", "documento", "valor", "débito", "crédito", "partidas", "status", "obs", "id", "par", "razão (cp antigo)"])
            for m in lanc[emp]:
                if m.get("omitido"):
                    w.append([m["data"], m["banco"], m["descricao"], m.get("documento", ""), float(m["valor"]), "", "", "", "OMITIDO",
                              m["omitido"], m["id"], m.get("par", ""), m.get("cp_razao", "")]); continue
                bco = self.cod(m["banco"], emp); v = m["valor"]
                deb, cred = (bco, m["conta"]) if v > 0 else (m["conta"], bco)
                w.append([m["data"], bco, m["descricao"], m.get("documento", ""), float(v), deb, cred,
                          "; ".join(f"{c}={br(x)}" for c, x in (m.get("partidas") or [])), m["status"], m["obs"], m["id"],
                          m.get("par", ""), m.get("cp_razao", "")])
                if m["status"] == "SEM PROVA": w.cell(w.max_row, 9).fill = verm
        w = wb.create_sheet("Ligação 544")
        w.append(["empresa", "data", "histórico", "valor", "perna 544 (D+ / C-)", "par", "status", "obs"])
        for emp in EMPRESAS:
            for m in lanc[emp]:
                if m.get("omitido"): continue
                for c, x in self.pernas(m, emp):
                    if c == "544":
                        w.append([emp, m["data"], m["descricao"], float(m["valor"]), float(x), m.get("par", ""), m["status"], m["obs"]])
        w.append([]); w.append(["Saldo acumulado 544 34", float(self.s544["34"])]); w.append(["Saldo acumulado 544 118", float(self.s544["118"])])
        w.append(["Soma (deve zerar ou bater com pendências)", float(self.s544["34"] + self.s544["118"])])
        w = wb.create_sheet("Pendências")
        w.append(["tipo", "empresa", "data", "valor", "histórico", "ação"])
        for p in pend:
            w.append([p["tipo"], p["empresa"], p["data"], float(p["valor"]), p["descricao"], p["acao"]])
        for emp in EMPRESAS:
            for m in lanc[emp]:
                if not m.get("omitido") and m["status"] == "SEM PROVA":
                    w.append(["Sem prova (confirmar classificação)", emp, m["data"], float(m["valor"]), m["descricao"], m["obs"]])
        for s in wb.worksheets:
            for col in s.columns:
                s.column_dimensions[col[0].column_letter].width = min(60, max(10, max(len(str(c.value or "")) for c in col) + 2))
        wb.save(pasta / f"Conferencia_Mtz_Fl_{iso(comp)}.xlsx")
        falhas = [f"({t[0]}) {t[1]}: {t[3]}" for t in travas if not t[2]]
        self.resumo.append((comp, ok, falhas, cont))
        print(f"{comp}: {'LIBERADO' if ok else 'BLOQUEADO'} | " + " | ".join(f"{k[0]} {k[1]}={n}" for k, n in sorted(cont.items())))
        for f_ in falhas: print("   trava " + f_)

    def periodo(self):
        for comp in sorted(self.f["meses"], key=lambda c: (c[3:], c[:2])):
            self.mes(comp)
        estado = {"saldos_bancos": {e: {k: str(v) for k, v in self.saldo[e].items()} for e in EMPRESAS},
                  "saldo_506_credor": {e: str(self.s506[e]) for e in EMPRESAS},
                  "saldo_544": {e: str(self.s544[e]) for e in EMPRESAS},
                  "pendencias_544": [{"empresa_faltando": e, "valor": str(x), "data": p["data"], "tipo": p["tipo"]} for e, x, p in self.pend_544]}
        (self.saida / "estado_final.json").write_text(json.dumps(estado, ensure_ascii=False, indent=1), encoding="utf-8")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sp = ap.add_subparsers(dest="cmd", required=True)
    for nome in ("razao-xls", "razao-pdf"):
        p = sp.add_parser(nome); p.add_argument("entrada"); p.add_argument("-o", "--saida", required=True)
    p = sp.add_parser("periodo"); p.add_argument("--fontes", required=True); p.add_argument("--saida", required=True)
    p.add_argument("--previa", action="store_true", help="grava PREVIA_*.txt mesmo com trava falhando (só para revisão)")
    a = ap.parse_args()
    if a.cmd == "razao-xls": cmd_razao_xls(a)
    elif a.cmd == "razao-pdf": cmd_razao_pdf(a)
    else:
        m = Motor(a.fontes, a.saida, a.previa); m.periodo()
        sys.exit(0 if all(ok for _, ok, _, _ in m.resumo) else 2)


if __name__ == "__main__":
    main()
