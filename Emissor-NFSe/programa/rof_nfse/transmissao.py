# -*- coding: utf-8 -*-
"""Conversa com a API da Sefin Nacional (emissão) e do ADN (DANFSe), com autenticação mútua (mTLS).

Endpoints usados (Manual dos Contribuintes - APIs do Emissor Público Nacional, v1.2):
    POST /nfse              envia a DPS assinada (XML compactado em GZip e codificado em Base64, dentro de JSON)
    GET  /nfse/{chave}      consulta a NFS-e pela chave de acesso
    GET  /dps/{id}          recupera a chave de acesso a partir do Id da DPS
    HEAD /dps/{id}          diz se já existe NFS-e para aquele Id de DPS

ATENÇÃO: as páginas de documentação interativa (Swagger) só abrem com certificado digital, então
os endereços-base e os nomes dos campos JSON abaixo NÃO puderam ser conferidos na fonte oficial
durante a construção. Eles ficam no arquivo de configuração e devem ser confirmados no primeiro
teste em Produção Restrita (botão "Testar conexão"). Toda resposta bruta é gravada no histórico.
"""
import base64
import gzip
import http.client
import json
import os
import socket
import ssl
from urllib.parse import urlsplit

URLS_PADRAO = {
    # ambiente 2 = Produção Restrita (homologação/testes); ambiente 1 = Produção
    "2": {"sefin": "https://sefin.producaorestrita.nfse.gov.br/SefinNacional",
          "sefin_alternativas": ["https://sefin.producaorestrita.nfse.gov.br/API/SefinNacional"],
          "adn": "https://adn.producaorestrita.nfse.gov.br"},
    "1": {"sefin": "https://sefin.nfse.gov.br/SefinNacional",
          "sefin_alternativas": ["https://sefin.nfse.gov.br/sefinnacional"],
          "adn": "https://adn.nfse.gov.br"},
}
CAMPO_ENVIO = "dpsXmlGZipB64"
TEMPO_LIMITE = 60


class ErroTransmissao(Exception):
    """Falha de rede/certificado ANTES de o servidor responder. incerta=True quando o pedido pode ter chegado."""

    def __init__(self, msg, incerta=False):
        super().__init__(msg)
        self.incerta = incerta


class Resposta:
    def __init__(self, status, corpo, cabecalhos):
        self.status, self.corpo, self.cabecalhos = status, corpo, cabecalhos
        try:
            self.json = json.loads(corpo.decode("utf-8")) if corpo else None
        except Exception:
            self.json = None

    def texto(self, limite=4000):
        return self.corpo.decode("utf-8", "replace")[:limite] if self.corpo else ""


def compactar(xml_bytes):
    return base64.b64encode(gzip.compress(xml_bytes)).decode("ascii")


def descompactar(texto_b64):
    return gzip.decompress(base64.b64decode(texto_b64))


def _pegar(d, *nomes):
    """Lê um campo do JSON sem depender de maiúsculas/minúsculas."""
    if not isinstance(d, dict):
        return None
    baixo = {str(k).lower(): v for k, v in d.items()}
    for n in nomes:
        if n.lower() in baixo:
            return baixo[n.lower()]
    return None


def interpretar_emissao(resp):
    """Normaliza a resposta do POST /nfse."""
    j = resp.json
    chave = _pegar(j, "chaveAcesso", "chave")
    xml_b64 = _pegar(j, "nfseXmlGZipB64", "nfseXmlGZipBase64", "nfseXml")
    erros = _pegar(j, "erros", "erro") or []
    if isinstance(erros, dict):
        erros = [erros]
    lista = []
    for e in erros if isinstance(erros, list) else []:
        lista.append({"codigo": str(_pegar(e, "codigo", "Codigo") or ""),
                      "descricao": str(_pegar(e, "descricao", "Descricao", "mensagem") or ""),
                      "complemento": str(_pegar(e, "complemento", "Complemento") or "")})
    alertas = _pegar(j, "alertas") or []
    xml_nfse = None
    if xml_b64:
        try:
            xml_nfse = descompactar(xml_b64)
        except Exception:
            xml_nfse = None
    autorizada = resp.status in (200, 201) and bool(chave) and xml_nfse is not None
    return {"autorizada": autorizada, "chave": chave, "xml_nfse": xml_nfse, "erros": lista, "alertas": alertas,
            "id_dps": _pegar(j, "idDps", "idDPS"), "status_http": resp.status}


class Cliente:
    def __init__(self, cert, ambiente, urls=None, ca_bundle=None):
        self.cert = cert
        self.ambiente = str(ambiente)
        self.urls = dict(URLS_PADRAO[self.ambiente])
        self.urls.update({k: v for k, v in (urls or {}).items() if v})
        self.ca_bundle = ca_bundle

    def _contexto(self):
        ctx = ssl.create_default_context(cafile=self.ca_bundle or None)  # confere o certificado do servidor, sempre
        ctx.minimum_version = ssl.TLSVersion.TLSv1_2
        caminho, senha = self.cert.arquivo_pem_temporario()
        try:
            ctx.load_cert_chain(caminho, password=senha)
        finally:
            try:
                os.remove(caminho)
            except OSError:
                pass
        return ctx

    def _pedir(self, metodo, url, corpo=None, aceita="application/json", limite=TEMPO_LIMITE):
        u = urlsplit(url)
        if u.scheme != "https":
            raise ErroTransmissao("Endereço inseguro (não é https): " + url)
        if getattr(self.cert, "thumbprint", None):  # certificado do Windows: a conexão é feita pelo Windows
            dados = json.dumps(corpo).encode("utf-8") if corpo is not None else None
            try:
                st, cb, cab = self.cert.pedir(metodo, url, dados, aceita, limite)
            except Exception as e:
                raise ErroTransmissao("Falha na conexão pelo certificado do Windows: %s" % e,
                                      incerta=bool(getattr(e, "enviado", False)) and corpo is not None)
            return Resposta(st, cb, cab)
        try:
            ctx = self._contexto()
        except ssl.SSLError as e:
            raise ErroTransmissao("Não foi possível carregar o certificado para a conexão: %s" % e)
        cab = {"Accept": aceita, "User-Agent": "EmissorROF"}
        dados = None
        if corpo is not None:
            dados = json.dumps(corpo).encode("utf-8")
            cab["Content-Type"] = "application/json"
        con = http.client.HTTPSConnection(u.hostname, u.port or 443, context=ctx, timeout=limite)
        enviado = False
        try:
            con.connect()
            con.request(metodo, u.path + ("?" + u.query if u.query else ""), body=dados, headers=cab)
            enviado = True
            r = con.getresponse()
            return Resposta(r.status, r.read(), dict(r.getheaders()))
        except ssl.SSLCertVerificationError as e:
            raise ErroTransmissao("O certificado do servidor não foi reconhecido por este computador (%s). "
                                  "Instale a cadeia ICP-Brasil no Windows ou indique o arquivo de cadeia na configuração. "
                                  "O programa não desliga essa verificação." % e.verify_message)
        except ssl.SSLError as e:
            raise ErroTransmissao("Falha na conexão segura (o servidor pode ter recusado o certificado): %s" % e, incerta=enviado)
        except (socket.timeout, TimeoutError):
            raise ErroTransmissao("O servidor não respondeu em %d segundos." % limite, incerta=enviado)
        except (OSError, http.client.HTTPException) as e:
            raise ErroTransmissao("Falha de rede: %s" % e, incerta=enviado)
        finally:
            con.close()

    # --- operações ---------------------------------------------------------------------
    def enviar_dps(self, xml_assinado):
        return self._pedir("POST", self.urls["sefin"] + "/nfse", {CAMPO_ENVIO: compactar(xml_assinado)})

    def existe_dps(self, id_dps):
        """True se já existe NFS-e para o Id; False se não; None se a resposta não permite concluir."""
        r = self._pedir("HEAD", self.urls["sefin"] + "/dps/" + id_dps, limite=25)
        if r.status == 200:
            return True
        if r.status == 404:
            return False
        return None

    def chave_por_dps(self, id_dps):
        r = self._pedir("GET", self.urls["sefin"] + "/dps/" + id_dps)
        return (_pegar(r.json, "chaveAcesso", "chave") if r.status == 200 else None), r

    def consultar_nfse(self, chave):
        r = self._pedir("GET", self.urls["sefin"] + "/nfse/" + chave)
        xml = None
        b64 = _pegar(r.json, "nfseXmlGZipB64", "nfseXmlGZipBase64")
        if r.status == 200 and b64:
            try:
                xml = descompactar(b64)
            except Exception:
                xml = None
        return xml, r

    def baixar_danfse(self, chave):
        """PDF oficial do DANFSe. A FAQ (17.8) informa que essa API está suspensa desde 03/08/2026;
        se voltar, funciona; se não, devolve None e o PDF é baixado na consulta pública do portal."""
        try:
            r = self._pedir("GET", self.urls["adn"] + "/danfse/" + chave, aceita="application/pdf")
        except ErroTransmissao:
            return None
        if r.status == 200 and r.corpo[:4] == b"%PDF":
            return r.corpo
        return None

    def testar_conexao(self, id_teste):
        """Tenta o endereço configurado e as alternativas; diz qual respondeu. Não emite nada."""
        resultados = []
        for base in [self.urls["sefin"]] + list(self.urls.get("sefin_alternativas") or []):
            try:
                r = self._pedir("HEAD", base + "/dps/" + id_teste, limite=15)
                # 404 = serviço respondeu que a DPS não existe (é o esperado); 200 seria coincidência.
                ok = r.status in (200, 404)
                resultados.append({"base": base, "status_http": r.status, "ok": ok,
                                   "obs": "serviço respondeu" if ok else "resposta inesperada"})
            except ErroTransmissao as e:
                resultados.append({"base": base, "status_http": None, "ok": False, "obs": str(e)})
        return resultados
