# Guia de classificação de movimentos de extrato bancário

Use este guia para sugerir a contrapartida dos movimentos que as regras da empresa
não classificaram. Os **nomes** de conta abaixo são referência: o código usado no
TXT tem de ser o **código reduzido do plano de contas daquela empresa no Domínio**
(campo `contas` do JSON da empresa, ou o plano de contas que o usuário enviar).
Nunca invente um código. Se não existir conta adequada no plano, avise e peça ao
usuário que diga o código.

Convenção do extrato: valor **positivo = entrada** (o banco é debitado), valor
**negativo = saída** (o banco é creditado). A coluna "Contrapartida" abaixo é a
conta do outro lado do lançamento.

## Entradas (dinheiro que entra)

| Descrição típica no extrato | Contrapartida usual | Observação |
|---|---|---|
| PIX RECEBIDO / TED RECEBIDA / DOC CRED de cliente | Clientes (Duplicatas a Receber) ou Receita de vendas/serviços | Empresas que registram as notas fiscais pelo módulo Escrita Fiscal com integração geralmente baixam **Clientes**; sem integração, lançar direto na receita. Pergunte qual o costume do escritório para a empresa e grave na regra. |
| CIELO, REDE, STONE, GETNET, PAGSEGURO, SUMUP, "ANTECIP" | Cartões a receber / Clientes | A taxa da maquininha normalmente já vem descontada; se o extrato mostra bruto e taxa separados, a taxa vai para Despesas com taxas de cartão. |
| COBRANÇA / LIQUIDAÇÃO DE BOLETO / "CRED COBRANCA" | Clientes | |
| RENDIMENTO / REND PAGO APLIC / REMUNERAÇÃO | Receitas financeiras – rendimentos de aplicação | Se houver IR retido na fonte, pode existir lançamento separado. |
| RESGATE APLICAÇÃO / RESG AUTOMATICO | Aplicações financeiras (ativo) | Não é receita. |
| EMPRÉSTIMO / CRÉDITO PESSOAL PJ / LIBERAÇÃO DE CRÉDITO | Empréstimos e financiamentos (passivo) | Não é receita. |
| TRANSF de conta da própria empresa | Outra conta bancária da empresa | Não é receita. Confirme se a outra conta está no plano de contas. |
| Depósito/PIX do sócio | Conta corrente de sócios / Mútuo com sócios / Adiantamento para aumento de capital | Pergunte a natureza; nunca lançar como receita sem confirmar. |
| ESTORNO / DEVOLUÇÃO / "DEV PIX" | Mesma conta do lançamento original | Localize o lançamento de origem no próprio extrato. |

## Saídas (dinheiro que sai)

| Descrição típica no extrato | Contrapartida usual | Observação |
|---|---|---|
| TARIFA / CESTA / PACOTE SERVIÇOS / TAR PIX / TAR TED | Despesas bancárias | |
| IOF | IOF (despesas financeiras/tributárias) | |
| JUROS / ENCARGOS / MORA / JUROS CHEQUE ESPECIAL | Juros passivos (despesas financeiras) | |
| APLICAÇÃO / APLIC AUTOMÁTICA | Aplicações financeiras (ativo) | |
| PAGTO BOLETO / PIX ENVIADO a fornecedor | Fornecedores | Com integração da Escrita Fiscal, baixa **Fornecedores**; senão, conta de despesa ou estoque. |
| DAS / SIMPLES NACIONAL | Simples Nacional a recolher | |
| DARF (código 0561, 1708, 5952, 2089, 2372, 8109, 2172...) | Tributo correspondente a recolher (IRRF, PIS, COFINS, CSLL, IRPJ) | O código da receita costuma aparecer no complemento; use-o para identificar o tributo. |
| GPS / INSS / DCTFWEB | INSS a recolher | |
| FGTS / GRF / FGTS DIGITAL | FGTS a recolher | |
| PAGTO SALÁRIO / FOLHA / "PAG SALARIO" | Salários a pagar | |
| PRÓ-LABORE | Pró-labore a pagar | |
| PIX/TED para sócio (sem ser pró-labore) | Lucros distribuídos a pagar / Conta corrente de sócios | Pergunte. É ponto sensível fiscalmente. |
| PARCELA EMPRÉSTIMO / FINANCIAMENTO | Empréstimos e financiamentos (principal) + Juros (despesa) | Se só vier o valor total, lançar tudo no passivo e alertar sobre a separação dos juros. |
| CONTA DE LUZ / ENERGIA / CEMIG / ENEL / COPEL / CPFL | Energia elétrica | |
| ÁGUA / SABESP / COPASA / CEDAE | Água e esgoto | |
| TELEFONE / VIVO / CLARO / TIM / OI / INTERNET | Telefone e internet | |
| ALUGUEL | Aluguéis | |
| HONORÁRIOS CONTÁBEIS | Serviços contábeis | |
| CARTÃO DE CRÉDITO (fatura) | Cartão de crédito a pagar | A fatura em si não é despesa; as despesas estão nos itens da fatura. |
| TRANSF para conta da própria empresa | Outra conta bancária da empresa | |
| SAQUE | Caixa | |
| IPVA (guia da Sefaz por código de barras) | Despesa com veículos (sempre) | conferir no relatório de pagamentos do cliente |
| CHEQUE COMPENSADO | Depende do beneficiário | Peça ao usuário se não houver informação. |

## Pontos de atenção na análise

- **Sócios e pessoas físicas**: qualquer movimento com nome de sócio ou CPF precisa
  de confirmação da natureza (pró-labore, lucro, empréstimo, reembolso).
- **Transferências entre contas próprias** aparecem duas vezes (uma em cada extrato):
  a contrapartida deve ser a outra conta banco, nunca receita/despesa.
- **Aplicação e resgate automáticos** podem gerar dezenas de lançamentos por mês;
  sugira regra própria para eles.
- **Estornos**: sinal oposto ao lançamento original, mesma conta.
- **Valores altos e atípicos**: destaque no relatório (o `analisar` lista os 10 maiores).
- **Duplicidades**: mesma data, valor e descrição podem ser legítimas (duas tarifas iguais),
  mas devem ser conferidas.
