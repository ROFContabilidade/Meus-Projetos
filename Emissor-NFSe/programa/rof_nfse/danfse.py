# -*- coding: utf-8 -*-
"""DANFSe (PDF) gerado a partir do XML oficial da NFS-e devolvido pela Sefin Nacional.

Por que existe: a API oficial do DANFSe (ADN) está suspensa (FAQ 17.8; em 21/11/2026 respondia 503) e,
no portal, cada download do PDF exige validação humana (hCaptcha). O XML autorizado é o documento
fiscal; o DANFSe é só a representação dele. Este módulo desenha o PDF no mesmo arranjo do DANFSe
v2.0 oficial, com a chave de acesso e o endereço da consulta pública, para o tomador conferir a
autenticidade no site do governo. Usa PyMuPDF; se a biblioteca `qrcode` estiver instalada, inclui o QR Code.
"""
from decimal import Decimal

try:
    import pymupdf as fitz  # PyMuPDF (nome novo)
except ImportError:  # versões antigas
    import fitz
from lxml import etree

NS = "{http://www.sped.fazenda.gov.br/nfse}"
URL_CONSULTA = "https://www.nfse.gov.br/ConsultaPublica/?tpc=1&chave="

MUNICIPIOS = {"4107652": ("Fazenda Rio Grande", "PR"), "4106902": ("Curitiba", "PR"), "4105805": ("Colombo", "PR"),
              "4104204": ("Campo Largo", "PR"), "4114302": ("Mandirituba", "PR"), "4209102": ("Joinville", "SC"),
              "4119509": ("Ponta Grossa", "PR"), "4119152": ("Pinhais", "PR"), "4125506": ("São José dos Pinhais", "PR"),
              "4100400": ("Almirante Tamandaré", "PR"), "4101804": ("Araucária", "PR")}
OP_SN = {"1": "Não Optante", "2": "Optante - Microempreendedor Individual (MEI)", "3": "Optante - Microempresa ou Empresa de Pequeno Porte (ME/EPP)"}
REG_SN = {"1": "Regime de apuração dos tributos federais e municipal pelo SN",
          "2": "Regime de apuração dos tributos federais pelo SN e o ISSQN pela NFS-e conforme respectiva legislação municipal do tributo",
          "3": "Regime de apuração dos tributos federais e municipal pela NFS-e conforme respectivas legislações federal e municipal de cada tributo"}
TRIB_ISSQN = {"1": "Operação Tributável", "2": "Imunidade", "3": "Exportação de Serviço", "4": "Não Incidência"}
RET_ISSQN = {"1": "Não Retido", "2": "Retido pelo Tomador", "3": "Retido pelo Intermediário"}


def _t(no, caminho, padrao="-"):
    if no is None:
        return padrao
    e = no.find("/".join(NS + p for p in caminho.split("/")))
    return (e.text or "").strip() if e is not None and e.text else padrao


def _moeda(v):
    try:
        d = Decimal(str(v))
    except Exception:
        return "-"
    s = "{:,.2f}".format(d)
    return "R$ " + s.replace(",", "X").replace(".", ",").replace("X", ".")


def _doc(d):
    d = "".join(c for c in (d or "") if c.isdigit())
    if len(d) == 14:
        return "%s.%s.%s/%s-%s" % (d[:2], d[2:5], d[5:8], d[8:12], d[12:])
    if len(d) == 11:
        return "%s.%s.%s-%s" % (d[:3], d[3:6], d[6:9], d[9:])
    return d or "-"


def _cep(c):
    c = "".join(x for x in (c or "") if x.isdigit())
    return "%s.%s-%s" % (c[:2], c[2:5], c[5:]) if len(c) == 8 else (c or "-")


def _fone(f):
    f = "".join(x for x in (f or "") if x.isdigit())
    if len(f) == 11:
        return "(%s) %s-%s" % (f[:2], f[2:7], f[7:])
    if len(f) == 10:
        return "(%s) %s-%s" % (f[:2], f[2:6], f[6:])
    return f or "-"


def _data(iso, com_hora=False):
    if not iso or iso == "-":
        return "-"
    d = iso[:10].split("-")
    txt = "%s/%s/%s" % (d[2], d[1], d[0]) if len(d) == 3 else iso
    if com_hora and len(iso) >= 19:
        txt += " " + iso[11:19]
    return txt


_IBGE = None


def _tabela_ibge():
    """Tabela completa de municípios do IBGE (tabelas/municipios_ibge.json); carrega uma vez."""
    global _IBGE
    if _IBGE is None:
        import json
        import os
        arq = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "tabelas", "municipios_ibge.json")
        try:
            with open(arq, encoding="utf-8") as f:
                _IBGE = {k: tuple(v) for k, v in json.load(f)["municipios"].items()}
        except (OSError, ValueError, KeyError):
            _IBGE = {}
    return _IBGE


def _mun(cod):
    n, uf = MUNICIPIOS.get(cod or "", None) or _tabela_ibge().get(cod or "", ("", ""))
    return ("%s / %s" % (n, uf)) if n else (cod or "-")


def dados_da_nfse(xml_bytes):
    doc = etree.fromstring(xml_bytes, etree.XMLParser(resolve_entities=False, no_network=True))
    inf = doc.find(NS + "infNFSe")
    dps = inf.find(NS + "DPS/" + NS + "infDPS")
    chave = (inf.get("Id") or "")[3:]
    emit = inf.find(NS + "emit")
    toma = dps.find(NS + "toma")
    prest = dps.find(NS + "prest")
    serv = dps.find(NS + "serv")
    val = dps.find(NS + "valores")
    tot = val.find(NS + "trib/" + NS + "totTrib") if val is not None else None
    r = {
        "chave": chave, "n_nfse": _t(inf, "nNFSe"), "dh_proc": _t(inf, "dhProc"), "x_loc_emi": _t(inf, "xLocEmi"),
        "amb_ger": _t(inf, "ambGer"), "c_stat": _t(inf, "cStat"), "x_trib_nac": _t(inf, "xTribNac"),
        "x_nbs": _t(inf, "xNBS"), "x_loc_prest": _t(inf, "xLocPrestacao"), "x_loc_incid": _t(inf, "xLocIncid"),
        "v_liq": _t(inf, "valores/vLiq"), "tp_amb": _t(dps, "tpAmb"),
        "n_dps": _t(dps, "nDPS"), "serie": _t(dps, "serie"), "dh_emi": _t(dps, "dhEmi"), "d_compet": _t(dps, "dCompet"),
        "e_cnpj": _t(emit, "CNPJ"), "e_nome": _t(emit, "xNome"), "e_im": _t(emit, "IM", ""),
        "e_lgr": _t(emit, "enderNac/xLgr", ""), "e_nro": _t(emit, "enderNac/nro", ""), "e_cpl": _t(emit, "enderNac/xCpl", ""),
        "e_bairro": _t(emit, "enderNac/xBairro", ""), "e_mun": _t(emit, "enderNac/cMun", ""), "e_uf": _t(emit, "enderNac/UF", ""),
        "e_cep": _t(emit, "enderNac/CEP", ""), "e_fone": _t(emit, "fone", "") or _t(prest, "fone", ""),
        "e_email": _t(emit, "email", "") or _t(prest, "email", ""),
        "op_sn": _t(prest, "regTrib/opSimpNac", ""), "reg_sn": _t(prest, "regTrib/regApTribSN", ""),
        "t_doc": _t(toma, "CNPJ", "") or _t(toma, "CPF", ""), "t_nome": _t(toma, "xNome"),
        "t_lgr": _t(toma, "end/xLgr", ""), "t_nro": _t(toma, "end/nro", ""), "t_cpl": _t(toma, "end/xCpl", ""),
        "t_bairro": _t(toma, "end/xBairro", ""), "t_mun": _t(toma, "end/endNac/cMun", ""), "t_cep": _t(toma, "end/endNac/CEP", ""),
        "t_fone": _t(toma, "fone", ""), "t_email": _t(toma, "email", ""),
        "c_trib_nac": _t(serv, "cServ/cTribNac", ""), "c_nbs": _t(serv, "cServ/cNBS", ""), "desc": _t(serv, "cServ/xDescServ", ""),
        "c_loc_prest": _t(serv, "locPrest/cLocPrestacao", ""),
        "v_serv": _t(val, "vServPrest/vServ", "0"), "trib_issqn": _t(val, "trib/tribMun/tribISSQN", ""),
        "ret_issqn": _t(val, "trib/tribMun/tpRetISSQN", ""),
        "p_fed": _t(tot, "pTotTrib/pTotTribFed", ""), "p_est": _t(tot, "pTotTrib/pTotTribEst", ""),
        "p_mun": _t(tot, "pTotTrib/pTotTribMun", ""), "p_sn": _t(tot, "pTotTribSN", ""),
    }
    return r


def _qr_png(texto):
    try:
        import io
        import qrcode
        img = qrcode.make(texto, box_size=4, border=1)
        b = io.BytesIO()
        img.save(b, format="PNG")
        return b.getvalue()
    except Exception:
        return None


def gerar_pdf(xml_bytes):
    d = dados_da_nfse(xml_bytes)
    pdf = fitz.open()
    pg = pdf.new_page(width=595, height=842)  # A4 em pontos
    M, W = 28, 595 - 56
    y = [M]
    preto = (0, 0, 0)
    cinza = (0.93, 0.93, 0.93)

    def txt(x, yy, s, tam=7, negrito=False, largura=None):
        fonte = "hebo" if negrito else "helv"
        s = str(s if s not in (None, "") else "-")
        if largura:
            while fitz.get_text_length(s, fontname=fonte, fontsize=tam) > largura and len(s) > 3:
                s = s[:-4] + "..."
        pg.insert_text((x, yy), s, fontname=fonte, fontsize=tam, color=preto)

    def caixa(h, titulo=None):
        r = fitz.Rect(M, y[0], M + W, y[0] + h)
        pg.draw_rect(r, color=preto, width=0.6)
        if titulo:
            pg.draw_rect(fitz.Rect(M, y[0], M + W, y[0] + 11), color=preto, fill=cinza, width=0.6)
            txt(M + 4, y[0] + 8.2, titulo, 7.5, True)
        return r

    def campo(col, lin, rot, val, ncols=4, largura=None, base=None):
        cw = W / ncols
        x = M + 4 + col * cw
        yy = (base or y[0]) + lin
        txt(x, yy, rot, 6.2, True)
        txt(x, yy + 8, val, 7.2, False, largura or (cw - 8))

    # Cabeçalho
    caixa(46)
    txt(M + 6, y[0] + 20, "NFS-e", 20, True)
    txt(M + 6, y[0] + 31, "Nota Fiscal de Serviço Eletrônica", 7)
    txt(M + 205, y[0] + 17, "DANFSe v2.0", 11, True)
    txt(M + 182, y[0] + 29, "Documento Auxiliar da NFS-e", 9, True)
    txt(M + 395, y[0] + 14, "Município: %s - %s" % (d["x_loc_emi"], d["e_uf"] or "PR"), 8.5)
    txt(M + 395, y[0] + 24, "Ambiente Gerador: %s" % d["amb_ger"], 6.5)
    txt(M + 395, y[0] + 32, "Tipo de Ambiente: %s" % ("1 (Produção)" if d["tp_amb"] == "1" else d["tp_amb"] + " (TESTE - sem valor fiscal)"), 6.5)
    y[0] += 46

    # Identificação
    r = caixa(92)
    b = y[0]
    txt(M + 4, b + 9, "CHAVE DE ACESSO DA NFS-e", 6.5, True)
    txt(M + 4, b + 18, d["chave"], 8)
    campo(0, 30, "NÚMERO DA NFS-e", d["n_nfse"], base=b)
    campo(1, 30, "COMPETÊNCIA DA NFS-e", _data(d["d_compet"]), base=b)
    campo(2, 30, "DATA E HORA DA EMISSÃO DA NFS-e", _data(d["dh_proc"], True), base=b)
    campo(0, 50, "NÚMERO DA DPS", d["n_dps"], base=b)
    campo(1, 50, "SÉRIE DA DPS", d["serie"], base=b)
    campo(2, 50, "DATA E HORA DA EMISSÃO DA DPS", _data(d["dh_emi"], True), base=b)
    campo(0, 70, "EMITENTE DA NFS-e", "Prestador", base=b)
    campo(1, 70, "SITUAÇÃO DA NFS-e", "NFS-e Gerada" if d["c_stat"] == "100" else d["c_stat"], base=b)
    campo(2, 70, "FINALIDADE", "NFS-e regular", base=b)
    qr = _qr_png(URL_CONSULTA + d["chave"])
    if qr:
        pg.insert_image(fitz.Rect(M + W - 78, b + 4, M + W - 6, b + 76), stream=qr)
    else:
        txt(M + W - 132, b + 32, "Autenticidade: consulte a chave", 6, True)
        txt(M + W - 132, b + 40, "de acesso no portal nacional", 6, True)
        txt(M + W - 132, b + 48, "www.nfse.gov.br/consultapublica", 6)
    y[0] += 92

    # Prestador
    caixa(66, "PRESTADOR / FORNECEDOR")
    b = y[0] + 12
    end_e = ", ".join(p for p in [d["e_lgr"], d["e_nro"], d["e_cpl"], d["e_bairro"]] if p)
    campo(0, 8, "CNPJ / CPF / NIF", _doc(d["e_cnpj"]), base=b)
    campo(2, 8, "Indicador Municipal (Inscrição)", d["e_im"] or "-", base=b)
    campo(3, 8, "Telefone", _fone(d["e_fone"]), base=b)
    campo(0, 26, "Nome / Nome Empresarial", d["e_nome"], ncols=2, base=b)
    campo(2, 26, "Município / Sigla UF", _mun(d["e_mun"]), base=b)
    campo(3, 26, "Código IBGE / CEP", "%s / %s" % (d["e_mun"], _cep(d["e_cep"])), base=b)
    campo(0, 44, "Endereço", end_e, ncols=2, base=b)
    campo(2, 44, "E-mail", d["e_email"] or "-", largura=W / 2 - 8, base=b)
    y[0] += 66
    caixa(22)
    campo(0, 8, "Simples Nacional na Data de Competência", OP_SN.get(d["op_sn"], d["op_sn"]), ncols=2)
    campo(1, 8, "Regime de Apuração Tributária pelo SN", REG_SN.get(d["reg_sn"], d["reg_sn"] or "-"), ncols=2)
    y[0] += 22

    # Tomador
    caixa(66, "TOMADOR / ADQUIRENTE")
    b = y[0] + 12
    end_t = ", ".join(p for p in [d["t_lgr"], d["t_nro"], d["t_cpl"], d["t_bairro"]] if p)
    campo(0, 8, "CNPJ / CPF / NIF", _doc(d["t_doc"]), base=b)
    campo(2, 8, "Indicador Municipal (Inscrição)", "-", base=b)
    campo(3, 8, "Telefone", _fone(d["t_fone"]), base=b)
    campo(0, 26, "Nome / Nome Empresarial", d["t_nome"], ncols=2, base=b)
    campo(2, 26, "Município / Sigla UF", _mun(d["t_mun"]), base=b)
    campo(3, 26, "Código IBGE / CEP", "%s / %s" % (d["t_mun"] or "-", _cep(d["t_cep"])), base=b)
    campo(0, 44, "Endereço", end_t or "-", ncols=2, base=b)
    campo(2, 44, "E-mail", d["t_email"] or "-", largura=W / 2 - 8, base=b)
    y[0] += 66
    caixa(20)
    txt(M + 175, y[0] + 8, "DESTINATÁRIO DA OPERAÇÃO NÃO IDENTIFICADO NA NFS-e", 7)
    txt(M + 175, y[0] + 17, "INTERMEDIÁRIO DA OPERAÇÃO NÃO IDENTIFICADO NA NFS-e", 7)
    y[0] += 20

    # Serviço
    linhas = (d["desc"] or "").splitlines() or ["-"]
    h_desc = 12 + 9 * len(linhas)
    caixa(46 + h_desc, "SERVIÇO PRESTADO")
    b = y[0] + 12
    ctn = d["c_trib_nac"]
    ctn_txt = "%s.%s.%s" % (ctn[:2], ctn[2:4], ctn[4:6]) if len(ctn) == 6 else ctn
    nbs = d["c_nbs"]
    nbs_txt = "%s.%s.%s.%s" % (nbs[0], nbs[1:5], nbs[5:7], nbs[7:]) if len(nbs) == 9 else nbs
    campo(0, 8, "Código de Tributação Nacional", "%s - %s" % (ctn_txt, d["x_trib_nac"]), base=b)
    campo(1, 8, "Código da NBS", nbs_txt, base=b)
    campo(2, 8, "Local da Prestação / Sigla UF / País", "%s / BR" % _mun(d["c_loc_prest"]), largura=W / 2 - 8, base=b)
    txt(M + 4, b + 30, "Descrição do Serviço", 6.2, True)
    for i, l in enumerate(linhas):
        txt(M + 4, b + 39 + 9 * i, l, 7.4, False, W - 10)
    y[0] += 46 + h_desc

    # Tributação municipal
    caixa(42, "TRIBUTAÇÃO MUNICIPAL (ISSQN)")
    b = y[0] + 12
    campo(0, 8, "Tipo de Tributação do ISSQN", TRIB_ISSQN.get(d["trib_issqn"], d["trib_issqn"]), base=b)
    campo(1, 8, "Município de Incidência do ISSQN", d["x_loc_incid"], base=b)
    campo(2, 8, "Regime Especial de Tributação", "Nenhum", base=b)
    campo(3, 8, "Retenção do ISSQN", RET_ISSQN.get(d["ret_issqn"], d["ret_issqn"]), base=b)
    txt(M + 4, b + 27, "ISSQN apurado pelo Simples Nacional (sem destaque de alíquota nesta NFS-e).", 6.5)
    y[0] += 42

    # Tributação federal
    caixa(30, "TRIBUTAÇÃO FEDERAL")
    campo(0, 19, "IRRF / CP / CSLL / PIS / COFINS retidos", "R$ 0,00 (não retidos)", ncols=2)
    campo(1, 19, "PIS / COFINS - situação tributária", "00 - Nenhum", ncols=2)
    y[0] += 30

    # Valor total
    caixa(42, "VALOR TOTAL DA NFS-E")
    b = y[0] + 12
    campo(0, 8, "Valor do Serviço", _moeda(d["v_serv"]), base=b)
    campo(1, 8, "Desconto Incondicionado", "R$ 0,00", base=b)
    campo(2, 8, "Total das Retenções", "R$ 0,00", base=b)
    txt(M + 4 + 3 * W / 4, b + 8, "Valor Líquido da NFS-e", 6.2, True)
    txt(M + 4 + 3 * W / 4, b + 18, _moeda(d["v_liq"]), 9, True)
    y[0] += 42

    # Totais aproximados
    caixa(30, "TOTAIS APROXIMADOS DOS TRIBUTOS")
    v = Decimal(str(d["v_serv"] or "0"))

    def ap(p):
        try:
            return "%s (%s%%)" % (_moeda((v * Decimal(p) / 100).quantize(Decimal("0.01"))), str(p).replace(".", ","))
        except Exception:
            return "-"
    if d["p_sn"] and d["p_sn"] != "-":
        campo(0, 19, "Alíquota nominal do Simples Nacional", ap(d["p_sn"]), ncols=2)
    else:
        campo(0, 19, "Federais", ap(d["p_fed"]), ncols=3)
        campo(1, 19, "Estaduais", ap(d["p_est"]), ncols=3)
        campo(2, 19, "Municipais", ap(d["p_mun"]), ncols=3)
    y[0] += 30

    # Informações complementares
    caixa(40, "INFORMAÇÕES COMPLEMENTARES")
    txt(M + 4, y[0] + 20, "A autenticidade desta NFS-e pode ser verificada pela chave de acesso no portal nacional:", 6.8)
    txt(M + 4, y[0] + 29, URL_CONSULTA + d["chave"], 6.8)
    txt(M + 4, y[0] + 37, "DANFSe gerado a partir do XML oficial da NFS-e autorizada pela Sefin Nacional.", 6.2)
    y[0] += 40

    pdf.set_metadata({"title": "DANFSe %s - NFS-e %s" % (d["e_nome"], d["n_nfse"]), "author": d["e_nome"]})
    saida = pdf.tobytes(garbage=3, deflate=True)
    pdf.close()
    return saida
