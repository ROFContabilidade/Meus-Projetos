# Roteiro padrão: NOVA EMPRESA

Este roteiro vale para toda empresa nova no escritório. Siga as etapas **na ordem**.
Cada resposta vai para o JSON da empresa (`empresas/<codigo>-<nome>.json`, a partir de
`assets/empresa_modelo.json`), porque é esse arquivo que garante que os lançamentos dos
próximos meses sigam o mesmo padrão, seja quem for que faça.

Pergunte de forma organizada: poucas perguntas por vez, numeradas, com opções quando
couber (use a ferramenta de perguntas com opções, se houver). Não siga adiante com
suposições. Se a resposta não veio, registre como pendente e pergunte de novo.

## Etapa 1: Responsável pelo lançamento

Primeira pergunta, sempre:

> Com quem será feito o lançamento contábil desta empresa? **Elen** ou **Rosangela**?

Grave em `responsavel_lancamento` e registre também quem cadastrou e a data. Coloque o
nome da responsável no resumo final.

## Etapa 2: CNPJ e análise do cartão CNPJ

Peça o CNPJ (ou o cartão CNPJ em PDF). Consulte:

```bash
python scripts/consulta_cnpj.py <CNPJ> --json trabalho/cnpj.json
```

Apresente a análise em tabela: razão social, nome fantasia, situação cadastral (e desde
quando), início das atividades, natureza jurídica, porte, capital social, matriz/filial,
endereço, telefones, CNAE principal e secundários, histórico do Simples/MEI (opção e
exclusão), regime tributário declarado por ano e quadro societário (nome, qualificação,
data de entrada).

Depois da tabela, traga **o que isso muda na contabilização**. Exemplos:
- Lucro Presumido/Real: DARFs de IRPJ (2089), CSLL (2372), PIS (8109), COFINS (2172);
  indústria também IPI; comércio/indústria ICMS estadual; serviços ISS municipal.
- Simples Nacional: DAS. MEI: DAS-MEI.
- Situação diferente de ATIVA, exclusão recente do Simples ou mudança de regime: alerte.
- Sócios: movimentos com os nomes deles no extrato exigirão confirmação.
- Atividades que indicam recebimento por cartão, marketplace ou cobrança bancária.

Se a consulta falhar (sem internet), peça o cartão CNPJ em PDF e leia os mesmos dados dele.

## Etapa 3: Sistema contábil

Pergunte sempre, mesmo que pareça óbvio:

> A empresa utiliza o sistema **Domínio**?

- **Sim** → grave `usa_dominio: true` e peça o **código da empresa no Domínio**. O arquivo
  de importação é o padrão do escritório (`layout_txt.formato = "dominio"`, arquivos
  `_PAGAR` e `_RECEBER`). Não é preciso pedir modelo de arquivo.
- **Não** → pergunte qual sistema e peça um arquivo de importação que esse sistema já tenha
  aceitado. Configure `layout_txt` com `"formato": "delimitado"` para ficar idêntico a ele
  (`references/dominio.md`, seção formato alternativo). Sem modelo, não gere o arquivo:
  entregue a planilha classificada e explique o motivo.

## Etapa 4: Perguntas sobre a empresa

Confirme e complete o que o cartão CNPJ não responde. Pergunte em blocos:

**Tributação e cadastro**
1. Regime tributário atual e desde quando. Confirme mesmo que a Receita mostre um
   regime, porque o dado público pode estar desatualizado.
2. CPF completo de cada sócio (o cartão CNPJ mostra o CPF mascarado) e quem é o administrador.
3. Os sócios recebem pró-labore? Qual valor e em que dia? Há distribuição de lucros
   mensal e por qual conta ela é lançada?

**Bancos e recebimentos**
4. Quais contas bancárias a empresa tem (banco, agência, conta)? Qual o código de cada
   uma no plano de contas? Há aplicação automática, poupança, conta de investimento?
5. Como a empresa recebe: boleto/cobrança, PIX, cartão (qual maquininha), marketplace?
   A taxa do cartão vem descontada?
6. Os recebimentos são baixados em **Clientes** (vendas integradas pela Escrita Fiscal)
   ou lançados direto em receita?

**Pagamentos**
7. Os pagamentos a fornecedores são baixados em **Fornecedores** (notas de entrada
   integradas) ou lançados direto em despesa/estoque?
8. Há funcionários? Quem faz a folha? Como os salários são pagos (SISPAG, lote, PIX)?
   **Calendário da folha**: o padrão do escritório são dois pagamentos por mês, o
   **salário líquido no início do mês** (Salários a pagar) e o **adiantamento de salário
   do dia 15 ao 20** (Adiantamento de salário). Confirme se a empresa segue esse padrão,
   anote os códigos das duas contas no plano e crie as regras com `dia_de`/`dia_ate`.
   Avise que o **relatório da folha** será pedido todo mês para a conferência.
9. Há empréstimos, financiamentos, consórcio, leasing ou parcelamentos de tributos
   (REFIS, parcelamento simplificado)?
10. Há cartão de crédito empresarial? A fatura é lançada por item ou pelo total?
11. Existem empresas ligadas ou do mesmo grupo? As transferências entre elas são mútuo?
12. Sócios pagam despesas pessoais pela conta da empresa, ou a empresa recebe dinheiro
    dos sócios? Como o escritório lança isso?
13. Qual conta o escritório usa para o que não se identifica (ex.: "Despesas a
    identificar")? Grave em `conta_transitoria`. Lembre que o padrão é perguntar antes de usá-la.
14. Regra dos sócios: há pró-labore fixo (valor líquido)? As retiradas passam de
    R$ 50.000,00/mês por sócio (regra do excedente em empréstimo, Lei 15.270/2025)? Quais
    contas: retirada, empréstimo, pró-labore? Existem contas que **não** devem ser usadas?
15. Impostos: quais guias a empresa paga e onde ficam (pasta `Guias`)? Contas de multa e
    juros de mora?
16. **Pasta dos arquivos** no Google Drive (padrão
    `G:\Meu Drive\Trabalho ROF\Contabilidade\Arquivos RENATA Dominio\<cód> - <empresa>\<ano>\<MM_AAAA>\Extrato`)
    e se o TXT sai em **arquivo único** por mês ou separado em `_PAGAR`/`_RECEBER`
    (`separar_pagar_receber`).

**Dúvidas adicionais**: pergunte o que mais a análise do CNPJ, do balancete ou do razão
levantar (atividade incomum, filial, contas com saldo estranho, etc.). Cada resposta que
afete a classificação vira uma regra ou uma observação no JSON.

## Etapa 5: Documentos para seguir o padrão de lançamentos

Peça os documentos dos **últimos meses (ideal: 3 a 6 meses)**:

| Documento | Para quê |
|---|---|
| **Balancete** | Saldos de abertura, contas em uso, saldo da conta banco para conferir o extrato |
| **Relatório de entradas** (notas fiscais de entrada) | Nomes de fornecedores e valores, para identificar boletos e PIX pagos e saber se baixam Fornecedores ou despesa |
| **Razão** (principalmente das contas de banco) | O padrão de lançamento que o escritório usa: que conta cada tipo de movimento recebe |
| **Plano de contas** (`Contas.xls` exportado do Domínio) | Códigos reduzidos: `python scripts/plano_contas.py Contas.xls -o contas.json` |
| TXT de importação de meses anteriores (se houver) | Histórico exato; leia com `ler ... --juntar` |
| Extrato do mês a lançar (OFX de preferência) | O trabalho do mês |

Ao receber:
- **Razão / TXT anteriores** → extraia o padrão (descrição do movimento → conta) e
  transforme em `regras`. Liste o que parecer erro ou incoerência (conta de receita
  usada em pagamento, sócio lançado como despesa, transferência entre empresas em caixa)
  e **pergunte** antes de copiar esse padrão.
- **Balancete** → confira o saldo da conta banco com o saldo inicial do extrato. Uma
  diferença indica mês com lançamento faltando ou em duplicidade: aponte.
- **Relatório de entradas** → para os fornecedores recorrentes, crie regras pelo nome
  (ex.: `"contem": ["ALSCO BRASIL"]` → conta do fornecedor ou da despesa). O extrato
  costuma cortar o nome do beneficiário (ex.: "ALSCO BRASIL" vira "ALSCO BRASI"), então use o
  começo do nome. Ao conciliar, confira nome **e valor** com a nota.

## Etapa 6: Confirmação do cadastro e skill da empresa

Mostre um resumo do cadastro (responsável, empresa, regime, sócios, sistema, código,
bancos, contas principais, regras criadas, pendências) e peça confirmação antes de
lançar o primeiro extrato. Salve o JSON e entregue-o ao usuário. Depois gere a skill da
empresa (`scripts/gerar_skill_empresa.py`), no padrão de `references/padrao_rof.md`
(seção 9), e entregue o `.skill` para instalar.
