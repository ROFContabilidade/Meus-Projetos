# Automação fiscal — COSMETICI (empresa 25)

CNPJ 33.039.048/0001-62 · Lucro Presumido · indústria de cosméticos · Fazenda Rio Grande/PR

## O que faz

| Etapa | Onde | Resultado |
|---|---|---|
| Organizar a pasta do mês | `rotina-mensal/` (Windows, dois cliques) | Subpastas 01_XML_Saidas … 09_Apuracao, ZIP extraído, XML separados por tipo |
| Apurar os impostos | `.claude/skills/rof-fiscal-cosmetici/scripts/fiscal_cosmetici.py apurar` | `AAAA-MM/Apuracao_Fiscal_Cosmetici_MM-AAAA.xlsx` com guias, cálculos e conferência |
| Conferir os XML | mesma planilha, aba **Divergências** | ICMS/IPI recalculados, CFOP × UF, ST, numeração, SPED × XML |
| Créditos das entradas | `fiscal_cosmetici.py creditos` | `AAAA-MM/Creditos_Entradas_Cosmetici_MM-AAAA.xlsx`: insumo × uso e consumo × remessa, Simples Nacional (vCredICMSSN), IPI, CT-e, DIFAL e conferência XML × ERP × SIEG |
| TXT para o Domínio | `AAAA-MM/Lancamentos_Fiscais_Cosmetici_MM-AAAA.txt` | Provisões dos impostos (só depois de preencher as contas em `config/cosmetici.json`) |

## Validação

| Mês | Item | Automação | Pago / SPED |
|---|---|---|---|
| 07/2026 | PIS | 2.975,63 | DARF 2.975,63 |
| 07/2026 | COFINS | 13.787,78 | DARF 13.787,78 |
| 08/2026 | Faturamento | 445.743,94 | planilha FAT 445.743,94 |
| 08/2026 | PIS | 5.562,12 | DARF 5.562,12 |
| 08/2026 | COFINS | 25.935,13 | DARF 25.935,13 |
| 08/2026 | IPI | 21.408,41 | DARF / SPED 21.408,41 |
| 08/2026 | ICMS-ST | 54.079,89 | SPED 54.079,89 |
| 08/2026 | ICMS débitos / créditos NF-e | 40.635,74 / 6.830,19 | SPED igual |
| 08/2026 | ICMS a recolher | 33.805,55 | SPED 32.594,87 (diferença = crédito de CT-e 1.210,68, CT-e não estavam nos arquivos) |
| 2º tri/2026 | IRPJ / CSLL | 13.972,85 / 10.785,34 | DARFs iguais |

## Rotina da pasta (computador do escritório)

1. Copie a pasta `rotina-mensal` para o computador (ex.: `C:\ROF\Cosmetici-Fiscal`).
2. Jogue os ZIP/XML/SPED/guias/relatórios do mês **soltos** na pasta `MM_AAAA` da Cosmetici no `I:`.
3. Dois cliques em **TESTAR_SIMULACAO.bat** (mostra o que vai fazer) e depois em **ORGANIZAR_MES_ANTERIOR.bat** — ou **ORGANIZAR_ESCOLHER_MES.bat** para outro mês.
4. Nada é apagado nem sobrescrito; o log fica em `rotina-mensal\logs`.

Requer o Google Drive para computador aberto (unidade `I:`).
