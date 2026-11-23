# -*- coding: utf-8 -*-
"""Testes automáticos do Emissor ROF. Rodar:  python testes\\testar_tudo.py

Usam um certificado de TESTE gerado na hora (não é ICP-Brasil) e um servidor SIMULADO.
Provam a lógica do programa; NÃO provam a conversa com a Sefin Nacional de verdade,
que só pode ser testada em Produção Restrita com o certificado real da ROF.
Dados fictícios: CNPJ/CPF com dígito verificador válido, mas inventados.
"""
import os
import sys
import tempfile
import unittest
from datetime import date, datetime, timedelta, timezone

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
_tmp = tempfile.mkdtemp(prefix="emissor_rof_teste_")
os.environ["EMISSOR_ROF_LOCAL"] = _tmp

from cryptography import x509
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives.serialization import pkcs12
from cryptography.x509.oid import NameOID, ObjectIdentifier
from lxml import etree

from rof_nfse import assinatura, dados, dps, emissao, regras, transmissao

CNPJ_EMIT = "11222333000181"
CNPJ_ROF = "11444777000161"
CPF_TOM = "52998224725"
HOJE = date.today()


def gerar_pfx(caminho, cnpj, senha="senha-de-teste", dias=365):
    chave = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    nome = x509.Name([x509.NameAttribute(NameOID.COMMON_NAME, "EMPRESA TESTE LTDA:" + cnpj)])
    agora = datetime.now(timezone.utc)
    der_cnpj = b"\x13\x0e" + cnpj.encode()  # PrintableString de 14 posições, como no e-CNPJ
    cert = (x509.CertificateBuilder().subject_name(nome).issuer_name(nome).public_key(chave.public_key())
            .serial_number(x509.random_serial_number()).not_valid_before(agora - timedelta(days=1))
            .not_valid_after(agora + timedelta(days=dias))
            .add_extension(x509.SubjectAlternativeName([x509.OtherName(ObjectIdentifier("2.16.76.1.3.3"), der_cnpj)]), False)
            .sign(chave, hashes.SHA256()))
    with open(caminho, "wb") as f:
        f.write(pkcs12.serialize_key_and_certificates(b"teste", chave, cert, None,
                                                      serialization.BestAvailableEncryption(senha.encode())))
    return caminho


def empresa(**mud):
    e = {"cnpj": CNPJ_EMIT, "razao": "CLINICA EXEMPLO LTDA", "municipio_ibge": "4106902", "municipio_nome": "Curitiba",
         "op_simp_nac": 3, "reg_ap_trib_sn": 1, "reg_esp_trib": 0, "certificado_proprio": False,
         "procuracao_validade": (HOJE + timedelta(days=200)).isoformat(), "pasta_notas": "", "producao_liberada": False,
         "servicos": [{"apelido": "Psicoterapia", "c_trib_nac": "041601", "c_trib_mun": "", "c_nbs": "",
                       "descricao_modelo": "Sessões de psicoterapia.", "trib_issqn": 1, "tp_ret_issqn": 1, "p_aliq": None,
                       "tot_trib": {"tipo": "pTotTribSN", "valor": "6,00"}, "exige_tomador": True}]}
    e.update(mud)
    return e


def nota(**mud):
    n = {"cnpj_emitente": CNPJ_EMIT, "servico": "Psicoterapia", "valor": "350,00", "competencia": HOJE.isoformat(),
         "descricao": "Sessões de psicoterapia realizadas no mês. Beneficiário: Fulano de Tal.",
         "tomador": {"doc": CPF_TOM, "nome": "Maria de Souza", "email": "maria@example.com", "fone": "41999990000",
                     "endereco": {"cep": "80010000", "logradouro": "Rua XV de Novembro", "numero": "100",
                                  "complemento": "", "bairro": "Centro", "cod_mun": "4106902"}}}
    n.update(mud)
    return n


def erros(itens):
    return [i["msg"] for i in itens if i["nivel"] == "erro"]


class ServidorSimulado:
    """Imita a Sefin Nacional: guarda as DPS aceitas e devolve uma NFS-e mínima."""

    def __init__(self, modo="ok"):
        self.modo, self.notas, self.envios = modo, {}, 0

    def existe_dps(self, ident):
        return ident in self.notas

    def enviar_dps(self, xml):
        self.envios += 1
        doc = etree.fromstring(xml)
        ident = doc[0].get("Id")
        if self.modo == "timeout":
            self.notas[ident] = self._nfse(doc)  # o servidor emitiu, mas a resposta se perdeu
            raise transmissao.ErroTransmissao("O servidor não respondeu.", incerta=True)
        if self.modo == "sem_rede":
            raise transmissao.ErroTransmissao("Falha de rede.", incerta=False)
        if self.modo == "rejeita":
            return transmissao.Resposta(400, b'{"erros":[{"Codigo":"E0718","Descricao":"A assinatura deve ser feita com o certificado digital do emitente da DPS."}]}', {})
        chave, nfse = self._nfse(doc)
        self.notas[ident] = (chave, nfse)
        import json
        return transmissao.Resposta(201, json.dumps({"chaveAcesso": chave, "idDps": ident,
                                                     "nfseXmlGZipB64": transmissao.compactar(nfse)}).encode(), {})

    def _nfse(self, doc):
        chave = ("41069022" + "2" + CNPJ_EMIT + "0000000000042" + "2611" + "123456789" + "0")[:50].ljust(50, "0")
        n = etree.Element("{%s}NFSe" % dps.NS, nsmap={None: dps.NS})
        inf = etree.SubElement(n, "{%s}infNFSe" % dps.NS, Id="NFS" + chave)
        etree.SubElement(inf, "{%s}nNFSe" % dps.NS).text = "42"
        n.find("{%s}infNFSe" % dps.NS).append(etree.fromstring(etree.tostring(doc)))
        return chave, etree.tostring(n, xml_declaration=True, encoding="UTF-8")

    def chave_por_dps(self, ident):
        return (self.notas[ident][0] if ident in self.notas else None), None

    def consultar_nfse(self, chave):
        for c, x in self.notas.values():
            if c == chave:
                return x, None
        return None, None

    def baixar_danfse(self, chave):
        return None


class TesteValidadores(unittest.TestCase):
    def test_cpf_cnpj(self):
        self.assertTrue(regras.cpf_valido("529.982.247-25"))
        self.assertFalse(regras.cpf_valido("529.982.247-26"))
        self.assertFalse(regras.cpf_valido("11111111111"))
        self.assertTrue(regras.cnpj_valido("11.222.333/0001-81"))
        self.assertFalse(regras.cnpj_valido("11.222.333/0001-82"))
        self.assertFalse(regras.cnpj_valido("00000000000000"))

    def test_valor(self):
        self.assertEqual(str(regras.para_decimal("1.234,56")), "1234.56")
        self.assertEqual(str(regras.para_decimal("350")), "350.00")
        self.assertEqual(str(regras.para_decimal("350.5")), "350.50")
        self.assertIsNone(regras.para_decimal("350,555"))   # não arredonda por conta própria
        self.assertIsNone(regras.para_decimal("abc"))

    def test_id_dps(self):
        i = dps.id_dps("4106902", CNPJ_EMIT, 1, 27)
        self.assertEqual(i, "DPS4106902" + "2" + CNPJ_EMIT + "00001" + "000000000000027")
        self.assertEqual(len(i), 45)


class TesteRegras(unittest.TestCase):
    def test_nota_boa_passa(self):
        self.assertEqual(erros(regras.conferir_nota(empresa(), nota(), [], HOJE)), [])

    def casos_de_erro(self):
        return {
            "servico fora da ficha": (empresa(), nota(servico="Venda de livro")),
            "valor zero": (empresa(), nota(valor="0,00")),
            "valor invalido": (empresa(), nota(valor="trezentos")),
            "competencia futura": (empresa(), nota(competencia=(HOJE + timedelta(days=1)).isoformat())),
            "cpf invalido": (empresa(), nota(tomador=dict(nota()["tomador"], doc="52998224726"))),
            "tomador ausente": (empresa(), nota(tomador=None)),
            "diagnostico na descricao": (empresa(), nota(descricao="Sessões de psicoterapia. Diagnóstico: ansiedade.")),
            "colchetes por preencher": (empresa(), nota(descricao="Atendimento a [nome do paciente]")),
            "descricao vazia": (empresa(), nota(descricao="   ")),
            "descricao longa": (empresa(), nota(descricao="a" * 2001)),
            "procuracao vencida": (empresa(procuracao_validade=(HOJE - timedelta(days=1)).isoformat()), nota()),
            "sem procuracao": (empresa(procuracao_validade=None), nota()),
            "nao optante": (empresa(op_simp_nac=1, reg_ap_trib_sn=None,
                                    servicos=[dict(empresa()["servicos"][0], tot_trib={"tipo": "pTotTrib", "fed": 1, "est": 0, "mun": 1})]), nota()),
            "mei com aliquota do simples": (empresa(op_simp_nac=2, reg_ap_trib_sn=None), nota()),
            "tomador cnpj sem endereco": (empresa(), nota(tomador={"doc": CNPJ_ROF, "nome": "Empresa X", "email": "x@example.com"})),
            "tomador e o emitente": (empresa(), nota(tomador=dict(nota()["tomador"], doc=CNPJ_EMIT))),
            "email invalido": (empresa(), nota(tomador=dict(nota()["tomador"], email="maria@"))),
            "simples com retencao sem aliquota (E0621)": (empresa(servicos=[dict(empresa()["servicos"][0], tp_ret_issqn=2)]), nota()),
            "simples sem retencao com aliquota (E0625)": (empresa(servicos=[dict(empresa()["servicos"][0], p_aliq="2,00")]), nota()),
            "codigo de servico inexistente": (empresa(servicos=[dict(empresa()["servicos"][0], c_trib_nac="999999")]), nota()),
        }

    def test_cada_erro_bloqueia(self):
        tab = dados.carregar_tabelas()
        for nome, (e, n) in self.casos_de_erro().items():
            with self.subTest(nome):
                self.assertTrue(erros(regras.conferir_nota(e, n, [], HOJE, tab)), "deveria bloquear: " + nome)

    def test_competencia_2027_bloqueia_simples(self):
        r = regras.conferir_nota(empresa(), nota(competencia="2027-01-05"), [], date(2027, 1, 10))
        self.assertTrue(any("IBS/CBS" in m for m in erros(r)))

    def test_mes_anterior_e_aviso(self):
        ant = HOJE.replace(day=1) - timedelta(days=1)
        r = regras.conferir_nota(empresa(), nota(competencia=ant.isoformat()), [], HOJE)
        self.assertEqual(erros(r), [])
        self.assertTrue(any(i["nivel"] == "aviso" and i["campo"] == "competencia" for i in r))

    def test_duplicidade(self):
        h = [{"situacao": "AUTORIZADA", "tomador_doc": CPF_TOM, "valor": "350.00", "competencia": HOJE.isoformat(), "n_nfse": "41", "n_dps": 9}]
        r = regras.conferir_nota(empresa(), nota(), h, HOJE)
        self.assertTrue(any(i.get("duplicidade") for i in r))
        h[0]["situacao"] = "REJEITADA"
        self.assertFalse(any(i.get("duplicidade") for i in regras.conferir_nota(empresa(), nota(), h, HOJE)))


class TesteXmlEAssinatura(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.cert = assinatura.Certificado(gerar_pfx(os.path.join(_tmp, "rof.pfx"), CNPJ_ROF), "senha-de-teste")

    def test_certificado(self):
        r = self.cert.resumo()
        self.assertEqual(r["documento"], CNPJ_ROF)
        self.assertTrue(r["vigente"])
        with self.assertRaises(assinatura.ErroCertificado):
            assinatura.Certificado(os.path.join(_tmp, "rof.pfx"), "senha errada")

    def test_xml_valido_no_esquema_oficial(self):
        for e, n in ((empresa(), nota()),
                     (empresa(op_simp_nac=2, reg_ap_trib_sn=None, servicos=[dict(empresa()["servicos"][0], tot_trib={"tipo": "indTotTrib"})]), nota()),
                     (empresa(im="123456", fone="4133334444", email="clinica@example.com",
                              servicos=[dict(empresa()["servicos"][0], c_trib_mun="001", c_nbs="123012100", tp_ret_issqn=2, p_aliq="2,01")]),
                      nota(desconto_incondicionado="10,00", tomador={"doc": CNPJ_ROF, "nome": "Empresa & Filhos <Ltda>", "email": "x@example.com",
                                                                    "endereco": {"cep": "80010000", "logradouro": "Rua A", "numero": "S/N", "complemento": "Sala 2", "bairro": "Centro", "cod_mun": "4106902"}}))):
            raiz, ident = dps.montar_dps(e, n, 1, 5, "2")
            self.assertEqual(dps.validar_xsd(raiz, dados.pasta_schemas()), [])
            xml = dps.serializar(raiz)
            self.assertTrue(xml.startswith(b"<?xml version='1.0' encoding='UTF-8'?>") or xml.startswith(b'<?xml version="1.0" encoding="UTF-8"?>'))
            self.assertNotIn(b"xmlns:", xml)   # sem prefixo de namespace (regra E1228)
            self.assertNotIn(b"<xNome>CLINICA", xml)   # prestador-emitente sem nome (E0121)

    def test_assinatura_fecha_e_detecta_adulteracao(self):
        for alg in ("sha1", "sha256"):
            raiz, _ = dps.montar_dps(empresa(), nota(), 1, 5, "2")
            assinatura.assinar(raiz, self.cert, alg)
            xml = dps.serializar(raiz)
            self.assertEqual(dps.validar_xsd(etree.fromstring(xml), dados.pasta_schemas()), [])
            assinatura.conferir_assinatura(xml)
            adulterado = xml.replace(b"<vServ>350.00</vServ>", b"<vServ>950.00</vServ>")
            self.assertNotEqual(adulterado, xml)
            with self.assertRaises(Exception):
                assinatura.conferir_assinatura(adulterado)

    def test_conferencia_independente_com_signxml(self):
        try:
            from signxml import XMLVerifier, SignatureConfiguration, DigestAlgorithm, SignatureMethod
        except ImportError:
            self.skipTest("signxml não instalado (conferência independente opcional)")
        raiz, _ = dps.montar_dps(empresa(), nota(), 1, 5, "2")
        assinatura.assinar(raiz, self.cert, "sha256")
        xml = dps.serializar(raiz)
        pem = self.cert.cert.public_bytes(serialization.Encoding.PEM)
        XMLVerifier().verify(xml, x509_cert=pem.decode(), expect_config=SignatureConfiguration(
            signature_methods=frozenset({SignatureMethod.RSA_SHA256}), digest_algorithms=frozenset({DigestAlgorithm.SHA256})))

    def test_gzip_base64_ida_e_volta(self):
        self.assertEqual(transmissao.descompactar(transmissao.compactar(b"<a>\xc3\xa7</a>")), b"<a>\xc3\xa7</a>")


class TesteEmissao(unittest.TestCase):
    def setUp(self):
        self.dir = tempfile.mkdtemp(prefix="dados_", dir=_tmp)
        self.cfg = dict(dados.CONFIG_PADRAO, pasta_dados=self.dir, serie=3, ambiente="2", usuario="teste")
        dados.salvar_empresa(empresa(pasta_notas=os.path.join(self.dir, "pasta do cliente")), self.cfg)
        self.cert = assinatura.Certificado(gerar_pfx(os.path.join(self.dir, "rof.pfx"), CNPJ_ROF), "senha-de-teste")

    def test_sem_confirmacao_nao_envia(self):
        srv = ServidorSimulado()
        r = emissao.emitir(nota(), self.cfg, self.cert, "sim", cliente=srv)
        self.assertEqual(r["situacao"], "BLOQUEADA")
        self.assertEqual(srv.envios, 0)

    def test_emissao_completa(self):
        srv = ServidorSimulado()
        r = emissao.emitir(nota(), self.cfg, self.cert, "EMITIR", cliente=srv)
        self.assertEqual(r["situacao"], "AUTORIZADA", r)
        self.assertEqual(r["n_nfse"], "42")
        self.assertEqual(r["divergencias"], [])
        self.assertTrue(any("pasta do cliente" in a for a in r["arquivos"]))
        self.assertTrue(all(os.path.isfile(a) for a in r["arquivos"]))
        self.assertTrue(any("ENVIAR a nota ao tomador" in p for p in r["pendencias"]))
        h = dados.historico(CNPJ_EMIT, self.cfg)
        self.assertEqual(h[0]["situacao"], "AUTORIZADA")
        # segunda nota igual: bloqueia por duplicidade; com confirmação expressa, emite com outro número
        r2 = emissao.emitir(nota(), self.cfg, self.cert, "EMITIR", cliente=srv)
        self.assertEqual(r2["situacao"], "BLOQUEADA")
        self.assertEqual(srv.envios, 1)
        r3 = emissao.emitir(nota(), self.cfg, self.cert, "EMITIR", confirmo_duplicidade=True, cliente=srv)
        self.assertEqual(r3["situacao"], "AUTORIZADA")
        self.assertNotEqual(r3["id_dps"], r["id_dps"])

    def test_erro_de_conferencia_nao_envia(self):
        srv = ServidorSimulado()
        r = emissao.emitir(nota(valor="0"), self.cfg, self.cert, "EMITIR", cliente=srv)
        self.assertEqual(r["situacao"], "BLOQUEADA")
        self.assertEqual(srv.envios, 0)

    def test_producao_exige_liberacao(self):
        srv = ServidorSimulado()
        r = emissao.emitir(nota(), dict(self.cfg, ambiente="1"), self.cert, "EMITIR", cliente=srv)
        self.assertEqual(r["situacao"], "BLOQUEADA")
        self.assertIn("PRODUÇÃO", r["msg"])
        self.assertEqual(srv.envios, 0)

    def test_rejeicao(self):
        r = emissao.emitir(nota(), self.cfg, self.cert, "EMITIR", cliente=ServidorSimulado("rejeita"))
        self.assertEqual(r["situacao"], "REJEITADA")
        self.assertEqual(r["erros"][0]["codigo"], "E0718")

    def test_sem_rede_nao_fica_incerta(self):
        r = emissao.emitir(nota(), self.cfg, self.cert, "EMITIR", cliente=ServidorSimulado("sem_rede"))
        self.assertEqual(r["situacao"], "NAO_ENVIADA")
        self.assertTrue(emissao.conferir(nota(), self.cfg)["ok"])   # pode tentar de novo

    def test_timeout_trava_e_reconcilia_sem_duplicar(self):
        srv = ServidorSimulado("timeout")
        r = emissao.emitir(nota(), self.cfg, self.cert, "EMITIR", cliente=srv)
        self.assertEqual(r["situacao"], "INCERTA")
        # enquanto estiver incerta, nenhuma outra nota da empresa sai
        srv.modo = "ok"
        r2 = emissao.emitir(nota(valor="99,00"), self.cfg, self.cert, "EMITIR", cliente=srv)
        self.assertEqual(r2["situacao"], "BLOQUEADA")
        self.assertEqual(srv.envios, 1)
        # a conferência no servidor descobre que a nota existe e fecha o caso
        r3 = emissao.conferir_no_servidor(CNPJ_EMIT, r["id_dps"], self.cfg, self.cert, cliente=srv)
        self.assertEqual(r3["situacao"], "AUTORIZADA", r3)
        self.assertEqual(dados.historico(CNPJ_EMIT, self.cfg)[0]["situacao"], "AUTORIZADA")
        self.assertEqual(srv.envios, 1)   # nada foi reenviado

    def test_numeracao_nunca_repete(self):
        nums = [dados.proximo_numero(CNPJ_EMIT, 3, self.cfg) for _ in range(5)]
        self.assertEqual(len(set(nums)), 5)
        self.assertEqual(nums, sorted(nums))


if __name__ == "__main__":
    unittest.main(verbosity=1)
