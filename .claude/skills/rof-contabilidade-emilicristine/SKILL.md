---
name: rof-contabilidade-emilicristine
description: "EMILI CRISTINE DE LIMA LTDA, CNPJ 55.436.584/0001-34, Simples Nacional, marketing e representação comercial (prestação de serviço), bancos: Nubank (8) e Mercado Pago (9). Use quando Rosangela ou Elen enviarem extrato, plano de contas, razão ou pedirem lançamentos/conciliação/TXT Domínio desta empresa."
---

# ROF Contabilidade EMILI CRISTINE DE LIMA — Lançamentos Contábeis e Conciliação

## Dados da Empresa

| Campo | Informação |
|---|---|
| Razão social | EMILI CRISTINE DE LIMA LTDA |
| CNPJ | 55.436.584/0001-34 |
| CNPJ sem formatação | 55436584000134 |
| CNAE principal | 7319-0/03 — Marketing direto |
| CNAEs secundários | 7319-0/02 Promoção de vendas; 7319-0/04 Consultoria em publicidade; 7319-0/99 Outras atividades de publicidade; 4616-8/00, 4618-4/01, 4619-2/00 Representantes comerciais; 4759-8/99, 4772-5/00, 4781-4/00, 4789-0/01, 4789-0/99 Comércio varejista diversos |
| Setor | Marketing e representação comercial — prestação de serviço |
| Regime tributário | Simples Nacional |
| Banco(s) | NU PAGAMENTOS (Nubank) → conta 8 · BANCO MERCADO PAGO → conta 9 |
| Endereço | Rua Luciano Floriano dos Santos, 71 — São Dimas, Colombo/PR — CEP 83411-170 |
| Abertura | 07/06/2024 |
| Cadastrado por | Rosangela |

> **Análises e classificações são feitas exclusivamente pelas contadoras Rosangela e Elen.** Renata Bastos (CRC-PR PR075217/O-2) aparece apenas como contadora registrada que assina os relatórios do sistema Domínio (licenciado para PAES E BASTOS CONTABILIDADE LTDA) — não valida classificações desta empresa.

## Sócia

| Sócia | CPF | Conta no Domínio |
|---|---|---|
| Emili Cristiana de Lima | 105.905.719-07 | **527** (1.2.2.04.001 — Sócios/Ativo — retiradas) |

- Sócia-Administradora única. Sem funcionários CLT.

## Regras de Trabalho (ACORDO COM A CONTADORA)

1. **Fidelidade total** aos dados enviados — não alterar nada sem consultar
2. **Consulta prévia** antes de qualquer alteração
3. **Base legal** sempre que sugerir algum ajuste
4. **Histórico**: copiar o texto exatamente como aparece no extrato bancário

## Leiaute do Arquivo TXT para Domínio

Confirmado pelos TXT do Otimizza já aceitos:

```
|0000|55436584000134|
|6000|X||||
|6100|DD/MM/AAAA|CONTA_DEBITO|CONTA_CREDITO|VALOR||HISTORICO||||
```

- **Pagamento (saída):** débito na conta de despesa/ativo/passivo, crédito no banco (8 ou 9)
- **Recebimento (entrada):** débito no banco (8 ou 9), crédito na conta de receita/cliente
- Antes de cada `|6100|` vai uma linha `|6000|X||||`
- Contas usadas são os **códigos reduzidos** do plano (ex.: 8, 9, 504, 527, 479...)
- Valor com vírgula decimal: ex. 11380,18
- **ARQUIVO ÚNICO POR MÊS (REGRA FIXA):** toda a movimentação de **todos os bancos/carteiras** vai num **único TXT**, pagamentos e recebimentos **ordenados por data**. **Nunca separar por banco.** Mesmo quando os extratos chegarem em arquivos distintos (Nubank, Mercado Pago, arquivos PAGAR/RECEBER do Otimizza), consolidar tudo em um só arquivo mensal.

## Plano de Contas — Contas Operacionais (códigos reduzidos)

| Cód | Classificação | Nome | Natureza |
|---|---|---|---|
| 5 | 1.1.1.01.001 | Caixa Geral | Ativo |
| **8** | 1.1.1.02.001 | NU PAGAMENTOS S.A - CONTA 687857088-6 | Ativo (Banco) |
| **9** | 1.1.1.02.002 | BANCO MERCADO PAGO - CONTA 43785213334 | Ativo (Banco) |
| **504** | 1.1.2.01.001 | Clientes Diversos | Ativo |
| 538 | 1.2.2.01.001 | Empréstimos de Sócios | Ativo |
| **527** | 1.2.2.04.001 | Emili Cristiana de Lima (105.905.719-07) | Ativo (Sócia) |
| 539 | 2.1.1.01.002 | Empréstimo Mercado Pago | Passivo |
| **506** | 2.1.3.01.001 | Fornecedor Modelo | Passivo |
| **479** | 2.1.4.01.015 | Simples Nacional a Recolher | Passivo |
| 490 | 2.1.4.01.022 | Parcelamento Simples Nacional - 1 | Passivo |
| 491 | 2.1.4.01.023 | (-) Encargos Parcelamento Simples Nacional | Passivo |
| 512 | 2.1.4.01.025 | ICMS Antecipado a Recolher | Passivo |
| **188** | 2.1.5.01.002 | Pró-labore a Pagar | Passivo |
| **191** | 2.1.5.02.001 | INSS a Recolher | Passivo |
| 537 | 2.1.6.01.xxx | Adiantamento de Clientes | Passivo |
| 510 | 2.1.6.02.001 | Honorários Contábeis | Passivo |
| 528 | 2.3.5.01.006 | Distribuição de Lucros | PL |
| 533 | 3.1.3.01.002 | Pró-labore (custo) | Resultado |
| 531 | 3.1.7.01.001 | ICMS Antecipação Total | Resultado |
| 352 | 3.2.2.03.007 | Multas de Mora | Resultado |
| **356** | 3.2.2.04.003 | Telefone | Resultado |
| **357** | 3.2.2.04.004 | Aluguéis | Resultado |
| 359 | 3.2.2.04.006 | Despesas Administrativas | Resultado |
| 361 | 3.2.2.04.008 | Assistência Contábil | Resultado |
| **362** | 3.2.2.04.— (a confirmar) | Serviços Prestados por Terceiros | Resultado |
| **493** | 3.2.2.04.014 | Despesas Diversas | Resultado |
| 58 | 3.2.2.04.015 | Outros Materiais de Consumo | Resultado |
| 375 | 3.2.2.05.008 | Encargos de Parcelamento | Resultado |
| 411 | 4.1.1.02.001 | Serviços Prestados (receita) | Receita |
| 480 | 4.1.2.03.008 | (-) Simples Nacional | Dedução |

## Regra de Classificação das Contrapartes

### Para cada lançamento do extrato, siga esta ordem:

1. Identificar natureza (entrada / saída) e o banco de origem (8 = Nubank, 9 = Mercado Pago)
2. Identificar favorecido (nome, CNPJ/CPF)
3. Se tiver CNPJ → pesquisar na Receita Federal → verificar atividade → classificar conforme plano de contas
4. Se Pessoa Física (exceto a sócia) → tratar como despesa/receita conforme natureza (padrão: 493 Despesas Diversas quando saída não identificada, salvo classificação já confirmada abaixo)
5. Se a sócia Emili Cristine → aplicar Regra Mensal de Retiradas (pró-labore 188 + excedente 527)
6. Histórico: copiar exatamente como aparece no extrato

## Regra Inviolável — Conferência de Saldo

> Nunca entregar o TXT sem que os saldos do extrato estejam fechando.

1. Saldo anterior (abertura) informado no extrato
2. Saldo final (encerramento) informado no extrato
3. Diferença esperada = Saldo final − Saldo anterior
4. Somar todas as entradas lançadas no TXT
5. Somar todas as saídas lançadas no TXT
6. Diferença apurada = Total entradas − Total saídas

Se Diferença apurada ≠ Diferença esperada → NÃO entregar o TXT. (Conferir cada banco/carteira contra seu próprio saldo antes de consolidar no arquivo único.)

**Verificação no código:**
- Entrada no banco = banco é DEBITADO (`deb == banco`)
- Saída do banco = banco é CREDITADO (`cred == banco`)

## Regra Inviolável — Aplicações Financeiras e Rendimentos

> Nunca omitir movimentações de aplicação financeira do TXT.

Esta empresa **não possui aplicação financeira cadastrada** até o momento. Se surgir rendimento/resgate em Nubank ou Mercado Pago, sinalizar para a contadora antes de lançar.

## Regra Inviolável — Tributos, IOF e IRRF

> Nunca omitir tributos, IOF nem IRRF do TXT.

- **DAS-Simples Nacional** → **479** (Simples Nacional a Recolher)
- **DARF referente ao INSS do pró-labore** (valor = base × 11%; hoje R$ 178,31) → **191** (INSS a Recolher). *Não usar 479 para o INSS do pró-labore.*
- O INSS pró-labore pode não ocorrer em todos os meses — se não houver DARF no extrato, não há lançamento.
- Outros DARF de natureza diferente → sinalizar para a contadora definir a conta.
- Não há conta específica de IOF/IRRF cadastrada. Se aparecer no extrato, **sinalizar para a contadora** definir a conta antes de gerar o TXT — nunca omitir por valor pequeno.

## Regra Mensal — Retiradas da Sócia e Pró-labore (SEGREGAR SEMPRE)

> ANTES DE LANÇAR qualquer pagamento à sócia: confirmar com a contadora o total pago no mês.

**Pró-labore base: salário mínimo nacional vigente — R$ 1.621,00 (2026). Atualizar sempre que o salário mínimo for reajustado.**

| Cálculo | Fórmula | Valor |
|---|---|---|
| Base | Salário mínimo nacional vigente | R$ 1.621,00 |
| INSS (11%) | Base × 11% | R$ 178,31 |
| Pró-labore líquido | Base − INSS | R$ 1.442,69 |

**Regra de lançamento das retiradas (padrão da skill — SEGREGAR pró-labore do excedente):**

| Situação | Débito | Crédito |
|---|---|---|
| Até o pró-labore líquido do mês (R$ 1.442,69) | **188** Pró-labore a Pagar | banco (8 ou 9) |
| Valor excedente ao pró-labore líquido | **527** Retirada de sócia | banco (8 ou 9) |
| INSS do pró-labore pago via DARF (R$ 178,31) | **191** INSS a Recolher | banco (8 ou 9) |

- Aplicar sobre o **total de retiradas do mês**: a primeira parcela de R$ 1.442,69 é pró-labore (188); todo o restante é retirada de sócia (527).
- Se a primeira retirada do mês já exceder R$ 1.442,69, **dividir essa linha em duas** no TXT: uma de R$ 1.442,69 → 188 (histórico "REF. AO PAGAMENTO DE PRO-LABORE ...") e o restante → 527 (mantendo o histórico do extrato). O total do banco não muda e o saldo continua fechando.

## Regra — Devolução / Aporte da Sócia

Quando a sócia deposita valores **na empresa** (entrada no extrato):

| Débito | Crédito |
|---|---|
| banco (8 ou 9) | **527** |

Reduz o saldo devedor da sócia. (Ex. confirmado no razão: transferência recebida da Emili Cristine → crédito em 527.)

## Particularidades dos Bancos

- **Nubank (8)** e **Mercado Pago (9)** são bancos digitais comuns. Sem reserva/liberação (não são intermediários de marketplace nesta conta).
- Tarifas/cobranças diversas de conta (ex.: pagamento Cora, PIX a terceiros não identificados) → **493 Despesas Diversas**, salvo identificação específica.
- Recebimentos de plataformas (marketplace/afiliados) caem como receita de clientes → **504**.

## Classificações Recorrentes Confirmadas

| Fornecedor / Descrição no extrato | Natureza | Conta |
|---|---|---|
| EBAZAR.COM.BR (Mercado Livre) | Recebimento | **504** |
| KIWIFY PAGAMENTOS | Recebimento | **504** |
| SHPP BRASIL (CNPJ 38.372.267/0001-82) | Recebimento | **504** |
| MAREE INSTITUICAO DE PAGAMENTO (CNPJ 38.372.267/0001-82 — mesmo grupo do SHPP) | Recebimento | **504** |
| BOTICARIO PRODUTOS DE BELEZA | Recebimento | **504** |
| AMAZON SERVICOS DE VAREJO | Recebimento | **504** |
| "Dinheiro recebido FIXOS / CASHBACKS AFILIADOS" | Recebimento | **504** |
| PIX Emili Cristine de Lima (enviado) | Saída | **188** até R$ 1.442,69 / **527** excedente (ver Regra Mensal) |
| PIX / transferência recebida da Emili Cristine | Entrada | **527** (devolução) |
| PAES E BASTOS CONTABILIDADE | Saída | **510** Honorários Contábeis |
| RBA CONTABILIDADE LTDA | Saída | **510** Honorários Contábeis |
| DAS-SIMPLES NACIONAL / PIX RECEITA FEDERAL (DAS) | Saída | **479** |
| RECEITA FED-DARF = INSS pró-labore (R$ 178,31) | Saída | **191** INSS a Recolher |
| CLARO MOVEL | Saída | **356** Telefone |
| Boleto aluguel (ex.: "GRPQA") | Saída | **357** Aluguéis |
| 53.274.851 SERGIO DA CRUZ (CNPJ 53.274.851/0001-99 — comércio varejista, Colombo/PR) | Saída | **506** Fornecedor Modelo |
| 20.870.703 DAIANE RAMOS BARBOSA (CNPJ 20.870.703/0001-88) | Saída | **506** Fornecedor Modelo |
| GISELLE CRISTINA MICHEL (PF) | Saída | **362** Serviços Prestados por Terceiros |
| L.A. FISIO LTDA (CNPJ 53.962.929/0001-68 — fisioterapia) | Saída | **493** Despesas Diversas |
| ITALO SUPERMERCADOS LTDA / FESTVAL (supermercados) | Saída | **493** Despesas Diversas |
| MERCADO PAGO IP (PIX enviado / tarifa) | Saída | **493** Despesas Diversas |
| CORA (pagamento de conta) | Saída | **493** Despesas Diversas |
| PIX enviado a terceiro PF não identificado (ex.: Eduardo Heimart) | Saída | **493** Despesas Diversas |
| POSTO SORRISO / postos de combustível | Saída | **493** Despesas Diversas |
| "Aprovação de crédito em parcelas fixas empréstimos" | Entrada | **539** Empréstimo Mercado Pago |

## Entrega Mensal Padrão (SEMPRE)

Todo fechamento mensal entrega, **sempre juntos**:

1. **TXT único** com toda a movimentação do mês (todos os bancos, ordenado por data), no leiaute Domínio acima.
2. **Relatório de Retiradas de Sócio** (conta 527), em **Excel**, detalhando: retiradas (saídas), devoluções/aportes (entradas), retirada líquida do mês e pró-labore pago (conta 188). Gerar automaticamente junto com o TXT, sem precisar pedir.

## Fluxo de Trabalho

1. Receber extratos (TXT Otimizza / PDF / CSV / OFX) e, se houver, plano de contas atualizado
2. Para cada lançamento: identificar natureza → banco (8/9) → favorecido → classificar → registrar histórico exato
3. Sinalizar lançamentos não identificados para revisão da contadora
4. Aplicar a Regra Mensal de Retiradas (segregar pró-labore 188 / excedente 527) e verificar INSS (191), tributos, IOF/IRRF e empréstimos
5. Conferir saldo de cada banco: entradas − saídas = variação do extrato (regra inviolável)
6. Gerar **TXT único** com toda a movimentação do mês (todos os bancos juntos), ordenado por data
7. Gerar **sempre** o Relatório de Retiradas de Sócio (Excel) junto com o TXT

## Pendências a Confirmar com a Contadora

- Confirmar a classificação completa (sub-conta) da conta **362** Serviços Prestados por Terceiros no plano do Domínio
- Conta específica para IOF/IRRF caso passem a ocorrer (hoje inexistente no plano)
- Atualizar salário mínimo vigente a cada reajuste anual (impacta pró-labore líquido e INSS)

---

## Padrão ROF — Pró-labore, Retiradas e Relatório do Sócio

> Regra validada pela contadora Rosangela em 24/09/2026 para todas as empresas do escritório.
> As regras específicas desta empresa descritas acima **continuam valendo**. Este bloco completa o que faltar e **não substitui** nenhuma conta, exceção ou classificação já confirmada. Em caso de conflito, prevalece a regra específica da empresa.

### Parâmetros desta empresa

| Sócio | CPF | Pró-labore | Conta pró-labore a pagar | Conta do sócio (retirada / aporte) |
|---|---|---|---|---|
| Emili Cristine de Lima | 105.905.719-07 | Variável — perguntar todo mês | **188** | **527** |

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
