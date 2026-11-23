# -*- coding: utf-8 -*-
"""Certificado digital A1 (.pfx) e assinatura XMLDSig da DPS.

Padrão do Manual Integrado do Sistema Nacional NFS-e: assinatura "enveloped" sobre a tag
que tem o atributo Id (infDPS), canonicalização C14N 1.0, certificado X509 do titular
dentro de KeyInfo. O manual de 2022 fala em RSA-SHA1; o algoritmo fica configurável
("sha1" ou "sha256") para ser confirmado no teste em Produção Restrita.

A senha do certificado NUNCA é gravada em disco: fica só na memória enquanto o programa está aberto.
"""
import base64
import hashlib
import os
import re
import tempfile
from datetime import datetime, timezone

from cryptography import x509
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives.serialization import pkcs12
from lxml import etree

DSIG = "http://www.w3.org/2000/09/xmldsig#"
C14N = "http://www.w3.org/TR/2001/REC-xml-c14n-20010315"
ENVELOPED = "http://www.w3.org/2000/09/xmldsig#enveloped-signature"
ALGS = {
    "sha1": ("http://www.w3.org/2000/09/xmldsig#rsa-sha1", "http://www.w3.org/2000/09/xmldsig#sha1", hashes.SHA1, hashlib.sha1),
    "sha256": ("http://www.w3.org/2001/04/xmldsig-more#rsa-sha256", "http://www.w3.org/2001/04/xmlenc#sha256", hashes.SHA256, hashlib.sha256),
}
OID_ICP_CNPJ = "2.16.76.1.3.3"   # OtherName com o CNPJ do titular (e-CNPJ)
OID_ICP_CPF = "2.16.76.1.3.1"    # OtherName com dados do titular pessoa física (e-CPF)


class ErroCertificado(Exception):
    pass


class Certificado:
    def __init__(self, caminho_pfx, senha):
        if not os.path.isfile(caminho_pfx):
            raise ErroCertificado("Arquivo do certificado não encontrado: " + caminho_pfx)
        with open(caminho_pfx, "rb") as f:
            dados = f.read()
        try:
            chave, cert, cadeia = pkcs12.load_key_and_certificates(dados, senha.encode("utf-8") if senha else None)
        except Exception:
            raise ErroCertificado("Não foi possível abrir o certificado. Confira a senha e se o arquivo é um A1 (.pfx/.p12).")
        if chave is None or cert is None:
            raise ErroCertificado("O arquivo não contém chave privada e certificado.")
        self.chave, self.cert, self.cadeia = chave, cert, list(cadeia or [])
        self.caminho = caminho_pfx

    @property
    def validade_inicio(self):
        return self.cert.not_valid_before_utc

    @property
    def validade_fim(self):
        return self.cert.not_valid_after_utc

    def dias_para_vencer(self):
        return (self.validade_fim - datetime.now(timezone.utc)).days

    def vigente(self):
        agora = datetime.now(timezone.utc)
        return self.validade_inicio <= agora <= self.validade_fim

    def titular(self):
        cn = self.cert.subject.get_attributes_for_oid(x509.NameOID.COMMON_NAME)
        return cn[0].value if cn else self.cert.subject.rfc4514_string()

    def documento_titular(self):
        """CNPJ (14) ou CPF (11) do titular, lido da extensão ICP-Brasil; cai para o nome comum (NOME:documento)."""
        try:
            san = self.cert.extensions.get_extension_for_class(x509.SubjectAlternativeName).value
            for nome in san:
                if isinstance(nome, x509.OtherName):
                    bruto = nome.value
                    texto = re.sub(rb"[^0-9]", b"", bruto[2:] if len(bruto) > 2 else bruto).decode()
                    if nome.type_id.dotted_string == OID_ICP_CNPJ and len(texto) >= 14:
                        return texto[-14:]
            for nome in san:
                if isinstance(nome, x509.OtherName) and nome.type_id.dotted_string == OID_ICP_CPF:
                    bruto = nome.value
                    texto = re.sub(rb"[^0-9]", b"", bruto[2:] if len(bruto) > 2 else bruto).decode()
                    if len(texto) >= 19:
                        return texto[8:19]  # data de nascimento (8) + CPF (11)
        except x509.ExtensionNotFound:
            pass
        m = re.search(r":(\d{14}|\d{11})$", self.titular())
        return m.group(1) if m else ""

    def resumo(self):
        return {
            "titular": self.titular(),
            "documento": self.documento_titular(),
            "valido_de": self.validade_inicio.astimezone().strftime("%d/%m/%Y"),
            "valido_ate": self.validade_fim.astimezone().strftime("%d/%m/%Y"),
            "dias_para_vencer": self.dias_para_vencer(),
            "vigente": self.vigente(),
            "emissor": self.cert.issuer.rfc4514_string(),
        }

    def cert_base64(self):
        return base64.b64encode(self.cert.public_bytes(serialization.Encoding.DER)).decode()

    def arquivo_pem_temporario(self):
        """Grava certificado + chave (cifrada com senha aleatória) num arquivo temporário privado,
        só pelo tempo de abrir a conexão TLS. Devolve (caminho, senha). Quem chama apaga."""
        senha = base64.b64encode(os.urandom(24))
        pem = self.cert.public_bytes(serialization.Encoding.PEM)
        for c in self.cadeia:
            pem += c.public_bytes(serialization.Encoding.PEM)
        pem += self.chave.private_bytes(serialization.Encoding.PEM, serialization.PrivateFormat.PKCS8,
                                        serialization.BestAvailableEncryption(senha))
        fd, caminho = tempfile.mkstemp(prefix="rofnfse_", suffix=".pem")
        with os.fdopen(fd, "wb") as f:
            f.write(pem)
        return caminho, senha.decode()


def _c14n(elemento):
    """Canonicalização C14N 1.0 de um trecho do documento.
    O trecho é primeiro isolado num documento próprio (levando o namespace em vigor) e só então
    canonicalizado. Canonicalizar o subelemento direto, pela libxml2, gera xmlns="" indevidos nos
    filhos; os testes comparam este resultado com uma biblioteca independente (signxml)."""
    isolado = etree.fromstring(etree.tostring(elemento, with_tail=False),
                               etree.XMLParser(resolve_entities=False, no_network=True))
    return etree.tostring(isolado, method="c14n", exclusive=False, with_comments=False)


def assinar(raiz, cert, algoritmo="sha1", tag_assinada="infDPS"):
    """Assina a tag com Id e acrescenta <Signature> como último filho da raiz. Devolve a própria raiz."""
    if algoritmo not in ALGS:
        raise ValueError("Algoritmo de assinatura desconhecido: " + algoritmo)
    uri_sig, uri_dig, classe_hash, func_hash = ALGS[algoritmo]
    if not cert.vigente():
        raise ErroCertificado("Certificado digital fora da validade (%s)." % cert.resumo()["valido_ate"])
    alvo = None
    for filho in raiz:
        if etree.QName(filho).localname == tag_assinada:
            alvo = filho
    if alvo is None or not alvo.get("Id"):
        raise ValueError("Tag %s com atributo Id não encontrada." % tag_assinada)
    for velho in raiz.findall("{%s}Signature" % DSIG):
        raiz.remove(velho)

    digest = base64.b64encode(func_hash(_c14n(alvo)).digest()).decode()

    sig = etree.SubElement(raiz, "{%s}Signature" % DSIG, nsmap={None: DSIG})
    si = etree.SubElement(sig, "{%s}SignedInfo" % DSIG)
    etree.SubElement(si, "{%s}CanonicalizationMethod" % DSIG, Algorithm=C14N)
    etree.SubElement(si, "{%s}SignatureMethod" % DSIG, Algorithm=uri_sig)
    ref = etree.SubElement(si, "{%s}Reference" % DSIG, URI="#" + alvo.get("Id"))
    trs = etree.SubElement(ref, "{%s}Transforms" % DSIG)
    etree.SubElement(trs, "{%s}Transform" % DSIG, Algorithm=ENVELOPED)
    etree.SubElement(trs, "{%s}Transform" % DSIG, Algorithm=C14N)
    etree.SubElement(ref, "{%s}DigestMethod" % DSIG, Algorithm=uri_dig)
    etree.SubElement(ref, "{%s}DigestValue" % DSIG).text = digest

    assinatura = cert.chave.sign(_c14n(si), padding.PKCS1v15(), classe_hash())
    etree.SubElement(sig, "{%s}SignatureValue" % DSIG).text = base64.b64encode(assinatura).decode()
    ki = etree.SubElement(sig, "{%s}KeyInfo" % DSIG)
    xd = etree.SubElement(ki, "{%s}X509Data" % DSIG)
    etree.SubElement(xd, "{%s}X509Certificate" % DSIG).text = cert.cert_base64()
    return raiz


def conferir_assinatura(xml_bytes, tag_assinada="infDPS"):
    """Autoverificação: relê o XML final e confere o resumo e a assinatura com a chave pública do
    certificado embutido. Lança exceção se algo não bater. Devolve o certificado (x509)."""
    doc = etree.fromstring(xml_bytes, etree.XMLParser(resolve_entities=False, no_network=True))
    sig = doc.find("{%s}Signature" % DSIG)
    if sig is None:
        raise ValueError("XML sem assinatura.")
    si = sig.find("{%s}SignedInfo" % DSIG)
    uri_sig = si.find("{%s}SignatureMethod" % DSIG).get("Algorithm")
    alg = next((k for k, v in ALGS.items() if v[0] == uri_sig), None)
    if alg is None:
        raise ValueError("Algoritmo de assinatura não reconhecido.")
    _, _, classe_hash, func_hash = ALGS[alg]
    ref = si.find("{%s}Reference" % DSIG)
    alvo = next((f for f in doc if etree.QName(f).localname == tag_assinada), None)
    if alvo is None or "#" + (alvo.get("Id") or "") != ref.get("URI"):
        raise ValueError("A referência da assinatura não aponta para a tag assinada.")
    digest = base64.b64encode(func_hash(_c14n(alvo)).digest()).decode()
    if digest != (ref.find("{%s}DigestValue" % DSIG).text or "").strip():
        raise ValueError("Resumo (digest) não confere: o conteúdo mudou depois da assinatura.")
    cert = x509.load_der_x509_certificate(base64.b64decode(sig.find(".//{%s}X509Certificate" % DSIG).text))
    valor = base64.b64decode(sig.find("{%s}SignatureValue" % DSIG).text)
    cert.public_key().verify(valor, _c14n(si), padding.PKCS1v15(), classe_hash())
    return cert
