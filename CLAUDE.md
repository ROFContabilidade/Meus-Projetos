# ROF Contabilidade - regras permanentes

## Extratos bancários
- Para analisar um extrato, leia o `<nome>_extrato.md` gerado pelo conversor (fica ao lado do original, em
  `OneDrive\EXTRATOS\01 - Entrada\...` ou na pasta `Extrato` do cliente no Google Drive: Arquivos RENATA Dominio,
  Arquivos ROF Dominio e Arquivos PROTECTION Dominio\25 - Cosmetici). **Nunca** leia o PDF ou o OFX original.
- Só abra a imagem da página (pasta indicada na linha `Origem` do .md, `%TEMP%\ROF-Extratos-OCR\...\pN.png`) quando a
  linha estiver marcada `[OCR pN]` (ou o .md disser que todas as linhas são OCR) e o valor parecer duvidoso, ou quando
  a linha `Confere` disser `NÃO`.
- Se o `_extrato.md` ainda não existir, rode o conversor primeiro:
  `python "%OneDrive%\EXTRATOS\_ferramentas\conversor.py" "<arquivo>"`.
- Código do conversor: `Conversor-Extratos/` (ver a skill `rof-conversor-extratos`).
