---
name: "rof-fiscal-cosmetici"
description: "COSMETICI INDUSTRIA E COMERCIO DE COSMETICOS (CNPJ 33.039.048/0001-62, empresa 25 no Domínio, Lucro Presumido, indústria de cosméticos - PR): automação fiscal do mês. Lê os XML de NF-e/CT-e (ou os relatórios SIEG) e o SPED, apura PIS/COFINS (0,65%/3% + monofásico 2,2%/10,3%), IRPJ/CSLL trimestral, ICMS, ICMS-ST e IPI, confere os XML e entrega a planilha Apuracao_Fiscal_Cosmetici_MM-AAAA.xlsx e o TXT de provisões para o Domínio. Também tem a rotina de organizar a pasta fiscal do mês. Usar quando falarem em fiscal/apuração/impostos/guias/DARF/SPED/XML/faturamento da Cosmetici."
---

# ROF Contabilidade — Fiscal COSMETICI

> **Regra de ouro:** nada é corrigido nas notas de entrada nem de saída. Lê-se o XML e escritura-se exatamente o que está nele
> (CFOP, CST, bases, impostos, retenções). Nota que deveria ter retenção e não tem → escritura sem retenção. As divergências da
> revisão automática são só informativas e nunca alteram valores.

Empresa 25 no Domínio · CNPJ 33.039.048/0001-62 · IE 90809060-88 · Fazenda Rio Grande/PR · Lucro Presumido desde 2026
(até 2025 era Simples Nacional — balancete 12/2025 ainda tem as contas do Simples).

## Entregas do mês

1. `Cosmetici/Fiscal/<AAAA-MM>/Apuracao_Fiscal_Cosmetici_MM-AAAA.xlsx` — abas: Resumo (guias + cálculo de cada imposto + confronto com o SPED), Saídas por acumulador, Notas de saída, Itens de saída, Entradas e créditos, CT-e, Divergências, Observações, Canceladas e inutilizadas.
2. `Cosmetici/Fiscal/<AAAA-MM>/Lancamentos_Fiscais_Cosmetici_MM-AAAA.txt` — provisões no leiaute do Domínio (`|0000|`, `|6000|X||||`, `|6100|`), **só quando as contas estiverem preenchidas** em `contas_dominio` do config (hoje estão todas `null` — pedir as contas à contadora; nunca inventar conta).

Commit/push e enviar a planilha ao usuário (SendUserFile). Não versionar XML, SPED nem relatórios do cliente (ficam no Drive).

## Passo a passo

1. **Arquivos do mês** no Google Drive (buscar por `33039048000162`, `Cosmetici`, `MM.AA`): ZIP de XML de saída (`33039048000162.zip`), ZIP de entradas (`xmls_*.zip`, `DownloadDFe_*.zip`), `Recebidas.zip` (NFS-e), relatórios SIEG (`Relatorio_Detalhamento_Produtos.xlsx`, `Relatorio_CTe.xlsx`, `RelatorioNFS_ABRASF_*.xlsx`) e, se já existir, o SPED do mês. Baixar com `download_file_content` (o resultado grande vai para arquivo JSON: `jq -r .content arquivo | base64 -d > destino`). Colocar tudo numa pasta de trabalho no scratchpad.
2. **Aprender os fornecedores** com o SPED do mês anterior (define CFOP de entrada e se credita ICMS/IPI por fornecedor e NCM):
   `python scripts/fiscal_cosmetici.py aprender --sped <SpedEFD do mês anterior>`
3. **Faturamento do trimestre:** os meses anteriores do trimestre têm de estar em `faturamento_mensal` do config. Se faltar, calcular pelo SPED transmitido: `python scripts/fiscal_cosmetici.py faturamento-sped --sped <SPED> --gravar` (também mostra o PIS/COFINS para conferir com o DARF).
4. **Apurar:** `python scripts/fiscal_cosmetici.py apurar --mes AAAA-MM --pasta <pasta do mês>` (ou `--xml ... --sieg-produtos ... --sieg-cte ... --sped ...`). Com o SPED do mesmo mês, a aba Resumo mostra o confronto item a item.
5. **Revisar** as abas Divergências (ALTA primeiro) e Observações; apresentar ao usuário e perguntar só o que não dá para decidir. Fornecedor novo = crédito pela regra padrão do CFOP → confirmar insumo × uso e consumo.
6. Depois de conferido, `--gravar-faturamento` grava o faturamento do mês no config (para o IRPJ/CSLL do trimestre). Commit/push.

`python scripts/testes.py` roda os testes sintéticos (não usam arquivo de cliente).

## Regras de cálculo (validadas com 07 e 08/2026 — bateram centavo a centavo com DARF/SPED)

- **Acumuladores de saída** (Domínio): 200 vendas s/ ST PR (5101/5102), 201 vendas fora do PR (6101/6102), 202 vendas c/ ST PR (5401/5403/5405), 254/255 industrialização para outra empresa (5124/6124), 207 bonificação 5910, 208 bonificação 6910, 212 outras saídas 5949, 204/205 vendas para a COSMETICON (pelo cliente: 5101/5102 → 204, 5401 → 205), 217/277 retorno de industrialização (6902/5902). CFOP sem acumulador = divergência ALTA → acrescentar no config.
- **Valor contábil** do item = vProd − vDesc + vFrete + vSeg + vOutro + IPI + ICMS-ST (+ FCP-ST).
- **Faturamento** (receita bruta p/ IRPJ/CSLL) = vendas + industrialização − devoluções de venda (entradas 1201/1202/1410/1411/2201/2202/2410/2411) − ICMS-ST − IPI. 08/2026 = 445.743,94; 07/2026 = 391.529,15.
- **PIS/COFINS** (fórmula da planilha `FAT. 08.26_Cosmetici`, aba "Empresa 25"):
  - base 0,65% / 3% = industrialização (vlr contábil 5124+6124) − ICMS dessas notas;
  - base 2,2% / 10,3% = vendas (200+201+202) − ICMS das vendas − IPI total − ST total;
  - cada parcela arredondada antes de somar (como no DARF). Códigos 8109 / 2172, vencimento dia 25.
  - Devoluções **não** são deduzidas da base (como foi pago). A planilha mostra quanto seria deduzindo — decisão da contadora (`pis_cofins.deduzir_devolucoes`).
  - Toda venda vai a 2,2%/10,3%, inclusive NCM fora da lista monofásica (ex.: 2847.00.00 oxidante/água oxigenada) — a planilha aponta em Observações quanto seria a 0,65%/3%.
- **IRPJ/CSLL** trimestral: receita do trimestre × 8% (IRPJ) / 12% (CSLL); IRPJ 15% + adicional 10% sobre o que passar de R$ 60.000 no trimestre; CSLL 9%. Códigos 2089 / 2372, vencimento último dia útil do mês seguinte ao trimestre. Conferido com o 2º tri/2026 (receita 998.642,37 → IRPJ 13.972,85, CSLL 10.785,34).
- **ICMS próprio** (GR-PR 1015, dia 12): débitos das saídas − créditos das entradas (fornecedor aprendido do SPED; novo = regra do CFOP) − créditos de CT-e em que a COSMETICI é tomadora ± ajustes do mês (`icms.ajustes`). Industrialização 5124 sai com CST 51 (diferimento, sem ICMS).
- **ICMS-ST** (GR-PR 100099, dia 10): ST destacada nas saídas para o PR − ST de devoluções.
- **IPI** (DARF 5123, dia 25): débitos das saídas − créditos das entradas de insumo.

## Regras de escrituração das entradas (validadas nos SPED 07/2026 e 08/2026 transmitidos)

- **Insumo** (MP, embalagem, rótulo, essência, ativos cosméticos): 1101/2101 com crédito do ICMS destacado (e do IPI). Simples: só o vCredICMSSN (CSOSN 101/201/900).
- **Uso e consumo** (escritório, limpeza, copa/mercado, EPI, laboratório, manutenção): **1556/2556 com base e ICMS zerados**; mercadoria com ST já retida: **1407/2407 (CST 60)**. Indústria não recolhe ST nas compras.
- **DIFAL** de uso e consumo/ativo de outra UF: base dupla `(vc − ICMS origem) / (1 − 19,5%) × 19,5% − ICMS origem` (Simples: ICMS de origem pela alíquota nominal de 12%); **E111 PR000081 a débito** na apuração (paga na GR-PR 1015) + E113 por nota. Ex.: Agatha NF 2230, 5.800,00 → 540,37 (07/2026).
- **ICMS antecipado de importado** (entrada interestadual a 4%): **8% da base**; E111 PR000080 (débito) + PR020212 (crédito de mesmo valor, saldo zero) com E113 por nota - sem guia própria (07 e 08: GR-PR 1015 = saldo da apuração). Ex.: Emuna NF 2446, 1.475,00 → 118,00.
- **Canceladas** (NF-e de terceiros e CT-e): escriturar com situação 02, bases zeradas e a chave (ex.: CT-e 2022868 em 08/2026).
- **CT-e** com a COSMETICI tomadora (inclusive "outra tomadora", TEX Courier dos envios da GULA): crédito do ICMS (2352/2353); intraestadual CST 40 sem crédito.
- Histórico por fornecedor + NCM (`aprender` com os SPED de 07 **e** 08): REATEC (reagente "PS") = 1556; HS Inklaser (cartucho do codificador inkjet) = 2101 com crédito; Agatha (pincel/tigela/espátula) = 2556 + DIFAL; Sul Tape (bolha/filme/fita) = 1556; Labaz (reagentes PA) = 1101 com crédito do Simples.
- Acumuladores das entradas: config `acumuladores_entrada` por CFOP, levantados no Acompanhamento de Entradas/Saídas e nos Demonstrativos de ICMS de 01 a 08/2026 (pasta `25 - Cosmetici/2026/MM_2026/Relatorios`, colunas CFOP e AC.): 1101/1102→100, 2101/2102/2122→101, 1556→104, 2556→105, 1407→107, 1910→110, 1411→113, 2202→133, 2411→134, 2901→144, 1911→147, 2911→148, 1901→149, 1949/2949→155, 2924→164, 1924→165, 2910→189, 1653→192, 2902→198, 2124→199, 2922→238, 1352/1353/1932→1000, 2352/2353→1001; 1923 sem histórico. Referência: `Cosmetici/Fiscal/2026-09/Acumuladores_Dominio_Cosmetici_2026.xlsx` e `acumuladores_servicos` por CNPJ do prestador (8xx). Conta contábil: CONFIRMADA pelo relatório do Domínio "Lançamentos gerados pela Escrita" (`Lançamentos.xls`, pasta do mês) cruzado nota a nota (número + valor) com o Acompanhamento de Entradas: config `acumuladores_entrada[cfop].conta` (débito/crédito/lançamentos/outras) e `contas_servicos_por_acumulador`; fornecedores.json `contas_dominio[tipo][conta]` (regra: embalagem/rótulo → 600 INSUMOS, químico → 56 MATÉRIA-PRIMA; uso e consumo 513, escritório 359, limpeza 360, EPI 656, manutenção 321). O Resumo Contábil sintético só confirma os totais dos pares.
- Pasta do mês anterior (`MM_AAAA/Relatorios`): NF_Entrada (SIEG + Acompanhamento de Entradas com AC), NF Serviços Tomados, Demonst. ICMS/IPI (.xls), Registro de Saídas; `Guias/`: GR-PR 1015, DARF 5123/8109/2172/1708, ISS retido Fazenda Rio Grande.

## Relação das notas de saída (comando `saidas`)

`python scripts/fiscal_cosmetici.py saidas --mes AAAA-MM --pasta <pasta do mês>` → `Cosmetici/Fiscal/<AAAA-MM>/Relacao_Saidas_Cosmetici_MM-AAAA.xlsx`: uma aba, uma linha por número (autorizadas, canceladas em vermelho, inutilizadas em cinza), ordem de data de saída + número, com tudo o que está destacado no XML (produtos, desconto, frete, outras, base/ICMS, base ST/ICMS-ST, FCP-ST, IPI, PIS, COFINS, DIFAL UF destino, total), acumulador do Domínio pelo CFOP, a sugestão de importação (como está no XML / cancelada situação 02 / inutilizada situação 05), a conferência XML x Faturamento x Registro do ERP (lida de `Cruzamento_Relatorios_ERP_x_XML_MM-AAAA.xlsx` na pasta de saída) e a análise informativa da revisão (revisao.revisar_saidas). Totais só das autorizadas.

## Relação das notas de entrada (comando `entradas`)

`python scripts/fiscal_cosmetici.py entradas --mes AAAA-MM --pasta <pasta do mês>` (ou `--xml`, `--sieg-cte`, `--nfse-xml`) → `Relacao_Entradas_Cosmetici_MM-AAAA.xlsx`, valores exatamente como no XML:
- **Todas as entradas**: NF-e, CT-e e NFS-e juntas, na ordem da emissão;
- **NF-e dentro do estado** e **NF-e fora do estado** (pela UF do fornecedor), com CFOP do XML, CFOP de entrada e acumulador sugeridos, canceladas em vermelho;
- **CT-e**: só aqueles em que a Cosmetici é tomadora, dentro e fora do estado; os que não têm XML na pasta vêm do relatório SIEG, em cinza (pedir o XML). CT-e com outro tomador não é entrada da Cosmetici e fica de fora;
- Em todas as abas: conta contábil do Domínio (lancamentos_contabeis), conferência com os relatórios SIEG/ABRASF e, nas NF-e, natureza, créditos de ICMS/IPI, DIFAL, antecipado e a análise de cada nota.
- **NFS-e tomadas**: retenções do XML (ISS retido, IRRF, vRetCSLL, INSS/vRetCP, vTotalRet), em amarelo as notas com qualquer retenção. Com `tpRetPisCofins` 3, o `vRetCSLL` é o total de PIS, COFINS e CSLL retidos (4,65%), como vem no XML.

## TXT de importação das notas no Domínio (comando `importacao`)

`python scripts/fiscal_cosmetici.py importacao --mes AAAA-MM --pasta <pasta do mês>` (ou `--xml`, `--sieg-cte`) → `Cosmetici/Fiscal/<AAAA-MM>/IMPORTACAO_DOMINIO_MMAAAA.TXT`. É o leiaute que o Domínio aceita para importar as notas na Escrita Fiscal: SPED EFD ICMS/IPI (versão 020), igual ao arquivo aceito da Kopp Indústria (mesma quantidade de campos em cada registro - conferido no teste), cp1252, CRLF, valores com vírgula.
- Bloco 0: cabeçalho (0000/0005/0100 do SPED 08/2026 da Cosmetici, config `sped_cabecalho`), 0150 com COD_PART = CNPJ/CPF e o endereço do XML, 0190, 0200 (código do item gerado: F + hash para entradas, K para saídas), 0400 = acumuladores usados.
- C100/C170/C190 de entradas e saídas: no C170, COD_NAT = acumulador do Domínio e COD_CTA = conta contábil (entradas). **REGRA DA USUÁRIA: tudo EXATAMENTE como no XML** - CST (origem+CST ou CSOSN), base, alíquota e valor de ICMS (o diferimento do PR - 19,5% com pDif, efetivo 12% - vem como o emitente informou: vBC, pICMS e o vICMS já diferido), ST, CST/enquadramento/base/alíquota/valor de IPI, CST/base/alíquota/valor de PIS e COFINS, e os totais do C100 do ICMSTot. Nada é zerado nem recalculado (uso e consumo, 1407, Simples: o crédito fica pela parametrização do acumulador no Domínio). Só o CFOP vira o de entrada. `auditar()` confere o TXT contra o XML campo a campo (09/2026: 141 documentos, 385 itens, 0 diferenças). C101 quando há DIFAL; canceladas COD_SIT 02 e inutilizadas 05 só com número/chave; vendas para a Cosmeticon nos acumuladores 204/205.
- IBS/CBS (reforma, 2026: IBS 0,1% / CBS 0,9%) estão nos XML, mas o leiaute 020 aceito pelo Domínio não tem campo para eles: ficam nas relações de entradas e saídas (colunas Base IBS/CBS, IBS, CBS).
- D100/D190 só para CT-e com XML em que a Cosmetici é tomadora (precisa do município de início e fim); sem XML fica fora e é listado.
- Bloco E só com E100 (a apuração, o DIFAL e o antecipado - E111 - são feitos no Domínio); NFS-e não entram (não são do SPED ICMS/IPI).
- 09/2026: saídas = XML (180.815,24 / ICMS 16.317,95 / ST 865,16 / IPI 4.403,24); entradas 127.478,55 com os valores do XML; fora: Linares 1923 (sem acumulador) e 29 CT-e sem XML.
- Não importar também o TXT contábil (`contabil`): a Escrita Fiscal já gera os lançamentos.

## Lançamentos contábeis das entradas (comando `contabil`)

`python scripts/fiscal_cosmetici.py contabil --mes AAAA-MM --pasta <pasta do mês> [--lancamentos-escrita Lançamentos.xls]` → `Lancamentos_Contabeis_Entradas_Cosmetici_MM-AAAA_RASCUNHO.txt` (leiaute da skill rof-contabilidade-cosmetici: `|0000|CNPJ|`, `|6000|X||||`, `|6100|DD/MM/AAAA|débito|crédito|valor com vírgula||histórico||||`, cp1252, CRLF) + planilha de conferência com aba Pendências.
- `--lancamentos-escrita` aprende do Domínio a conta de cada fornecedor (grava em fornecedores.json).
- NF-e: um lançamento por nota × CFOP de entrada, valor contábil do XML; conta do acumulador, trocada pela do fornecedor quando ele tem histórico (compras e uso e consumo). Fornecedor sem histórico fica em amarelo ("conferir"). Devolução da Cosmeticon credita 664.
- CT-e: só tomadora, D 312 / C 506; sem XML usa o relatório SIEG; cancelado não entra.
- NFS-e: conta do acumulador do prestador; ISS retido em lote `|6000|D||||` (D despesa total / C 506 líquido / C 183 ISS); IRRF em lote próprio D 506 / C 178.
- Sem conta comprovada (CFOP 1923, prestador novo, retenção de PIS/COFINS/CSLL) NÃO entra no TXT - vai para Pendências. Histórico igual ao do Domínio: `<TIPO> <nº> <NOME> <NOME> <CNPJ>`.
- ATENÇÃO: se as notas forem importadas na Escrita Fiscal, o Domínio gera esses lançamentos sozinho (origem "Entradas EF") - não importar o TXT também, senão duplica. O TXT serve para conferência ou para quando a contabilização não vem da Escrita.

## Cruzamento das entradas com os relatórios (comando `cruzar-entradas`)

`python scripts/fiscal_cosmetici.py cruzar-entradas --mes AAAA-MM --pasta <pasta do mês>` (ou `--xml`, `--sieg-produtos`, `--sieg-cte`, `--nfse`, `--nfse-xml`) → `Cruzamento_Entradas_Relatorios_x_XML_MM-AAAA.xlsx`. Só compara; nada é alterado.
- **NF-e** x Relatorio_Detalhamento_Produtos: por nota (valor, ICMS, IPI, ST, nº de itens) e **item a item** (aba "NF-e itens", 25 campos: CFOP, NCM, CEST, origem, CST ICMS, quantidade, valor, desconto, frete, outras, base/%/ICMS, base ST/ST, CST/base/%/IPI, CST/base/valor de PIS e COFINS). O SIEG não traz o nº do item: pareia pela ordem quando a descrição bate, senão pela descrição e valor. Diferenças só de formato do relatório não contam: NCM sem zero à esquerda, NCM 00000000 em branco, e o grupo PISOutr/COFINSOutr (CST 49-99) que o SIEG não exporta — aceito só quando o XML não tem valor de PIS/COFINS.
- **CT-e** x Relatorio_CTe: valor, base, %, ICMS, CST, CFOP, tomador, emissão, emitente/trajeto, NF-e vinculada, cancelados, sem XML.
- **NFS-e** (XML padrão nacional da pasta `Doc's/Recebidas`) x RelatorioNFS_ABRASF: valor, base ISS, ISS, ISS retido, IRRF, PIS, COFINS, total retido, líquido, código do serviço (4 primeiros dígitos), emissão, Simples, cancelada. Prestador do Simples sem retenção vem sem `vBC` no XML e o relatório repete o valor como base: marcado OK com observação.
- Downloads pequenos do Drive vêm embutidos na resposta (base64) e não viram arquivo: recuperar do transcript da sessão (`~/.claude/projects/<projeto>/<sessão>.jsonl` e `.../subagents/*.jsonl`, campo `"content"` com `title`) - assim o arquivo sai idêntico ao do Drive. Para muitos arquivos, baixar por um subagente e recuperar do transcript dele.

## Análise de crédito das entradas (comando `creditos`)

`python scripts/fiscal_cosmetici.py creditos --mes AAAA-MM --xml <zips/pastas> --sieg-produtos Relatorio_Detalhamento_Produtos.xlsx --relatorio-erp "Faturamento Cosmetici.pdf" [--cte-json dados/cte_relatorio_sieg.json]`
→ `Cosmetici/Fiscal/<AAAA-MM>/Creditos_Entradas_Cosmetici_MM-AAAA.xlsx` (Resumo, item a item, Simples Nacional, CT-e, conferência de saídas XML × ERP × SIEG, conferência de entradas XML × SIEG, base legal). A apuração usa a mesma classificação.

Natureza de cada item (ordem): `natureza_entradas` do config (decisão do escritório) → CFOP do fornecedor (5901/5924/5923… = insumo do cliente/remessa, sem crédito; 5949 = outras; devolução) → histórico do SPED anterior (fornecedor + NCM) → NCM (insumo/embalagem/rótulo, uso e consumo, ativo).
- **Regime normal:** crédito do ICMS destacado só em insumo/embalagem/devolução (inclusive CST 51 com valor destacado). Uso e consumo sem crédito (LC 87/96 art. 33, I). Ativo → CIAP 1/48. Item que o SPED anterior escriturou sem crédito continua sem crédito (alerta "revisar").
- **Simples Nacional:** crédito = `vCredICMSSN` da nota, só com CSOSN 101/201/900 e só em mercadoria para industrialização (LC 123/06 art. 23 §1º; Res. CGSN 140/2018 art. 59). CSOSN 102/103/300/400/500 = sem direito. % informado com valor zerado ou CSOSN 101 com 0% = pedir correção ao fornecedor (não creditar). Simples nunca gera crédito de IPI.
- **IPI:** só insumo de fornecedor que destacou IPI (RIPI art. 226, I).
- **DIFAL:** uso e consumo/ativo de outra UF → estimativa pela base dupla (19,5%).
- **PIS/COFINS:** Lucro Presumido cumulativo → sem crédito.
- **CT-e:** crédito do frete com a COSMETICI tomadora (XML), **seguindo a natureza da NF-e transportada** (chaves no CT-e): frete de compra de uso e consumo/outras = sem crédito (LC 87/96 art. 33, I); frete de retorno de insumo do cliente = confirmar quem paga. CT-e que só aparece no relatório SIEG fica como pendente até baixar o XML. CT-e da TEX Courier de envios da GULA com a COSMETICI no documento: não creditar sem confirmar.

## Conferência automática dos XML

ICMS e IPI recalculados (BC × alíquota), CST × valor, os cruzamentos da revisão automática (abaixo), CFOP × UF do destinatário, alíquota interestadual (4% importado; 7% N/NE/CO/ES; 12% S/SE), CFOP com ST sem ST destacada e CFOP sem ST com ST destacada (visto em 08/2026: oxidantes em 5102 com ST para GULA), monofásico × CST PIS, numeração das notas próprias (buraco sem cancelamento/inutilização), notas fora do mês, CC-e, manifestação de desconhecimento, fornecedor sem histórico e, com SPED: notas no SPED sem XML e vice-versa.

## Revisão automática (`scripts/revisao.py`) e aba Checklist

Cruzamentos que a contadora refazia à mão; rodam em todo `apurar`/`creditos` e vão para a aba Divergências. A aba **Checklist** da planilha mostra cada verificação com OK / VERIFICAR / NÃO EXECUTADO (faltou arquivo):
- **5124/6124 x 5902/6902:** insumo do cliente (CST 41, PIS 49) emitido com CFOP de industrialização e devolvido de novo no retorno (ALTA - infla a base do PIS/COFINS e do IRPJ/CSLL); 5124/6124 sem remessa citada, sem retorno e sem remessa recebida no mês (pode ser venda 5101: monofásico + IPI); retorno que cita a NF de industrialização errada (CC-e).
- **Contribuinte como consumidor final:** cliente com IE (ou que no mês já foi contribuinte) emitido com indIEDest 9/indFinal 1 - some a ST e muda a alíquota. Mesmo CNPJ com UF diferente no mês.
- **CFOP de revenda (5102/6102) com IPI destacado** (produção própria = 5101/5401); **5124 interna tributada** quando as demais têm diferimento (CST 51); produto **sem grupo de IPI**.
- **Mesmo produto (cProd) com NCM/IPI diferentes** nas vendas do mês (ex.: Neutralizante com IPI 0% numa nota e 14,3% noutra).
- **PIS/COFINS informado no XML x apuração:** o ERP emite as 5124/6124 com CST 02 (2,2%/10,3%); a apuração usa 0,65%/3% (Lei 11.051/04 art. 10 - concentrada é do encomendante).
- **XML x Registro de Saídas do ERP** (`Relatorios/Saidas Cosmetici.pdf`, lido sozinho na `--pasta` ou `--registro-saidas`): nota a nota UF, CFOP, valor contábil, base, ICMS, ST e IPI; o registro do Cosmos não lista os retornos 5902/6902, mas o total geral os inclui.
- **Remessas recebidas** (5901/5924/5923…) sem retorno no mês = estoque de terceiros (informativo).
- **NFS-e tomadas** (`--nfse RelatorioNFS_ABRASF_*.xlsx`, ou achado na `--pasta`): extrai da nota valor, base, ISS, ISS retido, IRRF, PIS, COFINS, outras retenções e líquido - **sem recalcular** retenção (aba "NFS-e tomadas" da planilha de créditos).
- Fora do automático (fazer à mão e marcar no checklist): extrato (`Extrato/Relatorio Conferencia MM.AA.pdf`, sem CNPJ/NF) x entradas, CT-e e NFS-e - atenção aos pagamentos "PAGAR BOLETO DA REMAZZO" (compra de outra empresa paga pela Cosmetici, sem NF-e e sem crédito); ISS de prestador de outro município; alíquotas internas/ST de cosméticos por UF.
- Pasta do mês no Drive: `25_*/.../09_2026/` com `Doc's` (ZIPs de XML, `Recebidas` = PDFs das NFS-e), `Relatorios` (Faturamento e Saidas do ERP, SIEG produtos/CT-e/NFS-e), `Extrato`, `SPED`, `EFD_Reinf`, `Guias`. Cruzar **todos** os relatórios - o checklist do mês fica em `Cosmetici/Fiscal/AAAA-MM/Checklist_Conferencia_MM-AAAA.md`.

## Rotina mensal da pasta (Windows)

`Cosmetici/Fiscal/rotina-mensal/` — `organizar_fiscal_cosmetici.ps1` + `.bat`. Acha `I:\Meu Drive\EMPRESAS ATIVAS\25_*\FISCAL(-CONTABIL)\AAAA\MM_AAAA`, cria as subpastas (01_XML_Saidas … 09_Apuracao), extrai os ZIP (ZIP fica) e separa os XML pelo conteúdo (emitente = COSMETICI → saída). Nunca apaga nem sobrescreve. A pasta organizada pode ir direto para `apurar --pasta`.

## Pendências / decisões em aberto

- Contas do Domínio para o TXT de provisões (PIS, COFINS, IPI, ICMS, ICMS-ST, IRPJ, CSLL) — sugestão para ST: D 482 / C 481 (balancete 12/2025), não confirmada.
- Deduzir devoluções da base do PIS/COFINS? NCM 2847 a 2,2%/10,3% ou 0,65%/3%?
- CT-e de 08/2026 não estavam nos arquivos lidos: crédito do SPED = 1.210,68 (única diferença do ICMS de 08/2026).
- 09/2026 (XML da pasta 09_2026/Doc's): 91 saídas batem com o relatório do ERP (R$ 180.815,24; ICMS 16.317,95) e com o SIEG; as NF 8938, 8948, 8951… que faltavam no SIEG são inutilizadas (procInutNFe). Créditos: ICMS NF-e normal 6.073,67 + Simples 98,95 (Lunaflexo, CSOSN 101) + CT-e com XML 149,14 (o CT-e 5597996 de R$ 36,18 é frete do pincel da Agatha - CFOP 6949/uso, sem crédito); IPI 2.305,74. ICMS a recolher 9.996,19.
  Decisões em aberto (checklist `2026-09/Checklist_Conferencia_09-2026.md`): pagamentos da Remazzo pela Cosmetici (R$ 9.907,81 + Embacaps/Multiquim a confirmar); NF 8966 neutralizante sem IPI; NCM 3307.10 nos óleos da NF 8980; CST PIS 02 nas industrializações; TEX Courier paga pela Cosmetici (CT-e 36425929 = R$ 54,83); GULA emitida como consumidor final desde a NF 8966 (sem ST, 16 notas, R$ 35.221,15 de produtos; 8966/8967 com endereço em SP); frascos da MIX em 5124/6124 e de novo em 5902/6902 (R$ 3.004,50 na base do PIS/COFINS/IRPJ/CSLL); 5124/6124 sem insumo do cliente (8939 Cândido, 8979 Barbara); 8939 tributada x diferimento; NFS-e 18 Genesis sem PIS/COFINS/CSLL retidos (R$ 33,86); XML de 12 CT-e de frete de venda (R$ 294,06); REATEC (NF 695) e MERCKPAR (NF 42) CSOSN 101 sem %; reagentes da NewProv como uso e consumo (R$ 438,49); DIFAL R$ 104,87 (HS Inklaser).
