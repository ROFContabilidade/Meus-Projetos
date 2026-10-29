---
name: "rof-analise-simples-nacional"
description: "ROF Contabilidade - ANÁLISE SIMPLES NACIONAL COMPLETA para a Reforma Tributária (2027): compara o DAS pago em 2026 com o DAS de 2027 no mesmo faturamento (fim do PIS/COFINS monofásico dentro do Simples, CBS 15,33% + IBS 0,17% na partilha), calcula quanto o cliente precisa aumentar o preço (3 cenários: só impostos; impostos + marketplace/cartão; impostos + marketplace + despesas de venda) e compara Simples PURO × HÍBRIDO (IBS/CBS por fora, alíquota padrão 9,2%). Entrega planilha Excel com gráficos e PARECER EM WORD para o cliente, com base legal (LC 123, LC 214/2025, LC 227/2026, Resoluções CGSN 186 e 194/2026). Também gera relatório INTERNO de divergência faturamento declarado × recebimentos bancários (Razão) × compras, com riscos de exclusão (LC 123 arts. 29 e 34). Só empresas do Simples; não compara com Lucro Presumido. Usar quando falarem em análise do Simples Nacional, reforma tributária 2027, monofásico, híbrido ou puro, IBS/CBS no DAS, reajuste de preço por causa da reforma, opção pelo regime regular, ou faturamento caiu e entradas continuam altas."
---

# ROF - Análise Simples Nacional completa (Reforma 2027)

Rosangela/Elen pedem a análise de uma empresa do Simples Nacional. Entregas:

1. **Planilha do estudo** (`NN_EMPRESA_Planilha_Simples_2027.xlsx`) — abas 1-Faturamento, 2-DAS 2026 x 2027 (gráficos), 3-Compras, 4-Formação de preço (3 cenários, células amarelas editáveis), 5-Puro x Híbrido.
2. **Parecer em Word para o cliente** (`NN_EMPRESA_Parecer_Simples_2027.docx`). Cliente recebe SÓ Word.
3. **Relatório interno de divergência** (`NN_EMPRESA_Relatorio_Faturamento_x_Entradas.xlsx`) — só quando pedirem ou quando o estudo mostrar compras > 80% do faturamento ou recebimentos muito acima do declarado. **Nunca enviar ao cliente.**

Escopo: Simples puro × híbrido. **Não** comparar com Lucro Presumido/Real.

## Fontes (economizar tokens)

Pasta: `G:\Meu Drive\Trabalho ROF\Contabilidade\Arquivos RENATA Dominio\NN - Nome\AAAA\MM_AAAA\Relatorio\`.

- **Usar primeiro o que já está lançado/exportado**: relatórios .xls do Domínio, Razão (.xlsx), TXTs dos extratos, MDs. **Não ler PDFs de extrato** — se só houver PDF, converter uma vez para MD e usar o MD.
- Por mês: relatório **"Produtos monofásicos/subst. trib."** (abas Simples Nacional, Memória de cálculo, Anexo). A aba Anexo traz o faturamento dos 12 meses anteriores (base do RBT12).
- **Acompanhamento de Entradas** (aba Entradas): acumuladores 101–105 mercadorias, 300/301 fretes CT-e (124/224 remessas e 128/228 devoluções não entram).
- **Razão** das contas de banco (para o relatório de divergência): exportar do Domínio em .xlsx (o .xls de 6,5 MB derrubou o Drive).
- Drive: arquivos acima de ~6 MB derrubam a conexão — pedir exportação menor. Arquivos pequenos voltam inline (salvar com Write/base64).
- `.xls` com erro "Expected BOF record" → `comum.abrir_xls` converte com `soffice` automaticamente.

## Passo a passo

Scripts em `scripts/` (Python 3 + xlrd + openpyxl; Word com `docx` do Node — `npm install docx` se faltar). Rodar com `python -I` nos arquivos baixados.

```bash
python ler_apuracao.py mono_01.xls mono_02.xls ... -o apuracao.json
python ler_compras.py ent_01.xls ent_02.xls ... -o compras.json
python estudo_simples.py --apuracao apuracao.json --compras compras.json --empresa "NOME LTDA" --cnpj 00.000.000/0001-00 \
   --saida NN_NOME_Planilha_Simples_2027.xlsx --resumo resumo.json \
   --canal "Comissão do marketplace" --canal-pct 0.16 --despesas "Fretes" --usar-fretes --margem 0.10 --aliq-regular 0.092
node parecer.js resumo.json NN_NOME_Parecer_Simples_2027.docx [textos.json]
# relatório interno (opcional)
python ler_razao.py Razao.xlsx --excluir NOME_DA_EMPRESA SOBRENOME_SOCIO 00000000 -o recebimentos.json
python relatorio_divergencia.py --apuracao apuracao.json --recebimentos recebimentos.json --compras compras.json \
   --empresa "NOME LTDA (empresa NN)" --saida NN_NOME_Relatorio_Faturamento_x_Entradas.xlsx
```

- **Mês sem relatório** monofásico: `--mes-manual "07/2026;rpa=70336.04;das=4803.72[;mono=...]"` (RPA da aba Anexo, DAS da guia). Fica marcado com * no Word.
- **Canal**: e-commerce → "Comissão do marketplace" (~16%); loja física → "Taxas de cartão" (~3%). **Despesas**: `--usar-fretes` quando houver CT-e; senão `--despesas-pct` estimado. Estimativas sempre marcadas na planilha e no Word.
- `textos.json` do Word (opcional): `cliente` (com nome fantasia), `regime` (ex.: "Simples Nacional – Anexo I, 4ª faixa"), `data`, `resumo_extra`, `puro_hibrido_extra` (ex.: % de vendas para pessoa física), `premissas_extra`, `recomendacao`.
- `ler_razao.py`: recebimento = débito em conta de banco com contrapartida 504 (Clientes). `--excluir` tira transferências próprias/sócio (nome, sobrenome, CNPJ com e sem pontuação); "RESERVA STONE"/"DINHEIRO GUARDADO/RESGATADO" saem como aplicação. Conferir no print as contas de banco detectadas (`bancos`).
- Validar: abrir as planilhas recalculadas (`soffice --convert-to xlsx`) sem `#`; Word → PDF → conferir páginas.

## Regras de cálculo

- **2026**: receita monofásica tem PIS e COFINS zerados no DAS (LC 123 art. 18 §4º-A I).
- **2027-2028**: PIS (2,76%) + COFINS (12,74%) = 15,50% da partilha do Anexo I viram CBS 15,33% + IBS 0,17% (LC 214 Anexo XVIII). Nominais e parcelas a deduzir não mudam. O monofásico de PIS/COFINS acaba (Lei 10.485 só até 2026); no Simples só segrega monofásico e IBS/CBS por substituição (art. 18 §4º-A I na redação do art. 517 da LC 214).
- **Aumento do mês** = receita monofásica × (alíquota de PIS + COFINS da seção tributada normal do mesmo mês).
- **Carga 2026** = DAS pago ÷ faturamento; **carga 2027** = carga 2026 + %monofásico × alíquota PIS+COFINS. Projeção anual = faturamento 12 meses × carga.
- **Reajuste**: (1+p)(1 − custos% − carga27) = (1 − custos% − carga26). Na planilha: preço = custo ÷ (1 − soma dos % sobre a venda).
- **Híbrido** = (carga27 − fatia CBS/IBS) + alíquota regular × (1 − (compras + fretes) ÷ faturamento), crédito integral. Se compras + fretes > faturamento → **NÃO CONFIÁVEL** (não usar para decidir).
- Prazos da opção pelo regime regular no 1º semestre de 2027: até **30/10/2026**; cancelamento de **03/11 a 20/12/2026** (Res. CGSN 186/2026 art. 2º, redação da 194/2026). Opção semestral (LC 123 art. 13 §§9-11). Crédito do adquirente = valor cobrado no DAS (art. 23 §1º-A).

## Divergência (relatório interno)

Alertas automáticos: recebidos de clientes > 1,2x o declarado; compras > 80% do faturamento (LC 123 art. 29 X); queda da média mensal > 30%. Riscos citados: art. 34 (presunções de omissão), Lei 9.430/96 art. 42 (fora da pasta de legislação — conferir), art. 29 VIII, X, XI, art. 26 I, art. 29 §§1-2 (3/10 anos), art. 17 V e art. 31 §2º (regularizar débito em 30 dias). Quando o declarado não é confiável, dizer no parecer que o estudo da reforma depende de base real e marcar o híbrido como não confiável.

## Base legal

Textos em `Legislacao-Simples-Nacional/` (lc123-2006.md, lc214-2025.md, lc227-2026.md, lc238-2026.md, lei10485-2002.md, resolucao-cgsn-140/186/194) e `reforma-tributaria/`. Conferir o artigo no MD antes de citar; não citar de memória.

## Casos de teste (conferidos em out/2026)

| Empresa | Resultado esperado |
|---|---|
| **75 – A F EMERICH** (autopeças, Mercado Livre, 98% monofásico) | jan-set DAS 39.694,94 → 46.809 (+17,9%); fat. 12m 805.478,81; carga 6,74% → 7,95%; +R$ 9.738/ano; reajustes 1,47% / 1,83% / 2,34% (16% marketplace, fretes reais 14,3%, margem 10%); híbrido 9,2% = 10,35% → +R$ 19.374/ano → **puro**. Julho via `--mes-manual`. |
| **85 – LETICIA STANICHUK** (padaria PR, 3,8% monofásico) | fat. 12m 177.629,25; +R$ 52/ano; compras 405% do declarado → híbrido não confiável; Razão: recebidos de clientes jan-ago R$ 679.705,28 (15,2x o declarado), excluídos R$ 63.166,61, 7.339 lançamentos. |

(O parecer entregue ao Adilson em out/2026 usou carga média de 6,71%; o script usa DAS pago ÷ faturamento, por isso difere em centavos de ponto.)

## Regras ROF

- Não inventar número: tudo sai dos relatórios; o que for estimativa fica escrito "estimativa".
- Base legal sempre, com artigo.
- Linguagem simples no Word (cliente leigo); detalhes técnicos ficam na planilha.
- Relatório de divergência é interno. Nunca mandar ao cliente.
