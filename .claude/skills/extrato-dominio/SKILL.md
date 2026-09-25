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

Scripts (Python 3; `plano_contas.py` precisa de `pip install olefile`):
- `scripts/consulta_cnpj.py`: consulta e analisa o cartão CNPJ.
- `scripts/plano_contas.py`: converte o `Contas.xls` exportado do Domínio.
- `scripts/extrato_dominio.py`: `ler`, `classificar`, `analisar`, `gerar` (`--help` mostra as opções).

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

### Folha de pagamento

Padrão do escritório: **dois pagamentos por mês** aos funcionários.

| Quando | O que é | Lançamento |
|---|---|---|
| Início do mês (dia 1 a 10) | Salário líquido do mês anterior | D Salários a pagar / C Banco |
| Dia 15 a 20 | Adiantamento de salário | D Adiantamento de salário (ativo) / C Banco |

As regras usam a data (`"dia_de": 1, "dia_ate": 10` e `"dia_de": 15, "dia_ate": 20`).
Um pagamento de salário **fora dessas datas** fica pendente de propósito: pode ser
rescisão, férias, 13º, pensão ou um acerto. Pergunte.

O usuário envia o **relatório da folha** todo mês. Se ele ainda não veio, peça antes de
fechar os lançamentos de folha. Com o relatório:
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

- O script recusa gerar com pendentes. `--usar-transitoria` só com o aval explícito do
  usuário, e isso deve ser avisado no resumo.
- Empresa que **não** usa o Domínio: siga a etapa 3 de `references/nova_empresa.md`.

## Entrega

1. Os arquivos `_PAGAR.txt` e `_RECEBER.txt`.
2. Um resumo com responsável (Elen/Rosangela), período, quantidade de lançamentos,
   entradas, saídas, conferência de saldo, total por conta, itens em transitória e alertas.
3. A conferência da folha com o relatório (quando houver pagamento de salário).
4. As perguntas que ficaram em aberto, se houver.
5. O JSON da empresa atualizado (regras, decisões e pendências), para guardar para o próximo mês.
