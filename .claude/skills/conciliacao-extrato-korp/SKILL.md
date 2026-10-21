---
name: "conciliacao-extrato-korp"
description: "Conciliação de extrato Korp: compara o relatório 'Extrato Bancário' do Korp com o 'Razão Contábil' da conta do banco (ex.: 2871 Sicredi Matriz, Korp Informática, Domínio 140/145) e aponta por que o razão não fecha — lançamentos que faltam no razão, sobras, rateios por centro de custo e diferença de saldo. Usar quando enviarem os dois .xlsx (extrato e razão) pedindo conferir diferença, 'razão não fecha' ou conciliação de extrato Korp."
---

# Conciliação de extrato Korp (extrato × razão)

**Base de comparação = EXTRATO.** O razão é conferido contra ele (o extrato é o que o banco realmente movimentou).

## Entradas
- `*_Matriz_2.xlsx` → "Extrato Bancário" (colunas: Data, Descrição, Informação, Conta, Desc. C. Gerencial, D/C, Valor, Saldo; rodapé "RESUMO DO EXTRATO" com saldo inicial, total créditos/débitos e saldo final).
- `*_Matriz.xlsx` → "Razão Contábil" da conta do banco (Data, N. Lanc., Obs, Empresa, Débitos, Créditos, CC, Saldo Acumulado; "Saldo Anterior" no cabeçalho).

## Procedimento
1. Rodar `scripts/conciliar.py EXTRATO.xlsx RAZAO.xlsx` (corrige o styles.xml inválido que impede o openpyxl de abrir os arquivos do Korp; sempre `python3 -I`).
2. Conferir o saldo inicial (extrato = "Saldo Anterior" do razão) e comparar totais de débito/crédito e saldo final.
3. O script casa por **data + valor** (extrato `-` = crédito no razão da conta banco; `+` = débito) e depois agrupa **rateios**: um movimento do extrato = soma de várias linhas do razão na mesma data (cartão de crédito, lote CNAB, vários centros de custo). Rateio que fecha não é erro.
4. O que sobra é a causa: **faltam no razão** (no extrato e sem lançamento) e **sobram no razão** (lançado sem movimento no banco).
5. Validar: soma dos itens que faltam/sobram = diferença entre os saldos finais (razão − extrato). Se não fechar, olhar data trocada, valor digitado errado ou lançamento duplicado.

## Resposta ao usuário
- Saldos (inicial, final de cada um, diferença) e totais débito/crédito de cada lado.
- Tabela dos lançamentos faltantes: data, histórico do extrato, valor, efeito (faltou débito/crédito).
- Lista curta dos rateios que parecem divergir mas fecham.
- Providências: TED entre Matriz/Filial → conferir o par no razão da outra empresa; pagamentos sem lançamento → contas a pagar sem baixa/data diferente. Oferecer TXT corrigido (precisa de CC e contrapartida).

## Caso de referência (set/2026, conta 2871 Sicredi Matriz, Korp 140)
Diferença de 67.888,00 (razão -47.685,64 × extrato 20.202,36) = TED Filial→Matriz 28/09 de +70.000,00 sem lançamento − Edu Informática 16/09 (-1.904,00, AD00121) − Mercado Livre 11/09 (-208,00, AC374).
