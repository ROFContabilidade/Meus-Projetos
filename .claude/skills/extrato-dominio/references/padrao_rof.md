# Padrão ROF Contabilidade: regras que valem para todas as empresas e skills

Estas regras vêm das skills validadas pelo escritório (Kopp Instituto, empresa 133, e
F W S Gonçalves, empresa 82) e valem para **toda empresa e toda skill nova**. A skill de cada
empresa (`rof-contabilidade-<empresa>`) repete estas regras e acrescenta as particularidades
dela.

## 1. Acordo de trabalho com a contadora

1. **Fidelidade total** aos dados enviados: não alterar nada sem consultar.
2. **Consulta prévia** antes de qualquer alteração de conta, regra ou histórico.
3. **Base legal** sempre que sugerir um ajuste (lei, IN, artigo).
4. **Não inventar** dados, documentos, contas, históricos, vínculos, regime ou alíquota.
   O que não foi confirmado fica escrito como "não confirmado".
5. **Histórico**: o texto do extrato, sem reescrever. O prefixo, se a empresa usa um
   (ex.: `REF. A `), é configuração da empresa. Quando houver fonte contábil melhor (nota
   fiscal, razão, relatório), confirme com a contadora qual histórico usar.
6. **Razão antigo não conferido não é verdade.** Se o histórico contrariar as regras
   validadas (ex.: salários lançados como serviços de terceiros, impostos em despesas
   diversas), siga a regra e aponte a divergência. Não copie o erro.
7. **Cada empresa em uma conversa separada.** Nunca misture contas, históricos ou dados de
   empresas diferentes.
8. Registre toda decisão com **quem validou e quando** (ex.: "validado por Elen, 08/2026").
   Orientação nova da contadora prevalece e é registrada na skill.

## 2. Validação de cada lançamento

Para cada operação do extrato, antes de classificar, escreva a frase objetiva:
- "Foi feito um pagamento de R$ X, na data DD/MM/AAAA, para [favorecido]"
- "Foi recebido R$ X, na data DD/MM/AAAA, de [favorecido]"

Ordem de classificação:
1. Natureza (entrada ou saída).
2. Favorecido (descrição do extrato, MEMO/CHECKNUM do OFX).
3. Tem CNPJ ou razão social? Consulte na Receita (`consulta_cnpj.py`) e veja se a atividade
   bate com a empresa. Isso serve de **evidência auxiliar**: não substitui nota fiscal,
   contrato ou orientação da contadora.
4. Pessoa física não sócia (profissional autônomo) → Serviços prestados por terceiros.
5. Funcionário CLT → conferir com o extrato da folha (salário, férias, rescisão).
6. Sócio → regra de retiradas/pró-labore da empresa.
7. Transferência entre contas da própria empresa → banco ↔ banco, lançada **uma vez só**.

Classifique cada item como **CONFIRMADO**, **PROVÁVEL**, **NÃO CRUZADO** ou **DIVERGENTE**.
O TXT definitivo só leva itens CONFIRMADOS. Com qualquer outro, o arquivo sai marcado como
**PRÉVIA** e as dúvidas vão para a contadora.

Não classifique toda pessoa jurídica como fornecedor: a conta de fornecedores só serve
quando o favorecido fornece algo coerente com a atividade e há nota fiscal.

## 3. Regras invioláveis

- **Conferência de saldo por banco**: saldo final − saldo inicial do extrato = entradas −
  saídas lançadas. Se não fechar, **o TXT não é entregue** (`gerar` recusa). Confira cada
  banco/produto separadamente (conta corrente, aplicação, poupança, maquininha).
- **Aplicações e rendimentos nunca são omitidos**: aplicação, resgate, rendimento, IRRF
  sobre rendimento, cota capital de cooperativa. Confira as frentes (corrente, aplicação,
  poupança) juntas, nunca só a conta corrente.
- **IOF e IRRF nunca são omitidos**, mesmo com valor pequeno. Sem conta no plano? Pergunte.
- **Competência**: não incluir movimento de outro mês no TXT; registre que ele ficou para o
  período correto.
- **Não declarar que o TXT foi aceito** sem importação real no Domínio: separe "validação
  estática" (formato, contas, saldos) de "importação efetiva".
- **Conta ausente numa cópia do plano** exportado não significa que não existe, se o razão
  ou o Domínio a comprovam. Registre a divergência.

## 4. Impostos

- Cada guia na **sua** conta de passivo (Simples, PIS, COFINS, IRPJ, CSLL, IRRF, CSRF, INSS
  retido, DCTFWeb/INSS, FGTS, ISS, ISS retido...). Nunca em despesas diversas.
- Confira o valor com a guia da competência (pasta `Guias`, ou o comprovante no e-CAC).
- Guia paga com atraso: principal na conta do imposto; **multa** e **juros** nas contas de
  multa/juros de mora, com os valores da própria guia. Se a empresa não tiver essas contas,
  pergunte.

## 5. Folha de pagamento

- Padrão: salário líquido no início do mês → Salários a pagar; adiantamento do dia 15 ao 20
  → Adiantamento de salário. Férias → Férias a pagar/Adiantamento de férias. Rescisão →
  Rescisão a pagar. Pró-labore → Pró-labore a pagar.
- Confira sempre com o **Extrato Mensal da folha do Domínio** (`folha_extrato_mensal.py`),
  funcionário por funcionário, pelo valor exato.

## 6. Sócios

Antes de lançar qualquer pagamento a sócio, confirme a regra da empresa e o total pago no mês:
- **Pró-labore fixo** (ex.: salário mínimo − INSS 11%): o acumulado do mês até o líquido vai
  para Pró-labore a pagar; o excedente vai para a conta do sócio (retirada/lucro). Uma
  operação que ultrapasse o limite vira **duas linhas `|6100|`** na mesma data.
- **Retiradas acima de R$ 50.000,00/mês por sócio**: o excedente vai para empréstimo ao
  sócio, por causa da retenção de 10% de IRRF sobre lucros e dividendos acima de R$ 50 mil
  por mês para a mesma pessoa física (Lei 15.270/2025, que incluiu o art. 6º-A na Lei
  9.250/1995). Some **todos** os pagamentos a favor do sócio no mês, inclusive contas
  pessoais pagas pela empresa.
- Depósito do sócio na empresa: D banco / C conta do sócio (ou mútuo, conforme a empresa).
- Nunca lance pagamento a sócio em serviços de terceiros ou fornecedores.

## 7. Arquivo TXT do Domínio

O leiaute é o mesmo para todas as empresas: `|0000|CNPJ|`, depois, para cada lançamento,
`|6000|X||||` e `|6100|data|débito|crédito|valor||histórico||||`, em cp1252 com CRLF, valor
com vírgula decimal. Partida com mais de um débito vira uma linha `|6100|` por débito.
Pergunte na abertura da empresa se ela usa arquivo **único** por mês (todos os bancos, em
ordem de data) ou **separado** em `_PAGAR`/`_RECEBER`, e salve com o nome e a pasta padrão:
`G:\Meu Drive\Trabalho ROF\Contabilidade\Arquivos RENATA Dominio\<cód> - <empresa>\<ano>\<MM_AAAA>\Extrato`.

## 8. Planilhas e listas de controle

- Status com cor: **verde** = OK/feito, **amarelo** = a fazer/pendente.
- Antes de entregar, **confira se nada ficou de fora**: conte os itens da fonte e os da
  planilha. Numa lista de empresas, compare com a relação completa de códigos do escritório.

## 9. Estrutura da skill de cada empresa (`rof-contabilidade-<empresa>`)

1. Dados da empresa (razão social, fantasia, CNPJ com e sem máscara, código no Domínio,
   CNAEs, endereço, natureza jurídica, regime com a data e quem confirmou, bancos, pasta,
   responsável: Elen ou Rosangela).
2. Quando ativar (nomes, CNPJ, contas bancárias, nomes de arquivo) e "não misturar empresas".
3. Sócios (CPF, participação, contas de retirada, empréstimo e pró-labore).
4. Regras de trabalho (acordo com a contadora).
5. Leiaute do TXT e forma de entrega (único ou PAGAR/RECEBER, nome, pasta).
6. Fontes do extrato por banco (OFX, PDF, particularidades).
7. Plano de contas: contas operacionais e **contas que NÃO devem ser usadas**.
8. Regras invioláveis (saldo por banco, aplicações, IOF/IRRF).
9. Impostos, folha e sócios (regras da empresa).
10. Particularidades dos bancos.
11. Classificações recorrentes **confirmadas** (favorecido → conta, quem validou).
12. Fluxo de trabalho mensal.
13. Pendências a confirmar com a contadora.
14. Saldos conferidos por mês (referência para o mês seguinte).
