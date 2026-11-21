# Auditoria fiscal e da folha (Óticas 34/118)

Scripts usados na auditoria de 01-09/2026 (21/11/2026). Todos recebem a pasta de trabalho `S` com esta estrutura:

- `S/dados/razao34_long.csv`, `S/dados/razao118_long.csv`: razão longo (`rotina_mes.py razao-xls` / `razao-pdf`).
- `S/dados/folha_full.csv`: `folha_csv.py` do Extrato Mensal (inclua a competência anterior ao período).
- `S/fiscal/{34|118}_FAT_MM.xlsx` e `{34|118}_ENT_MM.xlsx`: relatórios FAT e NF Entrada do mês (pastas MM_AAAA do Drive).
- `S/saida/`: saída do `rotina_mes.py periodo` (Conferencia_Mtz_Fl_*.xlsx e TXT).

Ordem:
1. `python -I fiscal_ler.py S/fiscal` → `fiscal.json` (emissor, Domínio saídas/entradas, consulta SEFAZ, faturamento). Ajuste o laço de meses no fim do arquivo.
2. `python -I aud_saidas.py S` → emissor × Domínio × 408; notas rejeitadas sem reemissão; escrituradas sem autorização.
3. `python -I aud_entradas.py S` → SEFAZ × Domínio × 506 × 55.
4. `python -I aud_folha.py S` → por conta (5, 187, 188, 192, 191, 541, 532): folha × pagos nos TXT × saldo. Saldos de 31/12/2025 no topo do arquivo: para outro período, troque pelos saldos de abertura.
5. `python -I aud_func.py S` → por empregado: devido (adiantamento + líquido anterior) × pago.
6. `python -I chk_txt.py S/saida` → todo lote |6000|C|/|6000|D| balanceado.

Decisões que valem na leitura dos achados (decisoes.md): notas da MSO emitidas no lugar da matriz ficam como saída;
remessas/retornos em D 59 / C 60 são mantidas (uma anula a outra); NF 832 (Hoya) é real.
