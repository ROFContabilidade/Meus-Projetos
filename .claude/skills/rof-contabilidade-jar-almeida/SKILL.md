---
name: rof-contabilidade-jar-almeida
description: "Lançamentos contábeis e conciliação bancária da J A R DE ALMEIDA LTDA (CNPJ 59.888.774/0001-43, Simples Nacional, comércio varejista de doces e balas, PR) para o sistema Domínio (Thomson Reuters). Use quando Rosangela ou Elen enviarem extrato, plano de contas, razão ou pedirem lançamentos desta empresa."
---

# ROF Contabilidade — J A R DE ALMEIDA LTDA

## Dados da Empresa

| Campo | Informação |
|---|---|
| Razão social | J A R DE ALMEIDA LTDA |
| CNPJ | 59.888.774/0001-43 |
| Carteira | Contabilidade **ROF** — pasta **110_Cacau Ribeiro** (loja BR Cacau; extratos "JAR BR CACAU"). Mesma sócia da Guria Chic (Junia), mas é **outra empresa**. **Não confundir** com a 85 - Letícia Doces (RENATA) |
| CNPJ sem formatação | 59888774000143 |
| CNAE principal | 4721-1/04 — Comércio varejista de doces, balas, bombons e semelhantes |
| CNAE secundário 1 | 4712-1/00 — Comércio varejista de mercadorias em geral, com predominância de produtos alimentícios |
| CNAE secundário 2 | 4723-7/00 — Comércio varejista de bebidas |
| CNAE secundário 3 | 5611-2/03 — Lanchonetes, casas de chá, de sucos e similares |
| Setor | Comércio varejista de doces, balas e semelhantes |
| Regime tributário | Simples Nacional |
| UF | PR — Paraná |
| Data de abertura | 13/03/2025 |
| Capital social | R$ 250.000,00 |
| Banco(s) | Sicredi (conta **8**) · Sicoob (conta **9**) |
| Folha de pagamento | Sim |
| Cadastrado por | Rosangela |

## Sócias

| Sócio | CPF | Conta no Domínio | Função |
|---|---|---|---|
| Junia Aparecida Ribeiro de Almeida | 073.402.009-08 | **539** | Sócia-Administradora |

## Regras de Trabalho (ACORDO COM A CONTADORA)

1. **Fidelidade total** aos dados enviados — não alterar nada sem consultar
2. **Consulta prévia** antes de qualquer divergência ou dúvida de classificação
3. **Base legal** sempre que sugerir algum ajuste
4. **Histórico**: copiar o texto exatamente como aparece no extrato bancário — não resumir, não traduzir, não alterar
5. **Contas bancárias e plano de contas**: extrair os códigos contábeis dos documentos enviados — não perguntar antecipadamente

## Leiaute do Arquivo TXT para Domínio

```
|0000|59888774000143|
|6000|X||||
|6100|DD/MM/AAAA|CONTA_DEBITO|CONTA_CREDITO|VALOR||HISTORICO||||
|6000|X||||
|6100|DD/MM/AAAA|CONTA_DEBITO|CONTA_CREDITO|VALOR||HISTORICO||||
```

- **Um `|6000|X||||` por lançamento** — obrigatório antes de CADA linha `|6100|`. Um único `|6000|` cobrindo múltiplos `|6100|` causa erro no Domínio: "Não é permitido ter mais de um lançamento no tipo 'um débito para um crédito'"
- **Pagamento (saída):** débito na conta de despesa/ativo, crédito no banco
- **Recebimento (entrada):** débito no banco, crédito na conta de receita
- **Arquivo único:** pagamentos e recebimentos ordenados por data — NÃO gerar dois arquivos separados
- **Valor:** com vírgula decimal — ex.: 1500,00
- **Histórico:** remover todo caractere `|` do texto — o OFX do Sicredi inclui ` |0001-43` nos memos de cartão/débito, o que quebra o leiaute no Domínio (lido como separador de campo)

## Plano de Contas — Contas Operacionais

| Cód | Classificação | Observação |
|---|---|---|
| 8   | Banco Sicredi — Conta 65975-8 | Conta movimento Sicredi |
| 9   | Banco Sicoob — Conta 104253-0 | Conta movimento Sicoob |
| 152 | Empréstimos / Contratos bancários | Amortizações e liquidações de contrato (ex.: C64030204) |
| 312 | Fretes | Imperial Locação e Transporte (36.933.715/0002-25) |
| 187 | Salários e Ordenados a Pagar | Pagamento de salários CLT |
| 188 | Pró-labore a Pagar | Pró-labore da sócia Junia |
| 191 | INSS a Recolher | GPS — recolhimento INSS |
| 192 | FGTS a Recolher | Recolhimento FGTS (CEF) |
| 274 | Salários e Ordenados (custo) | Custo folha de pagamento |
| 354 | Energia Elétrica | COPEL e similares |
| 356 | Telefone | Internet, telefone, recarga celular |
| 359 | Despesas Administrativas | Despesas fixas administrativas (ex.: Claudia Elisa Cantador Kravetz) |
| 362 | Serviços Prestados por Terceiros | Serviços PF (ex.: Luciana Aparecida Rangel) |
| 364 | Despesas com Cartão de Crédito | PJBank e adquirentes |
| 366 | Serviços de Assessoria e Gerenciamento | Marketing, assessoria (ex.: Agência de Ideias) |
| 369 | Despesas Bancárias | Tarifas, pacote de serviços, seguro prestamista, juros cheque especial |
| 373 | IOF | IOF — lançar separadamente, nunca embutir |
| 512 | ICMS Antecipado | GR-PR "GOVERNO DO PARANA" (76.416.890/0001-89) — valor total da guia, inclusive multa/juros (contadora, 24/09/2026) |
| 470 | CMV | Compras de mercadorias para revenda |
| 479 | Simples Nacional a Recolher | DAS — Receita Federal >R$1.000 |
| 493 | Despesas Diversas | Despesas não classificadas especificamente |
| 504 | Clientes Diversos | Todas as receitas de vendas (PIX, cartão, TED) |
| 506 | Fornecedor | Compras e serviços de fornecedores (GMX Chocolates, LTS Toys, Pluxee, Antilhas Gráfica, RGT Automação, CISS Consultoria e similares) |
| 510 | Honorários Contábeis | R O F da Silva (escritório contábil) |
| 539 | Junia Aparecida Ribeiro de Almeida | Conta ativo da sócia — retiradas e aportes |
| 521 | Despesas com Alimentação | Vale-refeição e similares |
| 548 | Despesas com Suporte Técnico | Sistemas e TI (verificar plano de contas) |
| 58  | Outros Materiais de Consumo | Materiais gráficos (verificar plano de contas) |

## Classificações Recorrentes Validadas pela Contadora

| CNPJ / Favorecido | Conta | Observação |
|---|---|---|
| 65315372000152 — GMX CHOCOLATES FINOS LTDA | **506** | Fornecedor de mercadorias |
| 36933715000225 — IMPERIAL LOCACAO E TRANSPORTE | **312** | Fretes |
| 69034668000156 — PLUXEE BENEFICIOS BRASIL S A | **506** | Fornecedor |
| 02096748000165 — ANTILHAS GRAFICA E EMBALAGENS LTDA | **506** | Fornecedor |
| 07750595000141 — R G T AUTOMACAO LTDA | **506** | Fornecedor |
| 23776451000200 — LTS TOYS I E COMERCIO B L | **506** | Fornecedor |
| 82213604000180 — CISS CONSULTORIA EM INFORMATICA SERVICO | **506** | Fornecedor |
| 37264420000195 — R O F DA SILVA LTDA | **510** | Honorários contábeis |

> Classificações validadas pela contadora têm prioridade sobre a classificação automática por CNPJ.

> **Fornecedores do relatório de Entradas → 506** (contadora, 24/09/2026): todo pagamento a fornecedor que conste no relatório de notas de entrada da empresa (Entradas.xls / "NF Entrada_MM.AA_Cacau.xlsx" na pasta Relatorios do mês) vai para a conta **506**. Conferir o favorecido do extrato com a lista de emitentes desse relatório antes de classificar.

## Regra de Classificação das Contrapartes — LEIA ANTES DE CLASSIFICAR

Para cada lançamento do extrato, siga esta ordem:

1. Identifique o favorecido (nome, CNPJ/CPF)
2. Se tiver CNPJ → pesquisar no portal da Receita Federal para verificar a atividade → classificar conforme plano de contas
3. Se for Pessoa Física (exceto sócia) → conta de serviços PF (verificar no plano de contas)
4. Se for a sócia Junia → aplicar **Regra de Retiradas** abaixo
5. Histórico: copiar o texto exato do extrato

## Regra Mensal — Retiradas e Pró-labore da Sócia

> **ANTES DE LANÇAR qualquer pagamento à sócia: identificar o total retirado no mês e se houve pagamentos parciais.**

**Pró-labore mensal = Salário mínimo nacional vigente**

| Cálculo | Fórmula |
|---|---|
| Base (pró-labore bruto) | Salário mínimo nacional vigente |
| INSS (11%) | Base × 11% |
| Pró-labore líquido | Base − INSS |

### Pró-labore (CONFIRMADO — processado via folha, pago via PIX pelo banco):

Aparece no extrato como PIX_DEB para o CPF da sócia (073.402.009-08).

| Valor acumulado no mês | Débito | Crédito |
|---|---|---|
| Até o pró-labore líquido | **188** (pró-labore a pagar) | Banco |
| Excedente ao pró-labore líquido | **539** (conta ativo da sócia) | Banco |

### Devolução / Aporte da Sócia (sócia deposita dinheiro na empresa):

| Débito | Crédito |
|---|---|
| Banco | **539** (conta ativo da sócia) |

O crédito na conta 539 **reduz o saldo devedor** da sócia com a empresa. A mesma conta cobre retirada e devolução — sentidos opostos do mesmo movimento.

## Regra Inviolável — Conferência de Saldo Antes da Entrega

> **Nunca entregar o TXT sem que os saldos do extrato estejam fechando.**

Antes de gerar o arquivo final, conferir obrigatoriamente:

1. Saldo anterior (abertura) informado no extrato
2. Saldo final (encerramento) informado no extrato
3. Diferença esperada = Saldo final − Saldo anterior
4. Somar todas as entradas lançadas no TXT
5. Somar todas as saídas lançadas no TXT
6. Diferença apurada = Total entradas − Total saídas

Se Diferença apurada ≠ Diferença esperada → **NÃO entregar o TXT.** Identificar e corrigir a divergência antes de qualquer entrega.

## Regra Inviolável — Aplicações Financeiras e Rendimentos

> Esta empresa não possui aplicação financeira cadastrada no onboarding. Verificar no plano de contas e no extrato a cada competência se isso mudou.

## Regra Inviolável — IOF e IRRF

> **Nunca omitir IOF nem IRRF do TXT.**

- **IOF:** lançar separadamente — não embutir no valor principal. Conta: **373**
- **IRRF:** nunca omitir por valor pequeno — se constar no extrato ou razão, lança. Conta: verificar no plano de contas.

## Regra — Transferências Entre Contas Próprias

Quando a empresa transferir dinheiro entre suas próprias contas (ex.: Sicredi → Sicoob):

- Lançar diretamente banco a banco (débito na conta destino, crédito na conta origem)
- **Nunca usar conta de caixa como passagem intermediária**, salvo orientação expressa da contadora

## Regra — Simples Nacional

- Conta débito: **479** (SIMPLES NACIONAL A RECOLHER)
- Lançar quando constar no extrato (débito automático ou guia paga via Receita Federal)

## Particularidades do Banco

- **Sicredi e Sicoob** — contas correntes padrão
- Sem banco intermediário (Mercado Pago, Stone, PagSeguro etc.)
- Sicoob: conta garantida (cheque especial contratado R$ 5.000,00) — saldo pode ficar devedor; juros da conta garantida → 369
- Transferência Sicredi → Sicoob aparece como "PAGAMENTO PIX 59888774000143 CACAU RIBEIRO" no Sicredi e "PIX REC.OUTRA IF" no Sicoob → D 9 / C 8, uma linha só
- Sem aplicações financeiras cadastradas
- Guias ficam em `Fiscal_Contabil\2026\<MM_AAAA>\Guias` (DAS, ICMS Antecipado GR-PR, GNRE ST, DeSTDA). Pagamentos ao "GOVERNO DO PARANA" (CNPJ 76.416.890/0001-89) são ICMS Antecipado (GR-PR). Ex.: 28/08/2026 R$ 23,49 = ICMS Antecipado 04/2026 e R$ 37,05 = ICMS Antecipado 05/2026 (receita 32,96 + multa 3,29 + juros 0,80), pagos em atraso
- Tarifas bancárias: classificar conforme plano de contas

## Fluxo de Trabalho

1. Receber extrato bancário (PDF, CSV ou OFX) e plano de contas
2. Extrair códigos contábeis dos bancos e demais contas diretamente do plano de contas enviado
3. Para cada lançamento:
   - a. Identificar natureza (entrada/saída)
   - b. Identificar favorecido
   - c. Aplicar regras de classificação na ordem acima
   - d. Registrar histórico copiando o texto exato do extrato
4. Sinalizar lançamentos não identificados para revisão antes de finalizar
5. Verificar IOF e IRRF — nada pode ficar de fora
6. Conferir saldo: entradas − saídas = variação do extrato
7. Gerar TXT único ordenado por data — **um `|6000|X||||` antes de cada `|6100|`**

## Parâmetros Adicionais

- O razão bancário serve como referência histórica de classificação quando disponível
- Qualquer dúvida ou divergência: pontuar para a contadora **antes** de prosseguir
- Esta empresa deve ser trabalhada em conversa separada das demais

## Pendências a Confirmar com a Contadora

- [x] ~~Confirmar se a sócia Junia tem pró-labore ativo ou somente retirada direta~~ — **pró-labore ativo, processado via folha de pagamento e pago via PIX pelo banco**
- [ ] Razão bancário dos meses anteriores (empresa aberta em 13/03/2025 — verificar se há histórico)
- [ ] Confirmar IRRF quando aparecer no extrato (conta não identificada no plano)

## Relatório XLS — Movimentações da Sócia

Quando solicitado, gerar planilha `.xlsx` com as datas e valores pagos/recebidos da sócia no período:

- **Colunas:** Data · Tipo (Pró-labore / Retirada / Aporte) · Débito/Crédito · Valor (R$) · Histórico
- **Rodapé:** total do período por tipo
- **Observação:** identificar parcelas de pró-labore (D-188/C-Banco), excedente/retirada (D-539/C-Banco) e aportes (D-Banco/C-539) separadamente
- **Formato:** Arial, cabeçalho azul, linhas de pró-labore em verde, retiradas em laranja claro, aportes em amarelo claro

## Histórico de Competências Processadas

| Competência | Bancos | Lançamentos | Status |
|---|---|---|---|
| Julho/2026 | Sicredi (8) + Sicoob (9) | 343 | ✅ TXT entregue (v3) |
| Agosto/2026 | Sicredi (8) + Sicoob (9) | 361 (v2) | ✅ Importar `CACAU_RIBEIRO_JAR_202608_v2.txt` + `CacauRibeiro_JAR_ProLabore_Retiradas_202608_v2.xlsx` (pasta 08_2026\Extratos). Gerado em 24/09/2026 — saldos fecham; pró-labore confirmado pela contadora: R$ 1.621,00 − INSS 11% = líquido R$ 1.442,69; ICMS Antecipado 04 e 05/2026 na 512; Receita R$ 672,60 na 191 (mantido); DAS 07/2026 R$ 961,04 NÃO pago em agosto (em aberto) |

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
