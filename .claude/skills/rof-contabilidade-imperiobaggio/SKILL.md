---
name: rof-contabilidade-imperiobaggio
description: "Regra de distinção sócia/cliente: pró-labore e retirada só com CPF 030.704.189-10 identificado; sem CPF = recebimento de cliente (504)"
---

# ROF Contabilidade Império Baggio — Lançamentos Contábeis e Conciliação

## Dados da Empresa

| Campo | Informação |
|---|---|
| Razão social | MARIA P S BAGGIO RESTAURANTE |
| Nome fantasia | Império Baggio |
| CNPJ | 20.632.522/0001-13 |
| CNPJ sem formatação | 20632522000113 |
| CNAE principal | 5611-2/01 — Restaurantes e similares |
| Setor | Restaurante / Alimentação |
| Regime tributário | Simples Nacional |
| Banco principal | Banco Sicredi — Conta 90051-5 → cód **8** |
| Aplicação financeira | Poupança Sicredi → cód **11** |
| Cadastrado por | Rosangela |
| Escritório contábil | PAES E BASTOS CONTABILIDADE LTDA (CNPJ 29.650.531/0001-01) |
| Contadora responsável | RENATA BASTOS AMADO — CRC PR075217/O-2 |

---

## Sócios

| Sócio | CPF | Conta no Domínio |
|---|---|---|
| MARIA PINHEIRO DOS SANTOS BAGGIO | 030.704.189-10 | **563** (ativo — retiradas) |

---

## Funcionários CLT

| Nome | Cargo | Salário base |
|---|---|---|
| JANAINE MAIA DE OLIVEIRA LIMA | Auxiliar de Cozinha | R$ 1.585,00 |

> Dados completos da folha serão buscados no Domínio: Módulo Folha → Relatórios → Cadastrais → Empregado, quando o primeiro extrato chegar.

---

## Regras de Trabalho (ACORDO COM A CONTADORA)

1. **Fidelidade total** aos dados enviados — não alterar nada sem consultar
2. **Consulta prévia** antes de qualquer alteração
3. **Base legal** sempre que sugerir algum ajuste
4. **Histórico**: copiar o texto exatamente como aparece no extrato bancário

---

## Regras Gerais de Classificação (confirmadas 08/2026)

1. **Pagamento a PESSOA FÍSICA** (exceto sócios e colaboradores CLT) → **sempre conta 362** (serviços de terceiros PF).
2. **Pagamento a CNPJ** ainda não mapeado → **pesquisar a atividade do CNPJ na Receita Federal** e alocar a conta conforme a atividade, sob a ótica de um restaurante (mercadoria/insumo → 506/521; serviço → 359/362; etc.).
3. **Compras de mercadoria / insumo para revenda** (mercados, carnes, bebidas, distribuidoras, panificadoras, doces), seja por boleto, PIX ou COMPRAS NACIONAIS no cartão: o **pagamento no banco vai SEMPRE para 506** (D 506 / C 8) e a **compra é reconhecida como despesa em 470** por lançamento interno **D 470 / C 506** (não entra no TXT bancário). **Nunca lançar pagamento de mercadoria direto em 470.**

---

## Leiaute do Arquivo TXT para Domínio

```
|0000|20632522000113|
|6000|X||||
|6100|DD/MM/AAAA|CONTA_DEBITO|CONTA_CREDITO|VALOR||HISTORICO||||
```

- **Um bloco `|6000|X||||` para CADA lançamento**, seguido da linha `|6100|...` (não usar um único |6000| para vários |6100|).
- Pagamento (saída): débito na conta de despesa/ativo, crédito no banco (8)
- Recebimento (entrada): débito no banco (8), crédito na conta de receita
- Arquivo único: pagamentos e recebimentos ordenados por data
- Valor com vírgula decimal: ex. 1500,00
- Codificação: latin-1
- **Sanitização obrigatória do histórico:** remover TODO `|` do campo histórico (`hist.replace('|',' ').strip()[:60]`). Os memos Sicredi trazem `|0001-13` embutido (ex.: `SICREDI CREDITO ELO-869248405 |0001-13`) — se não removido, o Domínio rejeita com erro de filial.

---

## Plano de Contas — Contas Operacionais

| Cód | Classificação | Nome | Natureza |
|---|---|---|---|
| 8 | 1.1.1.02.001 | BANCO SICREDI - CONTA 90051-5 | Ativo |
| 11 | 1.1.1.03.001 | APLICAÇÃO POUPANÇA SICREDI | Ativo |
| 34 | — | TRIBUTOS PAGOS A MAIOR OU INDEVIDAMENTE | Ativo |
| 52 | — | OUTRAS ENTRADAS | Ativo |
| 188 | 2.1.5.01.002 | PRÓ-LABORE A PAGAR | Passivo |
| 191 | 2.1.5.02.001 | INSS A RECOLHER | Passivo |
| 245 | — | CAPITAL SOCIAL | PL |
| 275 | 3.1.1.02.002 | PRÓ-LABORE | Despesa |
| 339 | 3.2.2.01.009 | ASSISTÊNCIA MÉDICA E SOCIAL | Despesa |
| 350 | 3.2.2.03.005 | TAXAS DIVERSAS | Despesa |
| 354 | 3.2.2.04.001 | ENERGIA ELÉTRICA | Despesa |
| 355 | 3.2.2.04.002 | ÁGUA E ESGOTO | Despesa |
| 356 | 3.2.2.04.003 | TELEFONE/INTERNET | Despesa |
| 359 | 3.2.2.04.006 | DESPESAS ADMINISTRATIVAS | Despesa |
| 360 | 3.2.2.04.007 | DESPESA COM ALIMENTAÇÃO | Despesa |
| 361 | 3.2.2.04.008 | ASSISTÊNCIA CONTÁBIL | Despesa |
| 362 | 3.2.2.04.009 | SERVIÇOS PRESTADOS POR TERCEIROS | Despesa |
| 364 | 3.2.2.04.011 | DESPESA COM DESLOCAMENTO | Despesa |
| 366 | 3.2.2.04.013 | PLANO COM ASSISTÊNCIA MÉDICA | Despesa |
| 408 | 4.1.1.01.003 | VENDA DE MERCADORIAS | Receita |
| 447 | — | BONIFICAÇÃO, DOAÇÃO E BRINDES | Receita |
| 470 | 3.1.7.01.001 | CUSTOS DAS MERCADORIAS VENDIDAS (CMV) | Despesa |
| 479 | 2.1.4.01.015 | SIMPLES NACIONAL A RECOLHER | Passivo |
| 480 | 4.1.2.03.008 | (-) SIMPLES NACIONAL | Dedução |
| 493 | 3.2.2.04.014 | DESPESAS DIVERSAS | Despesa |
| 504 | 1.1.2.01.001 | CLIENTES DIVERSOS | Ativo |
| 506 | 2.1.3.01.001 | FORNECEDOR MODELO | Passivo |
| 510 | 2.1.6.02.001 | HONORÁRIOS CONTÁBEIS | Passivo |
| 521 | 3.2.2.01.012 | DESPESAS COM ALIMENTAÇÃO (insumos cozinha) | Despesa |
| 522 | — | LUCRO ACUMULADO DO EXERCÍCIO | PL |
| 523 | — | (-) PREJUÍZO ACUMULADO DO EXERCÍCIO | PL |
| 525 | 3.2.2.05.009 | TARIFAS BANCÁRIAS | Despesa |
| 526 | — | AJUSTE EXERCÍCIO ANTERIOR | — |
| 548 | 3.2.2.04.015 | DESPESAS COM MARKETING | Despesa |
| 549 | 3.2.2.04.016 | DESPESAS COM CARTÃO DE CRÉDITO | Despesa |
| 550 | — | CONSÓRCIO SICREDI | Ativo (confirmar natureza no balancete) |
| 563 | — | CONTA SÓCIO — MARIA P S BAGGIO (retiradas) | Ativo |
| 565 | 3.2.2.04.017 | MATERIAL DE LIMPEZA/COPA/CONSUMO | Despesa |

---

## Regra de Classificação dos Lançamentos

### Para cada lançamento do extrato, siga esta ordem:

1. Identificar natureza (entrada / saída)
2. Identificar favorecido (nome, CNPJ/CPF)
3. Consultar a seção "Classificações Confirmadas" abaixo
4. Se **PF** não sócio/colaborador → **362**
5. Se **CNPJ** não identificado → pesquisar na Receita Federal → verificar atividade → classificar conforme plano de contas
6. Se sócio (CPF 030.704.189-10) → aplicar **Regra de Retiradas**
7. Histórico: copiar exatamente como aparece no extrato

---

## Regra Inviolável — Conferência de Saldo

> Nunca entregar o TXT sem que os saldos do extrato estejam fechando.

1. Saldo anterior (abertura) informado no extrato
2. Saldo final (encerramento) informado no extrato
3. Diferença esperada = Saldo final − Saldo anterior
4. Somar todas as entradas lançadas no TXT
5. Somar todas as saídas lançadas no TXT
6. Diferença apurada = Total entradas − Total saídas

**Se Diferença apurada ≠ Diferença esperada → NÃO entregar o TXT.**

> ⚠️ OFX do Sicredi só traz o **saldo final** (BALAMT), não o de abertura. Nesses casos, conferir entradas − saídas = variação, e cruzar a abertura implícita com o app/PDF do cliente.

---

## Regra Inviolável — Aplicação Poupança (conta 11)

> Nunca omitir movimentações de aplicação financeira do TXT.

- **Aplicação (saída do banco):** D **11** / C **8**
  - Históricos: `REF. A APLICACAO POUPANCA` e `APLICACAO POUPANCA-CAPTACAO`
- **Resgate (entrada no banco):** D **8** / C **11**
- A poupança Sicredi não gera rendimento tributável separado no extrato (rendimentos já líquidos incorporados ao saldo).

---

## Regra Inviolável — IOF e IRRF

> Nunca omitir IOF nem IRRF do TXT.

- Esta empresa não possui aplicação financeira com rendimento tributável separado identificado até o momento.
- Caso apareça IOF ou IRRF no extrato → classificar em **350** (Taxas Diversas) — confirmar com a contadora.

---

## Regra — Consórcio Sicredi (conta 550)

> `DEBITO CONVENIOS-CONSORCIO ... ADM.CONSORCIO SICREDI` (CNPJ 07.808.907/0001-20) → **D 550 / C 8**.
> ⚠️ **NÃO é Simples Nacional** — não confundir com `DEBITO CONVENIOS` do Simples (479). O texto do histórico traz "CONSORCIO" e "ADM.CONSORCIO SICREDI". Confirmado em 08/2026.

---

## Regra Mensal — Retiradas dos Sócios

> ⚠️ **ATENÇÃO:** O nome da empresa (MARIA P S BAGGIO RESTAURANTE) é idêntico ao nome da sócia (MARIA PINHEIRO DOS SANTOS BAGGIO). Por isso, **a classificação como pró-labore ou retirada só se aplica quando o CPF da sócia (030.704.189-10) estiver identificado no lançamento.** Se o lançamento trouxer o nome da empresa/sócia mas sem o CPF — ou com CNPJ próprio da empresa — classificar como **recebimento de cliente (D 8 / C 504)**.

| Situação no extrato | Classificação |
|---|---|
| Lançamento com **CPF 030.704.189-10** | Pró-labore (188) ou retirada (563) — aplicar regra abaixo |
| Lançamento com nome MARIA / BAGGIO **sem CPF identificado** | **504** — recebimento de cliente |
| Lançamento com **CNPJ 20.632.522/0001-13** (próprio da empresa) | **504** — recebimento de cliente (ou estorno — analisar) |

> ANTES DE LANÇAR qualquer pagamento a sócio: confirmar com a contadora o total pago no mês.

**Pró-labore base: salário mínimo nacional vigente — R$ 1.621,00 (2026). Atualizar sempre que o salário mínimo for reajustado.**

### Reconhecimento do pró-labore (lançamento interno — não é extrato):

> ⚠️ **NÃO entra no TXT** — importado da folha do Domínio (confirmado pela contadora em 24/09/2026). Quadro mantido só como referência.

| Lançamento | Débito | Crédito | Valor |
|---|---|---|---|
| Pró-labore do mês | **275** | **188** | R$ 1.621,00 |
| INSS a recolher | **188** | **191** | R$ 178,31 |

### Pagamentos via extrato bancário:

| Cálculo | Valor |
|---|---|
| Base (salário mínimo) | R$ 1.621,00 |
| INSS (11%) | R$ 178,31 |
| Pró-labore líquido | R$ 1.442,69 |

| Valor acumulado no mês | Débito | Crédito | Histórico sugerido |
|---|---|---|---|
| Até R$ 1.442,69 (pró-labore líquido) | **188** | **8** | conforme extrato |
| Excedente (retirada adicional) | **563** | **8** | conforme extrato |

- **Pagamento do INSS pró-labore à Receita Federal** (CNPJ 00.394.460/0058-87, DARF código 1099 — CP Segurado Contribuinte Individual, R$ 178,31): **D 191 / C 8** (baixa do INSS a recolher). Confirmado 08/2026 (substitui a antiga dúvida 191 vs 350).
- **Multa/juros de tributos** (ex.: DARF código 4406 — multa por atraso PGDAS-D): **D 350 / C 8** (taxas diversas) — confirmar com a contadora.
- Em **08/2026 não houve retirada nem pró-labore líquido pago à sócia** pela conta Sicredi (só o INSS de R$ 178,31 recolhido).

---

## Regra — Devolução / Aporte do Sócio

Quando Maria deposita valores **na empresa** (entrada no extrato):

| Débito | Crédito |
|---|---|
| **8** (banco) | **563** (conta ativo da sócia) |

---

## Particularidades do Banco

**Sicredi — conta corrente, banco cooperativo (não é banco intermediário com reserva)**

- Tarifas e encargos:
  - `CESTA DE RELACIONAMENTO` → **D 525 / C 8**
  - `INTEGR.CAPITAL SUBSCRITO` → **D 525 / C 8**
  - `EST CESTA/TARIFA SERVICO` → **D 525 / C 8** (se crédito/estorno: D 8 / C 525)
- O Sicredi é o próprio adquirente dos cartões (SICREDI CREDITO / SICREDI DEBITO) — créditos do maquininha liquidam direto na conta, sem intermediário.
- **Não há reserva/liberação de liquidez** — cada crédito é definitivo ao entrar na conta.
- **⚠️ Regra obrigatória ao gerar o TXT:** o extrato Sicredi inclui o código da filial (`|0001-13`, `|99|0001-13`, `|VISA|0001-13` etc.) dentro do texto do histórico. Como o Domínio usa `|` como separador de campos, esses trechos causam erro de importação. **Antes de salvar o TXT, remover todos os `|` do histórico.**

---

## Classificações Confirmadas pelo Razão

### RECEBIMENTOS (entradas no banco → D 8)

| Descrição no extrato | CNPJ/CPF | Crédito | Observação |
|---|---|---|---|
| REF. A RECEBIMENTO PIX [qualquer CPF/CNPJ] | qualquer | **504** | clientes PF e PJ (mesmo memo com nome de PF = cliente, não 362) |
| SICREDI CREDITO/DEBITO (VISA/MASTER/ELO/AMEX) | — | **504** | adquirência cartão |
| REF A SUB CR/DB | — | **504** | subcredenciamento |
| VR Benefícios | 02.535.864/0001-33 | **504** | vale refeição/alimentação |
| Alelo | 04.740.876/0001-25 | **504** | vale refeição/alimentação |
| Ticket | 47.866.934/0001-74 | **504** | vale refeição/alimentação |
| Pluxee | 69.034.668/0001-56 | **504** | vale refeição/alimentação |
| Banco Topázio | 07.679.404/0001-00 | **504** | intermediário cartões |
| REF A RECEBIMENTO PIX [99 Food — 60112920000123] | — | **504** | repasse vendas delivery |
| DEVOLUCAO PIX de prestador PF (ex.: Gustavo Baggio) | — | **362** | estorno de serviço PF (reduz 362) |
| EST CESTA/TARIFA SERVICO (crédito) | — | **525** | estorno de tarifa |
| EST. DEB VISA ELECTRON UBER TRIP | — | **364** | estorno de deslocamento (exceção!) |

### PAGAMENTOS (saídas do banco → C 8)

#### Fornecedores de mercadoria — pagamento D **506** / C **8** + reconhecimento interno D **470** / C **506**
Todo pagamento de mercadoria/insumo para revenda (boleto, PIX ou COMPRAS NACIONAIS no cartão) vai para **506** no banco; o custo entra em **470** por lançamento interno (D 470 / C 506). Nunca lançar pagamento de mercadoria direto em 470. Fornecedores confirmados:

| Fornecedor | CNPJ |
|---|---|
| MAX COLOMBO / COLOMBO RMC | — |
| SUPER MUFFATO / SUPERMERCADOS S | — |
| SUPERMERCADOS SANTOS | — |
| STIVAL E LARA | — |
| FRIMESA | — |
| SEGALAS ALIMENTOS | 01.333.984/0001-95 |
| COPAL ALIMENTOS | — |
| BRF SA | — |
| OESA | — |
| BALLESTEROS | 76.649.169/0001-39 |
| LA NUOVA PASTA | — |
| PALMIPAO / PANIFICADORA SAO / PANI SAO DOMINGOS | — |
| DONATELLA PANIFIC / GEBELLA PANIFICAD (panificadoras) | — |
| DISTRIBUIDORA DE DOCES | — |
| HUGO CINI | 76.490.572/0001-68 |
| FRUTARIA AVILA | — |
| L5W ALIMENTOS | — |
| JCRC DISTRIBUIDORA | — |
| PARMA DIST | 86.836.848/0001-70 |
| PJL COMERCIO DE GAS | 11.088.956/0001-03 |
| SPAL IND BRAS DE BEBIDAS (refrigerantes) | 61.186.888/0001-93 |
| REFRIKO IND COM BEBIDAS | 10.656.672/0001-03 |
| FRIGO M | 09.028.367/0001-98 |
| COMERCIO DE CARNES DONAU | 85.032.688/0001-44 |
| DESTRO BRASIL DISTRIBUICAO | 13.495.487/0001-72 |
| FERREIRA E SILV (ferragista/materiais) | — |
| CRBS S.A. / CDD CURITIBA | 56.228.356/0059-58 |
| JM MOVEIS SOB MEDIDA | 37.152.887/0001-43 |

> **Bonificações SPAL:** `BONIFICACAO RECEBIDA` → D **447** / C **470** (reduz CMV)
> **Outras entradas BRF:** `OUTRAS ENTRADAS BRF S.A.` → D **52** / C **506**

#### Insumos de cozinha não-CMV (D **521**)

| Fornecedor / Descrição |
|---|
| MP OVOSBORATO (ovos) |
| KI BIFE COLOMBO |
| PRV PRODUTOS ALIMENTÍCIOS |
| EMPORIO KIBIFE |
| NOBRE PAN / ARABIS ESFIRRARIA |
| UPSORVETERIA |
| IFOOD (insumos) |
| Outros pequenos fornecedores de insumos de cozinha |

#### Serviços de terceiros — Pessoas Físicas (D **362**)
**Regra geral:** todo pagamento PIX a CPF (autônomos), exceto a sócia, vai para **362**.

| Nome | CPF |
|---|---|
| ROSANGELA VAZ DOS SANT | 057.094.689-16 |
| JESSICA BAGGIO | 068.863.679-94 |
| JEFFERSON GASPARIN | 023.088.989-17 |
| SILVANA FRANDINA | 631.860.479-00 |
| GUSTAVO BAGGIO DE SOUZ | 155.480.559-76 |
| GABRIEL BAGGIO DA SILVA | — |
| MICHELY BAGGIO DA SILVA | 033.731.119-60 |
| EMANUELLY BAGGIO DE SO | 155.480.699-26 |
| MARIA EDUARDA BAGGIO ROCHA | 118.348.109-81 |
| ANA CRISTINA BAGGIO | 053.646.769-27 |
| POLIANA SCHMIDT | 102.982.819-96 |
| ROGERS PONTAROLO | 068.759.799-42 |
| FRANCIELE APARECIDA | 078.991.889-70 |
| CARLA CRISTINA MEDEIRO | 026.101.189-88 |
| MILTON SERGIO PERPETUO | 713.500.559-72 |
| GUSTAVO HENRIQUE CRUZ | 149.097.019-31 |
| JINMEI SITU | 800.363.829-14 |
| ANNA LUIZA KEPPEL | 123.769.549-08 |
| ANA LUCIA BAGGIO | 042.458.639-86 |
| JOAO PINHEIRO DOS SANTOS | 321.317.989-20 |
| LEANDRO DE OLIVEIRA | — (confirmado 08/2026) |
| MARIA APARECIDA MARTINS CASTRO | 718.049.789-49 |
| SIRLEI BERNARDI | — |
| VALDECIR GALVAO | — |
| NEIRI MATHIAS | — |
| VANESSA DOS SANTOS GUSMAO | — |
| CARMEM LUCIA JANUARIO DE SOUZA | — |
| MURILO DE PAULA CARVALHO | — |
| NELSON APARECIDO VICENTE | — |
| CIULEN CHAN ARANA | — |
| CAMYLLE VIEIRA | — |
| Outros CPFs autônomos | — |

#### Serviços com lançamento interno via SERVIÇO TOMADO (D **359** / C **506**)
Essas operações NÃO são lançamentos de extrato bancário — são movimentos internos registrados pela contadora:

| Plataforma | CNPJ |
|---|---|
| 99 Food (comissão) | 60.112.920/0001-23 |
| Ticket (taxa) | 47.866.934/0001-74 |

#### Deslocamento (D **364**)

| Descrição / Fornecedor | CNPJ/CPF |
|---|---|
| UBER TRIP / UBER HELP / UBER DO BRASIL | 17.895.646/0001-87 |
| DL UBERRIDES | — |
| AUTO POSTO LOGUS I | — |
| AUTO POSTO OLARIA | — |
| AUTO POSTO VIA DA U | — |
| POSTOCRESPO | — |
| 99 TECNOLOGIA (99 Taxi) | 18.033.552/0001-61 |

#### Energia elétrica (D **354**)
- COPEL-DIS / COPELDIS — CNPJ 04.368.898/0001-06 → boleto ou PIX

#### Água e esgoto (D **355**)
- SANEPAR — CNPJ 76.484.013/0001-45 → PIX ou débito convênio

#### Telefone/Internet (D **356**)
- CLIENT CO SERVI (Clientes e Companhia Serv.) — CNPJ 53.420.564/0001-40
- TIM — CNPJ 02.421.421/0001-11
- TRES PINHEIROS (provedor local) — —
- DEB. RECARGA CELULAR

#### Despesas administrativas (D **359**)
- STAHSEFSKI & MENEGOTTO (adm/consultoria) — CNPJ 24.456.254/0001-87
- SANTOS E DOMINGOS A — CNPJ 26.190.158/0001-65
- PAPELARIA STAR e similares (papelaria/escritório)

#### Alimentação de colaboradores (D **360**)
- ANILA RESTAURANTE, QUEIJOTRANCADO, PASTELARIA SANTA, THE BEST ACAI, IMPERIAL CHURROS, BAR EDMUNDO e similares
- 99 Food PIX (ref. alimentação de colaboradores) — CNPJ 60.112.920/0001-23

#### Assistência contábil (D **361**)
- PAES E BASTOS CONTABILIDADE — CNPJ 29.650.531/0001-01 → R$ 340,00/mês

#### Plano de saúde (D **366**)
- R. KFOURI - CLINICA — CNPJ 04.440.750/0001-35
- VITA SAUDE SELECT (Colombo) — R$ 400,00/mês

#### Tarifas bancárias (D **525**)
- `CESTA DE RELACIONAMENTO` (R$ 57,50)
- `INTEGR.CAPITAL SUBSCRITO` (R$ 16,00)
- `EST CESTA/TARIFA SERVICO`

#### Cartão de crédito (D **549**)
- `DEB.CTA.FATURA` — fatura do cartão corporativo

#### Marketing (D **548**)
- ByteDance / TikTok — CNPJ 27.415.911/0001-36
- ADOBE (assinatura)

#### Material de limpeza/copa (D **565**)
- EXTRALIMP COLOMBO (R$ 56,56)

#### Despesas diversas (D **493**)
- DROGA1000 (farmácia)
- AVIARIO KIFLORA
- TINTAS VERGINIA
- BANCO PAN SA (financiamento) — CNPJ 59.285.411/0001-13
- MIDWAY S.A. (financeira/financiamento) — CNPJ 09.464.032/0001-12
- PAGAR.ME PAGAMENTOS (instituição de pagamento) — CNPJ 18.727.053/0001-74
- PJBANK (maquininha) — CNPJ 18.191.228/0001-71
- TRIAD ASSOCIACAO — CNPJ 36.005.927/0001-61
- APPF CEI BELA VIS (associação)
- LIFE PARK ESTACIONAMENTO
- ASSOCIACAO METROCARD — CNPJ 10.319.963/0001-06
- FLORICULTURA NASATO
- MASTER ESPUMA / MINEIRUSBAR / MP WSAUTOCENTER
- PONTO CERTO COL, FIK BELLA COSME, BINHO AGROPECUARIA
- PARÓQUIA SENHOR DO BOM JESUS — R$ 125,00
- PEDRO KA — CNPJ 54.939.535/0001-51
- R V COMERCIO DE MEDICA, AMORIM E DIAS 2 LTDA, EFFICIENCY GYM → confirmar atividade (provisório 493)

#### Tributos (D **350** — Taxas Diversas)
- RECEITA FEDERAL (CNPJ 00.394.460/0058-87) — taxas federais e multas (ex.: multa PGDAS-D cód. 4406)
- GOVERNO PR / tributos estaduais
- DEBITO ARRECADACAO (guias diversas)

> **INSS pró-labore** (DARF cód. 1099, R$ 178,31) → **D 191 / C 8** (ver Regra Mensal — Retiradas).

#### Simples Nacional — débito automático (D **479**)
- `DEBITO CONVENIOS ID ... ADM.C` (Simples Nacional) → **D 479 / C 8**
- Reconhecimento mensal (lançamento interno): D **480** / C **479**
- ⚠️ NÃO confundir com `DEBITO CONVENIOS-CONSORCIO` (→ conta 550).

#### Consórcio (D **550**)
- `DEBITO CONVENIOS-CONSORCIO ... ADM.CONSORCIO SICREDI` (CNPJ 07.808.907/0001-20) → **D 550 / C 8**

#### Aplicação poupança (D **11**)
- `REF. A APLICACAO POUPANCA` / `APLICACAO POUPANCA-CAPTACAO` → D **11** / C **8**

---

## Fluxo de Trabalho

1. Receber extrato bancário (PDF, CSV ou OFX) e confirmar período
2. Para cada lançamento: identificar natureza → favorecido → classificar → copiar histórico exato do extrato
3. Sinalizar lançamentos não identificados para revisão da contadora
4. Verificar aplicação poupança, IOF e IRRF
5. Conferir saldo: entradas − saídas = variação do extrato
6. Gerar TXT único ordenado por data no leiaute Domínio (um |6000| por lançamento, histórico sem `|`)
7. **Apresentar tabela de retiradas da sócia** (ver regra abaixo)

---

## Regra Inviolável — Tabela de Retiradas da Sócia (ao final de cada competência)

> Sempre ao finalizar o TXT de uma competência, apresentar à contadora a tabela completa das movimentações da sócia **Maria Pinheiro dos Santos Baggio** no mês.

Formato obrigatório:

| Data | Descrição | Conta | Valor |
|---|---|---|---|
| DD/MM | ... | 188 / 563 | R$ X |
| | **Total pró-labore líquido (188)** | | R$ X |
| | **Total retirada adicional (563)** | | R$ X |
| | **Total geral pago à sócia** | | R$ X |

- Incluir TED/estorno se houver (mesmo que resultado líquido seja zero)
- Informar se houve mês sem retirada
- Entregar também planilha XLSX com o relatório formatado

---

## Pendências a Confirmar com a Contadora

- [x] Liquidação do INSS pró-labore no extrato: **D 191 / C 8** — confirmado 08/2026
- [x] `DEBITO CONVENIOS-CONSORCIO` (ADM.CONSORCIO SICREDI): **D 550 / C 8** — confirmado 08/2026
- [x] Pagamento de mercadoria: **D 506 / C 8** no banco + reconhecimento **D 470 / C 506** — confirmado 08/2026
- [ ] `DEBITO CONVENIOS` (Simples Nacional): confirmado **D 479 / C 8** ou conta específica?
- [x] `CDD CURITIBA / CRBS S.A.` (CNPJ 56.228.356/0059-58): **506** — confirmado 07/2026
- [ ] `PEDRO KA` (CNPJ 54.939.535/0001-51): confirmar atividade → 362 ou 359
- [ ] MIDWAY, PAGAR.ME, R V COMERCIO DE MEDICA, AMORIM E DIAS, EFFICIENCY GYM: confirmar atividade (provisório 493)
- [ ] Funcionária CLT JANAINE: dados completos da folha a buscar no Domínio (Módulo Folha → Relatórios → Cadastrais → Empregado)

---

## Padrão ROF — Pró-labore, Retiradas e Relatório do Sócio

> Regra validada pela contadora Rosangela em 24/09/2026 para todas as empresas do escritório.
> As regras específicas desta empresa descritas acima **continuam valendo**. Este bloco completa o que faltar e **não substitui** nenhuma conta, exceção ou classificação já confirmada. Em caso de conflito, prevalece a regra específica da empresa.

### Parâmetros desta empresa

| Sócio | CPF | Pró-labore | Conta pró-labore a pagar | Conta do sócio (retirada / aporte) |
|---|---|---|---|---|
| Maria Pinheiro dos Santos Baggio | 030.704.189-10 (obrigatório identificar o CPF) | Variável — perguntar todo mês | **188** | **563** |

> O "Reconhecimento do pró-labore" (D 275 / C 188) acima vem da folha do Domínio e **não** entra no TXT (item 9).

### Pergunta obrigatória antes de escriturar cada competência

> **Antes de lançar qualquer movimento do mês, perguntar à contadora e aguardar a resposta:**
> - Empresa **com** pró-labore → **"Qual o valor do pró-labore de <sócio> em <mês/ano>?"** (o valor pode variar de um mês para outro)
> - Empresa **sem** pró-labore → **"A empresa continua sem pró-labore em <mês/ano>?"**
>
> Aplicar a regra abaixo com o valor informado (base informada − INSS 11% = limite líquido).
>
> **Simples Nacional com Fator R:** o pró-labore é definido pela contadora conforme a estratégia do Fator R (folha de salários 12 meses ÷ receita bruta 12 meses ≥ 28% → Anexo III; abaixo → Anexo V). Ao perguntar, lembrar desse ponto e oferecer o cálculo do Fator R se a contadora enviar folha e receita dos últimos 12 meses. Nunca definir ou sugerir o valor do pró-labore por conta própria. Se a resposta mudar a situação da empresa (passou a ter ou deixou de ter pró-labore), registrar na tabela de parâmetros acima. Esta pergunta substitui qualquer tratamento antigo de "pró-labore variável" (confirmado pela contadora em 24/09/2026).

### Regra de lançamento

1. **Pró-labore líquido do mês** = valor bruto informado pela contadora para o mês − INSS 11%. **Não existe valor padrão**: o pró-labore varia por empresa e por mês. Nunca presumir salário mínimo nem repetir o valor do mês anterior. Valores fixos citados em outras partes desta skill (ex.: R$ 1.442,69) são apenas histórico ou exemplo — o limite do mês é sempre o informado pela contadora.
2. **Identificar o sócio pelo CPF** (ou nome completo) no favorecido. Sem identificação segura → sinalizar, não presumir.
3. **Acumular cronologicamente** todos os pagamentos ao sócio no mês, **somando todos os bancos**. Cada sócio tem seu próprio acumulado.
4. **Com pró-labore:**
   - Até completar o pró-labore líquido → **D conta de pró-labore a pagar / C banco**
   - O que exceder → **D conta do sócio (retirada) / C banco**
   - Pagamento único que atravessa o limite → **duas linhas `|6100|`** na mesma data (uma para cada débito), ambas creditando o banco, somando o valor total.
5. **Sem pró-labore:** toda saída ao sócio → **D conta do sócio / C banco**.
6. **Entrada do sócio na empresa** (devolução ou aporte) → **D banco / C conta do sócio** (reduz o saldo de retiradas).
7. **INSS do pró-labore** (DARF código 1099) → **D 191 (INSS a recolher) / C banco**, salvo conta diferente definida acima.
8. Pagamento ao sócio **nunca** vai para fornecedores, serviços de terceiros ou despesa.
9. **Provisão do pró-labore e do INSS NÃO entra no TXT** (D despesa / C pró-labore a pagar; D INSS / C 191). Ela é importada da **folha do Domínio**; não existe provisão manual. O TXT registra somente o **pagamento** (baixa). Esta regra prevalece sobre qualquer instrução antiga de provisão nesta skill (confirmado pela contadora em 24/09/2026).

### Relatório de Pró-labore e Retiradas — ENTREGA OBRIGATÓRIA

> Toda competência entrega **sempre dois arquivos juntos**: o TXT do Domínio **e** a planilha XLSX do sócio. O TXT nunca é entregue sozinho. Gerar sem esperar pedido — inclusive quando o mês não teve retirada (informar "sem movimentação do sócio no mês").

**Arquivo:** `<Empresa>_ProLabore_Retiradas_AAAAMM.xlsx` (se esta empresa já define nome ou formato próprio acima, usar o da empresa).

**Aba "Resumo"**
- Empresa, CNPJ, competência e bancos considerados
- Parâmetros: base do pró-labore, INSS 11% e pró-labore líquido
- Por sócio: total pago no mês · pró-labore pago (conta de pró-labore) · retiradas (conta do sócio) · devoluções/aportes · **retirada líquida do mês** · INSS recolhido no mês · pró-labore líquido não pago no mês (se o total pago ficou abaixo do limite)

**Uma aba por sócio**, uma linha por movimento, em ordem de data:
Data · Banco · Cód. conta bancária · Histórico do extrato · Tipo (Pró-labore / Retirada / Aporte-Devolução) · Valor · Acumulado no mês · Parcela pró-labore · Parcela retirada · Conta débito · Conta crédito

- Usar fórmulas: `Parcela pró-labore = MÍN(valor; limite − acumulado anterior)` e `Parcela retirada = valor − parcela pró-labore`
- Linhas divididas em duas no TXT aparecem como **uma linha** na planilha, com as duas parcelas preenchidas
- Aportes/devoluções com cor diferenciada; subtotais por tipo
- Nota de rodapé quando algum extrato estiver incompleto

**Conferência obrigatória antes de entregar:**
- Soma da planilha = soma das linhas do TXT nas contas de pró-labore e do sócio
- Nenhum pagamento ao sócio ficou fora do relatório
- Apresentar também no chat um resumo curto por sócio (pró-labore · retirada · aporte · líquido)
