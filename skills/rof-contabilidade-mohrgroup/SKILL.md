---
name: rof-contabilidade-mohrgroup
description: "MOHR GROUP LTDA (Miss Mohr Boutique), CNPJ 17.593.725/0001-33, código 1005 no Domínio, Simples Nacional (varejo de vestuário), bancos Itaú (6), Sicredi (8) e Sicoob (9), sócios Emerson Mohr e Sueli Ribeiro Mohr. Analista da empresa: concilia os 3 bancos, cruza extrato × folha × guias × notas × razão, separa pró-labore e retirada dos sócios, gera o TXT único do Domínio e as planilhas de retiradas. Usar quando mencionar Mohr, Mohr Group, Miss Mohr, Emerson Mohr, Sueli Mohr, o CNPJ 17.593.725/0001-33, a empresa 1005, ou enviar extrato, OFX, razão, balancete, folha ou guias dela — sempre junto com o rof-analista."
---
# MOHR GROUP (1005)

**Antes de tudo, siga o roteiro do `rof-analista` (cérebro):** leitura da pasta, consulta de CNPJ, conferência por script,
árvore de decisão, perguntas em lote e parecer. Esta skill só traz o que é da Mohr. Em conflito: decisão registrada → cérebro → esta skill.
- Dados, plano de contas e regras executáveis: `references/empresa.json`
- Favorecido → conta: `references/classificacao.md` (buscar pelo nome, não ler inteiro)
- Decisões já tomadas e pendências abertas: `references/decisoes.md` (buscar, não ler inteiro)

**Pasta do mês (Drive):** `1005_Mohr Group Ltda\Fiscal_Contabil\<ANO>\<MM_AAAA>\` (Extrato, Guias, Relatórios). Os `_extrato.md` já vêm prontos do Conversor ROF.
Scripts do cérebro em `../rof-analista/scripts/`. Sicoob: sempre OFX/CSV; PDF só se não houver outro.

## Particularidades (o que foge do padrão ROF)

1. **Sócios com pró-labore de 1 salário mínimo** (R$ 1.621,00; líquido R$ 1.442,69 após INSS 11%), cada um.
   Pagamento ao sócio, em ordem de data nos 3 bancos: até o líquido **D 188**; excedente **D 539** (Emerson) / **D 548** (Sueli).
   O PIX que cruza o limite é **um lote C** (C banco / D 188 / D 539 ou 548). Entrada do sócio: D banco / C 539 ou 548.
   INSS do pró-labore: 2 × R$ 178,31 → 191. O CPP patronal está no DAS (Anexo I).
2. **Auto Mais Itaú (11):** APL e RESGATE ficam fora do TXT (`IGNORAR`). O rendimento entra sempre: D 6 / C 432, mesmo que seja R$ 0,03.
   Se o líquido da Auto Mais no mês não zerar, o script avisa: lance o líquido D 11 / C 6 (ou o inverso).
3. **Aplicação Sicredi:** aporte mensal (APLIC.FINANC.AVISO PREVIO) D 71 / C 8. Sobras do Sicoob: D 9 / C 432.
4. **Transferência própria** (CNPJ 17593725000133, "MISS MOHR BOUTIQUE"): lançar uma vez só, D destino / C origem.
   Recebimento que passa pela **blink** é cliente (504), não transferência.
5. **IOF (373) e IRRF (375)** em linha própria, nunca embutidos. Guia com juros vai em lote C (juros 372). A conta de multa não existe no plano (pendência P7).
6. **Fatura Mastercard do Sicoob → 555**; o cartão "BUSINESS" está na 364 (pendência P3).
7. **Contas vigiadas:** 362 (prestador PF sem nota), 493, 506, 539, 548 e 555. Rode `variacao.py --vigiar 362` e comente no parecer.
8. **Comércio:** mercadoria = baixa do fornecedor (506) pela nota de entrada, nunca despesa. CMV/estoque: pendência P6.

## Fluxo (curto)

1. Cérebro, etapas 0 e 1: `consulta_cnpj.py 17593725000133` (Simples todo mês); meses N−1 a N−3; saldo inicial de cada banco = razão anterior.
2. Para cada banco: `extrato_dominio.py ler` → `extrato_dominio.py classificar -e references/empresa.json` → `conferir.py`
   (guias, folha, notas, razão, `--socios "EMERSON MOHR;SUELI RIBEIRO MOHR"`). Resolva os pendentes pela árvore do cérebro.
3. Junte os 3 bancos num CSV `data;banco;descricao;valor;conta;partidas;status` e gere o TXT:
   ```
   python scripts/gera_txt_mohr.py classificado.csv --empresa references/empresa.json --competencia MM/AAAA \
     --saldos "6=ini:fim;8=ini:fim;9=ini:fim" -o MOHR_MM_AAAA.txt
   ```
   Valores especiais na `conta`: `SOCIO:E`/`SOCIO:S` (o script divide 188 × 539/548), `IGNORAR` (Auto Mais) e `6`/`8`/`9` (transferência).
   Na coluna `partidas` vão as contrapartidas múltiplas, assim: `479=500,00+372=12,30`.
   **O script não grava o TXT se algum banco não fechar** (extrato e efeito do TXT) ou se houver status pendente.
   Ele grava também `retiradas_socios_AAAAMM_mohrgroup.xlsx` (padrão Mohr) e `_visao_socios.txt`, que serve só para as planilhas e **não se importa no Domínio**.
4. Planilhas do cérebro, a partir da visão (188E/188S separam os sócios):
   ```
   python ../rof-analista/scripts/planilha_socios.py --txt MOHR_MM_AAAA_visao_socios.txt --mes "Mês/AAAA" --empresa "MOHR GROUP LTDA" \
     --socio "EMERSON MOHR|035.870.159-70|188E,539" --socio "SUELI RIBEIRO MOHR|037.687.209-85|188S,548" --banco 6,8,9 \
     --nomes-conta "188E=PRÓ-LABORE EMERSON;188S=PRÓ-LABORE SUELI;539=EMERSON MOHR;548=SUELI RIBEIRO MOHR" \
     --planilha MOHR_Retiradas_Socios_AAAA.xlsx -o MOHR_Retiradas_Socios_AAAA.xlsx
   python ../rof-analista/scripts/planilha_socio_mes.py --txt MOHR_MM_AAAA_visao_socios.txt --competencia MM/AAAA --empresa "MOHR GROUP LTDA" \
     --cnpj 17.593.725/0001-33 --socio "EMERSON MOHR|035.870.159-70|188E,539" --banco 6,8,9 --anual MOHR_Retiradas_Socios_AAAA.xlsx -o MOHR_Emerson_MM_AAAA.xlsx
   ```
   Repita o segundo comando para a Sueli (`188S,548`).
5. Entrega: **um único TXT** + `retiradas_socios_AAAAMM_mohrgroup.xlsx` + planilha anual + planilha mensal de cada sócio + parecer de até 5 linhas.
   Registre as respostas novas em `references/decisoes.md` (quem validou e quando).
