# Importação de lançamentos no Domínio (Thomson Reuters)

## Formato padrão do escritório (`"formato": "dominio"`)

É o leiaute padrão de lançamentos contábeis do Domínio, confirmado com arquivos que o
Domínio já aceitou (empresa 60, Kopp, 02/2026). Campos separados por `|`, encoding
Windows (cp1252), quebra de linha CRLF:

```
|0000|02967738000158|
|6000|X||||
|6100|02/02/2026|651|8|180,00||REF. A SISPAG FORNECEDORES||||
|6000|X||||
|6100|02/02/2026|8|504|3384,84||REF. A RECEBIMENTO MOV TIT COB DISP 02/02S||||
```

| Registro | Conteúdo |
|---|---|
| `0000` | CNPJ da empresa, só números (uma vez, no início) |
| `6000` | abre um lote; `X` = um débito para um crédito |
| `6100` | data · conta débito · conta crédito · valor (vírgula, sem milhar) · código do histórico (vazio) · complemento · 4 campos vazios |

- Contas = **código reduzido** do plano de contas da empresa.
- O complemento leva o prefixo `REF. A ` (campo `prefixo_complemento` no JSON da empresa)
  mais a descrição do extrato.
- O escritório gera **dois arquivos por extrato**, `_PAGAR` (saídas: D despesa / C banco)
  e `_RECEBER` (entradas: D banco / C cliente). É o `separar_pagar_receber: true` do JSON.
  Os arquivos saem com o nome `<saída>_PAGAR.txt` e `<saída>_RECEBER.txt`.

## Histórico: ler TXT antigos do Domínio

Os TXT de meses anteriores servem de histórico. Com eles dá para criar as regras de uma empresa
nova ou conferir se as regras reproduzem o que o escritório fez:

```bash
python scripts/extrato_dominio.py ler MES_PAGAR.txt --juntar MES_RECEBER.txt -e empresas/<empresa>.json -o historico.csv
```

O CSV sai já com a coluna `conta` (a contrapartida). O sinal do valor vem de qual lado
está a `conta_banco`. Agrupe por descrição e conta para montar as regras.

## Plano de contas

```bash
pip install olefile   # só na primeira vez
python scripts/plano_contas.py Contas.xls -o contas.json
```

Gera `{codigo_reduzido: "classificação nome"}` só com as contas analíticas. Cole o resultado
no campo `contas` do JSON da empresa. O .xls exportado pelo Domínio costuma vir com estrutura
interna inconsistente, e o Excel antigo, o xlrd e o LibreOffice recusam abrir; o script tem leitor próprio.

## Como importar no Domínio

Módulo **Contabilidade**, com a empresa aberta, na rotina de importação de lançamentos
(Arquivo → Importação), usando o leiaute padrão do Domínio. Importe o `_PAGAR` e o `_RECEBER`.
O Domínio avisa se alguma conta não existir.

## Formato alternativo (`"formato": "delimitado"`)

Para leiautes personalizados, com uma linha por lançamento e separador configurável, use
`layout_txt.formato = "delimitado"` e defina `campos` (ordem), `separador`, `cabecalho`.
Campos disponíveis: `data`, `conta_debito`, `conta_credito`, `valor`, `historico`,
`complemento`, `documento`, `codigo_empresa`, `cnpj`, `filial`, `vazio`.
