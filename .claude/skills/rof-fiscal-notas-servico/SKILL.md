---
name: "rof-fiscal-notas-servico"
description: "ROF Contabilidade - leitura e conferência de NOTAS FISCAIS DE SERVIÇO (NFS-e) PRESTADAS e TOMADAS de qualquer empresa do escritório. Sempre pergunta primeiro se é PRESTADO ou TOMADO e pede o CNPJ. Consulta o CNAE da empresa na Receita; no PRESTADO aponta o anexo do Simples Nacional de cada ATIVIDADE da nota (ex.: 17.06 = Anexo III, 10.09 = Anexo V com Fator R) e monta a planilha com a sequência das notas, atividade, tomador, alíquota de ISS, informações complementares, discriminação e retenções; no TOMADO lê com atenção a atividade destacada em cada nota (sem consultar o CNPJ do prestador), confere se tem ou deveria ter retenção (IRRF, CSRF, INSS e ISS) e compara com o que a nota destaca. Aponta toda inconsistência. Usar quando enviarem XML/PDF de NFS-e, falarem em notas de serviço, serviços prestados ou tomados, retenções, ISS retido, sequência de notas, anexo do Simples ou CNAE para nota de serviço."
---

# ROF - Leitura de NFS-e prestadas e tomadas

Rosangela/Elen enviam as notas fiscais de serviço de uma empresa (XML e/ou PDF, avulsas ou em ZIP).
A entrega é **uma planilha por empresa, por mês e por tipo (prestado ou tomado)** com todos os dados das notas e a aba
**Inconsistências**. A leitura tem de ser **criteriosa**: ler nota por nota, campo por campo, inclusive a discriminação
e as informações complementares, e apontar **tudo** o que estiver estranho. É melhor um alerta a mais do que um erro passando.

## Leitura de Arquivos (padrão ROF, economia de tokens)

Regra obrigatória antes de abrir qualquer documento (validado por Rosangela, 29/10/2026). Ler sempre na ordem:

1. **MD** (`.md`): ler direto.
2. **OFX ou XML**: ler direto ou pelo script da skill.
3. **Planilha** (`.xlsx`, `.xls`, `.csv`): ler pelo script da skill.
4. **PDF**: **nunca abrir o PDF direto** (gasta muitos tokens). Antes:
   - se esta skill tem script que lê aquele PDF (ex.: `extrato_dominio.py ler`), usar o script;
   - senão, converter: `python scripts/ler_documento.py converter <arquivo.pdf>` (o `.md` fica salvo ao lado do PDF) e ler o `.md`.
5. **Nada funcionou** (PDF escaneado, conversão vazia): **parar e avisar a Rosangela**; não ler o PDF direto.

Para uma pasta inteira: `python scripts/ler_documento.py escolher <pasta>` mostra o que ler, na ordem, e o que ignorar (ex.: se existe `Entradas.xlsx`, o `Entradas.pdf` é ignorado).

## 1. Perguntas obrigatórias antes de ler (sempre, todas as empresas)

1. **"As notas são de serviços PRESTADOS (emitidas pela empresa) ou TOMADOS (recebidas de fornecedores)?"**
   Não supor pelo nome do arquivo. Se vierem as duas no mesmo lote, separar e confirmar.
2. **"Qual o CNPJ da empresa?"** - consultar o CNAE (passo 2). Se a empresa já tem skill própria
   (`rof-contabilidade-<empresa>`), ler o regime/anexo registrado nela e comparar com a consulta.
3. **Competência** (mês/ano) das notas.

**Não** pedir faturamento (RBT12) nem folha: o Fator R não é calculado aqui. **Não** consultar o CNPJ dos prestadores no tomado.

Fazer as perguntas juntas, numa mensagem só, e esperar a resposta.

## 2. Consulta do CNPJ e dos CNAEs

```bash
S=.claude/skills/rof-fiscal-notas-servico/scripts
python3 $S/consulta_cnpj.py <CNPJ> --json empresa.json
```

Traz razão social, situação, município, **Simples (data de opção/exclusão)**, **MEI**, CNAE principal e secundários e um
**anexo sugerido** para cada CNAE (tabela interna `tabelas.py`). A sugestão é atalho: a palavra final é do
**Anexo VI da Resolução CGSN 140/2018** e do art. 18 da LC 123/2006. Quando vier "conferir" ou "?", pesquisar e decidir;
se continuar a dúvida, dizer que é dúvida.

### Como apontar o anexo (PRESTADO, empresa do Simples)

- O anexo é da **atividade destacada em cada nota** (item da LC 116 + discriminação), não só do CNAE principal. Exemplos:
  **17.06 promoção de vendas / propaganda → Anexo III** (padrão do escritório); **10.09 representação → Anexo V com Fator R**;
  17.19 contabilidade → III; 17.01 consultoria → V com Fator R; 7.02 obra → IV.
- Escrever "**Anexo V (Fator R)**" para as atividades do §5º-I, sem calcular o Fator R (= Anexo V, ou III se folha/receita ≥ 28%).
- A tabela `ITENS_LC116` em `tabelas.py` dá o anexo de cada item; ela vira a coluna **"Anexo Simples (atividade)"** e o
  quadro **faturamento por anexo** na aba Empresa e CNAEs. Quando a discriminação mostrar outra atividade, ou a tabela disser
  "conferir"/"?", decidir e gravar `"anexo"` na nota (com o porquê em `"apontamentos"`). Quando a analista definir um anexo
  diferente do da tabela, **atualizar `ITENS_LC116`** para valer nas próximas empresas.
- Uma empresa pode ter receitas em anexos diferentes no mesmo mês: o quadro separa por anexo.
- **Anexo III** direto: contabilidade, fisioterapia, academias, ensino, estética/beleza, corretagem, agência de viagem,
  software (§5º-D), manutenção/reparos, transporte municipal, locação de bens móveis etc.
- **Anexo V (Fator R)** (§5º-I e §5º-J): medicina, odontologia, psicologia, nutrição, fono, engenharia, arquitetura,
  consultoria, auditoria, publicidade, representação comercial, intermediação, despachante, tradução, TI (consultoria/suporte) etc.
- **Anexo IV** (§5º-C): construção civil, vigilância, limpeza/conservação, paisagismo, advocacia. CPP fora do DAS e
  **sofre retenção de INSS 11%** quando houver cessão de mão de obra/empreitada.
- **Atividade impeditiva** (cessão/locação de mão de obra fora do Anexo IV, holding, factoring etc.): apontar como ERRO grave.
- Nota com atividade que **não está em nenhum CNAE do CNPJ**: apontar (precisa incluir o CNAE ou a nota está errada).
- Gravar a conclusão em `empresa.json` (`"conclusao_anexo"`) - aparece na aba **Empresa e CNAEs**.
  Escrever o anexo de cada atividade e o porquê, ex.: *"17.06 promoção de vendas - Anexo III (R$ 1.000,00). 10.09
  representação comercial - Anexo V (Fator R) (R$ 5.000,00)."*

## 3. Ler as notas

- **XML** (preferir sempre): `python3 -I $S/ler_nfse_xml.py <pasta ou arquivos> --saida notas.json`
  Lê NFS-e **Padrão Nacional** (nfse.gov.br) e **ABRASF/municipais**. Arquivos baixados ficam numa pasta própria; rodar com `-I`.
- **PDF**: `pdftotext -layout nota.pdf -` (ou a skill `anthropic-skills:pdf`; OCR se for imagem) e preencher o mesmo
  JSON à mão, com os mesmos campos. Se tiver XML e PDF da mesma nota, conferir um contra o outro.
- **Depois do script, ler cada nota de verdade** (discriminação, informações complementares, valores) e completar no JSON
  o que o script não achou. Campo que não existe na nota fica vazio e vira apontamento - nunca inventar.
- O que eu (Claude) encontrar lendo vai no campo `"apontamentos": ["..."]` de cada nota. Começar o texto com `ERRO: ` ou
  `ALERTA: ` para dar a gravidade (sem prefixo = APONTAMENTO, só observação).

### O que procurar (lista mínima - apontar tudo o que mais parecer errado)

**Comuns (prestado e tomado)**
- Sequência: números faltando, repetidos, notas canceladas ou substituídas (a substituída não pode entrar).
- Competência/data de emissão fora do mês; nota emitida num mês com competência de outro.
- Valor líquido ≠ valor do serviço - desconto incondicionado - retenções (ISS retido conta).
- ISS ≠ base × alíquota; base ≠ valor - deduções - desconto incondicionado.
- Retenção escrita só na discriminação/informações complementares e **não** nos campos próprios (ou o contrário);
  valores do texto diferentes dos campos.
- Discriminação vazia, genérica ("serviços prestados") ou que **não combina com o item da LC 116** escolhido.
- Item da LC 116 que não corresponde a nenhum CNAE do prestador.
- Município de incidência do ISS errado: serviços do **art. 3º da LC 116** (construção, limpeza, vigilância, guarda,
  eventos, etc.) são devidos no **local da prestação**; os demais, no estabelecimento do prestador.
- ISS retido com tomador pessoa física; tomador sem CPF/CNPJ; dados do tomador de outra empresa.
- Reforma tributária (2026 em diante): campos IBS/CBS ausentes ou estranhos no layout nacional - apontar como ALERTA.

**PRESTADO**
- Empresa do Simples com **IRRF/PIS/COFINS/CSLL destacados** (optante não sofre, salvo pagamento por órgão público federal -
  IN RFB 1.234/2012) → ERRO.
- Simples com INSS retido fora do Anexo IV → conferir.
- Alíquota de ISS do Simples fora de 2% a 5%.
- Nota marcada "não optante" com CNPJ optante (ou o contrário); falta da frase do Simples nas informações complementares.
- MEI: não destaca ISS na nota; alertar se vier ISS/retenção.
- Tomador órgão público: conferir retenções da IN RFB 1.234/2012 e a regra do município.
- Atividade da nota em anexo diferente do que vem sendo tributado no DAS.

**TOMADO** - **não consultar o CNPJ do prestador**. Tudo sai da nota: ler com muita atenção o **item da LC 116, a atividade
e a discriminação** e decidir se tem ou deveria ter retenção. O regime do prestador vem do campo da nota (Simples/MEI/não optante)
ou do texto ("optante pelo Simples Nacional"); se a nota não disser, considerar não optante e apontar.
O script sugere o enquadramento pelo item (`ITENS_LC116`) e marca ALERTA "confirmar": **conferir sempre com a discriminação** -
item e descrição que não combinam são apontamento, e o que vale é o serviço realmente prestado. Gravar o enquadramento
decidido em `"enquadramento"` (chaves em `tabelas.RETENCOES`):

| enquadramento | IRRF | CSRF (4,65%) | INSS 11% | Exemplos |
|---|---|---|---|---|
| `servico_profissional` | 1,5% | sim | - | contabilidade, advocacia, engenharia, consultoria, medicina, TI de consultoria, auditoria, publicidade (lista art. 714 §1º RIR/2018) |
| `limpeza_conservacao` | 1% | sim | sim* | limpeza, conservação, zeladoria |
| `seguranca_vigilancia` | 1% | sim | sim* | vigilância, segurança, portaria |
| `locacao_mao_obra` | 1% | sim | sim | cessão/locação de mão de obra, temporários |
| `manutencao` | - | sim | se cessão/empreitada (`"cessao_mao_obra": true`) | manutenção de máquinas, instalações, elevadores |
| `assessoria_credito_mercadologica` | 1,5% | sim | - | assessoria creditícia/mercadológica, gestão de crédito, cobrança, factoring |
| `comissao_representacao` | 1,5% | - | - | representação comercial, corretagem, comissões |
| `propaganda_publicidade` | 1,5% | - | - | agências de propaganda (conferir se cabe como profissional) |
| `construcao_empreitada` | - | - | sim | obra, reforma, empreitada (ISS no local da obra) |
| `transporte` / `sem_retencao` | - | - | - | frete, demais serviços |

\* INSS só com cessão de mão de obra ou empreitada (IN RFB 2.110/2022). Se precisar corrigir o que a nota diz, gravar
`"prestador_simples"`, `"prestador_mei"`, `"prestador_anexo_iv"` (Simples com atividade de obra/limpeza/vigilância é marcado
automaticamente) e `"base_inss"` se houver dedução de material/equipamento.

Regras aplicadas pelo script: prestador **Simples** não sofre IRRF nem CSRF e só sofre INSS se for Anexo IV; **MEI** sem retenção;
**dispensa** quando o IRRF ou a CSRF calculados forem ≤ R$ 10,00 e o INSS < R$ 10,00.
O script compara o **esperado** com o **destacado**: retenção devida e não destacada é ERRO (a tomadora responde pelo recolhimento).

**ISS no tomado**: conferir se o serviço tem **retenção na fonte pelo tomador** - LC 116 art. 6º §2º (itens 3.05, 7.02, 7.04, 7.05,
7.09, 7.10, 7.12, 7.16, 7.17, 7.19, 11.02, 17.05 e 17.10, e os do art. 3º prestados no município do tomador) + **lei do
município da empresa** (pesquisar quando não souber). Prestador do Simples: reter pela alíquota informada na nota
(LC 123 art. 21 §4º); sem alíquota informada, apontar. MEI e ISS fixo (sociedade uniprofissional): não reter. Escrever
o resultado nos `"apontamentos"` da nota (ex.: "ISS 2% deveria ser retido - item 7.02, obra em <município>").

Guias que saem das retenções (citar no resumo final): IRRF **1708**, CSRF **5952** (DARF/DCTFWeb conforme a época), INSS na
EFD-Reinf (R-2010) / DCTFWeb, ISS na guia do município. Prestado com retenção sofrida: conferir informe/R-2020.

### Cruzar com os relatórios

Se a pasta `Relatorio` do mês tiver o **relatório da prefeitura** (NFS-e emitidas) e/ou a **planilha do portal nacional**
(Emitidas - Completa), cruzar número a número e valor a valor com as notas lidas: nota que aparece só de um lado, valor diferente,
cancelada/substituída, total do mês. A prefeitura de Curitiba lista por competência (inclui nota emitida no mês seguinte com
competência do mês); o portal lista por data de geração. O resultado vai em `"apontamentos_gerais"` do `empresa.json`.

## 4. Gerar a planilha

```bash
python3 $S/planilha_nfse.py prestado notas.json empresa.json "NFSe_Prestadas_<Empresa>_MM-AAAA.xlsx" --competencia AAAA-MM
python3 $S/planilha_nfse.py tomado   notas.json empresa.json "NFSe_Tomadas_<Empresa>_MM-AAAA.xlsx"   --competencia AAAA-MM
```

Abas:
- **Notas Prestadas** - nº (ordem crescente), emissão, competência, situação, tomador (CPF/CNPJ e nome), **município do tomador,
  local da prestação e município de incidência do ISS** (preencher `tomador_municipio`, `municipio_prestacao`, `municipio_incidencia`
  com o nome da cidade/UF; alerta automático quando local da prestação ≠ município do tomador), item LC 116,
  atividade, **anexo do Simples da atividade**, discriminação, informações complementares, valor, base, alíquota e valor do ISS, ISS retido, IRRF, PIS, COFINS,
  CSLL, INSS, total retido, líquido, status; no título a sequência e os números faltando.
- **Notas Tomadas** - os mesmos dados do lado do prestador (com local da prestação e município de incidência do ISS) + regime do prestador, enquadramento, alíquotas e valores
  **esperados** de IRRF/CSRF/INSS e a observação da regra aplicada.
- **Inconsistências** - uma linha por apontamento (ERRO / ALERTA / APONTAMENTO), com colunas "Resolvido?" e "Observação" para a analista.
- **Empresa e CNAEs** - dados da consulta, anexo de cada CNAE, **faturamento do mês por anexo/atividade** e a conclusão.
- **Regras de retenção** (tomado).

## 5. Entrega

1. **Dados de clientes NUNCA vão para o GitHub** (no repositório fica só a skill). Trabalhar numa pasta temporária
   (scratchpad da sessão, ex.: `<scratchpad>/Notas-Servico/<NUM_Empresa>/<AAAA-MM>/` com `config/notas.json` e `empresa.json`).
2. **Salvar a planilha no Google Drive, na pasta `Relatorio` do mês da empresa** - sem pedir permissão (autorizado pela
   Rosangela em 13/10/2026): `Arquivos RENATA Dominio > <NUM - Empresa> > <ANO> > MM_AAAA > Relatorio`.
   Upload com `create_file` (base64, `disableConversionToGoogleType: true`). O conector não substitui conteúdo de arquivo:
   versão nova vai com sufixo `_v2`, `_v3`...
3. Enviar a planilha (SendUserFile) e responder no chat, curto:
   - Prestado: **anexo de tributação de cada atividade** (ex.: 17.06 → III; 10.09 → V com Fator R), sequência (de-até, faltando, canceladas), total faturado,
     total de retenções sofridas e os **ERROS**.
   - Tomado: notas com retenção devida (quanto de IRRF, CSRF, INSS e ISS a recolher) e os **ERROS**.
   - O que ficou em dúvida e o que preciso da analista.
4. Commit/push no branch só das mudanças da skill.
5. Se a empresa tiver skill própria, registrar lá o anexo confirmado e as decisões novas da analista.

## Cuidados

- Nunca afirmar alíquota, anexo ou retenção sem base: citar a norma ou dizer que é dúvida.
- Nunca alterar arquivos do cliente no Drive; só ler.
- Regras mudam (ex.: reforma tributária 2026-2033, novas INs): se a nota trouxer campo ou regra que não está aqui, pesquisar e atualizar esta skill.
