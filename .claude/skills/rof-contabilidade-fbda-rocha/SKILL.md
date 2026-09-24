---
name: rof-contabilidade-fbda-rocha
description: "Conciliação bancária, classificação contábil e geração de TXT Domínio para a FB DA ROCHA LTDA, CNPJ 65.815.958/0001-86. Usar sempre que forem enviados extratos, OFX, PDF, razão, balancete, plano de contas ou TXT dessa empresa, especialmente operações no Sicredi, SicrediInvest, poupança e movimentações do sócio Felipe Bochnia da Rocha."
---

# Skill empresarial — FB DA ROCHA

## Identificação permanente

Tratar a empresa como **FB DA ROCHA** ou **F B DA ROCHA LTDA**, CNPJ **65.815.958/0001-86**. A atividade principal informada é CNAE **8211-3/00**; atividades secundárias: **7020-4/00**, **8219-9/99** e **8599-6/04**. O banco é **Sicredi**, cooperativa **0730**, conta corrente **51833-7**, código contábil **8**.

Usar a FWS somente como referência metodológica quando necessário. Não transportar automaticamente contas, códigos, pró-labore, rateios ou regras da FWS para esta empresa.

## Regras contábeis validadas

Aplicar as regras seguintes somente após conferir a competência e o extrato original:

| Código | Conta | Uso validado |
|---:|---|---|
| 8 | Banco do Sicredi 51833-7 | Conta corrente principal |
| 48 | Aplicação SicrediInvest CDI100 | Aplicações e resgates do investimento |
| 71 | Aplicação Sicredi Poupança | Aplicações e resgates da poupança na referência atual |
| 504 | Clientes Diversos | Recebimentos de clientes quando a operação confirmar receita de cliente |
| 530 | Felipe Bochinia da Rocha (CPF 080.233.039-88) | Toda movimentação bancária do sócio |
| 479 | Simples Nacional a Recolher | Pagamentos à Receita Federal quando a guia confirmar o tributo |
| 510 | Honorários Contábeis | Pagamentos à contabilidade quando a natureza for confirmada |
| 370 | Despesas Bancárias | Tarifas e históricos recorrentes do banco (ver abaixo) |

**Não usar a conta 11 (POUPANÇA, 1.1.1.03.001)** para a poupança da referência atual, embora ela exista no plano. A poupança em uso é a **71**. Só mudar mediante orientação expressa da contadora.

### Favorecidos recorrentes

| Favorecido | CNPJ/CPF | Conta |
|---|---|---:|
| ALIANÇA LOCAÇÃO DE BETONEIRAS E MÁQUINAS LTDA — cliente único da empresa | 12.475.825/0001-41 | 504 |
| FELIPE BOCHNIA DA ROCHA — sócio | 080.233.039-88 | 530 |
| RECEITA FEDERAL | 00.394.460/0058-87 | 479 |
| RBA CONTABILIDADE LTDA — honorários contábeis | 29.650.531/0001-01 | 510 |

O CNPJ 29.650.531/0001-01 aparecia até 07/2026 como **PAES E BASTOS CONTABILIDADE** e a partir de 08/2026 como **RBA CONTABILIDADE LTDA**. É a mesma empresa, com alteração de razão social. Não tratar como fornecedor novo; manter a conta 510.

### Históricos bancários já classificados

| Histórico no extrato | Conta | Observação |
|---|---:|---|
| `INTEGR.CAPITAL SUBSCRITO` — R$ 20,00 mensais | 370 | Decisão confirmada por Everton em 09/2026: **manter em 370**. Tecnicamente é integralização de cota-parte na cooperativa (natureza patrimonial, não despesa), mas a série histórica está lançada assim desde 04/2026. Não reclassificar por iniciativa própria. |
| `RENOVACAO CH. ESP.` — tarifa de renovação do limite | 370 | Validado em 08/2026. É tarifa, não juros — não usar a conta 374 (Juros e Comissões Bancárias). |
| `APLIC.FINANC.AVISO PREVIO-CAPTACAO` | 48 | Aplicação no SicrediInvest: D 48 / C 8 |
| `APLICACAO POUPANCA-CAPTACAO` | 71 | Aplicação na poupança: D 71 / C 8 |
| `TRANSFERENCIA DA POUPANCA` | 71 | Resgate: D 8 / C 71 |

### Sócio

O sócio é **Felipe Bochnia da Rocha**, CPF **080.233.039-88**. Não existe pró-labore fixo validado para esta empresa. Não aplicar salário mínimo, rateio da FWS, INSS ou conta de serviços de terceiros por iniciativa própria.

Toda saída identificada no extrato em nome ou CPF do sócio deve ser lançada exclusivamente em **D 530 / C 8**. Toda entrada identificada em nome ou CPF do sócio deve ser lançada exclusivamente em **D 8 / C 530**. Não utilizar outra conta para essas movimentações, salvo orientação posterior expressa da contadora acompanhada de justificativa.

**Monitorar a conta 530 a cada competência.** O padrão da empresa é repasse de 85% a 95% de tudo que o cliente paga, quase sempre no mesmo dia do recebimento, e a conta **nunca registrou lançamento a crédito** — nenhuma devolução, compensação ou baixa. Em 31/08/2026 o saldo devedor acumulado era de R$ 99.351,00 em 26 saques desde 04/2026.

Ao fechar cada competência, informar a posição da 530 e sinalizar as exposições, sem alterar a classificação:

- ausência total de pró-labore, sendo o sócio-administrador segurado obrigatório como contribuinte individual (art. 12, V, "f", da Lei 8.212/91);
- se a 530 caracteriza mútuo, há incidência de IOF (art. 13 da Lei 9.779/99), sem recolhimento identificado;
- retiradas que superem o lucro apurado deixam de ser distribuição isenta e viram rendimento tributável na pessoa física (art. 238 do RIR/2018). Em 30/06/2026 as retiradas já alcançavam 89,9% do lucro acumulado.

A decisão sobre instituir pró-labore, formalizar distribuição de lucros ou contratar mútuo é da contadora. A skill apenas registra e alerta.

### Investimentos e poupança

Lançar aplicações que saem da conta corrente pela conta do produto: **D 48 / C 8** para SicrediInvest e **D 71 / C 8** para Poupança. Não registrar rendimento provisionado como entrada bancária — o SicrediInvest acumula rendimento provisionado no extrato do produto e ele **não entra no TXT**.

A poupança é POUPANÇA TRADICIONAL, conta 51833-7, aniversário no dia 10. Até 08/2026 o extrato do produto acusa rendimento 0,00 e IRRF 0,00. Conferir mesmo assim a cada competência: havendo crédito de rendimento, tratá-lo com a contadora antes de lançar.

### Cheque especial

A empresa opera com limite de cheque especial de R$ 1.500,00 e entra em saldo negativo intradiário com frequência, zerando no mesmo dia com o recebimento do cliente. Isso é normal nesta empresa e não gera lançamento por si só. O CET do produto é elevado (309,27% ao ano em 08/2026); mencionar no parecer apenas se houver juros efetivamente debitados.

## Fluxo obrigatório de conciliação

1. Identificar a competência pelo período real do extrato. Não misturar conteúdo de meses diferentes.
2. Tratar o **extrato bancário original** — OFX, PDF ou arquivo bancário equivalente — como fonte principal.
3. Conferir saldo inicial, total de créditos, total de débitos e saldo final pela equação `saldo inicial + créditos - débitos = saldo final`.
4. Confrontar OFX e PDF/XLS por data, valor, direção e histórico. Se houver diferença, interromper a classificação, revisar as fontes e marcar a conciliação como pendente.
5. Conciliar conta corrente, SicrediInvest e Poupança com os respectivos relatórios. Transferências entre produtos não são receitas ou despesas.
6. Para cada favorecido, pesquisar o CNPJ quando disponível, verificar a atividade econômica e avaliar se a operação faz sentido para a empresa. Não classificar toda pessoa jurídica automaticamente como fornecedor.
7. Escolher a conta mais adequada existente no plano. Mercado, lanchonete, telefonia, tributos, tarifas, honorários, serviços e outras naturezas devem ser distinguidos conforme documento e atividade.
8. Apresentar divergências com **como está**, **como deveria ser**, fonte, fundamento, risco e decisão necessária. Em caso de dúvida real, conversar antes de consolidar.
9. Conferir o encadeamento com a competência anterior: o saldo de abertura do extrato tem de bater com o saldo de fechamento do mês anterior. Se não bater, o TXT anterior não foi importado ou houve lançamento manual — apurar antes de seguir.
10. Após o lançamento, conferir o Razão e o Balancete da competência contra o extrato e os saldos dos produtos.

## Âncoras de continuidade

Saldos de fechamento confirmados, para validar o mês seguinte. **Atualizar a cada competência encerrada.**

| Conta | Descrição | 30/06/2026 | 31/07/2026 | 31/08/2026 |
|---:|---|---:|---:|---:|
| 8 | Banco Sicredi 51833-7 | 167,86 | 92,08 | 272,96 |
| 48 | SicrediInvest CDI100 | 1.000,00 | 1.800,00 | 1.800,00 |
| 71 | Sicredi Poupança | 100,00 | 200,00 | 300,00 |
| 530 | Felipe Bochnia da Rocha | 55.651,00 | 83.551,00 | 99.351,00 |

Lucro acumulado até 30/06/2026 conforme Balancete: R$ 61.914,55.

## Controle de competência

Arquivos de meses anteriores podem ser usados somente como **referência estrutural do leiaute**. Nunca copiar datas, valores ou históricos de um mês para o TXT de outro. Antes da entrega, verificar todos os registros `|6100|` e confirmar que pertencem à competência solicitada.

## Leiaute TXT Domínio

O modelo histórico aceito observou registros no padrão:

```text
|0000|65815958000186|
|6000|X||||
|6100|DD/MM/AAAA|CONTA_DEBITO|CONTA_CREDITO|VALOR||HISTORICO||||
```

Usar valor com vírgula decimal, data `DD/MM/AAAA`, contas numéricas não nulas, histórico preservado do extrato e quebra de linha **CRLF**. Não inserir linha vazia, registro-placeholder, conta 0, valor 0, cabeçalho duplicado ou conteúdo de competência diferente.

O histórico segue o padrão `REF A ` + memo do OFX, preservando o texto original do banco.

Por preferência operacional da Rosangela, gerar **um único TXT consolidado** por competência, com um único cabeçalho e todos os lançamentos de pagamentos e recebimentos em ordem cronológica, salvo se ela pedir separação. Não concatenar dois arquivos prontos, pois isso duplica o cabeçalho e pode gerar lançamento vazio no Domínio. Usar nome curto, por exemplo:

```text
FB DA ROCHA_SICREDI_8-26.txt
```

O nome pode incluir `PAGAR` ou `RECEBER` apenas se a usuária pedir arquivos separados. A aceitação final depende do teste no Domínio; validar estruturalmente antes de entregar e não afirmar que o sistema aceitou sem confirmação.

### Checklist de validação estrutural

Rodar antes de entregar, programaticamente, e reportar o resultado:

- um único `|0000|`, nenhum cabeçalho duplicado;
- contagem de `|6000|` igual à de `|6100|`;
- todas as quebras de linha em CRLF;
- nenhuma linha vazia;
- todas as datas dentro da competência solicitada;
- nenhuma conta nula, zerada, nem débito igual a crédito;
- nenhum valor zero e nenhum separador decimal com ponto;
- recomposição da equação de saldo batendo com o saldo final do extrato e do OFX.

## Notas operacionais

Os relatórios do Domínio (Razão, Balancete, Plano de contas) chegam em `.xls` que o `xlrd` não consegue abrir — acusam OLE2 inconsistente. Converter com LibreOffice antes de ler:

```bash
libreoffice --headless --convert-to csv --outdir out arquivo.xls
```

O extrato do Sicredi costuma vir em dois formatos, OFX e XLS, que devem ser conferidos um contra o outro. Os extratos de SicrediInvest e poupança vêm em PDF — ler com `pdftotext -layout`.

## Entrega padrão

Para cada competência, entregar o TXT com nome curto e, quando solicitado, a planilha analítica e o parecer. Informar expressamente a competência, o número de registros, os totais de pagamentos e recebimentos, o saldo final e as pendências documentais reais. Separar modelo estrutural, dados da competência e arquivo final para evitar confusão.

Quando houver pasta do computador conectada à sessão, gravar os arquivos finais nela além de entregá-los na conversa.

---

## Padrão ROF — Pró-labore, Retiradas e Relatório do Sócio

> Regra validada pela contadora Rosangela em 24/09/2026 para todas as empresas do escritório.
> As regras específicas desta empresa descritas acima **continuam valendo**. Este bloco completa o que faltar e **não substitui** nenhuma conta, exceção ou classificação já confirmada. Em caso de conflito, prevalece a regra específica da empresa.

### Parâmetros desta empresa

| Sócio | CPF | Pró-labore | Conta pró-labore a pagar | Conta do sócio (retirada / aporte) |
|---|---|---|---|---|
| Felipe Bochnia da Rocha | 080.233.039-88 | **Não há** | — | **530** |

> Manter o monitoramento e os alertas da conta 530 descritos acima; incluir a posição acumulada da 530 na aba Resumo.

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
