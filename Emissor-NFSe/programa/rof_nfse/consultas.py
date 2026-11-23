# -*- coding: utf-8 -*-
"""Consultas automáticas a bases públicas, para evitar digitação:
- CNPJ: BrasilAPI (dados públicos do cadastro da Receita Federal).
- CEP: ViaCEP (traz o código IBGE do município, exigido na nota).
Só são enviados o CNPJ ou o CEP consultado. CPF nunca é enviado a lugar nenhum.
São consultas de apoio: o que vale é a conferência da pessoa na ficha de emissão.
"""
import json
import ssl
import urllib.error
import urllib.request

from . import regras


def _get_json(url):
    req = urllib.request.Request(url, headers={"User-Agent": "EmissorROF", "Accept": "application/json"})
    with urllib.request.urlopen(req, timeout=20, context=ssl.create_default_context()) as r:
        return json.loads(r.read().decode("utf-8"))


def consultar_cep(cep):
    cep = regras.so_digitos(cep)
    if len(cep) != 8:
        return {"ok": False, "msg": "CEP deve ter 8 dígitos."}
    try:
        d = _get_json("https://viacep.com.br/ws/%s/json/" % cep)
    except (urllib.error.URLError, OSError, ValueError) as e:
        return {"ok": False, "msg": "Consulta de CEP indisponível (%s). Preencha à mão." % e}
    if d.get("erro"):
        return {"ok": False, "msg": "CEP não encontrado."}
    return {"ok": True, "cep": cep, "logradouro": d.get("logradouro") or "", "bairro": d.get("bairro") or "",
            "municipio": d.get("localidade") or "", "uf": d.get("uf") or "", "cod_mun": d.get("ibge") or ""}


def consultar_cnpj(cnpj):
    cnpj = regras.so_digitos(cnpj)
    if not regras.cnpj_valido(cnpj):
        return {"ok": False, "msg": "CNPJ inválido (dígito verificador não confere)."}
    try:
        d = _get_json("https://brasilapi.com.br/api/cnpj/v1/%s" % cnpj)
    except urllib.error.HTTPError as e:
        return {"ok": False, "msg": "CNPJ não encontrado na consulta pública (HTTP %s)." % e.code}
    except (urllib.error.URLError, OSError, ValueError) as e:
        return {"ok": False, "msg": "Consulta de CNPJ indisponível (%s). Preencha à mão." % e}
    cep = regras.so_digitos(d.get("cep"))
    cod_mun = str(d.get("codigo_municipio_ibge") or "")
    if len(cod_mun) != 7 and len(cep) == 8:   # garante o código IBGE pelo CEP
        c = consultar_cep(cep)
        if c.get("ok"):
            cod_mun = c.get("cod_mun") or cod_mun
    simples, mei = d.get("opcao_pelo_simples"), d.get("opcao_pelo_mei")
    op = 2 if mei else (3 if simples else (1 if simples is False else None))
    return {
        "ok": True, "cnpj": cnpj,
        "razao": d.get("razao_social") or "", "fantasia": d.get("nome_fantasia") or "",
        "situacao": d.get("descricao_situacao_cadastral") or "",
        "email": (d.get("email") or "").lower(), "fone": regras.so_digitos(d.get("ddd_telefone_1")),
        "op_simp_nac_sugerido": op,
        "endereco": {"cep": cep, "logradouro": ((d.get("descricao_tipo_de_logradouro") or "") + " " + (d.get("logradouro") or "")).strip(),
                     "numero": d.get("numero") or "", "complemento": d.get("complemento") or "",
                     "bairro": d.get("bairro") or "", "municipio": d.get("municipio") or "", "uf": d.get("uf") or "",
                     "cod_mun": cod_mun},
    }
