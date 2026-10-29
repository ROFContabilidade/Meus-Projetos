---
name: rof-leitura-extratos
description: "Regra da ROF Contabilidade para LER extratos bancários e comprovantes: nunca abrir o PDF/OFX/CSV/XLSX original, sempre o arquivo <nome>_extrato.md gerado pelo Conversor de extratos ROF (conversor.py) ao lado do original. Usar sempre que for analisar, conciliar ou lançar um extrato, ou quando falarem em conversor de PDF, conversor de extratos, _extrato.md, Confere NÃO ou pasta Extrato do cliente."
---

# Leitura de extratos (Conversor de extratos ROF)

## Onde estão os arquivos
- No computador da Rosângela roda o **Conversor de extratos ROF** (programa `conversor.py`, instalado em
  `C:\Users\User\OneDrive\EXTRATOS\_ferramentas`). A cada 5 minutos ele converte sozinho os arquivos
  (PDF com texto ou escaneado, OFX, CSV, XLSX) de:
  - pastas **"Extrato"** dos clientes no Google Drive (G:) — `G:\Meu Drive\Trabalho ROF\Contabilidade\`
    **Arquivos RENATA Dominio**, **Arquivos ROF Dominio** e **Arquivos PROTECTION Dominio\25 - Cosmetici**
    (inclusive subpastas como "Comprovantes"), arquivos salvos a partir de 01/09/2026;
  - `C:\Users\User\OneDrive\EXTRATOS\01 - Entrada`.
- Ao lado de cada original fica um arquivo com o mesmo nome terminado em **`_extrato.md`**
  (ex.: `sicredi_09.pdf` → `sicredi_09_extrato.md`). O original nunca é alterado.

## Regra
- **NUNCA** leia o PDF, OFX, CSV ou XLSX original do extrato. Leia **sempre** o `_extrato.md`.
- `# Extrato - ...` = extrato bancário:
  - cabeçalho com Banco | Ag | Conta | Titular | Período;
  - linha `Saldo inicial | Créditos | Débitos | Saldo final | Confere: sim/NÃO`;
  - tabela `data|histórico|doc|valor|saldo`, uma linha por lançamento, débito com sinal negativo, valores como estão
    no extrato (vírgula decimal);
  - `## Fora da tabela` = linhas com dados que não viraram lançamento; `## Fora do período` = lançamentos de outro
    mês (não entram no Confere).
- `# Documento - ...` = comprovante, relatório, balancete ou planilha: texto limpo, sem tabela. Use para conferir os
  lançamentos do extrato.
- **Confere: NÃO** ou linha marcada `[OCR pN]` com valor duvidoso → avisar a Rosângela antes de lançar. Só nesse
  caso abra a imagem da página (a pasta aparece na linha `Origem` do .md, `...\ROF-Extratos-OCR\...\pN.png`).
- Se o `_extrato.md` ainda não existir: pedir para esperar 5 minutos ou dar dois cliques em
  **"Converter extratos agora"** na área de trabalho (ou rodar
  `python "C:\Users\User\OneDrive\EXTRATOS\_ferramentas\conversor.py" "<arquivo>"`).

## Mais detalhes
- Manual: `C:\Users\User\OneDrive\EXTRATOS\_ferramentas\LEIA-ME.md`.
- Código e manutenção: repositório ROFContabilidade/Meus-Projetos, pasta `Conversor-Extratos/` (skill
  `rof-conversor-extratos`).
