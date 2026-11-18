# Ótica Visoluz: classificação do extrato Sicredi (conta 8)

Fonte: razão 01-09/2026 + folha + notas de entrada. **Status:** P = provado por documento; R = padrão do razão ou
proposta do analista (aguarda validação); ? = sem prova (vai para pergunta). A versão para a máquina está em `regras.json`.

## Entradas
| Padrão no extrato | Conta | St | Observação |
|---|---|---|---|
| SICREDI DEBITO / ANTEC / ANTECIPACAO (Visa, Master, Elo) | C 504 | P | liquidação de cartões |
| PIX de pessoa física ou jurídica (cliente), Negresco, Senffnet, Freios Itororó | C 504 | R | venda |
| PIX de/para 24026777000274 (FILIAL) | 544 | P | transferência entre matriz e filial; zera com o extrato da filial (Rosangela, 18/11/2026) |
| PIX de 24026777000193 (próprio CNPJ) | C 9 | ? | provável transferência do Itaú |
| PIX de Ótica Visoluk / Pedro Jefferson | C 152 | R | mútuo |
| PIX da sócia (CPF 03214955942) | C 531 | R | devolução |
| Resgate de aplicação | C 11 (+ C 432 dos centavos) | P | |
| Estorno de cesta/tarifa | C 525 | P | |

## Saídas
| Padrão | Conta | St | Observação |
|---|---|---|---|
| PIX empregado = líquido da folha do mês anterior | D 187 | P | |
| PIX empregado = adiantamento da folha do mês, ou dia 15-25 ≥ 300 | D 5 | P/R | a folha lança D25/C5 |
| PIX empregado ≥ 200 sem par na folha | D 187 | R | |
| PIX empregado < 200 | D 521 | R | vale-alimentação (a folha desconta VA) |
| PIX sócia | D 188 até 1.442,69/mês; excedente D 531 | R | lote `|6000|C|` |
| Ótica Visoluk / Pedro Jefferson | D 152 | R | mútuo |
| Hoya, SC Comércio, Grown, Galáxia, LCB, JKLens, JN, Kenerson, Arteres, Litz | D 506 | P | NF no razão |
| ABA Consultoria (SST) | D 506 116,40 + D 372 diferença | P | |
| Arquem Sistemas | D 359 | R | software |
| Amil | D 366 | R | confirmar se o plano é dos empregados |
| Sunaga Serviços Médicos | D 306 | R | |
| Metrocard | D 530 | P | VT |
| Paes e Bastos / RBA Contabilidade | D 361 | P | o razão usava 527 (errado) |
| Copel 354 · recarga 356 · IOF 526 · juros cheque especial 372 · tarifas/cesta/cobrança 525 · custas de protesto 365 | | P | |
| Integralização de capital Sicredi | D 525 | R | correto: ativo (cota de cooperativa) |
| Aplicação poupança / aviso prévio | D 11 | P | |
| DEB.CTA.FATURA (cartão Sicredi) | D 364 | ? | pedir a fatura |
| Shopping Popular | D 320 | ? | provável aluguel |
| Receita Federal / DARF sem guia | D 350 | ? | pedir a guia |
| Supermercado, padaria, lanche, 99Food | D 521 | R | |
| Posto, estacionamento | D 527 | R | |
| Renner, paróquia, brinquedos, farmácia, pet, agropecuária | D 531 | ? | pessoal da sócia |
| Isabella Paula de Souza, Camila Hadassa Muller | D 362 | ? | fora da folha: alerta |
| Outros PIX a pessoa física | D 362 | ? | |
