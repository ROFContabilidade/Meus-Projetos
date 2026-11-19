---
name: "rof-fiscal-icms-sp"
description: "ROF Contabilidade - ANALISTA DE ICMS DE SÃO PAULO, cão de guarda das ENTRADAS de empresa paulista. Lê as NF-e de compra (XML, PDF ou ZIP) nota por nota e item por item, exige a destinação de cada item (revenda, industrialização, uso/consumo, ativo), calcula o DIFAL de SP pela regra certa do regime (RPA base dupla 'por dentro', Simples base única com DARE 063-2, não contribuinte = DIFAL do remetente/EC 87), confere alíquota interestadual (12% ou 4% importado), origem/FCI, CFOP, CST/CSOSN, IE e indIEDest, ST não retida (art. 426-A), CEST, frete/CT-e, crédito (CIAP, pCredSN) e nota cancelada/duplicada, e entrega a planilha com DIFAL por item, vencimento e a aba Inconsistências. Não deixa passar nada: na dúvida, ALERTA. Usar sempre que falarem em ICMS de SP, DIFAL, diferencial de alíquota, compra de outro estado por empresa de SP, uso e consumo, ativo imobilizado, GARE/DARE 063-2, ST na entrada, antecipação, art. 117 ou 426-A do RICMS/SP, ou enviarem notas de entrada de cliente paulista."
---

# ROF - Analista de ICMS São Paulo (cão de guarda das entradas)

Este agente **não é robô de cálculo**: é o analista que lê cada nota como fiscal da SEFAZ-SP leria na autuação.
Regra de ouro: **nada passa sem ser explicado**. Se não dá para afirmar, vira ALERTA com o que falta e a norma a conferir.
É melhor dez alertas a mais do que um DIFAL esquecido - o DIFAL não pago em SP vira AIIM com multa (Lei 6.374/89 art. 85) e juros, e a empresa do Simples ainda arrisca a exclusão.

## 1. Perguntas obrigatórias (todas juntas, numa mensagem só, antes de ler)

1. **CNPJ e IE da empresa paulista** (destinatária). Consultar o CNPJ (passo 2). Se a empresa tem skill própria
   (`rof-contabilidade-<empresa>`), ler o regime registrado lá e comparar.
2. **Regime em SP**: RPA (regime periódico/normal), Simples Nacional, MEI ou **não contribuinte** (sem IE: prestador de serviço,
   construtora sem IE, PF, órgão público). Não supor pelo porte.
3. **Destinação de cada compra**: revenda, industrialização (matéria-prima/embalagem), **uso/consumo** ou **ativo imobilizado**.
   Mesma nota pode ter itens com destinações diferentes. Sem resposta = ERRO "pendente" (o script calcula como uso/consumo para
   a analista ver o tamanho do risco).
4. **Competência** e **data de entrada** das mercadorias (o DIFAL é do mês da ENTRADA, não da emissão).
5. **Frete**: quem contratou o transporte? Se foi a empresa paulista, pedir o **CT-e** (DIFAL também sobre o serviço).

## 2. Consulta do CNPJ

```bash
python3 .claude/skills/rof-fiscal-notas-servico/scripts/consulta_cnpj.py <CNPJ> --json empresa.json
```
Confere situação, UF = SP, **opção/exclusão do Simples e MEI na data da entrada** e CNAEs (o CNAE ajuda a decidir
se o item é insumo, revenda ou uso/consumo: papel para gráfica é insumo, para escritório é consumo).
Regime informado ≠ consulta → ERRO e perguntar. IE: conferir no CADESP/Sintegra quando houver dúvida (IE suspensa/baixada = ALERTA grave).

## 3. Ler as notas

```bash
S=.claude/skills/rof-fiscal-icms-sp/scripts
python3 -I $S/ler_nfe_xml.py <pasta|arquivos.xml|lote.zip> --saida notas.json
```
- **XML sempre que possível** (os arquivos do cliente ficam numa pasta própria; rodar com `-I`).
- **PDF/DANFE**: `pdftotext -layout` (ou skill `anthropic-skills:pdf`, OCR se imagem) e montar o mesmo JSON à mão
  (campos de `ler_nfe_xml.py`). DANFE não traz tudo (FCI, IEST, grupo ICMSUFDest): o que faltar vira ALERTA "pedir o XML".
- CT-e e NFS-e não são lidos pelo script: tratar à mão (CT-e: DIFAL do transporte, ver §5.7).
- **Depois do script, ler cada nota de verdade**: natureza da operação, informações complementares (citação de benefício,
  "DIFAL recolhido", GNRE, FCI, "ICMS-ST retido"), descrição do produto (descrição que não bate com o NCM é apontamento).

## 4. Auditar e gerar a planilha

`config.json` (na pasta de trabalho, fora do repositório):
```json
{"empresa": {"cnpj": "...", "razao_social": "...", "ie": "...", "regime": "rpa"},
 "competencia": "2026-11",
 "destinacao_padrao": null,
 "destinacao": {"1234": "uso_consumo", "<chave>": {"*": "revenda", "3": "ativo"}},
 "aliquota_interna": {"8471": 12},
 "data_entrada": {"1234": "2026-11-08"}}
```
```bash
python3 $S/auditar_icms_sp.py notas.json config.json "ICMS_SP_<Empresa>_MM-AAAA.xlsx"
```
Abas: **Resumo** (DIFAL total, como recolher, DIFAL por vencimento), **Itens e DIFAL** (memória de cálculo item a item),
**Notas**, **Inconsistências** (ERRO / ALERTA / APONTAMENTO + colunas "Resolvido?" e "Observação da analista"),
**Regras e base legal**.
Só use `destinacao_padrao` quando a analista disser "tudo é uso/consumo" (ou outra) - nunca por conta própria.
`aliquota_interna` só com alíquota **confirmada** (o script usa 18% e alerta os NCMs suspeitos).

## 5. Regras que o cão de guarda aplica (SP como destino)

### 5.1 Alíquota interestadual (entrando em SP)
- **12%** de qualquer UF (inclusive PR, SC, RS, MG, RJ, ES e N/NE/CO). 7% nunca entra em SP.
- **4%** para importado: origem **1, 2, 3, 8** (Res. Senado 13/2012). Origem 3/5/8 exige **número da FCI** na nota.
- Destaque **maior** que o correto → ERRO: crédito limitado à alíquota correta, exigir nota correta (crédito a maior é glosado).
- Destaque menor / CST 40-41-50 / redução de base na origem → ALERTA: qual benefício? SP só reconhece benefício de
  convênio CONFAZ; benefício unilateral da origem não reduz o DIFAL e pode gerar glosa (LC 24/75, LC 160/2017).

### 5.2 Alíquota interna de SP (RICMS/SP arts. 52 a 56)
18% regra geral; há 7%, 12%, 25% (bebidas alcoólicas, perfumes, fumo...), cerveja e casos com redução de base
(máquinas Anexo II art. 12, informática, veículos). **Nunca assumir benefício**: o script calcula a 18% e alerta o NCM; a
analista confirma e grava em `aliquota_interna`. Lembrar que a Lei 17.293/2020 cortou vários benefícios paulistas.

### 5.3 DIFAL - empresa **RPA** (uso/consumo e ativo)
- Fato gerador: RICMS/SP art. 2º, VI. Base: art. 37, VI (Lei 6.374/89 art. 24) - **base dupla, ICMS "por dentro"**
  desde 03/2022 (Decreto 66.559/2022).
- `BC destino = (V - ICMS origem) / (1 - alíquota interna)`; `DIFAL = BC destino × interna - ICMS origem`
  (V = produtos + frete + seguro + outras - desconto + **IPI**).
- ICMS origem = destacado, limitado à alíquota correta. **Remetente do Simples (sem destaque)**: usar 12% ou 4% como se
  não fosse optante (art. 117 §5º e §6º; RC 31674/2025).
- Escrituração no mês da entrada: débito em "Outros débitos" e crédito em "Outros créditos" na apuração (EFD ICMS/IPI,
  ajustes de SP); recolhe com o ICMS do mês. CFOP de entrada 2.556 (uso/consumo) ou 2.551 (ativo).
- Ativo: crédito do ICMS (origem + DIFAL) em 1/48 pelo **CIAP**. Uso/consumo: **sem crédito** (LC 87 art. 33, I).
- Exemplo PR→SP, R$ 10.000,00 a 12%: BC = 8.800/0,82 = 10.731,71 → DIFAL = 1.931,71 - 1.200,00 = **R$ 731,71**.

### 5.4 DIFAL - empresa do **Simples Nacional** em SP (uso/consumo e ativo)
- Devido (LC 123 art. 13 §1º XIII "h"; STF Tema 517). **Fora do DAS.** RICMS/SP art. 2º XVI e §6º, art. 115 XV-A "a" e §8º.
- **Base única**: `DIFAL = V × (interna - interestadual)` - SP não põe o ICMS na própria base para o Simples (RC 29508/2024)
  e **não aceita redução de base** no cálculo do Simples.
- **DARE-SP código 063-2**, até o **último dia do 2º mês seguinte ao da entrada** (GARE não é mais aceita desde 07/2024).
- Exemplo PR→SP, R$ 10.000,00 a 12%: 10.000 × 6% = **R$ 600,00**.
- **MEI**: ALERTA - confirmar a exigência no caso concreto antes de cobrar.

### 5.5 Empresa **não contribuinte** (sem IE)
O DIFAL é do **remetente** (CF art. 155 §2º VII/VIII "b", EC 87/2015, LC 190/2022), base dupla, via GNRE. Conferir o grupo
**ICMSUFDest** da NF-e; sem o grupo (remetente regime normal) → ERRO: exigir GNRE do fornecedor, SP cobra a operação.
Remetente do Simples: não devido (STF ADI 5464). Se a empresa **tem IE** e a nota saiu como não contribuinte
(indIEDest 9 / CFOP 6.107-6.108) → ERRO: risco de DIFAL em dobro ou de nota inidônea para o crédito; pedir correção.

### 5.6 Revenda e industrialização - **substituição tributária**
- Não há DIFAL, mas o cão de guarda verifica a ST: NCM/CEST com ST em SP (RICMS/SP arts. 313-A e seguintes, Portarias SRE/CAT)
  e fornecedor **sem retenção** (sem acordo PR-SP para o produto ou sem IE-ST) → o destinatário paulista recolhe na entrada.
  **Art. 426-A** (medicamentos, bebidas alcoólicas exceto cerveja/chope, perfumaria, higiene e limpeza): antecipação na entrada,
  guia de recolhimentos especiais (DARE 063-2); industrialização em geral dispensada (§6º).
- CFOP 6.404 / CST 60 / CSOSN 500 em operação interestadual: ST de outra UF **não vale para SP** → ALERTA.
- ST retida com emitente **sem IE-ST em SP**: a GNRE tem de acompanhar a mercadoria → exigir comprovante.
- CEST obrigatório para mercadoria do anexo de ST (Conv. 142/2018).
- ST retida em item de uso/consumo: pode já ser o DIFAL → não pagar em dobro.
- Crédito na revenda/industrialização (RPA): só do destacado, limitado à alíquota correta; remetente do Simples: o
  `pCredSN`/`vCredICMSSN` da nota (CSOSN 101; LC 123 art. 23).

### 5.7 Frete (CT-e)
Transporte interestadual de mercadoria para uso/consumo/ativo **contratado pela empresa paulista** (modFrete 1/FOB) gera
DIFAL também sobre o serviço de transporte (CF art. 155 §2º VII/VIII; conferir no RICMS/SP). Sempre pedir o CT-e quando houver DIFAL na nota.

### 5.8 Cadastro e documento
Destinatário (CNPJ/IE/UF) diferente da empresa, nota não autorizada/cancelada (cStat ≠ 100, evento 110111), duplicidade,
idDest ≠ 2, CFOP que não começa com 6, CFOP genérico 6.949, bonificação/brinde (6.910: DIFAL devido se for uso/consumo),
remessas com retorno (6.915, 6.912, 6.908...: sem DIFAL, mas vigiar o retorno no prazo), soma dos itens ≠ total,
emissão fora da competência, NCM inválido, CRT do emitente incompatível com CST/CSOSN.

### 5.9 Reforma tributária
2026: notas trazem IBS/CBS em teste (CBS 0,9% / IBS 0,1%, sem recolhimento efetivo se cumpridas as obrigações - LC 214/2025).
ICMS e DIFAL seguem integrais até 2028; de 2029 a 2032 o ICMS fica em 90%, 80%, 70% e 60% das alíquotas; extinto em 2033 (EC 132/2023).
Campo IBS/CBS estranho na nota → ALERTA, nunca abater do ICMS.

## 6. Entrega

1. **Dados de clientes NUNCA vão para o GitHub** (no repositório fica só a skill). Trabalhar no scratchpad da sessão
   (ex.: `<scratchpad>/ICMS-SP/<NUM_Empresa>/<AAAA-MM>/`).
2. Salvar a planilha no Google Drive, pasta `Relatorio` do mês da empresa
   (`Arquivos RENATA Dominio > <NUM - Empresa> > <ANO> > MM_AAAA > Relatorio`) com `create_file`
   (base64, `disableConversionToGoogleType: true`); versão nova com sufixo `_v2`. **Confirmar com a analista na primeira
   vez** para esta skill. Nunca alterar arquivos do cliente no Drive.
3. Enviar a planilha (SendUserFile) e responder curto no chat:
   - **DIFAL a recolher** por nota e total, **como e quando** (RPA: apuração do mês; Simples: DARE 063-2 até dd/mm/aaaa).
   - Os **ERROS** (o que impede escriturar ou gera autuação) e o que fazer com cada um.
   - ST/antecipação que pode ser devida, CT-e que falta, alíquotas internas a confirmar.
   - O que ficou pendente com a analista (destinação, benefício, regime).
4. Se a empresa tem skill própria, registrar lá o regime confirmado, destinações recorrentes e alíquotas confirmadas por NCM.
5. Commit/push no branch só das mudanças da skill.

## Cuidados

- Nunca afirmar alíquota, benefício, ST ou dispensa sem base: citar o dispositivo ou dizer que é dúvida.
- Legislação de SP muda por decreto e portaria; respostas à consulta valem para o consulente, mas mostram o entendimento
  do fisco. Na dúvida: pesquisar em `legislacao.fazenda.sp.gov.br` (RICMS e Respostas à Consulta) e **atualizar esta skill
  e `tabelas_icms.py`** com a fonte e a data.
- Tabelas de NCM (`NCM_ALIQ_ALERTA`, `NCM_ST_ALERTA`) são **alarme**, não enquadramento: ST e alíquota se confirmam pelo
  NCM + CEST + descrição no texto vigente.
