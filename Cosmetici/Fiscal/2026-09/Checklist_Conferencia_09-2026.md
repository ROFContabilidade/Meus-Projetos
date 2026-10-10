# Checklist da conferência — COSMETICI 09/2026

Autorrevisão feita em 10/10/2026, com base em 142 XML de NF-e, 115 eventos, 6 inutilizações, 12 XML de CT-e, o relatório SIEG de produtos, o relatório de faturamento do ERP, o relatório SIEG de NFS-e (21 notas) e os SPED de jul/ago.

Legenda: ✅ OK · ⚠️ precisa de decisão da contadora · 🔧 erro meu, já corrigido · ⏳ pendente (falta arquivo ou consulta)

## 1. O que foi pedido x o que foi entregue

| Pedido | Situação |
|---|---|
| Levantar os XML de setembro | ✅ 91 saídas, 3 canceladas, 6 inutilizadas, 48 entradas, 5 CT-e tomados (XML) |
| Cruzar com os relatórios de saída | ✅ XML x ERP (Cosmos) x SIEG: as 91 saídas batem (R$ 180.815,24; ICMS 16.317,95). As 3 diferenças de numeração são canceladas ou inutilizadas. |
| Cruzar com os relatórios de entrada | ✅ XML x SIEG: as 48 entradas batem. ⏳ Faltam os XML de 12 CT-e que só aparecem no SIEG. |
| Notas que dão crédito, conforme a atividade | ✅ Analisado item a item (aba "Entradas - crédito item a item"). 🔧 Um CT-e foi corrigido (ver 4.1). |
| Crédito das notas de empresas do Simples | ✅ Lunaflexo, CSOSN 101: crédito de R$ 98,95. ⚠️ REATEC e MERCKPAR (ver 3.3). |
| Revisar cada CFOP e cada NCM conforme a atividade | ✅ Itens 2 e 3 abaixo. Encontrei pontos novos que **não estavam** na entrega anterior. |

## 2. Saídas — CFOP × NCM × destinatário (91 notas, 22 combinações CFOP/CST/NCM)

| # | Verificação | Resultado | Status |
|---|---|---|---|
| 2.1 | Numeração sequencial | Sem buracos. As lacunas são as NF 8940 e 8952 (canceladas) e 6 números inutilizados. | ✅ |
| 2.2 | ICMS e IPI recalculados (BC × alíquota) e CST × valor | Sem diferença | ✅ |
| 2.3 | Alíquota interestadual (4%/7%/12%) | Sem diferença | ✅ |
| 2.4 | **GULA (IE 9084324601) emitida como consumidor final** a partir da NF 8966 | Até a NF 8955 a GULA saía como contribuinte, com CFOP 5401, ST e diferimento parcial. A partir de 10/09 o cadastro passou a indIEDest=9 / indFinal=1. São 16 notas e R$ 35.221,15 em produtos: **sem ST**, com ICMS cheio de 19,5% e IPI na base. Se a GULA revende, a ST não foi retida. Para ter uma ordem de grandeza: na NF 8955 a ST foi de 31% do valor dos produtos. | ⚠️ ALTA |
| 2.5 | GULA, mesmo CNPJ (PR) com endereço em São Paulo | As NF 8966 e 8967 saíram com CFOP 6102, endereço em SP e DIFAL para SP de R$ 62,28 (40,06 + 22,22). Esse DIFAL é recolhido por GNRE para SP e **não entra na GR-PR**. | ⚠️ ALTA |
| 2.6 | CFOP de revenda (5102/6102) em produto fabricado pela Cosmetici, com IPI destacado | 13 notas da GULA. O produto próprio sai com 5101 (ou 5401 com ST). Na NF 8980 há ainda 3 óleos com NCM 3307.10 sem grupo de IPI. | ⚠️ MÉDIA |
| 2.7 | **Frascos da MIX** emitidos em 5124/6124 (CST 41, PIS 49) **e de novo** no retorno 5902/6902 | NF 8989, 8999, 9000, 9020 e 9021, somando R$ 3.004,50. Os mesmos frascos voltaram nas NF 8993, 9005, 9002, 9026 e 9024. Esse valor entra no acumulador de industrialização e infla as bases: PIS R$ 19,53, COFINS R$ 90,13, IRPJ cerca de R$ 60,09 e CSLL cerca de R$ 32,45. | ⚠️ ALTA |
| 2.8 | Industrialização (5124/6124) sem insumo do cliente | NF 8939 (Cândido, R$ 556,05) e NF 8979 (Barbara/GO, R$ 4.098,00) não citam remessa, não têm retorno e não há remessa recebida no mês. Se não houve insumo do cliente, a operação é venda: PIS/COFINS monofásico (diferença de cerca de R$ 39,61 e R$ 337,29) e IPI tributado. | ⚠️ MÉDIA |
| 2.9 | Diferimento nas 5124 internas | A NF 8939 (Cândido) foi tributada a 19,5% (ICMS R$ 108,44), enquanto os outros 35 itens 5124 saíram com CST 51 (diferimento). | ⚠️ MÉDIA |
| 2.10 | Retorno citando a NF errada | A NF 9017 (Luan Lorandi) diz "industrialização efetuada na NFE 9015", que é do Fabiano. A correta é a 9016. Corrigir por CC-e. | ⚠️ BAIXA |
| 2.11 | Produto sem grupo de IPI | NF 8939, 8973 e 8980 (3 itens). Conferir o cadastro no ERP. | ⚠️ BAIXA |
| 2.12 | IPI CST 55 (suspenso) nas 5124/6124 | Consistente com o RIPI art. 43, VI e VII (retorno ao encomendante para comércio ou nova industrialização). | ✅ |
| 2.13 | NCM × PIS/COFINS monofásico | NCM 3305/3307 com CST 02, conforme. O oxidante NCM 2847 (R$ 5.475,65) não está na lista monofásica e foi levado a 2,2%/10,3%, como foi pago em agosto. Se fosse a 0,65%/3%, a diferença seria PIS R$ 84,87 e COFINS R$ 399,72. | ⚠️ (decisão já registrada) |
| 2.14 | ST interestadual (vendas 6101/6102 para RJ, RS, SP) | Não verifiquei os protocolos/convênios de cosméticos de cada UF de destino. | ⏳ |

## 3. Entradas — CFOP × NCM × atividade (48 notas, 81 itens)

| # | Verificação | Resultado | Status |
|---|---|---|---|
| 3.1 | Insumo com crédito (regime normal) | Bispharma, Chemyunion, Scentec, Altec, MCassab (4% importado), Provital, Alloxy (CST 51 com destaque), Distribuidora Industrial (álcool) | ✅ ICMS R$ 6.073,67 · IPI R$ 2.305,74 |
| 3.2 | Simples Nacional com crédito | Lunaflexo, NF 3795, CSOSN 101: R$ 98,95 (LC 123/06 art. 23 §1º) | ✅ |
| 3.3 | Simples com CSOSN 101 sem % de crédito | REATEC NF 695 (R$ 3.738,00) e MERCKPAR NF 42 (R$ 1.180,00). Pedir correção ao fornecedor; não creditar como está. | ⚠️ |
| 3.4 | Simples sem direito a crédito (CSOSN 102/103/400/500) | Yahweh, Caetano, Farmanilquima, Sul Tape, Savatec, Dispoli, ILS, Thermosul | ✅ sem crédito |
| 3.5 | Uso e consumo sem crédito (LC 87/96 art. 33, I) | Ellolimp, Supermercado Boza, ILS (EPI), Dispoli (luvas), HS Inklaser (cartucho de impressora) | ✅ |
| 3.6 | Reagentes de laboratório da NewProv (NCM 3822) | Tratados como uso e consumo (controle de qualidade), com R$ 438,49 de ICMS não creditado | ⚠️ confirmar |
| 3.7 | DIFAL de uso e consumo vindo de outra UF | HS Inklaser (SP): R$ 104,87 estimado pela base dupla | ⚠️ confirmar recolhimento |
| 3.8 | Remessas para industrialização (5901/6901/5923/5924) | Sem crédito, conforme. Ficam 12 remessas sem retorno no mês (estoque de terceiros): Linares para os clientes Z.R., Vitta Hair, Onixsul, F.B. Ribeiro e BB; Bepump e Outlet para a SB Beauty; Onixsul NF 17187; BB NF 4551. A Linares usa 5923 (venda à ordem) onde o normal seria 5924. Isso não afeta a Cosmetici. | ✅ informativo |
| 3.9 | Chemyunion NF 391/392 ("antecipação de pagamento", 6949, NCM 00) | São faturas financeiras: 391 + 392 = 8.747,38, igual à NF 19303 (mercadoria). Sem crédito, sem duplicidade. | ✅ |
| 3.10 | Carbon Científica (5949, R$ 1,00) e Agatha (pincel, 6949, CSOSN 201) | Amostras ou outras saídas, sem crédito | ✅ |
| 3.11 | Fornecedores sem histórico no SPED | 11 fornecedores, classificados pelo NCM. A tabela está acima. Confirmar para gravar o histórico. | ⚠️ |
| 3.12 | Extrato × compras | Há pagamentos de "compra de matéria-prima" a Embacaps, Quimiformula, Dinaco, Quantiq e Multiquim sem NF-e em setembro. Também não há NF-e de Embacaps, Quimiformula, Dinaco e Quantiq nos SPED de julho e agosto, e o DF-e da SEFAZ de setembro também não traz nenhuma. Devem ser parcelas de compras mais antigas. Conferir no contas a pagar. | ⏳ |

## 4. CT-e

| # | Verificação | Resultado | Status |
|---|---|---|---|
| 4.1 | Crédito do frete × natureza da NF-e transportada | **Erro meu**: o CT-e 5597996 (Expresso São Miguel, R$ 36,18) é o frete do pincel da Agatha (6949/uso), que não dá crédito. Corrigi a regra no código para todos os meses. **ICMS a recolher passou de R$ 9.960,01 para R$ 9.996,19.** | 🔧 |
| 4.2 | Os outros 4 CT-e com XML (Trans Tomaz) | Frete de compra de insumo (Altec, Bispharma, Scentec, Chemyunion): R$ 149,14 | ✅ |
| 4.3 | 12 CT-e de frete de venda só no SIEG (Braspress, Expresso São Miguel, Rodonaves) | Crédito potencial de R$ 294,06, fora da apuração até chegar o XML. Quando o XML chegar, o código confere se o frete é de retorno de insumo do cliente. | ⏳ |
| 4.4 | 17 CT-e da TEX Courier (envios da GULA, R$ 85,80) | Sem crédito até confirmar quem é o tomador | ⚠️ |

## 5. Serviços tomados (NFS-e) — novo

| # | Verificação | Resultado | Status |
|---|---|---|---|
| 5.1 | Retenção de IRRF e PIS/COFINS/CSLL | Genesis Aliança, NFS-e 18 (medicina ocupacional, R$ 728,14): só o IRRF de R$ 10,92 foi descontado. PIS/COFINS/CSLL de 4,65% = **R$ 33,86 não retidos** (Lei 10.833/03 art. 30). | ⚠️ MÉDIA |
| 5.2 | Plus Santé, NFS-e 9227 (atendimento móvel, R$ 342,30) | Confirmar se é serviço profissional (CSRF de R$ 15,92) | ⚠️ BAIXA |
| 5.3 | Extralab, NFS-e 43 (calibração, R$ 1.835,50) | CSRF de R$ 85,35 retida, conforme | ✅ |
| 5.4 | Hotéis, telecom, software, Flash (benefícios), plano odontológico e prestadores do Simples | Sem retenção, conforme | ✅ |
| 5.5 | ISS de prestador de outro município (Insetcontrol/MS, dedetização) | Conferir a lei de Fazenda Rio Grande sobre a retenção pelo tomador | ⏳ |

## 6. Impostos do mês (após a correção do item 4.1)

| Imposto | Valor | Situação |
|---|---|---|
| PIS (8109) | 1.495,34 | ⚠️ cai R$ 19,53 se 2.7 for duplicidade |
| COFINS (2172) | 6.953,10 | ⚠️ cai R$ 90,13 se 2.7 for duplicidade |
| IPI (5123) | 2.097,50 | ⚠️ depende de 2.8 |
| ICMS próprio (GR-PR 1015) | **9.996,19** (antes 9.960,01) | ⚠️ depende de 2.4, 2.9 e 4.3 |
| ICMS-ST (GR-PR 100099) | 865,16 | ⚠️ depende de 2.4 |
| IRPJ 3º tri (2089) | 13.991,33 | ⚠️ depende de 2.7 |
| CSLL 3º tri (2372) | 10.795,32 | ⚠️ depende de 2.7 |

Nenhum valor foi alterado por conta dos achados ⚠️. A apuração continua fiel aos XML até a contadora decidir.

## 7. O que mudou no trabalho para não precisar refazer

Os cruzamentos 2.4 a 2.11, 3.8, 4.1 e 5.1 agora rodam sozinhos em todo mês. Eles aparecem nas abas **Checklist** e **Divergências** da planilha de apuração. A aba Checklist marca cada verificação como OK, VERIFICAR ou NÃO EXECUTADO (quando falta arquivo). Para as NFS-e, basta colocar o `RelatorioNFS_ABRASF_*.xlsx` na pasta do mês.

Ainda fora do automático, a fazer à mão: extrato × fornecedores, ISS de outro município e ST interestadual por UF.
