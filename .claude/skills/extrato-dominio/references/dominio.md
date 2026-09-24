# Importação de lançamentos no Domínio (Thomson Reuters)

## Formato gerado

Por padrão o script gera um TXT **delimitado por ponto e vírgula**, uma linha por
lançamento (uma partida simples: 1 débito × 1 crédito), sem cabeçalho:

```
DATA;CONTA_DEBITO;CONTA_CREDITO;VALOR;HISTORICO;COMPLEMENTO
05/08/2026;7;512;1250,00;;PIX RECEBIDO JOAO DA SILVA
06/08/2026;415;7;39,90;;TARIFA PACOTE SERVICOS
```

- Data `dd/mm/aaaa`; valor com vírgula decimal e sem separador de milhar.
- Contas = **código reduzido** do plano de contas da empresa no Domínio.
- Histórico = código de histórico padrão do Domínio (pode ficar vazio; o texto vai no complemento).
- Encoding Windows (ANSI/cp1252) e quebra de linha CRLF, que é o que o Domínio lê sem
  estragar acentos.

## Como importar no Domínio

1. Módulo **Contabilidade**, com a empresa correta aberta.
2. Menu **Arquivo → Importação → Importação de Lançamentos** (o nome exato pode variar
   um pouco conforme a versão).
3. Na primeira vez, cadastre um **leiaute de importação** do tipo *separado por caractere*,
   com separador `;` e os campos **na mesma ordem** do `layout_txt.campos` da empresa
   (data, conta débito, conta crédito, valor, código do histórico, complemento).
   Depois é só reutilizar o leiaute.
4. Selecione o TXT, confira a prévia e importe. O Domínio aponta contas inexistentes ou
   inválidas; se isso ocorrer, corrija o código no JSON da empresa e gere de novo.

## Ajustando o layout

Se o escritório já tem um leiaute cadastrado no Domínio com outra ordem ou outros
campos, ajuste `layout_txt` no JSON da empresa em vez de mudar o Domínio.
Campos disponíveis para `layout_txt.campos`:

| Campo | Conteúdo |
|---|---|
| `data` | data do movimento (formato em `formato_data`) |
| `conta_debito` / `conta_credito` | códigos reduzidos |
| `valor` | valor absoluto (decimal em `decimal`) |
| `historico` | código do histórico padrão |
| `complemento` | texto do lançamento (limitado a `tam_max_complemento`) |
| `documento` | número do documento do extrato |
| `codigo_empresa` | código da empresa no Domínio |
| `cnpj` | CNPJ só com números |
| `filial` | valor do campo `filial` do JSON |
| `vazio` | coluna vazia (para pular posições) |

Outras opções: `separador`, `formato_data` (sintaxe Python, ex. `%d%m%Y`), `decimal`
(`,` ou `.`), `encoding`, `quebra_linha`, `cabecalho` (true/false).

Se o usuário tiver um TXT que o Domínio já aceitou, compare com ele e ajuste o
`layout_txt` para ficar idêntico. Esse é o jeito mais seguro de acertar o formato.
