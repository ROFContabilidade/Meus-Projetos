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

## Como decidir (e quando perguntar)
1. Item novo sem regra sai como **FINALIDADE A DEFINIR**. Ler a descrição/NCM/fornecedor e propor a
   finalidade; perguntar ao escritório quando houver dúvida real (ex.: química que pode ser processo ou laboratório).
2. Resposta do escritório vira regra em `regras.json` (`finalidade_por_item`, `finalidade_por_fornecedor`
   ou `finalidade_por_ncm`) — nunca decidir de novo o mesmo caso no mês seguinte.
3. Acumulador sem cadastro (`ac: null`) aparece em Alertas: pedir o código ao escritório.
4. O SPED é o gabarito final; o relatório do Domínio é a importação antes das correções manuais.
   "Corrigido à mão?" mostra o retrabalho que a sugestão evita.
5. Nunca afirmar irregularidade sem a evidência na linha (XML, SPED ou relatório); usar VERIFICAR.

## Conta contábil
`regras.json` traz `contas_padrao` (por finalidade), `conta` dentro das regras e
`conta_por_fornecedor_razao` (aprendido do razão: histórico "COMPRAS ... <nº> <FORNECEDOR>" x conta de débito
contra 506 FORNECEDOR MODELO). Atualizar com o razão do período mais recente.

## Nova empresa
Copiar `regras.json` da Kopp, trocar `empresa`, `acumuladores` (tirar do relatório "Resumo por acumulador"
e do 0400 do SPED), `devolucoes_proprias`, `saidas` e zerar fornecedores/NCM específicos.
