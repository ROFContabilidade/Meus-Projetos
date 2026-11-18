# Classificação — ÓTICA VISOUUP (118)

As regras executáveis ficam em `references/regras.json`. A primeira regra que casar vale, então a ordem importa. `t` = D saída / C entrada, `c` = trechos do histórico, `st` = CONFIRMADO / PROVAVEL / PERGUNTA.

| Padrão no extrato | Conta | Observação |
|---|---|---|
| RECEBIMENTO REDE, REDECARD, AT/DB0105585564, SENFFNET | C 504 | cartões |
| PIX recebido de pessoa | C 504 | venda |
| PIX RECEBIDO ADRIANA R DE PAULA LTDA | C 504 (proposta) | não veio do Sicredi da matriz. Pedir a origem (outra conta/maquininha?) |
| RENDIMENTOS REND PAGO APLIC AUT | C 432 | |
| TAR ... | D 525 | tarifa |
| PIX ENVIADO OTICA VISOLUZ | D 152 | conferir no Sicredi da matriz (mesmo dia, mesmo valor) |
| PIX OTICA VISOLUK / PEDRO JEFFERSON LUIZ | D/C 166 | Visoluk (CNPJ 49.192.337/0001-37) |
| BOLETO SC COMERCIO / ARQUEM / SINGULAR | D 506 | baixa de NF. Juros do boleto vão para a 372 (lote C) |
| HOYA, SALES VISION, LITZ ARMAÇÕES | D 506 + pergunta | fornecedor sem nota na filial |
| SHOPPING POPULAR | D 341 | aluguel (a confirmar) |
| SUNAGA SERVICOS MEDICOS | D 366 | exames (a confirmar) |
| Empregados CLT da matriz, METROCARD, CEF MATRIZ | D 152 | folha é da matriz |
| PF sem vínculo | D 362 | vigiada |
| PIX para ADRIANA RODRIGUES DE PAULA (CPF) | D 531 | planilha de sócios |
| Renner, Torra Torra, Realize, Pefisa, Havan, farmácia, clínica | D 531 | gasto pessoal (a confirmar) |
| RBA CONTABILIDADE | D 361 | |
| COPEL 354 · TIM 356 · Município de Colombo 350 | | |
| iFood, 99 Food, padaria, mercado | D 521 | |
| Estapar, posto, Pagar.me, armarinho, Dez Produções | D 359 | miúdas |
