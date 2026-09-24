---
name: extrato-dominio
description: Lança e analisa extratos bancários de empresas clientes de escritório de contabilidade e gera o arquivo TXT de lançamentos contábeis para importar no sistema Domínio (Thomson Reuters). Lê OFX, CSV e PDF de qualquer banco, classifica cada movimento na conta contábil (débito/crédito), faz conferência de saldo, duplicidades e itens pendentes, e cadastra nova empresa com as suas regras de classificação. Use sempre que o usuário mencionar extrato bancário, conciliação bancária, lançamentos do banco, arquivo OFX, importação no Domínio, "lançar o extrato", "nova empresa" para o escritório, ou pedir um TXT para o Domínio, mesmo sem citar a skill pelo nome.
---

# Extrato bancário → lançamentos no Domínio

Serve para o trabalho de rotina do escritório contábil: pegar o extrato do banco de
uma empresa cliente, transformar cada movimento em lançamento contábil (partida
simples: banco × contrapartida) e entregar um **TXT pronto para importar no Domínio**,
junto com uma análise do extrato.

Fale com o usuário em português do Brasil, em linguagem de escritório contábil
(não de programador). Mostre tabelas curtas, não despeje CSV bruto.

Tudo roda pelo script `scripts/extrato_dominio.py` (Python 3, sem dependências):
`ler`, `classificar`, `analisar`, `gerar`. Rode `--help` se tiver dúvida.

## 1. Identificar a empresa (ou cadastrar uma nova)

Cada empresa tem um arquivo de configuração JSON em `empresas/` na pasta de trabalho
(ex.: `empresas/0123-padaria-pao-doce.json`). Ele guarda o código da empresa no
Domínio, a conta do banco, o plano de contas usado e as **regras de classificação**
aprendidas nos meses anteriores. É isso que faz o trabalho ficar mais rápido a cada mês.

- Se já existir o arquivo da empresa, use-o.
- Se for **nova empresa**, copie `assets/empresa_modelo.json` e preencha com o usuário:
  - código da empresa no Domínio, razão social, CNPJ, regime tributário;
  - `conta_banco`: código reduzido da conta do banco no plano de contas do Domínio
    (uma empresa com vários bancos tem uma conta para cada banco; use a do extrato atual,
    ou crie um JSON por conta bancária);
  - `conta_transitoria`: conta para itens não identificados (opcional);
  - `contas`: código reduzido → nome. Se o usuário mandar o plano de contas exportado
    do Domínio (PDF, Excel, TXT), extraia dele. Sem plano de contas, **pergunte** os
    códigos; nunca invente código de conta, porque um código errado faz o Domínio
    rejeitar a importação ou, pior, lançar na conta errada.
  - Troque os `"0000"` das regras-modelo pelos códigos reais, ou remova as regras
    que não se aplicam.

## 2. Ler o extrato

```bash
python scripts/extrato_dominio.py ler <extrato.ofx|.csv> -o trabalho/normalizado.csv
```

- **OFX** é o melhor formato (todo banco exporta, vem com saldo). Prefira pedir OFX.
- **CSV/Excel**: o script detecta as colunas de data, descrição, valor ou crédito/débito.
  Para `.xlsx`, converta para CSV antes.
- **PDF**: extraia as linhas (use a skill de PDF, se disponível, ou `pdftotext -layout`)
  e monte um CSV `data;descricao;documento;valor` com saídas negativas, depois rode `ler`
  nele. Confira o total com o PDF, pois a extração de PDF pode perder linhas.

Anote o período, o total de entradas e saídas e, no OFX, o saldo final.

## 3. Classificar

```bash
python scripts/extrato_dominio.py classificar trabalho/normalizado.csv -e empresas/<empresa>.json -o trabalho/classificado.csv
```

As regras do JSON classificam o que já é conhecido. Para os **pendentes** (o script os
lista agrupados por descrição):

1. Leia `references/classificacao.md` e sugira a contrapartida de cada grupo usando o
   plano de contas da empresa.
2. Mostre ao usuário uma tabela: descrição | entrada/saída | qtd | total | conta sugerida.
   Marque com ⚠️ o que exige confirmação: sócios, pessoas físicas, empréstimos,
   transferências e valores atípicos.
3. Com a confirmação, preencha as colunas `conta` (e `historico`/`complemento`, se quiser)
   no `classificado.csv`. Linhas que já têm conta são preservadas se o `classificar`
   for rodado de novo.
4. **Grave regras novas no JSON da empresa** para os padrões que se repetem
   (ex.: `{"nome": "Energia", "tipo": "saida", "contem": ["CEMIG"], "conta": "452"}`).
   Use termos específicos o bastante para não capturar movimento errado; `nao_contem`
   e `regex` ajudam. A primeira regra que casa vence, então regras específicas vão antes
   das genéricas. Não crie regra para um movimento isolado de natureza incerta.

## 4. Analisar

```bash
python scripts/extrato_dominio.py analisar trabalho/classificado.csv -e empresas/<empresa>.json --saldo-inicial "10.000,00" --saldo-final "12.345,67"
```

Informe os saldos quando tiver (OFX traz o final; o inicial vem do extrato ou do
balancete do mês anterior). O relatório mostra totais, conferência de saldo,
possíveis duplicidades, pendentes, total por conta e maiores valores. Traga para o
usuário um resumo curto com o que pede atenção, não o relatório inteiro.

## 5. Gerar o TXT do Domínio

```bash
python scripts/extrato_dominio.py gerar trabalho/classificado.csv -e empresas/<empresa>.json -o <EMPRESA>_<AAAA-MM>_lancamentos.txt
```

- Entrada: **D banco / C contrapartida**. Saída: **D contrapartida / C banco**.
- O script recusa gerar com pendentes. Com o aval do usuário, `--usar-transitoria`
  lança os pendentes na conta transitória, e isso deve ser avisado no resumo final.
- O formato (ordem dos campos, separador, data, decimal, encoding) vem de `layout_txt`
  no JSON. Leia `references/dominio.md` para ajustar o layout e para as instruções de
  importação. Se o usuário tiver um TXT que o Domínio já aceitou, alinhe o layout a ele.

## Entrega

Entregue:
1. o arquivo `.txt` para importação;
2. um resumo: período, quantidade de lançamentos, entradas, saídas, conferência de saldo,
   itens em transitória ou pendentes e alertas (sócios, duplicidades, valores atípicos);
3. o JSON da empresa atualizado com as regras novas, dizendo que ele deve ser guardado
   para o próximo mês;
4. na primeira vez, o passo a passo curto de importação no Domínio (`references/dominio.md`).
