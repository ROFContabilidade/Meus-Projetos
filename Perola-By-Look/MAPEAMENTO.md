# Pérola By Look: mapeamento da empresa

Levantamento feito em 23/11/2026 a partir da pasta `G:\Meu Drive\Trabalho ROF\Contabilidade\Arquivos RENATA Dominio\49 - Perola By Look`, lida pelo Google Drive, e da consulta do CNPJ na Receita.
Escopo de trabalho: lançamentos de **07/2026 em diante**. O Domínio já tem os bancos lançados até 06/2026.

## 1. Cadastro

| Campo | Dado |
|---|---|
| Razão social | PEROLA C L KUSIAK LTDA |
| Nome fantasia | PEROLA BY LOOK |
| CNPJ | 30.582.416/0001-26 |
| Código Domínio | 49 |
| IE (PR) | 91033515-42 |
| Abertura | 29/05/2018, matriz única, ME, capital social R$ 10.000,00 |
| Endereço | Av. República Argentina, 2891, loja 02, Portão, Curitiba/PR |
| Sócia-administradora | Pérola Cristina Ludovico Kusiak (CPF 028.077.919-48), única sócia |
| Regime | **Simples Nacional** desde 29/05/2018, sem exclusão (Receita, 15/11/2026). Foi MEI até 31/08/2023. Apuração por competência. |
| Anexo | **Anexo I (comércio)**: revenda de mercadorias sem ST. RBT12 de 07/2026 = R$ 86.785,06, 1ª faixa (DAS ≈ 2,64%) |
| CNAE principal | 47.72-5-00 cosméticos e perfumaria |
| CNAEs secundários | 47.81-4-00 vestuário (é a atividade real: as NFC-e são de roupas), 47.82-2-01 calçados, 47.55-5-03 cama, mesa e banho, 47.83-1-01/02 joias e relógios, 47.89-0-01 bijuterias, 47.59-8-01 tapeçaria |
| Funcionários | **Nenhum**. A folha tem só o pró-labore da sócia |
| Contabilidade anterior | RBA Contabilidade / Paes e Bastos Contabilidade (Renata Bastos Amado, CRC PR075217/O-2). Os honorários são pagos à Paes e Bastos |

**Perfil de custo (comércio varejista de roupas):** mercadoria para revenda vai para estoque (55), e a baixa vai para o CMV (469/470). Aluguel da loja, energia, telefone, sistema e plano de saúde são despesas administrativas. O pró-labore está classificado hoje como custo (275 "Mão de obra direta"). No comércio, o correto seria despesa com pessoal: **ponto para a contadora decidir**.

## 2. Estrutura das pastas

```
49 - Perola By Look/
├── Contabil.xls                      (relatório antigo, 2025)
├── 2023/  2024/
├── 2025/  01_2025 … 12_2025, Razão.xls, Demonstrações Contábeis/ (DEFIS 2025 + recibo,
│          Balancete 2025 "alterar", Balancete 1º tri, Relatórios de conf)
└── 2026/
    ├── Automoção Contabil/   ← BASE DO MAPEAMENTO (gerada pelo Domínio em 23/10 e 23/11/2026)
    │     Balancete.pdf (01–09/2026) · Razão.xls (01–09/2026) · Plano de Contas.xls
    │     Extrato Folha Mensal.pdf (01–11/2026) · Pagamento de Encargos.pdf · Resumo impostos.pdf · Entradas.xls
    ├── 01_2026 … 06_2026     (06 já tem os TXT PAGAR/RECEBER de Itaú e PagBank gerados)
    ├── 07_2026  Extratos/ (Itaú PDF+MD, PagBank PDF+MD, OFX, XLS) · Guias/ (DAS, Extrato SN)
    │            Relatorios/ (FAT, NFC-e gerencial) · Doc's/ (XML NFC-e, notasXML) · EFD_REINF/
    ├── 08_2026  Extrato/ (Itaú, PagBank, OFX + MD) · Guias/ · Relatorio/ (FAT, NF_Entrada) · Doc's/ (DFe, DANFE)
    ├── 09_2026  Extrato/ (+ Comprovantes JPEG, Aplicação.png) · Guias/ · Relatorio/ (FAT, NF_Entrada, Contas.xls) · Doc's/ (NFS-e recebidas)
    └── 10_2026  Extrato/ (+ Comprovantes, aplicação.png) · Guias/ · Relatorio/ (FAT, NF_Entrada) · Doc's/
```

Os meses 07 a 10/2026 têm tudo o que é preciso para trabalhar: extrato dos 2 bancos já convertido em `_extrato.md`, DAS, extrato do PGDAS, faturamento (NFC-e) e notas de entrada. **Não há pasta 11/2026 ainda.**

## 3. Contas bancárias e saldos para começar 07/2026

| Conta Domínio | Banco | Saldo no razão em 30/06/2026 | Saldo inicial do extrato de 07/2026 | Confere |
|---|---|---|---|---|
| 8 | PagBank (PagSeguro) ag. 0001, cc 21930485-4 | 1.673,02 D | 1.673,02 | ✅ |
| 9 | Itaú Empresas ag. 4119, cc 0099191-9 | 151,75 D | 151,75 | ✅ |
| 48 | Aplicação CDB PagBank | 22.666,55 D (sem movimento em 2026) | a conferir | ⚠️ |
| 11 | "Poupança Caixa" (usada para o CDB PagBank) | **19.188,33 C** | n/a | ❌ |
| 5 | Caixa geral | 1.000,00 D | n/a | ⚠️ |

Conferência de 07/2026 pelo `_extrato.md`: Itaú 151,75 → 2.092,83 (créditos 19.533,74, débitos 17.592,66, fecha). PagBank 1.673,02 → 1.244,93 (créditos 9.996,21, débitos 10.424,30, fecha).
O PDF do Itaú (emitido em 01/09) mostra **R$ 17.000,00 em "investimentos automáticos"**. Não existe conta no plano para aplicação do Itaú.

## 4. Plano de contas usado (contas com movimento em 2026)

| Grupo | Conta: uso |
|---|---|
| Disponível | 5 Caixa · 8 PagBank · 9 Itaú · 11 Poupança CEF (usada para o CDB) · 48 CDB PagBank |
| Clientes | 504 Clientes diversos (recebe as vendas de cartão e PIX) · 564 Vendas canceladas |
| Estoque | 55 Mercadorias para revenda |
| Sócia | 551 Pérola Cristina (conta corrente da sócia) · 576 Distribuição de lucros |
| Passivo | 506 Fornecedor modelo · 479 Simples a recolher · 512 ICMS antecipado a recolher · 188 Pró-labore a pagar · 191 INSS a recolher · 510 Honorários contábeis · 547 Adiantamento de clientes |
| Custos | 275 Pró-labore · 469/470 CMV · 516 ICMS antecipação parcial |
| Despesas | 320 Aluguéis · 354 Energia · 356 Telefone/internet · 358/359 Administrativas · 350 Taxas diversas · 361 Assistência contábil · 362 Serviços de terceiros · 366 Plano médico · 493 Despesas diversas · 521 Alimentação · 558 Sistemas · 574 Marketing |
| Receitas | 408 Venda de mercadorias · 480 (−) Simples Nacional · 432 Juros de aplicações |

## 5. Padrões de lançamento (razão 01–06/2026, 3.211 partidas)

**Entradas**
- PagBank: "Vendas – Disponível DÉBITO VISA/MASTER/ELO" (≈ 110 por mês), D 8 / C 504. Rendimento diário em conta, D 8 / C 432.
- Itaú: "RECEBIMENTO REDE MAST/VISA/ELO/AMEX" (Rede), "RECEBIMENTOS SENFFNET" e PIX de clientes, D 9 / C 504.
- Receita: vem da integração fiscal (NFC-e), D 504 / C 408 "VENDAS DE MERCADORIAS NESTA DATA – CLIENTE BALCÃO".

**Saídas fixas (todo mês, quase todas pelo PagBank)**

| Favorecido | Conta | Valor típico |
|---|---|---|
| Imobiliária Martins (aluguel da loja) | 320 | 6.694,72 a 6.858,60 |
| Sul América Paraná Clínicas (plano de saúde) | 366 (ou baixa da 506 quando há NFS-e) | 177,79 + 1.113,52 a 1.489,81 |
| Paes e Bastos Contabilidade | 361/510 (às vezes caiu na 362 por engano) | 314 a 328 |
| Telefônica (Vivo) | 356 | 59,99 + 227,05 |
| Copel | 354 | 160 a 260 |
| Excellent Sistemas | 558 | 157,27 |
| DAS Simples Nacional | 479 | guia do mês anterior |
| DARF 178,31 (INSS do pró-labore) | hoje vai para a 350 ❌ (deveria ser a 191) | 178,31 |
| SEFAZ-PR (ICMS antecipado) | hoje vai para a 350 ❌ (deveria ser a 512) | variável |

**Saídas variáveis (Itaú, por PIX): compras de mercadoria.** São confecções e atacadistas: Matex Tecidos, Confecções Polares, Norte Vest, Martinez Confecções, Amanda Modas, Louver Fashion, Quinzy, Nova Fashion, Maju, A9 Variedades. Também PF ligadas ao comércio do Brás e do Bom Retiro: Morales Gutierrez, Rojas Rivera, Vila Lazo, Pacheco Aguayo, Flores Laura, Chinuri Condori, Mendez Huallpa, Wan Bing Yan, Lin Bochun. Mais Rick Costa Turismo (≈ 7 PIX por mês, provavelmente a excursão de compras).
Hoje essas compras estão espalhadas entre **362, 493, 470 e 506**. Só uma parte tem nota de entrada: em 07/2026 entrou 1 NF (Norte Vest, R$ 926,28) contra cerca de R$ 12 mil pagos a confecções.

**Folha:** pró-labore mensal de R$ 1.621,00, INSS de 11% (R$ 178,31), líquido de R$ 1.442,69. Lançamento: D 275 / C 188 e D 188 / C 191. A sócia recebe por PIX, para a 188 ou a 551.

## 6. Alertas: precisam de decisão antes de lançar 07/2026

| # | O que vi | Valores | Por que importa | Sugestão |
|---|---|---|---|---|
| 1 | **Recebimentos de cartão e PIX muito acima da receita declarada no PGDAS** | 01–06/2026: R$ 36.171 declarados × R$ 155.426 recebidos (3,3 a 8,4 vezes). 07/2026: R$ 4.254,69 (31 NFC-e) × ≈ R$ 29.400 recebidos | Lei 9.430/96, art. 42: crédito sem origem é presunção de omissão de receita. A Receita e a SEFAZ cruzam com a DIMP das maquininhas (Rede, PagBank, Senff). Por isso a 504 tem saldo credor de 252.711 | Falar com a cliente: todas as vendas precisam de NFC-e. Avaliar com a contadora se retifica o PGDAS. Até lá, lançar as entradas na 504 como hoje e registrar a pendência |
| 2 | Compras de mercadoria sem nota, lançadas como serviço (362) ou despesa (493) | 362 = 142.095 e 493 = 58.340 no acumulado | Distorce o CMV e o estoque. Se o pagamento a PF for serviço, cabe INSS de 20% | Para 07/2026 em diante, pagamento a confecção ou atacadista vai para a 55 (estoque), mesmo sem nota, com alerta. Pedir as notas aos fornecedores |
| 3 | Arlete Aparecida Barbosa Coelho recebe com frequência | 10.033,94 em 2026 | Pode ser vínculo de emprego informal (CLT art. 3º), com risco trabalhista e de INSS | Perguntar à cliente quem é e qual a função |
| 4 | O DARF do INSS do pró-labore vai para a 350, não para a 191 | 191 acumula 3.107,61 C. O relatório "Pagamento de Encargos" mostra 01 a 11/2026 em aberto | A despesa conta duas vezes e o passivo fica falso | De 07/2026 em diante: D 191 / C banco. Reclassificar 01–06 (6 × 178,31) |
| 5 | O ICMS antecipado (SEFAZ-PR) vai para a 350, não para a 512 | 512 = 554,05 C | O mesmo problema do item 4 | D 512 / C banco |
| 6 | Resgate do CDB PagBank lançado na 11 (Poupança CEF) | 11 = 19.188,33 C, 48 = 22.666,55 D parada | A conta de aplicação fica com saldo credor, o que não pode existir | Reclassificar 19.188,33 da 11 para a 48 e conferir o saldo da 48 com o extrato da aplicação |
| 7 | Aplicação automática do Itaú (R$ 17.000) sem conta no plano | n/a | O saldo do banco fica diferente do patrimônio real | Criar a conta "Aplicação automática Itaú" e pedir o extrato da aplicação em XLS ou OFX (existe `Aplicação.png` em 09 e 10) |
| 8 | Distribuição de lucros de 9.867,19 (06/2026) com prejuízo acumulado | PL negativo (−209 mil) | Sem lucro apurado, a retirada não é lucro isento (LC 123, art. 14). Vira adiantamento ou mútuo da sócia | Reclassificar para 551 (adiantamento à sócia) |
| 9 | Resultado de 2025 aparentemente não encerrado | O balancete de 2026 traz saldo anterior nas contas de resultado (ex.: 320 = 76.984) | O resultado de 2026 sai inflado | Conferir no Domínio se o encerramento de 2025 foi feito |
| 10 | Saldos parados | 547 Adiantamento de clientes 312.388,89 C · 510 Honorários 1.298 D (pagou sem provisionar) · 5 Caixa 1.000 D | Balanço distorcido | Analisar a origem com a contadora |
| 11 | Plano de saúde pago pela empresa | 366 = 22.681 no ano | Se for da sócia, pode ser remuneração indireta | Confirmar quem são os beneficiários |
| 12 | Pró-labore como custo (275) numa empresa de comércio | 14.589 no ano | Classificação: no comércio é despesa | Decisão da contadora |

## 7. Por onde começar 07/2026

1. Fontes: `07_2026/Extratos/Itau_07.26_extrato.md` e `Pagbank 07.26_extrato.md` (os dois fecham) mais OFX, `Guias/DAS_07.26` e `Extrato S.N_07.26` (RPA 4.254,69, DAS 112,33, vencimento 20/08), `Relatorios/FAT. 07.26` e NFC-e, NF de entrada (Norte Vest 926,28 e serviço 15.01 de 51,20 da Senff).
2. O DAS pago em 07 é o de 06/2026 (R$ 237,26, PagBank). O DARF de 178,31 é o INSS de 06.
3. Gerar um TXT por mês (tudo no mesmo arquivo, em ordem de data, no leiaute `|0000|30582416000126|` e `|6000|X|` / `|6100|`, igual aos TXT de 06/2026). Usar os lotes `|6000|D|` ou `|6000|C|` quando houver mais de uma partida.
4. Antes de gerar, preciso das respostas aos itens 1, 2, 3, 6, 7 e 8 acima.
