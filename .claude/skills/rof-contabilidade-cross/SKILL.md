---
name: rof-contabilidade-cross
description: "CROSS REPRESENTACAO LTDA, CNPJ 52.164.932/0001-73, Simples Nacional, representação comercial, bancos Cresol (8), Viacredi (9), Caixa (5). Lançamentos, conciliação e TXT único Domínio. Use quando Rosangela/Elen enviarem extrato/OFX, razão, plano de contas ou pedirem lançamentos desta empresa."
---

# ROF Contabilidade CROSS — Lançamentos e Conciliação

## Dados da Empresa

| Campo | Informação |
|---|---|
| Razão social | CROSS REPRESENTACAO LTDA |
| CNPJ | 52.164.932/0001-73 (sem formatação: 52164932000173) |
| CNAE principal | 46.18-4-01 — Rep. comerciais de medicamentos, cosméticos e perfumaria |
| CNAEs secundários | 46.17-6-00 (alimentos/bebidas/fumo); 73.19-0-02 (promoção de vendas) |
| Setor | Representação comercial |
| Regime | Simples Nacional |
| Bancos | Cresol conta 047602-1 → **8** · Viacredi 22375740 → **9** · Caixa Geral → **5** |
| Cadastrado por | Rosangela |
| Contadora | Renata Bastos Amado (CRC-PR 075217/O-2) — Paes e Bastos Contabilidade |

## Sócios (dois com o mesmo nome — pai e filho)

| Sócio | CPF | Conta |
|---|---|---|
| Marcos Antonio Rodrigues Assunção (administrador/pai) | 600.549.219-53 | **534** |
| Marcos Antonio Rodrigues Assunção Filho | 066.051.229-76 | **535** |

> Distinguir SEMPRE pelo CPF do TED/PIX: `...60054921953` = pai (534); `...06605122976` = filho (535). Em PIX sem CPF, classificar no pai (534) e sinalizar "(IDENTIFICAR)" para confirmação.

## REGRA — Pagamento a Sócio (pró-labore + excedente)

**Todo pagamento a sócio no mês: paga PRIMEIRO o pró-labore líquido, e o excedente vai para a conta do sócio (534 pai / 535 filho).**

- Até o pró-labore líquido → **débito 188 (PRÓ-LABORE A PAGAR)** / crédito banco.
- Excedente → **débito 534 (conta do sócio pai — retirada/distribuição)** / crédito banco. Para o filho, excedente → **535**.
- Aplicar o pró-labore à primeira transferência do mês, somando os dois bancos (dividir a linha em duas se necessário: parte 188, parte 534).

| Sócio | Base pró-labore | INSS 11% | Líquido (→188) | Excedente |
|---|---|---|---|---|
| Pai | R$ 3.242,00 | R$ 356,62 | **R$ 2.885,38** | → **534** |
| Filho | salário mínimo nacional vigente (R$ 1.621,00 em 2026 — atualizar no reajuste) | base × 11% | base − INSS | → **535** |

## Leiaute TXT Domínio

```
|0000|52164932000173|
|6000|X||||
|6100|DD/MM/AAAA|DEBITO|CREDITO|VALOR||HISTORICO||||
```
- Um `|6000|X|||` por lançamento. Valor com vírgula (1500,00). Arquivo único, todos os bancos, ordenado por data.
- Recebimento: débito banco / crédito **504**. Pagamento: débito conta / crédito banco.

## Regra de Classificação

1. Recebimento → crédito **504** (clientes diversos). Receita reconhecida por NF (504/411).
2. **PF (exceto sócios) → sempre 362.**
3. **CNPJ → classificar pela atividade** (lista recorrente abaixo).
4. **Sócio → regra pró-labore/excedente** (188 até o líquido; excedente → 534 pai / 535 filho), distinguindo pai/filho por CPF.
5. Histórico: copiar como no extrato.

### Classificações recorrentes confirmadas

| Favorecido / descrição | Conta |
|---|---|
| Condor, Benevi, iFood, Atacadão, Zamp, açaí, cafés | 521 (alimentação) |
| Copel | 354 · Sanepar | 355 · TIM/Vivo/Claro | 356 |
| Unimed | 538 · Icatu/HDI/seguros | 358 · Paes e Bastos/RBA | 510 |
| 99 Tecnologia, Fiz Transportes, Opera Park, Detran | 493 (veículo) |
| Toallitas, Mark1, Bytedance, SHPP, Marketplace, AH Beauty, Sem Parar | 365 (diversas) |
| **CROSS COM E REPRES LTDA** | **506** (pagamento a PJ — NÃO é transferência entre contas: não há crédito correspondente no outro banco) |
| **Banco Bradesco, Safra CFI, Banco do Brasil** (PG.P/INTERNET) | **506** |
| **DAS / Simples** | **479** · **DARF (INSS)** → **191** |
| Aplicação para conta investimento; DB. COTAS | **48** (aplicação financeira) |
| Integralização programa capitalização | 528 |
| Pacote de serviços / desp. bancária | 528 · Tarifa PJ | 369 · IOF | 527 · Juros | 372 |
| PGT.FATURA CARTAO / CARTAOCRED | **359** · IPTU | **350** |
| Devolução PIX recebida | estornar na mesma conta do pagamento original |

## Regra Inviolável — Conferência de Saldo

> Conferir por banco: abertura (= fechamento do mês anterior) + entradas − saídas = **saldo do extrato**. Em OFX, bater com o `LEDGERBAL`; em PDF, com o saldo final. E Σ débitos = Σ créditos. Preferir OFX direto do banco — arquivos convertidos já vieram incompletos (faltando lançamentos e saldo).

## Regra — Duplicatas no OFX

> O OFX (Cresol) pode trazer linhas duplicadas com **data fora da competência** (ex.: aplicação/capitalização datadas de mês futuro, sem número de identificação). Excluir essas linhas — a prova é que o banco só fecha (LEDGERBAL) sem elas. Manter as versões reais (com ID completo, na data correta).

## Alerta de Duplicidade na Importação

> O balancete/razão pode já conter o mês (import anterior via Otimizza). Antes de reimportar o TXT, confirmar com Rosangela se o lançamento anterior daquele mês foi removido do Domínio.

## Fluxo

1. Receber extrato/OFX (Cresol e Viacredi), plano de contas e razão.
2. Classificar cada lançamento (natureza → favorecido → conta), aplicar regras acima.
3. Excluir duplicatas fora da competência.
4. Conferir saldo de cada banco contra o extrato/LEDGERBAL.
5. Gerar TXT único ordenado por data.
6. Entregar junto a planilha de retiradas dos sócios (pró-labore × excedente, quebra por banco).

---

## Padrão ROF — Pró-labore, Retiradas e Relatório do Sócio

> Regra validada pela contadora Rosangela em 24/09/2026 para todas as empresas do escritório.
> As regras específicas desta empresa descritas acima **continuam valendo**. Este bloco completa o que faltar e **não substitui** nenhuma conta, exceção ou classificação já confirmada. Em caso de conflito, prevalece a regra específica da empresa.

### Parâmetros desta empresa

| Sócio | CPF | Pró-labore | Conta pró-labore a pagar | Conta do sócio (retirada / aporte) |
|---|---|---|---|---|
| Sócio pai | final ...60054921953 | Variável — perguntar todo mês (última referência: base R$ 3.242,00) | **188** | **534** |
| Sócio filho | final ...06605122976 | Variável — perguntar todo mês | **188** | **535** |

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
