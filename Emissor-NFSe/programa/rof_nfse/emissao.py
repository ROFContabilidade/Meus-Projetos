# -*- coding: utf-8 -*-
"""Roteiro da emissão, do pedido até os arquivos salvos.

Ordem fixa (nenhum passo é pulado):
 1. recarrega a ficha da empresa e confere o pedido (regras.py);
 2. trava se houver nota em situação INCERTA da mesma empresa (resolve antes, para não duplicar);
 3. confere certificado, procuração e ambiente;
 4. numera, monta o XML, valida no esquema oficial, assina e autoverifica a assinatura;
 5. grava o XML e o registro PREPARADA antes de enviar;
 6. pergunta ao servidor se aquele Id de DPS já existe (HEAD /dps/{id});
 7. envia; interpreta a resposta; confere a nota devolvida contra o pedido;
 8. grava XML da NFS-e, tenta o DANFSe e registra AUTORIZADA / REJEITADA / INCERTA / NAO_ENVIADA.
"""
from datetime import datetime

from lxml import etree

from . import assinatura, dados, dps, regras, transmissao

PALAVRA_CONFIRMACAO = "EMITIR"
NSN = "{%s}" % dps.NS


def ficha_de_emissao(emp, nota, cfg):
    """A 'ficha de emissão' por tela, como a Rosângela pediu: Pessoas, Serviço, Valores, Emitir."""
    serv = regras.localizar_servico(emp, nota.get("servico")) or {}
    tom = nota.get("tomador") or {}
    end = tom.get("endereco") or {}
    op = emp.get("op_simp_nac")
    tot = serv.get("tot_trib") or {}
    if tot.get("tipo") == "pTotTribSN":
        tot_txt = "Alíquota nominal do Simples: %s%%" % tot.get("valor")
    elif tot.get("tipo") == "pTotTrib":
        tot_txt = "Percentuais: federal %s%%, estadual %s%%, municipal %s%%" % (tot.get("fed"), tot.get("est"), tot.get("mun"))
    else:
        tot_txt = "Não informar"
    valor = regras.para_decimal(nota.get("valor"))
    comp = regras.para_data(nota.get("competencia"))
    tabelas = dados.carregar_tabelas()
    ctn = str(serv.get("c_trib_nac") or "")
    endereco_txt = ""
    if regras.so_digitos(end.get("cep")):
        endereco_txt = "%s, %s%s - %s - CEP %s - município IBGE %s" % (
            end.get("logradouro", ""), end.get("numero", ""), (" " + end["complemento"]) if end.get("complemento") else "",
            end.get("bairro", ""), regras.so_digitos(end.get("cep")), end.get("cod_mun", ""))
    return [
        {"tela": "Pessoas", "campos": [
            ["Emitente (prestador)", "%s - CNPJ %s" % (emp.get("razao", ""), emp.get("cnpj", ""))],
            ["Município emissor (IBGE)", "%s %s" % (emp.get("municipio_ibge", ""), emp.get("municipio_nome", ""))],
            ["Simples Nacional", regras.OP_SIMP_NAC.get(op, "?")],
            ["Regime de apuração", regras.REG_AP_TRIB_SN.get(emp.get("reg_ap_trib_sn"), "não se aplica")],
            ["Regime especial", regras.REG_ESP_TRIB.get(emp.get("reg_esp_trib", 0), "?")],
            ["Tomador", ("%s - %s" % (tom.get("nome", ""), tom.get("doc", ""))) if regras.so_digitos(tom.get("doc")) else "NÃO IDENTIFICADO"],
            ["E-mail / telefone do tomador", "%s / %s" % (tom.get("email") or "-", tom.get("fone") or "-")],
            ["Endereço do tomador", endereco_txt or "-"],
        ]},
        {"tela": "Serviço", "campos": [
            ["Serviço da ficha", serv.get("apelido", "FORA DA FICHA")],
            ["Código de tributação nacional", "%s - %s" % (ctn, tabelas.get("servicos", {}).get(ctn, "?"))],
            ["Código de tributação municipal", serv.get("c_trib_mun") or "-"],
            ["NBS", serv.get("c_nbs") or "-"],
            ["Município da prestação (IBGE)", str(nota.get("cod_mun_prestacao") or emp.get("municipio_ibge", ""))],
            ["Descrição", regras.limpar_texto(nota.get("descricao"))],
        ]},
        {"tela": "Valores", "campos": [
            ["Valor do serviço", ("R$ " + "{:,.2f}".format(valor).replace(",", "X").replace(".", ",").replace("X", ".")) if valor is not None else "INVÁLIDO"],
            ["Desconto incondicionado", nota.get("desconto_incondicionado") or "-"],
            ["Tributação do ISSQN", regras.TRIB_ISSQN.get(serv.get("trib_issqn", 1), "?")],
            ["Retenção do ISSQN", regras.TP_RET_ISSQN.get(serv.get("tp_ret_issqn", 1), "?")],
            ["Alíquota do ISSQN", ("%s%%" % serv.get("p_aliq")) if serv.get("p_aliq") not in (None, "") else "não informada"],
            ["Retenções federais (IRRF, CSLL, PIS/Cofins, INSS)", "nenhuma (esta versão não lança retenções federais)"],
            ["IBS/CBS", "não destacado (Simples Nacional, competência até 12/2026)"],
            ["Valor aproximado dos tributos", tot_txt],
        ]},
        {"tela": "Emitir", "campos": [
            ["Competência", comp.strftime("%d/%m/%Y") if comp else "INVÁLIDA"],
            ["Ambiente", "PRODUÇÃO (nota com valor fiscal)" if str(cfg.get("ambiente")) == "1" else "Produção Restrita (TESTE, sem valor fiscal)"],
            ["Série / canal", "série %s, emissão por API" % cfg.get("serie")],
        ]},
    ]


def conferir(nota, cfg):
    emp = dados.carregar_empresa(nota.get("cnpj_emitente"), cfg)
    if not emp:
        return {"ok": False, "itens": [{"nivel": "erro", "campo": "cnpj_emitente",
                                         "msg": "Empresa sem ficha. Cadastre a ficha antes de emitir."}], "ficha": []}
    hist = dados.historico(emp["cnpj"], cfg)
    itens = regras.conferir_nota(emp, nota, hist, tabelas=dados.carregar_tabelas())
    incertas = [h for h in hist if h.get("situacao") == "INCERTA"]
    if incertas:
        itens.insert(0, {"nivel": "erro", "campo": "incerta",
                         "msg": "Há %d envio(s) desta empresa com resultado INCERTO (DPS %s). Resolva no Histórico "
                                "(botão Conferir no servidor) antes de emitir outra nota." %
                                (len(incertas), ", ".join(str(h.get("n_dps")) for h in incertas))})
    xml_previa = ""
    if not any(i["nivel"] == "erro" and not i.get("duplicidade") for i in itens):
        try:
            raiz, _ = dps.montar_dps(emp, nota, cfg["serie"], 1, cfg["ambiente"])
            falhas = dps.validar_xsd(raiz, dados.pasta_schemas(cfg.get("ambiente")))
            for f in falhas:
                itens.append({"nivel": "erro", "campo": "xsd", "msg": "O XML não passou no esquema oficial: " + f})
            xml_previa = etree.tostring(raiz, pretty_print=True, encoding="unicode")
        except Exception as e:  # nunca deixa a conferência quebrar sem explicar
            itens.append({"nivel": "erro", "campo": "xml", "msg": "Não foi possível montar o XML: %s" % e})
    return {"ok": not any(i["nivel"] == "erro" for i in itens), "itens": itens,
            "ficha": ficha_de_emissao(emp, nota, cfg), "xml_previa": xml_previa,
            "so_duplicidade": bool(itens) and all(i["nivel"] != "erro" or i.get("duplicidade") for i in itens)}


def _texto(no, caminho):
    e = no.find(caminho)
    return (e.text or "").strip() if e is not None else ""


def ler_nfse(xml_nfse):
    """Extrai da NFS-e devolvida os dados usados na conferência pós-emissão."""
    doc = etree.fromstring(xml_nfse, etree.XMLParser(resolve_entities=False, no_network=True))
    inf = doc.find(NSN + "infNFSe")
    if inf is None:
        raise ValueError("XML devolvido não é uma NFS-e.")
    idp = inf.find(NSN + "DPS/" + NSN + "infDPS")
    d = {"n_nfse": _texto(inf, NSN + "nNFSe"), "id_nfse": inf.get("Id") or "",
         "c_stat": _texto(inf, NSN + "cStat"), "dh_proc": _texto(inf, NSN + "dhProc"),
         "v_liq": _texto(inf, NSN + "valores/" + NSN + "vLiq")}
    if idp is not None:
        d.update({"id_dps": idp.get("Id") or "",
                  "prest": _texto(idp, NSN + "prest/" + NSN + "CNPJ"),
                  "toma": _texto(idp, NSN + "toma/" + NSN + "CNPJ") or _texto(idp, NSN + "toma/" + NSN + "CPF"),
                  "v_serv": _texto(idp, NSN + "valores/" + NSN + "vServPrest/" + NSN + "vServ"),
                  "d_compet": _texto(idp, NSN + "dCompet")})
    return d


def _conferir_devolvida(lida, emp, nota, ident):
    """Confere a nota autorizada contra o pedido. Devolve lista de divergências (vazia = tudo certo)."""
    div = []
    if lida.get("id_dps") and lida["id_dps"] != ident:
        div.append("Id da DPS devolvido (%s) difere do enviado (%s)." % (lida["id_dps"], ident))
    if lida.get("prest") and lida["prest"] != regras.so_digitos(emp["cnpj"]):
        div.append("CNPJ do prestador devolvido difere do emitente.")
    doc = regras.so_digitos((nota.get("tomador") or {}).get("doc"))
    if (lida.get("toma") or "") != doc:
        div.append("Tomador devolvido difere do pedido.")
    v = regras.para_decimal(lida.get("v_serv"))
    if v is not None and v != regras.para_decimal(nota.get("valor")):
        div.append("Valor do serviço devolvido (%s) difere do pedido." % lida.get("v_serv"))
    return div


def mensagem_ao_tomador(emp, nota, n_nfse, chave):
    tom = nota.get("tomador") or {}
    return ("Olá, %s.\n\nSegue a Nota Fiscal de Serviço eletrônica (NFS-e) nº %s, emitida por %s, no valor de R$ %s.\n"
            "Em anexo vão o PDF (DANFSe) e o arquivo XML.\n"
            "A autenticidade pode ser conferida em https://www.nfse.gov.br/consultapublica com a chave de acesso:\n%s\n\n"
            "Qualquer dúvida, estamos à disposição.") % (
        (tom.get("nome") or "").split(" ")[0] or "tudo bem", n_nfse, emp.get("razao", ""),
        str(regras.para_decimal(nota.get("valor"))).replace(".", ","), chave)


def emitir(nota, cfg, cert, confirmacao="", confirmo_duplicidade=False, cliente=None):
    """Emite de fato. `cert` é um assinatura.Certificado já aberto. Devolve um dicionário com 'situacao'."""
    passos = []
    falha = lambda msg, **extra: dict({"situacao": "BLOQUEADA", "msg": msg, "passos": passos}, **extra)

    if confirmacao != PALAVRA_CONFIRMACAO:
        return falha("Emissão não confirmada. Digite %s para confirmar." % PALAVRA_CONFIRMACAO)
    erros_cfg = dados.conferir_config(cfg)
    if erros_cfg:
        return falha("Configuração inválida: " + " ".join(erros_cfg))

    res = conferir(nota, cfg)
    erros = [i for i in res["itens"] if i["nivel"] == "erro" and not (i.get("duplicidade") and confirmo_duplicidade)]
    if erros:
        return falha("A conferência encontrou erro(s). Nada foi enviado.", itens=res["itens"])
    passos.append("Pedido conferido contra a ficha: sem erros.")

    emp = dados.carregar_empresa(nota["cnpj_emitente"], cfg)
    ambiente = str(cfg["ambiente"])
    if ambiente == "1" and not emp.get("producao_liberada"):
        return falha("Esta empresa ainda não está liberada para PRODUÇÃO. Faça primeiro uma emissão de teste "
                     "em Produção Restrita e marque 'produção liberada' na ficha.")
    if cert is None:
        return falha("Certificado digital não carregado. Abra o certificado na aba Configuração.")
    if not cert.vigente():
        return falha("Certificado digital vencido em %s." % cert.resumo()["valido_ate"])
    doc_cert = cert.documento_titular()
    cnpj = regras.so_digitos(emp["cnpj"])
    if doc_cert != cnpj and doc_cert[:8] != cnpj[:8] and emp.get("certificado_proprio"):
        return falha("A ficha diz que a empresa emite com certificado próprio, mas o certificado aberto é de outro titular (%s)." % doc_cert)
    passos.append("Certificado vigente (titular %s). %s" % (
        doc_cert or "?", "É o do próprio emitente." if doc_cert == cnpj else "Emissão por procuração eletrônica."))

    serie = int(cfg["serie"])
    numero = dados.proximo_numero(cnpj, serie, cfg)
    raiz, ident = dps.montar_dps(emp, nota, serie, numero, ambiente)
    falhas = dps.validar_xsd(raiz, dados.pasta_schemas(cfg.get("ambiente")))
    if falhas:
        return falha("O XML não passou no esquema oficial: " + "; ".join(falhas))
    assinatura.assinar(raiz, cert, cfg.get("algoritmo_assinatura", "sha1"))
    xml = dps.serializar(raiz)
    falhas = dps.validar_xsd(etree.fromstring(xml), dados.pasta_schemas(cfg.get("ambiente")))
    if falhas:
        return falha("O XML assinado não passou no esquema oficial: " + "; ".join(falhas))
    assinatura.conferir_assinatura(xml)
    passos.append("XML montado (DPS série %d nº %d), válido no esquema oficial, assinado e assinatura conferida." % (serie, numero))

    tom = nota.get("tomador") or {}
    base_reg = {"id_dps": ident, "serie": serie, "n_dps": numero, "ambiente": ambiente,
                "competencia": regras.para_data(nota["competencia"]).isoformat(), "valor": str(regras.para_decimal(nota["valor"])),
                "tomador_doc": regras.so_digitos(tom.get("doc")), "tomador_nome": regras.limpar_texto(tom.get("nome")),
                "servico": nota.get("servico"), "usuario": cfg.get("usuario", ""), "pedido": nota}
    nome_base = "NFSe_%s_DPS-%05d-%d_%s" % (cnpj, serie, numero, dados.nome_seguro(tom.get("nome") or "sem-tomador", 30))
    arqs, _ = dados.salvar_arquivo(emp, nota["competencia"], nome_base + "_DPS-enviada.xml", xml, cfg)
    dados.registrar(cnpj, dict(base_reg, situacao="PREPARADA", arquivos=arqs), cfg)

    cliente = cliente or transmissao.Cliente(cert, ambiente, cfg.get("urls"), cfg.get("ca_bundle") or None)
    try:
        ja = cliente.existe_dps(ident)
    except transmissao.ErroTransmissao as e:
        dados.registrar(cnpj, dict(base_reg, situacao="NAO_ENVIADA", detalhe=str(e)), cfg)
        return {"situacao": "NAO_ENVIADA", "passos": passos, "id_dps": ident,
                "msg": "Não foi possível falar com o servidor ANTES do envio; nada foi emitido. Detalhe: %s" % e}
    if ja and not any(h.get("id_dps") == ident and h.get("situacao") not in ("PREPARADA",) for h in dados.historico(cnpj, cfg)
                      if h is not None):
        # número já usado por OUTRO sistema (portal antigo, prefeitura): nunca é envio nosso. Não emite; orienta.
        dados.registrar(cnpj, dict(base_reg, situacao="NAO_ENVIADA",
                                   detalhe="DPS série %d nº %d já usada por outro sistema." % (serie, numero)), cfg)
        return {"situacao": "NAO_ENVIADA", "passos": passos, "id_dps": ident,
                "msg": ("A DPS série %d nº %d já existe na Receita (outro sistema, ou envio anterior interrompido: "
                        "confira em 'NFS-e Emitidas'). Nada foi enviado agora. "
                        "Informe na ficha da empresa a última DPS usada nessa série (campo 'dps_ja_usadas', ex.: "
                        "{\"%d\": <última>}) e emita de novo." % (serie, numero, serie))}
    if ja:
        dados.registrar(cnpj, dict(base_reg, situacao="INCERTA", detalhe="O servidor informou que este Id de DPS já tem NFS-e."), cfg)
        return {"situacao": "INCERTA", "passos": passos, "id_dps": ident,
                "msg": "O servidor informou que já existe NFS-e para esta DPS. Use 'Conferir no servidor' no Histórico."}
    passos.append("Servidor confirmou que esta DPS ainda não existe.")

    try:
        resp = cliente.enviar_dps(xml)
    except transmissao.ErroTransmissao as e:
        sit = "INCERTA" if e.incerta else "NAO_ENVIADA"
        dados.registrar(cnpj, dict(base_reg, situacao=sit, detalhe=str(e)), cfg)
        return {"situacao": sit, "passos": passos, "id_dps": ident,
                "msg": ("O envio saiu mas a resposta não chegou: a nota PODE ter sido emitida. NÃO emita de novo. "
                        "Vá ao Histórico e clique em 'Conferir no servidor'. Detalhe: %s" % e) if e.incerta else
                       ("Falha antes do envio; nada foi emitido. Detalhe: %s" % e)}

    r = transmissao.interpretar_emissao(resp)
    bruto = resp.texto()
    if not r["autorizada"]:
        if r["erros"] or 400 <= resp.status < 500:
            dados.registrar(cnpj, dict(base_reg, situacao="REJEITADA", erros=r["erros"], status_http=resp.status, resposta=bruto), cfg)
            return {"situacao": "REJEITADA", "passos": passos, "id_dps": ident, "erros": r["erros"], "status_http": resp.status,
                    "msg": "A Sefin Nacional REJEITOU a DPS. Nenhuma nota foi emitida. Veja os motivos.", "resposta": bruto}
        dados.registrar(cnpj, dict(base_reg, situacao="INCERTA", status_http=resp.status, resposta=bruto,
                                   detalhe="Resposta fora do padrão esperado."), cfg)
        return {"situacao": "INCERTA", "passos": passos, "id_dps": ident, "status_http": resp.status, "resposta": bruto,
                "msg": "O servidor respondeu de forma inesperada (HTTP %s). NÃO emita de novo: confira no Histórico." % resp.status}

    return _concluir_autorizada(emp, nota, cfg, cliente, base_reg, nome_base, ident, r["chave"], r["xml_nfse"], passos, r.get("alertas"))


def _concluir_autorizada(emp, nota, cfg, cliente, base_reg, nome_base, ident, chave, xml_nfse, passos, alertas=None):
    cnpj = regras.so_digitos(emp["cnpj"])
    try:
        lida = ler_nfse(xml_nfse)
    except Exception as e:
        lida = {"n_nfse": "", "erro_leitura": str(e)}
    divergencias = _conferir_devolvida(lida, emp, nota, ident) if not lida.get("erro_leitura") else \
        ["Não foi possível ler o XML devolvido (%s)." % lida["erro_leitura"]]
    arquivos, falhas = dados.salvar_arquivo(emp, nota["competencia"], "%s_NFSe-%s.xml" % (nome_base, lida.get("n_nfse") or "autorizada"), xml_nfse, cfg)
    pdf = cliente.baixar_danfse(chave) if cliente else None
    if not pdf:  # API oficial do DANFSe suspensa: gera o PDF a partir do XML autorizado
        try:
            from . import danfse
            pdf = danfse.gerar_pdf(xml_nfse)
            passos.append("DANFSe gerado a partir do XML oficial (API do DANFSe indisponível).")
        except Exception as e:
            passos.append("Não foi possível gerar o DANFSe: %s" % e)
            pdf = None
    if pdf:
        a2, f2 = dados.salvar_arquivo(emp, nota["competencia"], "%s_NFSe-%s_DANFSe.pdf" % (nome_base, lida.get("n_nfse") or ""), pdf, cfg)
        arquivos += a2
        falhas += f2
    dados.registrar(cnpj, dict(base_reg, situacao="AUTORIZADA", chave=chave, n_nfse=lida.get("n_nfse"), arquivos=arquivos,
                               divergencias=divergencias, danfse=bool(pdf), alertas=alertas or [],
                               autorizada_em=datetime.now().isoformat(timespec="seconds")), cfg)
    passos.append("NFS-e nº %s autorizada. XML salvo%s." % (lida.get("n_nfse") or "?", " e DANFSe salvo" if pdf else ""))
    pendencias = []
    if not pdf:
        pendencias.append("Baixar o DANFSe (PDF) na consulta pública https://www.nfse.gov.br/consultapublica com a chave de acesso, "
                          "ou em 'NFS-e Emitidas' no portal, e salvar na pasta do cliente.")
    if falhas:
        pendencias.append("Não consegui gravar em: " + "; ".join(falhas) + ". Há cópia na pasta de dados do programa.")
    pendencias.append("ENVIAR a nota ao tomador (o sistema nacional não envia). Texto pronto abaixo.")
    return {"situacao": "AUTORIZADA", "passos": passos, "id_dps": ident, "chave": chave, "n_nfse": lida.get("n_nfse"),
            "arquivos": arquivos, "divergencias": divergencias, "pendencias": pendencias, "alertas": alertas or [],
            "mensagem_tomador": mensagem_ao_tomador(emp, nota, lida.get("n_nfse") or "?", chave),
            "msg": "NFS-e nº %s emitida%s." % (lida.get("n_nfse") or "?", " em AMBIENTE DE TESTE (sem valor fiscal)" if str(cfg["ambiente"]) != "1" else "")}


def conferir_no_servidor(cnpj, id_dps, cfg, cert, cliente=None):
    """Resolve um envio INCERTO: pergunta ao servidor se a DPS virou nota."""
    hist = [h for h in dados.historico(cnpj, cfg) if h.get("id_dps") == id_dps]
    if not hist:
        return {"situacao": "ERRO", "msg": "DPS não encontrada no histórico."}
    h = hist[0]
    if cert is None:
        return {"situacao": "ERRO", "msg": "Abra o certificado digital na aba Configuração."}
    emp = dados.carregar_empresa(cnpj, cfg)
    cliente = cliente or transmissao.Cliente(cert, h.get("ambiente") or cfg["ambiente"], cfg.get("urls"), cfg.get("ca_bundle") or None)
    try:
        existe = cliente.existe_dps(id_dps)
        if existe is False:
            dados.registrar(cnpj, {"id_dps": id_dps, "situacao": "NAO_GEROU_NOTA",
                                   "detalhe": "Servidor confirmou que esta DPS não gerou NFS-e."}, cfg)
            return {"situacao": "NAO_GEROU_NOTA", "msg": "O servidor confirmou: essa DPS NÃO virou nota. Pode emitir de novo com segurança."}
        chave, _ = cliente.chave_por_dps(id_dps)
        if not chave:
            return {"situacao": "INCERTA", "msg": "O servidor não devolveu a chave de acesso. Consulte 'NFS-e Emitidas' no portal antes de qualquer nova emissão."}
        xml_nfse, _ = cliente.consultar_nfse(chave)
    except transmissao.ErroTransmissao as e:
        return {"situacao": "INCERTA", "msg": "Servidor fora de alcance agora (%s). Tente de novo em alguns minutos." % e}
    if not xml_nfse:
        dados.registrar(cnpj, {"id_dps": id_dps, "situacao": "AUTORIZADA", "chave": chave,
                               "detalhe": "Nota existe; XML ainda não recuperado."}, cfg)
        return {"situacao": "AUTORIZADA", "chave": chave, "msg": "A nota EXISTE (chave %s), mas o XML não veio. Baixe pelo portal." % chave}
    nota = h.get("pedido") or {}
    base_reg = {k: h.get(k) for k in ("id_dps", "serie", "n_dps", "ambiente", "competencia", "valor", "tomador_doc", "tomador_nome", "servico", "usuario", "pedido")}
    nome_base = "NFSe_%s_DPS-%05d-%d_%s" % (regras.so_digitos(cnpj), int(h.get("serie") or 0), int(h.get("n_dps") or 0),
                                             dados.nome_seguro(h.get("tomador_nome") or "sem-tomador", 30))
    return _concluir_autorizada(emp, nota, cfg, cliente, base_reg, nome_base, id_dps, chave, xml_nfse,
                                ["Envio incerto resolvido: a nota existe no servidor."])
