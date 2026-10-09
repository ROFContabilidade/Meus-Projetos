# Fiscal — conferência automática das notas

Lê os XML das notas **item a item** e diz, para cada transação, qual é a finalidade, o CFOP de entrada,
o acumulador do Domínio, o crédito de ICMS/IPI e o DIFAL; depois compara com o que foi escriturado
(SPED Fiscal e relatórios do Domínio) e lista as pendências.

- `scripts/nfe_xml.py` — leitura do XML da NF-e (itens, tributos, eventos de cancelamento).
- `scripts/sped_efd.py` — leitura do SPED Fiscal (C100/C170/C190, D100, 0400, E111/E113).
- `scripts/dominio_relatorios.py` — leitura dos relatórios "Acompanhamento de Entradas/Saídas" do Domínio.
- `scripts/conferencia.py` — regras + cruzamentos; `scripts/planilha.py` — planilha de saída.
- `empresas/<cod>-<nome>/regras.json` — acumuladores e regras de finalidade da empresa (cresce a cada mês).

Passo a passo: `.claude/skills/rof-fiscal-conferencia-notas/SKILL.md`.
