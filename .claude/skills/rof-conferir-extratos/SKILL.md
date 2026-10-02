---
name: "rof-conferir-extratos"
description: "Rotina mensal da ROF Contabilidade: conferir, pasta a pasta no Google Drive, quais empresas já mandaram e quais ainda faltam mandar o extrato bancário, usando como base a aba Contabil da planilha \"Rotinas tarefas do mes.xlsm\". Gera a planilha \"Extratos faltantes\" (Painel, Resumo por empresa, Por banco, Mensagens de WhatsApp, Arquivos encontrados). Usar quando pedirem para conferir/checar extratos recebidos ou faltantes, controle de extratos, quem não mandou extrato, cobrar extrato dos clientes, ou atualizar o Controle de Extratos."
---

# ROF — Conferência de extratos bancários (Drive × Rotina)

Programa: `Conferencia-Extratos/conferir_extratos.py` (deste repositório). Ele **não** acessa o Drive:
o Claude varre o Drive pelo conector Google Drive, monta um *snapshot* JSON e o script cruza com a Rotina.

## Base: planilha da Rotina
- Arquivo **"Rotinas tarefas do mes.xlsm"** no Meu Drive (id `1Tjj4GVBsPtlmW8deUIs2iW6HvYQp638Y`; se mudar, `search_files` por `title contains 'Rotina'`).
- Baixar com `download_file_content` (o resultado vem grande → salvo em arquivo; `jq -r .content arq | base64 -d > rotina.xlsm`).
- Aba **Contabil**: col. A = grupo (KON / ROF SERVIÇOS / PROTECTION), C = empresa (com CNPJ), D = código Domínio,
  E = descrição ("Extrato Bancario Sicredi"...), F = status (Realizado / Em execução / S/MOV). Cada linha de extrato = um banco esperado.

## Onde ficam as pastas (G: = Meu Drive da Rosangela → Trabalho ROF\Contabilidade)
| Grupo na Rotina | Pasta raiz | id |
|---|---|---|
| KON CONTABILIDADE | Arquivos RENATA Dominio | `10Hxhjex-oHA4Ik7zZmCUeoy4DzVzMv4R` |
| ROF SERVIÇOS | Arquivos ROF Dominio | `1dpHtr-3dH3eRmlzDHTenky0XfBVN864B` |
| PROTECTION CONTABILIDADE | Arquivos PROTECTION Dominio | `1engfKFRy8bVfaJWw1-0cOe-c2LpaPszZ` |

- Empresa = pasta que começa com o código (`17 - AP Transportes`, `7_D C Grup`, `1008_Abba Joinville`). `1_RBA Contabilidade` = KON (mesmo CNPJ).
- Código 25 existe nos dois: KON = Celular no Boleto (RENATA); PROTECTION = Cosmetici. Casar pela raiz do grupo.
- Estruturas do mês encontradas (todas valem):
  - `<empresa>\2026\MM_2026\Extrato` (a maioria)
  - `<empresa>\MM_2026\Extrato` (empresas novas, sem pasta de ano)
  - `<empresa>\FISCAL-CONTABIL\2026\MM_2026\Extrato` ou `FISCAL_CONTABIL\MM_2026\Extratos` (7, 10, 164)
  - ROF: `<empresa>\Fiscal_Contabil\2026\MM_2026\Extrato` ou `Fiscal_Contabil\MM_2026\Extrato(s)`
  - Cuidado: 109 tem `2026\08_2026\08_2026\Extrato` (duplicada).
- Pastas `INATIVAS` (RENATA) e `INATIVADAS` (ROF): 68, 97, 123 estão lá (na Rotina constam S/MOV).

## Como varrer rápido (conector Google Drive)
- Usar consultas em lote: `(parentId = 'A' or parentId = 'B' ...) and mimeType = 'application/vnd.google-apps.folder'`, ~40 pais por consulta, `pageSize: 100`, `excludeContentSnippets: true`.
- `title = '2026'` / `title = '08_2026'` só é exato **combinado com parentId**; sozinho a busca é aproximada.
- `title contains 'Extrato'` pega "Extrato" e "Extratos".
- Resposta muito grande é salva em arquivo → extrair com `jq -r '.files[] | [.parentId, .title] | @tsv'`.
- **Sempre paginar** a listagem de arquivos: se vier `nextPageToken`, repetir a mesma consulta com `pageToken`
  até não vir mais (em 02/10/2026 a 1ª varredura sem paginar perdeu ~146 arquivos de 08/09, ex.: Sicoob da Pai e Filhos).
- Truque para a resposta ir para arquivo (e ler com jq em vez de copiar à mão): usar `snippetVerbosity: DETAILED`
  ou `MAX_ALLOWED` nas listagens de arquivos; ~35 pastas por consulta. O snippet também traz o texto (OCR) das imagens.
- Ordem: raiz → empresas → (ano | FISCAL…) → `MM_AAAA` → `Extrato` → arquivos. Guardar tudo em TSV no scratchpad.

## Snapshot e relatório
1. Montar `snapshot_AAAA-MM-DD.json` (formato no cabeçalho do script): para cada empresa e mês
   `pasta_mes`, `pasta_extrato`, `arquivos` (nomes) e `obs` opcional; e `inativas_no_drive`.
2. Rodar: `python Conferencia-Extratos/conferir_extratos.py rotina.xlsm snapshot.json Extratos_faltantes_AAAA-MM-DD.xlsx`
3. Meses: por padrão o **mês que acabou de fechar** e o **anterior** (ex.: em 02/10 → 08_2026 e 09_2026);
   se pedirem histórico, incluir mais meses no snapshot (em 02/10/2026 foi feito 04_2026 a 09_2026).
   Mês anterior à primeira pasta de mês da empresa sai como "—" (ainda não era cliente).
4. Salvar a planilha e o snapshot em `Conferencia-Extratos/relatorios/`, mandar para a usuária e resumir no chat
   (quantas faltam por mês + lista das que faltam).

## Regras de classificação
- **Recebido**: OFX/PDF/CSV/XLS/ZIP na pasta Extrato do mês; ou só TXT do escritório (= já lançado, extrato original fora da pasta).
- **FALTANDO**: pasta Extrato vazia, sem pasta Extrato, ou pasta do mês não criada.
- **Recebido (já conciliado)**: só planilha de Retiradas/Conciliação/Pró-labore do escritório na pasta — a conciliação
  foi feita com o extrato (regra da Rosangela, caso Pai e Filhos). Antes, procurar o extrato original na pasta.
- **Verificar**: só imagem/comprovante, ou só arquivos do escritório.
- **S/MOV**: todas as contas da empresa marcadas S/MOV na Rotina, **ou** print/imagem na pasta Extrato dizendo que o
  período não teve movimento ("não houve movimentações", "nenhuma movimentação", "empresa sem movimento").
  Ler o texto da imagem (snippet da busca ou `read_file_content`) e marcar `"sem_movimento": true` + `obs` no snapshot.
  Ex.: 141 TML Leite 08/2026 (print Cora), 67 Ligiane 05/2026.
- Ignorar como extrato: `.txt`, Retiradas, Conciliacao, Lancamentos, Balancete, ProLabore, comprovantes, NF/DANFE.
- Banco pelo nome do arquivo: `sicredi_*`/`relato_rio` Sicredi; uuid `xxxxxxxx-…-AAAA-MM-DD-AAAA-MM-DD` Nubank;
  `Nome_ddmmaaaa_a_ddmmaaaa_hash` Cora; `Extrato-dd-mm-aaaa-a-…` Inter; `extrato-da-sua-conta-*` C6;
  `account_statement-*`/`MercadoPago` Mercado Pago; `Entradas_Saidas_ag…` e `Extrato_NNNN_NNNNNN_data` Itaú;
  `extrato-pj-*` Santander. Quando o nome não indica o banco → "Verificar" na aba Por banco.

## Cuidados
- **Nunca** mover, renomear, apagar ou sobrescrever nada no Drive. Gravar a planilha no Drive (pasta
  `Arquivos RENATA Dominio\Controle de Extratos`) só com autorização da Rosangela, como arquivo novo.
- Em 09/2026 muitas pastas do mês ainda não existiam (02/10): é normal no início do mês; repetir a conferência depois.
- Empresas 160–163 e 165–167 estavam na Rotina mas sem pasta no Drive (02/10/2026) — avisar.
- Pasta `Extrato` dentro de `Extrato` (ex.: 132 em 05/2026): listar também a subpasta.
- Ao citar empresas para a Rosangela, conferir o código: 141 (TML Leite) e 142 (F B da Rocha) ficam lado a lado.
