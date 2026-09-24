---
name: rof-contabilidade-paiefilhos
description: "PAI E FILHOS LTDA (Metalúrgica Pai e Filhos), CNPJ 54.239.093/0001-30, Simples Nacional, metalurgia/usinagem, banco principal: Sicoob 92010-0 (conta 8). Gera TXT único de lançamentos para o Domínio + planilha de sócios, conciliando saldos."
---

# ROF Contabilidade PAI E FILHOS — Lançamentos Contábeis e Conciliação

## Dados da Empresa

| Campo | Informação |
|---|---|
| Razão social | PAI E FILHOS LTDA |
| Nome fantasia | METALÚRGICA PAI E FILHOS |
| CNPJ | 54.239.093/0001-30 |
| CNPJ sem formatação | 54239093000130 |
| CNAE principal | 2539-0/01 — Serviços de usinagem, tornearia e solda |
| CNAEs secundários | 3319-8/00 — Manutenção e reparação de equipamentos e produtos não especificados |
| Setor | Metalurgia / usinagem |
| Regime tributário | Simples Nacional |
| Banco(s) | Sicoob 92010-0 → conta **8** (principal) · InfinitePay 18851875-7 → conta **9** · Caixa Geral → conta **5** |
| Data de abertura | 07/03/2024 |
| Sistema contábil | Domínio (Thomson Reuters) — licenciado para PAES E BASTOS CONTABILIDADE LTDA |
| Cadastrado por | Rosangela |

## Sócios

| Sócio | CPF | Conta no Domínio |
|---|---|---|
| Airton de Souza | 724.135.909-78 | **528** (1.2.2.04.001 — Sócios/Ativo não circulante) |
| Wagner de Souza | 096.511.249-70 | **529** (1.2.2.04.002 — Sócios/Ativo não circulante) |

- Ambos os sócios têm pró-labore.
- CPFs mascarados no extrato: Airton = `***.135.909-**` · Wagner = `***.511.249-**`.

## Funcionários CLT

| Colaborador | Cargo | Salário base |
|---|---|---|
| Anderson Renam Pereira | Soldador | R$ 2.500,00 |

- CPF mascarado no extrato: `***.735.529-**`.
- Pagamento de salário CLT no extrato → débito **187** (Salários e Ordenados a Pagar), crédito banco.
- Dados completos da folha serão buscados no Domínio: **Módulo Folha → Relatórios → Cadastrais → Empregado**, a cada novo extrato.

## Regras de Trabalho (ACORDO COM A CONTADORA)

1. **Fidelidade total** aos dados enviados — não alterar nada sem consultar.
2. **Consulta prévia** antes de qualquer alteração.
3. **Base legal** sempre que sugerir algum ajuste.
4. **Histórico**: copiar o texto exatamente como aparece no extrato (normalizar para ASCII maiúsculo, sem acento, como no padrão Otimizza).

## Leiaute do Arquivo TXT para Domínio (Otimizza)

```
|0000|54239093000130|
|6000|X||||
|6100|DD/MM/AAAA|CONTA_DEBITO|CONTA_CREDITO|VALOR||HISTORICO||||
```

- Cabeçalho `|0000|CNPJ|` **uma vez** no topo do arquivo.
- **Antes de cada** `|6100|`, uma linha `|6000|X||||`.
- Pagamento (saída): débito na conta de despesa/custo/passivo, **crédito no banco**.
- Recebimento (entrada): **débito no banco**, crédito na contraparte (padrão **504**).
- Valor com **vírgula** decimal: ex. `1500,00`. Data `DD/MM/AAAA`.

### REGRA FIXA — Arquivo TXT ÚNICO

> **Gerar sempre UM único arquivo TXT, mesmo que a empresa tenha 10 contas bancárias diferentes.**

- Consolidar todos os bancos (Sicoob `8`, InfinitePay `9`, etc.) em um só arquivo.
- **Ordenar todos os lançamentos por data**, independentemente do banco de origem.
- Cada lançamento usa o **código contábil do seu próprio banco** como débito (recebimento) ou crédito (pagamento).

### ENTREGA PADRÃO — Planilha de Sócios junto ao TXT

> **Toda competência entrega SEMPRE dois arquivos: o TXT único + a planilha XLSX de pró-labore e retiradas por sócio.** Não esperar o usuário pedir a planilha — já gerar e enviar junto.

Planilha (`.xlsx`, fonte Arial, valores em R$): aba **Resumo** (parâmetros do pró-labore + consolidado por sócio) e uma aba por sócio (**Airton**, **Wagner**) com cada pagamento do mês e o rateio por fórmula (`Pró-labore = MÍN(valor; limite − acumulado anterior)`; `Retirada = valor − pró-labore`). Nome sugerido: `PaiEFilhos_ProLabore_Retiradas_MMAAAA.xlsx`.

## Plano de Contas — Contas Operacionais

| Cód | Classificação | Nome | Natureza |
|---|---|---|---|
| 5 | 1.1.1.01.001 | CAIXA GERAL | Ativo — disponível |
| 8 | 1.1.1.02.001 | SICOOB COOP. DE CRÉDITO — CONTA 92010-0 | Ativo — banco (principal) |
| 9 | 1.1.1.02.002 | INFINITEPAY — CONTA 18851875-7 | Ativo — banco |
| 504 | 1.1.2.01.001 | CLIENTES DIVERSOS | Ativo — duplicatas a receber |
| 528 | 1.2.2.04.001 | AIRTON DE SOUZA (724.135.909-78) | Ativo — sócios |
| 529 | 1.2.2.04.002 | WAGNER DE SOUZA (096.511.249-70) | Ativo — sócios |
| 506 | 2.1.3.01.001 | FORNECEDORES (insumos/materiais que condizem com a atividade) | Passivo — fornecedores |
| 479 | 2.1.4.01.015 | SIMPLES NACIONAL A RECOLHER (DAS) | Passivo — tributário |
| 187 | 2.1.5.01.001 | SALÁRIOS E ORDENADOS A PAGAR | Passivo — pessoal |
| 188 | 2.1.5.01.002 | PRÓ-LABORE A PAGAR | Passivo — pessoal |
| 539 | 2.1.5.01.004 | 13º SALÁRIO A PAGAR | Passivo — pessoal |
| 543 | (folha) | FÉRIAS A PAGAR | Passivo — pessoal |
| 191 | 2.1.5.02.001 | INSS A RECOLHER (DARF previdenciário) | Passivo — social |
| 192 | 2.1.5.02.002 | FGTS A RECOLHER (Caixa Econômica) | Passivo — social |
| 494 | (folha) | IRRF S/ FOLHA A RECOLHER | Passivo — social |
| 510 | 2.1.6.02.001 | HONORÁRIOS CONTÁBEIS (pagamento a contabilidade) | Passivo — contas a pagar |
| 545 | 2.1.6 (adiant.) | ADIANTAMENTOS DE CLIENTES | Passivo — outras obrigações |
| 546 | 2.3.5.01.006 | DISTRIBUIÇÃO DE LUCROS | Patrimônio líquido |
| 467 | 3.1.6.01.001 | CUSTOS DOS SERVIÇOS PRESTADOS (inclui manutenção mecânica e serviços operacionais PJ) | Custo |
| 534 | 3.1.3.01.001 | SALÁRIOS E ORDENADOS (custo MOD) | Custo — mão de obra |
| 535 | 3.1.3.01.002 | PRÓ-LABORE (custo) | Custo — mão de obra |
| 537 | 3.1.3.01.004 | FGTS (custo) | Custo — mão de obra |
| 541 | 3.1.3.01.006 | FÉRIAS (custo) | Custo — mão de obra |
| 350 | 3.2.2.03.005 | TAXAS DIVERSAS | Despesa administrativa |
| 354 | 3.2.2.04.001 | ENERGIA ELÉTRICA (Copel) | Despesa geral |
| 355 | 3.2.2.04.002 | ÁGUA E ESGOTO (Sanepar) | Despesa geral |
| 356 | 3.2.2.04.003 | TELEFONE/INTERNET (TIM, provedores) | Despesa geral |
| 359 | 3.2.2.04.006 | DESPESAS ADMINISTRATIVAS (inclui ALUGUEL pago via saque Banco 24 Horas) | Despesa geral |
| 361 | 3.2.2.04.008 | ASSISTÊNCIA CONTÁBIL (pagamento a contabilidade usa 510) | Despesa geral |
| 362 | 3.2.2.04.009 | SERVIÇOS PRESTADOS POR TERCEIROS | Despesa geral — **default para pagamento a Pessoa Física (não sócio/colaborador)** |
| 493 | 3.2.2.04.014 | DESPESAS DIVERSAS | Despesa geral |
| 530 | 3.2.2.04.015 | DESPESA COM DESLOCAMENTO (combustível/posto) | Despesa geral |
| 521 | 3.2.2.04.016 | DESPESAS COM ALIMENTAÇÃO (mercados/restaurantes) | Despesa geral |
| 532 | 3.2.2.05.009 | TARIFAS BANCÁRIAS | Despesa financeira |
| 411 | 4.1.1.02.001 | SERVIÇOS PRESTADOS | Receita |
| 432 | (receita fin.) | RECEITA FINANCEIRA (rendimento mensal InfinitePay) | Receita |
| 480 | 4.1.2.03.008 | (-) SIMPLES NACIONAL | Dedução da receita |

## Regra de Classificação das Contrapartes

### Para cada lançamento do extrato, siga esta ordem:

1. Identificar **natureza** (entrada / saída).
2. Identificar **favorecido** (nome, CNPJ/CPF no histórico).
3. **Recebimento** (RECEBIMENTO PIX, CRED.LIQ.COBRANCA, devolução PIX) → débito banco, **crédito 504**.
4. **Sócio** (CPF `***.135.909-**` Airton ou `***.511.249-**` Wagner, PIX "Wagner de Souza" na InfinitePay, ou "SAQUE NA AGENCIA NOME <sócio>") → aplicar **Regra Mensal — Retiradas dos Sócios**.
5. **Colaborador CLT** (CPF `***.735.529-**` Anderson) → **187**.
6. **Pagamento a CNPJ**: SEMPRE confirmar o CNPJ na Receita e verificar a atividade (CNAE):
   - Insumo/material/fornecedor que **condiz com metalurgia/usinagem** (sucata, gases, ferragens, ferramentas, tintas, materiais, serralheria, usinagem, solda) → **506**.
   - Energia elétrica → **354** · Água/esgoto → **355** · Telefone/internet → **356**.
   - Contabilidade → **510**.
   - Manutenção mecânica / reparação de equipamentos / serviço operacional (PJ) → **467**.
   - DAS Simples Nacional (Receita Federal) → **479** · DARF INSS previdenciário → **191** · FGTS (Caixa Econômica) → **192**.
   - Combustível (Premmia/Ipiranga, postos) → **530**.
   - CNPJ cuja atividade não se enquadre acima → sinalizar para a contadora (NÃO usar 362, reservado a PF).
7. **Pagamento a Pessoa Física** (exceto sócios e colaborador) → **362**.
8. **Histórico**: copiar exatamente como aparece no extrato.

> **Pagamentos à Receita Federal (00.394.460) vêm em vários DARF/DAS no mesmo mês** — identificar cada um pelo comprovante: DAS Simples → 479; DARF INSS (cód. 1082 empregados / 1099 contribuinte individual-sócios) → 191. Na dúvida, pedir o documento.

### CNPJs já confirmados

| CNPJ | Empresa | Atividade | Conta |
|---|---|---|---|
| 03.228.783/0001-53 | Oxiberti Gases Industriais | Gases industriais (solda) | **506** |
| 04.247.051/0001-73 | Ferro Velho Coradin | Sucata metálica | **506** |
| 32.481.136/0001-57 | Liquivaz | Comércio de gás | **506** |
| 00.111.430/0001-80 | Tratoraço | Ferragens e ferramentas | **506** |
| 30.357.390/0001-12 | Tintas Pelicano | Tintas | **506** |
| 05.556.189/0001-17 | Cavallari Materiais (Hilton G. Cavallari) | Materiais de construção | **506** |
| 07.322.005/0001-80 | Metalúrgica Piquiri (Francinei Pereira) | Carrocerias/metal | **506** |
| 33.903.326/0001-88 | Casa Saldatore (Oximoreto) | Materiais p/ solda e ferramentas | **506** |
| 13.374.446/0001-28 | Tornearia Santana | Usinagem/tornearia/solda | **506** |
| 20.655.292/0001-08 | John Erick Vidal (MEI) | Reparação de equipamentos | **467** |
| 46.831.359/0001-01 | Cleverson Calegari (MEI) | Manutenção mecânica de veículos | **467** |
| 04.368.898/0001-06 | Copel | Energia elétrica | **354** |
| 76.484.013/0001-45 | Sanepar | Água/esgoto | **355** |
| 53.420.564/0001-40 | Client Co (SCM) | Internet | **356** |
| 02.421.421/0001-11 | TIM | Telefonia | **356** |
| 29.650.531/0001-01 | RBA Contabilidade | Contabilidade | **510** |
| 34.274.233/0001-02 | Premmia/Ipiranga | Combustível | **530** |
| 76.648.500/xxxx | Mitra/Arquidiocese (Paróquia) | Doação | **493** |
| 00.394.460/0058-87 | Receita Federal | DAS → 479 · DARF INSS → 191 (identificar pelo comprovante) | **479/191** |
| 00.360.305/0001-04 | Caixa Econômica Federal | FGTS | **192** |

### Merchants de cartão (COMPRA MASTERCARD MAESTRO) já confirmados

| Merchant | Conta |
|---|---|
| Tintas Pelicano, Ferro Velho Coradin, Cavallari Materiais, Agropecuaria Parana, Hilton Gustavo, Serralheria (M J Aces), Soares Gas | **506** |
| MP *Helicar | **467** |
| Postos / combustível | **530** |
| Restaurantes / mercados / padarias | **521** |
| Farmácia, DPaschoal (autopeças), demais compras diversas | **493** |

### Classificações recorrentes por padrão de histórico

| Padrão no histórico | Conta |
|---|---|
| RECEBIMENTO PIX / CRED.LIQ.COBRANCA / devolução PIX | **504** (crédito) |
| RENDIMENTOS MENSAL (InfinitePay) | **432** (crédito, receita financeira) |
| PIX a Pessoa Física não identificada (não sócio/colaborador) · SICOOB-PDF | **362** |
| Mercados, supermercados, padarias, restaurantes, açougue, bebidas (COMP MASTER) | **521** |
| Farmácia, lojas de varejo, autopeças, estacionamento, compras diversas | **493** |
| Postos / autopostos / combustível | **530** |
| DEB.CONV.SANEAMENTO (Sanepar) | **355** |
| Energia elétrica (Copel) | **354** |
| Telefone / internet | **356** |
| TARIFA COBRANCA | **350** |
| DEB PACOTE SERVICOS / tarifas do banco | **532** |
| DEB.TIT.COMPE / DEB.CONV.DEMAIS EMPRESAS (boletos/convênios) | **493** |
| **SAQUE DINHEIRO BANCO 24H / BANCO 24 HORAS** (= ALUGUEL) | **359** |
| SAQUE TERMINAL / demais saques / transferência interna p/ caixa | **5** (Caixa Geral) |

## Regra Inviolável — Conferência de Saldo

> Nunca entregar o TXT sem que os saldos do extrato estejam fechando.

1. Saldo anterior (abertura) e saldo final (encerramento) do extrato.
2. Diferença esperada = Saldo final − Saldo anterior.
3. Diferença apurada = Total entradas lançadas − Total saídas lançadas.
4. Se **apurada ≠ esperada** → **NÃO entregar o TXT**. Conferir por banco e no consolidado.

## Regra Inviolável — Aplicações Financeiras e Rendimentos

> Nunca omitir movimentações de aplicação financeira do TXT.

A conta InfinitePay (9) paga **rendimento mensal** — lançar como **débito banco 9, crédito 432** (Receita Financeira). Nunca omitir, mesmo valores pequenos (ex.: R$ 1,53).

## Regra Inviolável — IOF e IRRF

> Nunca omitir IOF nem IRRF do TXT.

- **IOF** → sem conta cadastrada. Se aparecer, sinalizar para criar a conta antes de lançar.
- **IRRF** → conta **494** (IRRF s/ folha a recolher); nunca omitir por valor pequeno.

## Regra Mensal — Retiradas dos Sócios

> ANTES DE LANÇAR qualquer pagamento a sócio: confirmar com a contadora o total pago no mês por sócio.

**Pró-labore base: salário mínimo nacional vigente — R$ 1.621,00 (2026). Atualizar sempre que o salário mínimo for reajustado.**

| Cálculo | Fórmula | Valor 2026 |
|---|---|---|
| Base | Salário mínimo nacional vigente | R$ 1.621,00 |
| INSS (11%) | Base × 11% | R$ 178,31 |
| Pró-labore líquido | Base − INSS | R$ 1.442,69 |

**Ordem obrigatória: pagar SEMPRE o pró-labore primeiro. O que exceder o pró-labore líquido vira retirada de sócio.**

Regra de lançamento por sócio (aplicar sobre o **acumulado do mês** de cada sócio, **consolidando todos os bancos**):

| Faixa do acumulado no mês | Débito | Crédito |
|---|---|---|
| **1º** — até o pró-labore líquido (R$ 1.442,69) | **188** (Pró-labore a Pagar) | banco (**8**/**9**) |
| **2º** — o que exceder R$ 1.442,69 | **528** (Airton) ou **529** (Wagner) — retirada de sócio | banco (**8**/**9**) |

- Sempre esgotar a faixa de pró-labore (**188**) antes de lançar qualquer valor como retirada (**528/529**).
- Um mesmo pagamento pode ser **dividido** entre as duas contas quando cruzar o limite (parte em **188**, o restante em **528/529**).
- **Gerar sempre a planilha XLSX de pró-labore/retiradas por sócio e entregar junto ao TXT** (ver ENTREGA PADRÃO).

## Regra — Devolução / Aporte do Sócio

Quando o sócio deposita valores **na empresa** (entrada no extrato):

| Débito | Crédito |
|---|---|
| banco (**8**/**9**) | **528** (Airton) ou **529** (Wagner) |

## Particularidades do Banco

- **Sicoob 92010-0 (conta 8)** — banco principal. Tarifas de cobrança → **350**; pacote de serviços → **532**.
- **InfinitePay (conta 9)** — adquirente/conta digital; recebimentos de cartão e **rendimento mensal → 432**. Consolidar no mesmo TXT.
- Sem banco intermediário com regra de reserva/liberação.

## Fluxo de Trabalho

1. Receber extrato(s) bancário(s) (PDF, CSV, OFX ou TXT Otimizza) — de todas as contas.
2. Para cada lançamento: identificar natureza → favorecido → **confirmar CNPJ na Receita** → classificar → registrar histórico exato.
3. Sinalizar lançamentos não identificados para revisão da contadora.
4. Verificar rendimentos, IOF e IRRF (regras invioláveis).
5. Conferir saldo: entradas − saídas = variação do extrato (por banco e consolidado).
6. Gerar **um único TXT** consolidado, ordenado por data.
7. Gerar **a planilha XLSX de pró-labore/retiradas por sócio** e entregar **junto** ao TXT (entrega padrão, sem esperar o usuário pedir).

## Histórico de Competências

- **07/2026** — concluída (Sicoob). Abertura R$ 29.379,50 → encerramento R$ 31.443,59 (variação R$ 2.064,09, conferido). InfinitePay sem movimento. Pró-labore R$ 1.442,69 por sócio; retiradas Airton R$ 1.007,31 / Wagner R$ 1.877,31.
- **08/2026** — concluída (Sicoob + InfinitePay). Sicoob 31.443,59 → 24.854,76; InfinitePay 2.553,13 → 2.004,66 (ambos conferidos). Rendimento InfinitePay R$ 1,53 → 432. Pró-labore R$ 1.442,69 por sócio; retiradas Airton R$ 5.607,31 / Wagner R$ 1.927,31 (inclui Pix R$ 550 na InfinitePay). Pendência: 2 DARF Receita Federal de 18/08 (R$ 87,05 e R$ 104,01) sem comprovante — provisório em 479.

## Pendências a Confirmar com a Contadora

- Competência 08/2026: comprovantes dos 2 pagamentos à Receita Federal de 18/08 (R$ 87,05 e R$ 104,01) para separar DAS/INSS (provisório 479).
- Tratamento de recebimentos InfinitePay (líquido de taxas × bruto + tarifa), caso passem a receber cartão pela conta.

---

## Padrão ROF — Pró-labore, Retiradas e Relatório do Sócio

> Regra validada pela contadora Rosangela em 24/09/2026 para todas as empresas do escritório.
> As regras específicas desta empresa descritas acima **continuam valendo**. Este bloco completa o que faltar e **não substitui** nenhuma conta, exceção ou classificação já confirmada. Em caso de conflito, prevalece a regra específica da empresa.

### Parâmetros desta empresa

| Sócio | CPF | Pró-labore | Conta pró-labore a pagar | Conta do sócio (retirada / aporte) |
|---|---|---|---|---|
| Airton | ver acima | Variável — perguntar todo mês | **188** | **528** |
| Wagner | ver acima | Variável — perguntar todo mês | **188** | **529** |

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
