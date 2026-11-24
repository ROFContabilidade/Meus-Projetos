"""Consulta CNPJ na base pública da Receita (BrasilAPI; reserva: publica.cnpj.ws).
Uso: python3 consulta_cnpj.py 43.666.432/0001-49
"""
import json, re, sys, urllib.request


def _get(url):
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read().decode("utf-8"))


def consulta(cnpj):
    c = re.sub(r"\D", "", cnpj)
    try:
        d = _get(f"https://brasilapi.com.br/api/cnpj/v1/{c}")
        return {
            "razao_social": d.get("razao_social"), "nome_fantasia": d.get("nome_fantasia"),
            "situacao": d.get("descricao_situacao_cadastral"), "abertura": d.get("data_inicio_atividade"),
            "municipio": f"{d.get('municipio')}/{d.get('uf')}", "porte": d.get("porte"),
            "simples": d.get("opcao_pelo_simples"), "opcao_simples": d.get("data_opcao_pelo_simples"),
            "exclusao_simples": d.get("data_exclusao_do_simples"), "mei": d.get("opcao_pelo_mei"),
            "cnae_principal": f"{d.get('cnae_fiscal')} {d.get('cnae_fiscal_descricao')}",
            "cnaes_secundarios": [f"{s['codigo']} {s['descricao']}" for s in d.get("cnaes_secundarios") or [] if s.get("codigo")],
            "regime_declarado": d.get("regime_tributario"),
            "socios": [s.get("nome_socio") for s in d.get("qsa") or []],
        }
    except Exception:
        d = _get(f"https://publica.cnpj.ws/cnpj/{c}")
        e = d["estabelecimento"]; sn = d.get("simples") or {}
        return {
            "razao_social": d.get("razao_social"), "nome_fantasia": e.get("nome_fantasia"),
            "situacao": e.get("situacao_cadastral"), "abertura": e.get("data_inicio_atividade"),
            "municipio": f"{e['cidade']['nome']}/{e['estado']['sigla']}",
            "simples": sn.get("simples") == "Sim", "opcao_simples": sn.get("data_opcao_simples"),
            "exclusao_simples": sn.get("data_exclusao_simples"), "mei": sn.get("mei") == "Sim",
            "cnae_principal": f"{e['atividade_principal']['id']} {e['atividade_principal']['descricao']}",
            "cnaes_secundarios": [f"{s['id']} {s['descricao']}" for s in e.get("atividades_secundarias") or []],
            "socios": [s.get("nome") for s in d.get("socios") or []],
        }


if __name__ == "__main__":
    print(json.dumps(consulta(sys.argv[1]), ensure_ascii=False, indent=1))
