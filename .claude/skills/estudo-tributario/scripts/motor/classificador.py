"""Classifica vendas e compras nas linhas do simulador e levanta alertas."""
from collections import defaultdict

# Ordem igual à aba 'Dados de Entrada' do simulador (linhas 10 a 20)
LINHAS = [
    # chave, rótulo, anexo, presunção IRPJ, presunção CSLL, CBS, ICMS-ST na compra, ISS
    ("cafe_pacote", "Café em pacote — varejo (NCM 09.01 / 2101.1)", "I", .08, .12, "ZERO", "N", "N"),
    ("cafe_atacado", "Atacado de café (NCM 09.01 / 2101.1)", "I", .08, .12, "ZERO", "N", "N"),
    ("servido", "Café servido, comida e bebida não alcoólica preparada", "I", .08, .12, "REST", "N", "N"),
    ("alcoolica", "Bebida alcoólica (servida ou revenda)", "I", .08, .12, "CHEIA", "S", "N"),
    ("bebida_fria", "Cerveja, água e refrigerante (revenda)", "I", .08, .12, "CHEIA", "S", "N"),
    ("outras_revenda", "Outras mercadorias de revenda", "I", .08, .12, "CHEIA", "N", "N"),
    ("cafe_torrado_proprio", "Café torrado pela própria empresa (indústria)", "II", .08, .12, "ZERO", "N", "N"),
    ("eventos_alimentacao", "Eventos — alimentação preparada", "I", .08, .12, "REST", "N", "N"),
    ("eventos_servico", "Eventos — espaço / organização", "III", .32, .32, "CHEIA", "N", "S"),
    ("cursos", "Cursos e treinamentos", "III", .32, .32, "CHEIA", "N", "S"),
    ("aluguel_maquinas", "Aluguel de máquinas (bens móveis)", "III", .32, .32, "CHEIA", "N", "N"),
]
CHAVES = [l[0] for l in LINHAS]

# Ordem igual à aba 'Compras e Despesas' (linhas 5 a 17)
COMPRAS = [
    ("cafe", "Café comprado (produtor rural ou fornecedor)", "ZERO"),
    ("cesta", "Leite, açúcar e outros itens da cesta básica", "ZERO"),
    ("alcool", "Bebidas alcoólicas compradas", "CHEIA"),
    ("fria", "Cerveja, água e refrigerante comprados", "CHEIA"),
    ("insumos", "Outros insumos e mercadorias (regime normal)", "CHEIA"),
    ("simples", "Compras de fornecedores do Simples", "SIMPLES"),
    ("energia", "Energia elétrica", "CHEIA"),
    ("aluguel_pj", "Aluguel pago a pessoa jurídica", "ALUGUEL"),
    ("aluguel_pf", "Aluguel pago a pessoa física", "ZERO"),
    ("servicos", "Serviços de PJ (manutenção, internet, marketing)", "CHEIA"),
    ("cartao", "Taxas de cartão e tarifas bancárias", "ZERO"),
    ("outras", "Outras despesas sem crédito", "ZERO"),
    ("depreciacao", "Depreciação do ano (só para o Lucro Real)", "ZERO"),
]

CFOP_VENDA = ("51", "61", "54", "64", "71")
CFOP_DEVOL_VENDA = ("1201", "1202", "2201", "2202", "1410", "1411", "2410", "2411")


def _ncm(n):
    return (n or "").replace(".", "")


def eh_cafe(ncm):
    n = _ncm(ncm)
    return n.startswith("0901") or n.startswith("21011")


def cesta_zero(ncm, regras):
    n = _ncm(ncm)
    return any(n.startswith(p) for p in regras["cesta_basica_zero_ncm_prefixos"])


def tem(desc, palavras):
    d = " " + (desc or "").lower() + " "
    return any(p in d for p in palavras)


def linha_venda(item, nota, regras):
    """Decide a linha de receita de um item vendido."""
    ncm, desc = _ncm(item["ncm"]), item["desc"]
    nfce = nota.get("modelo") == "65"
    if eh_cafe(ncm):
        if tem(desc, regras["palavras_servido"]) and not tem(desc, regras["palavras_pacote"]):
            return "servido"
        if not nfce and nota.get("dest_pj"):
            return "cafe_atacado"
        return "cafe_pacote"
    if ncm.startswith("2203") or ncm.startswith("2201") or ncm.startswith("2202"):
        return "bebida_fria"
    if ncm[:4] in ("2204", "2205", "2206", "2207", "2208"):
        return "alcoolica"
    if nfce:  # cafeteria: o que sai na NFC-e e não é café em pacote nem bebida pronta é preparado
        if tem(desc, regras["palavras_pacote"]):
            return "outras_revenda"
        return "servido"
    return "outras_revenda"


def linha_pdv(item, regras):
    ncm, desc = _ncm(item.get("ncm")), item["desc"].lower()
    if ncm:
        return linha_venda({"ncm": ncm, "desc": desc}, {"modelo": "65"}, regras)
    if any(k in desc for k in ("cerveja", "chopp", "chope", "refri", "água", "agua ", "coca", "guaran")):
        return "bebida_fria"
    if any(k in desc for k in ("whisky", "uisque", "vodka", "gin ", "cachaça", "cachaca", "rum ", "vinho", "licor",
                               "tequila", "espumante", "drink", "caipir", "dose", "negroni", "aperol", "spritz")):
        return "alcoolica"
    if tem(desc, regras["palavras_pacote"]) and ("caf" in desc):
        return "cafe_pacote"
    return "servido"


def classificar(notas, eventos, cnpj, regras, pdv=None):
    canceladas = {e["chave"] for e in eventos if e["tipo"] == "110111"}
    receita = defaultdict(float)
    compras = defaultdict(float)
    meses_venda, meses_compra = set(), set()
    det = defaultdict(lambda: defaultdict(float))  # detalhe por linha -> ncm
    sinais = defaultdict(float)
    produtores = defaultdict(float)
    for nt in notas:
        if nt["chave"] in canceladas:
            sinais["canceladas"] += 1
            continue
        saida = nt["emit_doc"] == cnpj and nt.get("tpNF", "1") == "1"
        entrada = nt["dest_doc"] == cnpj and nt["emit_doc"] != cnpj
        for it in nt["itens"]:
            cf, ncm, v = it["cfop"], _ncm(it["ncm"]), it["valor"]
            if saida and cf.startswith(CFOP_VENDA):
                ln = linha_venda(it, nt, regras)
                receita[ln] += v
                det[ln][ncm[:4] or "s/NCM"] += v
                meses_venda.add(nt["data"][:7])
                if not ncm or ncm == "00000000":
                    sinais["venda_sem_ncm"] += v
                if ln == "alcoolica" and nt.get("modelo") == "55" and nt.get("dest_pj"):
                    sinais["atacado_alcool"] += v
                if ncm.startswith("09012") and ln in ("cafe_pacote", "cafe_atacado"):
                    sinais["venda_cafe_torrado"] += v
            elif saida and cf in CFOP_DEVOL_VENDA:
                pass
            elif entrada and cf.startswith(CFOP_VENDA):
                meses_compra.add(nt["data"][:7])
                if nt["emit_pf"]:
                    produtores[nt["emit_nome"]] += v
                    sinais["compra_pf"] += v
                if ncm.startswith("090111") or ncm.startswith("090112"):
                    sinais["compra_cafe_cru"] += v
                    if nt["emit_uf"] == "PR" and it["vicms"] == 0:
                        sinais["cafe_cru_pr_sem_icms"] += v
                if eh_cafe(ncm):
                    compras["cafe"] += v
                elif cesta_zero(ncm, regras):
                    compras["cesta"] += v
                elif ncm[:4] in ("2204", "2205", "2206", "2207", "2208"):
                    compras["alcool"] += v
                elif ncm[:4] in ("2201", "2202", "2203"):
                    compras["fria"] += v
                elif nt["emit_crt"] in ("1", "4"):
                    compras["simples"] += v
                else:
                    compras["insumos"] += v
    origem_receita = "XML"
    if pdv:
        receita_pdv = defaultdict(float)
        for it in pdv:
            receita_pdv[linha_pdv(it, regras)] += it["valor"]
        if sum(receita.values()) == 0:
            receita, origem_receita = receita_pdv, "PDV"
        else:
            sinais["pdv_total"] = sum(receita_pdv.values())
            # o PDV separa melhor servido x pacote dentro do varejo
            varejo = receita["servido"] + receita["cafe_pacote"]
            base = receita_pdv["servido"] + receita_pdv["cafe_pacote"]
            if varejo and base:
                receita["servido"] = varejo * receita_pdv["servido"] / base
                receita["cafe_pacote"] = varejo * receita_pdv["cafe_pacote"] / base
                origem_receita = "XML + PDV (mix servido × pacote)"
    # Torrefação própria: comprou café cru e vendeu torrado
    if sinais["compra_cafe_cru"] > 0 and sinais["venda_cafe_torrado"] > 0:
        for k in ("cafe_pacote", "cafe_atacado"):
            receita["cafe_torrado_proprio"] += receita[k]
            receita[k] = 0.0
        sinais["torrefacao"] = 1
    return {
        "receita": dict(receita), "compras": dict(compras), "detalhe": {k: dict(v) for k, v in det.items()},
        "meses_venda": sorted(m for m in meses_venda if m), "meses_compra": sorted(m for m in meses_compra if m),
        "sinais": dict(sinais), "produtores": dict(produtores), "origem_receita": origem_receita,
    }
