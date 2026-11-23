# -*- coding: utf-8 -*-
"""Certificado A1 instalado no Windows (repositório "Pessoal"), usado sem exportar a chave e sem senha.

Mesma interface de assinatura.Certificado (titular, documento, validade, resumo, cert_base64, chave.sign),
mais `pedir()`, que faz a conexão HTTPS com o certificado pelo próprio Windows (win_cert.ps1).
Serve quando o certificado está instalado como "não exportável": o Python não lê a chave, mas o Windows
assina e apresenta o certificado em nome do programa.
"""
import base64
import json
import os
import subprocess
import tempfile

from cryptography import x509
from cryptography.hazmat.primitives import hashes

from . import assinatura

_PS1 = os.path.join(os.path.dirname(os.path.abspath(__file__)), "win_cert.ps1")


class ErroWindows(Exception):
    pass


def _rodar(args, limite=120):
    fd, saida = tempfile.mkstemp(prefix="rofwin_", suffix=".json")
    os.close(fd)
    try:
        cmd = ["powershell", "-NoProfile", "-NonInteractive", "-ExecutionPolicy", "Bypass", "-File", _PS1] + args + ["-Saida", saida]
        flags = getattr(subprocess, "CREATE_NO_WINDOW", 0)
        subprocess.run(cmd, capture_output=True, timeout=limite, creationflags=flags)
        with open(saida, "r", encoding="utf-8-sig") as f:
            texto = f.read().strip()
        if not texto:
            raise ErroWindows("O ajudante do Windows não respondeu.")
        return json.loads(texto)
    finally:
        try:
            os.remove(saida)
        except OSError:
            pass


def listar_certificados():
    """Certificados com chave privada no repositório Pessoal do usuário: [{thumb, titular, validade}]."""
    ps = ("Get-ChildItem Cert:\\CurrentUser\\My | Where-Object { $_.HasPrivateKey } | "
          "ForEach-Object { '{0}|{1}|{2}' -f $_.Thumbprint, $_.Subject, $_.NotAfter.ToString('yyyy-MM-dd') }")
    r = subprocess.run(["powershell", "-NoProfile", "-NonInteractive", "-Command", ps], capture_output=True, text=True,
                       timeout=60, creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))
    saida = []
    for linha in (r.stdout or "").splitlines():
        partes = linha.strip().split("|")
        if len(partes) == 3:
            saida.append({"thumb": partes[0], "titular": partes[1], "validade": partes[2]})
    return saida


class _ChaveWindows:
    def __init__(self, thumb):
        self.thumb = thumb

    def sign(self, dados, _padding, classe_hash):
        alg = "sha256" if isinstance(classe_hash, hashes.SHA256) else "sha1"
        fd, entrada = tempfile.mkstemp(prefix="rofsig_", suffix=".bin")
        with os.fdopen(fd, "wb") as f:
            f.write(dados)
        try:
            r = _rodar(["-Op", "sign", "-Thumb", self.thumb, "-Alg", alg, "-Entrada", entrada])
        finally:
            os.remove(entrada)
        if not r.get("ok"):
            raise assinatura.ErroCertificado("O Windows não assinou com o certificado: %s" % r.get("erro"))
        return base64.b64decode(r["assinatura"])


class CertificadoWindows(assinatura.Certificado):
    """Herda os métodos de leitura (titular, documento, validade, resumo) do Certificado .pfx."""

    def __init__(self, thumb):  # noqa: não chama o __init__ do pai (não há arquivo nem senha)
        thumb = "".join(c for c in str(thumb) if c.isalnum()).upper()
        r = _rodar(["-Op", "info", "-Thumb", thumb])
        if not r.get("ok"):
            raise assinatura.ErroCertificado("Certificado não encontrado no Windows: %s" % r.get("erro"))
        if not r.get("tem_chave"):
            raise assinatura.ErroCertificado("O certificado está no Windows sem a chave privada.")
        self.cert = x509.load_der_x509_certificate(base64.b64decode(r["der"]))
        self.chave = _ChaveWindows(thumb)
        self.cadeia = []
        self.thumbprint = thumb
        self.caminho = "windows:" + thumb

    def arquivo_pem_temporario(self):
        raise assinatura.ErroCertificado("Certificado do Windows não sai do repositório; a conexão é feita pelo Windows.")

    def pedir(self, metodo, url, corpo_bytes=None, aceita="application/json", limite=60):
        """Pedido HTTPS com o certificado. Devolve (status, corpo_bytes, cabecalhos). Lança ErroWindows com .enviado."""
        entrada = ""
        if corpo_bytes is not None:
            fd, entrada = tempfile.mkstemp(prefix="rofreq_", suffix=".json")
            with os.fdopen(fd, "wb") as f:
                f.write(corpo_bytes)
        try:
            args = ["-Op", "http", "-Thumb", self.thumbprint, "-Metodo", metodo, "-Url", url, "-Aceita", aceita,
                    "-Limite", str(int(limite))]
            if entrada:
                args += ["-Entrada", entrada]
            r = _rodar(args, limite=limite + 60)
        finally:
            if entrada:
                os.remove(entrada)
        if not r.get("ok"):
            e = ErroWindows("%s (%s)" % (r.get("erro"), r.get("status_web") or ""))
            e.enviado = bool(r.get("enviado"))
            raise e
        return int(r["status"]), base64.b64decode(r.get("corpo") or ""), r.get("cabecalhos") or {}
