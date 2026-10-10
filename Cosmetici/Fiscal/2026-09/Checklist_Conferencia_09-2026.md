# Checklist da conferência — COSMETICI 09/2026 (revisão sistemática)

Revisão de 10/10/2026. Os arquivos e relatórios da pasta `09_2026` do Drive foram cruzados uns com os outros e com os XML, nota a nota e item a item.

**Legenda:**
- ✅ confere
- ⚠️ precisa de decisão ou correção (não alterei valores)
- 🔧 erro meu, já corrigido
- ⏳ não deu para verificar (motivo indicado)

---

## A. Mapa da pasta e o que foi cruzado com o quê

| Arquivo da pasta | Cruzado com | Resultado |
|---|---|---|
| `Doc's/33039048000162 (1).zip` (XML de saída) e `xmls_*.zip`, `DownloadDFe_77/78.zip` (entradas, eventos, CT-e) | Todos os relatórios abaixo | 142 NF-e, 115 eventos, 6 inutilizações e 12 CT-e lidos. Saídas: 91 autorizadas, 3 canceladas (NF 8940, 8952 e uma entrada). |
| `Relatorios/Faturamento Cosmetici.pdf` (ERP) | XML de saída | ✅ 91 notas, R$ 180.815,24, ICMS 16.317,95 |
| `Relatorios/Saidas Cosmetici.pdf` (**Registro de Saídas do ERP**, novo nesta revisão) | XML, nota a nota: UF, CFOP, valor contábil, base, ICMS, ST e IPI | ✅ 59 de 61 notas iguais. Os totais batem: base 163.293,99, ICMS 16.317,95, ST 865,16, base IPI 148.532,74 e IPI 4.403,24. ⚠️ NF 8966 e 8967: o ERP registra UF **PR** e o XML tem endereço em **SP** (CFOP 6102). ⚠️ O registro não lista as 30 notas de retorno 5902/6902 (R$ 13.253,13), mas o "Total Geral" de 180.815,24 as inclui. |
| `Relatorios/Relatorio_Detalhamento_Produtos.xlsx` (SIEG) | XML de entrada e de saída | ✅ 48 entradas e 91 saídas. As notas que faltavam no SIEG são inutilizadas. |
| `Relatorios/Relatorio_CTe.xlsx` (SIEG) | CT-e em XML e extrato | ✅ 5 CT-e com XML. ⏳ 12 CT-e de frete de venda sem XML. ⚠️ TEX Courier (ver E.3). |
| `Relatorios/RelatorioNFS_ABRASF_..._2026-09.xlsx` (21 NFS-e) | Regras de retenção e extrato | Ver F |
| `Doc's/Recebidas/` (PDF das NFS-e: Andrade, Oficina, Extralab, Genesis, Tipografia…) | Relatório ABRASF | ✅ Correspondem a notas do relatório |
| `Extrato/Relatorio Conferencia 09.26.pdf` (extrato Itaú pelo ERP) e `.ofx` | Entradas, CT-e e NFS-e | Ver G |
| `SPED/`, `EFD_Reinf/`, `Guias/` | — | ⏳ Pastas vazias: o SPED de setembro ainda não foi gerado. O cruzamento XML × SPED roda quando ele existir. |

---

## B. Saídas — matriz completa NCM × CFOP × CST × alíquota (91 notas, 25 combinações)

| NCM | CFOP | ICMS (CST / %) | IPI (CST / %) | PIS no XML | Valor | Notas | Situação |
|---|---|---|---|---|---|---|---|
| 2847.00.00 oxidante | 5101 | 00 / 19,5 | 51 / 0 | 02 / 2,2 | 4.680,21 | 8968, 8970, 9011, 9022 | ✅ ICMS. ⚠️ NCM fora da lista monofásica, levado a 2,2%/10,3% (diferença PIS 84,87 / COFINS 399,72 se fosse 0,65%/3% — decisão já registrada). ⏳ Confirmar o IPI 0% na TIPI. |
| 2847.00.00 | 5124 | 51 diferido | 55 suspenso | 02 / 2,2 | 16.702,25 | 8945, 8977, 8992, 9001, 9023 | ✅ diferimento e suspensão. ⚠️ CST de PIS no XML (ver B.2) |
| 2847.00.00 | 6101 | 00 / 12 | 51 / 0 | 02 | 1.941,00 | 8998 (RJ), 9015 (RS) | ✅ alíquota de 12%. ⏳ ST interestadual por protocolo |
| 2847.00.00 | 6124 | 00 / 7 | 55 | 02 | 10.268,40 | 9004, 9025 (MS) | ✅ |
| 3305.10.00 | 5124 | **00 / 19,5** | **sem grupo** | 02 | 556,05 | 8939 Cândido | ⚠️ tributada enquanto as outras 5124 têm diferimento (ICMS 108,44); sem grupo de IPI; sem insumo do cliente |
| 3305.10.00 | 6124 | 00 / 7 | **sem grupo** | 02 | 4.049,52 | 8973 (BA) | ✅ alíquota. ⚠️ sem grupo de IPI |
| 3305.20.00 | 5102 | 00 / 19,5 | 50 / 14,3 | 02 | 6.901,45 | 8982 GULA | ⚠️ grupo GULA (C.1) |
| 3305.90.00 | 5102 | 00 / 19,5 | 50 / 14,3 | 02 | 24.738,37 | 11 notas GULA | ⚠️ grupo GULA (C.1) |
| 3305.90.00 | 5124 | 51 diferido | 55 | 02 | 20.244,90 | 7 notas | ✅ |
| 3305.90.00 | 5401 | 10 / 12 (diferimento parcial de 38,46%) | 50 / 14,3 | 02 | 4.050,02 | 8955 GULA | ✅ ST recalculada: MVA 63,75%, alíquota 23%, ST 865,16 confere item a item |
| 3305.90.00 | 6102 | 00 / 12 | 50 / 14,3 | 02 | 370,33 | 8967 GULA (SP) | ⚠️ C.1 |
| 3305.90.00 | 6102 | 00 / 12 | **51 / 0** | 02 | 667,68 | 8966 GULA (SP) | ⚠️ **o mesmo Neutralizante saiu com 14,3% na NF 8980**. IPI a menor ≈ R$ 95,48. A base do FCP no XML também está errada (3.338,40). |
| 3305.90.00 | 6124 | 00 / 12 | 55 | 02 | 36.139,52 | 12 notas SC/RS/RJ/SP | ✅ |
| 3305.90.00 | 6124 | 00 / 7 | 55 | 02 | 27.097,01 | 7 notas PA/MA/GO/CE/BA/MS | ✅ (8979 Barbara: ver C.3) |
| **3307.10.00** (preparações para barbear) | 5102 | 00 / 19,5 | **sem grupo** | 02 | 6.150,90 | 8980 GULA (óleos de chia, girassol e cártamo de 30 ml) | ⚠️ A classificação parece errada: óleo capilar ou corporal não é preparação para barbear. Revisar o NCM e o IPI no cadastro. |
| 3923.30.90 frasco | 5124 / 6124 | 41 | — | 49 | 3.004,50 | 8989, 8999, 9000, 9020, 9021 | ⚠️ **duplicidade com o retorno** (C.2) |
| 3923.30.90 | 5902 / 6902 | 41 | — | 49 | 3.004,50 | 8993, 9002, 9005, 9024, 9026 | ✅ |
| 4819.10.00 cartucho, 4821.90.00 rótulo, 7612.10.00 bisnaga, 3305.10.00 | 5902 / 6902 | 41 | — | 49 | 10.248,63 | 25 notas | ✅ retorno simbólico |

Outros pontos das saídas:
- **B.1** ✅ A alíquota interestadual é de 7% para N/NE/CO e de 12% para S/SE em todas as notas. ICMS e IPI recalculados (base × alíquota) batem em todos os itens. A numeração está completa.
- **B.2** ⚠️ **PIS/COFINS no XML × apuração.** As 35 notas de industrialização informam CST 02 (monofásico) a 2,2%/10,3%: R$ 115.057,65, com PIS de R$ 2.531,30 e COFINS de R$ 11.850,96 destacados nos XML. A apuração e os DARFs de julho e agosto usam 0,65%/3%. No meu entendimento, a alíquota concentrada na encomenda é do encomendante (Lei 11.051/2004, art. 10), e então a apuração está certa e o erro é o cadastro fiscal do ERP (deveria ser CST 01). **Confirmar.** Se o entendimento fosse o contrário, o PIS/COFINS de setembro subiria cerca de R$ 9.800 (8,85% sobre R$ 110.717,87).
- **B.3** ⏳ **Alíquotas de cosmético a confirmar na legislação.** As vendas no PR usam 19,5%, a ST da NF 8955 usa 23% e o DIFAL para SP usa 18%. Não consigo confirmar daqui a alíquota interna de cosméticos de cada UF.

## C. Achados das saídas por cliente/operação

| # | Achado | Notas | Valor | Status |
|---|---|---|---|---|
| C.1 | **GULA (IE 9084324601)**: depois da NF 8955 (contribuinte, CFOP 5401, com ST) passou a sair como **consumidor final** (indIEDest 9 / indFinal 1). Não houve ST, o ICMS foi cheio, o CFOP 5102 (revenda) foi usado em produção própria e as NF 8966 e 8967 têm endereço em SP (o ERP registra PR). Os CT-e da TEX Courier pagos pela Cosmetici mostram entregas para PE, SC, RS, SP, DF e MG, o que indica uma operação de venda/entrega a consumidores da GULA. | 16 notas (8966–9019) | R$ 35.221,15 em produtos | ⚠️ ALTA — confirmar a operação com o cliente |
| C.2 | **MIX**: frascos do cliente emitidos em 5124/6124 e devolvidos de novo em 5902/6902 | 8989, 8999, 9000, 9020, 9021 | R$ 3.004,50. Na base: PIS 19,53, COFINS 90,13, IRPJ ≈ 60,09, CSLL ≈ 32,45 | ⚠️ ALTA |
| C.3 | Industrialização sem insumo do cliente (sem remessa citada, sem retorno e sem remessa recebida) | 8939 Cândido, 8979 Barbara (GO) | 556,05 + 4.098,00 | ⚠️ Se for venda: monofásico e IPI |
| C.4 | A NF 9017 cita a industrialização na 9015 (que é do Fabiano), quando a correta é a 9016 | 9017 | — | ⚠️ CC-e |
| C.5 | Produto sem grupo de IPI | 8939, 8973, 8980 | — | ⚠️ cadastro |

## D. Entradas — matriz NCM × CFOP × natureza × crédito (48 notas, 81 itens)

| NCM | Fornecedor (CFOP) | Natureza | Crédito ICMS | Crédito IPI | Situação |
|---|---|---|---|---|---|
| 7612.10.00 bisnaga | Bispharma (6101) | insumo/embalagem | 2.987,66 | 1.618,32 | ✅ |
| 3402.42.00 | Chemyunion NF 19303 (6101) | insumo | 1.016,64 | 275,34 | ✅ As NF 391 e 392 são antecipação/financeiras (391 + 392 = 19303) e o extrato confirma o pagamento de 8.472,04 = NF 391 |
| 2847.00.00 peróxido | Alloxy (5101, CST 51) | insumo | 671,22 | — | ✅ O extrato confirma 2 × 2.796,75 = 5.593,50 |
| 3302.90.19 fragrância | Scentec (6101) | insumo | 557,29 | 150,93 | ✅ |
| 8309.90.00 tampa | Altec (6101) | insumo | 300,79 | — | ✅ |
| 2207.10.10 álcool | Distribuidora Industrial (5101, CST 51) | insumo | 224,41 | — | ✅ |
| 3824.99.89 | Provital (6102) | insumo | 160,71 | 261,15 | ✅ |
| 2909.44.29 | MCassab (6102, 4% importado) | insumo | 154,95 | — | ✅ |
| 3919.10.90 rótulo | Lunaflexo (CSOSN 101, Simples) | insumo | 98,95 (vCredICMSSN) | — | ✅ LC 123/06 art. 23 |
| 2922.11.00 / 2832.10.10 | REATEC NF 695 e MERCKPAR NF 42 (CSOSN 101 **sem %**) | insumo | 0 | — | ⚠️ pedir correção ao fornecedor |
| 4821.10.00, 3923.21/29, 1515.90.90, 3923.90.90 | Yahweh, Caetano, Farmanilquima, Sul Tape (CSOSN 102/103) | insumo | 0 | — | ✅ Simples sem crédito |
| 3822.19.90 reagentes | NewProv (5101) | uso (laboratório) | 0 (438,49 destacado) | — | ⚠️ confirmar |
| 8443.99.23 cartucho de impressora | HS Inklaser (6102, SP) | uso | 0 | 0 | ⚠️ DIFAL de R$ 104,87 |
| 0901/0903/1701/4823 | Supermercado Boza | uso (copa) | 0 | — | ✅ |
| 5603, 6401–6403, 3926.20 | ILS (EPI), Dispoli (luvas), Ellolimp (limpeza) | uso | 0 | — | ✅ |
| 3814.00.90 | Savatec (solvente do inkjet) | uso | 0 | — | ✅ |
| 8533.40.99 | Thermosul (resistências, CSOSN 102) | uso/manutenção | 0 | — | ✅ |
| 9603.30.00 pincel | Agatha (6949, CSOSN 201) | outras | 0 | — | ✅ |
| 2832, 2835, 2922 PA (R$ 1,00) | Carbon Científica (5949) | amostras | 0 | — | ✅ |
| 4821, 4911, 3923, 3923.50, 8413, 8424 | Linares (5923/5924/5949), Bepump e Outlet (6924), Onixsul, BB, Mix (5901/6901) | remessa ou insumo do cliente | 0 | — | ✅ Remessas sem retorno no mês = estoque de terceiros (12 notas) |

Totais: ICMS de NF-e R$ 6.073,67 + Simples R$ 98,95 · IPI R$ 2.305,74 ✅. Coerência menor, sem efeito: na Sul Tape, o plástico bolha foi classificado como insumo e o filme stretch como uso. Os dois são CSOSN 103, sem crédito.

## E. CT-e

| # | Item | Situação |
|---|---|---|
| E.1 | CT-e 5597996 (Expresso São Miguel, R$ 36,18): frete do pincel da Agatha | 🔧 Erro meu, corrigido. O crédito agora segue a NF-e transportada. **ICMS 9.996,19.** |
| E.2 | 4 CT-e da Trans Tomaz (fretes de insumo: Altec, Bispharma, Scentec, Chemyunion) | ✅ R$ 149,14 |
| E.3 | **TEX Courier**: 17 CT-e no SIEG (R$ 818,95, ICMS 85,80) com a Cosmetici como tomadora. O extrato mostra pagamento de **R$ 54,83 em 30/09 = CT-e 36425929** e de R$ 88,99 em 15/09, como "frete sobre vendas". | ⚠️ A Cosmetici paga esses fretes, e o crédito de até R$ 85,80 depende de qual operação a nota cobre (ligado a C.1) |
| E.4 | 12 CT-e de venda sem XML (Braspress, Expresso São Miguel, Rodonaves) | ⏳ Crédito potencial de R$ 294,06. Pedir os XML. |

## F. NFS-e tomadas (21 notas do relatório ABRASF)

| # | Item | Situação |
|---|---|---|
| F.1 | Genesis, NFS-e 18 (medicina ocupacional, R$ 728,14) | ⚠️ Só o IRRF de R$ 10,92 foi retido. **PIS/COFINS/CSLL de R$ 33,86 não retidos** (Lei 10.833/03 art. 30) |
| F.2 | Plus Santé, NFS-e 9227 (R$ 342,30) | ⚠️ Confirmar se é serviço profissional (CSRF de R$ 15,92) |
| F.3 | Extralab (calibração) | ✅ CSRF de R$ 85,35 retida |
| F.4 | Hotéis, telecom, software, Flash, Dental Uni e prestadores do Simples | ✅ Sem retenção |
| F.5 | ISS da dedetização (Insetcontrol/MS) | ⏳ Lei de Fazenda Rio Grande |
| F.6 | EFD-Reinf (R-4020) para as retenções | ⏳ Pasta vazia |

## G. Extrato bancário (`Relatorio Conferencia 09.26.pdf`) × documentos

| Pagamento | Documento | Situação |
|---|---|---|
| Quimiformula 832,20 × 2, Dinaco 2.414,00, Embacaps 2.043,96, Quantiq 3.785,45 | O próprio extrato diz **"PAGAR BOLETO DA REMAZZO"** | ⚠️ São compras de **outra empresa (Remazzo)** pagas pela Cosmetici: R$ 9.907,81. Não há NF-e para a Cosmetici, e não pode haver crédito. Contabilizar como conta corrente com a Remazzo (contabilidade). |
| Embacaps 2.883,24 × 2 (16 e 23/09), Multiquim 5.189,10 e 5.187,45 | Sem histórico no relatório | ⚠️ Confirmar se também são da Remazzo. A Multiquim é fornecedora da Cosmetici (SPED de agosto); a Embacaps não tem nota da Cosmetici em jul–set. |
| Alloxy 2 × 2.796,75 | NF 38175 | ✅ |
| Chemyunion 8.472,04 | NF 391 (antecipação) | ✅ |
| Yahweh 722,06 e 1.763,20 | NF 786, 795 e 814 (parceladas) | ✅ Fornecedora com notas no mês; os valores são parcelas |
| Braspress 1.492,54 | "Frete NF 8794" (venda de agosto) | ✅ Competência de agosto |
| Expresso São Miguel 1.291,26 e Trans Tomaz 488,88 | CT-e do mês | ⏳ Não fecham com os CT-e de setembro; provavelmente faturas de vários CT-e, inclusive de agosto |
| TEX Courier 88,99 e 54,83 | CT-e TEX | ⚠️ E.3 |
| Ecoplus (lavanderia, 672,00), Copel Telecom (559,92), Oxxygenio Sítio (520,00) | **Sem NFS-e/NF no relatório nem na pasta** | ⚠️ Pedir os documentos. Copel Telecom = NF de comunicação (mod. 62), sem crédito de ICMS para indústria. |
| Dental Uni 110,06 | NFS-e de 107,56 | ✅ Diferença de 2,50 (encargo) |
| Tecnoponto 74,90 | NFS-e 173228 | ✅ |

## H. Impostos de setembro (com a correção de E.1)

| Imposto | Valor | Depende de |
|---|---|---|
| PIS (8109) | 1.495,34 | C.2 (−19,53), C.3, B.2 |
| COFINS (2172) | 6.953,10 | C.2 (−90,13), C.3, B.2 |
| IPI (5123) | 2.097,50 | C.3, NF 8966 (+95,48 se o IPI correto for 14,3%), NCM 3307.10 |
| ICMS (GR-PR 1015) | **9.996,19** | C.1, B.3, E.3, E.4 |
| ICMS-ST (GR-PR 100099) | 865,16 | C.1 |
| DIFAL SP (GNRE, NF 8966/8967) | 62,28 | C.1 — não entra na GR-PR |
| IRPJ / CSLL 3º tri | 13.991,33 / 10.795,32 | C.2 (−60,09 / −32,45) |

## I. O que passou a ser automático (abas Checklist e Divergências)

Rodam sozinhos todo mês:
- todos os cruzamentos de B, C e E.1;
- F.1;
- o novo **XML × Registro de Saídas do ERP**, nota a nota (o PDF `Saidas*.pdf` na pasta do mês é lido sozinho);
- **mesmo produto com NCM/IPI diferentes**;
- **PIS/COFINS informado no XML × apuração**.

Continuam manuais: o extrato (o PDF do ERP não traz CNPJ nem número de nota), as alíquotas internas e protocolos de ST por UF, e o ISS de outro município.
