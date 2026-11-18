---
name: rof-contabilidade-otica-visouup
description: "ÓTICA VISOUUP: ADRIANA R. DE PAULA LTDA, FILIAL CNPJ 24.026.777/0002-74, código 118 no Domínio, com contabilidade separada da matriz Ótica Visoluz (24.026.777/0001-93, empresa 34). Simples Nacional Anexo I (comércio de óptica), com exclusão agendada para 31/12/2026. Sem folha. Conciliação do Itaú ag 3702 cc 98896-9 (conta 8), conta corrente com a matriz (152), Visoluk (166), retiradas da sócia Adriana e TXT único do mês para o Domínio. Usar quando mencionarem VisouUP, Visou UP, Ótica VisouUP, filial da Visoluz, o CNPJ 0002-74, a empresa 118 ou a pasta 118, sempre junto com o rof-analista."
---

# ÓTICA VISOUUP: filial 118

**Siga o `rof-analista`.** Esta skill guarda só o que é desta filial. Dados: `references/empresa.json`. Regras de classificação: `references/regras.json` (executável) e `references/classificacao.md`. Decisões: `references/decisoes.md` (busque pelo favorecido ou valor). Panorama e riscos: `references/panorama.md`.

## Perfil
- **Filial com contabilidade própria** (118), mas é o mesmo CNPJ raiz da matriz Visoluz (34): o Simples é um só. O DAS é pago pela matriz; a filial não lança DAS no banco.
- Comércio varejista de óptica (Anexo I). Lentes e armações são compra para revenda (55/506). Os serviços da SC Comércio (acumulador 142, CFOP 1.124) são industrialização (325).
- **Sem folha.** Todo PIX para empregado CLT da matriz, Metrocard ou CEF MATRIZ é despesa da matriz paga pela filial: vai para a **152**, nunca para a 362 nem para a 192 da filial (proposta 18/11/2026).
- Exclusão do Simples em 31/12/2026: a partir de 01/2027, rever regime, plano e esta skill.

## Rotina do mês
1. Pasta `118 - Otica VisouUP/<ANO>/<MM_AAAA>`: `Extrato/*_extrato.md` (Itaú), `Relatorio(s)/FAT.*.xlsx` e `NF_Entrada_*.xlsx`.
2. `python scripts/extrato_dominio.py ler <extrato.md> -o ext.csv` (tem de dar "confere: sim"; saldo inicial = razão da conta 8).
3. `python scripts/classificar.py ext.csv references/regras.json cls.csv`. Linha "SEM REGRA" ou PERGUNTA vai para a tabela de perguntas.
4. **Espelho 152 (filial) × 544 (matriz, empresa 34):** saldo devedor da 152 = saldo credor da 544. **Conferir a 152 com o extrato Sicredi da matriz** (pasta `34 - Otica Visoluz/<ANO>/<MM_AAAA>/Extrato`): cada PIX enviado à Visoluz tem de aparecer lá como "RECEBIMENTO PIX 24026777000274".
5. Notas de entrada × pagamentos: boleto SC/Arquem/Singular baixa a 506. Compra com NF sem pagamento na filial = perguntar quem pagou (matriz?).
6. `python scripts/gerar_txt.py cls.csv references/regras.json VISOUUP_118_MM_AAAA.txt [--split=ID=506:161.34,372:3.80]` gera **um TXT** por mês. O líquido da conta 8 tem de bater com o extrato.
7. Planilha de sócios do cérebro com `--socio "ADRIANA RODRIGUES DE PAULA|032.149.559-42|531,539"`.
8. Comparar faturado (FAT) × recebido (504) e registrar no parecer.

## Alertas permanentes
- 504 credor e 506 sem baixa vêm de 01–06/2026: não lançar ajuste sem a contadora.
- 527 Despesas diversas **não se usa** (em 01–06 recebeu pagamento de fornecedor).
- 362: pessoa física sem vínculo (Camila Hadassa, Isabella, Giovana, Regiane…). Risco de vínculo e de INSS.
- Retiradas da sócia com prejuízo acumulado: ficam em 531 (adiantamento) até haver lucro apurado.
