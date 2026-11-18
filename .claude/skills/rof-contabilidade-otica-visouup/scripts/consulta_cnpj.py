#!/usr/bin/env python3
"""Consulta o cartão CNPJ em fontes públicas (dados da Receita Federal) e imprime a análise.

Uso: python consulta_cnpj.py 02.967.738/0001-58 [--json dados_cnpj.json]

Fontes, em ordem: BrasilAPI, ReceitaWS, CNPJ.ws (sem chave). Usa só a biblioteca padrão.
"""
import argparse
import json
import re
import sys
import urllib.request

FONTES = [
    ("BrasilAPI", "https://brasilapi.com.br/api/cnpj/v1/{}"),
    ("ReceitaWS", "https://receitaws.com.br/v1/cnpj/{}"),
    ("CNPJ.ws", "https://publica.cnpj.ws/cnpj/{}"),
]


def valida_cnpj(c):
    if len(c) != 14 or c == c[0] * 14:
        return False
    def dv(base, pesos):
        s = sum(int(d) * p for d, p in zip(base, pesos)) % 11
        return "0" if s < 2 else str(11 - s)
    p1 = [5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
    d1 = dv(c[:12], p1)
    d2 = dv(c[:12] + d1, [6] + p1)
    return c[12:] == d1 + d2


def buscar(cnpj):
    erros = []
    for nome, url in FONTES:
        try:
            req = urllib.request.Request(url.format(cnpj), headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=30) as r:
                dados = json.loads(r.read().decode("utf-8"))
            if dados.get("status") == "ERROR":
                erros.append(f"{nome}: {dados.get('message')}")
                continue
            return nome, dados
        except Exception as e:  # tenta a próxima fonte
            erros.append(f"{nome}: {e}")
    raise SystemExit("Não foi possível consultar o CNPJ:\n  " + "\n  ".join(erros))


def normalizar(fonte, d):
    """Converte as respostas das três fontes para um formato único."""
    if fonte == "BrasilAPI":
        return {
            "razao_social": d.get("razao_social"), "nome_fantasia": d.get("nome_fantasia"),
            "situacao": d.get("descricao_situacao_cadastral"), "data_situacao": d.get("data_situacao_cadastral"),
            "inicio_atividade": d.get("data_inicio_atividade"), "natureza_juridica": d.get("natureza_juridica"),
            "porte": d.get("porte"), "capital_social": d.get("capital_social"),
            "matriz_filial": d.get("descricao_identificador_matriz_filial"),
            "endereco": f"{d.get('descricao_tipo_de_logradouro', '')} {d.get('logradouro', '')}, {d.get('numero', '')} "
                        f"{d.get('complemento') or ''} - {d.get('bairro', '')} - {d.get('municipio', '')}/{d.get('uf', '')} "
                        f"CEP {d.get('cep', '')}",
            "telefones": [t for t in (d.get("ddd_telefone_1"), d.get("ddd_telefone_2")) if t],
            "email": d.get("email"),
            "cnae_principal": f"{d.get('cnae_fiscal')} - {d.get('cnae_fiscal_descricao')}",
            "cnaes_secundarios": [f"{c['codigo']} - {c['descricao']}" for c in d.get("cnaes_secundarios") or [] if c.get("codigo")],
            "simples": {"optante": d.get("opcao_pelo_simples"), "inicio": d.get("data_opcao_pelo_simples"),
                        "exclusao": d.get("data_exclusao_do_simples")},
            "mei": {"optante": d.get("opcao_pelo_mei"), "inicio": d.get("data_opcao_pelo_mei"),
                    "exclusao": d.get("data_exclusao_do_mei")},
            "regime_tributario": [f"{r['ano']}: {r['forma_de_tributacao']}" for r in d.get("regime_tributario") or []],
            "socios": [{"nome": s.get("nome_socio"), "cpf_cnpj": s.get("cnpj_cpf_do_socio"),
                        "qualificacao": s.get("qualificacao_socio"), "entrada": s.get("data_entrada_sociedade")}
                       for s in d.get("qsa") or []],
        }
    if fonte == "ReceitaWS":
        return {
            "razao_social": d.get("nome"), "nome_fantasia": d.get("fantasia"),
            "situacao": d.get("situacao"), "data_situacao": d.get("data_situacao"),
            "inicio_atividade": d.get("abertura"), "natureza_juridica": d.get("natureza_juridica"),
            "porte": d.get("porte"), "capital_social": d.get("capital_social"),
            "matriz_filial": d.get("tipo"),
            "endereco": f"{d.get('logradouro', '')}, {d.get('numero', '')} {d.get('complemento', '')} - {d.get('bairro', '')} "
                        f"- {d.get('municipio', '')}/{d.get('uf', '')} CEP {d.get('cep', '')}",
            "telefones": [d.get("telefone")] if d.get("telefone") else [], "email": d.get("email"),
            "cnae_principal": "; ".join(f"{a['code']} - {a['text']}" for a in d.get("atividade_principal") or []),
            "cnaes_secundarios": [f"{a['code']} - {a['text']}" for a in d.get("atividades_secundarias") or []],
            "simples": d.get("simples") or {}, "mei": d.get("simei") or {}, "regime_tributario": [],
            "socios": [{"nome": s.get("nome"), "cpf_cnpj": "", "qualificacao": s.get("qual"), "entrada": ""}
                       for s in d.get("qsa") or []],
        }
    est = d.get("estabelecimento") or {}
    return {
        "razao_social": d.get("razao_social"), "nome_fantasia": est.get("nome_fantasia"),
        "situacao": est.get("situacao_cadastral"), "data_situacao": est.get("data_situacao_cadastral"),
        "inicio_atividade": est.get("data_inicio_atividade"),
        "natureza_juridica": (d.get("natureza_juridica") or {}).get("descricao"),
        "porte": (d.get("porte") or {}).get("descricao"), "capital_social": d.get("capital_social"),
        "matriz_filial": est.get("tipo"),
        "endereco": f"{est.get('tipo_logradouro', '')} {est.get('logradouro', '')}, {est.get('numero', '')} - "
                    f"{est.get('bairro', '')} - {(est.get('cidade') or {}).get('nome', '')}/{(est.get('estado') or {}).get('sigla', '')} "
                    f"CEP {est.get('cep', '')}",
        "telefones": [f"{est.get('ddd1', '')}{est.get('telefone1', '')}"] if est.get("telefone1") else [],
        "email": est.get("email"),
        "cnae_principal": f"{(est.get('atividade_principal') or {}).get('id')} - {(est.get('atividade_principal') or {}).get('descricao')}",
        "cnaes_secundarios": [f"{a.get('id')} - {a.get('descricao')}" for a in est.get("atividades_secundarias") or []],
        "simples": d.get("simples") or {}, "mei": {}, "regime_tributario": [],
        "socios": [{"nome": s.get("nome"), "cpf_cnpj": s.get("cpf_cnpj_socio"),
                    "qualificacao": (s.get("qualificacao_socio") or {}).get("descricao"), "entrada": s.get("data_entrada")}
                   for s in d.get("socios") or []],
    }


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("cnpj")
    p.add_argument("--json", help="grava os dados normalizados neste arquivo")
    a = p.parse_args()
    cnpj = re.sub(r"\D", "", a.cnpj)
    if not valida_cnpj(cnpj):
        raise SystemExit(f"CNPJ inválido (dígito verificador não confere): {a.cnpj}")
    fonte, bruto = buscar(cnpj)
    d = normalizar(fonte, bruto)
    d["cnpj"] = f"{cnpj[:2]}.{cnpj[2:5]}.{cnpj[5:8]}/{cnpj[8:12]}-{cnpj[12:]}"
    d["fonte"] = fonte
    print(json.dumps(d, ensure_ascii=False, indent=1))
    if a.json:
        with open(a.json, "w", encoding="utf-8") as f:
            json.dump(d, f, ensure_ascii=False, indent=1)


if __name__ == "__main__":
    main()
