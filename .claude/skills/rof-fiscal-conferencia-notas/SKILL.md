---
name: rof-fiscal-conferencia-notas
description: Conferência fiscal mensal das notas (NF-e, CT-e, NFS-e) de uma empresa da ROF Contabilidade. Lê os XML item a item, identifica a finalidade de cada item comprado (insumo, embalagem, ferramenta, uso e consumo, revenda, ativo), sugere CFOP de entrada e acumulador do Domínio, recalcula créditos de ICMS/IPI e DIFAL (base dupla PR) e compara com o SPED Fiscal e os relatórios de acompanhamento do Domínio. Entrega uma planilha de conferência com pendências. Usar quando pedirem para conferir/automatizar as notas fiscais do mês, acumuladores, CFOP de entrada, leitura de XML, SPED Fiscal x XML, ou citarem "Fiscal/empresas/<empresa>".
---

# Conferência fiscal de notas (XML x Domínio x SPED)

Scripts em `Fiscal/scripts/`, regras por empresa em `Fiscal/empresas/<cod>-<nome>/regras.json`,
resultado em `Fiscal/empresas/<cod>-<nome>/<AAAA-MM>/`.

## Entradas (pasta do mês no Drive: `Arquivos RENATA Dominio/<cod> - <empresa>/<ano>/<MM_AAAA>`)
- `Doc's/*.zip` com XML: DownloadDFe (SEFAZ — traz cancelamentos), notas de venda/devolução do cliente, notasXML.
- `SPED/ICMS_IPI/*.txt` — SPED Fiscal entregue (gabarito final).
- `Relatorio/NF_Entrada_*.xlsx` — aba `Entradas` = Acompanhamento de Entradas do Domínio; aba `download_excel` = lista SEFAZ.
- `Relatorio/FAT*.xlsx` — aba `Saídas` = Acompanhamento de Saídas; aba `Relatório de Notas Fiscais ...` = ERP do cliente.
- `Relatorio/*Recebidas - Completa*.xlsx` — NFS-e recebidas (lista nacional); `Serviços Tomados*.xls` — Domínio.

Baixar com o Google Drive MCP (arquivos grandes caem em `tool-results/` como JSON base64:
decodificar com `json.load(...)['content']`), extrair os ZIP numa pasta só de dados.

## Rodar
```
python3 Fiscal/scripts/conferencia.py --regras Fiscal/empresas/60-kopp-industria/regras.json \
  --xml <pasta XML> --sped <SPED.txt> \
  --dom-entradas NF_Entrada.xlsx --dom-saidas FAT.xlsx \
  --sefaz NF_Entrada.xlsx --sefaz-aba download_excel \
  --nfse-recebidas Recebidas.xlsx --dom-servicos Servicos_Tomados.xls \
  --erp-notas FAT.xlsx --erp-aba 'Relatório de Notas Fiscais Kopp' \
  --competencia 2026-08 --saida Fiscal/empresas/60-kopp-industria/2026-08/Conferencia_....xlsx
```

### Mês aberto (antes de importar no Domínio)
Sem SPED e sem relatório do mês: omitir `--sped`/`--dom-*`. O robô entra em **modo pré-importação**:
classifica cada item (CFOP, acumulador, conta), confere notas próprias, lista da SEFAZ x XML,
numeração, série 2 do ERP e NFS-e. `--historico` recebe o "Acompanhamento de Entradas" do Domínio de
meses anteriores (PDF ou Excel) e serve para: mostrar como cada fornecedor/prestador foi lançado,
marcar `CONFERIR HISTÓRICO` quando a sugestão difere, e avisar nota já lançada.
```
python3 Fiscal/scripts/conferencia.py --regras .../regras.json --xml <pasta XML> \
  --sefaz notasExcel_NFe.xlsx notasExcel_CTe.xlsx --sefaz-aba download_excel \
  --historico Entradas_jan-ago.pdf --nfse-recebidas Recebidas.xlsx \
  --erp-notas 'Relatório de Notas Fiscais.xlsx' --competencia 2026-09 --saida .../Pre_Conferencia_....xlsx
```
`--acumuladores` recebe o "Resumo por acumulador" do Domínio (PDF): catálogo com o nome de cada acumulador,
usado para as saídas e para escolher o acumulador de serviço (item da LC 116 + retenções).

Classificar pela atividade: o material comprado condiz com o que a empresa fabrica/vende? A regra
`perfil_venda` olha como a própria empresa fatura o mesmo item (x101 produção → INSUMO; x102 → REVENDA).
Serviços: natureza pelo item da LC 116, acumulador pelo catálogo, conta pela natureza > razão > padrão,
e alerta de retenção (IRRF/CSRF) faltando em prestador fora do Simples.

Junto com a pré-conferência sai `Entradas_para_conferencia_MM-AAAA.xlsx`: uma linha por documento de entrada,
abas NF-e dentro do estado, NF-e fora do estado, devoluções/retornos, serviços tomados e CT-e, com total e
coluna "Conferido" (`planilha_entradas.py`).

Excel é sempre melhor que PDF; PDF do Acompanhamento é lido por `dominio_pdf.py` (precisa de `pdftotext`).

## Como decidir (e quando perguntar)
1. Item novo sem regra sai como **FINALIDADE A DEFINIR**. Ler a descrição/NCM/fornecedor e propor a
   finalidade; perguntar ao escritório quando houver dúvida real (ex.: química que pode ser processo ou laboratório).
2. Resposta do escritório vira regra em `regras.json` (`finalidade_por_item`, `finalidade_por_fornecedor`
   ou `finalidade_por_ncm`) — nunca decidir de novo o mesmo caso no mês seguinte.
3. Acumulador sem cadastro (`ac: null`) aparece em Alertas: pedir o código ao escritório.
4. O SPED é o gabarito final; o relatório do Domínio é a importação antes das correções manuais.
   "Corrigido à mão?" mostra o retrabalho que a sugestão evita.
5. Nunca afirmar irregularidade sem a evidência na linha (XML, SPED ou relatório); usar VERIFICAR.

## Notas canceladas
Regra do escritório: toda nota cancelada é **lançada**, com situação CANCELADA, só participante e chave, e valor,
base, imposto e crédito zerados. Vale para entradas de terceiros, saídas, devoluções próprias e CT-e com a empresa
tomadora; o CT-e em que ela não é tomadora continua fora. Confirme o cancelamento pelo evento 110111 (nProt) ou pela
lista da SEFAZ. No SPED ICMS/IPI (conferido na Kopp em 07 e 08/2026) a cancelada sai como
`|C100|IND_OPER|IND_EMIT||55|02|SER|NUM|CHAVE|` com o resto vazio, sem COD_PART, C170 ou C190.

## ICMS antecipado
Entrada com crédito e ICMS destacado a 4% (importado): antecipado de 8% sobre a BC. Ajuste E111 PR000080 (débito)
e PR020212 (crédito) do mesmo valor (regra `antecipado` em regras.json).

## TXT de importação no Domínio
Formato validado: importado sem erros na Kopp 09/2026 (12/10/2026).
Base x alíquota de cada C170 tem de fechar com o ICMS (o Domínio recalcula): diferimento parcial (CST 51) vai com a
alíquota efetiva e crédito do Simples com a base = crédito / pCredSN. Venda a consumidor final de outra UF leva C101
(DIFAL). Notas corrigidas depois da importação: `txt_importacao.reimportar` gera o TXT _CORRECAO só com elas.
`--txt-cabecalho <SPED anterior da empresa>` gera `IMPORTACAO_DOMINIO_MMAAAA.TXT` (EFD ICMS/IPI, latin-1, CRLF) com
TODAS as notas do mês e a planilha `_conferencia.xlsx`. Modelo aceito pelo Domínio: EFD da Ectas 08/2026 —
COD_PART = CNPJ, série sem zeros, contadores com 9 dígitos, NFS-e tomada = C100 modelo 01 com CFOP 1933/2933
(UF pelo município da chave da NFS-e) e CST 090. C170 em TODAS as NF-e (o Domínio usa o COD_NAT = acumulador e só
confere os valores item a item): CST do Simples = CSOSN sem origem; IPI sem crédito entra no valor do item e o CST do
IPI fica vazio (senão o Domínio exige IPI no acumulador); frete/seguro/outras rateados pelo valor do item, como o
Domínio faz, e a sobra de arredondamento do emissor (até R$ 1,00) vai para outras despesas; código de produto com
10 caracteres (o Domínio corta em 14); sem CEST no 0200. Cancelada: COD_SIT 02 com participante, data, itens e C190
zerados — mas o Domínio ignora o participante
de documento com COD_SIT 02 e usa o da nota anterior, então com `txt_importacao.canceladas = lancar_manual` elas
saem do TXT e vão para a aba "Canceladas - lançar à mão". PIS/COFINS: notas próprias com CST e valores do XML
(o Domínio recusa CST 98 em saída); terceiros 98 zerado. Venda a consumidor final com IPI na base do ICMS: o
Domínio soma o IPI de novo em "outras" do ICMS e recusa — ajustar no Domínio (não há campo no leiaute). CT-e (D100) não tem campo de acumulador: vale o CFOP x
acumulador da importação. NFS-e só com `txt_importacao.incluir_nfse` (Kopp: modelo 01 sem espécie).

## Conta contábil
`regras.json` traz `contas_padrao` (por finalidade), `conta` dentro das regras e
`conta_por_fornecedor_razao` (aprendido do razão: histórico "COMPRAS ... <nº> <FORNECEDOR>" x conta de débito
contra 506 FORNECEDOR MODELO). Atualizar com o razão do período mais recente.

## Nova empresa
Indústria: seguir a skill `rof-fiscal-motor-industria` (`scripts/nova_empresa.py` cria a pasta e o regras.json a partir de
`empresas/_modelo-industria/`). Empresa já em produção: ver a skill dela (Kopp: `rof-fiscal-kopp-industria`).
