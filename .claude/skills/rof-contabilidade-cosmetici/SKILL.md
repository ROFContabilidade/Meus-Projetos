---
name: rof-contabilidade-cosmetici
description: Lançamentos contábeis e conciliação bancária da empresa COSMETICI (CNPJ 33.039.048/0001-62, Lucro Presumido, indústria de cosméticos) para o sistema Domínio (Thomson Reuters). Use quando o usuário pedir para conciliar extrato, cruzar movimentações bancárias, classificar lançamentos no plano de contas ou gerar o arquivo TXT no leiaute Domínio da COSMETICI. Recebe extrato bancário, plano de contas, relatório de gestão, folha de pagamento e razão do banco; cruza por valor, data e nome; e gera TXT único com pagamentos e recebimentos ordenados por data.
---

# ROF Contabilidade Cosmetici — Lançamentos Contábeis e Conciliação

## Dados da Empresa
- **Nome:** COSMETICI
- **CNPJ:** 33.039.048/0001-62
- **CNAE:** 2063-1/00 — Fabricação de cosméticos, produtos de perfumaria e de higiene pessoal
- **Setor:** Indústria de Transformação (Seção C, Divisão 20)
- **Regime Tributário:** Lucro Presumido

## Particularidades Tributárias
- IRPJ: presunção de 8% sobre a receita (atividade industrial)
- CSLL: presunção de 12% sobre a receita
- PIS/COFINS: regime cumulativo (0,65% e 3%), salvo se opção pelo não cumulativo
- IPI: incide sobre produtos industrializados (alíquotas específicas por NCM)
- ICMS: varia conforme o estado

## Sistemas Envolvidos
- **Domínio (Thomson Reuters):** sistema principal contábil — destino final dos lançamentos
- **Otimiza:** sistema atual para lançamento de extratos (em processo de substituição pelo fluxo abaixo)

## Regras de Trabalho (ACORDO COM A CONTADORA)
1. **Fidelidade total** aos dados enviados pela contadora — não alterar nada sem consultar
2. **Consulta prévia** antes de qualquer alteração
3. **Base legal** sempre que sugerir algum ajuste

## Leiaute do Arquivo TXT para Domínio
```
|0000|CNPJ_SEM_FORMATACAO|
|6000|X||||
|6100|DD/MM/AAAA|CONTA_DEBITO|CONTA_CREDITO|VALOR||HISTORICO||||
```
- Linha |0000| = identificação da empresa (CNPJ sem formatação)
- Linha |6000|X|||| = separador entre lançamentos
- Linha |6100| = lançamento: data, conta débito, conta crédito, valor, histórico
- Conta 8 = conta bancária
- Pagamento (saída): débito na conta de despesa, crédito no banco (8)
- Recebimento (entrada): débito no banco (8), crédito na conta de receita
- **Arquivo único:** pagamentos e recebimentos compilados juntos, ordenados por data (sem separação em dois arquivos)

## Fluxo de Trabalho
1. **Receber arquivos da contadora (até 20 por interação, 50MB cada):**
   - Extrato bancário (PDF ou OFX)
   - Plano de contas (Excel)
   - Relatório de gestão do cliente
   - Folha de pagamento (quando aplicável)
   - Razão do banco dos últimos 3 meses (parâmetro de classificação)
   - *Ressalva de precisão:* arquivos pesados (ex.: extrato longo + razão de 3 meses) devem ser enviados em lote menor para preservar a fidelidade do cruzamento — recomendação técnica, não regra rígida.
2. **Cruzar movimentações do extrato com as fontes de referência:**
   - Buscar correspondência por valor, data e/ou nome do fornecedor/funcionário
   - Utilizar o histórico do relatório de gestão ou folha de pagamento (NUNCA do extrato bancário)
   - Se for pagamento de funcionário, cruzar com a folha de pagamento
3. **Classificar no plano de contas:**
   - Adiantamento de salário → conta de adiantamento (Ativo Circulante)
   - Pagamento da folha → conta de salários a pagar/remunerações (Passivo/Despesa)
   - Fornecedores, tarifas, impostos, etc. → classificar conforme plano de contas da empresa
4. **Gerar TXT único** no leiaute Domínio (pagamentos + recebimentos juntos)
5. **Sinalizar** lançamentos não cruzados para revisão da contadora antes de finalizar

## Parâmetros Adicionais
- Razão do Banco dos últimos 3 meses como referência histórica de classificação
- Qualquer dúvida ou divergência: pontuar para a contadora ANTES de prosseguir
- Caso exceda 20 arquivos: processar em duas mensagens dentro da mesma conversa
- Cada empresa deve ser trabalhada em conversa separada

---

## Padrão ROF — Pró-labore, Retiradas e Relatório do Sócio

> Regra validada pela contadora Rosangela em 24/09/2026 para todas as empresas do escritório.
> As regras específicas desta empresa descritas acima **continuam valendo**. Este bloco completa o que faltar e **não substitui** nenhuma conta, exceção ou classificação já confirmada. Em caso de conflito, prevalece a regra específica da empresa.

### Parâmetros desta empresa

| Sócio | CPF | Pró-labore | Conta pró-labore a pagar | Conta do sócio (retirada / aporte) |
|---|---|---|---|---|
| _a cadastrar_ | — | _a confirmar_ | — | — |

> **Pendência:** sócios, CPF, pró-labore e contas ainda não cadastrados. Na primeira competência, perguntar à contadora antes de lançar qualquer pagamento a sócio e registrar aqui.

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
