---
name: rof-nova-empresa
description: "Adiciona busca automática do salário mínimo nacional vigente na Etapa 2 de pró-labore"
---

# ROF Nova Empresa — Onboarding e Geração de Skill

## Objetivo

Guia o levantamento de dados de um novo cliente em 4 etapas enxutas e gera automaticamente o SKILL.md da empresa no padrão ROF, compatível com o sistema Domínio (Thomson Reuters).

---

## Abertura

Ao ser invocado, fazer imediatamente:

> "Olá! Com quem estou trabalhando hoje — Rosangela ou Elen?"

Registrar o nome como **responsável pelo cadastro** (campo "Cadastrado por" no SKILL.md gerado). Se informar outro nome, registrar normalmente.

---

## Etapa 1 — Dados Cadastrais

1. Pedir **somente o CNPJ** (com ou sem formatação).
2. **Buscar automaticamente** na Receita Federal via:
   `https://www.receitaws.com.br/v1/cnpj/{CNPJ_SEM_FORMATACAO}`
3. **Apresentar tabela** com os dados retornados:

| Campo | Dado retornado |
|---|---|
| Razão Social | |
| CNPJ | |
| Situação | |
| CNAE Principal | |
| CNAEs Secundários | |
| Endereço | |
| Abertura | |

4. Perguntar: **"[Nome], pode confirmar?"**
5. Após confirmação, perguntar:
   - **Regime tributário**: Simples Nacional · Lucro Presumido · Lucro Real · MEI
   - **Setor / atividade resumida** (ex.: saúde, academia, comércio, cosméticos)
   - **Vai usar o Domínio?** (sim / não — define se gera leiaute TXT)

---

## Etapa 2 — Sócios, Pró-labore e CLT

Para **cada sócio**, perguntar:
- **Nome completo** e **CPF**
- **Tem pró-labore?**

### Com pró-labore
- **O pró-labore não tem padrão e varia mês a mês** (em especial no Simples Nacional com Fator R). No SKILL.md gerado, registrar `Pró-labore: variável — perguntar todo mês` — o valor informado no cadastro é só a última referência.
- Informar o **valor atual** do pró-labore (referência)
- Se o usuário indicar **"salário mínimo nacional"** como base:
  - **Buscar automaticamente** o valor vigente via WebSearch: `"salário mínimo nacional vigente [ano corrente] Brasil valor"`
  - Apresentar o valor encontrado e confirmar com o usuário antes de calcular
  - Registrar no SKILL.md apenas como referência: `Pró-labore: variável — perguntar todo mês (última referência: R$ X.XXX,XX, [mês/ano])`
- Calcular automaticamente:
  - INSS = Base × 11%
  - Pró-labore líquido = Base − INSS
- Regra de lançamento:
  - Até o valor líquido → **pró-labore** (conta passivo a pagar)
  - Excedente → **retirada de sócio** (conta ativo, com nº + nome + CPF do sócio)
- Perguntar a **conta contábil** do sócio no Domínio (ex.: 526, 532, 541)

### Sem pró-labore
- Toda retirada vai direto para **retirada de sócio** (conta ativo, com nº + nome + CPF)
- Perguntar a **conta contábil** do sócio no Domínio

### Em ambos os casos
- Depósito do sócio **na empresa** (entrada no extrato) = **devolução / estorno** → crédito na conta ativo do sócio (reduz saldo devedor)
- Registrar no SKILL.md gerado a **pergunta mensal obrigatória** (valor do pró-labore do mês, ou se continua sem pró-labore) e o **Relatório XLSX de Pró-labore e Retiradas** como entrega obrigatória junto com o TXT — ver estrutura abaixo.
- Provisão do pró-labore/INSS **não** entra no TXT (vem da folha do Domínio).

### Funcionários CLT
- Perguntar: **"A empresa tem funcionários CLT?"**
- Se sim: registrar nome, cargo e salário base informados. Adicionar nota: *"Dados completos da folha serão buscados no Domínio: Módulo Folha → Relatórios → Cadastrais → Empregado, quando o primeiro extrato chegar."*

---

## Etapa 3 — Documentos de Referência

Solicitar os seguintes arquivos (todos em **Excel**, preferencialmente):

| Documento | Finalidade |
|---|---|
| Razão das contas bancárias — últimos 3 meses | Referência histórica de classificação |
| Plano de contas | Estrutura de contas do Domínio |
| Balancete — últimos 3 meses | Confirmar saldos e contas em uso |
| TXT Otimizza (se disponível) | Confirmar leiaute aceito pelo Domínio |

- Se algum documento não estiver disponível (empresa nova), registrar como **pendência** no SKILL.md.
- O TXT Otimizza serve **exclusivamente** para confirmar o leiaute — classificações partem sempre do plano de contas e razão.

Analisar os documentos recebidos e extrair:
- Contas operacionais relevantes (banco, clientes, fornecedores, sócios, tributos, despesas recorrentes)
- Contrapartidas já validadas pela contadora para movimentos recorrentes
- Particularidades do banco (tarifas, IOF, reserva/liberação se for banco intermediário)

---

## Etapa 4 — Revisão e Geração do SKILL.md

1. **Apresentar resumo** de todas as informações coletadas.
2. **Perguntar se há correções** ou informações adicionais.
3. **Confirmar o nome da skill** (padrão: `rof-contabilidade-<slug>`, minúsculo, sem espaços, sem acentos).
4. **Gerar o arquivo SKILL.md** completo (estrutura abaixo) e salvar em:
   `/root/.claude/skills/synced/rof-contabilidade-<slug>/SKILL.md`
5. Informar ao usuário:
   > "Para empacotar, execute:
   > ```
   > cd /root/.claude/skills/synced/skill-creator
   > python -m scripts.package_skill /root/.claude/skills/synced/rof-contabilidade-<slug>
   > ```
   > O arquivo `.skill` gerado pode ser importado no seu escritório."
6. **Registrar a nova empresa** na seção "Empresas cadastradas" do motor (`rof-contabilidade/SKILL.md`).

---

## Estrutura do SKILL.md Gerado

```markdown
---
name: rof-contabilidade-<slug>
description: "<razão social>, CNPJ <CNPJ>, <regime>, <setor>, banco principal: <banco>"
---

# ROF Contabilidade <NOME> — Lançamentos Contábeis e Conciliação

## Dados da Empresa

| Campo | Informação |
|---|---|
| Razão social | <razão social> |
| CNPJ | <CNPJ formatado> |
| CNPJ sem formatação | <CNPJ só números> |
| CNAE principal | <código + descrição> |
| CNAEs secundários | <lista ou "—"> |
| Setor | <setor resumido> |
| Regime tributário | <regime> |
| Banco(s) | <nome banco → código contábil> |
| Cadastrado por | <responsável pelo cadastro> |

## Sócios

| Sócio | CPF | Conta no Domínio |
|---|---|---|
| <nome> | <CPF> | **<código>** (<classificação>) |

## Regras de Trabalho (ACORDO COM A CONTADORA)

1. **Fidelidade total** aos dados enviados — não alterar nada sem consultar
2. **Consulta prévia** antes de qualquer alteração
3. **Base legal** sempre que sugerir algum ajuste
4. **Histórico**: copiar o texto exatamente como aparece no extrato bancário

## Leiaute do Arquivo TXT para Domínio

|0000|<CNPJ sem formatação>|
|6000|X||||
|6100|DD/MM/AAAA|CONTA_DEBITO|CONTA_CREDITO|VALOR||HISTORICO||||

- Pagamento (saída): débito na conta de despesa/ativo, crédito no banco
- Recebimento (entrada): débito no banco, crédito na conta de receita
- Arquivo único: pagamentos e recebimentos ordenados por data
- Valor com vírgula decimal: ex. 1500,00

## Plano de Contas — Contas Operacionais

| Cód | Classificação | Nome | Natureza |
|---|---|---|---|
<tabela com todas as contas levantadas>

## Regra de Classificação das Contrapartes

### Para cada lançamento do extrato, siga esta ordem:

1. Identificar natureza (entrada / saída)
2. Identificar favorecido (nome, CNPJ/CPF)
3. Se tiver CNPJ → pesquisar na Receita Federal → verificar atividade → classificar conforme plano de contas
4. Se Pessoa Física (exceto sócios) → conta <código PF>
5. Se sócio → aplicar Regra de Retiradas
6. Se banco intermediário → regra automática (se aplicável)
7. Histórico: copiar exatamente como aparece no extrato

## Regra Inviolável — Conferência de Saldo

> Nunca entregar o TXT sem que os saldos do extrato estejam fechando.

1. Saldo anterior (abertura) informado no extrato
2. Saldo final (encerramento) informado no extrato
3. Diferença esperada = Saldo final − Saldo anterior
4. Somar todas as entradas lançadas no TXT
5. Somar todas as saídas lançadas no TXT
6. Diferença apurada = Total entradas − Total saídas

Se Diferença apurada ≠ Diferença esperada → NÃO entregar o TXT.

## Regra Inviolável — Aplicações Financeiras e Rendimentos

> Nunca omitir movimentações de aplicação financeira do TXT.

<se não houver: "Esta empresa não possui aplicação financeira cadastrada.">
<se houver: listar contas e regras específicas>

## Regra Inviolável — IOF e IRRF

> Nunca omitir IOF nem IRRF do TXT.

- IOF → conta <código> — lançar separadamente
- IRRF → conta <código> — nunca omitir por valor pequeno

## Regra Mensal — Retiradas dos Sócios

> **Pergunta obrigatória antes de escriturar cada competência (aguardar resposta):**
> - Com pró-labore → "Qual o valor do pró-labore de <sócio> em <mês/ano>?" (pode variar mês a mês)
> - Sem pró-labore → "A empresa continua sem pró-labore em <mês/ano>?"
>
> Acumular os pagamentos a cada sócio no mês em ordem de data, **somando todos os bancos**. Pagamento que atravessa o limite vira duas linhas `|6100|`. Provisão do pró-labore/INSS **não** entra no TXT (vem da folha do Domínio). INSS DARF 1099 → D 191 / C banco.

**Pró-labore: variável — perguntar o valor todo mês (última referência: R$ <valor>, <mês/ano>). Não existe valor padrão; no Simples Nacional considerar a estratégia do Fator R definida pela contadora.**

| Cálculo | Fórmula |
|---|---|
| Base | Valor bruto informado pela contadora no mês |
| INSS (11%) | Base × 11% |
| Pró-labore líquido | Base − INSS |

| Valor acumulado | Débito | Crédito |
|---|---|---|
| Até o pró-labore líquido | <conta passivo> | <conta banco> |
| Excedente | <conta ativo sócio> | <conta banco> |

## Regra — Devolução / Aporte do Sócio

Quando o sócio deposita valores **na empresa** (entrada no extrato):

| Débito | Crédito |
|---|---|
| <conta banco> | <conta ativo do sócio> |

## Regra Inviolável — Relatório de Pró-labore e Retiradas (entrega obrigatória)

> Toda competência entrega **sempre dois arquivos juntos**: o TXT **e** a planilha `<Empresa>_ProLabore_Retiradas_AAAAMM.xlsx`. Gerar sem esperar pedido, inclusive sem movimentação do sócio no mês.

- **Aba Resumo:** empresa, CNPJ, competência, bancos; parâmetros (base, INSS 11%, líquido); por sócio: total pago, pró-labore pago, retiradas, devoluções/aportes, retirada líquida, INSS recolhido, pró-labore líquido não pago
- **Uma aba por sócio:** Data · Banco · Cód. conta bancária · Histórico · Tipo (Pró-labore / Retirada / Aporte-Devolução) · Valor · Acumulado · Parcela pró-labore · Parcela retirada · Conta débito · Conta crédito — fórmulas `MÍN(valor; limite − acumulado anterior)` e `valor − parcela pró-labore`; aportes em cor diferenciada; subtotais
- **Conferência:** soma da planilha = linhas do TXT nas contas de pró-labore e do sócio; resumo curto por sócio também no chat

## Particularidades do Banco

<se banco intermediário: regras de retenção/liberação de reserva>
<se banco comum: tarifas e IOF>

## Classificações Recorrentes Confirmadas

| Fornecedor / Descrição | Conta |
|---|---|
<linhas confirmadas pelo razão>

## Fluxo de Trabalho

1. Receber extrato bancário (PDF, CSV ou OFX) e plano de contas; fazer a pergunta mensal do pró-labore
2. Para cada lançamento: identificar natureza → favorecido → classificar → registrar histórico
3. Sinalizar lançamentos não identificados para revisão
4. Verificar aplicações financeiras, IOF e IRRF
5. Conferir saldo: entradas − saídas = variação do extrato
6. Gerar TXT único ordenado por data
7. Gerar e entregar junto a planilha XLSX de Pró-labore e Retiradas

## Pendências a Confirmar com a Contadora

<lista de itens pendentes — remover quando resolvidos>
```