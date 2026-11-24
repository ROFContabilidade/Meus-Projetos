"""Cálculo dos três regimes — mesma lógica das fórmulas do simulador Excel."""
from classificador import LINHAS, COMPRAS


def faixa(rbt, R):
    lim = R["simples"]["limites_inferiores"]
    f = 0
    for i, v in enumerate(lim):
        if rbt >= v:
            f = i
    return f


def aliq_efetiva(rbt, anexo, R):
    if rbt <= 0:
        return 0.0
    t = R["simples"][anexo]
    f = faixa(rbt, R)
    return (rbt * t["aliq"][f] - t["deduz"][f]) / rbt


def calcular(receita, compras, folha, R, icms_carga=None, receita_grupo_outras=0.0):
    """receita: {chave_linha: valor anual}; compras: {chave_compra: valor anual};
    folha: {'salarios':, 'prolabore':}. Retorna dict com os três regimes."""
    cbs, ibs = R["cbs"]["aliquota"], R["ibs"]["aliquota"]
    icms_carga = icms_carga or R["carga_icms_padrao"]
    rbt = sum(receita.get(k, 0) for k, *_ in LINHAS)
    f = faixa(rbt, R)
    das = base_ir = base_cs = deb = icms = iss = 0.0
    linhas = []
    for chave, rot, anexo, pir, pcs, trat, st, tem_iss in LINHAS:
        v = receita.get(chave, 0.0)
        ef = aliq_efetiva(rbt, anexo, R)
        share = R["simples"][anexo]["icms"][f] if st == "S" else 0
        d = v * ef * (1 - share)
        fator = {"ZERO": 0, "REST": 1 - R["reducao_restaurante"], "CHEIA": 1}[trat]
        db = v * (cbs + ibs) * fator
        ic = v * icms_carga.get(chave, 0)
        isv = v * R["iss_padrao"] if tem_iss == "S" else 0
        das += d; base_ir += v * pir; base_cs += v * pcs; deb += db; icms += ic; iss += isv
        linhas.append({"chave": chave, "rotulo": rot, "receita": v, "anexo": anexo, "das": d, "cbs_debito": db})
    extra = max(0, rbt - 5e6) / max(rbt, 1) * R["presuncao_extra_acima_5mi"]["valor"]
    base_ir *= 1 + extra; base_cs *= 1 + extra
    cred = 0.0
    for chave, rot, tipo in COMPRAS:
        v = compras.get(chave, 0.0)
        if tipo == "CHEIA":
            cred += v * (cbs + ibs)
        elif tipo == "ALUGUEL":
            cred += v * (cbs + ibs) * R["credito_aluguel_pj_fracao"]
        elif tipo == "SIMPLES":
            cred += v * R["credito_fornecedor_simples"]
    cbs_liq = max(0.0, deb - cred)
    sal, pro = folha.get("salarios", 0.0), folha.get("prolabore", 0.0)
    patronal = sal * (R["inss_patronal"] + R["rat_ajustado"] + R["terceiros"]) + pro * R["inss_patronal"]
    fgts = sal * R["fgts"]
    irpj_lp = base_ir * R["irpj"] + max(0, base_ir - R["limite_adicional_anual"]) * R["adicional_irpj"]
    csll_lp = base_cs * R["csll"]
    despesas = sum(compras.get(k, 0.0) for k, *_ in COMPRAS)
    lucro = rbt - cbs_liq - icms - iss - despesas - sal - pro - patronal - fgts
    irpj_lr = max(0, lucro) * R["irpj"] + max(0, lucro - R["limite_adicional_anual"]) * R["adicional_irpj"]
    csll_lr = max(0, lucro) * R["csll"]
    grupo = rbt + receita_grupo_outras
    simples_ok = grupo <= R["limite_simples"]
    reg = {
        "Simples Nacional": {"DAS": das},
        "Lucro Presumido": {"IRPJ": irpj_lp, "CSLL": csll_lp, "CBS/IBS": cbs_liq, "ICMS": icms, "ISS": iss, "Patronal": patronal},
        "Lucro Real": {"IRPJ": irpj_lr, "CSLL": csll_lr, "CBS/IBS": cbs_liq, "ICMS": icms, "ISS": iss, "Patronal": patronal},
    }
    totais = {k: sum(v.values()) for k, v in reg.items()}
    candidatos = {k: v for k, v in totais.items() if simples_ok or k != "Simples Nacional"}
    ordem = sorted(candidatos, key=candidatos.get)
    return {
        "receita_total": rbt, "faixa_simples": f + 1, "aliq_efetiva_anexo_I": aliq_efetiva(rbt, "I", R),
        "linhas": linhas, "regimes": reg, "totais": totais, "melhor": ordem[0],
        "economia": candidatos[ordem[1]] - candidatos[ordem[0]] if len(ordem) > 1 else 0,
        "segundo": ordem[1] if len(ordem) > 1 else None,
        "creditos": cred, "cbs_debito": deb, "lucro_estimado": lucro, "fgts": fgts,
        "receita_grupo": grupo, "simples_permitido": simples_ok, "acima_sublimite": rbt > R["sublimite_icms_iss"],
    }
