---
name: rof-contabilidade-lucasromano
description: "Lucas Romano Santos Ltda | CNPJ 43.534.615/0001-00 | Simples Nacional | Serviços de informação e administrativos | Nubank"
---

# ROF Contabilidade Lucas Romano — Lançamentos Contábeis e Conciliação

## Dados da Empresa

| Campo | Informação |
|---|---|
| Razão social | LUCAS ROMANO SANTOS LTDA |
| Nome fantasia | ROMANO |
| CNPJ | 43.534.615/0001-00 |
| CNPJ sem formatação | 43534615000100 |
| CNAE principal | 5819-1/00 — Edição de cadastros, listas e outros produtos gráficos |
| CNAE secundário 1 | 6399-2/00 — Outras atividades de prestação de serviços de informação |
| CNAE secundário 2 | 8219-9/99 — Preparação de documentos e serviços especializados de apoio administrativo |
| Setor | Serviços de informação / administrativos |
| Regime tributário | Simples Nacional |
| Banco | Nubank — Conta 44490784-4 → código **8** |
| Sistema | Domínio (Thomson Reuters) |
| Cadastrado por | Rosangela |

## Sócios

| Sócio | CPF | Conta no Domínio |
|---|---|---|
| LUCAS ROMANO SANTOS | 094.738.999-71 | **528** (Sócios, Administradores e Pessoas Ligadas — Ativo Não-Circulante) |

- **Sem pró-labore estabelecido**
- **Sem funcionários CLT**

## Regras de Trabalho (ACORDO COM A CONTADORA)

1. **Fidelidade total** aos dados enviados — não alterar nada sem consultar
2. **Consulta prévia** antes de qualquer alteração
3. **Base legal** sempre que sugerir algum ajuste
4. **Histórico**: copiar o texto exatamente como está no extrato bancário, sem alterar, resumir ou traduzir

## Leiaute do Arquivo TXT para Domínio

```
|0000|43534615000100|
|6000|X||||
|6100|DD/MM/AAAA|CONTA_DEBITO|CONTA_CREDITO|VALOR||HISTORICO||||
```

- Pagamento (saída): débito na conta de despesa/ativo, crédito no banco (8)
- Recebimento (entrada): débito no banco (8), crédito na conta de receita/ativo
- ⚠️ **ARQUIVO ÚNICO OBRIGATÓRIO**: todos os lançamentos de todos os bancos, pagamentos e recebimentos, ordenados por data — em um único TXT. Mesmo que a empresa tenha múltiplos bancos, a contadora importa um único arquivo no Domínio. **NUNCA gerar arquivos separados por banco ou por tipo de movimento.**
- Valor com vírgula decimal: ex. 1500,00

## Plano de Contas — Contas Operacionais

| Cód | Classificação | Nome | Natureza |
|---|---|---|---|
| 8 | 1.1.1.02.001 | NU PAGAMENTOS S.A — CONTA 44490784-4 | Banco / Ativo Circulante |
| 504 | 1.1.2.01.001 | CLIENTES DIVERSOS | Ativo Circulante — Duplicatas a Receber |
| 506 | 2.1.3.01.001 | FORNECEDOR MODELO | Passivo — Fornecedores |
| 510 | 2.1.6.02.001 | HONORÁRIOS CONTÁBEIS | Passivo — Contas a Pagar |
| 528 | 1.2.2.04.001 | LUCAS ROMANO SANTOS (094.738.999-71) | Ativo Não-Circulante — Sócios |
| 529 | 3.2.2.04.015 | DESPESAS DIVERSAS | Despesa Administrativa |
| 533 | 2.3.5.01.007 | DISTRIBUIÇÃO DE LUCROS | Patrimônio Líquido |
| 535 | 1.2.2.01.001 | EMPRÉSTIMOS DE SÓCIOS | Ativo Não-Circulante — Títulos a Receber |
| 361 | 3.2.2.04.008 | ASSISTÊNCIA CONTÁBIL | Despesa Administrativa |
| 362 | 3.2.2.04.009 | SERVIÇOS PRESTADOS POR TERCEIROS | Despesa Administrativa |
| 365 | 3.2.2.04.012 | DESPESAS LEGAIS E JUDICIAIS | Despesa Administrativa |
| 411 | 4.1.1.02.001 | SERVIÇOS PRESTADOS | Receita Operacional |
| 467 | 3.1.6.01.001 | CUSTOS DOS SERVIÇOS PRESTADOS | Custo |
| 479 | 2.1.4.01.015 | SIMPLES NACIONAL A RECOLHER | Passivo — Obrigações Tributárias |
| 480 | 4.1.2.03.008 | (-) SIMPLES NACIONAL | Dedução da Receita |

## Regra de Classificação das Contrapartes — LEIA ANTES DE CLASSIFICAR

### Para cada lançamento do extrato, siga esta ordem:

1. Identifique o favorecido (nome, CNPJ/CPF)
2. Se tiver CNPJ → pesquisar no portal da Receita Federal (https://www.receita.fazenda.gov.br/PessoaJuridica/CNPJ/cnpjreva/Cnpjreva_Solicitacao2.asp) → verificar atividade → classificar conforme plano
3. Se for Pessoa Física (exceto sócio) → **362** (Serviços Prestados por Terceiros)
4. Se for o sócio Lucas Romano → aplicar **Regra Inviolável — Pró-labore x Retirada de Sócio**
5. Histórico: copiar o texto exatamente como está no extrato

### Classificação dos pagamentos à Receita Federal

| Tipo de pagamento | Conta |
|---|---|
| DAS — Simples Nacional | **479** — Simples Nacional a Recolher |
| INSS (se houver no futuro) | **191** — verificar conta no plano de contas |

## Regra Inviolável — Conferência de Saldo Antes da Entrega

> **Nunca entregar o TXT sem que os saldos do extrato estejam fechando.**

Antes de gerar o arquivo final, conferir obrigatoriamente:

1. Saldo anterior (abertura) informado no extrato
2. Saldo final (encerramento) informado no extrato
3. Diferença esperada = Saldo final − Saldo anterior
4. Somar todas as entradas lançadas no TXT
5. Somar todas as saídas lançadas no TXT
6. Diferença apurada = Total entradas − Total saídas

Se Diferença apurada ≠ Diferença esperada → NÃO entregar o TXT. Identificar e corrigir a divergência antes de qualquer entrega.

## Regra Inviolável — Aplicações Financeiras e Rendimentos

> **Nunca omitir movimentações de aplicação financeira do TXT.**

Esta empresa não possui aplicação financeira cadastrada. Verificar no plano de contas a cada competência se isso mudou.

## Regra Inviolável — IOF e IRRF

> **Nunca omitir IOF nem IRRF do TXT.**

### IOF
- Conta: verificar no plano de contas se aparecer no extrato
- Lançar separadamente — não embutir no valor principal

### IRRF
- Conta: verificar no plano de contas se aparecer no extrato
- Nunca omitir por valor pequeno — se constar no extrato ou razão, lança

## Regra Inviolável — Pró-labore x Retirada de Sócio

> ANTES DE LANÇAR qualquer pagamento ao sócio: confirmar com a contadora o total pago no mês e se houve pagamentos parciais.

**Sócio sem pró-labore estabelecido — todos os pagamentos vão para retirada de sócio:**

| Movimento | Débito | Crédito |
|---|---|---|
| Pagamento ao sócio (saída) | **528** — Lucas Romano Santos | **8** — Nubank |
| Depósito do sócio na empresa (entrada) | **8** — Nubank | **528** — Lucas Romano Santos |

> ⚠️ **Depósito do sócio na empresa**: lançar provisoriamente em **528** e **sinalizar para análise da contadora** antes de finalizar — pode ser devolução de retirada (528) ou empréstimo de sócio (535), dependendo do contexto.

## Classificações Recorrentes Confirmadas pelo Razão

| Favorecido / Descrição | CNPJ/CPF | Conta |
|---|---|---|
| OURIBANK S.A. — transferências recebidas (receita de clientes) | 78.632.767/0001-20 | **504** — Clientes Diversos |
| PAES E BASTOS CONTABILIDADE LTDA | 29.650.531/0001-01 | **510** — Honorários Contábeis |
| RECEITA FEDERAL — DAS / Simples Nacional | 00.394.460/0058-87 | **479** — Simples Nacional a Recolher |
| LUCAS ROMANO SANTOS — pagamentos/retiradas | CPF 094.738.999-71 | **528** — Retirada de Sócio |
| LUCAS ROMANO SANTOS — depósito na empresa | CPF 094.738.999-71 | **528** ⚠️ analisar antes de finalizar |
| GOOGLE CLOUD BRASIL COMPUTACAO E SERVICOS DE DADOS LTDA | verificar CNPJ | **467** — Custos dos Serviços Prestados |
| MURILO MINORU MURATA (Pessoa Física) | verificar CPF | **362** — Serviços Prestados por Terceiros |

## Fluxo de Trabalho

1. Receber extrato bancário (PDF, CSV ou OFX)
2. Para cada lançamento:
   a. Identificar natureza (entrada/saída)
   b. Identificar favorecido (CNPJ/CPF)
   c. Verificar nas Classificações Recorrentes acima
   d. Se não encontrar: pesquisar CNPJ na Receita Federal e classificar conforme plano de contas
   e. Aplicar regra de sócio se for Lucas Romano Santos
   f. Registrar histórico copiando exatamente do extrato
3. Sinalizar lançamentos não identificados para revisão antes de finalizar
4. Verificar IOF e IRRF — nada pode ficar de fora
5. Conferir saldo: entradas − saídas = variação do extrato
6. Gerar **um único TXT** com todos os lançamentos ordenados por data

## Parâmetros Adicionais

- O razão serve como referência histórica de classificação (período disponível: 01/03/2026 a 30/06/2026)
- Qualquer dúvida ou divergência: pontuar para a contadora ANTES de prosseguir
- Cada empresa deve ser trabalhada em conversa separada
- Contadora responsável: Renata Bastos Amado — CRC PR075217/O-2

## Pendências a Confirmar com a Contadora

- Conta **191** (INSS) não localizada no plano de contas atual — empresa sem pró-labore. Verificar se precisará ser criada no futuro.
- Depósito do sócio na empresa: confirmar a cada ocorrência se é **devolução de retirada (528)** ou **empréstimo de sócio (535)**.

---

## Padrão ROF — Pró-labore, Retiradas e Relatório do Sócio

> Regra validada pela contadora Rosangela em 24/09/2026 para todas as empresas do escritório.
> As regras específicas desta empresa descritas acima **continuam valendo**. Este bloco completa o que faltar e **não substitui** nenhuma conta, exceção ou classificação já confirmada. Em caso de conflito, prevalece a regra específica da empresa.

### Parâmetros desta empresa

| Sócio | CPF | Pró-labore | Conta pró-labore a pagar | Conta do sócio (retirada / aporte) |
|---|---|---|---|---|
| Lucas Romano Santos | 094.738.999-71 | **Não há** | — | **528** |

> Depósito do sócio: manter a sinalização da regra acima (528 × 535).

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
