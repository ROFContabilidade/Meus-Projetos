---
name: "rof-fiscal-cosmetici"
description: "COSMETICI INDUSTRIA E COMERCIO DE COSMETICOS (CNPJ 33.039.048/0001-62, empresa 25 no Domínio, Lucro Presumido, indústria de cosméticos - PR): automação fiscal do mês. Lê os XML de NF-e/CT-e (ou os relatórios SIEG) e o SPED, apura PIS/COFINS (0,65%/3% + monofásico 2,2%/10,3%), IRPJ/CSLL trimestral, ICMS, ICMS-ST e IPI, confere os XML e entrega a planilha Apuracao_Fiscal_Cosmetici_MM-AAAA.xlsx e o TXT de provisões para o Domínio. Também tem a rotina de organizar a pasta fiscal do mês. Usar quando falarem em fiscal/apuração/impostos/guias/DARF/SPED/XML/faturamento da Cosmetici."
---

# ROF Contabilidade — Fiscal COSMETICI

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

- **Acumuladores de saída** (Domínio): 200 vendas s/ ST PR (5101/5102), 201 vendas fora do PR (6101/6102), 202 vendas c/ ST PR (5401/5403/5405), 254/255 industrialização para outra empresa (5124/6124), 208 bonificação (6910), 217/277 retorno de industrialização (6902/5902). CFOP sem acumulador = divergência ALTA → acrescentar no config.
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

## Conferência automática dos XML

ICMS e IPI recalculados (BC × alíquota), CST × valor, CFOP × UF do destinatário, alíquota interestadual (4% importado; 7% N/NE/CO/ES; 12% S/SE), CFOP com ST sem ST destacada e CFOP sem ST com ST destacada (visto em 08/2026: oxidantes em 5102 com ST para GULA), monofásico × CST PIS, numeração das notas próprias (buraco sem cancelamento/inutilização), notas fora do mês, CC-e, manifestação de desconhecimento, fornecedor sem histórico e, com SPED: notas no SPED sem XML e vice-versa.

## Rotina mensal da pasta (Windows)

`Cosmetici/Fiscal/rotina-mensal/` — `organizar_fiscal_cosmetici.ps1` + `.bat`. Acha `I:\Meu Drive\EMPRESAS ATIVAS\25_*\FISCAL(-CONTABIL)\AAAA\MM_AAAA`, cria as subpastas (01_XML_Saidas … 09_Apuracao), extrai os ZIP (ZIP fica) e separa os XML pelo conteúdo (emitente = COSMETICI → saída). Nunca apaga nem sobrescreve. A pasta organizada pode ir direto para `apurar --pasta`.

## Pendências / decisões em aberto

- Contas do Domínio para o TXT de provisões (PIS, COFINS, IPI, ICMS, ICMS-ST, IRPJ, CSLL) — sugestão para ST: D 482 / C 481 (balancete 12/2025), não confirmada.
- Deduzir devoluções da base do PIS/COFINS? NCM 2847 a 2,2%/10,3% ou 0,65%/3%?
- CT-e de 08/2026 não estavam nos arquivos lidos: crédito do SPED = 1.210,68 (única diferença do ICMS de 08/2026).
- 09/2026 (preliminar, só o relatório SIEG de produtos): faltam no relatório as NF 8948, 8951, 8956, 8965 e 8972 — conferir se são canceladas/inutilizadas ou se o relatório veio incompleto.
