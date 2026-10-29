## Leitura de extratos (Conversor de extratos ROF)

Validado por Rosangela, 29/10/2026. Para extratos, esta seção prevalece sobre "Leitura de Arquivos".

- No meu computador roda o "Conversor de extratos ROF" (programa conversor.py, instalado em
  C:\Users\User\OneDrive\EXTRATOS\_ferramentas). Ele converte sozinho, a cada 5 minutos, os extratos
  (PDF, OFX, CSV, XLSX) das pastas "Extrato" dos clientes no Google Drive (Arquivos RENATA Dominio,
  Arquivos ROF Dominio e Arquivos PROTECTION Dominio\25 - Cosmetici) e da pasta
  C:\Users\User\OneDrive\EXTRATOS\01 - Entrada.
- Ao lado de cada original ele grava um arquivo com o mesmo nome terminado em _extrato.md
  (ex.: sicredi_09.pdf -> sicredi_09_extrato.md).
- NUNCA leia o PDF, OFX, CSV ou XLSX original do extrato. Leia SEMPRE o _extrato.md.
  - O que começa com "# Extrato -" é o extrato: tabela data|histórico|doc|valor|saldo, débito com sinal
    negativo, e a linha "Confere" (saldo inicial + créditos + débitos = saldo final).
  - O que começa com "# Documento -" é comprovante, relatório ou planilha: texto limpo, use para conferir
    os lançamentos.
- Se o Confere disser "NÃO", ou se uma linha marcada [OCR] tiver valor duvidoso, avise-me antes de lançar.
  Só nesse caso abra a imagem da página (a pasta aparece na linha "Origem" do .md).
  - O mesmo vale quando o .md disser "tabela NÃO montada" (não há linha Confere): avise antes de lançar.
- Se o _extrato.md ainda não existir, peça para eu esperar 5 minutos ou dar dois cliques em
  "Converter extratos agora" na área de trabalho.
- Com o motor desta skill (`scripts/extrato_dominio.py`), o passo de leitura é sempre sobre o .md:
  `python scripts/extrato_dominio.py ler "<nome>_extrato.md" -o trabalho/normalizado.csv`. O script recusa
  o arquivo e pede para avisar a Rosangela quando o Confere não é "sim" ou a tabela não foi montada, e
  lista as linhas [OCR] em ATENCAO_OCR.
