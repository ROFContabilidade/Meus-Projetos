---
name: rof-contabilidade-fwsgoncalves
description: Conciliação bancária, classificação contábil e geração de TXT no leiaute Domínio para a F W S GONCALVES LTDA (Simples Nacional), CNPJ 22.147.527/0001-86, fabricante/montadora/comércio de móveis. Usar automaticamente quando o usuário enviar extratos, relatórios, razões, plano de contas ou pedir lançamentos, conferência de favorecidos, conciliação entre Sicredi, SicrediInvest e poupança, ou arquivo TXT dessa empresa.
---

# ROF Contabilidade — F W S GONCALVES LTDA

## Dados da Empresa

| Campo             | Valor                                           |
|-------------------|-------------------------------------------------|
| Razão Social      | F W S GONCALVES LTDA                            |
| Nome Fantasia     | Art&Stilo Móveis Sob Medida                     |
| CNPJ              | 22147527000186                                  |
| CNPJ formatado    | 22.147.527/0001-86                              |
| Regime Tributário | Simples Nacional (optante desde 29/03/2015; confirmado por Elen em 24/09/2026) |

**CNAEs:**
- 3101-2/00 — Fabricação de móveis com predominância de madeira *(principal)*
- 3329-5/01 — Serviços de montagem de móveis de qualquer material
- 4754-7/01 — Comércio varejista de móveis

**Sócio:** Fernando Willian dos Santos Gonçalves — CPF 036.587.709-37

**Ativar esta skill** ao identificar: **F W S GONCALVES LTDA**, **F W GONCALVES LTDA**, **22.147.527/0001-86**, **22147527000186**, **Art&Stilo Móveis Sob Medida**, conta Sicredi cooperativa 0730/52431-6, ou arquivos com `Fwsgoncalves`. Não misturar dados, contas ou históricos de outras empresas.

---

## Contas Bancárias e Financeiras

| Banco / Produto                          | Código contábil | Natureza                   | Status         |
|------------------------------------------|----------------:|----------------------------|----------------|
| Sicredi Cooperativa 0730 — CC 52431-6   | **14**          | Banco conta movimento      | Atual — usar   |
| Sicredi — Poupança Tradicional 52431-6  | **167**         | Poupança                   | Atual — usar   |
| Sicredi — SicrediInvest CDI100 (título 8521501414-1) | **71** | Aplicação financeira   | Atual — usar   |
| Bradesco — CC 0256506-4                 | **8**           | Banco conta movimento      | Histórico — não usar em operações atuais sem documento |
| Bradesco — Aplicação CBD                | **48**          | Aplicação financeira       | Histórico       |
| Bradesco — Título de capitalização      | **558**         | Aplicação/título           | Histórico       |

---

## Plano de Contas — Principais Contas Operacionais

| Código | Classificação      | Nome                                              |
|-------:|--------------------|---------------------------------------------------|
| 14     | 1.1.1.02.003       | Banco Sicredi 0730 52431-6                        |
| 71     | 1.1.4.01.003       | Aplicação SicrediInvest                           |
| 167    | 1.1.4.01.004       | Poupança Tradicional Sicredi                      |
| 188    | 2.1.5.01.002       | Pró-labore a pagar                                |
| 191    | 2.1.5.02.001       | INSS a recolher                                   |
| 275    | 3.1.1.02.002       | Pró-labore (despesa)                              |
| 356    | 3.2.2.04.003       | Telefone/Internet                                 |
| 357    | 3.2.2.04.004       | Material de construção                            |
| 362    | 3.2.2.04.009       | Serviços Prestados por Terceiros                  |
| 364    | 3.2.2.04.011       | Despesa com deslocamento                          |
| 366    | 3.2.2.04.013       | Sistema/software                                  |
| 369    | 3.2.2.05.002       | Despesas bancárias                                |
| 371    | 3.2.2.05.005       | Tarifas bancárias                                 |
| 432    | 4.1.3.01.001       | Juros de aplicações                               |
| 470    | 3.1.7.01.001       | Custos das mercadorias vendidas                   |
| 479    | 2.1.4.01.015       | Simples Nacional a recolher                       |
| 493    | 3.2.2.04.014       | Despesas diversas                                 |
| 504    | 1.1.2.01.001       | Clientes diversos                                 |
| 506    | 2.1.3.01.001       | Fornecedor modelo                                 |
| 510    | 2.1.6.02.001       | Honorários contábeis                              |
| 521    | 3.2.2.04.016       | Despesas com alimentação                          |
| 541    | 1.2.2.04.001       | Fernando Willian dos Santos Gonçalves (036.587.709-37) |
| 586    | 3.2.2.05.010       | IRRF sobre aplicação                              |
| 590    | 3.2.2.04.019       | Bens de pequeno valor (criada no Domínio em 09/2026, cadastro 01/01/2026) |

> As contas **362** e **541** foram confirmadas no razão e reconhecidas no Domínio. Se o plano exportado não exibir uma delas, confrontar com o razão e registrar a divergência — não declarar inexistência.

---

## Leiaute do Arquivo TXT para Domínio

```
|0000|22147527000186|
|6000|X||||
|6100|DD/MM/AAAA|CONTA_DEBITO|CONTA_CREDITO|VALOR||HISTORICO||||
```

- **Um `|6000|X||||` por lançamento** — um por cada linha `|6100|`
- O campo tipo deve ser literalmente a letra **X**
- Valor: vírgula decimal, duas casas, sem símbolo `R$` — exemplo: `1500,00`
- Pagamento (saída): débito na conta de despesa/passivo/ativo e crédito no banco
- Recebimento (entrada): débito no banco e crédito na conta 504
- **Arquivo único:** pagamentos e recebimentos juntos, em ordem cronológica
- **Partida com dois débitos e um crédito:** representar cada relação em uma linha `|6100|` separada

---

## Regra Obrigatória — Conciliação Integrada das Três Frentes Sicredi

Em toda competência, analisar conjuntamente as três frentes:

| Frente               | Produto / conta                              | Código | Conferência obrigatória                                      |
|----------------------|----------------------------------------------|-------:|--------------------------------------------------------------|
| Movimentação diária  | Sicredi corrente, cooperativa 0730/52431-6   | **14** | Entradas, saídas, saldo inicial e saldo final                |
| Aplicação            | SicrediInvest CDI100, título 8521501414-1    | **71** | Aportes, resgates, rendimentos, IRRF, saldo e posição        |
| Poupança             | Poupança Tradicional Sicredi, conta 52431-6  | **167**| Aplicações, resgates, capitalizações, IRRF, saldo e posição  |

Não concluir a conciliação apenas pelo extrato da conta 14. Confrontar saldo inicial, saldo final, aportes, resgates, transferências, rendimentos e IRRF entre as três frentes e seus razões. Não incluir lançamentos de meses fora da competência no TXT; registrar que ficaram para o período correto.

**Referência agosto/2026:** conta corrente saldo 31/07 R$ 83.940,33 → 31/08 R$ 15.564,00 (fechou). Poupança 401,53 → 503,10 (aplicação 100,00; rendimentos 1,51 + 0,52; IRRF 0,46 em 11/08). SicrediInvest sem movimento, R$ 29.640,69. Recebimentos via Barte Brasil são repasses de vendas no cartão (links de pagamento) → 504. Atenção: no PDF do extrato Sicredi as colunas saem desalinhadas — usar o OFX como fonte dos lançamentos e o PDF para os saldos.

**Referência julho/2026:** SicrediInvest permaneceu com saldo de R$ 29.640,69 sem movimentação. Poupança: aplicação de R$ 100,00, rendimentos de R$ 1,51 e R$ 0,47 e IRRF de R$ 0,45 em 10/07.

---

## Regras Especiais — Sócio (Fernando Willian dos Santos Gonçalves)

**Salário mínimo 2026: R$ 1.621,00 | INSS 11%: R$ 178,31 | Pró-labore líquido: R$ 1.442,69**

### Saída em nome do sócio (empresa paga para ele)

Acumular cronologicamente todos os pagamentos do mês (todos os bancos):

1. Enquanto o acumulado **não atingir R$ 1.442,69** → **D-188 / C-Banco**
2. Quando o acumulado **ultrapassar R$ 1.442,69**:
   - Parcela que completa o limite → **D-188 / C-Banco**
   - Excedente → **D-541 / C-Banco**
3. Pagamentos subsequentes no mesmo mês → **D-541 / C-Banco**

**Se uma operação individual ultrapassar o limite:** gerar duas linhas `|6100|` na mesma data, ambas creditando o banco, somando o valor total. Exemplo para R$ 6.750,00: D-188 R$ 1.442,69 + D-541 R$ 5.307,31, ambas C-14.

**Se a contadora informar pró-labore variável:** lançar conforme orientação expressa, sem aplicar o rateio padrão automaticamente.

> Não classificar pagamentos ao sócio nas contas 362 ou 506.

---

## Regras de Classificação de Pagamentos

### Recebimentos
- **Todos os recebimentos:** D-14 / C-504 — salvo orientação posterior expressa da contadora.

### Pessoa Física (exceto sócio)
- Qualquer pagamento a pessoa física não sócia → **conta 362** (Serviços Prestados por Terceiros)

### Aplicações e Rendimentos

| Evento                                        | Lançamento                |
|-----------------------------------------------|---------------------------|
| Transferência CC → Poupança                   | D-167 / C-14              |
| Rendimentos de poupança (confirmados)         | D-167 / C-432             |
| IRRF sobre rendimentos de poupança            | D-586 / C-167             |
| Resgate de poupança → CC                      | D-14 / C-167              |
| Aporte SicrediInvest                          | D-71 / C-14               |
| Resgate SicrediInvest                         | D-14 / C-71               |
| Rendimentos SicrediInvest (confirmados)       | D-71 / C-432              |
| IRRF sobre SicrediInvest                      | D-586 / C-71              |

> Não incluir movimentos de aplicação apenas por estimativa ou saldo. Confrontar PDF, razão e razão de importação. Distinguir provisão de crédito efetivo.

### Validação de Favorecidos

Para cada operação, formular antes da classificação:
- **"Foi feito um pagamento de R$ X, na data DD/MM/AAAA, para [favorecido]"**
- **"Foi recebido R$ X, na data DD/MM/AAAA, de [favorecido]"**

Classificar cada item como `CONFIRMADO`, `PROVÁVEL`, `NÃO CRUZADO` ou `DIVERGENTE`. Não incluir item incerto no TXT definitivo sem autorização. Quando não houver histórico suficiente, pesquisar CNPJ em fontes públicas como evidência auxiliar — não substitui nota fiscal, contrato ou orientação da contadora.

> Não classificar toda pessoa jurídica como fornecedor. A conta **506** só é usada quando o favorecido fornecer produtos/insumos/serviços coerentes com fabricação, montagem ou comércio de móveis.

---

## Classificações Recorrentes Validadas

| Operação / Favorecido                                  | Conta |
|--------------------------------------------------------|------:|
| Todos os recebimentos                                  | 504   |
| Clinipam (com nota fiscal)                             | 506   |
| San Luan / São João Ferragens                          | 506   |
| Materiais Elétricos                                    | 506   |
| Rudegon                                                | 506   |
| GMAD Curitiba                                          | 506   |
| Indústria e Comércio de Móveis Mara                    | 506   |
| Casa do MDF e Ferragens                                | 506   |
| Dinabox — automação/sistema (conforme nota fiscal)     | 506   |
| P.J. Gasparin / Geração Centerlar — material de construção | 506 |
| Tecplast — aguardar nota fiscal para definir natureza  | —     |
| Paes e Bastos — honorários contábeis                   | 510   |
| Servopa — consórcio (histórico anterior coerente)      | 113   |
| TIM — telefonia                                        | 356   |
| Supermercado Quintetto                                 | 521   |
| Receita Federal — 14/07/2026, R$ 1.402,93             | 479   |
| Integralização de R$ 20,00                             | 369   |
| Cesta de relacionamento                                | 369   |
| Teck Plast / Unipar Ind. e Com. de Embalagens (CNPJ 11.191.719/0001-73) | 506 |
| Bigfer Ind. e Com. de Ferragens                        | 506   |
| Indusflex Comércio de Ferramentas                      | 506   |
| JKB Comércio de Ferragens e Ferramentas                | 506   |
| Materiais Elétricos Zé (NF emitida por Zetta Distrib. Materiais Elétricos) | 506 |
| R L de Castro / Compensados Colombo (CNPJ 81.254.906/0001-34) | 506 |
| R R Leo Comércio de Madeiras — custo (validado por Elen, 08/2026) | 470 |
| Connectamais / Singular Soluções em Tecnologia — suporte de TI | 366 |
| Moviar Ar Condicionados — bens de pequeno valor (validado por Elen, 08/2026) | 590 |
| DAS Simples Nacional pago via PIX à Receita Federal     | 479   |
| INSS pago via PIX à Receita Federal (pró-labore R$ 178,31 e outras guias de INSS) | 191 |

> **INSS em atraso:** DARF código 1099 (CP segurado contribuinte individual 11%). Ex.: 20/08/2026, R$ 198,33 = PA 06/2026, principal 178,31 + multa 18,24 + juros 1,78 (comprovante de arrecadação e-CAC nº 07162623215870377). Lançado integralmente na 191 em 08/2026; confirmar com a contadora se multa/juros devem ir para conta de despesa.

> **Pagamento a fornecedor maior que a NF do mês** (orientação de Elen, 08/2026): valor da NF → **506**; excedente sem nota → **470** (custo). Ex.: Rudegon 26/08/2026 — NF 588713 R$ 7.952,35 na 506, R$ 1.428,54 + R$ 750,00 na 470.

> As classificações recorrentes não substituem a verificação dos documentos do período. Orientação nova da contadora prevalece e deve ser registrada.

---

## Fluxo de Trabalho por Competência

1. Confirmar empresa, CNPJ, período de competência e banco/produto.
2. Inventariar extrato corrente, SicrediInvest, poupança, plano, razões, relatórios e modelos TXT.
3. Reconciliar saldos e movimentos das três frentes Sicredi.
4. Para cada operação, redigir a frase objetiva de pagamento/recebimento.
5. Cruzar com documentos, plano e razão; pesquisar favorecidos quando necessário.
6. Aplicar as regras do sócio, das aplicações e das classificações recorrentes.
7. Separar confirmados, prováveis, não cruzados e divergentes; perguntar pendências antes de prosseguir.
8. Gerar TXT único apenas com classificações confirmadas — ou marcar expressamente como prévia.
9. Auditar cabeçalho, separadores, campos, datas, valores, contas, históricos, ordem, partida dobrada, saldos e exclusão de meses fora da competência.

---

## Observações Gerais

- Não inventar dados, documentos, contas, históricos ou vínculos.
- Não copiar automaticamente o histórico do extrato quando houver fonte contábil melhor (razão, nota fiscal, relatório).
- Não misturar contas do Bradesco histórico com o Sicredi atual.
- Não tratar ausência de conta em cópia do plano exportado como inexistência quando o razão ou o Domínio comprovam a conta.
- Não declarar aceitação funcional do TXT sem teste no Domínio — distinguir validação estática de importação efetiva.
- Cada empresa deve ser trabalhada em conversa separada.
- A referência detalhada e os achados documentais estão em `references/fwsgoncalves_reference.md`.

---

## Padrão ROF — Pró-labore, Retiradas e Relatório do Sócio

> Regra validada pela contadora Rosangela em 24/09/2026 para todas as empresas do escritório.
> As regras específicas desta empresa descritas acima **continuam valendo**. Este bloco completa o que faltar e **não substitui** nenhuma conta, exceção ou classificação já confirmada. Em caso de conflito, prevalece a regra específica da empresa.

### Parâmetros desta empresa

| Sócio | CPF | Pró-labore | Conta pró-labore a pagar | Conta do sócio (retirada / aporte) |
|---|---|---|---|---|
| Fernando Willian dos Santos Gonçalves | 036.587.709-37 | Variável — perguntar todo mês | **188** | **541** |

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
