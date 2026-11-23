# -*- coding: utf-8 -*-
"""Monta o XML da DPS (Declaração de Prestação de Serviços) no leiaute nacional v1.01
e confere contra o esquema XSD oficial (pasta schemas, pacote de produção de 09/02/2026).

Escopo da versão 1.0: emitente = prestador (tpEmit 1), tomador no Brasil, optante do
Simples Nacional (MEI ou ME/EPP), sem dedução, sem obra/evento/exportação e sem grupo IBS/CBS.
"""
import os
import re
import shutil
import tempfile
from datetime import datetime, timedelta, timezone

from lxml import etree

from . import regras

NS = "http://www.sped.fazenda.gov.br/nfse"
VER_LEIAUTE = "1.01"
VER_APLIC = "EmissorROF-" + regras.VERSAO
FUSO_BRASILIA = timezone(timedelta(hours=-3))

_schema_cache = {}


def id_dps(cod_mun, inscricao, serie, numero):
    """'DPS' + cód. município (7) + tipo de inscrição (1: 1 CPF, 2 CNPJ) + inscrição (14) + série (5) + número (15)."""
    ins = regras.so_digitos(inscricao)
    tipo = "2" if len(ins) == 14 else "1"
    ident = "DPS" + str(cod_mun) + tipo + ins.zfill(14) + str(int(serie)).zfill(5) + str(int(numero)).zfill(15)
    if len(ident) != 45:
        raise ValueError("Identificador da DPS com tamanho errado: " + ident)
    return ident


def _el(pai, nome, texto=None):
    e = etree.SubElement(pai, "{%s}%s" % (NS, nome))
    if texto is not None:
        e.text = str(texto)
    return e


def _dec(v):
    d = regras.para_decimal(v)
    if d is None:
        raise ValueError("Valor numérico inválido: %r" % (v,))
    return "%.2f" % d


def data_hora_emissao(agora=None, competencia=None):
    """dhEmi no horário de Brasília, com 90 s de folga para o relógio do computador (regra E0008),
    sem cair antes da data de competência (regra E0015)."""
    agora = agora or datetime.now(FUSO_BRASILIA)
    dh = agora - timedelta(seconds=90)
    if competencia and dh.date() < competencia <= agora.date():
        dh = agora
    return dh.replace(microsecond=0)


def montar_dps(emp, nota, serie, numero, ambiente, agora=None):
    """Devolve (raiz lxml, id). Chame regras.conferir_nota antes: aqui só se monta."""
    serv = regras.localizar_servico(emp, nota.get("servico"))
    if serv is None:
        raise ValueError("Serviço fora da ficha.")
    comp = regras.para_data(nota.get("competencia"))
    cnpj = regras.so_digitos(emp["cnpj"])
    cmun_emi = str(emp["municipio_ibge"])
    ident = id_dps(cmun_emi, cnpj, serie, numero)
    op = emp["op_simp_nac"]

    raiz = etree.Element("{%s}DPS" % NS, nsmap={None: NS})
    raiz.set("versao", VER_LEIAUTE)
    inf = _el(raiz, "infDPS")
    inf.set("Id", ident)
    _el(inf, "tpAmb", ambiente)
    _el(inf, "dhEmi", data_hora_emissao(agora, comp).isoformat())
    _el(inf, "verAplic", VER_APLIC)
    _el(inf, "serie", str(int(serie)))
    _el(inf, "nDPS", str(int(numero)))
    _el(inf, "dCompet", comp.isoformat())
    _el(inf, "tpEmit", 1)
    # Em 21/11/2026 a Produção Restrita (Sefin 1.6.0) já usava o leiaute novo, que exige finNFSe aqui e
    # cNBS antes da descrição; a PRODUÇÃO ainda recusava finNFSe. Por isso o leiaute segue o ambiente.
    novo = str(ambiente) == "2"
    if novo:
        _el(inf, "finNFSe", 0)  # 0 = NFS-e regular
    _el(inf, "cLocEmi", cmun_emi)

    # Prestador = emitente: sem nome e sem endereço (regras E0121 e E0128).
    prest = _el(inf, "prest")
    _el(prest, "CNPJ", cnpj)
    if str(emp.get("im") or "").strip():
        _el(prest, "IM", str(emp["im"]).strip())
    if regras.so_digitos(emp.get("fone")):
        _el(prest, "fone", regras.so_digitos(emp["fone"]))
    if str(emp.get("email") or "").strip():
        _el(prest, "email", str(emp["email"]).strip())
    reg = _el(prest, "regTrib")
    _el(reg, "opSimpNac", op)
    if op == 3:
        _el(reg, "regApTribSN", emp["reg_ap_trib_sn"])
    _el(reg, "regEspTrib", emp.get("reg_esp_trib", 0))

    tom = nota.get("tomador") or {}
    doc = regras.so_digitos(tom.get("doc"))
    if doc:
        t = _el(inf, "toma")
        _el(t, "CNPJ" if len(doc) == 14 else "CPF", doc)
        _el(t, "xNome", regras.limpar_texto(tom.get("nome")))
        end = tom.get("endereco") or {}
        if regras.so_digitos(end.get("cep")):
            e = _el(t, "end")
            nac = _el(e, "endNac")
            _el(nac, "cMun", str(end["cod_mun"]))
            _el(nac, "CEP", regras.so_digitos(end["cep"]))
            _el(e, "xLgr", regras.limpar_texto(end.get("logradouro")))
            _el(e, "nro", regras.limpar_texto(end.get("numero")))
            if regras.limpar_texto(end.get("complemento")):
                _el(e, "xCpl", regras.limpar_texto(end.get("complemento")))
            _el(e, "xBairro", regras.limpar_texto(end.get("bairro")))
        if regras.so_digitos(tom.get("fone")):
            _el(t, "fone", regras.so_digitos(tom["fone"]))
        if str(tom.get("email") or "").strip():
            _el(t, "email", str(tom["email"]).strip())

    s = _el(inf, "serv")
    loc = _el(s, "locPrest")
    _el(loc, "cLocPrestacao", str(nota.get("cod_mun_prestacao") or cmun_emi))
    cs = _el(s, "cServ")
    _el(cs, "cTribNac", serv["c_trib_nac"])
    if str(serv.get("c_trib_mun") or "").strip():
        _el(cs, "cTribMun", serv["c_trib_mun"])
    if novo and regras.so_digitos(serv.get("c_nbs")):
        _el(cs, "cNBS", regras.so_digitos(serv["c_nbs"]))
    _el(cs, "xDescServ", regras.limpar_texto(nota.get("descricao")))
    if not novo and regras.so_digitos(serv.get("c_nbs")):
        _el(cs, "cNBS", regras.so_digitos(serv["c_nbs"]))

    v = _el(inf, "valores")
    vs = _el(v, "vServPrest")
    _el(vs, "vServ", _dec(nota["valor"]))
    if nota.get("desconto_incondicionado"):
        dd = _el(v, "vDescCondIncond")
        _el(dd, "vDescIncond", _dec(nota["desconto_incondicionado"]))
    trib = _el(v, "trib")
    tm = _el(trib, "tribMun")
    _el(tm, "tribISSQN", serv.get("trib_issqn", 1))
    _el(tm, "tpRetISSQN", serv.get("tp_ret_issqn", 1))
    if serv.get("p_aliq") not in (None, ""):
        _el(tm, "pAliq", _dec(serv["p_aliq"]))
    tt = _el(trib, "totTrib")
    tot = serv.get("tot_trib") or {}
    if tot.get("tipo") == "pTotTribSN":
        _el(tt, "pTotTribSN", _dec(tot["valor"]))
    elif tot.get("tipo") == "pTotTrib":
        p = _el(tt, "pTotTrib")
        _el(p, "pTotTribFed", _dec(tot.get("fed", 0)))
        _el(p, "pTotTribEst", _dec(tot.get("est", 0)))
        _el(p, "pTotTribMun", _dec(tot.get("mun", 0)))
    else:
        _el(tt, "indTotTrib", 0)
    return raiz, ident


def _schema(pasta_schemas, arquivo):
    """Carrega o esquema oficial. Única adaptação: o padrão da série vem no arquivo oficial como
    '^0{0,4}\\d{1,5}$'. Em XSD puro, '^' e '$' são caracteres literais (nenhuma série passaria); o
    validador do governo os trata como início e fim. Aqui eles são retirados numa cópia temporária,
    só para a conferência local. Os arquivos da pasta schemas ficam intactos."""
    chave = os.path.join(pasta_schemas, arquivo)
    if chave not in _schema_cache:
        tmp = tempfile.mkdtemp(prefix="rofnfse_xsd_")
        try:
            for nome in os.listdir(pasta_schemas):
                if nome.lower().endswith(".xsd"):
                    with open(os.path.join(pasta_schemas, nome), "rb") as f:
                        conteudo = f.read()
                    conteudo = re.sub(rb'(<xs:pattern value=")\^([^"]*)\$(")', rb"\1\2\3", conteudo)
                    with open(os.path.join(tmp, nome), "wb") as f:
                        f.write(conteudo)
            parser = etree.XMLParser(resolve_entities=False, no_network=True)
            _schema_cache[chave] = etree.XMLSchema(etree.parse(os.path.join(tmp, arquivo), parser))
        finally:
            shutil.rmtree(tmp, ignore_errors=True)
    return _schema_cache[chave]


def validar_xsd(raiz, pasta_schemas, arquivo="DPS_v1.01.xsd"):
    """Devolve a lista de falhas de esquema (vazia = XML válido no esquema oficial)."""
    sch = _schema(pasta_schemas, arquivo)
    # Revalida a partir dos bytes, como o servidor fará.
    doc = etree.fromstring(serializar(raiz), etree.XMLParser(resolve_entities=False, no_network=True))
    if sch.validate(doc):
        return []
    return ["linha %s: %s" % (e.line, e.message) for e in sch.error_log]


def serializar(raiz):
    """XML final: UTF-8, com declaração, sem prefixo de namespace e sem espaços entre as tags."""
    return etree.tostring(raiz, xml_declaration=True, encoding="UTF-8")
