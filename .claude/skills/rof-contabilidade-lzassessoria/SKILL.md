---
name: rof-contabilidade-lzassessoria
description: "LZ ASSESSORIA ESPORTIVA LTDA — lançamentos contábeis, conciliação bancária e geração de TXT para Domínio. Simples Nacional Anexo V com estratégia de Fator R, NU BANK, sócio Lucas Zen Ribeiro Pinto."
---

# ROF Contabilidade LZ ASSESSORIA ESPORTIVA — Lançamentos Contábeis e Conciliação

## Dados da Empresa

| Campo | Informação |
|---|---|
| Razão social | LZ ASSESSORIA ESPORTIVA LTDA |
| Nome fantasia | LZ ASSESSORIA |
| CNPJ | 68.396.130/0001-29 |
| CNPJ sem formatação | 68396130000129 |
| CNAE principal | 93.13-1-00 — Atividades de condicionamento físico |
| CNAEs secundários | — |
| Setor | Personal Trainer / Atividade Física |
| Regime tributário | Simples Nacional — Anexo V (com estratégia de Fator R) |
| Banco principal | NU BANK C/c 436875117-6 → 1.1.1.02.001 |
| Abertura | 23/07/2026 |
| Porte | Microempresa |
| Capital social | R$ 1.000,00 |
| Cadastrado por | Rosangela |

## Sócios

| Sócio | CPF | Conta no Domínio |
|---|---|---|
| Lucas Zen Ribeiro Pinto | 106.669.109-60 | **526 (1.2.2.04.0001)** (Sócios, Administradores e Pessoas Ligadas — Ativo Não Circulante) |

## Regras de Trabalho (ACORDO COM A CONTADORA)

1. **Fidelidade total** aos dados enviados — não alterar nada sem consultar
2. **Consulta prévia** antes de qualquer alteração
3. **Base legal** sempre que sugerir algum ajuste
4. **Histórico**: copiar o texto exatamente como aparece no extrato bancário

## Leiaute do Arquivo TXT para Domínio

```
|0000|68396130000129|
|6000|X||||
|6100|DD/MM/AAAA|CONTA_DEBITO|CONTA_CREDITO|VALOR||HISTORICO||||
```

- Pagamento (saída): débito na conta de despesa/ativo, crédito no banco
- Recebimento (entrada): débito no banco, crédito na conta de receita/passivo
- Arquivo único: pagamentos e recebimentos ordenados por data
- Valor com vírgula decimal: ex. 1500,00

## Plano de Contas — Contas Operacionais

| Classificação | Nome | Natureza |
|---|---|---|
| **ATIVO** | | |
| 1.1.1.01.001 | CAIXA GERAL | Ativo |
| 1.1.1.02.001 | NU BANK - C/c 436875117-6 | Ativo (banco principal) |
| 1.1.1.03.001 | RDB NU BANK | Ativo (aplicação liquidez imediata) |
| 1.1.2.01.001 | CLIENTES DIVERSOS | Ativo |
| 1.1.2.01.002 | CLIENTES DIVERSOS | Ativo |
| 1.2.2.04.0001 | LUCAS ZEN RIBEIRO PINTO (106.669.109-60) | Ativo (conta 526 — retiradas do sócio) |
| **PASSIVO** | | |
| 2.1.4.01.008 | IRRF A RECOLHER | Passivo |
| 2.1.4.01.011 | PROVISÃO PARA IOF | Passivo |
| 2.1.4.01.015 | SIMPLES NACIONAL A RECOLHER | Passivo |
| 2.1.5.01.002 | PRÓ-LABORE A PAGAR | Passivo |
| 2.1.5.02.001 | INSS A RECOLHER | Passivo |
| 2.1.6.02.001 | HONORÁRIOS CONTÁBEIS | Passivo |
| **DESPESAS** | | |
| 3.2.2.01.002 | PRÓ-LABORE (despesa administrativa) | Resultado |
| 3.2.2.01.006 | INSS (despesa administrativa) | Resultado |
| 3.2.2.02.001 | ALUGUÉIS DE IMÓVEIS | Resultado |
| 3.2.2.03.005 | TAXAS DIVERSAS | Resultado |
| 3.2.2.04.001 | ENERGIA ELÉTRICA | Resultado |
| 3.2.2.04.003 | TELEFONE | Resultado |
| 3.2.2.04.006 | MATERIAL DE ESCRITÓRIO | Resultado |
| 3.2.2.04.008 | ASSISTÊNCIA CONTÁBIL | Resultado |
| 3.2.2.04.009 | SERVIÇOS PRESTADOS POR TERCEIROS | Resultado |
| 3.2.2.05.005 | JUROS DE MORA | Resultado |
| 3.2.2.05.007 | JUROS E COMISSÕES BANCÁRIAS | Resultado |
| **RECEITAS** | | |
| 4.1.1.02.001 | SERVIÇOS PRESTADOS | Resultado |
| 4.1.3.01.001 | JUROS DE APLICAÇÕES | Resultado |

## Regra de Classificação das Contrapartes

### Para cada lançamento do extrato, siga esta ordem:

1. Identificar natureza (entrada / saída)
2. Identificar favorecido (nome, CNPJ/CPF)
3. Se tiver CNPJ → pesquisar na Receita Federal → verificar atividade → classificar conforme plano de contas
4. Se Pessoa Física (exceto sócio) → conta 1.1.2.01.001 (CLIENTES DIVERSOS)
5. Se sócio (Lucas Zen Ribeiro Pinto) → aplicar Regra de Retiradas abaixo
6. Histórico: copiar exatamente como aparece no extrato

## Regra Inviolável — Conferência de Saldo

> Nunca entregar o TXT sem que os saldos do extrato estejam fechando.

1. Saldo anterior (abertura) informado no extrato
2. Saldo final (encerramento) informado no extrato
3. Diferença esperada = Saldo final − Saldo anterior
4. Somar todas as entradas lançadas no TXT
5. Somar todas as saídas lançadas no TXT
6. Diferença apurada = Total entradas − Total saídas

Se Diferença apurada ≠ Diferença esperada → **NÃO entregar o TXT.**

## Regra Inviolável — Aplicações Financeiras e Rendimentos

> Nunca omitir movimentações de aplicação financeira do TXT.

**Conta de aplicação:** 1.1.1.03.001 — RDB NU BANK

- Aplicação (saída do banco): D: 1.1.1.03.001 | C: 1.1.1.02.001
- Resgate (entrada no banco): D: 1.1.1.02.001 | C: 1.1.1.03.001
- Rendimento creditado: D: 1.1.1.03.001 | C: 4.1.3.01.001 (JUROS DE APLICAÇÕES)

## Regra Inviolável — IOF e IRRF

> Nunca omitir IOF nem IRRF do TXT.

- IOF → conta 3.2.2.05.007 (JUROS E COMISSÕES BANCÁRIAS) — lançar separadamente, histórico: "IOF"
- IRRF → conta 2.1.4.01.008 (IRRF A RECOLHER) — nunca omitir por valor pequeno

## Regra Mensal — Retiradas dos Sócios

> ANTES DE LANÇAR qualquer pagamento a sócio: confirmar com a contadora o total pago no mês.

**⚠️ ATENÇÃO FATOR R:** O pró-labore base é R$ 2.000,00, mas o valor pode variar mensalmente conforme estratégia de enquadramento no **Fator R** (Simples Nacional Anexo V → Anexo III). Confirmar com a contadora o valor a usar em cada mês antes de lançar.

> Fórmula do Fator R: Folha de Salários (12 meses) ÷ Receita Bruta (12 meses) ≥ 28% → migra para Anexo III.

| Cálculo | Fórmula / Valor |
|---|---|
| Base do pró-labore | Confirmado pela contadora mensalmente |
| INSS (11%) | Base × 11% |
| Pró-labore líquido | Base − INSS |

### Lançamentos do Pró-labore

> ⚠️ **Itens 1 e 2 (provisão e INSS) NÃO entram no TXT** — são importados da folha do Domínio (confirmado pela contadora em 24/09/2026). Ficam aqui só como referência. O TXT lança apenas o item 3 (pagamento).

**1. Provisão do pró-labore (competência):**

| Débito | Crédito | Histórico |
|---|---|---|
| 3.2.2.01.002 (PRÓ-LABORE) | 2.1.5.01.002 (PRÓ-LABORE A PAGAR) | Pró-labore Lucas — competência MM/AAAA |

**2. INSS sobre pró-labore (11%):**

| Débito | Crédito | Histórico |
|---|---|---|
| 3.2.2.01.006 (INSS) | 2.1.5.02.001 (INSS A RECOLHER) | INSS pró-labore Lucas — MM/AAAA |

**3. Pagamento efetivo ao sócio — Regra de lançamento:**

| Valor acumulado pago no mês | Débito | Crédito |
|---|---|---|
| Até o pró-labore líquido | 2.1.5.01.002 (PRÓ-LABORE A PAGAR) | 1.1.1.02.001 (NU BANK) |
| Excedente ao pró-labore líquido | 1.2.2.04.0001 — LUCAS ZEN RIBEIRO PINTO (conta 526) | 1.1.1.02.001 (NU BANK) |

## Regra — Devolução / Aporte do Sócio

Quando Lucas Zen Ribeiro Pinto deposita valores **na empresa** (entrada no extrato):

| Débito | Crédito | Histórico |
|---|---|---|
| 1.1.1.02.001 (NU BANK) | 1.2.2.04.0001 — conta 526 (LUCAS ZEN RIBEIRO PINTO) | Devolução/aporte sócio Lucas — MM/AAAA |

> Esta operação reduz o saldo devedor da conta 526 (ativo do sócio).

## Particularidades do Banco

**NU BANK (1.1.1.02.001):**
- Tarifas bancárias: D: 3.2.2.05.007 (JUROS E COMISSÕES BANCÁRIAS) | C: 1.1.1.02.001
- IOF: D: 3.2.2.05.007 | C: 1.1.1.02.001 — lançar separadamente
- Rendimentos de conta: D: 1.1.1.02.001 | C: 4.1.3.01.001 (JUROS DE APLICAÇÕES)

## Classificações Recorrentes Confirmadas

| Fornecedor / Descrição | Conta |
|---|---|
| *(A confirmar quando o primeiro extrato chegar)* | — |

## Fluxo de Trabalho

1. Receber extrato bancário do NU BANK (PDF, CSV ou OFX) e confirmar período
2. Confirmar com a contadora o valor do pró-labore do mês (estratégia Fator R)
3. Para cada lançamento: identificar natureza → favorecido → classificar → registrar histórico
4. Verificar aplicações financeiras (RDB NU BANK), IOF e IRRF
5. Sinalizar lançamentos não identificados para revisão
6. Conferir saldo: entradas − saídas = variação do extrato
7. Gerar TXT único ordenado por data

## Pendências a Confirmar com a Contadora

- [ ] Conta contábil exata para lançamento do pró-labore como despesa (3.2.2.01.002 ou 3.1.1.02.002 — confirmar com contadora se classifica como despesa administrativa ou custo direto)
- [ ] Primeiro extrato do NU BANK ainda não recebido — classificações recorrentes a confirmar
- [ ] Razão das contas bancárias — pendente (empresa nova, primeiro mês)
- [ ] Balancete — pendente (empresa nova, primeiro mês)
- [ ] TXT Otimizza de referência — pendente (empresa nova, primeiro mês)
- [ ] Confirmar se haverá clientes Pessoa Jurídica (uso da conta 1.1.2.01.001 ou conta específica)
- [ ] Simples Nacional: confirmar DAS mensal → conta 2.1.4.01.015 (Simples Nacional a Recolher)

---

## Padrão ROF — Pró-labore, Retiradas e Relatório do Sócio

> Regra validada pela contadora Rosangela em 24/09/2026 para todas as empresas do escritório.
> As regras específicas desta empresa descritas acima **continuam valendo**. Este bloco completa o que faltar e **não substitui** nenhuma conta, exceção ou classificação já confirmada. Em caso de conflito, prevalece a regra específica da empresa.

### Parâmetros desta empresa

| Sócio | CPF | Pró-labore | Conta pró-labore a pagar | Conta do sócio (retirada / aporte) |
|---|---|---|---|---|
| Lucas Zen Ribeiro Pinto | 106.669.109-60 | Variável — perguntar todo mês — Fator R (última referência: R$ 2.000,00) | **188** (2.1.5.01.002) | **526** |

> Os itens "1. Provisão" e "2. INSS" acima vêm da folha do Domínio e **não** entram no TXT (item 9). O TXT registra só o item 3 (pagamento).

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
