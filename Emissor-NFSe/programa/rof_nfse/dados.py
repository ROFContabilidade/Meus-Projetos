# -*- coding: utf-8 -*-
"""Arquivos do programa: configuração deste computador, fichas das empresas, histórico e notas.

- Configuração e contador de numeração: ficam NESTE computador (%APPDATA%\\EmissorROF).
- Fichas e histórico: ficam na "pasta de dados", que pode ser uma pasta compartilhada (Google Drive
  da ROF), para todas as pessoas enxergarem as mesmas fichas e o mesmo histórico.
- Cada computador usa uma SÉRIE de DPS diferente (1, 2, 3...). Assim duas pessoas nunca geram o
  mesmo número de DPS para o mesmo cliente, mesmo trabalhando ao mesmo tempo.
"""
import json
import os
import re
import sys
import tempfile
from datetime import datetime

from . import regras


def pasta_programa():
    if getattr(sys, "frozen", False):
        return getattr(sys, "_MEIPASS", os.path.dirname(sys.executable))
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def pasta_local():
    base = os.environ.get("EMISSOR_ROF_LOCAL") or os.path.join(os.environ.get("APPDATA") or os.path.expanduser("~"), "EmissorROF")
    os.makedirs(base, exist_ok=True)
    return base


def _ler_json(caminho, padrao):
    try:
        with open(caminho, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return padrao


def _gravar_json(caminho, obj):
    """Grava em arquivo temporário e troca de uma vez, para nunca deixar arquivo pela metade."""
    os.makedirs(os.path.dirname(caminho), exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=os.path.dirname(caminho), suffix=".tmp")
    with os.fdopen(fd, "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=2)
    os.replace(tmp, caminho)


CONFIG_PADRAO = {
    "pasta_dados": "",          # vazio = pasta local
    "serie": 1,                 # 1 a 49999 (faixa da emissão por API); uma por computador
    "ambiente": "2",            # "2" Produção Restrita (testes) | "1" Produção
    "caminho_pfx": "",
    "algoritmo_assinatura": "sha1",
    "urls": {},                 # sobrepõe os endereços padrão, se preciso
    "ca_bundle": "",
    "usuario": "",
}


def carregar_config():
    cfg = dict(CONFIG_PADRAO)
    cfg.update(_ler_json(os.path.join(pasta_local(), "config.json"), {}))
    return cfg


def conferir_config(cfg):
    erros = []
    try:
        s = int(cfg.get("serie"))
        if not 1 <= s <= 49999:
            erros.append("A série deve ficar entre 1 e 49999 (faixa da emissão por API; FAQ 18.1).")
    except (TypeError, ValueError):
        erros.append("Série inválida.")
    if str(cfg.get("ambiente")) not in ("1", "2"):
        erros.append("Ambiente deve ser 1 (produção) ou 2 (produção restrita).")
    if cfg.get("algoritmo_assinatura") not in ("sha1", "sha256"):
        erros.append("Algoritmo de assinatura deve ser sha1 ou sha256.")
    for nome, u in (cfg.get("urls") or {}).items():
        if isinstance(u, str) and u and not u.startswith("https://"):
            erros.append("Endereço %s precisa começar com https://" % nome)
    return erros


def salvar_config(cfg):
    limpo = {k: cfg.get(k, v) for k, v in CONFIG_PADRAO.items()}
    limpo["serie"] = int(limpo["serie"])
    limpo["ambiente"] = str(limpo["ambiente"])
    _gravar_json(os.path.join(pasta_local(), "config.json"), limpo)
    return limpo


def pasta_dados(cfg=None):
    cfg = cfg or carregar_config()
    p = (cfg.get("pasta_dados") or "").strip() or os.path.join(pasta_local(), "dados")
    os.makedirs(p, exist_ok=True)
    return p


# --- fichas das empresas -------------------------------------------------------------------
def _arq_empresa(cnpj, cfg=None):
    return os.path.join(pasta_dados(cfg), "empresas", regras.so_digitos(cnpj) + ".json")


def listar_empresas(cfg=None):
    pasta = os.path.join(pasta_dados(cfg), "empresas")
    saida = []
    if os.path.isdir(pasta):
        for nome in sorted(os.listdir(pasta)):
            if re.fullmatch(r"\d{14}\.json", nome):
                e = _ler_json(os.path.join(pasta, nome), None)
                if e:
                    saida.append(e)
    return sorted(saida, key=lambda e: str(e.get("razao") or "").lower())


def carregar_empresa(cnpj, cfg=None):
    return _ler_json(_arq_empresa(cnpj, cfg), None)


def salvar_empresa(emp, cfg=None, usuario=""):
    emp = dict(emp)
    emp["cnpj"] = regras.so_digitos(emp.get("cnpj"))
    emp["atualizado_em"] = datetime.now().isoformat(timespec="seconds")
    emp["atualizado_por"] = usuario
    caminho = _arq_empresa(emp["cnpj"], cfg)
    anterior = _ler_json(caminho, None)
    if anterior is not None:  # guarda a versão anterior da ficha antes de trocar
        copia = os.path.join(pasta_dados(cfg), "empresas", "versoes_anteriores",
                             "%s_%s.json" % (emp["cnpj"], datetime.now().strftime("%Y%m%d_%H%M%S")))
        _gravar_json(copia, anterior)
    _gravar_json(caminho, emp)
    return emp


# --- histórico -----------------------------------------------------------------------------
def _arq_historico(cnpj, cfg=None):
    return os.path.join(pasta_dados(cfg), "historico", regras.so_digitos(cnpj) + ".jsonl")


def registrar(cnpj, registro, cfg=None):
    """Acrescenta uma linha ao histórico (nunca apaga nem reescreve linhas antigas)."""
    caminho = _arq_historico(cnpj, cfg)
    os.makedirs(os.path.dirname(caminho), exist_ok=True)
    reg = dict(registro)
    reg["gravado_em"] = datetime.now().isoformat(timespec="seconds")
    with open(caminho, "a", encoding="utf-8") as f:
        f.write(json.dumps(reg, ensure_ascii=False) + "\n")
        f.flush()
        os.fsync(f.fileno())
    return reg


def historico(cnpj, cfg=None):
    """Situação atual de cada DPS (a última linha de cada Id vale), da mais nova para a mais antiga."""
    caminho = _arq_historico(cnpj, cfg)
    por_id = {}
    if os.path.isfile(caminho):
        with open(caminho, "r", encoding="utf-8") as f:
            for linha in f:
                linha = linha.strip()
                if not linha:
                    continue
                try:
                    reg = json.loads(linha)
                except ValueError:
                    continue
                atual = por_id.get(reg.get("id_dps"), {})
                atual.update(reg)
                por_id[reg.get("id_dps")] = atual
    return sorted(por_id.values(), key=lambda r: r.get("gravado_em", ""), reverse=True)


def proximo_numero(cnpj, serie, cfg=None):
    """Próximo número de DPS para (empresa, série): maior entre o contador local e o histórico, mais 1."""
    cnpj = regras.so_digitos(cnpj)
    arq = os.path.join(pasta_local(), "numeracao.json")
    cont = _ler_json(arq, {})
    chave = "%s_%05d" % (cnpj, int(serie))
    maior = int(cont.get(chave, 0))
    # piso informado na ficha: última DPS já usada nesta série por outro sistema (ex.: Lucas Soares, série 1 até 671)
    try:
        emp = carregar_empresa(cnpj, cfg) or {}
        maior = max(maior, int((emp.get("dps_ja_usadas") or {}).get(str(int(serie)), 0)))
    except (ValueError, TypeError, AttributeError):
        pass
    for h in historico(cnpj, cfg):
        if int(h.get("serie") or 0) == int(serie):
            maior = max(maior, int(h.get("n_dps") or 0))
    numero = maior + 1
    cont[chave] = numero
    _gravar_json(arq, cont)
    return numero


# --- arquivos das notas --------------------------------------------------------------------
def nome_seguro(texto, limite=60):
    t = regras.sem_acento(texto)
    t = re.sub(r"[^a-z0-9]+", "-", t).strip("-")
    return t[:limite] or "sem-nome"


def salvar_arquivo(emp, competencia, nome_arquivo, conteudo, cfg=None):
    """Grava na pasta de dados (cópia de segurança) e na pasta do cliente, se houver. Devolve os caminhos gravados."""
    comp = regras.para_data(competencia)
    sub = comp.strftime("%Y-%m") if comp else "sem-competencia"
    destinos = [os.path.join(pasta_dados(cfg), "notas", regras.so_digitos(emp["cnpj"]), sub)]
    if str(emp.get("pasta_notas") or "").strip():
        destinos.append(os.path.join(emp["pasta_notas"].strip(), sub))
    gravados, falhas = [], []
    for d in destinos:
        try:
            # caminhos longos (OneDrive com pastas fundas passam de 260 caracteres no Windows)
            if os.name == "nt" and not d.startswith("\\\\?\\") and len(os.path.join(d, nome_arquivo)) > 240:
                d = "\\\\?\\" + os.path.abspath(d)
            os.makedirs(d, exist_ok=True)
            caminho = os.path.join(d, nome_arquivo)
            if os.path.exists(caminho):  # nunca sobrescreve um documento fiscal já salvo
                base, ext = os.path.splitext(nome_arquivo)
                caminho = os.path.join(d, "%s_%s%s" % (base, datetime.now().strftime("%H%M%S"), ext))
            with open(caminho, "wb") as f:
                f.write(conteudo)
            gravados.append(caminho)
        except OSError as e:
            falhas.append("%s (%s)" % (d, e))
    return gravados, falhas


def carregar_tabelas():
    return _ler_json(os.path.join(pasta_programa(), "tabelas", "tabelas_oficiais.json"), {"servicos": {}, "nbs": {}})


def pasta_schemas(ambiente=None):
    """Esquemas oficiais. Produção Restrita (2) já está no leiaute novo: usa a cópia ajustada em schemas_restrita."""
    if str(ambiente or carregar_config().get("ambiente")) == "2":
        p = os.path.join(pasta_programa(), "schemas_restrita")
        if os.path.isdir(p):
            return p
    return os.path.join(pasta_programa(), "schemas")
