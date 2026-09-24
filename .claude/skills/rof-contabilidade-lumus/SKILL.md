---
name: rof-contabilidade-lumus
description: Lançamentos contábeis e conciliação bancária da empresa LUMUS - ESPECIALIDADES TERAPEUTICAS E NEURODESENVOLVIMENTO LTDA (CNPJ 50.724.260/0001-88, Simples Nacional, saúde/terapias, Mercado Pago) para o sistema Domínio (Thomson Reuters). Use quando o usuário pedir para conciliar extrato, cruzar movimentações, classificar lançamentos no plano de contas ou gerar o arquivo TXT no leiaute Domínio da LUMUS. Recebe extrato bancário do Mercado Pago, plano de contas e razão como referência; pesquisa CNPJ no portal da Receita antes de classificar; e gera TXT único com pagamentos e recebimentos ordenados por data.
---

# ROF Contabilidade Lumus — Lançamentos Contábeis e Conciliação

## Dados da Empresa

| Campo | Informação |
|---|---|
| Razão social | LUMUS - ESPECIALIDADES TERAPEUTICAS E NEURODESENVOLVIMENTO LTDA |
| CNPJ | 50.724.260/0001-88 |
| CNPJ sem formatação | 50724260000188 |
| CNAE principal | 8650-0/03 |
| CNAEs secundários | 8599-6/99 · 8630-5/03 · 8650-0/04 · 8650-0/06 |
| Setor | Saúde — especialidades terapêuticas e neurodesenvolvimento |
| Regime tributário | Simples Nacional |
| Banco único | MERCADO PAGO — conta 80117768620 → código contábil **541** |

## Sócias

| Sócia | CPF | Conta no Domínio |
|---|---|---|
| EDRINE JAMILLE DE DEUS MENDES | 061.628.879-44 | **526** (Ativo 1.2.2.04.001) |
| VERONICA DE DEUS CARVALHO | 090.937.859-23 | **546** (Ativo 1.2.2.04.002) |

## Regras de Trabalho (ACORDO COM A CONTADORA)

1. **Fidelidade total** aos dados enviados — não alterar nada sem consultar
2. **Consulta prévia** antes de qualquer alteração
3. **Base legal** sempre que sugerir algum ajuste
4. **Histórico idêntico ao extrato bancário** — copiar o texto do extrato sem alterar, sem resumir, sem traduzir

## Leiaute do Arquivo TXT para Domínio

```
|0000|50724260000188|
|6000|X||||
|6100|DD/MM/AAAA|CONTA_DEBITO|CONTA_CREDITO|VALOR||HISTORICO||||
```

- `|0000|` = identificação pela empresa (CNPJ sem formatação)
- `|6000|X||||` = separador entre lançamentos
- `|6100|` = lançamento: data · conta débito · conta crédito · valor · histórico
- **Pagamento (saída):** débito na conta de despesa/ativo, crédito no banco (**541**)
- **Recebimento (entrada):** débito no banco (**541**), crédito na conta de receita
- **Arquivo único:** pagamentos e recebimentos compilados juntos, ordenados por data — **NÃO gerar dois arquivos separados**
- Valor com vírgula decimal: ex. `1500,00`

## Plano de Contas — Contas Operacionais da Lumus

| Cód | Classificação | Nome | Natureza |
|---|---|---|---|
| **541** | 1.1.1.02.004 | BANCO MERCADO PAGO - 80117768620 | Ativo — conta bancária principal |
| **504** | 1.1.2.01.001 | CLIENTES DIVERSOS | Ativo — recebimentos de clientes |
| **526** | 1.2.2.04.001 | EDRINE JAMILLE DE DEUS MENDES | Ativo — conta corrente sócia Edrine |
| **546** | 1.2.2.04.002 | VERONICA DE DEUS CARVALHO | Ativo — conta corrente sócia Veronica |
| **527** | 1.1.3.00.01 | EMPRESTIMO A SOCIO A RECEBER | Ativo — empréstimo a sócia |
| **188** | 2.1.5.01.002 | PRÓ-LABORE A PAGAR | Passivo — pró-labore Edrine |
| **189** | 2.1.5.01.003 | PRÓ-LABORE VERONICA DE DEUS CARVALHO | Passivo — pró-labore Veronica |
| **506** | 2.1.3.01.001 | FORNECEDOR MODELO | Passivo — fornecedores PJ |
| **479** | 2.1.4.01.015 | SIMPLES NACIONAL A RECOLHER | Passivo — tributo |
| **542** | 3.1.3.01.001 | PRÓ-LABORE (despesa Edrine) | Resultado — custo pró-labore Edrine |
| **543** | 3.1.3.01.002 | PRÓ-LABORE VERONICA DE DEUS CARVALHO | Resultado — custo pró-labore Veronica |
| **362** | 3.2.2.04.009 | SERVIÇOS PRESTADOS POR TERCEIROS | Despesa — pagamentos a PF terceiros |
| **366** | 3.2.2.04.013 | DESPESAS ADMINISTRATIVAS | Despesa — reserva/liberação Mercado Pago e retiradas pessoais |
| **325** | 3.2.2.04.015 | DESPESAS DIVERSAS | Despesa — tarifas e taxas Mercado Pago |
| **493** | 3.2.2.04.014 | MULTA DE TRÂNSITO | Despesa — assinaturas, despesas diversas |

## Regra de Classificação das Contrapartes — LEIA ANTES DE CLASSIFICAR

> Esta é a regra mais importante do fluxo. O TXT do Otimizza **não é parâmetro de classificação** — serve apenas para conhecer o leiaute do Domínio. A classificação correta parte do extrato + plano de contas + razão + pesquisa externa.

### Para cada lançamento do extrato, siga esta ordem:

**1. Identifique a natureza: ENTRADA ou SAÍDA**

---

#### ENTRADAS (valor positivo no extrato)

> **Regra geral de entradas: D-541 / C-504 (Clientes Diversos)**
> Toda entrada de dinheiro é recebimento de cliente — conta **504** — salvo as exceções abaixo.

**Exceções às entradas:**
- **Aporte de sócia** (Edrine ou Veronica transferindo para a empresa) → aplicar a **Regra de Aporte** abaixo
- **Empréstimo creditado pelo banco** (descrição indica empréstimo/financiamento) → **perguntar à contadora antes de classificar** (geralmente conta **152**, mas confirmar)
- **Liberação de dinheiro** (reserva liberada pelo Mercado Pago) → D-541 / C-366
- **Dinheiro retirado Pessoal** → recebimento de cliente em dinheiro/presencial → segue a regra geral: D-541 / C-**504**

**Não é necessário pesquisar CNPJ para entradas** — independentemente de ser PF ou PJ, o recebimento vai para conta **504**.

---

#### SAÍDAS (valor negativo no extrato)

**2. Identifique o favorecido:**
- O extrato traz nome e, às vezes, CNPJ/CPF do favorecido.

**3. Se tiver CNPJ — pesquise no portal da Receita Federal antes de classificar:**
- Acesse: https://www.receita.fazenda.gov.br/PessoaJuridica/CNPJ/cnpjreva/Cnpjreva_Solicitacao2.asp
- Verifique a **atividade econômica (CNAE)** da empresa favorecida.
- Avalie se a atividade **condiz com a operação da Lumus** (saúde, terapias, neurodesenvolvimento).
- Com base na atividade confirmada, classifique na conta mais específica do plano de contas.

**4. Se for Pessoa Física — exceto as sócias:**
- Classificar **sempre** em `362` — SERVIÇOS PRESTADOS POR TERCEIROS.
- Não pesquisar; não criar conta nova.

**5. Se for uma das sócias (Edrine ou Veronica):**
- Aplicar a **Regra de Retiradas das Sócias** abaixo.

---

**6. Histórico:**
- Copiar **textualmente** do extrato bancário, sem alterar, resumir ou traduzir.

---

## Regra Mensal — Retiradas das Sócias

> **Acumular cronologicamente pelo extrato:** conforme os pagamentos às sócias aparecem no extrato (em ordem de data), somar o acumulado e aplicar o rateio automaticamente — sem perguntar o total antes.

**Pró-labore mensal por sócia = salário mínimo nacional vigente**

| Cálculo | Fórmula |
|---|---|
| Salário mínimo vigente | Consultar valor em vigor no mês de competência |
| INSS (11%) | Salário mínimo × 11% |
| **Pró-labore líquido** | Salário mínimo − INSS |

**Lançamentos por sócia — acumular cronologicamente no mês:**

| Valor acumulado | Débito | Crédito | Observação |
|---|---|---|---|
| Até o pró-labore líquido | `188` (Edrine) ou `189` (Veronica) | `541` | Pró-labore — passivo |
| Excedente acima do limite | `526` (Edrine) ou `546` (Veronica) | `541` | Adiantamento — ativo |

Se um único pagamento cruzar o limite, representar com **duas linhas `6100`** no TXT (uma por débito), crédito sempre no banco, preservando o total.

**Controle separado por sócia:** o acumulado de Edrine e o de Veronica são calculados de forma independente.

**Exemplo** — pró-labore líquido R$ 1.442,69; Edrine recebe R$ 3.000,00 em único PIX:
```
|6000|X||||
|6100|DD/MM/AAAA|188|541|1442,69||REF. A PIX ENVIADO EDRINE JAMILLE DE DEUS MENDES||||
|6000|X||||
|6100|DD/MM/AAAA|526|541|1557,31||REF. A PIX ENVIADO EDRINE JAMILLE DE DEUS MENDES||||
```

---

## Regra — Aporte de Sócia (sócia coloca dinheiro na empresa)

Quando uma sócia transfere ou deposita valores **para a empresa** (entrada no extrato MP):

| Débito | Crédito |
|---|---|
| `541` (banco MP) | `526` se Edrine / `546` se Veronica |

O crédito na conta da sócia (ativo) **reduz o saldo devedor** que ela tem com a empresa — é a devolução do que foi retirado anteriormente. O controle é individual: aporte de Edrine vai para 526, aporte de Veronica vai para 546.

---

## Particularidades do Mercado Pago

O Mercado Pago é intermediário financeiro: retém parte dos recebimentos como reserva temporária de proteção contra estornos, e a libera dias depois. Esses movimentos não representam receita de clientes nem pagamento a terceiros — são o próprio dinheiro da empresa circulando dentro do MP. Identificados pelo razão histórico da conta 541.

### Retenção de reserva pelo MP
- Aparece no extrato como saída (o valor retido sai do saldo disponível).
- Contrapartida confirmada no razão: **D `366` / C `541`**.
- Histórico no TXT: copiar exatamente o texto do extrato.

### Liberação da reserva pelo MP
- Aparece no extrato como entrada (o MP devolve o valor retido).
- Contrapartida confirmada no razão: **D `541` / C `366`**.
- Histórico no TXT: copiar exatamente o texto do extrato.

Esses dois lançamentos são automáticos e recorrentes — não exigem pesquisa de CNPJ. A conta `366` (Despesas Administrativas) é a contrapartida para ambos, conforme histórico do razão.

### Tarifas e taxas cobradas pelo Mercado Pago/Livre
- Confirmar natureza pelo histórico do extrato e pelo razão.
- Contrapartida: **`325`** (Despesas Diversas) / `541`.
- Histórico no TXT: copiar exatamente o texto do extrato.

### Assinaturas e despesas diversas (ex.: Meli+, outros serviços)
- Confirmar identificando o favorecido no extrato.
- Contrapartida: **`493`** (Multa de Trânsito — conta usada para este tipo de despesa) / `541`.
- Histórico no TXT: copiar exatamente o texto do extrato.

---

## Regra Inviolável — Conferência de Saldo Antes da Entrega

> **Nunca entregar o TXT sem que os saldos do extrato estejam fechando.**

Antes de gerar o arquivo final, conferir obrigatoriamente:

1. **Saldo anterior (abertura)** informado no extrato
2. **Saldo final (encerramento)** informado no extrato
3. **Diferença esperada** = Saldo final − Saldo anterior
4. **Somar todas as entradas** lançadas no TXT
5. **Somar todas as saídas** lançadas no TXT
6. **Diferença apurada** = Total entradas − Total saídas

Se **Diferença apurada ≠ Diferença esperada** → **NÃO entregar o TXT**. Identificar e corrigir a divergência antes de qualquer entrega.

---

## Regra Inviolável — Aplicações Financeiras e Rendimentos

> **Nunca omitir movimentações de aplicação financeira do TXT.**

A cada competência, antes de iniciar os lançamentos:

1. **Verificar no plano de contas** se a empresa possui conta(s) de aplicação financeira (CDB, poupança, fundo, RDB, etc.)
2. **Se houver aplicação, conferir obrigatoriamente:**
   - **Aporte** (transferência da conta corrente para a aplicação) → lançar
   - **Resgate** (transferência da aplicação para a conta corrente) → lançar
   - **Rendimentos creditados** → lançar na conta de receitas financeiras correspondente
   - **IRRF retido** sobre os rendimentos → lançar na conta de IRRF correspondente
3. **Nunca omitir rendimentos** por ausência de documento físico — se o extrato ou razão indicar crédito de rendimentos, lançar.
4. **Reconciliar saldo da aplicação:** saldo anterior + aportes + rendimentos − resgates − IRRF = saldo final do extrato/razão da aplicação.

---

## Regra Inviolável — IOF e IRRF

> **Nunca omitir IOF nem IRRF do TXT, seja sobre aplicação ou sobre qualquer outra operação.**

### IOF (Imposto sobre Operações Financeiras)
- Aparece no extrato como débito automático em operações de crédito, câmbio, seguros ou aplicações financeiras.
- Localizar a conta de IOF no plano de contas da Lumus e lançar sempre que aparecer no extrato.
- **Não incluir no valor principal da operação** — lançar separadamente.

### IRRF (Imposto de Renda Retido na Fonte)
- Aparece no extrato como débito automático sobre rendimentos de aplicações (CDB, poupança, fundos, RDB).
- Pode também incidir sobre pagamentos a prestadores de serviços (verificar no extrato/relatório).
- Localizar a conta de IRRF no plano de contas da Lumus e lançar sempre que aparecer no extrato ou razão.
- **Nunca omitir** por ser valor pequeno ou por ausência de documento físico — se constar no extrato ou razão, lança.

---

## Fluxo de Trabalho

1. **Confirmar o mês de competência do extrato** antes de qualquer lançamento.
2. **Receber o extrato do Mercado Pago** (PDF, CSV ou OFX) e o plano de contas.

2. **Para cada lançamento, na ordem:**
   a. Identificar natureza: entrada (recebimento) ou saída (pagamento).
   b. Identificar favorecido: nome, CNPJ ou CPF.
   c. Verificar se é reserva/liberação MP, tarifa MP ou assinatura → aplicar regra automática.
   d. Se sócia → aplicar Regra de Retiradas ou Regra de Aporte.
   e. Se PJ com CNPJ → pesquisar Receita Federal → classificar conforme atividade.
   f. Se PF (exceto sócias) → conta `362`.
   g. Copiar histórico textualmente do extrato.

3. **Sinalizar** lançamentos não identificados para revisão da contadora antes de finalizar.

4. **Gerar TXT único** no leiaute Domínio: pagamentos e recebimentos juntos, em ordem cronológica de data.

5. **Não gerar dois arquivos separados** (PAGAR e RECEBER): tudo em um único TXT.

## Parâmetros Adicionais

- O razão do Mercado Pago serve como referência histórica de classificação — consultar quando houver dúvida sobre um favorecido recorrente.
- Qualquer dúvida ou divergência: pontuar para a contadora ANTES de prosseguir.
- Cada empresa deve ser trabalhada em conversa separada.

## Pendências a confirmar com a contadora

- [ ] Confirmar conta para Simples Nacional quando pago via extrato MP (`479`?)

## Definições Confirmadas

- **"DINHEIRO RETIRADO PESSOAL"** (saque físico no terminal MP): lançar na conta **5** (Caixa) — a confirmar com o cliente o destino final.
- **Fornecedores PJ** com CNPJ e atividade compatível com a Lumus: usar conta **506** (Fornecedor Modelo).

---

## Padrão ROF — Pró-labore, Retiradas e Relatório do Sócio

> Regra validada pela contadora Rosangela em 24/09/2026 para todas as empresas do escritório.
> As regras específicas desta empresa descritas acima **continuam valendo**. Este bloco completa o que faltar e **não substitui** nenhuma conta, exceção ou classificação já confirmada. Em caso de conflito, prevalece a regra específica da empresa.

### Parâmetros desta empresa

| Sócio | CPF | Pró-labore | Conta pró-labore a pagar | Conta do sócio (retirada / aporte) |
|---|---|---|---|---|
| Edrine Jamille de Deus Mendes | ver acima | Variável — perguntar todo mês | **188** | **526** |
| Veronica de Deus Carvalho | ver acima | Variável — perguntar todo mês | **189** | **546** |

> Banco desta empresa = **541** (Mercado Pago).

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
