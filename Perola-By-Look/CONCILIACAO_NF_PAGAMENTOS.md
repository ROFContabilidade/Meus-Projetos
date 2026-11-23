# Pérola By Look: notas de entrada × pagamentos (01 a 10/2026)

Fontes: relatório de entradas do Domínio (01/01 a 31/10, emitido em 23/10), os XML das NF-e e NFS-e, o razão de 01 a 06 e os extratos de 07 a 10.
Script: `ferramentas/nf_pag.py`. Cruzamento por CNPJ ou nome primeiro e por valor depois, com janela de −5 a +75 dias da emissão.

**Regra (Rosangela, 23/11/2026):** se existe nota de entrada, o pagamento é D 506 / C banco. Nunca custo nem despesa: a nota já levou o valor ao estoque ou à despesa pela integração fiscal.

## A. 07 a 10/2026: como vai ser lançado

| Data | Banco | Pago | Nota | Lançamento |
|---|---|---|---|---|
| 02/07 | Itaú | 926,00 + 0,28 | Norte Vest 1520 (926,28) | D 506 926,28 |
| 08/07 | PagBank | 318,72 + 1.171,09 | Sul América 59807 e 63690 (06) | D 506 |
| 12/08 | Itaú | 1.314,00 | Maurício 34644 (1.289,07) | lote: D 506 1.289,07 + D 55 24,93 (diferença paga a mais) |
| 13/08 | Itaú | 1.200,00 | Ludy Flores 906 (1.645,00) | D 506 1.200,00. **Ficam 445,00 em aberto** |
| 13/08 | PagBank | 187,22 + 1.171,09 | Sul América de **07/2026: notas não escrituradas** | D 506, depois de escriturar as NFS-e de 07 |
| 14/08 | Itaú | 1.980,00 | Mercedes Calle 406 | D 506 |
| 02/09 | Itaú | 1.125,00 + 124,19 | Genilda 1089 (1.200,00) | lote: D 506 1.200,00 + D 55 49,19 |
| 04/09 | Itaú | 1.180,00 | José Chachaque 389 (480,00) | lote: D 506 480,00 + D 55 700,00 (mercadoria sem nota) |
| 04/09 | Itaú | 785,00 | Águia Fashion 723 (765,00) | lote: D 506 765,00 + D 55 20,00 |
| 12/09 | PagBank | 169,41 + 1.273,47 | Sul América 80927 e 85050 (08) | D 506 |
| 08/10 | Itaú | 1.500,00 (David Rojas Rivera, CNPJ 50.855.064) | Modas Carol 225 | D 506 (pago antes do vencimento de 08/11) |
| 13/10 | Itaú | 292,65 + 1.273,47 | Sul América 91083 e 97199 (09) | D 506 |
| 19/10 | Itaú | 185,00 | Singular 6393 | D 506 |
| mensal | n/a | n/a | Senff (51,20 · 3,99 · 5,30): comissão descontada do repasse | D 506 / C 504 |
| em aberto | n/a | n/a | Michael Fashion 336 (1.500,00, vencimento 08/11): **XML existe, nota não escriturada** | escriturar em 10. Pagamento em 11 |

## B. 01 a 06/2026 (já lançado): pagamento de nota lançado em custo ou despesa

O custo ou a despesa ficaram **em dobro**: entrou pela nota (estoque ou despesa a crédito da 506) e de novo pelo pagamento. E a 506 ficou em aberto.

| Pagamento | Nota | Valor | Lançado em | Ajuste |
|---|---|---|---|---|
| 25/03 Itaú | Vest Bellas 43571 | 684,75 | 470 | D 506 / C 470 |
| 26/03 Itaú | Vest Bellas 43613 | 156,75 | 470 | D 506 / C 470 |
| 13/04 Itaú (Olinda Lopes Caldeira) | Caldeira 18518 | 1.944,00 | 362 | D 506 / C 362 |
| 29/04 Itaú (Olinda Lopes Caldeira) | Caldeira 18568 | 1.458,00 | 362 | D 506 / C 362 |
| 18/05 Itaú | Norte Vest 1224 (parte PIX) | 658,66 | 470 | D 506 / C 470 |
| 26/05 Itaú | Norte Vest 1259 | 575,19 | 470 | D 506 / C 470 |
| 27/05 Itaú | Norte Vest 1267 | 890,19 | 470 | D 506 / C 470 |
| 07/01 PagBank | Paes e Bastos NFS-e 55 | 314,00 | 362 | D 506 / C 362 |
| 01 a 06 PagBank/Itaú | 10 NFS-e da Sul América | 6.318,62 | 366 (e 1.113,52 na 493) | D 506 / C 366 (e C 493) |
| **Total** | | **13.000,16** | 470: 2.965,54 · 362: 3.716,00 · 366/493: 6.318,62 | |

## C. Notas sem pagamento em banco (continuam na 506)

| Nota | Valor | Forma de pagamento no XML |
|---|---|---|
| Hanan Modas 912 (08/05) | 3.180,60 | 01 = dinheiro |
| Norte Vest 1224, parte em dinheiro (16/05) | 1.400,00 | 01 = dinheiro |
| Julia Comercial 9347 (19/05) | 395,88 | 01 = dinheiro |
| Julia Comercial 9376 (11/06) | 680,82 | 01 = dinheiro |
| Norte Vest 1416 (19/06) | 629,10 | 17 = PIX (não aparece em nenhum banco) |
| Luany Gonçalves NFS-e 24 (13/04) | 660,00 | n/a |
| Ludy Flores 906, saldo (08/2026) | 445,00 | 90 = sem pagamento |
| **Total** | **7.391,40** | |

## D. A 506 não fecha por fornecedor

A 506 é uma conta única ("Fornecedor modelo"). De 01 a 06, vários pagamentos **sem nota** foram debitados nela: Chique Modas 5.065, Dillymodas 1.760, Amanda Modas (vários), Lu Modas 1.095, Big Girls 1.644 e "PIX enviado" sem nome. Ao mesmo tempo, pagamentos **com nota** foram para 470, 362 e 366 (quadro B). Por isso o saldo de 22.401,50 C não representa o que se deve aos fornecedores.
Sugestão: depois dos ajustes do quadro B, os pagamentos sem nota que estão na 506 vão para a 55 (D 55 / C 506). O saldo que sobrar na 506 tem que ser igual à soma do quadro C.
