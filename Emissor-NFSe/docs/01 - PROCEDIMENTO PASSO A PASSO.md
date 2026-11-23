# Procedimento de emissão de NFS-e — passo a passo (versão de 21/11/2026)

Testado em produção em 21/11/2026: Soares Advocacia FRG (26 notas, outubro/2026) e Lucas Soares / Soares Curitiba
(12 notas, outubro/2026). Os comandos rodam no PowerShell, dentro de `04 - Programa`.

---
## 0. Uma vez por computador
1. Python 3.12 e as bibliotecas: `python -m pip install -r requirements.txt` (inclui `qrcode`, sem ela o PDF sai
   sem QR Code).
2. Conferir: `python emissor_rof.py --testes` (21 testes, todos OK).
3. Configuração em `%APPDATA%\EmissorROF\config.json`: `"ambiente": "1"` (produção), `"serie": 1`.

## 1. Uma vez por empresa (cadastro)
1. **Certificado A1 da empresa instalado no Windows** (repositório Pessoal), OU procuração eletrônica da empresa
   para o CNPJ de quem tem o certificado (serviço NFS-e, Portal de Serviços da Receita; FAQ NFS-e 17.7 e 28.2).
   - O .pfx fica no Drive da Rosângela (`Trabalho ROF > Certificados`). Baixar e instalar: a **pessoa** digita a
     senha. Jeito mais simples: script que pede só a senha e usa `Import-PfxCertificate` (sem `-Exportable`).
   - Ver a impressão digital: `python ferramentas_nfse.py certificados`.
2. **Baixar as notas já emitidas** (dados dos tomadores, padrão de descrição e numeração):
   `python ferramentas_nfse.py notas-emitidas --thumb <impressão> --cnpj <CNPJ> --saida <pasta>`
   → `indice_notas.csv` + XML. A última linha do comando mostra a **última DPS usada por série**.
3. **Ficha da empresa** em `%APPDATA%\EmissorROF\dados\empresas\<CNPJ>.json` (modelo nas fichas de `02 - EMPRESAS`).
   Campos que mais erram: `municipio_ibge`, `op_simp_nac` (3 = ME/EPP), `tot_trib` (copiar da nota anterior:
   `pTotTribSN` ou `pTotTrib`), `producao_liberada`, e **`dps_ja_usadas`** (ex.: `{"1": 671}`) quando a empresa já
   usou a série 1 em outro sistema. Sem isso o programa tenta uma DPS que já existe e para sem emitir.

## 2. Ler a planilha do mês
- Planilha `Faturamento <ano>.xlsx` da empresa (caminho na ficha). Uma aba por mês. Colunas: data, nome, valor, nº
  do contrato.
- **Não baixar.** Abrir no Chrome da ROF e ler pela consulta da própria planilha (JavaScript na página):
  `fetch('/spreadsheets/d/<id>/gviz/tq?tqx=out:csv&sheet=10')`. Atenção: células vazias deslocam colunas no CSV;
  **conferir na tela** a coluna do nº e a cor (azul = acordo/sucumbência/alvará, decisão do Dr.).
- Conferir que a soma das linhas bate com o total da aba.

## 3. Dados de cada tomador (três fontes)
1. Nota anterior do cliente (índice CSV / XML). É o modelo: mesmos dados e mesmo padrão de descrição.
2. Cliente sem nota anterior: contrato de honorários (Drive da ROF, pasta `CWB` ou pasta do cliente; OneDrive
   `CLIENTES - PROCESSOS\<área>\<NOME>\01 Docs`). PDF escaneado: ler pela visualização.
3. CEP: conferir no ViaCEP. Não existe nos Correios → buscar a rua (`viacep.com.br/ws/UF/Cidade/Rua/json/`), usar
   o CEP dos Correios e registrar. Código IBGE do município sempre do ViaCEP (não de memória).
- Endereço sem número: `S/N` e registrar como pendência.

## 4. Descrição da nota (padrões aprovados pelo Dr.)
```
Prestação de serviços jurídicos (Honorários Contratuais)
Contrato de honorários nº <nº>
[Acordo | Manutenção de contrato — se a nota anterior do cliente trazia]
Pagamento realizado dia <dd/mm/aaaa>.
```
- **Sem contrato** (cobrança de carteira, serviço avulso): sem a linha do contrato; "Honorários advocatícios" ou
  "serviço avulso: <qual>".
- **Acordo em execução de honorários** (cliente executado): nota em nome do executado, com os autos:
  `Acordo em execução judicial de honorários (execução de título extrajudicial) - Autos nº <nº CNJ>`.
- **Outros acordos (linhas azuis)**: o Dr. quer o nº dos autos; texto ainda a definir com ele.
- **Competência**: último dia do mês da aba (outubro/2026 → 31/10/2026).

## 5. Montar o lote
- Copiar `05 - Modelos\montar_lote_MODELO.py` para a pasta do andamento do mês, preencher a lista e rodar. Ele
  confere cada CEP no ViaCEP e grava `lote_<empresa>_<mes>.json`.
- `python emitir_lote.py <lote.json> --so-conferir` → todas devem dar **OK**.

## 6. Conferência com o Dr. e emissão
- Mostrar a tabela (linha, cliente, valor, contrato, fonte dos dados, pendências). Esperar o "sim".
- `python emitir_lote.py <lote.json> --thumb <impressão digital do certificado>`
- O lote **para no primeiro problema**. Se parar: ler a mensagem; se for dúvida se a nota saiu, perguntar à Receita
  antes de repetir (o programa faz isso: Histórico → "Conferir no servidor"). Nunca reemitir no escuro.
- Resultado com número e chave: `<lote>_resultado.json`.

## 7. PDFs
- O programa grava XML e PDF (DANFSe com QR Code) em `%APPDATA%\EmissorROF\dados\notas\<CNPJ>\<aaaa-mm>` e na
  `pasta_notas` da ficha.
- Copiar os PDFs com o **nome padrão da empresa** (ver ficha): Soares FRG `NF_<nº>_<NOME>.pdf`; Lucas
  `NFSe <nº> - <NOME>.pdf`.
- Nota emitida pelo portal (sem PDF): `python ferramentas_nfse.py por-chave --thumb <...> --saida <pasta> <chave>`.
- Abrir um PDF de cada lote e conferir número, tomador, valor, competência e QR.

## 8. Enviar ao Drive da ROF
Pasta: `Contabilidade > Advocacia Soares > Notas Fiscais > <ano> > <MM>_<ano>` (Soares FRG e Lucas juntas). Criar a
pasta do mês se não existir (Novo > Nova pasta).
O Drive só aceita arquivo pela janela do Windows, que o Claude não opera. Técnica que funciona (Chrome da ROF):
1. Na pasta de destino, `javascript_tool`: trocar `HTMLInputElement.prototype.click` para, em campo `type=file`,
   prender o campo na página com `aria-label` próprio em vez de abrir a janela (guardar o original).
2. Clicar em Novo > Upload de arquivo.
3. `find` pelo aria-label → `file_upload` com os caminhos dos PDFs (até 10 MB por vez; caminho longo → copiar antes
   para pasta curta).
4. Restaurar o `click` original e conferir os arquivos na pasta.
("Soltar" simulado por JavaScript **não** funciona.)

## 9. Registro
Arquivo `00 - ANDAMENTO (<empresa>, <mês>).md` na pasta do mês: lista das linhas, o que foi emitido (nº, chave),
fontes dos dados, correções feitas, pendências. Atualizar a cada etapa.

---
## Armadilhas já conhecidas
- **Certificado instalado no provedor novo (CNG)**: corrigido em 21/11/2026 (`win_cert.ps1` lê os dois formatos).
- **Série já usada por outro sistema**: preencher `dps_ja_usadas` na ficha (o programa para sem emitir se a DPS
  já existir e explica).
- **Caminhos acima de 260 caracteres** no OneDrive: o programa grava com prefixo de caminho longo; para ler à mão,
  usar `\\?\` ou copiar para pasta curta.
- **Dois Chromes conectados**: conferir qual está em uso (`list_connected_browsers`); o Drive da ROF fica no Chrome
  da ROF (conta da Rosângela), não no do Dr.
- **API oficial do DANFSe** fora do ar desde 08/2026: o PDF é gerado do XML oficial pelo programa.
- **Antes de 01/01/2027**: grupo IBS/CBS (reforma tributária) precisa entrar no programa; sem ele as notas de 2027
  são bloqueadas e a emissão volta ao portal.
- **Certificados**: Soares FRG vence 03/01/2027; Lucas Soares vence 01/10/2027.
