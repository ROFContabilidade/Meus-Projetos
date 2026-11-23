# -*- coding: utf-8 -*-
"""Regras de conferência do Emissor ROF.

Cada regra devolve um item {"nivel": "erro"|"aviso", "campo": ..., "msg": ...}.
ERRO bloqueia a emissão. AVISO aparece na ficha de emissão e pede atenção.

As regras marcadas com um código (E0121, E0710...) reproduzem regras oficiais do
Anexo I (RN DPS_NFS-e) v1.01 de 09/02/2026 e das Perguntas Frequentes v1.4 de
18/11/2026. As demais são cuidados da ROF (vieram do prompt da Rosângela).
"""
import re
import unicodedata
from datetime import date, datetime
from decimal import Decimal, InvalidOperation

VERSAO = "1.0"

OP_SIMP_NAC = {1: "Não optante", 2: "MEI", 3: "ME/EPP do Simples Nacional"}
REG_AP_TRIB_SN = {
    1: "Tributos federais e municipal pelo Simples Nacional",
    2: "Federais pelo Simples; ISSQN fora (pela NFS-e)",
    3: "Federais e ISSQN fora do Simples (pela NFS-e)",
}
REG_ESP_TRIB = {0: "Nenhum", 1: "Ato cooperado", 2: "Estimativa", 3: "Microempresa municipal",
                4: "Notário ou registrador", 5: "Profissional autônomo", 6: "Sociedade de profissionais", 9: "Outros"}
TRIB_ISSQN = {1: "Operação tributável", 2: "Imunidade", 3: "Exportação de serviço", 4: "Não incidência"}
TP_RET_ISSQN = {1: "Não retido", 2: "Retido pelo tomador", 3: "Retido pelo intermediário"}

# Data a partir da qual o Simples Nacional passa a destacar IBS/CBS (FAQ 15.4 e 20.4).
INICIO_IBSCBS_SIMPLES = date(2027, 1, 1)

TERMOS_PROIBIDOS_PADRAO = ["diagnostico", "diagnosticado", "cid", "cid-10", "cid-11", "hipotese diagnostica",
                           "transtorno", "depressao", "ansiedade", "autismo", "tea", "tdah", "hiv", "cancer",
                           "esquizofrenia", "bipolar"]
PADRAO_CID = re.compile(r"\b[A-TV-Z][0-9]{2}(\.[0-9]{1,2})?\b")


def so_digitos(s):
    return re.sub(r"\D", "", str(s or ""))


def sem_acento(s):
    return "".join(c for c in unicodedata.normalize("NFD", str(s or "")) if unicodedata.category(c) != "Mn").lower()


def cpf_valido(cpf):
    c = so_digitos(cpf)
    if len(c) != 11 or c == c[0] * 11:
        return False
    for n in (9, 10):
        soma = sum(int(c[i]) * (n + 1 - i) for i in range(n))
        if (soma * 10 % 11) % 10 != int(c[n]):
            return False
    return True


def cnpj_valido(cnpj):
    c = so_digitos(cnpj)
    if len(c) != 14 or c == c[0] * 14:
        return False
    for n in (12, 13):
        pesos = list(range(n - 7, 1, -1)) + list(range(9, 1, -1))
        soma = sum(int(c[i]) * pesos[i] for i in range(n))
        dv = 11 - soma % 11
        if (0 if dv >= 10 else dv) != int(c[n]):
            return False
    return True


def para_decimal(v):
    """Aceita 1.234,56 | 1234,56 | 1234.56 | 1234. Devolve Decimal com 2 casas ou None."""
    if isinstance(v, (int, Decimal)):
        return Decimal(v).quantize(Decimal("0.01"))
    s = str(v or "").strip().replace("R$", "").replace(" ", "")
    if not s:
        return None
    if "," in s:
        s = s.replace(".", "").replace(",", ".")
    try:
        d = Decimal(s)
    except InvalidOperation:
        return None
    if d != d.quantize(Decimal("0.01")):
        return None  # mais de 2 casas: não arredondo valor fiscal por conta própria
    return d.quantize(Decimal("0.01"))


def para_data(v):
    if isinstance(v, date) and not isinstance(v, datetime):
        return v
    s = str(v or "").strip()
    for fmt in ("%Y-%m-%d", "%d/%m/%Y"):
        try:
            return datetime.strptime(s, fmt).date()
        except ValueError:
            pass
    return None


def limpar_texto(s):
    """Tira caracteres de controle e espaços repetidos; mantém quebras de linha simples."""
    s = str(s or "").replace("\r\n", "\n").replace("\r", "\n")
    s = "".join(c for c in s if c == "\n" or unicodedata.category(c)[0] != "C")
    s = re.sub(r"[ \t]+", " ", s)
    s = re.sub(r"\n{3,}", "\n\n", s)
    return s.strip()


def _item(nivel, campo, msg):
    return {"nivel": nivel, "campo": campo, "msg": msg}


def conferir_ficha_empresa(emp, tabelas=None):
    """Confere a ficha (cadastro) de uma empresa emitente."""
    r = []
    E = lambda c, m: r.append(_item("erro", c, m))
    A = lambda c, m: r.append(_item("aviso", c, m))
    if not cnpj_valido(emp.get("cnpj")):
        E("cnpj", "CNPJ do emitente inválido (dígito verificador não confere).")
    if not str(emp.get("razao") or "").strip():
        E("razao", "Falta a razão social.")
    if not re.fullmatch(r"[0-9]{7}", str(emp.get("municipio_ibge") or "")):
        E("municipio_ibge", "Código IBGE do município do emitente deve ter 7 dígitos.")
    op = emp.get("op_simp_nac")
    if op not in (1, 2, 3):
        E("op_simp_nac", "Informe a situação no Simples Nacional: 1 não optante, 2 MEI, 3 ME/EPP.")
    reg = emp.get("reg_ap_trib_sn")
    if op == 3 and reg not in (1, 2, 3):
        E("reg_ap_trib_sn", "ME/EPP do Simples: informe o regime de apuração (1, 2 ou 3).")
    if op in (1, 2) and reg not in (None, "", 0):
        E("reg_ap_trib_sn", "Regime de apuração do Simples só existe para ME/EPP (regra E0162).")
    esp = emp.get("reg_esp_trib", 0)
    if esp not in REG_ESP_TRIB:
        E("reg_esp_trib", "Regime especial de tributação inválido.")
    if op == 2 and esp != 0:
        E("reg_esp_trib", "MEI não pode ter regime especial de tributação (regra E0174).")
    if op == 3 and reg == 1 and esp != 0:
        E("reg_esp_trib", "ME/EPP com apuração pelo Simples não pode ter regime especial (regra E0175).")
    if not emp.get("certificado_proprio"):
        v = para_data(emp.get("procuracao_validade"))
        if not v:
            E("procuracao_validade", "Sem procuração eletrônica registrada. A ROF só emite pela API com procuração "
                                     "do cliente para o serviço da NFS-e (Portal de Serviços da Receita Federal), "
                                     "ou com o certificado do próprio cliente.")
        else:
            dias = (v - date.today()).days
            if dias < 0:
                E("procuracao_validade", f"Procuração eletrônica vencida em {v.strftime('%d/%m/%Y')}.")
            elif dias <= 30:
                A("procuracao_validade", f"Procuração eletrônica vence em {dias} dia(s) ({v.strftime('%d/%m/%Y')}). Peça a renovação.")
    if not str(emp.get("pasta_notas") or "").strip():
        A("pasta_notas", "Sem pasta do cliente definida: os XML ficarão só na pasta de dados do programa.")
    if not emp.get("servicos"):
        E("servicos", "A ficha não tem nenhum serviço cadastrado.")
    apelidos = set()
    for i, s in enumerate(emp.get("servicos") or []):
        c = f"servicos[{i}]"
        ap = str(s.get("apelido") or "").strip()
        if not ap:
            E(c, "Serviço sem nome (apelido).")
        if ap.lower() in apelidos:
            E(c, f"Dois serviços com o mesmo nome: {ap}.")
        apelidos.add(ap.lower())
        ctn = str(s.get("c_trib_nac") or "")
        if not re.fullmatch(r"[0-9]{6}", ctn):
            E(c, f"{ap}: código de tributação nacional deve ter 6 dígitos (item, subitem e desdobro).")
        elif tabelas and ctn not in tabelas.get("servicos", {}):
            E(c, f"{ap}: código de tributação nacional {ctn} não existe na lista nacional (regra E0310).")
        ctm = str(s.get("c_trib_mun") or "")
        if ctm and (not re.fullmatch(r"[0-9]{3}", ctm) or ctm == "000"):
            E(c, f"{ap}: código de tributação municipal deve ter 3 dígitos e não pode ser 000 (regra E0315).")
        nbs = so_digitos(s.get("c_nbs"))
        if nbs:
            if len(nbs) != 9:
                E(c, f"{ap}: NBS deve ter 9 dígitos.")
            elif tabelas and nbs not in tabelas.get("nbs", {}):
                E(c, f"{ap}: NBS {nbs} não existe na tabela oficial (regra E0316).")
        tiss = s.get("trib_issqn", 1)
        if tiss not in TRIB_ISSQN:
            E(c, f"{ap}: tributação do ISSQN inválida.")
        ret = s.get("tp_ret_issqn", 1)
        if ret not in (1, 2):
            E(c, f"{ap}: retenção do ISSQN deve ser 1 (não retido) ou 2 (retido pelo tomador). "
                 "Retenção pelo intermediário não é atendida por este programa.")
        if op == 2 and ret != 1:
            E(c, f"{ap}: MEI não pode ter ISSQN retido (regra E0583).")
        if esp != 0 and ret != 1:
            E(c, f"{ap}: regime especial de tributação não admite retenção do ISSQN (regra E0588).")
        pal = s.get("p_aliq")
        if pal not in (None, ""):
            d = para_decimal(pal)
            if d is None or d < 0:
                E(c, f"{ap}: alíquota do ISSQN inválida.")
            elif d > Decimal("5.00"):
                E(c, f"{ap}: alíquota do ISSQN não pode passar de 5% (regra E0595).")
            if op == 2:
                E(c, f"{ap}: MEI não informa alíquota (regra E0600).")
            if tiss != 1:
                E(c, f"{ap}: não se informa alíquota em imunidade, exportação ou não incidência (regra E0602).")
            if esp != 0:
                E(c, f"{ap}: não se informa alíquota com regime especial de tributação (regra E0604).")
        if op == 3 and reg == 1 and tiss == 1 and esp == 0:
            if ret == 2 and pal in (None, ""):
                E(c, f"{ap}: ME/EPP do Simples com ISSQN retido pelo tomador precisa informar a alíquota do ISSQN "
                     "(regra E0621; a alíquota efetiva de ISS da empresa, mínimo aceito 1,80%).")
            if ret == 1 and pal not in (None, ""):
                E(c, f"{ap}: ME/EPP do Simples sem retenção não informa alíquota do ISSQN, que é apurado no DAS (regra E0625).")
        if op == 3 and reg in (2, 3) and pal not in (None, ""):
            A(c, f"{ap}: com ISSQN apurado fora do Simples e município conveniado, a alíquota vem do município e "
                 "não deve ser informada (regra E0635). Confira.")
        if not nbs:
            A(c, f"{ap}: sem NBS. Não é obrigatório para o Simples em 2026, mas a ROF trata nota sem NBS como erro "
                 "a corrigir, e será exigido com o IBS/CBS.")
        tt = (s.get("tot_trib") or {}).get("tipo")
        if tt not in ("pTotTribSN", "indTotTrib", "pTotTrib"):
            E(c, f"{ap}: defina o 'valor aproximado dos tributos' (pTotTribSN, indTotTrib ou pTotTrib).")
        if tt == "pTotTribSN":
            if op == 2:
                E(c, f"{ap}: MEI não informa a alíquota do Simples (regra E0710). Use 'não informar'.")
            if op == 1:
                E(c, f"{ap}: não optante não usa a alíquota do Simples (regra E0713).")
            d = para_decimal((s.get("tot_trib") or {}).get("valor"))
            if d is None or d <= 0 or d >= 100:
                E(c, f"{ap}: informe a alíquota NOMINAL da faixa do Simples (FAQ 20.5), ex.: 6,00.")
        if tt == "indTotTrib" and op == 1:
            E(c, f"{ap}: não optante não pode usar 'não informar tributos' (regra E0713).")
        if not str(s.get("descricao_modelo") or "").strip():
            A(c, f"{ap}: sem modelo de descrição; a descrição será digitada a cada nota.")
    return r


def localizar_servico(emp, apelido):
    for s in emp.get("servicos") or []:
        if str(s.get("apelido") or "").strip().lower() == str(apelido or "").strip().lower():
            return s
    return None


def conferir_nota(emp, nota, historico=None, hoje=None, tabelas=None):
    """Confere um pedido de emissão contra a ficha da empresa. Devolve a lista de erros e avisos."""
    hoje = hoje or date.today()
    r = [x for x in conferir_ficha_empresa(emp, tabelas) if x["nivel"] == "erro" or x["campo"] == "procuracao_validade"]
    E = lambda c, m: r.append(_item("erro", c, m))
    A = lambda c, m: r.append(_item("aviso", c, m))
    op = emp.get("op_simp_nac")

    serv = localizar_servico(emp, nota.get("servico"))
    if not serv:
        E("servico", "Serviço fora da ficha do cliente. PARE: confirme o enquadramento com a contadora "
                     "e cadastre o serviço na ficha antes de emitir. Venda de produto não é NFS-e.")

    valor = para_decimal(nota.get("valor"))
    if valor is None:
        E("valor", "Valor inválido. Use o formato 1.234,56 (duas casas).")
    elif valor <= 0:
        E("valor", "O valor do serviço deve ser maior que zero.")
    elif valor >= Decimal("100000.00"):
        A("valor", f"Valor alto (R$ {valor}). Confira se não há erro de digitação.")
    desc_inc = para_decimal(nota.get("desconto_incondicionado")) if nota.get("desconto_incondicionado") else None
    if nota.get("desconto_incondicionado") and (desc_inc is None or desc_inc < 0 or (valor and desc_inc >= valor)):
        E("desconto_incondicionado", "Desconto incondicionado inválido (deve ser menor que o valor do serviço).")

    comp = para_data(nota.get("competencia"))
    if not comp:
        E("competencia", "Data de competência inválida (dd/mm/aaaa).")
    else:
        if comp > hoje:
            E("competencia", "A competência não pode ser futura (regra E0015).")
        elif (comp.year, comp.month) != (hoje.year, hoje.month):
            A("competencia", f"Competência {comp.strftime('%m/%Y')} é de mês diferente do atual. "
                             "A regra da ROF é emitir no mês do serviço; confirme que a emissão retroativa é intencional.")
        if op in (2, 3) and comp >= INICIO_IBSCBS_SIMPLES:
            E("competencia", "Competência de 2027 em diante: o Simples Nacional passa a destacar IBS/CBS e este "
                             "programa (versão 1.0) ainda não gera o grupo IBS/CBS. Emita pelo portal até a atualização.")
    if op == 1:
        E("op_simp_nac", "Empresa não optante do Simples: o destaque de IBS/CBS já é exigido desde 01/10/2026 e esta "
                         "versão não gera o grupo IBS/CBS. Emita pelo portal (www.nfse.gov.br) até a atualização.")

    desc = limpar_texto(nota.get("descricao"))
    if not desc:
        E("descricao", "Falta a descrição do serviço.")
    elif len(desc) > 2000:
        E("descricao", f"Descrição com {len(desc)} caracteres; o limite é 2000.")
    else:
        if len(desc) < 10:
            A("descricao", "Descrição muito curta. Descreva o serviço de forma que o tomador reconheça.")
        base = " " + re.sub(r"[^a-z0-9\-]+", " ", sem_acento(desc)) + " "
        proib = [sem_acento(t) for t in (emp.get("termos_proibidos") or TERMOS_PROIBIDOS_PADRAO)]
        achados = sorted({t for t in proib if t and f" {t} " in base})
        if achados:
            E("descricao", "A descrição contém termo de saúde/diagnóstico, que nunca vai na nota: " + ", ".join(achados) + ".")
        if PADRAO_CID.search(desc):
            A("descricao", "A descrição parece conter um código CID (letra + números). Diagnóstico nunca vai na nota.")
        if re.search(r"\[[^\]]*\]|\{[^}]*\}", desc):
            E("descricao", "A descrição ainda tem trecho entre [colchetes] ou {chaves} por preencher.")

    cmun = str(nota.get("cod_mun_prestacao") or emp.get("municipio_ibge") or "")
    if not re.fullmatch(r"[0-9]{7}", cmun):
        E("cod_mun_prestacao", "Código IBGE do município da prestação deve ter 7 dígitos.")
    elif cmun != str(emp.get("municipio_ibge")):
        A("cod_mun_prestacao", "Serviço prestado em município diferente do da empresa: confira o local de incidência "
                               "do ISSQN e a retenção (serviço online = cidade da empresa).")

    tom = nota.get("tomador") or None
    ret = (serv or {}).get("tp_ret_issqn", 1)
    if not tom or not so_digitos(tom.get("doc")):
        if (serv or {}).get("exige_tomador", True):
            E("tomador", "Tomador não identificado. A ficha deste serviço exige tomador com CPF ou CNPJ.")
        else:
            A("tomador", "Nota sem tomador identificado.")
        if ret == 2:
            E("tomador", "Há retenção de ISSQN pelo tomador, então ele precisa de CPF/CNPJ (regra E0204).")
    else:
        doc = so_digitos(tom.get("doc"))
        if len(doc) == 11:
            if not cpf_valido(doc):
                E("tomador.doc", "CPF do tomador inválido (dígito verificador não confere).")
        elif len(doc) == 14:
            if not cnpj_valido(doc):
                E("tomador.doc", "CNPJ do tomador inválido (dígito verificador não confere).")
        else:
            E("tomador.doc", "CPF/CNPJ do tomador deve ter 11 ou 14 dígitos.")
        if doc == so_digitos(emp.get("cnpj")):
            E("tomador.doc", "O tomador é a própria empresa emitente.")
        nome = limpar_texto(tom.get("nome"))
        if not nome:
            E("tomador.nome", "Falta o nome do tomador.")
        elif len(nome) > 300:
            E("tomador.nome", "Nome do tomador passa de 300 caracteres.")
        email = str(tom.get("email") or "").strip()
        if email and not re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", email):
            E("tomador.email", "E-mail do tomador com formato inválido (regra E0247).")
        if email and len(email) > 80:
            E("tomador.email", "E-mail do tomador passa de 80 caracteres.")
        if not email:
            A("tomador.email", "Tomador sem e-mail: o portal não envia a nota; anote como ela será entregue.")
        fone = so_digitos(tom.get("fone"))
        if fone and not 6 <= len(fone) <= 20:
            E("tomador.fone", "Telefone do tomador deve ter de 6 a 20 dígitos.")
        end = tom.get("endereco") or {}
        tem_end = any(str(end.get(k) or "").strip() for k in ("cep", "logradouro", "numero", "bairro", "cod_mun"))
        if len(doc) == 14 and not tem_end:
            E("tomador.endereco", "Tomador com CNPJ precisa de endereço completo (regra E0235).")
        if ret == 2 and not tem_end:
            E("tomador.endereco", "ISSQN retido pelo tomador exige o endereço dele (regra E0237).")
        if tem_end:
            if not re.fullmatch(r"[0-9]{8}", so_digitos(end.get("cep"))):
                E("tomador.endereco.cep", "CEP do tomador deve ter 8 dígitos.")
            if not re.fullmatch(r"[0-9]{7}", str(end.get("cod_mun") or "")):
                E("tomador.endereco.cod_mun", "Código IBGE do município do tomador deve ter 7 dígitos "
                                              "(use o botão de busca do CEP).")
            for k, rot, mx in (("logradouro", "logradouro", 255), ("numero", "número", 60), ("bairro", "bairro", 60)):
                v = limpar_texto(end.get(k))
                if not v:
                    E(f"tomador.endereco.{k}", f"Endereço do tomador: falta {rot} (sem número, escreva S/N).")
                elif len(v) > mx:
                    E(f"tomador.endereco.{k}", f"Endereço do tomador: {rot} passa de {mx} caracteres.")
            if len(limpar_texto(end.get("complemento"))) > 156:
                E("tomador.endereco.complemento", "Complemento passa de 156 caracteres.")

    # Duplicidade: mesma empresa, mesmo tomador, mesmo valor e mesmo mês de competência.
    if historico and valor is not None and comp:
        doc_t = so_digitos((tom or {}).get("doc"))
        for h in historico:
            if h.get("situacao") not in ("AUTORIZADA", "INCERTA"):
                continue
            hc = para_data(h.get("competencia"))
            if (so_digitos(h.get("tomador_doc")) == doc_t and para_decimal(h.get("valor")) == valor
                    and hc and (hc.year, hc.month) == (comp.year, comp.month)):
                quando = h.get("competencia")
                r.append({"nivel": "erro", "campo": "duplicidade", "duplicidade": True,
                          "msg": f"POSSÍVEL NOTA REPETIDA: já existe nota {h.get('situacao')} para este tomador, com o mesmo "
                                 f"valor, na competência {quando} (nº {h.get('n_nfse') or 'a confirmar'}, DPS {h.get('n_dps')}). "
                                 "Só prossiga se for realmente outra prestação."})
                break
    return r
