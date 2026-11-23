# -*- coding: utf-8 -*-
"""MODELO de montagem de lote. Copie para a pasta de andamento do mês, preencha EMPRESA, COMPETENCIA e LINHAS,
e rode:  python montar_lote_<empresa>_<mes>.py
Ele confere cada CEP no ViaCEP (código IBGE do município) e grava lote_<...>.json ao lado.
Depois:  python "<pasta do sistema>\\04 - Programa\\emitir_lote.py" lote_<...>.json --so-conferir
"""
import json
import os
import urllib.request

AQUI = os.path.dirname(os.path.abspath(__file__))
CNPJ_EMITENTE = "00000000000000"      # CNPJ da empresa emitente (só números)
COMPETENCIA = "2026-10-31"            # último dia do mês da aba da planilha
MES = "10/2026"                       # para a data do pagamento na descrição
ARQUIVO_LOTE = "lote_EMPRESA_MES.json"


def end(cep, lgr, nro, cpl, bairro, cod_mun):
    return {"cep": cep, "logradouro": lgr, "numero": nro, "complemento": cpl, "bairro": bairro, "cod_mun": cod_mun}


def desc(contrato, extra, dia):
    """Padrão aprovado: ver '01 - PROCEDIMENTO', passo 4. contrato=None para nota sem contrato."""
    linhas = ["Prestação de serviços jurídicos (Honorários Contratuais)" if contrato else
              "Prestação de serviços jurídicos (Honorários advocatícios)"]
    if contrato:
        linhas.append("Contrato de honorários nº %s" % contrato)
    if extra:
        linhas.append(extra)  # "Acordo", "Manutenção de contrato", "Acordo em execução judicial ... - Autos nº ..."
    linhas.append("Pagamento realizado dia %s/%s." % (dia, MES))
    return "\n".join(linhas)


# (linha da planilha, valor "1234,56", dia "07", contrato ou None, extra ou "", CPF/CNPJ, NOME, e-mail, telefone,
#  endereço, fonte dos dados)
LINHAS = [
    (1, "100,00", "07", "123", "", "00000000000", "NOME DO TOMADOR", "email@exemplo.com", "41999999999",
     end("80000000", "RUA EXEMPLO", "100", "", "CENTRO", "4106902"), "NFS-e anterior nº X"),
]

lote = []
for (lin, valor, dia, contr, extra, doc, nome, email, fone, en, fonte) in LINHAS:
    try:
        v = json.loads(urllib.request.urlopen("https://viacep.com.br/ws/%s/json/" % en["cep"], timeout=15).read())
        chk = "OK" if v.get("ibge") == en["cod_mun"] else "CONFERIR: ViaCEP diz %s (%s) %s" % (
            v.get("localidade"), v.get("ibge"), "CEP inexistente" if v.get("erro") else "")
    except Exception as e:
        chk = "sem consulta (%s)" % e
    print(lin, nome, valor, "| CEP", en["cep"], chk)
    lote.append({"linha": lin, "fonte": fonte, "nota": {
        "cnpj_emitente": CNPJ_EMITENTE, "servico": "Advocacia", "valor": valor, "competencia": COMPETENCIA,
        "descricao": desc(contr, extra, dia),
        "tomador": {"doc": doc, "nome": nome, "email": email, "fone": fone, "endereco": en}}})

with open(os.path.join(AQUI, ARQUIVO_LOTE), "w", encoding="utf-8") as f:
    json.dump(lote, f, ensure_ascii=False, indent=1)
print("Lote gravado:", len(lote), "notas; total R$ %.2f" % sum(float(x[1].replace(".", "").replace(",", ".")) for x in LINHAS))
