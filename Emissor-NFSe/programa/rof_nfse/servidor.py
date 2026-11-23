# -*- coding: utf-8 -*-
"""Tela do programa: uma página local, aberta no navegador, servida só para este computador.

Segurança: escuta apenas em 127.0.0.1; toda chamada precisa de um código sorteado a cada abertura
(impede que outro site aberto no navegador dê ordens ao programa); nada vai para a internet além
das consultas de CNPJ/CEP e do envio da nota à Sefin Nacional.
"""
import json
import os
import secrets
import threading
import traceback
import webbrowser
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlsplit

from . import assinatura, consultas, dados, dps, emissao, regras, transmissao

TOKEN = secrets.token_urlsafe(24)
ESTADO = {"cert": None}
TRAVA = threading.Lock()   # uma emissão por vez


def _estado():
    cfg = dados.carregar_config()
    cert = ESTADO["cert"]
    empresas = []
    for e in dados.listar_empresas(cfg):
        itens = regras.conferir_ficha_empresa(e, dados.carregar_tabelas())
        empresas.append({"cnpj": e["cnpj"], "razao": e.get("razao", ""),
                         "erros": sum(1 for i in itens if i["nivel"] == "erro"),
                         "avisos": [i["msg"] for i in itens if i["nivel"] == "aviso" and i["campo"] == "procuracao_validade"]})
    return {"versao": regras.VERSAO, "config": cfg, "config_erros": dados.conferir_config(cfg),
            "pasta_dados": dados.pasta_dados(cfg), "certificado": cert.resumo() if cert else None,
            "empresas": empresas, "palavra": emissao.PALAVRA_CONFIRMACAO,
            "rotulos": {"op_simp_nac": regras.OP_SIMP_NAC, "reg_ap_trib_sn": regras.REG_AP_TRIB_SN,
                        "reg_esp_trib": regras.REG_ESP_TRIB, "trib_issqn": regras.TRIB_ISSQN, "tp_ret_issqn": regras.TP_RET_ISSQN}}


def _acao(caminho, q, corpo):
    cfg = dados.carregar_config()
    if caminho == "/api/estado":
        return _estado()
    if caminho == "/api/config":
        novo = dict(cfg)
        novo.update({k: corpo[k] for k in dados.CONFIG_PADRAO if k in corpo})
        erros = dados.conferir_config(novo)
        if novo.get("pasta_dados") and not os.path.isdir(novo["pasta_dados"]):
            erros.append("A pasta de dados não existe: " + novo["pasta_dados"])
        if erros:
            return {"ok": False, "erros": erros}
        dados.salvar_config(novo)
        return {"ok": True, "estado": _estado()}
    if caminho == "/api/certificado":
        try:
            cert = assinatura.Certificado((corpo.get("caminho") or cfg.get("caminho_pfx") or "").strip().strip('"'), corpo.get("senha") or "")
        except assinatura.ErroCertificado as e:
            return {"ok": False, "msg": str(e)}
        ESTADO["cert"] = cert
        if corpo.get("caminho"):
            cfg["caminho_pfx"] = cert.caminho
            dados.salvar_config(cfg)
        r = cert.resumo()
        avisos = []
        if not r["vigente"]:
            avisos.append("Certificado FORA DA VALIDADE.")
        elif r["dias_para_vencer"] <= 30:
            avisos.append("O certificado vence em %d dia(s). Providencie a renovação." % r["dias_para_vencer"])
        if not r["documento"]:
            avisos.append("Não foi possível ler o CNPJ/CPF do titular no certificado.")
        return {"ok": True, "certificado": r, "avisos": avisos}
    if caminho == "/api/certificados_windows":
        from . import certificado_windows
        return {"ok": True, "lista": certificado_windows.listar_certificados()}
    if caminho == "/api/certificado_windows":
        from . import certificado_windows
        try:
            cert = certificado_windows.CertificadoWindows(corpo.get("thumb") or "")
        except assinatura.ErroCertificado as e:
            return {"ok": False, "msg": str(e)}
        ESTADO["cert"] = cert
        return {"ok": True, "certificado": cert.resumo()}
    if caminho == "/api/certificado/fechar":
        ESTADO["cert"] = None
        return {"ok": True}
    if caminho == "/api/empresa":
        if corpo:
            itens = regras.conferir_ficha_empresa(corpo, dados.carregar_tabelas())
            if not regras.cnpj_valido(corpo.get("cnpj")):
                return {"ok": False, "itens": itens}
            dados.salvar_empresa(corpo, cfg, cfg.get("usuario", ""))
            return {"ok": True, "itens": itens}
        return {"ok": True, "empresa": dados.carregar_empresa(q.get("cnpj", [""])[0], cfg)}
    if caminho == "/api/cnpj":
        return consultas.consultar_cnpj(q.get("cnpj", [""])[0])
    if caminho == "/api/cep":
        return consultas.consultar_cep(q.get("cep", [""])[0])
    if caminho == "/api/servico":
        t = dados.carregar_tabelas()
        cod = regras.so_digitos(q.get("codigo", [""])[0])
        return {"codigo": cod, "descricao": t.get("servicos", {}).get(cod.zfill(6)) or t.get("nbs", {}).get(cod) or ""}
    if caminho == "/api/conferir":
        return emissao.conferir(corpo, cfg)
    if caminho == "/api/emitir":
        if not TRAVA.acquire(blocking=False):
            return {"situacao": "BLOQUEADA", "msg": "Já existe uma emissão em andamento. Aguarde terminar."}
        try:
            return emissao.emitir(corpo.get("nota") or {}, cfg, ESTADO["cert"], corpo.get("confirmacao") or "",
                                  bool(corpo.get("confirmo_duplicidade")))
        finally:
            TRAVA.release()
    if caminho == "/api/historico":
        return {"itens": [{k: v for k, v in h.items() if k != "resposta"} for h in dados.historico(q.get("cnpj", [""])[0], cfg)]}
    if caminho == "/api/conferir_no_servidor":
        with TRAVA:
            return emissao.conferir_no_servidor(corpo.get("cnpj"), corpo.get("id_dps"), cfg, ESTADO["cert"])
    if caminho == "/api/testar_conexao":
        if ESTADO["cert"] is None:
            return {"ok": False, "msg": "Abra o certificado digital primeiro."}
        cli = transmissao.Cliente(ESTADO["cert"], cfg["ambiente"], cfg.get("urls"), cfg.get("ca_bundle") or None)
        ident = dps.id_dps("4106902", ESTADO["cert"].documento_titular() or "00000000000000", cfg["serie"], 999999999999999)
        res = cli.testar_conexao(ident)
        return {"ok": any(r["ok"] for r in res), "resultados": res, "configurado": cli.urls["sefin"]}
    if caminho == "/api/abrir_pasta":
        p = corpo.get("caminho") or ""
        pasta = p if os.path.isdir(p) else os.path.dirname(p)
        if os.path.isdir(pasta):
            os.startfile(pasta)  # noqa: só existe no Windows
            return {"ok": True}
        return {"ok": False, "msg": "Pasta não encontrada."}
    return None


class Manipulador(BaseHTTPRequestHandler):
    server_version = "EmissorROF"

    def log_message(self, *a):
        pass

    def _responder(self, codigo, corpo, tipo="application/json; charset=utf-8"):
        self.send_response(codigo)
        self.send_header("Content-Type", tipo)
        self.send_header("Content-Length", str(len(corpo)))
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("Content-Security-Policy", "default-src 'self' 'unsafe-inline'; connect-src 'self'; frame-ancestors 'none'")
        self.end_headers()
        self.wfile.write(corpo)

    def _host_ok(self):
        host = (self.headers.get("Host") or "").split(":")[0]
        return host in ("127.0.0.1", "localhost")

    def _tratar(self, corpo):
        u = urlsplit(self.path)
        if not self._host_ok():
            return self._responder(403, b'{"msg":"acesso negado"}')
        if u.path == "/":
            with open(os.path.join(dados.pasta_programa(), "web", "index.html"), "rb") as f:
                html = f.read().replace(b"__TOKEN__", TOKEN.encode())
            return self._responder(200, html, "text/html; charset=utf-8")
        if not u.path.startswith("/api/"):
            return self._responder(404, b'{"msg":"nao encontrado"}')
        if not secrets.compare_digest(self.headers.get("X-Token") or "", TOKEN):
            return self._responder(403, b'{"msg":"acesso negado"}')
        try:
            r = _acao(u.path, parse_qs(u.query), corpo)
            if r is None:
                return self._responder(404, b'{"msg":"nao encontrado"}')
            self._responder(200, json.dumps(r, ensure_ascii=False, default=str).encode("utf-8"))
        except Exception as e:
            reg = os.path.join(dados.pasta_local(), "erros.log")
            with open(reg, "a", encoding="utf-8") as f:
                f.write(traceback.format_exc() + "\n")
            self._responder(500, json.dumps({"msg": "Erro interno: %s. Nada foi enviado nesta chamada, salvo se a tela "
                                                    "disser o contrário; confira o Histórico. Detalhe gravado em %s" % (e, reg)},
                                            ensure_ascii=False).encode("utf-8"))

    def do_GET(self):
        self._tratar({})

    def do_POST(self):
        n = int(self.headers.get("Content-Length") or 0)
        try:
            corpo = json.loads(self.rfile.read(n).decode("utf-8")) if n else {}
        except ValueError:
            return self._responder(400, b'{"msg":"pedido invalido"}')
        self._tratar(corpo)


def iniciar(abrir_navegador=True, porta=0):
    srv = ThreadingHTTPServer(("127.0.0.1", porta), Manipulador)
    url = "http://127.0.0.1:%d/" % srv.server_address[1]
    if abrir_navegador:
        threading.Timer(0.6, lambda: webbrowser.open(url)).start()
    return srv, url
