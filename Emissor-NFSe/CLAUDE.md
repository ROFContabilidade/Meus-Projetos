# Emissor ROF de NFS-e — instruções para o Claude no PC da Rosângela (ROF Contabilidade)

Você está em `C:\EmissorROF`, o sistema que emite as NFS-e (padrão nacional, API oficial da Receita) dos clientes
da ROF. Ele foi criado e testado em produção no computador do Dr. Everton em 21/11/2026 (38 notas autorizadas) e
instalado aqui pelo `1_INSTALAR.bat`. Leia este arquivo inteiro antes de agir. Depois, leia na ordem
`docs\01 - PROCEDIMENTO PASSO A PASSO.md`, `docs\03 - PENTE FINO E HISTORICO.md` e a ficha da empresa em `docs\`.

## Diferenças em relação aos documentos de `docs\` (escritos no PC do Dr.)
| Nos docs | Neste PC |
|---|---|
| pasta `04 - Programa` | `C:\EmissorROF\programa` (os comandos rodam lá dentro) |
| `05 - Modelos` | `C:\EmissorROF\modelos` |
| série 1 | **série 2**. A série 1 é do PC do Dr. Nunca mude a série deste PC para 1. |
| `python` | o comando gravado em `C:\EmissorROF\python.txt` (ex.: `py -3.12`) |
| Planilha lida pelo Chrome | O Drive da ROF está sincronizado em `G:\Meu Drive`: ler a planilha direto do arquivo, **só leitura**, com `openpyxl`. Conferir com a Rosângela as linhas coloridas (azul = acordo/sucumbência/alvará). |
| PDFs enviados ao Drive pelo Chrome (passo 8) | Basta **copiar** os PDFs para a pasta do mês em `G:\Meu Drive\...`, porque o Drive sincroniza sozinho. Não use a técnica do Chrome. |
| Andamentos em `AGENTES ICMS POR ESTADO...` (OneDrive do Dr.) | Gravar em `C:\EmissorROF\andamentos\<empresa>_<aaaa-mm>\` |

Caminhos no Drive (conferir que existem antes de usar):
- Planilha da Soares FRG: `G:\Meu Drive\Trabalho ROF\Soares Advocacia Financeiro\Soares FRG\Financeiro\<ano>\Faturamento <ano>.xlsx`
- Planilha da Soares Curitiba: `G:\Meu Drive\Trabalho ROF\Soares Advocacia Financeiro\Soares CURITIBA\Financeiro\<ano>\Faturamento <ano>.xlsx`
- PDFs das duas: `G:\Meu Drive\Contabilidade\Advocacia Soares\Notas Fiscais\<ano>\<MM>_<ano>\`
- Certificados (.pfx): `G:\Meu Drive\Trabalho ROF\Certificados\`

## Regras que não se quebram
1. **Só emite com o "sim" explícito** da Rosângela (que confirma com o Dr. Everton nas empresas dele), para a lista
   mostrada. Antes: `emitir_lote.py <lote> --so-conferir`, todas OK.
2. **Nunca digite senha de certificado, PIN ou senha de portal.** Certificado novo: a Rosângela roda
   `2_INSTALAR_CERTIFICADO.bat` e digita a senha. Você usa só a impressão digital (`4_VER_CERTIFICADOS.bat`).
3. **Nunca resolva o "Sou humano" (hCaptcha)** do portal.
4. **Nunca reemita no escuro.** Situação INCERTA ou erro no meio do lote: conferir no servidor (Histórico →
   "Conferir no servidor", ou `ferramentas_nfse.py notas-emitidas`) antes de repetir.
5. Conferir antes de cada lote: notas já emitidas no mês (`ferramentas_nfse.py notas-emitidas`) e a última DPS da
   série (`dps_ja_usadas` na ficha).
6. Divergência de dado do tomador (CEP, bairro, CPF): parar, conferir na fonte e dizer qual fonte diz o quê.
   Endereço completo com CEP em toda nota.
7. **Competência não pode ser futura** (regra E0015). O padrão é o último dia do mês da aba, então as notas do mês
   corrente só saem a partir do último dia do mês, salvo decisão da Rosângela.
8. Nunca apague nem mova arquivo de cliente. XML fica em `%APPDATA%\EmissorROF\dados\notas`; só PDF vai para o Drive.
9. Registrar o andamento de cada lote num `00 - ANDAMENTO.md` (emitidas, nº, chave, fontes, pendências).

## Empresas prontas (fichas em `%APPDATA%\EmissorROF\dados\empresas\`)
| Empresa | CNPJ | Observação |
|---|---|---|
| Soares Advocacia FRG | 43.174.172/0001-94 | série 1 usada até DPS 24 no PC do Dr.; certificado vence 03/01/2027 |
| Soares Curitiba (Lucas Soares) | 49.325.547/0001-56 | série 1 usada até 685 em outros sistemas; certificado vence 01/10/2027 |

Neste PC a série 2 é nova para as duas empresas (começa na DPS 1).

## Empresa nova do escritório
1. Certificado A1 dela instalado (`2_INSTALAR_CERTIFICADO.bat`) **ou** procuração eletrônica da empresa para a
   ROF (serviço NFS-e no e-CAC), usando o certificado da ROF.
2. Baixar as notas anteriores: `ferramentas_nfse.py notas-emitidas --thumb <impressão> --cnpj <CNPJ> --saida <pasta>`.
   Isso traz os tomadores, o padrão de descrição, os tributos aproximados e a última DPS por série.
3. Montar a ficha `<CNPJ>.json` copiando `modelos\ficha_empresa_MODELO` e preenchendo com os dados das notas
   anteriores (município IBGE, `op_simp_nac`, `tot_trib`, serviço/código, `dps_ja_usadas`). Mostrar à Rosângela.
4. Criar a ficha de texto em `docs\` (como as da Soares) com planilha, pasta das notas e nome padrão do PDF.
5. Limites: só Simples Nacional, sem retenções federais, sem cancelamento (portal), competência até 2026.

## Comandos (dentro de `C:\EmissorROF\programa`, usando o Python de `python.txt`)
- Testes: `emissor_rof.py --testes`
- Certificados: `ferramentas_nfse.py certificados`
- Notas já emitidas: `ferramentas_nfse.py notas-emitidas --thumb <T> --cnpj <CNPJ> --saida <pasta>`
- PDF por chave: `ferramentas_nfse.py por-chave --thumb <T> --saida <pasta> <chave>`
- Conferir lote: `emitir_lote.py <lote.json> --so-conferir`
- Emitir lote (só depois do "sim"): `emitir_lote.py <lote.json> --thumb <T>`
- Tela no navegador: `C:\EmissorROF\3_ABRIR_EMISSOR.bat`
