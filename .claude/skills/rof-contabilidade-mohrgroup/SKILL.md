---
name: rof-contabilidade-mohrgroup
description: "Corrige salário mínimo 2026 para R$1.621,00 e adiciona regra de sempre gerar planilha de retiradas junto ao TXT"
---

# ROF Contabilidade MOHR GROUP — Lançamentos Contábeis e Conciliação

## Dados da Empresa

| Campo | Informação |
|---|---|
| Razão social | MOHR GROUP LTDA |
| CNPJ | 17.593.725/0001-33 |
| CNPJ sem formatação | 17593725000133 |
| CNAE principal | 4781-4/00 — Comércio varejista de artigos do vestuário e acessórios |
| CNAEs secundários | 4713-0/02 — Lojas de variedades, exceto lojas de departamentos ou magazines |
| Setor | Comércio varejista (vestuário) |
| Regime tributário | Simples Nacional |
| Banco(s) | Sicredi → **8** · Sicoob → **9** · Itaú → **6** |
| Cadastrado por | Rosangela |

---

## Sócios

| Sócio | CPF | Conta no Domínio |
|---|---|---|
| Emerson Mohr | 035.870.159-70 | **539** (1.2.2.04.001 — Ativo sócio) |
| Sueli Ribeiro Mohr | 037.687.209-85 | **548** (1.2.2.04.002 — Ativo sócio) |

---

## Regras de Trabalho (ACORDO COM A CONTADORA)

1. **Fidelidade total** aos dados enviados — não alterar nada sem consultar a contadora
2. **Consulta prévia** antes de qualquer ajuste de conta ou classificação nova
3. **Base legal** sempre que sugerir alguma alteração
4. **Histórico**: copiar o texto **exatamente** como aparece no extrato bancário — sem resumir, traduzir ou alterar

---

## Leiaute do Arquivo TXT para Domínio

```
|0000|17593725000133|
|6000|X||||
|6100|DD/MM/AAAA|CONTA_DEBITO|CONTA_CREDITO|VALOR||HISTORICO||||
```

- **Recebimento (entrada):** débito no banco → crédito na conta de receita/cliente
  - Exemplo: `|6100|01/06/2026|6|504|412,80||REF. A RECEBIMENTO REDE MAST CD0049487205||||`
- **Pagamento (saída):** débito na conta de despesa/passivo → crédito no banco
  - Exemplo: `|6100|01/06/2026|373|9|2,12||REF. A DEB.IOF DOC. IOF/1-6||||`
- **Valor com vírgula decimal** (ex.: 1.219,64 → `1219,64`)
- **Arquivo único** com pagamentos e recebimentos ordenados por data — NÃO gerar dois arquivos separados
- Entre cada lançamento: `|6000|X||||`

---

## Plano de Contas — Contas Operacionais

| Cód | Classificação | Nome | Natureza |
|---|---|---|---|
| **6** | 1.1.1.02.003 | BANCO ITAÚ — CONTA 52610-4 | Ativo |
| **8** | 1.1.1.02.001 | BANCO SICREDI — CONTA 47923-9 | Ativo |
| **9** | 1.1.1.02.002 | BANCO SICOOB — CONTA 67025-1 | Ativo |
| **11** | 1.1.1.03.001 | APLICAÇÃO AUTO MAIS ITAÚ | Ativo |
| **71** | 1.1.4.01.002 | APLICAÇÃO SICREDI | Ativo |
| **152** | 2.1.1.01.001 | EMPRÉSTIMO J A R DE ALMEIDA LTDA | Passivo |
| **166** | 2.1.1.01.002 | EMPRÉSTIMO E FINANCIAMENTO A CURTO PRAZO | Passivo |
| **167** | 1.1.3.10.001 | EMPRÉSTIMO RIBEIRO FAST FASHION LTDA | Ativo |
| **187** | 2.1.5.01.001 | SALÁRIOS E ORDENADOS A PAGAR | Passivo |
| **188** | 2.1.5.01.002 | PRÓ-LABORE A PAGAR | Passivo |
| **191** | 2.1.5.02.001 | INSS A RECOLHER | Passivo |
| **192** | 2.1.5.02.002 | FGTS A RECOLHER | Passivo |
| **355** | 3.2.2.04.002 | ÁGUA E ESGOTO | Despesa |
| **356** | 3.2.2.04.003 | TELEFONE | Despesa |
| **357** | 3.2.2.04.004 | PLANOS MÉDICOS E ODONTOLÓGICOS | Despesa |
| **358** | 3.2.2.04.005 | SEGUROS | Despesa |
| **359** | 3.2.2.04.006 | DESPESAS ADMINISTRATIVAS | Despesa |
| **361** | 3.2.2.04.008 | ASSISTÊNCIA CONTÁBIL | Despesa |
| **362** | 3.2.2.04.009 | SERVIÇOS PRESTADOS POR TERCEIROS | Despesa |
| **364** | 3.2.2.04.011 | DESPESAS COM CARTÃO DE CRÉDITO | Despesa |
| **365** | 3.2.2.04.012 | DESPESAS LEGAIS E JUDICIAIS | Despesa |
| **369** | 3.2.2.05.002 | DESPESAS BANCÁRIAS | Despesa |
| **370** | 3.2.2.05.003 | TARIFAS BANCÁRIAS | Despesa |
| **372** | 3.2.2.05.005 | JUROS DE MORA | Despesa |
| **373** | 3.2.2.05.006 | IOF | Despesa |
| **375** | 3.2.2.05.008 | IRRF SOBRE APLICAÇÃO | Despesa |
| **432** | 4.1.3.01.001 | JUROS DE APLICAÇÕES (Rendimentos) | Receita |
| **479** | 2.1.4.01.015 | SIMPLES NACIONAL A RECOLHER | Passivo |
| **493** | 3.2.2.04.014 | DESPESAS DIVERSAS | Despesa |
| **504** | 1.1.2.01.001 | CLIENTES DIVERSOS | Ativo |
| **506** | 2.1.3.01.001 | FORNECEDOR MODELO | Passivo |
| **510** | 2.1.6.02.001 | HONORÁRIOS CONTÁBEIS | Passivo |
| **512** | 2.1.4.01.025 | ICMS ANTECIPADO A RECOLHER | Passivo |
| **521** | 3.2.2.04.021 | DESPESAS COM ALIMENTAÇÃO | Despesa |
| **539** | 1.2.2.04.001 | EMERSON MOHR (035.870.159-70) | Ativo sócio |
| **540** | 3.2.2.04.017 | DÍZIMOS E OFERTAS | Despesa |
| **541** | 3.2.2.04.018 | DESPESAS COM DESLOCAMENTO | Despesa |
| **548** | 1.2.2.04.002 | SUELI RIBEIRO MOHR (037.687.209-85) | Ativo sócio |
| **555** | — | DESPESA COM CARTÃO DE CRÉDITO *(conta nova — criada em 08/2026)* | Despesa |

---

## Regra de Classificação das Contrapartes — LEIA ANTES DE CLASSIFICAR

Para cada lançamento do extrato, siga esta ordem:

1. Identifique o favorecido (nome, CNPJ/CPF)
2. Se tiver **CNPJ** → pesquisar no portal da Receita Federal para verificar atividade → classificar conforme plano de contas
   - Receita Federal: https://www.receita.fazenda.gov.br/PessoaJuridica/CNPJ/cnpjreva/Cnpjreva_Solicitacao2.asp
3. Se for **Pessoa Física** (exceto sócios) → conta **362** (Serviços Prestados por Terceiros)
4. Se for **sócio** → aplicar **Regra Inviolável de Retiradas** (ver seção abaixo)
5. Se for débito de **fatura de cartão de crédito** → conta **555**
6. Se for **Receita Federal** → verificar natureza: Simples Nacional → **479** / INSS → **191**
7. **Histórico**: copiar exatamente do extrato bancário

---

## Regra Inviolável — Conferência de Saldo Antes da Entrega

> **Nunca entregar o TXT sem que os saldos do extrato estejam fechando.**

Antes de gerar o arquivo final, conferir obrigatoriamente:

1. Saldo anterior (abertura) informado no extrato
2. Saldo final (encerramento) informado no extrato
3. Diferença esperada = Saldo final − Saldo anterior
4. Somar todas as entradas lançadas no TXT
5. Somar todas as saídas lançadas no TXT
6. Diferença apurada = Total entradas − Total saídas

**Se Diferença apurada ≠ Diferença esperada → NÃO entregar o TXT. Identificar e corrigir a divergência antes de qualquer entrega.**

---

## Regra Inviolável — Planilha de Retiradas dos Sócios

> **Sempre gerar e entregar a planilha de retiradas junto ao TXT, a cada competência.**

A planilha deve conter obrigatoriamente:

1. **Parâmetros do mês**: Salário Mínimo vigente, INSS (11%), pró-labore líquido
2. **Detalhamento por sócio**: data, histórico, débito, crédito, valor, tipo (pró-labore / retirada)
3. **Totais por sócio**: pró-labore reconhecido (188), retiradas (539/548), INSS a recolher
4. **Resumo geral**: ambos os sócios lado a lado, total de INSS a recolher no mês
5. **Observações**: base legal do SM, alíquota INSS, regra de ordem de cobertura

Formato: arquivo `.xlsx` com formatação clara, nomeado `retiradas_socios_AAAAMM_mohrgroup.xlsx`.

---

## Regra Inviolável — Aplicações Financeiras e Rendimentos

> **Nunca omitir rendimentos de aplicação financeira do TXT.**

### Aplicação Auto Mais Itaú (conta 11)

A empresa recebe pagamentos via Rede (Visa/Mastercard/Amex) na conta Itaú (6), e o sistema aplica e resgata automaticamente na Auto Mais no mesmo dia.

| Movimento | Entra no TXT? | Lançamento |
|---|---|---|
| Recebimento Rede (Visa/Mast/Amex) | ✅ SIM | D **6** / C **504** |
| APL APLIC AUTO MAIS (aplicação automática) | ❌ NÃO | — |
| RESGATE APL APLIC AUTO MAIS | ❌ NÃO | — |
| **RENDIMENTOS REND PAGO APLIC AUT MAIS** | ✅ SIM | D **6** / C **432** |

> Os movimentos de aplicação e resgate da Auto Mais cancelam-se entre si e **não entram no TXT**.
> Os rendimentos **sempre entram**, mesmo que o valor seja pequeno (R$ 0,03, R$ 0,11 etc.).

### Aplicação Sicredi (conta 71)

Aporte fixo mensal de R$ 500,00 com aviso prévio.

| Movimento | Lançamento |
|---|---|
| APLIC.FINANC.AVISO PREVIO (saída do Sicredi) | D **71** / C **8** |
| CRED.DIST.SOBRAS (rendimentos/sobras — Sicoob) | D **9** / C **432** |

### IRRF sobre Aplicações (conta 375)

Conta existe no plano (375). Não apareceu nos meses analisados (valores de rendimento muito pequenos). **Monitorar a cada competência** — se aparecer no extrato, lançar: D **375** / C banco.

---

## Regra Inviolável — IOF e IRRF

> **Nunca omitir IOF nem IRRF do TXT.**

### IOF
- Conta: **373**
- Lançar separadamente — não embutir no valor principal
- Padrão Sicoob: `REF. A DEB.IOF DOC. IOF/1-X` → D **373** / C **9**
- Padrão Itaú: `REF. A IOF` → D **373** / C **6**

### IRRF sobre Aplicação
- Conta: **375**
- Nunca omitir por valor pequeno — se constar no extrato, lança: D **375** / C banco

---

## Regra Inviolável — Retiradas dos Sócios

> ANTES DE LANÇAR qualquer pagamento a sócio: confirmar o total pago no mês e se houve pagamentos parciais.

**Pró-labore mensal = 1 salário mínimo nacional vigente (para cada sócio)**

**Salário Mínimo Nacional 2026: R$ 1.621,00** (Decreto nº 12.302/2025, vigente desde 01/01/2026)

| Cálculo | Fórmula | Valor 2026 |
|---|---|---|
| Base | Salário mínimo nacional vigente | R$ 1.621,00 |
| INSS (11%) | Base × 11% | R$ 178,31 |
| **Pró-labore líquido** | Base − INSS | **R$ 1.442,69** |

### Lançamentos — acumular cronologicamente no mês:

| Valor acumulado no mês | Débito | Crédito |
|---|---|---|
| Até o pró-labore líquido (R$ 1.442,69) | **188** (Pró-labore a Pagar) | Banco |
| Excedente ao pró-labore líquido | **539** (Emerson) ou **548** (Sueli) | Banco |

> Esta regra é **inviolável**: todo pagamento a sócio deve primeiro cobrir o pró-labore antes de ser classificado como retirada.
> O controle é **individual por sócio**.

### INSS do pró-labore
Quando pago à Receita Federal (CNPJ 00.394.460/0058-87):

| Débito | Crédito |
|---|---|
| **191** (INSS a Recolher) | Banco |

---

## Regra — Devolução / Aporte do Sócio (sócio coloca dinheiro na empresa)

Quando o sócio transfere ou deposita valores **para a empresa** (entrada no extrato bancário):

| Débito | Crédito |
|---|---|
| Banco (6, 8 ou 9) | **539** (Emerson) ou **548** (Sueli) |

O crédito na conta ativo do sócio **reduz o saldo devedor** — é a devolução do que foi retirado anteriormente. O controle é **individual por sócio**.

---

## Regra — Transferências entre Contas Próprias da Empresa

A empresa possui três contas bancárias (Sicredi, Sicoob, Itaú) e realiza transferências PIX entre elas.

> **SEMPRE verificar**: se saiu de uma conta, a entrada deve aparecer na outra conta bancária da empresa.
> O PIX pode aparecer com o nome "MISS MOHR BOUTIQUE" (nome fantasia registrado no Sicredi) — é a mesma empresa.
> Recebimentos de clientes podem transitar por conta **blink** (banco transitório) antes de entrar nas contas — classificar como D banco / C504, não como transferência entre contas próprias.

| Movimento | Lançamento |
|---|---|
| Transferência entre contas próprias | D banco destino / C banco origem |

**Nunca usar conta de caixa ou conta de passagem intermediária.**

Exemplos confirmados pelo razão:
- Sicoob → Sicredi: D **8** / C **9**
- Sicredi → Sicoob: D **9** / C **8**

---

## Particularidades dos Bancos

### Itaú (conta 6) — Rede/Redecard
- Recebimentos de cartão via Rede (Visa, Mastercard, Amex): D **6** / C **504**
- Rendimentos Auto Mais: D **6** / C **432**
- IOF: D **373** / C **6**
- Tarifa (TAR PLANO ADAPT, etc.): D **370** / C **6**
- Seguro Prestamista / PRUDENTIAL: D **358** / C **6**

### Sicredi (conta 8)
- Recebimentos de clientes (PIX, boleto cobrança): D **8** / C **504**
- Aplicação Sicredi mensal (APLIC.FINANC.AVISO PREVIO): D **71** / C **8**
- Tarifas (TAR INCLUSAO/EXCLUSAO NEGATIVACAO, TAR SERV.COBR., etc.): D **370** / C **8**
- Custas de protesto: D **365** / C **8**
- Seguros: D **358** / C **8**
- Dízimos/ofertas (COMUNHA CRISTA ABBA): D **540** / C **8**
- Deslocamentos (UBER, AUTOPISTA/pedágio, GUSTAVO KLEMTZ): D **541** / C **8**
- Parcelas de empréstimos (COOPERATIVA CRE, etc.): D **166** / C **8**
- Honorários contábeis: D **510** / C **8**
- Alimentação: D **521** / C **8**

### Sicoob (conta 9)
- IOF (DEB.IOF): D **373** / C **9**
- Pacote de serviços (DEB PACOTE SERVICOS): D **369** / C **9**
- Empréstimo (DEB.EMPRESTIMO DOC. 01290747): D **166** / C **9**
- **Fatura Mastercard empresarial** (DEB.CONV.DEM.EMPRES DOC. MASTERCARD): D **555** / C **9**
- Juros conta garantida (JUROS CTA GARANTIDA): D **372** / C **9**
- Sobras / rendimentos cooperativa (CRED.DIST.SOBRAS): D **9** / C **432**
- Cheque compensado (CHQ CMP INTEGRADA): D **506** / C **9**

---

## Classificações Recorrentes Confirmadas pelo Razão (Abr–Jul 2026)

| Favorecido / Descrição no extrato | Conta |
|---|---|
| REDECARD / REDE MAST / REDE VISA / REDE AMEX CD0049487205 | **504** |
| RENDIMENTOS REND PAGO APLIC AUT MAIS | **432** |
| APL APLIC AUTO MAIS / RESGATE APL APLIC AUTO MAIS | *(não entra no TXT)* |
| APLIC.FINANC.AVISO PREVIO | D **71** / C **8** |
| CRED.DIST.SOBRAS (Sicoob) | D **9** / C **432** |
| RECEITA FEDERAL (CNPJ 00.394.460/0058-87) — Simples Nacional | **479** |
| RECEITA FEDERAL (CNPJ 00.394.460/0058-87) — INSS | **191** |
| DEB.IOF / IOF | **373** |
| TAR (tarifas diversas) | **370** |
| DEB PACOTE SERVICOS / DESPESAS BANCÁRIAS | **369** |
| JUROS CTA GARANTIDA | **372** |
| DEB.EMPRESTIMO DOC. 01290747 (Sicoob) | **166** |
| DEB.CONV.DEM.EMPRES DOC. MASTERCARD (Sicoob) | **555** |
| CHQ CMP INTEGRADA | **506** |
| PRUDENTIAL SEG / SEGURO PRESTAMISTA | **358** |
| DA VIVO / telefone | **356** |
| BUSINESS (cartão) | **364** |
| UBER DO BRASIL | **541** |
| AUTOPISTA PLANALT / pedágio | **541** |
| COMUNHA CRISTA ABBA | **540** |
| PLUXEE FROTA | **541** |
| PIX para EMERSON MOHR (CPF 035.870.159-70) | Ver **Regra Inviolável de Retiradas** |
| PIX para SUELI RIBEIRO MOHR (CPF 037.687.209-85) | Ver **Regra Inviolável de Retiradas** |
| PIX para/de mesmo CNPJ (17.593.725/0001-33 / MISS MOHR BOUTIQUE) | Transferência entre contas próprias |
| SICREDI ANTEC MASTER | **504** (adiantamento de recebíveis) |
| CRED COBRANCA DESCONTADA | **369** (tarifa) |
| MARTINSCARVALHO CO | **506** |
| DELIZ INDUSTRIA | **506** |
| DS FATIMA COMERCIO | **506** |
| ALCA SERV DE CO | **359** |
| SUL SYSTEM I CA | **359** |
| JACIRA MENDES PEREIRA (CPF PF) | **362** |
| GRACIELI DO MONTE (CPF PF) | **362** |
| ZELIA ANTONIO CELESTIN (CPF PF) | **362** |
| MARCIA BRUSKY (CPF PF) | **362** |
| PAULO CESAR SANTOS DE (CPF PF) | **362** |
| VENISSE BISPO DUTRA CNPJ 42.329.751/0001-04 | **493** |
| GABRIELE FERREIRA SILVA | **187** |
| LIQUIDACAO DE PARCELA (empréstimo Itaú/Sicoob) | **166** |

---

## Fluxo de Trabalho

1. Receber extrato bancário (PDF, CSV ou OFX) e identificar o banco (Sicredi/Sicoob/Itaú)
2. Para cada lançamento:
   a. Identificar natureza (entrada/saída)
   b. Identificar favorecido e aplicar regras de classificação na ordem da seção "Regra de Classificação"
   c. Verificar se é transferência entre contas próprias (conferir a contraparte na outra conta)
   d. Registrar histórico exatamente como aparece no extrato
3. Aplicar regras de sócios: confirmar total mensal antes de lançar qualquer retirada
4. Verificar aplicações financeiras: rendimentos **não podem** ficar de fora
5. Verificar IOF e IRRF: lançar separadamente, nunca embutir
6. Conferir saldo: entradas − saídas = variação do extrato
7. Gerar TXT único ordenado por data
8. **Gerar planilha de retiradas dos sócios** (`.xlsx`) — obrigatória a cada competência
9. **Nunca entregar sem fechar o saldo**

---

## Parâmetros Adicionais

- O razão dos meses anteriores serve como referência histórica de classificação
- Qualquer dúvida ou divergência: pontuar para a contadora **antes** de prosseguir
- Cada empresa deve ser trabalhada em conversa separada
- Conta 555 (Despesa com Cartão de Crédito) criada em agosto/2026 — verificar se foi cadastrada no Domínio antes de usar
- **Para o Sicoob**: sempre preferir OFX ou CSV ao PDF — a conversão de PDF pode gerar valores incorretos

---

## Pendências a Confirmar com a Contadora

- [ ] Conta bancária não identificada (inativa) — desconsiderar por ora, confirmar se será ativada
- [ ] IRRF sobre aplicação (conta 375) — nunca apareceu no razão; monitorar a cada competência
- [ ] Confirmar se conta 555 já foi parametrizada no Domínio antes da primeira utilização

---

## Padrão ROF — Pró-labore, Retiradas e Relatório do Sócio

> Regra validada pela contadora Rosangela em 24/09/2026 para todas as empresas do escritório.
> As regras específicas desta empresa descritas acima **continuam valendo**. Este bloco completa o que faltar e **não substitui** nenhuma conta, exceção ou classificação já confirmada. Em caso de conflito, prevalece a regra específica da empresa.

### Parâmetros desta empresa

| Sócio | CPF | Pró-labore | Conta pró-labore a pagar | Conta do sócio (retirada / aporte) |
|---|---|---|---|---|
| Emerson Mohr | 035.870.159-70 | Variável — perguntar todo mês | **188** | **539** |
| Sueli Ribeiro Mohr | 037.687.209-85 | Variável — perguntar todo mês | **188** | **548** |

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
