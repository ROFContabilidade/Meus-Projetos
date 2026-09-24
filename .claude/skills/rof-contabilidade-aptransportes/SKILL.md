---
name: rof-contabilidade-aptransportes
description: "ADRIANA PINHEIRO TRANSPORTES LTDA — lançamentos contábeis e conciliação bancária no Domínio (Sicredi, Nu Financeira, C6Bank). Simples Nacional, transporte de cargas."
---

# ROF Contabilidade AP TRANSPORTES — Lançamentos Contábeis e Conciliação

## Dados da Empresa

| Campo | Informação |
|---|---|
| Razão social | ADRIANA PINHEIRO TRANSPORTES LTDA |
| Nome fantasia | AP TRANSPORTES |
| CNPJ | 46.293.830/0001-55 |
| CNPJ sem formatação | 46293830000155 |
| CNAE principal | 49.30-2-02 — Transporte rodoviário de carga, exceto produtos perigosos e mudanças, intermunicipal, interestadual e internacional |
| CNAEs secundários | 53.20-2-02 — Serviços de entrega rápida |
| Setor | Transporte de cargas e entregas |
| Regime tributário | Simples Nacional (desde 06/05/2022) |
| Banco(s) | Sicredi conta 05303-6 → cód. **8** · Nu Financeira conta 565964683-1 → cód. **6** · C6Bank conta 387674713 → cód. **32** |
| Cadastrado por | Rosangela |

## Sócios

| Sócio | CPF | Conta no Domínio |
|---|---|---|
| Adriana Pinheiro dos Santos | 027.837.139-69 | **554** (ativo — 1.2.2.04.001) |

## Regras de Trabalho (ACORDO COM A CONTADORA)

1. **Fidelidade total** aos dados enviados — não alterar nada sem consultar
2. **Consulta prévia** antes de qualquer alteração
3. **Base legal** sempre que sugerir algum ajuste
4. **Histórico**: copiar o texto exatamente como aparece no extrato bancário

## Leiaute do Arquivo TXT para Domínio

```
|0000|46293830000155|
|6000|X||||
|6100|DD/MM/AAAA|CONTA_DEBITO|CONTA_CREDITO|VALOR||HISTORICO||||
```

- **Pagamento (saída):** débito na conta de despesa/ativo, crédito no banco
- **Recebimento (entrada):** débito no banco, crédito na conta de receita/origem
- Arquivo único: pagamentos e recebimentos ordenados por data
- Valor com vírgula decimal: ex. 1500,00
- TXT Otimizza confirmado para **C6Bank (conta 32)**

## Plano de Contas — Contas Operacionais

| Cód | Classificação | Nome | Natureza |
|---|---|---|---|
| **5** | 1.1.1.01.001 | CAIXA GERAL | Ativo |
| **8** | 1.1.1.02.001 | BANCO DO SICREDI - CONTA 05303-6 | Ativo |
| **6** | 1.1.1.02.003 | NU FINANCEIRA S.A - CONTA 565964683-1 | Ativo |
| **32** | 1.1.1.02.004 | BANCO C6BANK - CONTA 387674713 | Ativo |
| **504** | 1.1.2.01.001 | CLIENTES DIVERSOS | Ativo |
| **55** | 1.1.5.01.001 | MERCADORIAS PARA REVENDA | Ativo |
| **58** | 1.1.5.01.004 | OUTROS MATERIAIS DE CONSUMO | Ativo |
| **554** | 1.2.2.04.001 | ADRIANA PINHEIRO DOS SANTOS (027.837.139-69) | Ativo |
| **152** | 2.1.1.01.001 | EMPRÉSTIMO SICREDI | Passivo |
| **174** | 2.1.1.01.002 | EMPRESTIMO NU FINANCEIRA S.A | Passivo |
| **506** | 2.1.3.01.001 | FORNECEDOR MODELO | Passivo |
| **479** | 2.1.4.01.015 | SIMPLES NACIONAL A RECOLHER | Passivo |
| **510** | 2.1.6.02.001 | HONORÁRIOS CONTÁBEIS | Passivo |
| **556** | 2.3.5.01.006 | DISTRIBUIÇÃO DE LUCROS | PL |
| **467** | 3.1.6.01.001 | CUSTOS DOS SERVIÇOS PRESTADOS | Resultado |
| **470** | 3.1.7.01.001 | CUSTOS DAS MERCADORIAS VENDIDAS | Resultado |
| **312** | 3.2.1.04.001 | FRETES E CARRETOS | Resultado |
| **313** | 3.2.1.04.002 | MANUTENÇÃO DE VEÍCULOS | Resultado |
| **553** | 3.2.1.04.003 | SERVIÇOS DE OPERAÇÃO | Resultado |
| **350** | 3.2.2.03.005 | TAXAS DIVERSAS | Resultado |
| **352** | 3.2.2.03.007 | MULTAS DE MORA | Resultado |
| **354** | 3.2.2.04.001 | ENERGIA ELÉTRICA | Resultado |
| **358** | 3.2.2.04.005 | SEGUROS | Resultado |
| **362** | 3.2.2.04.009 | SERVIÇOS PRESTADOS POR TERCEIROS | Resultado |
| **493** | 3.2.2.04.014 | MULTA DE TRÂNSITO | Resultado |
| **525** | 3.2.2.04.015 | DESPESAS DIVERSAS | Resultado |
| **579** | 3.2.2.04.017 | DESPESA COM CARTÃO DE CRÉDITO | Resultado |
| **521** | 3.2.2.04.018 | DESPESAS COM ALIMENTAÇÃO | Resultado |
| **372** | 3.2.2.05.005 | JUROS DE MORA | Resultado |
| **526** | 3.2.2.05.009 | TARIFAS BANCÁRIAS | Resultado |
| **546** | 3.2.2.05.010 | IOF | Resultado |
| **411** | 4.1.1.02.001 | SERVIÇOS PRESTADOS | Resultado |
| **480** | 4.1.2.03.008 | (-) SIMPLES NACIONAL | Resultado |

## Regra de Classificação das Contrapartes

### Para cada lançamento do extrato, siga esta ordem:

1. Identificar natureza (entrada / saída)
2. Identificar favorecido (nome, CNPJ/CPF)
3. Se tiver CNPJ → pesquisar na Receita Federal → verificar atividade → classificar conforme plano de contas
4. Se Pessoa Física (exceto sócia) → conta **525** (Despesas Diversas) salvo instrução contrária
5. Se sócia Adriana (CPF 027.837.139-69) → aplicar Regra de Retiradas abaixo
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

## Regra Inviolável — IOF e Encargos Bancários

> Nunca omitir IOF nem encargos bancários do TXT.

- **IOF** → conta **546** — lançar separadamente, mesmo valor pequeno
- **Juros de mora / mora excesso limite / juros cheque especial** → conta **372**
- **Multa excesso limite / multas bancárias** → conta **352**
- **Tarifas (cesta de relacionamento, integração capital subscrito)** → conta **526**
- **Devolução de juros** (entrada no banco) → débito banco, crédito **372** (estorno)

## Particularidades do C6Bank (conta 32)

O C6Bank utiliza **cheque especial**. Lançamentos automáticos frequentes:

| Descrição no extrato | Conta | D/C |
|---|---|---|
| IOF ADICIONAL PJ-CH. ESPE / IOF BASICO CH PJ | **546** | D |
| JUROS UTILIZ.CH.ESPECIAL / JUROS CHEQUE ESP | **372** | D |
| ENC EXCESSO LIMITE / MORA EXC CHEQUE ESP | **372** | D |
| MULTA EXC CHEQUE ESP | **352** | D |
| DEV JUROS CHQ ESP (devolução) | **372** | C (estorno) |

## Regra Mensal — Retiradas da Sócia

> **Não há pró-labore.** Toda retirada vai direto para retirada de sócio.
> ANTES DE LANÇAR qualquer pagamento à Adriana: confirmar com a contadora o total pago no mês.

| Tipo de movimento | Débito | Crédito |
|---|---|---|
| Pagamento à Adriana (saída do banco) | **554** | banco |
| Recebimento da Adriana (entrada no banco) | banco | **554** |

- Histórico: copiar exatamente o texto do extrato
- Incluir nº + nome + CPF nos lançamentos de retirada conforme padrão do Domínio

## Regra — Devolução / Aporte da Sócia

Quando a Adriana deposita valores **na empresa** (entrada no extrato):

| Débito | Crédito |
|---|---|
| banco | **554** — Adriana Pinheiro dos Santos |

## Regra Inviolável — Planilha de Retiradas de Sócio

> **Sempre que gerar o TXT para o Domínio, gerar também a planilha XLSX de retiradas de sócio do mesmo período.**
> Os dois arquivos são entregues juntos — o TXT nunca é entregue sozinho.

**Estrutura da planilha:**
- Cabeçalho: Razão social + período de referência + nome e conta da sócia
- Colunas: Data · Banco · Cód. conta bancária · Tipo (Retirada / Aporte) · Histórico · Valor (R$)
- Linhas em destaque (cor diferenciada) para aportes/devoluções da sócia
- Subtotal retiradas, subtotal aportes e **saldo líquido do mês**
- Nota de rodapé quando o extrato de algum banco for parcial (período incompleto)
- Formato do valor: moeda BRL com duas casas decimais
- Retiradas = valor negativo; aportes = valor positivo (para cálculo do saldo líquido)

## Classificações Recorrentes Confirmadas

| Fornecedor / Descrição | CNPJ / CPF | Conta | Observação |
|---|---|---|---|
| Irmãos Muffato Cia Ltda | 76430438000171 | **504** | Recebimento (cliente principal) |
| COPEL Distribuição | 04368898000106 | **354** | Energia elétrica — débito em convênio |
| Paes e Bastos Contabilidade | 29650531000101 | **510** | Honorários contábeis |
| Auto Posto Pelanda / Pedro Pelanda / Juliane Pellanda (boleto) | vários | **467** | Custo dos serviços prestados (combustível) |
| Auto Postos — compras via Caixa (NF mercadoria) | vários | **55** | Mercadorias para revenda |
| Peças e materiais de consumo via Caixa | vários | **58** | Outros materiais de consumo |
| Cartão de crédito — C G E G CURITIBA | 81466286000105 | **579** | Fatura cartão |
| Zonta Administradora | — | **579** | Fatura cartão |
| Nu Pagamentos S/A | 18236120000158 | **525** | Verificar se cartão ou empréstimo |
| Santander / Banco Votorantim | vários | **525** | Despesas diversas — verificar contexto |
| Débito de arrecadação (DAS / guias) | — | **350** | Taxas diversas |
| Multa de trânsito | — | **493** | Multa de trânsito |
| Seguro | — | **358** | Seguros |
| Empréstimo Sicredi (parcela) | — | **152** | Liquidação de parcela |
| Empréstimo Nu Financeira (parcela) | — | **174** | Liquidação de parcela |
| Adriana Pinheiro dos Santos — saída | 027.837.139-69 | **554** | Retirada de sócio |
| Adriana Pinheiro dos Santos — entrada | 027.837.139-69 | **554** | Devolução / aporte |

## Fluxo de Trabalho

1. Receber extrato bancário (PDF, CSV ou OFX) + identificar qual banco (Sicredi/Nu/C6)
2. Para cada lançamento: identificar natureza → favorecido → classificar → registrar histórico exato
3. Sinalizar lançamentos não identificados para revisão com a contadora
4. Verificar IOF, juros e encargos do cheque especial (especialmente C6Bank)
5. Verificar retiradas da Adriana e confirmar total do mês com a contadora
6. Conferir saldo: entradas − saídas = variação do extrato
7. Gerar TXT único ordenado por data
8. **Gerar planilha XLSX de retiradas de sócio do mesmo período (entrega obrigatória junto com o TXT)**

## Pendências a Confirmar com a Contadora

- Classificação definitiva de Nu Pagamentos S/A e Santander (cartão de crédito ou empréstimo) — confirmar conta correta
- Adiantamento de clientes (cód. 569, saldo R$ 182.569,45) — confirmar origem e tratamento
- Verificar se há IRRF retido em algum recebimento

---

## Padrão ROF — Pró-labore, Retiradas e Relatório do Sócio

> Regra validada pela contadora Rosangela em 24/09/2026 para todas as empresas do escritório.
> As regras específicas desta empresa descritas acima **continuam valendo**. Este bloco completa o que faltar e **não substitui** nenhuma conta, exceção ou classificação já confirmada. Em caso de conflito, prevalece a regra específica da empresa.

### Parâmetros desta empresa

| Sócio | CPF | Pró-labore | Conta pró-labore a pagar | Conta do sócio (retirada / aporte) |
|---|---|---|---|---|
| Adriana Pinheiro dos Santos | 027.837.139-69 | **Não há** | — | **554** |

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
