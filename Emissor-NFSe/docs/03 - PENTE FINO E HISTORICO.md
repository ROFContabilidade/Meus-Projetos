# Pente fino do procedimento (21/11/2026) e histórico

Revisão de todo o caminho, do prompt que a Rosângela mandou em 20/11/2026 até as 38 notas emitidas em produção em
21/11/2026 (26 da Soares FRG e 12 da Lucas Soares).

## Linha do tempo
1. **20/11/2026** — Rosângela envia o prompt "Emitir NFS-e" (agente que preenche o portal). Original e análise em
   `AGENTES ICMS POR ESTADO (piloto com a Rosangela)\10 - Emissor de NFS-e\01` e `02` (18 falhas apontadas,
   prompt versão 2).
2. **21/11, manhã** — construído o programa próprio na API oficial (sem IA por nota, sem mensalidade).
3. **21/11, tarde/noite** — Soares FRG: notas 1 a 6 pelo portal (com o Dr.), 7 a 26 pelo programa. PDFs com QR e
   envio ao Drive.
4. **21/11, noite** — Lucas Soares (Curitiba): certificado instalado, notas anteriores baixadas pela API, 12 notas
   emitidas pelo programa (130 a 141).

## Achados e o que foi feito
| # | Achado | Situação |
|---|---|---|
| 1 | O "LEIA PRIMEIRO" antigo dizia que a emissão real nunca tinha sido testada. | Superado: 38 notas em produção. Este sistema substitui aquele resumo. |
| 2 | Prompt original fazia o agente digitar no portal a cada nota (caro, lento, sujeito ao "Sou humano"). | Portal fica só para exceção; emissão normal pelo programa (API). |
| 3 | PDF sem QR Code (biblioteca `qrcode` ausente). | Instalada; `requirements.txt` criado; todos os PDFs refeitos. |
| 4 | Download de PDF/XML no portal pede "Sou humano" a cada nota. | Ferramenta `por-chave` baixa o XML pela API e gera o PDF. |
| 5 | Certificado instalado no provedor novo do Windows (CNG) não assinava ("Chave inválida"). | Corrigido `win_cert.ps1` (lê CNG e CSP). Testado com os dois certificados. |
| 6 | Empresa que já usou a série em outro sistema (Lucas: série 1 até 671) faria o programa tentar DPS repetida. | Campo `dps_ja_usadas` na ficha; o programa para sem emitir e explica se achar DPS de outro sistema. A ferramenta `notas-emitidas` mostra a última DPS por série. |
| 7 | Erro de programa no meio do lote derrubava o `emitir_lote.py` sem mensagem clara. | Agora para com a mensagem e grava o resultado. |
| 8 | Caminho de arquivo acima de 260 caracteres (OneDrive) impedia gravar/ler (nota 22). | Gravação com prefixo de caminho longo; ferramentas também. |
| 9 | PDF mostrava código IBGE em vez do nome do município fora da lista curta. | Tabela completa do IBGE (5.571 municípios) em `tabelas\municipios_ibge.json`. |
| 10 | Aviso de biblioteca obsoleta (`fitz`). | Programa usa `pymupdf` (com recuo para versões antigas). |
| 11 | `EmissorROF.exe` desatualizado (anterior ao certificado do Windows). | Refeito em 21/11/2026 com as correções (ver `04 - Programa\Para instalar`). |
| 12 | Dados dos tomadores espalhados (notas antigas, contratos, planilhas). | Ferramenta `notas-emitidas` gera `indice_notas.csv` com tudo das notas anteriores. |
| 13 | Planilha lida por consulta (CSV) desloca colunas quando há célula vazia. | Procedimento manda conferir na tela (passo 2). |
| 14 | CEP de contrato inexistente nos Correios (Deivid, Júlia, Leandro Roberto). | Procedimento: CEP da rua nos Correios + registro. |
| 15 | **Senhas no nome dos arquivos de certificado** (pasta `Trabalho ROF > Certificados`). | **Risco de segurança: não corrigido** (decisão da ROF). Recomendação: renomear os .pfx e guardar as senhas em cofre/gerenciador. |
| 16 | Dois Chromes conectados ao mesmo tempo (Dr. e ROF). | Procedimento: conferir o navegador em uso antes de abrir o Drive. |

## Ainda falta (próximas etapas)
1. **Grupo IBS/CBS antes de 01/01/2027** (reforma tributária). Sem ele, notas de 2027 bloqueadas no programa.
2. **Procuração eletrônica para a ROF**: a ROF tem certificado A1 próprio (R O F da Silva Ltda). Com procuração de
   cada cliente (serviço NFS-e), a ROF emite por todos sem instalar o certificado de cada um.
3. Cancelamento e substituição de nota pelo programa (hoje: portal).
4. Texto das notas de acordos com nº dos autos (linhas azuis), a definir com o Dr.
5. Renovação dos certificados: Soares FRG 03/01/2027; Lucas 01/10/2027.
6. Instalar nos computadores da Ellen, Rosângela e Gabi (passo 0 do procedimento ou o `.exe`).
