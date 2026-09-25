---
name: extrato-dominio
description: Padrão do escritório de contabilidade para cadastrar NOVA EMPRESA e para lançar e conciliar extratos bancários, gerando o TXT de lançamentos contábeis aceito pelo sistema Domínio (Thomson Reuters). Cadastro de nova empresa com responsável (Elen ou Rosangela), análise do cartão CNPJ, perguntas sobre regime, sócios e práticas, e pedido de balancete, relatório de entradas e razão. Lê extratos OFX, CSV e PDF de qualquer banco, classifica cada movimento em débito/crédito, confere saldo e duplicidades e pergunta tudo o que gerar dúvida. Use sempre que o usuário disser "nova empresa", mandar CNPJ para cadastrar cliente, mencionar extrato bancário, conciliação bancária, lançamentos do banco, OFX, importação no Domínio, "lançar o extrato", razão ou balancete de cliente, ou pedir TXT para o Domínio, mesmo sem citar a skill.
---

# Padrão do escritório: nova empresa e extrato bancário → Domínio

Esta skill segue o padrão de trabalho do escritório contábil. Ela cadastra cada empresa
cliente do mesmo jeito e transforma o extrato bancário em lançamentos contábeis (banco ×
contrapartida), entregues num **TXT pronto para importar no Domínio**, junto com a análise
do extrato.

Fale em português do Brasil, em linguagem de escritório contábil (não de programador).
Mostre tabelas curtas, nunca CSV bruto.

**Leia `references/padrao_rof.md` antes de qualquer trabalho.** São as regras do escritório
que valem para todas as empresas e todas as skills: acordo com a contadora, validação de cada
lançamento (CONFIRMADO/PROVÁVEL/NÃO CRUZADO/DIVERGENTE), regras invioláveis, impostos, folha,
sócios e a estrutura da skill de cada empresa.

Scripts (Python 3; `plano_contas.py` precisa de `pip install olefile`; `folha_extrato_mensal.py`, de `pip install pdfplumber`):
- `scripts/consulta_cnpj.py`: consulta e analisa o cartão CNPJ.
- `scripts/plano_contas.py`: converte o `Contas.xls` exportado do Domínio.
- `scripts/extrato_dominio.py`: `ler`, `classificar`, `analisar`, `gerar` (`--help` mostra as opções).
- `scripts/folha_extrato_mensal.py`: `ler` (Extrato Mensal da folha do Domínio → registro) e `conferir` (folha × extrato).
- `scripts/impostos_dominio.py`: `ler` (demonstrativos XLS e Resumo dos Impostos PDF) e `conferir` (guias × extrato).
- `scripts/entradas_dominio.py`: `ler` (Acompanhamento de Entradas do Domínio → notas com retenções) e `conferir` (notas × pagamentos).
- `scripts/gerar_skill_empresa.py`: gera a skill da empresa `rof-contabilidade-<empresa>` a partir do JSON.

**Dados de clientes são sigilosos** (CPF, salários, extratos, plano de contas): nunca os envie
para repositório público nem para serviço externo. A pasta `empresas/` fica fora do git e é
entregue ao usuário como arquivo.

## Postura: atenção máxima e perguntar sempre na dúvida

Um lançamento errado custa mais do que uma pergunta. A conciliação só fecha se cada
movimento estiver na conta certa. Por isso:

- **Nunca adivinhe conta.** Se a descrição do movimento não deixa claro o que é, pergunte.
  Mandar para a conta transitória em silêncio não resolve: é adiar o problema.
- Pergunte **em lote**: agrupe as dúvidas numa tabela numerada (data, valor, descrição,
  o que você acha que é, opções de conta). Não faça uma pergunta por movimento.
- Sempre confirme: movimentos com **sócios** ou pessoas físicas, **empresas ligadas**,
  empréstimos, transferências entre contas, estornos, valores fora do padrão do mês,
  pagamentos sem descrição, contas usadas de forma incoerente (ex.: conta de receita
  num pagamento) e qualquer padrão do histórico que pareça erro.
- Cada resposta do usuário vira **regra** ou **observação** no JSON da empresa, para a
  pergunta não se repetir no mês seguinte. Registre a decisão e a data em `observacoes`.
- Revise o resultado antes de entregar: total por conta, maiores valores, itens na
  transitória. Pergunte se algo parecer estranho.

## 1. Nova empresa (roteiro padrão)

Quando o usuário disser "nova empresa" ou trouxer um cliente sem cadastro, siga
**`references/nova_empresa.md`** na ordem:

1. **Responsável**: "Com quem será feito o lançamento contábil: **Elen** ou **Rosangela**?"
2. **CNPJ**: peça o número, rode `consulta_cnpj.py` e apresente a análise do cartão CNPJ
   com o que ela muda na contabilização.
3. **Sistema**: pergunte sempre se a empresa **utiliza o Domínio** (e o código da empresa nele).
4. **Perguntas sobre a empresa**: regime tributário, CPF dos sócios, pró-labore, bancos,
   formas de recebimento e pagamento, folha, empréstimos, empresas ligadas, e as dúvidas
   adicionais que a análise levantar.
5. **Documentos**: balancete, relatório de entradas e razão dos últimos meses (mais o
   plano de contas e os TXT antigos, se houver), para seguir o padrão de lançamentos do escritório.
6. **Confirmação**: mostre o resumo do cadastro, salve `empresas/<codigo>-<nome>.json`
   (modelo em `assets/empresa_modelo.json`) e entregue ao usuário.
7. **Skill da empresa**: gere a skill própria no padrão ROF e entregue o `.skill` para instalar:
   `python scripts/gerar_skill_empresa.py empresas/<arquivo>.json [--folha empresas/<cod>-folha.csv] --nome <empresa> -o saida/`.
   Nos meses seguintes, o trabalho daquela empresa usa essa skill. Regere a skill sempre que
   uma decisão nova for registrada no JSON.

Se a empresa já tem JSON em `empresas/`, use-o. Confira `pendencias` e pergunte o que
ainda estiver em aberto antes de lançar.

## 2. Ler o extrato

```bash
python scripts/extrato_dominio.py ler <extrato.ofx|.csv> -o trabalho/normalizado.csv
```

- **OFX** é o melhor formato (todo banco exporta, vem com saldo). Prefira pedir OFX.
- **CSV**: o script detecta as colunas de data, descrição e valor (ou crédito/débito).
  Converta `.xlsx` para CSV antes.
- **PDF**: extraia as linhas (skill de PDF ou `pdftotext -layout`), monte um CSV
  `data;descricao;documento;valor` com saídas negativas e rode `ler` nele. Confira os totais
  com o PDF.
- **TXT antigo do Domínio** (histórico): `ler MES_PAGAR.txt --juntar MES_RECEBER.txt -e <empresa.json>`
  gera o CSV já com as contas usadas. Serve para criar e validar regras.

## 3. Classificar

```bash
python scripts/extrato_dominio.py classificar trabalho/normalizado.csv -e empresas/<empresa>.json -o trabalho/classificado.csv
```

As regras do JSON classificam o que já é conhecido (a primeira que casa vence; as
específicas ficam antes das genéricas). Para os **pendentes**, que o script lista agrupados:

1. Use `references/classificacao.md`, o plano de contas (`contas` no JSON), o razão e o
   relatório de entradas da empresa para sugerir a conta.
2. Monte a tabela de dúvidas (ver "Postura") e **pergunte**.
3. Preencha a coluna `conta` no `classificado.csv` com as respostas. Linhas que já têm
   conta são preservadas se o `classificar` for rodado de novo.
4. Grave regras novas no JSON para os padrões recorrentes, com termos específicos o
   bastante para não capturar movimento errado (`nao_contem` e `regex` ajudam;
   `dia_de`/`dia_ate` limitam a regra a dias do mês).

### Notas de fornecedores (relatório de entradas)

O relatório **Acompanhamento de Entradas** do Domínio identifica a quem foi cada pagamento:

```bash
python scripts/entradas_dominio.py ler Entradas.xls -o empresas/<cod>-entradas.csv [--acrescentar]
python scripts/entradas_dominio.py conferir trabalho/classificado.csv -n empresas/<cod>-entradas.csv \
    -e empresas/<empresa>.json [--aplicar trabalho/classificado_nf.csv]
```

- Confira o total lido com o "Total Geral" do relatório.
- O valor pago pode ser o **valor da nota**, o **líquido das retenções** (IRRF, CRF, ISS e INSS
  retidos, que vêm logo abaixo da nota) ou uma **parcela** do boleto.
- Níveis de evidência: **NOME + VALOR** (forte), **SÓ VALOR** (pagamento em lote sem nome, como
  SISPAG, com uma única nota possível), **SÓ NOME** (valor não bate: parcela, juros ou várias
  notas), **VÁRIAS NOTAS** (perguntar) e **SEM NOTA** (nota fora do período do relatório,
  adiantamento, securitizadora ou despesa sem nota: perguntar).
- **Padrão do escritório:** a nota já é contabilizada pela Escrita Fiscal, então o pagamento é
  **D 506 Fornecedor Modelo / C Banco** (`conta_fornecedores`). `--aplicar` grava NOME + VALOR como
  CONFIRMADO e SÓ VALOR como PROVÁVEL.
- **Sem nota fiscal** (e só nome ou várias notas): **informe o usuário** numa tabela e identifiquem
  juntos. Nunca lance por suposição.
- Todo mês o usuário envia, junto com o extrato, o **relatório de entradas** e uma **planilha
  mensal de conciliação**: use os dois como evidência antes de perguntar.

### Impostos (demonstrativos e resumo do Domínio)

```bash
python scripts/impostos_dominio.py ler Demonst*.xls Resumo_impostos.pdf -o empresas/<cod>-impostos.csv [--acrescentar]
python scripts/impostos_dominio.py conferir trabalho/classificado.csv -i empresas/<cod>-impostos.csv \
    -e empresas/<empresa>.json [--aplicar trabalho/classificado_impostos.csv]
```

- O **XLS de demonstrativos** traz uma aba por imposto e competência (ICMS, IPI, IRRF, CRF, ISS
  retido, INSS retido, IRPJ e CSLL trimestrais), com o código da receita no nome da aba. O **PDF
  "Resumo dos Impostos"** traz também **PIS e COFINS**. Leia os dois.
- A guia do mês M é da competência M−1 (IRPJ/CSLL: do trimestre, em cota única ou 3 quotas).
  Cada guia vai na **sua** conta (`contas_impostos`; padrão do plano do escritório: ICMS 172,
  IPI 171, IRRF 178, CRF 182, ISS retido 183, INSS retido 184, IRPJ 176, CSLL 177, PIS 179,
  COFINS 180). Enquanto a contadora não confirmar as contas da empresa, o status é PROVÁVEL; depois
  de confirmadas, grave `"contas_impostos_confirmadas": true` no JSON e as guias que batem com o
  demonstrativo entram como CONFIRMADO.
- Guia sem demonstrativo (valor não bate: multa/juros, parcelamento, DIFAL, outra competência):
  **informe o usuário** e peça o comprovante.

### Folha de pagamento

Padrão do escritório: **dois pagamentos por mês** aos funcionários.

| Quando | O que é | Lançamento |
|---|---|---|
| Início do mês (dia 1 a 10) | Salário líquido do mês anterior | D Salários a pagar / C Banco |
| Dia 15 a 20 | Adiantamento de salário | D Adiantamento de salário (ativo) / C Banco |

As regras usam a data (`"dia_de": 1, "dia_ate": 10` e `"dia_de": 15, "dia_ate": 20`).
Um pagamento de salário **fora dessas datas** fica pendente de propósito: pode ser
rescisão, férias, 13º, pensão ou um acerto. Pergunte.

O usuário envia o **relatório da folha** (Extrato Mensal do Domínio: Adiantamento e Folha
Mensal) todo mês. Se ele ainda não veio, peça antes de fechar os lançamentos de folha.
Registre e confira:

```bash
python scripts/folha_extrato_mensal.py ler Extrato_Mensal*.pdf -o empresas/<cod>-folha.csv --acrescentar
python scripts/folha_extrato_mensal.py conferir trabalho/classificado.csv -f empresas/<cod>-folha.csv
```

Com `-e empresas/<empresa>.json --aplicar trabalho/classificado_folha.csv`, grava o CSV já com as
contas de `contas_folha` (salario, adiantamento, rescisao, ferias, pro_labore) e status CONFIRMADO.

O `conferir` casa pelo valor exato e pela competência esperada:
- início do mês → salário (e pró-labore) da Folha Mensal da competência anterior;
- dias 15 a 20 → Adiantamento do próprio mês;
- fora do calendário → rescisão. O **líquido da rescisão sai junto com a Folha Mensal**
  (rubrica `LIQUIDO RESCISAO`);
- um pagamento que soma dois valores da mesma pessoa (ex.: adiantamento atrasado + salário)
  é dividido em duas linhas, uma por conta.

Ele lista o que bateu, os pagamentos sem correspondente e os valores da folha sem pagamento.
**Guias da folha**: o `ler` também grava `<cod>-folha-encargos.csv` (FGTS, FGTS rescisório,
INSS e IRRF de cada competência), e o `conferir` acha no extrato a guia do **FGTS Digital**
(FGTS a recolher) e a da **DCTFWeb**, que **sempre é dividida em duas linhas: INSS a recolher +
IRRF a recolher** (padrão do escritório). As contas ficam em `contas_folha` (`fgts`, `inss`, `irrf`).
**Pró-labore de sócio**: o líquido vai para Pró-labore a pagar; qualquer diferença é retirada
de sócio e exige **avisar o usuário antes de lançar**. Depois:
- confira cada pagamento do extrato com o líquido ou o adiantamento de cada funcionário
  (valor exato) e o total de cada lote;
- aponte quem está no relatório e não foi pago, pagamentos sem funcionário
  correspondente, e diferenças de valor;
- identifique rescisões, férias e 13º no relatório para classificar os pagamentos fora
  do calendário (contas próprias do plano, ex.: 13º a pagar, adiantamento de férias).
  Pergunte se a conta não estiver clara.

## 4. Analisar

```bash
python scripts/extrato_dominio.py analisar trabalho/classificado.csv -e empresas/<empresa>.json --saldo-inicial "10.000,00" --saldo-final "12.345,67"
```

O saldo inicial vem do balancete ou razão do mês anterior; o final, do extrato ou OFX.
Uma diferença de saldo significa lançamento faltando ou duplicado: investigue e aponte.
Traga um resumo curto com o que pede atenção.

## 5. Gerar o TXT do Domínio

```bash
python scripts/extrato_dominio.py gerar trabalho/classificado.csv -e empresas/<empresa>.json -o <CODIGO>_<EMPRESA>_<AAAA-MM>.txt
```

O modelo aceito pelo Domínio é **o mesmo para todas as empresas**, e o script já gera
nele: `|0000|CNPJ|`, depois, para cada lançamento, `|6000|X||||` e
`|6100|data|débito|crédito|valor||REF. A descrição||||`. O arquivo sai em cp1252 com CRLF,
dividido em `_PAGAR.txt` (saídas: D contrapartida / C banco) e `_RECEBER.txt` (entradas:
D banco / C contrapartida). Detalhes em `references/dominio.md`.

- **TXT definitivo** exige `--saldo-inicial` e `--saldo-final` (o saldo tem que fechar) e
  todos os lançamentos com status **CONFIRMADO**. Sem isso, o `gerar` recusa. `--previa`
  gera o arquivo com `_PREVIA` no nome, só para conferência, nunca para importar.
- O status vem da regra (`"status"` no JSON; padrão CONFIRMADO). Ao preencher conta à mão,
  preencha também a coluna `status` conforme a resposta da contadora.
- `--usar-transitoria` só com o aval explícito do usuário, e isso deve ser avisado no resumo.
- Empresa que **não** usa o Domínio: siga a etapa 3 de `references/nova_empresa.md`.

## Entrega

1. Os arquivos `_PAGAR.txt` e `_RECEBER.txt`.
2. Um resumo com responsável (Elen/Rosangela), período, quantidade de lançamentos,
   entradas, saídas, conferência de saldo, total por conta, itens em transitória e alertas.
3. A conferência da folha com o relatório (quando houver pagamento de salário).
4. As perguntas que ficaram em aberto, se houver.
5. O JSON da empresa atualizado (regras, decisões e pendências), para guardar para o próximo mês.
