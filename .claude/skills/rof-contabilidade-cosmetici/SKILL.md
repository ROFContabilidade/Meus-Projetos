---
name: rof-contabilidade-cosmetici
description: Lançamentos contábeis e conciliação bancária da COSMETICI (COSMETICI INDUSTRIA E COMERCIO DE COSMETICOS, CNPJ 33.039.048/0001-62, empresa 25 no Domínio, Lucro Presumido, indústria de cosméticos - PR) para o Domínio (Thomson Reuters). Extrato Itaú (conta 8) cruzado com o relatório "Extrato Da Conta" do ERP Cosmos, empresas do grupo (Cosmeticon, F.V.S, Gula/Fique Bem, Cabelo Meu) em conta de mútuo, conferência dos impostos fiscal x contábil (SPED x razão) e TXT único no leiaute Domínio. Usar quando mencionarem Cosmetici, a empresa 25, o CNPJ 33.039.048/0001-62, extrato Itaú da Cosmetici, relatório Cosmos, razão/balancete da Cosmetici ou conferência de impostos dela.
---

# ROF Contabilidade — COSMETICI (contábil)

Empresa 25 no Domínio · CNPJ 33.039.048/0001-62 · Fazenda Rio Grande/PR · Lucro Presumido desde 2026
(até 2025 Simples). Indústria de cosméticos. **Sem folha desde 03/2026.** A parte fiscal (XML, notas,
apuração) fica com a skill `rof-fiscal-cosmetici-industria`.

Arquivos do trabalho no repositório: `Cosmetici/Contabil/<período>/entregas` (o que foi entregue),
`.../dados` (JSON intermediários, balancete, razão, SPED) e os scripts em `scripts/` desta skill.
Ao terminar cada rodada: salvar lá, commit/push, enviar os arquivos (SendUserFile) e **atualizar a
seção "Histórico e status"** abaixo.

## Regras da usuária (Rosangela)
1. Não fazer a usuária preencher planilha: **decidir pelo razão, pelo balancete e pelo relatório Cosmos**; perguntar só o que não dá para decidir.
2. **Conferir sempre os pagamentos** contra o relatório Cosmos / histórico. **Recebimentos não precisam ser conferidos** (vão para 504 clientes).
3. O Domínio não exclui só a contrapartida: ou exclui o lançamento inteiro ou corrige manualmente. Por isso a correção é feita **excluindo todos os lançamentos da conta 8 do período e importando um TXT único** (nunca excluir lotes de integração do fiscal).
4. **Aplicação automática do Itaú não é segregada**: conta 8 = saldo total disponível (c/c + aplicação). Aplicações e resgates não são lançados; só o **rendimento vai para 432**. (Os 50 mil da conta 11 a usuária vai revisar.)
5. **Mazzoni (Carlos Alexandre, Michel Scander, Factoring A. Mazzoni)**: são sócios fora do contrato social, sem pró-labore → **deixar exatamente na conta que estava** no razão (em geral 362). Não usar pró-labore nem retirada de sócio. Boletos que o Cosmos lança como "pró-labore Mazzoni" (ex.: ASSOCIACAO F ~2.330/mês) seguem a mesma conta (362).
6. **Beauty Fair** → 688 FEIRAS E EVENTOS (inclusive devoluções à Claudia Rubin referentes à Beauty Fair).
7. **Conta 672 (EMPRESTIMO DE TERCEIRO) é SINTÉTICA no Domínio** – não usar. MRBS Administradora (parcela de empréstimo de 2016 que nunca foi para o passivo) → 364 como estava.
8. Usar como padrão de leiaute o TXT aceito pelo Domínio (pasta 06/2026, feito pela Cláudia).

## Leiaute TXT Domínio (cp1252, LF, histórico em MAIÚSCULAS)
```
|0000|33039048000162|
|6000|X||||
|6100|DD/MM/AAAA|DEBITO|CREDITO|1234,56||HISTORICO||||
```
Saída: D conta / C 8. Entrada: D 8 / C conta. Um `|6000|X||||` antes de cada `|6100|`. `scripts/saida.py:txt()`.

## Fontes
- **Extrato Itaú** (PDF mensal "COSMETICI-Extrato Mensal_<Mês>2026.pdf"; os OFX vinham idênticos → usar o PDF). `scripts/itau.py parse(path, ano)` (pdftotext -layout; para no "Saldo final"; confere saldo dia a dia).
- **Relatório Cosmos ERP "Extrato Da Conta"** ("Relatorio de conferencia MM.26.pdf" / "Relatorio Gestão"): colunas OP / PF (categoria) / PR, nome, observação. `scripts/cosmos.py` → JSON. Agosto/2026 veio incompleto (4 pagamentos).
- **Razão da conta 8 e balancete** do Domínio (xls → converter com `soffice --headless --convert-to csv`; xlrd falha).
- **Razão dos impostos** ("Razão_Impostos 2026.pdf") e **Resumo dos impostos** do fiscal ("Empresa 25 - ....pdf").
- **SPED EFD ICMS/IPI** (E110, E111, E116, E210, E250, E520) e **EFD-Contribuições** (M200 PIS, M600 COFINS) das pastas de cada mês.

## Cruzamento extrato × Cosmos (pagamentos)
Casar por data ±7 dias + valor + **semelhança do nome** (nunca só valor: PIX de mesmo valor para pessoas diferentes) e por **soma de grupo** (vários títulos num pagamento). Itens sem Cosmos: classificar pelo **histórico do mesmo favorecido de jan–jul** (`linhas_jan_ago.json`), não pela descrição genérica do banco.

### Categorias Cosmos (PF) → conta
| PF / favorecido | Conta |
|---|---|
| 53 comissão s/ vendas | 308 COMISSÕES |
| 97 / 4 fretes (Braspress, Rodonaves, Tex, Expresso São Miguel, MHLog...) | 312 FRETES |
| 81, 170, 171, 181 serviços PF/contrato; pessoas físicas pagas por serviço | 362 SERV. TERCEIROS |
| 45 Protection Assessoria (contabilidade) | 361 ASSIST. CONTÁBIL (não é grupo, mesmo citando Cosmeticon na obs.) |
| 47 software (Cosmos/CRMTech, Tecnoponto) | 640 SOFTWARE |
| 184 Beauty Fair | 688 FEIRAS E EVENTOS |
| 185 RNX / FIDC (antecipação) | 504 |
| 94 empréstimos de terceiros (Selito, MRBS) | conta original (672 é sintética); Factoring Mazzoni = regra Mazzoni |
| 6/9/104 fornecedor com NF (matéria-prima, embalagem) | 506 FORNECEDORES (Alloxy, Barentz, Skin Lab, Nova Piramidal...) |
| Savatec | 359 · Juarez A. Polli | 58 · Pizza Pack | 493 (como em 02/2026) |
| Melo & Cruz (aluguel) + condomínio | 320 |
| Tarifas 626 · IOF 625 · juros 375 · Itaucard 357 · rendimento 432 · recebimentos 504 |

### Empresas do grupo (uma conta corrente de mútuo por empresa, entrada e saída)
COSMETICON → 663 · F.V.S → 662 · CABELO MEU → 670 · GULA / FIQUE BEM (mesmo CNPJ) → 366.
Recebimento de **nota de venda** dessas empresas continua baixando o cliente (664 Cosmeticon / 671 FVS).
"OUTRAS ENTRADAS/SAÍDAS" do Cosmos (PF 71/1, OP 122/123) costumam ser transferências do grupo.
10 itens "outras" do Cosmos (+6.100 / −27.813) não estão no Itaú (provável outra conta).

## Conferência de impostos fiscal × contábil (fazer todo mês)
Comparar SPED/Resumo do fiscal com o razão das contas 29, 30, 171, 172, 176, 177, 178, 179, 180, 183, 481, 526.
- **IPI** 171/29 (E520), **ST** 481 (soma E210/E250), **IRPJ 176 / CSLL 177** (trimestral: 8%/12% presunção, 15% + adicional 10% acima de 60 mil/tri, CSLL 9%), **ISS retido 183**, **IRRF 178**: bateram jan–ago/2026.
- **ICMS 172 – erro recorrente da integração:** o ajuste de débito do E111 (PR000080 ICMS antecipado, PR000081 DIFAL) vai para a **526** e o crédito PR020212 abate a 172 → a 172 fica menor que a guia 1015 (em 01/2026 ficou devedora). Correção mensal **D 526 / C 172** pelo total do ajuste de débito (172+526 não muda). Pedir para corrigir a configuração do imposto "ICMS Antecipado - 1015 (3)" no Domínio para creditar a 172.
- **Crédito de ICMS das entradas** (30): conferir com E110 campo VL_TOT_CREDITOS; diferença = refazer integração das entradas do mês (05/2026 +1.247,52 e 06/2026 +154,64 pendentes).
- **PIS/COFINS**: conferir com M200/M600 da EFD **retificadora** (04/2026 o contábil ficou com a original).
- Layout E110: r[2] débitos, r[4] aj. débitos, r[6] créditos, r[8] aj. créditos, r[11] saldo, r[13] a recolher.
- Nenhuma conta de imposto tem baixa por pagamento em 2026 (só 3 SISPAG de ST em 04/2026) – impostos declarados e não pagos (dívida confessada, já ciente).
- IBS/CBS 2026 só informativo – não lançar.

## Conferência após importar
Saldo da conta 8 no fim de cada mês: 01 3.915,09 C · 02 38.533,72 C · 03 21.916,33 C · 04 2.486,01 D · 05 8.520,05 C · 06 1.254,93 C · 07 8.386,26 D · 08 3.506,09 C.
Impostos em 31/08 após o TXT de correção: 172 208.936,83 C · 526 72.983,74 C · 179 31.807,97 C · 180 148.430,30 C · 481 383.924,19 C.

## Scripts (`scripts/`, rodar a partir da pasta de trabalho com `cos/` e `tools/`)
`itau.py` (parser PDF Itaú) · `cosmos.py` (parser relatório Cosmos) · `regras_cosmos.py` (PF → conta) ·
`cruza.py` (Cosmos × razão) · `decide.py` (regras de decisão, grupo) · `gera.py`/`classif.py` (jul/ago) ·
`planilha_unica.py` (planilha de correção + TXT único jan–ago + conciliação mensal) · `saida.py` (txt/head) ·
`impostos.py` (conferência fiscal × contábil + TXT de correção de impostos).

## Histórico e status
**Rodada 12/10/2026 (jan–ago/2026)** – arquivos em `Cosmetici/Contabil/2026-01_a_08/entregas/`:
- `COSMETICI_TXT_UNICO_extratos_e_impostos_jan-ago2026.txt` – **arquivo final**: 1.789 lançamentos do Itaú jan–ago + 10 de impostos (8× D 526/C 172; PIS D 179/C 429 2.470,93 e COFINS D 180/C 428 11.404,30 em 30/04). Já com MRBS na 364 e as 12 reclassificações de jul/ago.
- `COSMETICI_TXT_UNICO_jan-ago2026.txt` – só extratos. `COSMETICI_extrato_julho2026_dominio.txt` / `..._agosto...` – mesmos lançamentos separados por mês (não importar junto com o único).
- `COSMETICI_reclassificacao_pagamentos_07-08_2026.txt` – 12 reclassificações (usar só se jul/ago já tinham sido importados sem elas): Ismael 17/08 362→308; Savatec 04/08 640→359; Braspress 07/08 350→312; Juarez 04/08 506→58; Tecnoponto 20/07, 30/07, 18/08 506→640; Alloxy 23/07 (2x) e 14/08 56→506; Associação F 28/07 e 03/08 506→362.
- `COSMETICI_correcao_impostos_jan-ago2026.txt` + `COSMETICI_conferencia_impostos_fiscal_x_contabil_jan-ago2026.xlsx`.
- `COSMETICI_planilha_correcao_jan-ago2026.xlsx` (decisões e conciliação; não reflete MRBS 364 nem as 12 reclassificações) e `COSMETICI_empresas_do_grupo_jan-ago2026.xlsx` (abas F.V.S, Cosmeticon, Gula).
- Importação: na primeira tentativa do TXT único o Domínio recusou só a linha 1847 (672 sintética) → corrigido para 364. Confirmar com a usuária se a importação foi concluída antes de mandar outro arquivo (não duplicar).

- **Conferência pós-importação (razão "Razão-Conferencia.xls", 12/10 23:26):** jan–jun batem lançamento a lançamento. Julho e agosto entraram DUAS vezes (TXT único às 22:56 + arquivos mensais) → saldo 31/08 5.757,25 C. Orientado excluir os lotes **29339 a 29798** (cópia antiga, com as contas antes das 12 reclassificações). Manter 29799–29808 (correções de impostos) e 29809–30268 (jul/ago corretos). Não importar o TXT de reclassificação. **Usuária confirmou a exclusão dos lotes 29339–29798 em 12/10.** Sempre conferir o razão da conta 8 depois de importar (comparar data+valor+contrapartida com o TXT).

**Pendências**
- Refazer integração das entradas de 05 e 06/2026 (crédito ICMS a maior 1.247,52 e 154,64).
- IRRF 03/2026 52,93: lote 22449 debitou a 178 contra a 31 – verificar a nota (se retenção sobre serviço tomado: D 31 / C 178 105,86).
- EFD-Contribuições na pasta de 07/2026 tem os valores de agosto – confirmar a transmitida (fiscal/contábil: PIS 2.975,63, COFINS 13.787,78).
- Ajustar no Domínio a configuração do ICMS Antecipado 1015 (3) → 172.
- Conta 506 com saldo devedor (180 mil em 06/2026) – revisar; conta 11 aplicação (50 mil) – usuária vai revisar.
- Setembro/2026: falta o extrato; IRPJ/CSLL do 3º trimestre na apuração de setembro.
