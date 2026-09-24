---
name: rof-contabilidade-glcar
description: "GL CAR COMERCIO DE VEICULOS LTDA, CNPJ 48.140.089/0001-18, Lucro Presumido, comércio/intermediação de veículos, bancos: Santander (cód 8) e Itaú (cód 9)"
---

# ROF Contabilidade GL CAR — Lançamentos Contábeis e Conciliação

## Dados da Empresa

| Campo | Informação |
|---|---|
| Razão social | GL CAR COMERCIO DE VEICULOS LTDA |
| Nome fantasia | GL CAR MULTIMARCAS |
| CNPJ | 48.140.089/0001-18 |
| CNPJ sem formatação | 48140089000118 |
| CNAE principal | 74.90-1-04 — Atividades de intermediação e agenciamento de serviços e negócios |
| CNAEs secundários | 45.11-1-02 · 45.12-9-01 · 45.12-9-02 · 73.19-0-02 |
| Setor | Comércio de veículos (intermediação, consignação e revenda) |
| Regime tributário | Lucro Presumido |
| Bancos | Santander (Conta 130033975 → cód **8**) · Itaú Empresas (Conta 99426-7 → cód **9**) · Banco Rendimento (Conta 11000-9 → cód **39**) · Mercado Pago (Conta 74905604163 → cód **52**) |
| Escritório contábil | PAES E BASTOS CONTABILIDADE LTDA |
| Contadora responsável | Renata Bastos Amado — CRC PR075217/O-2 |
| Cadastrado por | Rosangela |

## Sócios

| Sócio | CPF | Conta no Domínio |
|---|---|---|
| Gustavo Dalla Stella Souza Lima | 084.148.219-52 | **531** (Ativo NÃO-Circulante — Sócios) |
| Leonardo Ribeiro de Castilho Voinarski | 108.612.869-95 | **532** (Ativo NÃO-Circulante — Sócios) |

## Funcionários CLT

| Funcionário | Cargo | Salário Base | Conta Salário (passivo) | Conta Custo |
|---|---|---|---|---|
| Lucas Henrique Gilin Borges | Auxiliar de serviços gerais | R$ 1.788,91 | **187** (Salários e Ordenados a Pagar) | **534** (Salarios e Ordenados) |

> Nome no extrato: **LUCAS HENRIQUE GULIN BORG**
> FGTS: passivo **192** · custo **539**. Dados completos da folha: Domínio → Módulo Folha → Relatórios → Cadastrais → Empregado.

## Regras de Trabalho (ACORDO COM A CONTADORA)

1. **Fidelidade total** aos dados enviados — não alterar nada sem consultar
2. **Consulta prévia** antes de qualquer alteração
3. **Base legal** sempre que sugerir algum ajuste
4. **Histórico**: copiar o texto exatamente como aparece no extrato bancário

## Leiaute do Arquivo TXT para Domínio

```
|0000|48140089000118|
|6000|X||||
|6100|DD/MM/AAAA|CONTA_DEBITO|CONTA_CREDITO|VALOR||HISTORICO||||
```

- **Pagamento (saída):** débito na conta de despesa/ativo/passivo · crédito no banco
- **Recebimento (entrada):** débito no banco · crédito na conta de receita/passivo
- **Arquivo único:** pagamentos e recebimentos compilados juntos, ordenados por data (padrão confirmado pela contadora)
- Valor com vírgula decimal: `1500,00`
- Ordenado por data

**Leiaute confirmado pelo TXT Otimizza — junho/2026 (Itaú conta 9)**

## Plano de Contas — Contas Operacionais

| Cód | Classificação | Nome | Natureza |
|---|---|---|---|
| **8** | 1.1.1.02.001 | BANCO SANTANDER - CONTA 130033975 | Ativo |
| **9** | 1.1.1.02.002 | ITAU EMPRESAS - CONTA 99426-7 | Ativo |
| **39** | 1.1.1.02.004 | BANCO RENDIMENTO - CONTA 11000-9 | Ativo |
| **52** | 1.1.1.02.005 | MERCADO PAGO - CONTA 74905604163 | Ativo |
| **11** | 1.1.1.03.001 | APLICAÇÃO CONTAMAX AUTOMATICO | Ativo |
| **504** | 1.1.2.01.001 | CLIENTES DIVERSOS (SERVIÇOS PRESTADOS) | Ativo |
| **541** | 1.1.2.01.002 | CLIENTES DIVERSOS (REVENDA DE VEICULOS) | Ativo |
| **30** | 1.1.3.08.002 | ICMS A RECUPERAR | Ativo |
| **38** | 1.1.3.08.010 | IRRF S/ APLICAÇÃO | Ativo |
| **58** | 1.1.5.01.004 | VEICULOS PARA REVENDA | Ativo (Estoque) |
| **62** | 1.1.5.01.005 | CONSIGNAÇÃO DE VEICULOS | Ativo (Estoque) |
| **531** | 1.2.2.04.001 | GUSTAVO DALLA STELLA SOUZA LIMA (084.148.219-52) | Ativo NÃO-Circ |
| **532** | 1.2.2.04.002 | LEONARDO RIBEIRO DE CASTILHO VOINARSKI (108.612.869-95) | Ativo NÃO-Circ |
| **152** | 2.1.1.01.001 | EMPRÉSTIMO BANCO SANTANDER | Passivo |
| **506** | 2.1.3.01.001 | FORNECEDOR MODELO | Passivo |
| **172** | 2.1.4.01.002 | ICMS A RECOLHER | Passivo |
| **173** | 2.1.4.01.003 | ISS A RECOLHER | Passivo |
| **575** | 2.1.4.01.004 | CSLL A RECOLHER | Passivo |
| **577** | 2.1.4.01.005 | IRPJ A RECOLHER | Passivo |
| **179** | 2.1.4.01.009 | PIS A RECOLHER | Passivo |
| **180** | 2.1.4.01.010 | COFINS A RECOLHER | Passivo |
| **479** | 2.1.4.01.015 | SIMPLES NACIONAL A RECOLHER | Passivo |
| **187** | 2.1.5.01.001 | SALÁRIOS E ORDENADOS A PAGAR | Passivo |
| **188** | 2.1.5.01.002 | PRÓ-LABORE A PAGAR | Passivo |
| **191** | 2.1.5.02.001 | INSS A RECOLHER | Passivo |
| **192** | 2.1.5.02.002 | FGTS A RECOLHER | Passivo |
| **564** | 2.1.5.02.004 | CREDITO EMPRESTIMO EMPREGADO | Passivo |
| **510** | 2.1.6.02.001 | HONORÁRIOS CONTÁBEIS | Passivo |
| **530** | 2.1.6.02.002 | REPASSE VENDAS | Passivo |
| **548** | 2.3.5.01.007 | DISTRIBUIÇÃO DE LUCROS | PL |
| **534** | 3.1.3.01.001 | SALARIOS E ORDENADOS | Custo |
| **535** | 3.1.3.01.002 | PRÓ-LABORE | Custo |
| **538** | 3.1.3.01.005 | INSS | Custo |
| **539** | 3.1.3.01.006 | FGTS | Custo |
| **339** | 3.2.2.01.009 | ASSISTÊNCIA MÉDICA E SOCIAL | Despesa |
| **350** | 3.2.2.03.005 | TAXAS DIVERSAS | Despesa |
| **355** | 3.2.2.04.002 | ÁGUA E ESGOTO | Despesa |
| **356** | 3.2.2.04.003 | TELEFONE/INTERNET | Despesa |
| **359** | 3.2.2.04.006 | DESPESAS ADMINISTRATIVAS | Despesa |
| **361** | 3.2.2.04.008 | ASSISTÊNCIA CONTÁBIL | Despesa |
| **362** | 3.2.2.04.009 | SERVIÇOS PRESTADOS POR TERCEIROS | Despesa |
| **364** | 3.2.2.04.011 | SISTEMA | Despesa |
| **365** | 3.2.2.04.012 | DESPESAS LEGAIS E JUDICIAIS COM VEICULOS | Despesa |
| **366** | 3.2.2.04.013 | COMBUSTIVEL | Despesa |
| **521** | 3.2.2.04.022 | DESPESAS COM ALIMENTAÇÃO | Despesa |
| **525** | 3.2.2.04.015 | DESPESAS DIVERSAS | Despesa |
| **526** | 3.2.2.05.009 | TARIFAS BANCARIAS | Despesa Financeira |
| **527** | 3.2.2.04.016 | DESPESAS COM VEICULOS | Despesa |
| **533** | 3.2.2.05.010 | IOF | Despesa Financeira |
| **551** | 3.2.2.04.017 | DESPESA COM MARKETING | Despesa |
| **553** | 3.2.2.04.020 | DESPESA COM CARTAO DE CREDITO | Despesa |
| **561** | 3.2.2.04.023 | DESPESA COM DESLOCAMENTO | Despesa |
| **549** | 4.1.1.01.001 | VEICULOS PARA REVENDA | Receita |
| **411** | 4.1.1.02.001 | SERVIÇOS PRESTADOS | Receita |
| **432** | 4.1.3.01.001 | JUROS DE APLICAÇÕES | Receita Financeira |
| **569** | 6.1.1.00.1 | Mercadorias Recebidas em Consignação | Compensação Ativa |
| **573** | 6.2.1.00.1 | Consignantes - Mercadorias Recebidas | Compensação Passiva |

## Regra de Classificação das Contrapartes

### Para cada lançamento do extrato, siga esta ordem:

1. Identificar natureza (entrada / saída)
2. Identificar favorecido (nome, CNPJ/CPF)
3. Se tiver CNPJ → pesquisar na Receita Federal → verificar atividade → classificar conforme plano de contas
4. Se Pessoa Física (exceto sócios) → conta **362** (Serviços por Terceiros) — confirmar com a contadora se valor relevante
5. Se sócio (Gustavo ou Leonardo) → aplicar Regra de Retiradas
6. **Transferência entre contas da própria empresa** (CNPJ 48140089000118 como remetente ou "GL CAR MULTIMARCAS") → D: banco destino | C: banco origem
7. Histórico: copiar exatamente como aparece no extrato

### Conta 530 — REPASSE VENDAS (conta-chave desta empresa)

> Esta empresa é **intermediária de veículos**. A conta **530** é usada tanto para recebimentos (de compradores e financiadoras) quanto para pagamentos (a proprietários e consignantes de veículos). É o maior volume de movimentação do extrato.

- **Recebimento de comprador / financiadora → banco:** D: banco | C: **530**
- **Repasse ao dono do veículo → saída do banco:** D: **530** | C: banco
- Confirmar com a contadora quando o nome for desconhecido e o valor for relevante

**Principais financiadoras identificadas no Razão (crédito → 530):**
- CNPJ 59588111000103 — aparece com frequência, valores altos (Itaú Crédito / financiadora)
- "FIN VEIC ITC AFR3J51" — financiamento de veículo via Itaú (L = liberação, R = parcela)

## Regra Inviolável — Conferência de Saldo

> Nunca entregar o TXT sem que os saldos do extrato estejam fechando.

Aplicar para cada banco individualmente:

1. Saldo anterior (abertura) informado no extrato
2. Saldo final (encerramento) informado no extrato
3. Diferença esperada = Saldo final − Saldo anterior
4. Somar todas as entradas lançadas no TXT
5. Somar todas as saídas lançadas no TXT
6. Diferença apurada = Total entradas − Total saídas

Se Diferença apurada ≠ Diferença esperada → **NÃO entregar o TXT.**

## Regra Inviolável — Aplicações Financeiras e Rendimentos

> Nunca omitir movimentações de aplicação financeira do TXT.

- **APLICAÇÃO CONTAMAX AUTOMATICO** (conta **11**) — resgatada integralmente em 01/02/2026 (D: banco | C: **11**). Saldo atual: **R$ 0**. Se aparecer nova aplicação, confirmar conta com a contadora antes de lançar.
- **Conta 432** é utilizada para **todos os rendimentos de aplicação financeira**, independentemente do banco. Regra universal:
  - D: banco correspondente | C: **432** (Juros de Aplicações)
- Itaú: "APLIC AUT MAIS" / "REND PAGO APLIC AUT MAIS" → D: **9** | C: **432**
- Santander: rendimentos Contamax (apareciam até fev/2026) → D: **8** | C: **432**

## Regra Inviolável — IOF e IRRF

> Nunca omitir IOF nem IRRF do TXT.

- **IOF** → conta **533** — lançar separadamente, mesmo valor mínimo
- **IRRF s/ Aplicação** → conta **38** (Ativo) — lançar: D: **38** | C: banco
- **Tarifas bancárias** → conta **526** — lançar cada evento individualmente
- **Tarifa mensal pacote** (ex.: "TAR PLANO ADAPT 1", "TARIFA MENSALIDADE PACOTE") → **526**
- **Tarifa avulsa envio PIX** → **526**

## Regra Mensal — Retiradas dos Sócios

> ANTES DE LANÇAR qualquer pagamento a sócio: confirmar com a contadora o total pago no mês.

**Pró-labore base: salário mínimo nacional vigente — R$ 1.621,00 (2026). Atualizar sempre que o salário mínimo for reajustado.**

| Cálculo | Fórmula | Valor (2026) |
|---|---|---|
| Base | Salário mínimo nacional vigente | R$ 1.621,00 |
| INSS (11%) | Base × 11% | R$ 178,31 |
| Pró-labore líquido | Base − INSS | R$ 1.442,69 |

**Lançamento na competência (folha):**

> ⚠️ **NÃO entra no TXT** — importado da folha do Domínio (confirmado pela contadora em 24/09/2026). Quadro mantido só como referência.

| Débito | Crédito | Descrição |
|---|---|---|
| **535** (Pró-labore — custo) | **188** (Pró-labore a Pagar) | Valor bruto do pró-labore |
| **538** (INSS — custo) | **191** (INSS a Recolher) | INSS s/ pró-labore (11%) |

**Pagamento ao sócio (extrato bancário):**

| Valor acumulado no mês | Débito | Crédito |
|---|---|---|
| Até R$ 1.442,69 (pró-labore líquido) | **188** (Pró-labore a Pagar) | banco |
| Excedente acima de R$ 1.442,69 | **531** ou **532** (conta ativo do sócio) | banco |

> Gustavo → **531** · Leonardo → **532**

## Regra — Devolução / Aporte do Sócio

Quando o sócio deposita valores **na empresa** (entrada no extrato bancário):

| Débito | Crédito |
|---|---|
| banco | **531** ou **532** (conta ativo do sócio — reduz saldo devedor) |

## Particularidades dos Bancos

### Santander (conta **8**) — banco principal das operações históricas
- Tarifas → **526**
- IOF → **533**
- Empréstimo ativo → **152** (parcelas debitadas como D: **152** | C: **8**)
- PIX enviado "GL CAR MULTIMARCAS" = transferência interna para outro banco da empresa
- "ITAU-PDF- 6868-0099426-7" = transferência Santander → Itaú (D: **9** | C: **8**)

### Itaú Empresas (conta **9**)
- Tarifas → **526** (incluindo tarifa avulsa de PIX)
- IOF → **533**
- Aplicação Automática Mais: rendimentos → **432**
- PIX recebido com CNPJ 48140089000118 = transferência interna da empresa
- TXT gerado em arquivos separados: PAGAR e RECEBER
- "FIN VEIC ITC" = liberação ou parcela de financiamento de veículo → **530**

### Banco Rendimento (conta **39**) e Mercado Pago (conta **52**)
- Saldo zero no balancete de junho/2026; **Mercado Pago com pouca ou nenhuma movimentação**
- Movimentações aparecem como transferências internas no Santander/Itaú
- Ao receber extrato: tarifas → **526** · rendimentos → **432** · transferências entre bancos próprios → banco correspondente

## Classificações Recorrentes Confirmadas

| Fornecedor / Descrição no extrato | Conta | Observação |
|---|---|---|
| PAES E BASTOS CONTABILIDA | **510** | Honorários contábeis |
| SEFA PR GR / PGTO TRIBUTO ESTADUAL | **365** | Taxas veiculares estaduais (ICMS IPVA) |
| DETRAN PR / DEPARTAMENTO DE TRANSITO | **365** | Transferência, emplacamento |
| SUSSAI DESPACHANTE | **365** | Despachante — documentação de veículos |
| GOVERNO DO PARANA SECRETA | **365** | Taxas estaduais veiculares |
| DIRETORIA GERAL DE FINANC | **365** | DER — despesas legais/judiciais com veículos |
| DEPARTAMENTO DE ESTRADAS | **365** | DER — despesas legais/judiciais com veículos |
| WEBMOTORS S.A. | **527** | Portal de anúncios — despesas com veículos |
| INTERLAGOS COBRADORA LTDA | **527** | Serviços relacionados a veículos |
| BLIND NORTE VIDROS | **527** | Vidraçaria — veículos |
| NAVI TINTAS AUTOMOT | **527** | Tintas — veículos |
| AUTOPECAS ALVORADA | **527** | Autopeças |
| DPASCHOAL | **527** | Autopeças/pneus |
| MEGACAR COMERCIO DE PLACA | **527** | Placas — veículos |
| AKITA COMERCIO DE PECAS | **527** | Autopeças |
| UBER DO BRASIL TECNOLOGIA | **561** | Deslocamento |
| LIGGA TELECOM / LIGGA | **356** | Telefone/Internet |
| SANEPAR PARANA | **355** | Água e esgoto |
| CEF MATRIZ | **192** | FGTS |
| SIMPLES NACIONAL / DARF Simples | **479** | Simples Nacional a Recolher |
| INSS (DARF) / PAGAMENTO DARF TRIBUTOS FEDERAIS | **191** | INSS a Recolher |
| LUCAS HENRIQUE GULIN BORG | **187** | Salário CLT |
| ABA CONSULTORIA EM SAUDE | **339** | Assistência médica |
| ICARROS LTDA | **525** | Anúncios de veículos (despesas diversas) |
| SOCARRAO WEB S LTDA EPP | **525** | Sistema — confirmar com contadora |
| BANCO ITAUCARD S/A | **525** | Fatura cartão de crédito |
| BANCO C6 S.A. / BANCO C6 | **525** | Fatura cartão de crédito |
| BANCO PAN SA | **525** | Boleto/contrato — confirmar com contadora |
| BANCO VOTORANTIM S/A | **525** | Boleto/contrato — confirmar com contadora |
| BOX ENERGY COMERCIO DE BA | **525** | Confirmar com contadora |
| EBAZAR COM BR | **525** | E-commerce — confirmar |
| PIX MARKETPLACE / AVISO DE VENDA | **359** | Marketplace/aviso de venda (despesas adm.) |
| BOM NEGOCIO A INTERNET LT | **525** | Portal de anúncios — confirmar |
| JARAGUA SUL INDL BRINDES | **525** | Brindes/marketing — confirmar se vai para 551 |
| VELOZ GAS LTDA | **366** | Combustível |
| RENDIMENTO LIQUIDO CONTAMAX / APLIC AUT MAIS | **432** | Rendimentos de aplicação financeira |
| Vilmar Voinarski Consult / Vilmar Ribeiro de Castilho | **506** | Fornecedor |
| GONGRA COMERCIO DE VEICUL | **530** | Repasse de veículos |
| LAYSSEN PROMOCOES | **530** | Repasse de veículos |
| METROSUL | **530** | Repasse de veículos |
| PATRICIA ARTHUR | **530** | Repasse de veículos — confirmar PF |
| ZILA MARIA WALENGA SANTOS | **530** | Repasse de veículos — confirmar PF |
| LUCAS OLEINIK LANZONI | **530** | Repasse de veículos |
| EDINALDO DE OLIVEIRA / EDILSON | **530** | Repasse de veículos |
| SANTANDER SOC. (boleto) | **530** | Repasse via boleto Santander |
| PATRICK DE JESUS COSTA PI | **365** | Despachante — despesas legais/judiciais com veículos |
| MAYK VINICIO DAMIN | **362** | Serviços terceirizados |
| EVERSON RODRIGO MARCONDES | **362** | Serviços terceirizados |
| THAYNARA FRANCIS DOS SANT | **362** | Serviços terceirizados |
| SILVIO LUIZ DOMINGOS | **362** | Serviços terceirizados |
| DARLAM CRISTIANO WALENGA | **362** | Serviços terceirizados |
| VAGNER CRISTIANO DE GOUVE | **362** | Serviços terceirizados |
| JORGE LUCAS REIS MARTINS | **362** | Serviços terceirizados |
| MARCHETTI E MARCHETTI TEC | **525** | Sistema — avaliar se deve ir para 364 |
| ODA IMOVEIS VENDA E ADMIN | **359** | Despesas administrativas |
| COPEL-DIS | **525** | Energia elétrica — sem conta específica, usar 525 |

## Fluxo de Trabalho

1. Receber extrato bancário (PDF, CSV ou OFX) e informar o banco correspondente
2. Para cada lançamento: identificar natureza → favorecido → classificar → copiar histórico
3. Atenção especial: verificar se CNPJ 48140089000118 = transferência interna (não classificar como receita)
4. Verificar rendimentos de aplicação, IOF e tarifas
5. Conferir saldo do extrato vs. somatório do TXT
6. Gerar TXT **único** (pagamentos e recebimentos juntos, ordenados por data — padrão confirmado para todos os bancos)
7. Sinalizar pendências para revisão antes de entregar

## Pendências a Confirmar com a Contadora

- **Conta "5"** no TXT RECEBER de junho/2026 para "PIX RECEBIDO GL CAR" — aguardar: se aparecer no extrato de julho/2026 ou posterior, identificar com a contadora antes de lançar
- **IRRF s/ Aplicação** — conta **38** (Ativo) confirmada pela contadora. Lançar quando aparecer no extrato: D: **38** | C: banco

---

## Padrão ROF — Pró-labore, Retiradas e Relatório do Sócio

> Regra validada pela contadora Rosangela em 24/09/2026 para todas as empresas do escritório.
> As regras específicas desta empresa descritas acima **continuam valendo**. Este bloco completa o que faltar e **não substitui** nenhuma conta, exceção ou classificação já confirmada. Em caso de conflito, prevalece a regra específica da empresa.

### Parâmetros desta empresa

| Sócio | CPF | Pró-labore | Conta pró-labore a pagar | Conta do sócio (retirada / aporte) |
|---|---|---|---|---|
| Gustavo | ver acima | Variável — perguntar todo mês | **188** | **531** |
| Leonardo | ver acima | Variável — perguntar todo mês | **188** | **532** |

> O quadro "Lançamento na competência (folha)" acima é apenas referência: essa provisão vem da folha do Domínio e **não** entra no TXT (item 9).

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
