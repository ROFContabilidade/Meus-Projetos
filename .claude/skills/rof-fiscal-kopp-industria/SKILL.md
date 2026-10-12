---
name: rof-fiscal-kopp-industria
description: Fechamento fiscal mensal da KOPP INDÚSTRIA E COMÉRCIO DE PRODUTOS ODONTOLÓGICOS LTDA (Domínio 60, CNPJ 02.967.738/0001-58, PR, Lucro Presumido) - conferência das notas de entrada e saída, classificação, créditos, CT-e, NFS-e e retenções, planilhas para a analista e TXT de importação no Domínio. Usar quando pedirem a parte FISCAL da Kopp Indústria (notas do mês, XML, acumuladores, TXT de importação, canceladas, inutilizadas, relatório de erros do Domínio). Lançamentos contábeis/extrato da Kopp ficam com a skill rof-contabilidade-kopp-industria.
---

# Kopp Indústria — fiscal mensal

Piloto do motor `rof-fiscal-motor-industria` (ler antes as regras gerais e a tabela de erros do Domínio).
Regras da empresa: `Fiscal/empresas/60-kopp-industria/regras.json` (cada decisão com `_motivo` e em `_decisoes`).
Saídas do mês: `Fiscal/empresas/60-kopp-industria/<AAAA-MM>/` (fora do git).

## Empresa
Indústria de implantes e componentes odontológicos (NCM **9021**) e instrumentais/kits cirúrgicos (**9018**).
Vende produção (5101/6101: implantes, componentes, chaves, conexões, torquímetros, estojos) e revende (5102/6102:
principalmente brocas). Alíquota interna 19,5%. Implantes 9021 saem isentos no PR (item 67 Anexo V RICMS-PR,
cBenef PR810067, Conv. ICMS 126/10 mantém o crédito — sem estorno).

## Arquivos do mês (Drive: `Arquivos RENATA Dominio/60 - KOPP INDUSTRIA/<ano>/<MM_AAAA>`)
- `Doc's`: `DownloadDFe_*.zip` (SEFAZ — traz todas as NF-e próprias e cancelamentos), `notas_vendas_*.zip` e
  `devolucao_vendas_*.zip` (do cliente), `notasXML*.zip` (CT-e/terceiros).
- `notasExcel*.xlsx` (listas SEFAZ, aba `download_excel` — usar TODAS), `Relatório de Notas Fiscais Kopp
  Indústria.xlsx` (ERP), `*Recebidas - Completa*.xlsx` (NFS-e nacional), `Entradas.pdf` (histórico Domínio),
  `Empresa 60 - KOPP INDUSTRIA.pdf` (Resumo por acumulador).
- Cabeçalho do TXT: SPED ICMS/IPI do mês anterior (`Sped_Fiscal_kopp.txt`).

## Rodar (mês aberto)
```
python3 Fiscal/scripts/conferencia.py --regras Fiscal/empresas/60-kopp-industria/regras.json \
  --xml <pasta com todos os XML extraídos> \
  --sefaz notasExcel.xlsx notasExcel1.xlsx notasExcel2.xlsx --sefaz-aba download_excel \
  --historico Entradas.pdf --acumuladores "Empresa 60 - KOPP INDUSTRIA.pdf" \
  --nfse-recebidas "...Recebidas - Completa....xlsx" --erp-notas "Relatório de Notas Fiscais Kopp Indústria.xlsx" \
  --xml-anteriores <XML do mês anterior> --txt-cabecalho <SPED do mês anterior> \
  --competencia AAAA-MM --saida Fiscal/empresas/60-kopp-industria/AAAA-MM/Pre_Conferencia_Kopp_Industria_MM-AAAA.xlsx
```
Gera: Pre_Conferencia, Entradas_para_conferencia, Saidas_MM-AAAA, IMPORTACAO_DOMINIO_MMAAAA.TXT (+ _conferencia.xlsx,
_SEM_NOTAS_DO_ZIP, _CORRECAO conforme `txt_importacao`). Entregar também: acumuladores em uso, zip das canceladas,
relatório Canceladas e inutilizadas, inutilizadas (o TXT já leva).

## Acumuladores (Domínio da Kopp)
- Entradas: 113/213 compra p/ industrialização e revenda (1101/1102, 2101) · 107/207 uso e consumo · 108 uso e consumo
  c/ ST · 121/221 bonificação 1910/2910 (**com crédito**) · 124/224 outras entradas · 151/251 retorno de conserto ·
  154 retorno de industrialização 1902 · 155 industrialização por terceiros 1124 · 150/250 retorno de consignação ·
  159 retorno de exposição/feira 1914 · 133/233 devolução de venda (próprias).
- CT-e (só Kopp tomadora): **304** com ICMS, **302** sem ICMS (CFOP 1352/2352). No Domínio deixar 1352/2352 → 304.
- Saídas: 507/607 venda produção · 508/608 revenda · 521/621 consignação · 522/622 outras saídas · 523/623
  bonificação · 524/624 comodato · 530 remessa p/ industrialização · 626 conserto · 631 feira 5914/6914 · 632 exportação.
- Serviços: um acumulador por item da LC 116 (8xx "SERVIÇOS TOMADOS xx.xx"); com retenção, o de mesmo item com
  "IRRF/CSRL" no nome. NFS-e **não** vai no TXT (modelo 01 sem espécie no Domínio da Kopp) — lança pela planilha.
- Ajustes pendentes no Domínio (09/2026): vincular ICMS ao 521, 621, 159 e 302; IPI ao 522; DIFAL no 607/608.

## Decisões do escritório (Rosangela) — já estão no regras.json
- **Formato atual mantido (13/10/2026):** a Kopp segue com os acumuladores como estão (107, 108, 113, 213...). O Domínio
  contabiliza a nota pela conta do acumulador e ignora a conta do item (COD_CTA) do TXT; o escritório aceita assim e
  não cria acumulador por conta. `acumulador_por_conta` fica vazio. O TXT continua mandando a conta certa por item
  (planilhas também), para conferência ou ajuste manual quando necessário. Não oferecer de novo sem pedido.
- Uso e consumo sem crédito: base e ICMS zerados; de fora do estado gera DIFAL. Conta de revenda: 55.
- Crédito a 4% → ICMS antecipado 8% (E111 PR000080 / PR020212).
- Canceladas lançadas zeradas (participante + chave), **pelo XML**; inutilizadas no TXT (COD_SIT 05).
- Número sem XML, sem SEFAZ e sem chave no ERP → inutilizar na data das vizinhas.
- XML prevalece sobre o ERP. Retornos autorizados maiores que a remessa: lançar. Notas sem cBenef em 5901/6901: aceitas.
- Consignações (5917/6917) e devoluções saem do ERP com CST 00 e ICMS zero: aceito (isenção 9021).
- Fornecedores: Cipamed = embalagem; Air-Press, JC Gráfica, Cia da Embalagem = uso e consumo; Indusbello estojos;
  Biomedicare brocas = revenda; Cichon etiquetas = embalagem; Unimed conta 282; V M Comunicações sem retenção.
- NFS-e de outra competência: só apontar, não lançar.

## Pontos em aberto (atualizar a cada mês)
- Série 2 do ERP (09/2026: 51 documentos, R$ 259.970,85, "cliente retira", sem NF-e): resposta da Kopp.
- 64283 (venda PIX R$ 4.088,60, cliente com documento "ME95466") e 64393 (bonificação R$ 12.607,00): pedido no ERP sem
  NF-e autorizada — confirmar se a mercadoria saiu e se os números foram inutilizados na SEFAZ (relatório PDF entregue).
- Estojos Indusbello entram como 1101 (insumo); confirmar se a Kopp só revende (seria 1102).
- Biomedicare 2140 + 2154 devolvem mais do que a remessa 64068: lançadas (autorizadas).
- Correção 09/2026: excluir no Domínio e reimportar 1237, 1076, 2153, 64171, 64289 (`_CORRECAO.TXT`).

## Histórico do TXT
09/2026: canceladas importadas pelo zip de XML (nota + evento 110111) sem problema — confirmado pela Rosangela.
09/2026: 3 rodadas de erro até importar sem erros (12/10/2026); depois, revisão do crédito (base x alíquota no
diferimento e no Simples) e DIFAL das saídas (C101). Ver tabela de erros na skill do motor.
