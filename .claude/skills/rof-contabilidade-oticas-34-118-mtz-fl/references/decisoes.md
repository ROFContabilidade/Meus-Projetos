# Óticas 34 (matriz) e 118 (filial): decisões da contadora

Buscar com grep (favorecido ou valor). Coluna "Vale" = 34, 118 ou ambos. Decisão nova entra no fim, com quem validou e quando.
Valor 20% fora do padrão ou favorecido novo = perguntar de novo.

| Data | Vale | Padrão/favorecido | Decisão | Validado por |
|---|---|---|---|---|
| 13/11/2026 | ambos | Leiaute TXT | Um TXT por mês e por empresa, em ordem de data. Um movimento = um lançamento (lote `|6000|C|` / `|6000|D|` quando houver mais de uma contrapartida) | Rosangela/Elen (regra geral ROF) |
| 18/11/2026 | ambos | Skill única | Matriz e filial tratadas numa skill só (`rof-contabilidade-oticas-34-118-mtz-fl`), com TXT separados. A skill antiga da filial (visouup) será apagada; a `rof-contabilidade-otica-visoluz` é substituída por esta | Rosangela |
| 18/11/2026 | ambos | Ligação matriz↔filial | Conta **544 TRANSFERÊNCIAS ENTRE MATRIZ E FILIAL (1.1.1.04.001)**, sintética 543 (1.1.1.04 NUMERÁRIO EM TRÂNSITO), **criada nas duas empresas com o mesmo código**. Substitui a 152 "Empréstimo Ótica Visoluz" da 118 (não é empréstimo: mesma PJ, o dinheiro não volta). 544 da 34 + 544 da 118 = 0 no unificado | Rosangela |
| 18/11/2026 | ambos | Despesa da matriz paga pela filial (VA/PIX a empregados da matriz, Metrocard, CEF/FGTS, salários) | 118: D 544 / C 8. 34: D despesa ou obrigação / C 544 (o mesmo movimento gera as duas pernas) | Rosangela (explicado e aceito em 18/11) |
| 18/11/2026 | 34 | Conta 9 Itaú 0098929-8 | Inativa no Domínio desde 28/07/2026. Não lançar nela depois dessa data | Rosangela (print do plano) |
| 18/11/2026 | 34 | Sócia Adriana (PIX para o CPF 032.149.559-42) | 188 até o pró-labore líquido do mês (1.442,69) e o restante na 531. **01-06/2026 já declarados na EFD-Reinf: NÃO ALTERAR** (531 líquido D-C: jan 9.148,98; fev 3.987,31; mar 3.407,31; abr -13.862,69; mai 11.037,84; jun -942,69, conferido com o Razão_531 emitido em 18/11; o -942,62 anotado antes era erro de digitação. Em 31/03 há o fechamento do trimestre 531→539 (16.543,60), que não é banco e não entra na trava) | Rosangela |
| 18/11/2026 | ambos | Gastos pessoais pagos pela empresa (Renner, farmácia, paróquia, pet etc.) | Só PIX para o CPF da sócia vai para a 531. O resto fica em despesa (527; alimentação 521) | Rosangela |
| 18/11/2026 | ambos | Isabella Paula de Souza, Camila Hadassa Muller, Giovana de Paula e PF sem nota que não é funcionária | 362 (alerta trabalhista/INSS) | Rosangela |
| 18/11/2026 | 34 | PIX pequenos semanais a empregados (VA) | 542 VA/VR | Rosangela |
| 18/11/2026 | ambos | Ótica Visoluk / Pedro Jefferson Luiz (49.192.337/0001-37) | Mútuo sem contrato: 152 na 34; 166 na 118 | Rosangela |
| 18/11/2026 | ambos | Fornecedores (506) | O pagamento só debita a 506 até o saldo credor de notas de entrada registradas; o que passar vai para a 470 | Rosangela |
| 18/11/2026 | 34 | Boleto Itaú Unibanco 300,00 (27/07) | 506 por ora | Rosangela |
| 18/11/2026 | ambos | Boletos SC Comércio | 506 (com a regra da 506) | Rosangela |
| 18/11/2026 | 34 | Shopping Popular Ltda (50.546.599/0001-31) | 320 Aluguel. Fica na R. Arquimedes 214, Loja 3, o mesmo prédio da matriz (Receita) | Rosangela + consulta CNPJ |
| 18/11/2026 | 34 | Fatura cartão Sicredi (DEB.CTA.FATURA) | 364 até chegarem as faturas | Rosangela |
| 18/11/2026 | ambos | Amil; médicos/similares sem nota (Sunaga, Foccus) | 366. A 306 só com nota fiscal | Rosangela |
| 18/11/2026 | 34 | Adiantamento salarial pago pelo banco | D 5 / C 8 (a folha lança D 25 / C 5) | Rosangela |
| 18/11/2026 | 34 | Cota-capital Sicredi (INTEGR.CAPITAL) | Ativo 1.2.3.03.001 COTAS-CAPITAL SICREDI, código sugerido 545. **Confirmar se já foi criada** | Rosangela |
| 18/11/2026 | 34 | Parcelamento do Simples (1124) e DAS (3333) | 479; multa 352 e juros 372 separados pelo relatório de pagamentos da Receita | Rosangela (padrão do razão + relatório) |
| 18/11/2026 | 34 | PIX do próprio CNPJ (Itaú → Sicredi) | Transferência entre contas (D 8 / C 9), lançada uma vez só. Nunca 504/362 | analista; base Lei 9.430/96 art. 42 §3º I |
| 18/11/2026 | ambos | Refazer o banco 01-09/2026 | Refazer tudo (não TXT de ajuste): apagar no Domínio só os lançamentos de banco do período e importar o TXT completo. Folha e fiscal ficam | Rosangela |

## Propostas ainda não validadas
- 118 → Shopping Popular pago pela filial (2.796,80 em 07; 296,42 em 08): parece aluguel da MATRIZ (o imóvel é o da matriz) → 118 D 544 / 34 D 320 C 544. Confirmar.
- 34 → 3 DARF pagos pelo Itaú que NÃO estão no relatório da Receita: 30/04 596,12 e 592,75; 29/05 602,41. E PIX à Receita de 94,71 (20/02) e 173,71 (20/04). Pedir as guias.
