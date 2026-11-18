---
name: rof-contabilidade-otica-visoluz
description: "ÓTICA VISOLUZ (ADRIANA R. DE PAULA LTDA), CNPJ 24.026.777/0001-93 (matriz) e filial 24.026.777/0002-74, código 34 no Domínio, Simples Nacional Anexo I (comércio varejista de artigos de óptica, Colombo/PR), banco Sicredi 44846-8 (conta 8). Lançamentos do extrato, conciliação, folha integrada, retiradas da sócia, mútuo com a Ótica Visoluk e TXT mensal para o Domínio. Usar quando mencionarem Visoluz, Ótica Visoluz, Adriana R. de Paula, o CNPJ 24.026.777, a empresa 34, ou enviarem extrato, razão, balancete, folha ou guias dela."
---

# ÓTICA VISOLUZ (ADRIANA R. DE PAULA LTDA): empresa 34

**Antes de tudo, siga o roteiro do `rof-analista` (cérebro).** Esta skill só traz o que é da empresa.
- Dados: `references/empresa.json` · Regras de classificação (máquina): `references/regras.json`
- Classificação explicada: `references/classificacao.md` · Decisões já tomadas: `references/decisoes.md` (buscar com grep, não ler inteiro)

## Pasta do cliente (Google Drive)
`G:\Meu Drive\Trabalho ROF\Contabilidade\Arquivos RENATA Dominio\34 - Otica Visoluz\<ANO>\<MM_AAAA>\`
- `Extrato\` (PDF Sicredi + `_extrato.md` do Conversor) · `Guias\` (DAS, Extrato do Simples, ICMS antecipado)
- `Relatorio(s)\` (FAT.<MM>.<AA>_Visoluz.xlsx = faturamento matriz, filial e Mtz+Fl · NF_Entrada) · `Doc's\` (XML) · `DeSTDA\`
- `<ANO>\Automoção Contabil\`: Contas.xls (plano), Razão.xls, Balancete.pdf, **Extrato Mensal.pdf (folha)**
- Atenção: em 18/11/2026 a Rosangela salvou relatórios da Visoluz (Razão_Visoluz.xls até 10/2026, Pagamento de Encargos, Resumo de impostos, GR-PR) em `118 - Otica VisouUP\2026\Relatorio Claude`. Conferir sempre o CNPJ do arquivo, não a pasta.

## Rotina do mês (scripts)
```
python <rof-analista>/scripts/extrato_dominio.py ler <MM>/Extrato/<arquivo>_extrato.md -o norm.csv
python scripts/folha_csv.py "Extrato Mensal.pdf" -o folha.csv
python scripts/classificar_visoluz.py --extrato norm.csv --folha folha.csv --comp MM/AAAA \
       --saida-csv classificado.csv --saida-txt 34_OTICA_VISOLUZ_AAAA-MM.txt
```
Depois: `planilha_socios.py` e `planilha_socio_mes.py` do cérebro (sócia `ADRIANA RODRIGUES DE PAULA|032.149.559-42|531,188`)
e `variacao.py --vigiar 362`. Os itens PROVAVEL e SEM PROVA vão para a tabela de perguntas.

## Particularidades
- **Matriz + filial no mesmo DAS.** O Domínio 34 escritura a matriz; a receita da filial (FAT "Filial") entra no
  PGDAS, mas não na 408. Os PIX da filial (`24026777000274`) entram no Sicredi da matriz e vão para a **544 Transferências entre matriz e filial** (transitória, 1.1.1.04.001), nunca para 504. A 544 precisa zerar com o extrato da filial. A conta 9 (Itaú) está inativa desde 28/07/2026.
- **Folha integrada** no razão (Extrato Mensal): D 274/308/331/278… C 187; INSS 191; FGTS 192; pró-labore
  1.621,00 bruto / **1.442,69 líquido** (188). O adiantamento é lançado pela folha como **D 25 / C 5 (caixa)**, então o PIX
  do adiantamento no banco é **D 5 / C 8**. O líquido da folha pago por PIX é **D 187**.
- **Sócia (Adriana, CPF final -42):** PIX → 188 até o líquido do pró-labore do mês e o excedente → 531. Retiradas muito acima
  do pró-labore com prejuízo acumulado: perguntar todo mês (Lei 15.270 se passar de 50 mil).
- **Ótica Visoluk (CNPJ 49.192.337/0001-37, de Pedro Jefferson Luiz):** não emite NF para a Visoluz, então PIX
  enviados e recebidos são mútuo → **152**.
- **Fornecedores com NF** (Hoya, SC Comércio, Grown, Galáxia, LCB, JKLens, JN, Kenerson, Arteres, Litz, ABA): baixa na **506**;
  a ABA (SST) tem NFS-e de 116,40 e a diferença do boleto vai para 372.
- **Encargos em aberto (relatório de 18/11/2026):** FGTS de 06 a 11, consignado Crédito do Trabalhador (541) descontado e não repassado, tributos federais 06. Cobrar todo mês.
- **Vigiar:** 504 credora (recebido × faturado), 187/191/192 sem baixa, 362 (Isabella e Camila fora da folha), caixa 5 credor,
  538 adiantamento de clientes, DAS/FGTS/ICMS antecipado pagos fora do Sicredi, conta Itaú 0098929-8 (conta 9).
- **Simples:** a Receita mostra exclusão em 31/12/2026 e há estudo de Lucro Presumido na pasta. Confirmar o regime de 2027
  antes de lançar janeiro.
