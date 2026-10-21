---
name: "conciliacao-grupo-korp"
description: "Conciliação Grupo Korp: confere o extrato bancário Korp × razão da conta do banco (2871 Sicredi) das empresas do grupo — Korp Matriz (Domínio 140), Korp Filial (145) e DCK Serviços de T.I. (144) —, mostra por que o razão não fecha, sugere a conta do plano de contas Korp (considerando o centro de custo) para cada lançamento e monta a planilha de diferenças para o cliente. Usar quando enviarem Extrato e Razão (.xlsx do Korp) de Matriz, Filial ou DCK, ou falarem em conciliação do Grupo Korp, razão que não fecha, conta sugerida ou validação de extratos jan–out."
---

# Conciliação Grupo Korp (extrato × razão × plano de contas)

Substitui/amplia a skill `conciliacao-extrato-korp`. Base de comparação = **EXTRATO** (movimento real do banco); o razão é conferido contra ele.

## Empresas do grupo
| Empresa | Domínio | CNPJ | Nº no razão Korp | Banco |
|---|---|---|---|---|
| KORP INFORMÁTICA LTDA EPP — Matriz | 140 | 03.623.045/0001-00 | 1 | conta 2871 Sicredi (1.1.1.2.4) — extrato "SIC/MATRIZ" |
| KORP INFORMÁTICA — Filial | 145 | 03.623.045/0002-91 | 9 | 2871 Sicredi — "SIC/FILIAL" |
| DCK SERVIÇOS DE T.I. LTDA EPP | 144 | 13.645.287/0001-59 | 2 | 2871 Sicredi — "SIC/DCK" (também Itaú-DCK, aplicações) |

Mesmo plano de contas Korp nas três (a conta 2871 = Banco Sicredi em todas). Plano: `Plano de Contas - Atualizado.xls` no Drive (id `1exuSA2c8TgIrSVVPpw7ZCVLQN1E01lZH`, autor korp.rosangela) — baixar com `download_file_content` (vem em base64: `jq -r .content | base64 -d`), ler com `xlrd` (`pip install xlrd`). O **código reduzido** (ex.: 2698) é o número que vai no lançamento/TXT da Korp; coluna "Classificação" (ex.: 3.1.3.3.1.1) é a árvore. Conta **analítica** = a que não tem filha (`outra.startswith(cod+'.')`). Contas "NAO USAR" nunca sugerir. Confirmar o reduzido sempre pelo NOME no plano (erro já ocorrido: energia é 2688, despesas diversas 2687).

## Entradas
- **Extrato Bancário** (.xlsx do Korp): Data, Descrição, Informação, Conta, Descrição C. Gerencial, D/C (`+` entrada / `-` saída), Valor, Saldo; rodapé "RESUMO DO EXTRATO" (saldo inicial, créditos, débitos, saldo final).
- **Razão Contábil** da conta 2871: Data, N. Lanc., Obs ("VLR. DOCUMENTO Nro.: <doc> <favorecido>"), Empresa, Débitos, Créditos, CC, Saldo Acumulado; "Saldo Anterior" no cabeçalho; "Total :" por mês. No razão da conta do banco, **débito = entrada, crédito = saída**.

## Passo a passo
1. `scripts/preparar_xlsx.sh EXTRATO RAZAO pasta/` — conserta o styles.xml inválido (sempre `python3 -I`). Gera `a.xlsx` (extrato) e `b.xlsx` (razão).
2. `ler_extrato_razao.py` (gera `data.pkl`) → `casar_extrato_razao.py` (gera `res.pkl`):
   - casa **data + valor exato**;
   - o que sobra é tratado por **dia**: se num dia há 1 movimento do extrato sem par e a soma das linhas restantes do razão na mesma data é igual ao valor, é **rateio/lote** (lote CNAB, fatura de cartão, vários CC) — fecha. **Não usar combinações de subconjuntos em dias com muitas linhas** (explode; DCK tem 40–55 linhas por dia). Subconjunto só até ~16 linhas.
   - sobras reais = divergências; conferir que (soma do extrato sem razão) − (soma do razão sem extrato) = diferença dos saldos finais.
3. Conferir saldo inicial (= "Saldo Anterior"), totais de débito/crédito e saldo final de cada lado; mensal para períodos longos (diferença do mês × acumulada).
4. **Conta sugerida** (`planilha_conta_sugerida.py`, lê `a.xlsx`, `b.xlsx`, `plano.xls` na pasta): uma linha por lançamento do razão — N. Lanc, data, valor, histórico/categoria do extrato, confere?, CC, área do CC, código reduzido/classificação/nome sugeridos, confiança (Alta/Média/Baixa) e observação; aba "Faltam no razão" para os movimentos sem lançamento; aba "Resumo".
5. **Planilha para o cliente** (`planilha_cliente.py`): Resumo, Resumo mensal (fórmulas: saldo final = inicial + entradas − saídas; diferença acumulada e do mês; situação), Diferenças (item a item com valor, conta sugerida e o que fazer; total confere com o resumo, "não explicada" = 0) e Lançamentos agrupados (dias em que o lote fecha). Sem observações internas. Recalcular com `soffice --headless --convert-to xlsx` para ficar com valores em cache e conferir que não há `#` de erro.
6. Salvar em `Korp/<Matriz|Filial>/<AAAA-MM>/` ou `DCK/<ano>/`, commit/push e enviar (SendUserFile).

## Regras de conta sugerida (histórico → conta; reduzido)
Pagamentos de folha passam pelo passivo, não pela despesa: férias 2524 · rescisão (e VA/VR dif. CCT de rescisão) 2523 · salários 2521 · FGTS 2530 · INSS 2531 · IRRF 2533 · contrib. sindical 2529 · VT 3050 · refeição/ticket 3046 · plano de saúde (Unimed) 3044 · seguro de vida 3047 · exames SESI/saúde ocupacional 3107 · recrutamento (Gupy, Mapa) 3113.
Tributos: ICMS 2511 · PIS 2512 · COFINS 2513 · ISS 2516 · DARF unificado = INSS 2531 + IRRF 2533 (separar pela guia) · retenção "nº/U" do Ministério da Fazenda 2822 (confirmar).
Custo de serviço terceiro (por CC/categoria): Desenvolvedor 3139 · Suporte 3140 · Qualidade 3138 · Consultores 3065 · PJ 3067 · PJ Comercial 3141 · software/assinaturas 2859 (alt. 2839).
Administrativo: tarifa bancária e IOF cartão 2698 · energia 2688 · telefone 2657 · internet 3059 · condomínio 2869 · honorários contábeis 2628 / advocatícios 2629 · copa 2838 · expediente 2664 · frete/motoboy 2658 · táxi/Uber 2680 · viagens (adm) 2647 · bens de pequeno valor 2649 · despesas diversas 2687.
Comercial: hospedagem 2587 · publicidade 3060 · brindes 3133 · viagens/deslocamento 3034 · telefone 2592 · internet 2870.
Receitas/ativo: recebimento de cliente (lote CNAB, mensalidade, consultoria, desenvolvimento, LDU) 2436 · TED entre empresas/bancos 2872 (Transferência de recursos) · empréstimo da DCK 3085 · empréstimo entre Matriz e Filial 3086 (ou 2861) — confirmar.

## Centro de custo (instrução do usuário: "o plano separa por centro de custo")
CC conhecidos (Korp): **CC320 ADM geral · CC337 Desenvolvimento · CC345 Suporte · CC379 Comercial · CC506 Qualidade · CC644 Consultoria/CS**. A conta de despesa muda com o CC: CSP em CC337→3139, CC345→3140, CC506→3138, CC644→3065; CC379 usa contas comerciais; CC320 usa administrativas. **CCs sem de-para** (aparecem nos razões: 384, 476, 833, 744, 335, 318, 314, 616, 645, 344, 830, 773, 831, 341, 346, 321, 485): marcar "CC sem de-para", baixar a confiança e **pedir a tabela de CCs ao usuário** — não inventar. Registrar aqui a tabela quando vier.

## Achados já registrados
- **Matriz 09/2026:** razão −47.685,64 × extrato 20.202,36 (dif. 67.888,00) = TED Filial→Matriz 28/09 +70.000,00 sem lançamento − Edu Informática 16/09 (1.904,00, AD00121) − Mercado Livre 11/09 (208,00, AC374). TEDs/empréstimos entre Matriz, Filial e DCK cruzam nos dois lados.
- **Filial 09/2026:** fecha (64.024,21 → 15.284,93), sem diferença.
- **DCK jan–20/10/2026:** extrato 344.458,35 × razão 1.695.233,57 (dif. 1.350.775,22) = 5 TEDs "SIC/DCK para ITAU-DCK" lançadas a débito no razão sem movimento no extrato (22/06 500,00; 10/07 400.000,00 + 150.000,00; 17/07 400.000,00; 17/08 400.000,00; N. Lanc 151850–151854) + 18 tarifas de cobrança de outubro (275,22) não lançadas. Jan–mai e set fecham. Pendente: cruzar empréstimos DCK×Korp de jan–ago.

## Cuidados
- Pedido do usuário: planilha de conta sugerida traz **N. Lanc do razão, data e valor (conferido com o extrato)** e a conta do plano; não alterar N. Lanc (conferir 1:1 com o razão original — já validado).
- Mês de outubro/2026 da DCK é parcial (até 20/10): sem fechamento mensal.
- Lançamentos "AC…" sem categoria no extrato: baixa confiança (bem de pequeno valor 2649 por padrão).
- Não gerar TXT sem a contrapartida e o CC definidos pelo usuário; TXT da Korp exige CC nos dois lados (ver skill `rof-contabilidade-folha-korp`).
