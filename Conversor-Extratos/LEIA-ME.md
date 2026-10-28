# Conversor de extratos bancários (ROF Contabilidade)

Transforma extratos **PDF (com texto ou escaneado), OFX, CSV e XLSX** num arquivo `<nome>_extrato.md`
curto, para analisar no Claude gastando poucos tokens. **Tudo roda no computador**: nada vai para a internet.
O OCR é o do próprio Windows. O original **nunca** é apagado, movido nem alterado.

## Como usar
- Salve ou baixe o extrato em `EXTRATOS\01 - Entrada` (pode usar uma subpasta por cliente).
- Em até 5 minutos aparece ao lado o `itau-out-2026_extrato.md` (mesmo nome + `_extrato.md`).
- Para converter na hora:
  - dois cliques em **Converter extratos agora** (área de trabalho): converte tudo o que for novo na pasta de entrada;
  - ou clique com o botão direito no arquivo > **Enviar para** > **Converter extrato (ROF)**;
  - ou arraste o arquivo para cima de `CONVERTER_AGORA.bat`.
- Se o `.md` já existir, o original não é convertido de novo na rotina automática. Pelo "Enviar para",
  o arquivo novo sai como `_extrato (2).md`, `(3)`...

## O que sai no .md
```
# Extrato - itau-out-2026.pdf
Banco: Itaú (341) | Ag: 1234 | Conta: 56789-0 | Titular: ... | Período: 01/10/2026 a 31/10/2026
Origem: 01 - Entrada\Cliente\itau-out-2026.pdf | 2 página(s) | método: texto do PDF | gerado em ...
Saldo inicial: 8.230,15 | Créditos: ... (29) | Débitos: -... (31) | Saldo final: ... | Confere: sim
data|histórico|doc|valor|saldo
03/10/2026|PIX RECEBIDO FULANO|123456|1500,00|8.230,15
```
- Débito sai com `-`. Os valores saem como estão no extrato: nada é arredondado, corrigido ou inventado.
- **Confere** = saldo inicial + créditos + débitos = saldo final. Se der `NÃO (diferença de R$ x)`, ele também diz
  em que linha o saldo deixou de fechar (pode ser erro de OCR ou um lançamento que ficou fora da tabela).
- Linhas `[OCR pN]` foram lidas por OCR na página N. A imagem da página fica na pasta citada na linha `Origem`
  (`%TEMP%\ROF-Extratos-OCR\...\pN.png`).
- `## Fora da tabela`: linhas com dados que não viraram lançamento (nada some calado).
- Layout que não deu para entender com segurança: em vez da tabela, sai o texto limpo por página (`## Página N`).
- Cabeçalho e rodapé que se repetem em mais da metade das páginas, "Página X de Y", SAC/ouvidoria e avisos são retirados.

## Como funciona
| Tipo | Como lê |
|---|---|
| PDF com texto | texto do próprio PDF, página por página (Python + pymupdf) |
| PDF escaneado / foto | página com menos de 80 caracteres de texto próprio vai para o OCR do Windows (`Windows.Data.Pdf` + `Windows.Media.Ocr`, português). Decide pelo texto, **não** pelo número de imagens. O OCR que só relê o cabeçalho é descartado. |
| OFX | lançamentos `STMTTRN` direto do arquivo (Windows-1252 ou UTF-8, acentos preservados), sem FITID |
| CSV / XLSX | colunas Data / Histórico / Documento / Valor (ou Crédito e Débito) / Saldo |

## Arquivos desta pasta (`EXTRATOS\_ferramentas`)
| Arquivo | Para que serve |
|---|---|
| `conversor.py` | o conversor (PDF, OFX, CSV, XLSX). `python conversor.py` varre a entrada; `python conversor.py arquivo.pdf` converte um arquivo |
| `ocr_windows.ps1` | OCR do Windows: grava `pN.png` (imagem), `pN.txt` e `pN.tsv` (texto com posição das palavras) |
| `converter_sem_python.ps1` | plano B se o computador não tiver Python: OCR de todas as páginas do PDF, texto por página |
| `agendar_tarefa.ps1` | cria a tarefa **ROF - Converter extratos** (ao entrar no Windows e a cada 5 minutos, oculta) |
| `CONVERTER_AGORA.bat` | conversão na hora (dois cliques, arrastar e soltar ou Enviar para) |
| `config.json` | qual é a pasta de entrada |
| `python.txt` | onde está o Python (criado pelo instalador) |
| `conversor.log` | uma linha por arquivo: data, arquivo, resultado |
| `estado.json` | arquivos que deram erro (não tenta de novo até o arquivo mudar) |

## Problemas
- **Nada aparece**: veja o `conversor.log`. Arquivo recém-salvo espera 20 segundos. Arquivo que deu erro só é tentado
  de novo quando muda (ou pelo "Enviar para").
- **"OCR em português não instalado"**: Configurações > Hora e idioma > Idioma > Português (Brasil) > Opções >
  Reconhecimento óptico de caracteres > Baixar.
- **PDF com senha**: abra no navegador, imprima como PDF sem senha e salve na entrada.
- **.xls antigo**: abra no Excel e salve como `.xlsx`.
- Reinstalar ou mudar a pasta: rode o `INSTALAR_CONVERSOR.bat` de novo.
- Tirar a tarefa: Agendador de Tarefas > **ROF - Converter extratos** > Excluir.
