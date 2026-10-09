# Fiscal — conferência automática das notas

Lê os XML das notas **item a item** e diz, para cada transação, qual é a finalidade, o CFOP de entrada,
o acumulador do Domínio, o crédito de ICMS/IPI e o DIFAL; depois compara com o que foi escriturado
(SPED Fiscal e relatórios do Domínio) e lista as pendências. Com o mês ainda aberto (sem SPED), roda em
modo pré-importação: diz como lançar cada nota e compara com o histórico do Domínio.

- `scripts/nfe_xml.py` — leitura do XML da NF-e (itens, tributos, eventos de cancelamento).
- `scripts/sped_efd.py` — leitura do SPED Fiscal (C100/C170/C190, D100, 0400, E111/E113).
- `scripts/dominio_relatorios.py` — leitura dos relatórios "Acompanhamento de Entradas/Saídas" do Domínio.
- `scripts/dominio_pdf.py` — o mesmo relatório quando só existe em PDF (usado como histórico de lançamentos).
- `scripts/conferencia.py` — regras + cruzamentos; `scripts/planilha.py` — planilha de saída.
- `empresas/<cod>-<nome>/regras.json` — acumuladores e regras de finalidade da empresa (cresce a cada mês).

Passo a passo: `.claude/skills/rof-fiscal-conferencia-notas/SKILL.md`.
