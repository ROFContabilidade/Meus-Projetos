---
name: "rof-conversor-extratos"
description: "Conversor local de extratos bancários da ROF Contabilidade (PDF com texto ou escaneado, OFX, CSV, XLSX) para <nome>_extrato.md enxuto (data|histórico|doc|valor|saldo + linha Confere), com OCR do Windows e tarefa a cada 5 minutos na pasta OneDrive\\EXTRATOS\\01 - Entrada. Usar quando falarem em converter extrato, _extrato.md, pasta EXTRATOS, OCR de extrato escaneado, Confere NÃO, conversor.log, INSTALAR_CONVERSOR, ou antes de analisar qualquer extrato (ler o .md, nunca o PDF/OFX)."
---

# ROF — Conversor de extratos

Programa em `Conversor-Extratos/`. Roda no Windows da Rosângela; instalado em `%OneDrive%\EXTRATOS\_ferramentas`
pelo arquivo único `INSTALAR_CONVERSOR.bat`.

## Regra para analisar extratos
- Ler sempre o `<nome>_extrato.md`, **nunca** o PDF/OFX original.
- Abrir a imagem da página (`%TEMP%\ROF-Extratos-OCR\<nome>-<hash>\pN.png`, citada na linha `Origem`) só quando a
  linha for `[OCR pN]` (ou "todas as linhas foram lidas por OCR") com valor duvidoso, ou quando `Confere: NÃO`.
- `.md` ainda não existe → rodar `python conversor.py "<arquivo>"` primeiro.
- `## Fora da tabela` = linhas com dados que não viraram lançamento; olhar quando o Confere não bater.

## Regras do conversor (não quebrar)
- Original só leitura; `.md` nunca sobrescreve (`_extrato (2).md`...). Tudo local (sem internet; OCR = Windows.Media.Ocr).
- Página escaneada = menos de 80 caracteres de texto próprio (sem cabeçalho/rodapé repetido), **tenha ou não imagem**.
- OCR que relê o cabeçalho é removido; OCR vazio → `(OCR sem texto: abrir a imagem da página)`; nenhuma página some.
- Nunca arredondar/corrigir valor, data ou nome. Débito com `-`. Sinal vem de: `-`/`D`/`C`/parênteses, coluna
  Crédito/Débito do cabeçalho, seção "Total de entradas/saídas", ou diferença do saldo da linha; senão `(sinal?)`.
- Layout inseguro (sem lançamentos ou >25% das linhas com valor fora da tabela) → texto limpo por página.
- Ao mudar qualquer arquivo, rodar `python gerar_instalador.py` (regera `INSTALAR_CONVERSOR.bat` e confere os 8 arquivos).
- `.ps1` salvos em UTF-8 **com BOM** (Windows PowerShell 5.1). `.bat` só ASCII.
- Testes fora do Windows: `ROF_OCR_TESTE=tesseract python conversor.py --stats arquivo.pdf` (tesseract só para teste).
  O OCR do Windows (`ocr_windows.ps1`) não é testável fora do Windows.
