---
name: rof-contabilidade-ribeiro
description: "Regras e particularidades de lançamentos contábeis da RIBEIRO FAST FASHION LTDA (GURIA CHIC) no sistema Domínio"
---

# ROF Contabilidade — RIBEIRO FAST FASHION LTDA

## Dados da Empresa

| Campo | Informação |
|---|---|
| Razão social | RIBEIRO FAST FASHION LTDA |
| Nome fantasia | GURIA CHIC |
| CNPJ | 19.957.768/0001-86 |
| CNPJ sem formatação | 19957768000186 |
| Regime tributário | Simples Nacional |
| Responsável | Rosângela (ROF Contabilidade) |
| Banco Itaú | Conta código **6** |
| Banco Sicredi | Conta código **8** |
| Banco Sicoob | Conta código **9** |
| Script de geração | /root/gerar_julho2026.py (base para meses futuros) |

## Sócia

| Nome | CPF | Conta Domínio |
|---|---|---|
| Junia Aparecida Ribeiro de Almeida | 073.402.009-08 | 539 (ativo) |

## Funcionários (CLT)

| Nome | Cargo | Conta |
|---|---|---|
| Hillary Eduarda Silveira Rodrigues | Vendedora | 187 |
| Renata Caroline Rocha | — | 187 |
| Gabriela da Rocha Ramos | — | 187 |

## Regra IMUTÁVEL — Pró-labore e Retirada da Sócia

> **SEMPRE perguntar o salário mínimo nacional vigente no início de cada nova competência.**

**Fórmula:**
- Pró-labore bruto = salário mínimo nacional vigente
- INSS sócia = bruto × 11%
- **Pró-labore líquido = bruto × 89%**

**Aplicação — em ordem cronológica cruzando todos os bancos do mês:**

| Acumulado pago à sócia no mês | Conta Débito | Conta Crédito |
|---|---|---|
| Até o pró-labore líquido | **188** (Pró-labore a Pagar) | Banco |
| Excedente ao pró-labore líquido | **539** (Conta ativo da sócia) | Banco |

**Referência 2026:** salário mínimo R$1.621,00 → INSS R$178,31 → líquido **R$1.442,69**

## Entrega Obrigatória — Final de Cada Competência

> **Sempre entregar DOIS arquivos juntos:**
> 1. **TXT Domínio** (`RIBEIRO_FASTFASHION_AAAAMM_UNIFICADO.txt`)
> 2. **Planilha de retiradas da sócia** (`Pagamentos_Socia_Junia_MMMAAAA.xlsx`)

A planilha deve conter: Data · Banco · Conta Domínio · Histórico · Valor · Observação
Linhas com conta 188 = Pró-labore; linhas com conta 539 = Retirada de sócia.

## Plano de Contas — Contas Principais

| Cód | Descrição | Obs |
|---|---|---|
| 6 | Banco Itaú | Conta movimento |
| 8 | Banco Sicredi | Conta movimento |
| 9 | Banco Sicoob | Conta movimento |
| 152 | Empréstimos / Contratos bancários | |
| 187 | Salários e Ordenados a Pagar | Funcionários CLT |
| 188 | Pró-labore a Pagar | Sócia Junia |
| 350 | DAS / Simples Nacional | |
| 356 | Energia / Telecom | |
| 357 | Cartão de crédito — fatura | |
| 358 | Seguros | |
| 359 | Despesas Administrativas | |
| 362 | Serviços Prestados por Terceiros | PF não sócia/funcionária |
| 364 | Tarifas bancárias Itaú | |
| 366 | Veículos / Transporte (Uber) | |
| 369 | Tarifas bancárias Sicredi / Sicoob | |
| 370 | Tarifas de cobrança | |
| 372 | Juros | |
| 373 | IOF | Lançar separado, nunca embutir |
| 432 | Rendimentos financeiros | |
| 470 | Fornecedores | |
| 493 | Despesas Diversas | |
| 504 | Receita de vendas | |
| 506 | Cheques / Boletos fornecedores / Pluxee | |
| 510 | Honorários Contábeis | |
| 521 | Vale-alimentação | |
| 539 | Junia Aparecida Ribeiro de Almeida | Ativo — retiradas/aportes |
| 540 | Doações | |

## Classificações Recorrentes Validadas

| Favorecido / Padrão | Conta | Banco |
|---|---|---|
| HILLARY EDUARDA (PIX Itaú) | 187 | 6 |
| JUNIA APARECIDA / CPF 073.402.009-08 | 188 ou 539 (regra acima) | 6 ou 8 |
| KARIME KADRI | 362 | 6 |
| PLUXEE (boleto ou PIX, qualquer CNPJ) | 506 | 8 |
| SANCOR SEG (seguros) | 358 | 9 |
| VIVO / Telecom | 356 | 9 |
| MASTERCARD (DEB.CONV.DEM.EMPRES) | 357 | 9 |
| DEB.EMPRESTIMO Sicoob | 152 | 9 |
| EST.DEB.EMPRESTIMO (par do DEB.EMPRESTIMO) | Excluir ambos — saldo líquido zero | 9 |
| TARIFA ACAT.CHEQUE / PACOTE SERVICOS | 369 | 9 |
| JUROS ADIANT.DEPOSITANTE / CTA GARANTIDA | 372 | 9 |
| IOF Sicoob | 373 | 9 |
| CHQ CMP INTEGRADA | 506 | 9 |
| LIQUIDACAO BOLETO — ROF DA SILVA | 510 | 8 |
| LIQUIDACAO BOLETO — AREZZO | 506 | 8 |
| PAGAMENTO PIX — LEANDRO | 362 | 8 |
| PAGAMENTO PIX — FABRICIO MARQUES | 493 | 8 |
| PAGAMENTO PIX — JOSIANE SANTOS | 493 | 8 |
| PAGAMENTO PIX — ANA PAULA SCHMEGUEL | 493 | 8 |

## Regra — Transferências Interbancárias

- GURIA CHIC (CNPJ 19.957.768/0001-86) no memo = transferência entre contas próprias
- Um único lançamento: D=banco destino, C=banco origem
- Cruzar os três extratos para confirmar origem e destino

## Regra Inviolável — Sanitização do Histórico

- Remover todo `|` do campo histórico antes de gravar
- Sicredi inclui `|0001-86|` nos memos — sem remoção o Domínio rejeita o lançamento
- Código: `hist.replace('|', ' ').strip()[:60]`

## Regra Inviolável — Conferência de Saldo

Antes de entregar o TXT, conferir que entradas − saídas = variação do extrato em cada banco.

## Regra — DEB.EMPRESTIMO + EST.DEB.EMPRESTIMO (Sicoob)

Quando aparecerem em par no mesmo dia → saldo líquido zero → **excluir ambos** do TXT.

## Histórico de Competências Processadas

| Competência | Bancos | Lançamentos | Status |
|---|---|---|---|
| Julho/2026 | Itaú (6) + Sicredi (8) + Sicoob (9) | 691 | ✅ TXT + planilha entregues |

---

## Padrão ROF — Pró-labore, Retiradas e Relatório do Sócio

> Regra validada pela contadora Rosangela em 24/09/2026 para todas as empresas do escritório.
> As regras específicas desta empresa descritas acima **continuam valendo**. Este bloco completa o que faltar e **não substitui** nenhuma conta, exceção ou classificação já confirmada. Em caso de conflito, prevalece a regra específica da empresa.

### Parâmetros desta empresa

| Sócio | CPF | Pró-labore | Conta pró-labore a pagar | Conta do sócio (retirada / aporte) |
|---|---|---|---|---|
| Junia Aparecida Ribeiro de Almeida | ver acima | Variável — perguntar todo mês | **188** | **539** |

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
