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
~~O PDF do Itaú mostra R$ 17.000,00 em investimentos automáticos~~. **Corrigido:** os R$ 17.000 são o limite da conta. A aplicação automática do Itaú só começa em 14/10/2026 (saldo de 882,33 em 31/10). Saldos de todos os meses estão em `BASE_2026.md`.

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

## 6. Alertas depois da varredura completa (detalhes em `BASE_2026.md`)

Resolvido pelos documentos (não é mais pergunta): retiradas de 06 (WhatsApp: CDB → PagBank CPF da sócia), saldos do CDB (prints de 02, 03, 06, 09 e 10), aluguel de 10 (pago em 30/09 com desconto), o "R$ 17 mil" do Itaú (é limite), pagamentos a fornecedor com NF (cruzados por CNPJ: David Rojas = Modas Carol), padrão da Sul América (o mês M quita as NFS-e de M−1).

**Riscos para a contadora decidir (não são dúvidas de lançamento):**
1. **Omissão de receita.** De 07 a 10: R$ 96,5 mil recebidos × R$ 12,4 mil declarados. De 01 a 06: R$ 155 mil × R$ 36 mil. Lei 9.430/96, art. 42, mais a DIMP das maquininhas enviada à SEFAZ-PR.
2. **Compras sem nota:** R$ 40,9 mil de 07 a 10 (78% das compras). Mercadoria sem documento fiscal no estoque é infração de ICMS (RICMS-PR) e confirma a venda sem nota.
3. **Lucros de 9.867,19 informados na EFD-Reinf de 07** com PL negativo. Sugestão: reclassificar para a 551 e retificar o R-4010.
4. **DAS 09/2026 (56,73) em aberto**, confirmado no relatório de pagamentos do e-CAC (o pagamento de 15/10 foi estornado). Venceu em 20/10. Gerar DAS com multa e juros. O e-CAC também mostra que falta a provisão do DAS 04/2026 (124,01) e que os 45,44 de multa e juros do DAS 08/2025 foram para a 479.
5. **ICMS antecipado zerado de 08 a 10** com compras de SP e GO (CFOP 2102). Em 05 foi recolhido. Conferir o enquadramento no RICMS-PR antes de deixar de recolher.
6. Ajustes de 01 a 06 (período já lançado): DARF na 350 em vez da 191 (6 × 178,31) · ICMS antecipado na 350 em vez da 512 · resgate do CDB na 11 em vez da 48 · rendimento não contabilizado de 3.029,32 · 10.000 de retirada na 188 · Sul América paga direto na 366 com a NFS-e também escriturada (despesa em dobro) · resultado de 2025 aparentemente não encerrado.

## 7. Documentos que faltam na pasta

- NFS-e da Sul América de 07/2026 (2 notas, pagas em 13/08: 187,22 e 1.171,09)
- Michael Fashion NF-e 336 (1.500,00, vencimento 08/11): o XML está na pasta, mas **não foi escriturada** no Domínio (o relatório de entradas de 10 só tem a Modas Carol)
- Print do saldo do CDB em 31/07 e 31/08 (sem ele, o rendimento de 07 a 09 entra em 30/09)

## 8. Únicas perguntas que dependem da cliente

| # | O que vi | Pergunta |
|---|---|---|
| 1 | **Arlete Aparecida Barbosa Coelho** (CPF 419.813.679-34): de 07 a 10 **depositou** R$ 5.034,50 na empresa e recebeu R$ 892,10. De 01 a 06 recebeu R$ 10.033,94 (lançados na 362) | Ela é vendedora ou revendedora (recebe roupa, vende e repassa)? Se for, as entradas são venda (504) e as saídas são comissão. Se trabalha na loja, há risco de vínculo de emprego |
| 2 | Pagamentos sem identificação (R$ 4,5 mil): Rubesnei Rodrigues de Mello 1.040, "Pagamento e Serviços de" 912,19 (7×), Pedro Henrique Sena Pinho 850, Laudemira Maria Lucas 760, Maree 416,28, Elisangela Grochevski 239,99, Mooz 149,79, Fábio Júnio 100 | Mercadoria, serviço ou pessoal? |
