---
name: rof-controle-extratos
description: "ROF Contabilidade - atualiza a planilha Controle de Extratos e Lançamentos de todas as empresas do escritório (grupos ROF SERVIÇOS, KON CONTABILIDADE e PROTECTION). Lê de novo as pastas do Drive (Arquivos ROF Dominio, Arquivos RENATA Dominio... / empresa / MM_AAAA / Extrato), confere mês a mês se o extrato foi enviado, se falta enviar e se já foi lançado (TXT de lançamento na pasta), acrescenta o mês novo, atualiza a coluna das skills de cada empresa e refaz as mensagens de cobrança para o WhatsApp. Usar sempre que a usuária pedir para atualizar o controle de extratos, a planilha de extratos e lançamentos, ver quem não mandou extrato, quais empresas faltam lançar, cobrar extratos dos clientes, mensagens de cobrança, ou o painel de extratos do mês, mesmo sem citar a skill."
---

# ROF — Controle de Extratos e Lançamentos

A planilha `Controle_de_Extratos_e_Lancamentos_AAAA-MM-DD.xlsx` mostra, para cada empresa e cada mês
(de 04/2026 até o último mês fechado):

- **extrato**: `Recebido`, `FALTANDO`, `Verificar`, `S/MOV`, `—`;
- **lançamento**: `Já lançado`, `Pronto para lançar`, `Falta extrato`, `Verificar extrato`, `S/MOV`, `—`;
- as **mensagens de cobrança** prontas para o WhatsApp, com as colunas `Enviado?` e `Data envio`.

Abas: Painel, Resumo, Lançamentos, Skills prontas, Detalhes, Por banco, Mensagens, Arquivos encontrados.

Quem faz o trabalho é o `scripts/atualizar_controle.py`. Ele só **lê** o Drive e grava uma planilha nova.
A planilha anterior serve de **base**, porque guarda o que não está nas pastas: os bancos de cada
empresa na Rotina, as confirmações manuais ("lançado: confirmado pela Rosangela..."), os meses sem
movimento informados e o "Enviado?" das mensagens. Por isso, sempre parta da última planilha gerada.

## Onde rodar

As pastas ficam no computador do escritório, no Google Drive para computador:
`G:\Meu Drive\Trabalho ROF\Contabilidade\` (subpastas `Arquivos ROF Dominio`, `Arquivos RENATA Dominio`...).

- Rode numa sessão que enxergue essa pasta: Claude no computador (Cowork ou Claude Code) com a pasta
  `Contabilidade` compartilhada. O script percorre umas 3 mil pastas e arquivos em segundos.
- **Não** tente fazer a varredura pelo conector do Google Drive: ele devolve só 5 itens por consulta,
  então seriam milhares de chamadas. Se a sessão não tiver acesso à pasta, diga isso à usuária e peça
  para abrir a conversa no Claude do computador com a pasta `Contabilidade` liberada.
- Se a usuária insistir em atualizar pelo conector (sessão na nuvem), faça só um recorte
  (ex.: as empresas com skill): ache as pastas das empresas por `title = '...'`, depois as pastas
  `MM_2026` e `Extrato` com consultas `parentId = ... or ...` (até ~45 ids por consulta, `pageSize` 50),
  os TXTs com `mimeType = 'text/plain'` e os demais arquivos só das pastas que ainda não apareceram.
  Guarde cada id num arquivo do scratchpad a cada consulta. Na planilha, marque o que não foi lido
  como `Não conferido` e diga isso à usuária.
- Precisa de Python com `openpyxl` (`pip install openpyxl` se faltar; no Windows o comando pode ser `py`).

## Passo a passo

1. **Achar a planilha base**: a última `Controle_de_Extratos_e_Lancamentos*.xlsx` (pergunte onde está
   se não achar; a usuária também pode anexá-la). Ache também o `ajustes_controle_extratos.json`, que
   fica ao lado dela, se existir.
2. **Ajustes da usuária**: se ela contou algo que as pastas não mostram ("a 92 não teve movimento até
   outubro", "lancei a Cosmetici de julho, o TXT ficou fora da pasta", "a 139 abriu conta no Inter",
   "empresa 170 começou em 10/2026"), registre no `ajustes_controle_extratos.json`
   (formato em `references/ajustes.md`). Assim a informação não se perde na próxima atualização.
3. **Rodar**:
   ```
   python scripts/atualizar_controle.py --contabilidade "G:/Meu Drive/Trabalho ROF/Contabilidade" \
     --base "<planilha anterior>.xlsx" --ajustes "<ajustes_controle_extratos.json>" \
     --saida "Controle_de_Extratos_e_Lancamentos_<AAAA-MM-DD de hoje>.xlsx"
   ```
   - Por padrão o último mês é o **mês anterior ao atual** (em novembro, vai até outubro). Use
     `--fim MM_AAAA` para outro mês e `--inicio MM_AAAA` para mudar o primeiro.
   - Salve a planilha nova **ao lado da anterior**, com a data no nome. Nunca sobrescreva a anterior.
     Gravar no Drive precisa da autorização da usuária: pergunte uma vez onde salvar, se ela ainda não disse.
4. **Conferir antes de entregar**: o script mostra os totais dos dois últimos meses, as empresas
   novas e as que estão sem pasta. Abra a aba Detalhes nos casos estranhos, por exemplo
   "no controle anterior estava Recebido — conferir", uma empresa nova ou um mês inteiro FALTANDO.
   Investigue esses casos antes de entregar.
5. **Responder à usuária** em português simples, curto:
   - o resumo do mês novo (recebidos, faltando, já lançados, prontos para lançar);
   - as empresas com skill que estão **prontas para lançar** (aba Skills prontas, coluna "Fazer juntos"),
     oferecendo-se para lançar já com a skill de cada uma;
   - quantas mensagens de cobrança foram geradas (aba Mensagens), lembrando de marcar `Enviado?`;
   - as empresas novas ou sem pasta, que precisam ser conferidas na Rotina.

## Regras da conferência (o que o script faz)

- **Empresa ↔ pasta**: pelo nome da pasta registrado na base. Se o nome mudou, pelo número no início
  (`67 - X`, `67_X`) dentro da raiz do grupo (ROF → `Arquivos ROF Dominio`, KON → `Arquivos RENATA Dominio`,
  PROTECTION → `Arquivos PROTECTION...`). Pasta numerada que não está na base vira **empresa nova**.
- **Mês**: pasta `MM_AAAA` em qualquer subpasta da empresa (`2026\10_2026`, `Fiscal_Contabil\2026\10_2026`,
  e também a duplicada `08_2026\08_2026`).
- **Extrato** (pasta que começa com "Extrato" dentro do mês):
  - OFX/PDF/CSV/XLS/XLSX/ZIP → `Recebido`;
  - só imagens/comprovantes, ou só arquivos do escritório (razão, balancete, conciliação) → `Verificar`;
  - pasta vazia, sem pasta Extrato ou mês sem pasta → `FALTANDO`;
  - antes da 1ª pasta de mês da empresa → `—`.
- **Já lançado**: um TXT de lançamento na pasta do mês, normalmente dentro da Extrato
  (ex.: `64_LMP3-SOLUCOES_2026-07.txt`). Arquivos de SPED, EFD, ECD, REINF, folha etc. **não** contam.
  O `Extrato-01-09-2026-a-30-09-2026-TXT.txt` (extrato do banco em TXT) é **extrato**, não lançamento.
  Também conta como lançado o que a base já marcava como "Já lançado" (o script nunca rebaixa um
  lançamento) e o que estiver em `lancados` nos ajustes.
- **Bancos**: o banco sai do nome do arquivo e, no OFX, do código do banco (`<BANKID>`).
  Na aba Por banco, "Verificar — nome do arquivo não indica o banco" quer dizer que há extrato,
  mas não deu para saber de qual conta ele é.
- **S/MOV**: contas marcadas S/MOV na Rotina (vem da base), meses sem movimento informados (ajustes)
  ou status S/MOV que veio da base com confirmação manual.
- **Mensagens**: uma por empresa com algum mês `FALTANDO`, listando as contas da Rotina (exceto as S/MOV).
  `Enviado?` e `Data envio` são mantidos quando os meses pendentes não mudaram. Se mudaram, a mensagem
  é nova e volta para "Não".

## Skills das empresas

A coluna **Skill** e a aba **Skills prontas** saem de `references/skills_empresas.json`
(chave `"GRUPO|código"`). Sempre que for criada uma skill nova de empresa (`rof-contabilidade-...`),
acrescente a linha nesse arquivo. Confira também se alguma skill da lista de skills disponíveis
ainda não está no JSON e acrescente-a antes de rodar (o código da empresa está na descrição da skill).

## Cuidados

- Não mover, renomear nem apagar nada nas pastas das empresas.
- A Rotina (`Rotinas tarefas do mes.xlsm`) é a fonte dos bancos de cada empresa. Se a usuária disser que
  mudou a Rotina (conta nova, conta encerrada, empresa S/MOV), leve isso para os ajustes
  (`bancos_novos`, `bancos_encerrados`, `sem_movimento`).
- Se o script falhar porque a base tem outro formato (aba ou coluna com outro nome), ajuste o
  `ler_base` em vez de montar a planilha à mão. Assim a próxima atualização continua funcionando.
