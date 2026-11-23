# Sistema de emissão de NFS-e da ROF — instruções para qualquer Claude

Você está na pasta do sistema que emite as notas fiscais de serviço (NFS-e, padrão nacional) dos clientes da ROF
Contabilidade e das empresas do Dr. Everton Soares. Leia este arquivo inteiro antes de agir.

## O que existe aqui
| Arquivo / pasta | Para que serve |
|---|---|
| `00 - LEIA PRIMEIRO.md` | Resumo para pessoas (Dr. Everton, Rosângela, Ellen, Gabi). |
| `01 - PROCEDIMENTO PASSO A PASSO.md` | **O roteiro de cada mês.** Siga na ordem. |
| `02 - EMPRESAS\` | Uma ficha por empresa emitente: CNPJ, certificado, planilha, pasta das notas, padrão de descrição, numeração. |
| `03 - PENTE FINO E HISTORICO.md` | Achados, correções e decisões já tomadas (não repetir erros). |
| `04 - Programa\` | O programa (Python): emissão pela API oficial, ferramentas de consulta, testes. |
| `05 - Modelos\` | Modelo de lote (JSON) e script de montagem de lote. |

## Regras que não se quebram
1. **Só emite com o "sim" do Dr. Everton** (ou de quem ele autorizar), para aquela nota ou para o lote dito em palavras.
2. **Nunca digite senha de certificado, PIN ou senha de portal.** A pessoa digita. O certificado A1 fica instalado no
   Windows (repositório Pessoal, chave não exportável) e o programa assina por ele sem senha.
3. **Nunca resolva o "Sou humano" (hCaptcha)** do portal. Use a API (ferramentas do programa) para baixar XML/PDF.
4. **Antes de emitir:** conferir (`--so-conferir`), conferir se a nota já não foi emitida (histórico do programa e
   `notas-emitidas`) e conferir a última DPS usada na série (campo `dps_ja_usadas` da ficha).
5. **Divergência de dado do tomador** (CEP, bairro, CPF): parar, conferir na fonte (contrato, cadastro, Correios)
   e dizer qual fonte diz o quê. CEP que não existe nos Correios: usar o CEP da rua nos Correios e registrar.
6. **Endereço completo com CEP em toda nota** (ordem do Dr.).
7. **Nunca apague nem mova arquivo** de cliente. Só PDF vai para o Drive da ROF; XML fica guardado no computador.
8. Registrar o andamento de cada lote num arquivo `00 - ANDAMENTO` (o que foi emitido, número, chave, fontes,
   pendências), a cada etapa.

## Onde ficam as coisas (caminhos reais)
- Esta pasta (OneDrive do Dr.): `CLIENTES - PROCESSOS\11 - EXTRAJUDICIAL\ROF CONTABILIDADE\SISTEMA NFS-e ROF (comece aqui)`.
  Cópia no Google Drive da Rosângela: `Trabalho ROF > SISTEMA NFS-e ROF (comece aqui)`.
- Dados do programa em cada computador: `%APPDATA%\EmissorROF\` (config, numeração, fichas, histórico, notas).
- Planilhas de faturamento e PDFs das notas: Google Drive da Rosângela (conta da ROF, aberta no Chrome da ROF).
  Ver a ficha de cada empresa.
- Andamentos dos lotes já feitos: `ROF CONTABILIDADE\AGENTES ICMS POR ESTADO (piloto com a Rosangela)\10 - Emissor de NFS-e\06 ...` e `07 ...`.
- Certificados (arquivos .pfx) da ROF e clientes: Drive da Rosângela, `Trabalho ROF > Certificados`.

## Como o Claude trabalha aqui (resumo)
1. Ler a ficha da empresa em `02 - EMPRESAS`.
2. Ler a aba do mês na planilha de faturamento (sem baixar: abrir no Chrome da ROF e ler pela consulta da planilha).
3. Para cada linha: achar a nota anterior do cliente (`ferramentas_nfse.py notas-emitidas`, índice CSV) e copiar
   dados e padrão de descrição; cliente novo: contrato (Drive/OneDrive).
4. Montar o lote JSON (modelo em `05 - Modelos`), rodar `emitir_lote.py lote.json --so-conferir`.
5. Mostrar a tabela ao Dr. e emitir com o "sim": `emitir_lote.py lote.json --thumb <impressão digital>`.
6. Copiar os PDFs com o nome padrão da empresa e enviar ao Drive da ROF (técnica no procedimento, passo 8).
7. Registrar o andamento.

Detalhes, comandos e armadilhas: `01 - PROCEDIMENTO PASSO A PASSO.md`.
