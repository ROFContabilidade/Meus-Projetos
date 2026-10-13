---
name: "rof-fiscal-notas-servico"
description: "ROF Contabilidade - leitura e conferência de NOTAS FISCAIS DE SERVIÇO (NFS-e) PRESTADAS e TOMADAS de qualquer empresa do escritório. Sempre pergunta primeiro se é PRESTADO ou TOMADO e pede o CNPJ. Consulta o CNAE na Receita; no PRESTADO aponta o anexo do Simples Nacional e monta a planilha com a sequência das notas, atividade, tomador, alíquota de ISS, informações complementares, discriminação e retenções; no TOMADO confere se a atividade de cada prestador tem retenção (IRRF, CSRF, INSS e ISS) e compara com o que a nota destaca. Aponta toda inconsistência. Usar quando enviarem XML/PDF de NFS-e, falarem em notas de serviço, serviços prestados ou tomados, retenções, ISS retido, sequência de notas, anexo do Simples ou CNAE para nota de serviço."
---

# ROF - Leitura de NFS-e prestadas e tomadas

Rosangela/Elen enviam as notas fiscais de serviço de uma empresa (XML e/ou PDF, avulsas ou em ZIP).
A entrega é **uma planilha por empresa, por mês e por tipo (prestado ou tomado)** com todos os dados das notas e a aba
**Inconsistências**. A leitura tem de ser **criteriosa**: ler nota por nota, campo por campo, inclusive a discriminação
e as informações complementares, e apontar **tudo** o que estiver estranho. É melhor um alerta a mais do que um erro passando.

## 1. Perguntas obrigatórias antes de ler (sempre, todas as empresas)

1. **"As notas são de serviços PRESTADOS (emitidas pela empresa) ou TOMADOS (recebidas de fornecedores)?"**
   Não supor pelo nome do arquivo. Se vierem as duas no mesmo lote, separar e confirmar.
2. **"Qual o CNPJ da empresa?"** - consultar o CNAE (passo 2). Se a empresa já tem skill própria
   (`rof-contabilidade-<empresa>`), ler o regime/anexo registrado nela e comparar com a consulta.
3. **Competência** (mês/ano) das notas.
4. No **PRESTADO**, se for do Simples: perguntar o **RBT12** e a **folha dos últimos 12 meses** (Fator R) quando houver
   CNAE do Anexo V/III pelo Fator R e o anexo não estiver registrado na skill da empresa. Sem esses dados, apontar o anexo
   como "V ou III conforme Fator R" e dizer o que falta.
5. No **TOMADO**: os CNPJs dos prestadores saem das próprias notas; consultar **cada CNPJ de prestador** (CNAE e Simples/MEI).
   Se a nota vier sem CNPJ legível (PDF ruim), **pedir o CNPJ** em vez de supor.

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

### Como fechar o anexo (PRESTADO, empresa do Simples)

- O anexo é da **atividade efetivamente prestada em cada nota** (item da LC 116 + discriminação), não só do CNAE principal.
  Uma empresa pode ter receitas em anexos diferentes no mesmo mês: separar por anexo na planilha.
- **Anexo III** direto: contabilidade, fisioterapia, academias, ensino, estética/beleza, corretagem, agência de viagem,
  software (§5º-D), manutenção/reparos, transporte municipal, locação de bens móveis etc.
- **Anexo V ou III pelo Fator R** (§5º-I e §5º-J): medicina, odontologia, psicologia, nutrição, fono, engenharia, arquitetura,
  consultoria, auditoria, publicidade, representação comercial, intermediação, despachante, tradução, TI (consultoria/suporte) etc.
  **Fator R = folha 12 meses / RBT12 ≥ 28% → Anexo III; abaixo → Anexo V.**
- **Anexo IV** (§5º-C): construção civil, vigilância, limpeza/conservação, paisagismo, advocacia. CPP fora do DAS e
  **sofre retenção de INSS 11%** quando houver cessão de mão de obra/empreitada.
- **Atividade impeditiva** (cessão/locação de mão de obra fora do Anexo IV, holding, factoring etc.): apontar como ERRO grave.
- Nota com atividade que **não está em nenhum CNAE do CNPJ**: apontar (precisa incluir o CNAE ou a nota está errada).
- Gravar a conclusão em `empresa.json` (`"conclusao_anexo"`, `"fator_r"`, `"rbt12"`) - aparece na aba **Empresa e CNAEs**.
  Escrever o anexo de cada atividade e o porquê, ex.: *"Anexo III - 17.19 contabilidade (6920-6/01, §5º-B XIV). Consultoria
  tributária (6920-6/02) seria Anexo V/III pelo Fator R, mas não houve nota dessa atividade no mês."*

## 3. Ler as notas

- **XML** (preferir sempre): `python3 -I $S/ler_nfse_xml.py <pasta ou arquivos> --saida notas.json`
  Lê NFS-e **Padrão Nacional** (nfse.gov.br) e **ABRASF/municipais**. Arquivos baixados ficam numa pasta própria; rodar com `-I`.
- **PDF**: `pdftotext -layout nota.pdf -` (ou a skill `anthropic-skills:pdf`; OCR se for imagem) e preencher o mesmo
  JSON à mão, com os mesmos campos. Se tiver XML e PDF da mesma nota, conferir um contra o outro.
- **Depois do script, ler cada nota de verdade** (discriminação, informações complementares, valores) e completar no JSON
  o que o script não achou. Campo que não existe na nota fica vazio e vira apontamento - nunca inventar.
- O que eu (Claude) encontrar lendo vai no campo `"apontamentos": ["..."]` de cada nota.

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
- Alíquota de ISS do Simples fora de 2% a 5%, ou diferente da alíquota efetiva da faixa (com o RBT12).
- Nota marcada "não optante" com CNPJ optante (ou o contrário); falta da frase do Simples nas informações complementares.
- MEI: não destaca ISS na nota; alertar se vier ISS/retenção.
- Tomador órgão público: conferir retenções da IN RFB 1.234/2012 e a regra do município.
- Atividade da nota em anexo diferente do que vem sendo tributado no DAS.

**TOMADO** - para cada nota decidir o `"enquadramento"` da atividade (chaves em `tabelas.RETENCOES`):

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

\* INSS só com cessão de mão de obra ou empreitada (IN RFB 2.110/2022). Marcar também na nota:
`"prestador_simples"`, `"prestador_mei"`, `"prestador_anexo_iv"` (da consulta do CNPJ do prestador) e `"base_inss"` se houver
dedução de material/equipamento.

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

## 4. Gerar a planilha

```bash
python3 $S/planilha_nfse.py prestado notas.json empresa.json "NFSe_Prestadas_<Empresa>_MM-AAAA.xlsx" --competencia AAAA-MM
python3 $S/planilha_nfse.py tomado   notas.json empresa.json "NFSe_Tomadas_<Empresa>_MM-AAAA.xlsx"   --competencia AAAA-MM --prestadores prestadores.json
```
(`prestadores.json` = `{cnpj: saída do consulta_cnpj.py}` de cada prestador.)

Abas:
- **Notas Prestadas** - nº (ordem crescente), emissão, competência, situação, tomador (CPF/CNPJ e nome), item LC 116,
  atividade, discriminação, informações complementares, valor, base, alíquota e valor do ISS, ISS retido, IRRF, PIS, COFINS,
  CSLL, INSS, total retido, líquido, status; no título a sequência e os números faltando.
- **Notas Tomadas** - os mesmos dados do lado do prestador + regime do prestador, enquadramento, alíquotas e valores
  **esperados** de IRRF/CSRF/INSS e a observação da regra aplicada.
- **Inconsistências** - uma linha por apontamento (ERRO / ALERTA / APONTAMENTO), com colunas "Resolvido?" e "Observação" para a analista.
- **Empresa e CNAEs** - dados da consulta, anexo de cada CNAE e a **conclusão do anexo**.
- **Prestadores** e **Regras de retenção** (tomado).

## 5. Entrega

1. Salvar em `Notas-Servico/<NUM_Empresa>/<AAAA-MM>/` (planilha + `config/` com `notas.json`, `empresa.json`, `prestadores.json`).
   Não versionar XML/PDF de clientes no repositório.
2. Enviar a planilha (SendUserFile) e responder no chat, curto:
   - Prestado: **anexo de tributação** (por atividade, com o motivo), sequência (de-até, faltando, canceladas), total faturado,
     total de retenções sofridas e os **ERROS**.
   - Tomado: notas com retenção devida (quanto de IRRF, CSRF, INSS e ISS a recolher) e os **ERROS**.
   - O que ficou em dúvida e o que preciso da analista.
3. Commit/push no branch de trabalho.
4. Se a empresa tiver skill própria, registrar lá o anexo confirmado e as decisões novas da analista.

## Cuidados

- Nunca afirmar alíquota, anexo ou retenção sem base: citar a norma ou dizer que é dúvida.
- Nunca alterar arquivos do cliente no Drive; só ler.
- Regras mudam (ex.: reforma tributária 2026-2033, novas INs): se a nota trouxer campo ou regra que não está aqui, pesquisar e atualizar esta skill.
