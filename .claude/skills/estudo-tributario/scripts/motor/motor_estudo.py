"""Motor do Estudo Tributário — lê a pasta de ENTRADA e grava o estudo na pasta de RESULTADO.

Uso:
  python3 motor_estudo.py <pasta_entrada> <pasta_resultado> [--cnpj 00000000000000] [--grupo-outras 0]

Lê: XML de NF-e/NFC-e (e eventos de cancelamento), PDF do PGDAS-D, OFX, relatório do PDV (xlsx/csv)
e a FICHA_ESTUDO.xlsx (dados que não estão em documento). Gera: relatório PDF, simulador preenchido,
resultado.json, PENDENCIAS.txt e a FICHA_ESTUDO.xlsx pré-preenchida quando faltar algo.
"""
import argparse, glob, json, os, re, subprocess, sys
from collections import Counter
from datetime import date

AQUI = os.path.dirname(os.path.abspath(__file__))
SKILL = os.path.abspath(os.path.join(AQUI, "..", ".."))
sys.path.insert(0, AQUI)
sys.path.insert(0, os.path.join(SKILL, "scripts"))
import leitor, classificador, calculo  # noqa: E402
from classificador import LINHAS, COMPRAS  # noqa: E402

FICHA = [  # (rótulo na ficha, chave)
    ("CNPJ", "cnpj"),
    ("Salários CLT anuais (com 13º e férias)", "salarios"),
    ("Pró-labore anual dos sócios", "prolabore"),
    ("Nº de empregados", "empregados"),
    ("Energia elétrica anual", "energia"),
    ("Aluguel anual", "aluguel"),
    ("Locador do imóvel (PF ou PJ)", "locador"),
    ("Serviços de PJ anuais (manutenção, internet, marketing)", "servicos"),
    ("Taxas de cartão e tarifas bancárias anuais", "cartao"),
    ("Outras despesas anuais", "outras"),
    ("Depreciação anual", "depreciacao"),
    ("Receita anual de eventos — alimentação", "eventos_alimentacao"),
    ("Receita anual de eventos — espaço/organização", "eventos_servico"),
    ("Receita anual de cursos", "cursos"),
    ("Receita anual de aluguel de máquinas", "aluguel_maquinas"),
    ("Receita anual das outras empresas dos mesmos sócios", "grupo_outras"),
]
OBRIGATORIOS = ("salarios", "prolabore", "aluguel", "locador")


def brl(v):
    return "R$ " + f"{v:,.0f}".replace(",", "X").replace(".", ",").replace("X", ".")


def pct(v):
    return f"{v*100:.1f}%".replace(".", ",")


def consulta_cnpj(cnpj):
    try:
        import consulta_cnpj as cc
        return cc.consulta(cnpj)
    except Exception as e:
        return {"erro": str(e)}


def gravar_ficha(caminho, valores):
    from openpyxl import Workbook
    from openpyxl.styles import Font, PatternFill
    wb = Workbook(); ws = wb.active; ws.title = "Ficha"
    ws["A1"] = "Campo"; ws["B1"] = "Valor"; ws["C1"] = "Como preencher"
    for c in ("A1", "B1", "C1"):
        ws[c].font = Font(name="Arial", bold=True)
    for i, (rot, k) in enumerate(FICHA, 2):
        ws.cell(row=i, column=1, value=rot).font = Font(name="Arial")
        c = ws.cell(row=i, column=2, value=valores.get(k))
        c.font = Font(name="Arial", color="0000FF"); c.fill = PatternFill("solid", fgColor="FFFF00")
        ws.cell(row=i, column=3, value="valor anual em R$" if k not in ("cnpj", "locador", "empregados") else "").font = Font(name="Arial", size=9, color="777777")
    ws.column_dimensions["A"].width = 55; ws.column_dimensions["B"].width = 20; ws.column_dimensions["C"].width = 22
    wb.save(caminho)


def preencher_simulador(caminho, empresa, cnpj, regime, R, receita, compras, folha, grupo_outras):
    subprocess.run([sys.executable, os.path.join(SKILL, "scripts", "gerar_simulador.py"), caminho], check=True, capture_output=True)
    from openpyxl import load_workbook
    wb = load_workbook(caminho)
    de, cd, pa = wb["Dados de Entrada"], wb["Compras e Despesas"], wb["Parâmetros"]
    de["B3"], de["B4"], de["B5"], de["B6"] = empresa, cnpj, regime, grupo_outras
    for i, (k, rot, *_r) in enumerate(LINHAS):
        de.cell(row=10 + i, column=1, value=rot)
        de.cell(row=10 + i, column=2, value=round(receita.get(k, 0), 2))
        de.cell(row=10 + i, column=8, value=R["carga_icms_padrao"].get(k, 0))
    de["B24"], de["B25"], de["B26"] = folha.get("salarios", 0), folha.get("prolabore", 0), folha.get("empregados", 0)
    for i, (k, rot, tipo) in enumerate(COMPRAS):
        cd.cell(row=5 + i, column=1, value=rot)
        cd.cell(row=5 + i, column=2, value=round(compras.get(k, 0), 2))
        cd.cell(row=5 + i, column=3, value=tipo)
    pa["B4"], pa["B5"], pa["B6"] = R["cbs"]["aliquota"], R["ibs"]["aliquota"], R["reducao_restaurante"]
    wb.calculation.fullCalcOnLoad = True
    wb.save(caminho)
    rec = sorted(glob.glob("/root/.claude/skills/**/xlsx/scripts/recalc.py", recursive=True))
    if rec:
        subprocess.run([sys.executable, rec[0], caminho, "90"], capture_output=True)
        try:
            wbv = load_workbook(caminho, data_only=True)
            co = wbv["Comparativo"]
            return [co["B12"].value, co["C12"].value, co["D12"].value]
        except Exception:
            return None
    return None


def montar_alertas(cl, info, res, R, ficha, pgdas, ofx, fator):
    A = []  # (nível, texto)
    s = cl["sinais"]
    if not res["simples_permitido"]:
        A.append(("alto", f"Receita do grupo ({brl(res['receita_grupo'])}) acima do limite do Simples ({brl(R['limite_simples'])}) — Simples vedado (LC 123, art. 3º, §4º)."))
    elif res["receita_grupo"] > 0.85 * R["limite_simples"]:
        A.append(("medio", f"Receita do grupo ({brl(res['receita_grupo'])}) perto do limite do Simples de {brl(R['limite_simples'])}."))
    if res["acima_sublimite"]:
        A.append(("medio", "Receita acima do sublimite de R$ 3,6 mi: ICMS e ISS saem do DAS."))
    if s.get("compra_pf"):
        A.append(("alto", f"Compras de produtor rural pessoa física: {brl(s['compra_pf']*fator)}/ano. Funrural estimado de {brl(s['compra_pf']*fator*R['funrural_pf'])}/ano (1,5%) — conferir recolhimento e EFD-Reinf R-2055."))
    if s.get("cafe_cru_pr_sem_icms") and info.get("simples"):
        A.append(("alto", f"Café cru comprado de produtor do PR sem ICMS ({brl(s['cafe_cru_pr_sem_icms']*fator)}/ano). Comprador do Simples encerra o diferimento (RICMS/PR, Anexo VIII, art. 32, V) — conferir o ICMS da operação."))
    if s.get("torrefacao"):
        tem_cnae = "1081" in json.dumps(info.get("cnae_principal", "")) + json.dumps(info.get("cnaes_secundarios", []))
        A.append(("alto", "Compra café cru e vende café torrado: indica torrefação própria (indústria — Anexo II no Simples)." + ("" if tem_cnae else " Falta o CNAE 1081-3/02.") + " Receita de café movida para a linha de indústria — confirmar."))
    if s.get("atacado_alcool") and info.get("simples"):
        A.append(("alto", f"Venda de bebida alcoólica para empresas por NF-e ({brl(s['atacado_alcool']*fator)}/ano): atacado de bebida alcoólica é vedado no Simples (LC 123, art. 17, X) — conferir."))
    cnaes = json.dumps(info.get("cnaes_secundarios", [])) + str(info.get("cnae_principal", ""))
    if cl["receita"].get("alcoolica") and "5611205" not in cnaes.replace("-", "").replace("/", "") and info.get("cnae_principal"):
        A.append(("medio", "Vende bebida alcoólica, mas não tem o CNAE 5611-2/05 (bares). Avaliar inclusão."))
    if (ficha.get("eventos_alimentacao") or ficha.get("eventos_servico")) and not re.search(r"5620|8230", cnaes):
        A.append(("medio", "Faz eventos, mas não tem CNAE de bufê (5620-1/02) ou de eventos (8230-0/01)."))
    if s.get("venda_sem_ncm"):
        A.append(("medio", f"Vendas sem NCM válido ({brl(s['venda_sem_ncm']*fator)}/ano): revisar o cadastro do PDV antes de 2027 (cClassTrib)."))
    if cl["receita"].get("bebida_fria"):
        A.append(("info", "Cerveja, água e refrigerante perdem o monofásico em 2027: revenda passa a ter CBS (com crédito no regime regular)."))
    if cl["receita"].get("alcoolica"):
        A.append(("info", "Bebida alcoólica: Imposto Seletivo vem no custo do fornecedor (MP 1.399/2026); em 2027 ≈ IPI atual, tende a subir a partir de 2028."))
    if pgdas:
        rbt12 = [p["rbt12"] for p in pgdas if p.get("rbt12")]
        if rbt12 and res["receita_total"]:
            ult = rbt12[-1]
            if abs(ult - res["receita_total"]) / max(ult, 1) > 0.15:
                A.append(("medio", f"Receita anualizada dos documentos ({brl(res['receita_total'])}) difere do RBT12 do PGDAS ({brl(ult)}) em mais de 15% — conferir notas faltando ou receita sem nota."))
    if ofx and ofx["creditos"] and res["receita_total"]:
        cred_ano = ofx["creditos"] * (12 / max(len(ofx["meses"]), 1))
        if cred_ano > res["receita_total"] * 1.2:
            A.append(("medio", f"Créditos bancários ({brl(cred_ano)}/ano) bem acima do faturamento — conferir empréstimos, aportes, transferências ou receita sem nota."))
    if res["lucro_estimado"] < 0:
        A.append(("medio", f"Compras e despesas maiores que a receita (lucro estimado {brl(res['lucro_estimado'])}): pode faltar receita nos documentos ou haver compra de estoque/ativo — o Lucro Real fica distorcido."))
    if R["cbs"]["status"] == "a_confirmar":
        A.append(("info", f"Alíquota da CBS usada: {pct(R['cbs']['aliquota'])} — {R['cbs']['obs']}."))
    return A


HTML = """<!doctype html><html lang="pt-BR"><head><meta charset="utf-8"><style>
@page{{size:A4;margin:12mm 14mm}}*{{box-sizing:border-box}}
body{{font-family:"DejaVu Sans",Arial,sans-serif;font-size:9pt;color:#1f2430;line-height:1.38;margin:0}}
h1{{font-size:16pt;color:#1f4e5f;margin:0}}.s{{color:#5d6472;font-size:8.6pt;margin:2px 0 10px}}
h2{{font-size:10.5pt;color:#1f4e5f;margin:13px 0 5px;border-bottom:1px solid #c9d6da;padding-bottom:2px}}
.v{{background:#1f4e5f;color:#fff;border-radius:6px;padding:10px 14px;display:flex;justify-content:space-between;align-items:center}}
.v b{{font-size:14pt}}.v span{{font-size:9pt;opacity:.9}}
table{{width:100%;border-collapse:collapse;font-size:8.6pt}}th{{background:#e8f0f2;color:#1f4e5f;text-align:left;padding:4px 6px}}
td{{border-bottom:1px solid #e6ecee;padding:3.5px 6px}}td.n,th.n{{text-align:right;white-space:nowrap}}
tr.t td{{font-weight:700;background:#f4f8f9}}.best{{color:#1b7a3d;font-weight:700}}
.al{{padding:4px 8px;margin:3px 0;border-radius:3px;border-left:4px solid}}
.alto{{background:#fdf0ef;border-color:#b3261e}}.medio{{background:#fdf6ec;border-color:#e09f3e}}.info{{background:#eef4f5;border-color:#1f4e5f}}
.small{{font-size:7.6pt;color:#6b7280}}ul{{margin:3px 0;padding-left:16px}}
</style></head><body>
<h1>Estudo Tributário 2027</h1>
<div class="s">{empresa} · CNPJ {cnpj_fmt} · {regime_atual} · base: {base} · gerado em {hoje}</div>
<div class="v"><div><span>Regime de menor carga</span><br><b>{melhor}</b></div>
<div style="text-align:right"><span>Economia anual estimada frente a {segundo}</span><br><b>{economia}</b></div></div>
<h2>Comparativo — tributos por ano</h2>
<table><tr><th>Tributo</th><th class="n">Simples</th><th class="n">Presumido</th><th class="n">Real</th></tr>{comp}</table>
<div class="small">Receita anual considerada: {receita} · FGTS igual em todos ({fgts}) · Lucro contábil estimado: {lucro}</div>
<h2>De onde vem a receita</h2>
<table><tr><th>Linha</th><th class="n">Receita/ano</th><th>Simples</th><th>CBS/IBS 2027</th></tr>{rec}</table>
<div class="small">Origem: {origem}{anual}</div>
<h2>O que encontramos</h2>{alertas}
<h2>Premissas e pendências</h2><ul>{pend}</ul>
<div class="small" style="margin-top:10px">Estudo indicativo com as regras vigentes em {regras_data} (LC 214/2025, LC 123/2006, MP 1.399/2026). Valores marcados "a confirmar" dependem de norma ainda não publicada.</div>
</body></html>"""

TRAT = {"ZERO": "Alíquota zero", "REST": "Restaurante (−40%)", "CHEIA": "Alíquota cheia"}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("entrada"); ap.add_argument("saida")
    ap.add_argument("--cnpj"); ap.add_argument("--grupo-outras", type=float)
    ap.add_argument("--regras", default=os.path.join(SKILL, "references", "regras.json"))
    a = ap.parse_args()
    R = json.load(open(a.regras, encoding="utf-8"))
    os.makedirs(a.saida, exist_ok=True)

    notas, eventos, pgdas, pdv, ofxs, ficha, ignorados = [], [], [], None, [], {}, []
    for p in leitor.inventario(a.entrada):
        n = os.path.basename(p).lower(); ext = n.rsplit(".", 1)[-1] if "." in n else ""
        if ext == "xml":
            t, d = leitor.ler_xml(p)
            (notas if t == "nfe" else eventos if t == "evento" else ignorados).append(d if t else n)
        elif ext == "pdf":
            pg = leitor.ler_pgdas(leitor.texto_pdf(p))
            (pgdas.append(pg) if pg else ignorados.append(n))
        elif ext == "ofx":
            ofxs.append(leitor.ler_ofx(p))
        elif ext in ("xlsx", "xls", "csv", "xlsm"):
            if "ficha" in n:
                ficha_raw = leitor.ler_ficha(p)
                ficha = {k: ficha_raw.get(rot) for rot, k in FICHA if ficha_raw.get(rot) not in (None, "")}
            else:
                itens = leitor.ler_pdv(p)
                if itens:
                    pdv = (pdv or []) + itens
                else:
                    ignorados.append(n)
        else:
            ignorados.append(n)

    cnpj = re.sub(r"\D", "", a.cnpj or str(ficha.get("cnpj") or ""))
    if not cnpj:
        cont = Counter()
        for nt in notas:
            cont[nt["emit_doc"]] += 2 if nt["modelo"] == "65" else 1
            cont[nt["dest_doc"]] += 1
        cont.update([p["cnpj"] for p in pgdas if p.get("cnpj") and len(p["cnpj"]) == 14])
        cont.pop("", None)
        cnpj = cont.most_common(1)[0][0] if cont else ""
    info = consulta_cnpj(cnpj) if len(cnpj) == 14 else {}
    empresa = info.get("razao_social") or "Empresa"
    regime_atual = "Simples Nacional" if info.get("simples") else ("Regime normal" if info else "regime não identificado")

    cl = classificador.classificar(notas, eventos, cnpj, R, pdv)
    meses = cl["meses_venda"] or sorted({p["pa"] for p in pgdas if p.get("pa")})
    fator = 12 / len(meses) if meses and len(meses) < 12 else 1.0
    receita = {k: v * fator for k, v in cl["receita"].items()}
    compras = {k: v * fator for k, v in cl["compras"].items()}
    pend = []
    if not sum(receita.values()) and pgdas:
        rpa = [p["rpa"] for p in pgdas if p.get("rpa")]
        if rpa:
            total = sum(rpa) * (12 / len(rpa))
            cp = str(info.get("cnae_principal", ""))
            ln = "servido" if cp.startswith("5611") else "cafe_atacado" if cp[:4] in ("4637", "4621") else "outras_revenda"
            receita = {ln: total}
            pend.append(f"Receita tirada do PGDAS ({len(rpa)} mês(es)) e lançada toda em “{dict((l[0], l[1]) for l in LINHAS)[ln]}”. Mande os XMLs ou o relatório do PDV para separar por tipo.")
    for k in ("eventos_alimentacao", "eventos_servico", "cursos", "aluguel_maquinas"):
        if ficha.get(k):
            receita[k] = float(ficha[k])
    for k_f, k_c in (("energia", "energia"), ("servicos", "servicos"), ("cartao", "cartao"), ("outras", "outras"), ("depreciacao", "depreciacao")):
        if ficha.get(k_f):
            compras[k_c] = float(ficha[k_f])
    if ficha.get("aluguel"):
        alvo = "aluguel_pj" if str(ficha.get("locador", "")).strip().upper().startswith("PJ") else "aluguel_pf"
        compras[alvo] = float(ficha["aluguel"])
    folha = {k: float(ficha.get(k) or 0) for k in ("salarios", "prolabore", "empregados")}
    grupo_outras = a.grupo_outras if a.grupo_outras is not None else float(ficha.get("grupo_outras") or 0)

    faltando = [rot for rot, k in FICHA if k in OBRIGATORIOS and ficha.get(k) in (None, "")]
    if faltando:
        pend.append("Falta na FICHA_ESTUDO: " + "; ".join(faltando) + ". Sem a folha, o Simples fica favorecido artificialmente no comparativo.")
    if not notas and not pdv:
        pend.append("Nenhum XML de venda nem relatório do PDV encontrado.")
    if fator != 1.0:
        pend.append(f"Documentos de {len(meses)} mês(es) ({meses[0]} a {meses[-1]}): valores anualizados ×{fator:.2f}.")
    if not cl["meses_compra"]:
        pend.append("Sem XMLs de compra: créditos de CBS/IBS e alertas de Funrural e ICMS ficam incompletos.")
    pend.append("Carga de ICMS no regime normal estimada por linha (Parâmetros do motor) — confirmar com a apuração real.")
    if ignorados:
        pend.append(f"{len(ignorados)} arquivo(s) não reconhecido(s): " + ", ".join(sorted(set(map(str, ignorados)))[:8]) + ("…" if len(ignorados) > 8 else ""))

    res = calculo.calcular(receita, compras, folha, R, receita_grupo_outras=grupo_outras)
    ofx = None
    if ofxs:
        ofx = {"creditos": sum(o["creditos"] for o in ofxs), "debitos": sum(o["debitos"] for o in ofxs),
               "meses": sorted({m for o in ofxs for m in o["meses"]})}
    alertas = montar_alertas(cl, info, res, R, ficha, pgdas, ofx, fator)

    base_nome = re.sub(r"[^A-Za-z0-9]+", "_", empresa.title()).strip("_")[:40]
    sim = os.path.join(a.saida, f"Simulador_{base_nome}.xlsx")
    totais_xlsx = preencher_simulador(sim, empresa, cnpj, regime_atual, R, receita, compras, folha, grupo_outras)
    conferencia = None
    if totais_xlsx and all(isinstance(x, (int, float)) for x in totais_xlsx):
        py = [res["totais"][k] for k in ("Simples Nacional", "Lucro Presumido", "Lucro Real")]
        conferencia = max(abs(x - y) for x, y in zip(py, totais_xlsx))

    if faltando or not notas and not pdv:
        ficha_vals = {k: ficha.get(k) for _, k in FICHA}; ficha_vals["cnpj"] = cnpj
        gravar_ficha(os.path.join(a.saida, "FICHA_ESTUDO.xlsx"), ficha_vals)

    T = res["regimes"]
    linhas_comp = [("DAS", "Simples Nacional", "DAS")] + [(n, None, n) for n in ("IRPJ", "CSLL", "CBS/IBS", "ICMS", "ISS", "Patronal")]
    comp = ""
    for rot, so, key in linhas_comp:
        vals = [T["Simples Nacional"].get(key, 0), T["Lucro Presumido"].get(key, 0), T["Lucro Real"].get(key, 0)]
        nome = {"Patronal": "Contribuição patronal (INSS + RAT + terceiros)", "DAS": "DAS (inclui CPP, ICMS e ISS)"}.get(rot, rot)
        comp += f"<tr><td>{nome}</td>" + "".join(f'<td class="n">{brl(v) if v else "—"}</td>' for v in vals) + "</tr>"
    tot = [res["totais"][k] for k in ("Simples Nacional", "Lucro Presumido", "Lucro Real")]
    cls = ["best" if k == res["melhor"] else "" for k in ("Simples Nacional", "Lucro Presumido", "Lucro Real")]
    comp += '<tr class="t"><td>Total</td>' + "".join(f'<td class="n {c}">{brl(v)}</td>' for v, c in zip(tot, cls)) + "</tr>"
    comp += '<tr><td>% da receita</td>' + "".join(f'<td class="n">{pct(v/res["receita_total"]) if res["receita_total"] else "—"}</td>' for v in tot) + "</tr>"
    rec = ""
    for l in res["linhas"]:
        if l["receita"]:
            meta = next(x for x in LINHAS if x[0] == l["chave"])
            rec += f'<tr><td>{l["rotulo"]}</td><td class="n">{brl(l["receita"])}</td><td>Anexo {meta[2]}</td><td>{TRAT[meta[5]]}</td></tr>'
    al_html = "".join(f'<div class="al {n}">{t}</div>' for n, t in alertas) or '<div class="al info">Nenhum risco relevante encontrado nos documentos.</div>'
    melhor = res["melhor"] + ("" if res["simples_permitido"] else " (Simples vedado pelo limite)")
    html = HTML.format(
        empresa=empresa, cnpj_fmt=f"{cnpj[:2]}.{cnpj[2:5]}.{cnpj[5:8]}/{cnpj[8:12]}-{cnpj[12:]}" if len(cnpj) == 14 else cnpj,
        regime_atual=regime_atual, base=(f"{meses[0]} a {meses[-1]}" if meses else "ficha"), hoje=date.today().strftime("%d/%m/%Y"),
        melhor=melhor, segundo=res["segundo"] or "—", economia=brl(res["economia"]), comp=comp,
        receita=brl(res["receita_total"]), fgts=brl(res["fgts"]), lucro=brl(res["lucro_estimado"]), rec=rec or "<tr><td colspan=4>—</td></tr>",
        origem=cl["origem_receita"] if cl["receita"] else "PGDAS/ficha", anual=(" · anualizado" if fator != 1 else ""),
        alertas=al_html, pend="".join(f"<li>{p}</li>" for p in pend), regras_data=R["atualizado_em"])
    hp = os.path.join(a.saida, "relatorio.html")
    open(hp, "w", encoding="utf-8").write(html)
    pdf = os.path.join(a.saida, f"Estudo_Tributario_{base_nome}.pdf")
    r = subprocess.run(["node", os.path.join(SKILL, "scripts", "html_para_pdf.js"), os.path.abspath(hp), os.path.abspath(pdf)], capture_output=True, text=True)
    if r.returncode == 0:
        os.remove(hp)

    open(os.path.join(a.saida, "PENDENCIAS.txt"), "w", encoding="utf-8").write(
        "O QUE FALTA PARA FECHAR O ESTUDO\n\n" + "\n".join("- " + p for p in pend) + "\n")
    saida = {"empresa": empresa, "cnpj": cnpj, "regime_atual": regime_atual, "info_cnpj": info,
             "arquivos": {"nfe": len(notas), "eventos": len(eventos), "pgdas": len(pgdas), "pdv_itens": len(pdv or []), "ofx": len(ofxs), "ignorados": len(ignorados)},
             "meses": meses, "fator_anualizacao": fator, "receita": receita, "compras": compras, "folha": folha,
             "resultado": res, "alertas": alertas, "pendencias": pend, "sinais": cl["sinais"], "produtores": cl["produtores"],
             "conferencia_excel_diferenca": conferencia, "regras_data": R["atualizado_em"]}
    json.dump(saida, open(os.path.join(a.saida, "resultado.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1, default=str)
    print(f"{empresa} ({cnpj}) | {res['melhor']} | economia {brl(res['economia'])} | alertas {len(alertas)} | pendências {len(pend)} | PDF {'ok' if r.returncode == 0 else 'ERRO ' + r.stderr[:200]} | conferência Excel {conferencia}")


if __name__ == "__main__":
    main()
