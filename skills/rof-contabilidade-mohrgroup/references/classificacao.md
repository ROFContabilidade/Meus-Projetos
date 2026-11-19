# MOHR GROUP (1005) — favorecido → conta

Buscar (grep) pelo favorecido; não ler inteiro. Origem: razão abr–jul/2026, validado na skill anterior (acordo com a contadora).
As regras executáveis estão em `empresa.json` → `regras`. Estado: **C** = confirmado · **P** = provável (lança e marca) · **V** = vigiar/alertar no parecer.

| Favorecido / texto no extrato | Lançamento | Estado | Obs. |
|---|---|---|---|
| REDECARD / REDE MAST / REDE VISA / REDE AMEX CD0049487205 | D 6 / C 504 | C | |
| SICREDI ANTEC MASTER | D 8 / C 504 | C | antecipação de recebíveis |
| PIX/boleto de cliente (inclusive via blink) | D banco / C 504 | P | conferir com o relatório de vendas |
| RENDIMENTOS REND PAGO APLIC AUT MAIS | D 6 / C 432 | C | nunca omitir |
| APL APLIC AUTO MAIS / RESGATE APL APLIC AUTO MAIS | fora do TXT (`IGNORAR`) | C | líquido ≠ 0 → D 11 / C 6 |
| APLIC.FINANC.AVISO PREVIO | D 71 / C 8 | C | R$ 500/mês |
| CRED.DIST.SOBRAS (Sicoob) | D 9 / C 432 | C | |
| RECEITA FEDERAL 00.394.460/0058-87 — DAS | D 479 / C banco | C | achar a guia; juros 372 em lote C |
| RECEITA FEDERAL 00.394.460/0058-87 — INSS | D 191 / C banco | C | 2 × 178,31 do pró-labore |
| DEB.IOF / IOF | D 373 / C banco | C | |
| IRRF sobre aplicação | D 375 / C banco | C | nunca apareceu; monitorar |
| TAR (tarifas diversas, TAR PLANO ADAPT, TAR SERV.COBR., negativação) | D 370 / C banco | C | |
| DEB PACOTE SERVICOS | D 369 / C 9 | C | |
| CRED COBRANCA DESCONTADA | 369 | P | é crédito: ver P5 |
| JUROS CTA GARANTIDA | D 372 / C 9 | C | |
| DEB.EMPRESTIMO DOC. 01290747 / LIQUIDACAO DE PARCELA / COOPERATIVA CRE | D 166 / C banco | C | juros da parcela: ver P8 |
| DEB.CONV.DEM.EMPRES DOC. MASTERCARD (Sicoob) | D 555 / C 9 | C | 555 cadastrada? ver P2 |
| BUSINESS (cartão) | D 364 / C banco | P | 364 × 555: ver P3 |
| CHQ CMP INTEGRADA | D 506 / C 9 | P | só com nota de entrada |
| PRUDENTIAL SEG / SEGURO PRESTAMISTA | D 358 / C banco | C | |
| DA VIVO / telefone | D 356 / C banco | C | |
| Custas de protesto | D 365 / C 8 | C | |
| COMUNHA CRISTA ABBA | D 540 / C 8 | C | |
| UBER DO BRASIL / AUTOPISTA PLANALT / PLUXEE FROTA / GUSTAVO KLEMTZ | D 541 / C banco | C | |
| MARTINSCARVALHO CO / DELIZ INDUSTRIA / DS FATIMA COMERCIO | D 506 / C banco | C | baixa pela nota |
| ALCA SERV DE CO / SUL SYSTEM I CA | D 359 / C banco | C | |
| Honorários contábeis | D 510 / C 8 | C | |
| Alimentação | D 521 / C 8 | C | entidade: empresa ou sócio? |
| VENISSE BISPO DUTRA 42.329.751/0001-04 | D 493 / C banco | P | 493 genérica: natureza? |
| GABRIELE FERREIRA SILVA | D 187 / C banco | P | conferir com o líquido da folha |
| JACIRA MENDES PEREIRA (PF) | D 362 / C banco | V | prestador PF sem nota |
| GRACIELI DO MONTE (PF) | D 362 / C banco | V | idem |
| ZELIA ANTONIO CELESTIN (PF) | D 362 / C banco | V | idem |
| MARCIA BRUSKY (PF) | D 362 / C banco | V | idem |
| PAULO CESAR SANTOS DE (PF) | D 362 / C banco | V | idem |
| PIX para EMERSON MOHR 035.870.159-70 | `SOCIO:E` → 188 até 1.442,69, depois 539 | C | lote C quando cruza |
| PIX para SUELI RIBEIRO MOHR 037.687.209-85 | `SOCIO:S` → 188 até 1.442,69, depois 548 | C | lote C quando cruza |
| Entrada de Emerson / Sueli | D banco / C 539 / 548 | C | devolução ou aporte |
| PIX entre contas próprias (17.593.725/0001-33, MISS MOHR BOUTIQUE) | D destino / C origem | C | uma vez só |
