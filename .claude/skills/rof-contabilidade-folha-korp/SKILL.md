---
name: "rof-contabilidade-folha-korp"
description: "KORP INFORMÁTICA — Matriz (Domínio 140, CNPJ 03.623.045/0001-00) e Filial (Domínio 145, CNPJ 03.623.045/0002-91): avalia a folha exportada do Domínio contra o extrato mensal e o plano de contas Korp e entrega sempre 3 arquivos — planilha de correções da integração, planilha de fechamento das contas patrimoniais e o TXT corrigido (com centros de custo Korp CC337, CC345, CC379, CC506, CC644, CC320) para importar na Korp. Usar quando mencionarem Folha Korp, Korp Matriz/Filial, TXT da folha, extrato da folha, centro de custo Korp ou retorno de erro da Korp."
---

# ROF Contabilidade — Folha Korp (Domínio → Korp)

Use quando Everton/Rosangela enviarem o TXT da folha exportado do Domínio para a KORP INFORMÁTICA LTDA EPP (Matriz ou Filial), o extrato da folha, o balancete, ou o retorno de erro da Korp (`Problemas_Importacao_DOMINIO.txt`, ex.: "Centro de Custo: 000000X Não cadastrado no Sistema").

## Entregas padrão (sempre as 3, para Matriz e Filial)

1. **Planilha de correções** da integração no Domínio — `Integracao_Dominio_Korp_<Empresa>_MM-AAAA.xlsx`
2. **Planilha de fechamento das contas patrimoniais** — `Fechamento_Folha_Korp_<Empresa>_AAAA.xlsx` (um arquivo por ano; cada mês novo vira uma aba e uma coluna no Resumo)
3. **TXT corrigido** — `Folha_Korp_<Empresa>_MM-AAAA.txt` (só a empresa em questão)

Salvar em `Korp/<Matriz|Filial>/<AAAA-MM>/` no repositório (o fechamento anual em `Korp/<Empresa>/`), fazer commit/push e enviar os arquivos ao usuário (SendUserFile). O TXT não vai para o Google Drive pelo conector (tamanho + precisa manter ANSI).

Antes de gerar o TXT, **avaliar os lançamentos e apresentar as correções**; perguntar só o que não dá para decidir (CC novo, lançamento sem origem no extrato, conta inexistente no grupo). Não inventar conta nem centro de custo.

## Empresas

| | Matriz | Filial |
|---|---|---|
| Código Domínio | 0000140 | 0000145 |
| CNPJ (registro 01) | 03623045000100 | 03623045000291 |
| Registro 05 (CC) no TXT do Domínio | vem preenchido (CC 1–6) | **não vem** — reconstruir |

O Domínio exporta **um único TXT com as duas empresas** sob o cabeçalho da Matriz. O código da empresa está no final do histórico do registro 03 (**colunas 558–564**). Separar por empresa e gerar um TXT para cada, com o cabeçalho (código + CNPJ) da própria empresa.

## Fontes de dados

| Arquivo | Onde | Como ler |
|---|---|---|
| Extrato Mensal da folha (`Filial_Extrato Mensal_MM.AA.xlsx`) | Google Drive (buscar pelo título) | `scripts/extrato.py` — CC, funcionário, rubrica (código, nome, P/D), encargos por CC |
| TXT da folha (`Folha.txt`) | anexo do usuário | `scripts/txt_dominio.py` — registros 02/03/05, cp1252 |
| Balancete (`Balancete_MM.AA.xls`) | anexo do usuário | `python_calamine` (o xls do Domínio não abre com xlrd/LibreOffice) |
| Plano de contas Korp (`Plano_de_Contas.xls`) | anexo do usuário | `python_calamine`; conferir se a conta existe, é analítica e não é "NAO USAR" |

Os nomes de conta do **balancete do Domínio estão desatualizados** (ex.: 3078 aparece como "Plano Odontológico", 2904 como "PAT"). Avaliar sempre pelo **plano de contas da Korp**.

## Centros de custo (de-para Korp)

Tabela da Korp: 320 ADM GERAL · 337 DESENVOLVIMENTO EM GERAL · 345 SUPORTE EM GERAL · 379 COMERCIAL GERAL · 506 QUALIDADE · 644 CONSULTORIA.

**Matriz** (pelo número, que vem no registro 05):

| Domínio | Descrição | Korp |
|---|---|---|
| 0000001 | Desenvolvedores | CC337 |
| 0000002 | Qualidade | CC506 |
| 0000003 | Suporte | CC345 |
| 0000004 | Consultores (Implantação/Consultoria) | CC644 |
| 0000005 | Administrativos / Diretoria / Financeiro | CC320 |
| 0000006 | Comercial | CC379 |

**Filial** (pela **descrição** — a numeração da Filial é diferente da Matriz; ex.: CC 4 Filial = COM HANTERS ≠ CC 4 Matriz = Consultores):

| CC Domínio Filial | Descrição | Korp |
|---|---|---|
| 4, 5 | COM HANTERS, COM BRUNO ECKS | CC379 |
| 15 | CS CUSTOMER SUCCESS (usa contas do Comercial) | CC379 |
| 7, 11, 12, 13, 17 | DES TECNOLOGIA / WEB / BACKOFFICE / PRODUÇÃO / FISCAL CONTABIL | CC337 |
| 8, 16 | SD SUPORTE, SD INFRAESTRUTURA | CC345 |
| 9 | CONSULTORIA INTERNA E GP | CC644 |
| 10 | ADM FINANCEIRO | CC320 |
| 14 | QUALIDADE | CC506 |

CC novo sem de-para: não inventar — perguntar ao usuário e acrescentar aqui.

**Formato:** código Korp alinhado à esquerda com espaços até 7 caracteres (`CC337  `). No registro 05 o CC vai no lado débito (col. 10–16) **e** no lado crédito (col. 17–23), conforme a conta; o lado sem CC fica `0000000`.

**Quais contas levam CC** (regra observada na Matriz, aplicada à Filial): todas, **exceto 2530, 2531, 2533 e 3137**. Isso inclui 2521, 2523, 2524, 2526 e 2463. Um 05 por lado com CC (débito primeiro, depois crédito).

**Filial — como achar o CC de cada lançamento:** o TXT vem em blocos por CC, na ordem do extrato. Cada bloco da folha mensal termina com o INSS patronal (INSS Empresa/Terceiros/Acid. Trabalho). Confirmar o bloco batendo o `I.N.S.S.` descontado do bloco com o "Segurados" do CC no extrato. Blocos com outra data no registro 02 (férias, rescisões) pertencem ao CC do funcionário no extrato.

## Grupos de contas Korp por área (usar para sugerir a conta certa)

| Área (CC Korp) | Salário | HE | Ajuda custo | Contrib. assist. (crédito) | INSS | FGTS | Férias | 13º | Outros |
|---|---|---|---|---|---|---|---|---|---|
| Comercial (379) | 2323 | 2577 | 2578 | 3148 | 2332 | 2334 | 2576 | 2324 | 2867 Comissão · 2341 Plano saúde |
| DES (337) | 2884 | 2904 | 2888 | 2905 | 2885 | 2886 | 2907 | 3009 | 2906 Gratificação · 2910 Aux. Educação (estagiários) · 3019 Plano saúde |
| Suporte (345) | 2891 | 2917 | 3146 | 2923 | 3078 | 2913 | 3152 | 3010 | 3150 Gratificação · 3149 VT · 2918 Plano saúde |
| CS Interno (644) | 3095 | 3151 | 3089 | 2911 | 3143 | 3097 | 3098 | — | 2883 Plano saúde |
| AQ Qualidade (506) | 2900 | 2928 | 2934 | 3080 | 3142 | 2924 | 3012 | — | 2929 Plano saúde |
| ADM (320) | 2994 | 3004 | — | 3145 | 2996 | 2997 | 3017 | — | 2995 Estagiários · 3144 VT |

Passivo/ativo: 2521 Salários a Pagar · 2523 Indenizações Trabalhistas (rescisões) · 2524 Férias a Pagar · 2526 Estágios a pagar · 2530 FGTS · 2531 INSS · 2533 IRRF · 3137 Empréstimo a Funcionário (consignado) · 2463 Adiantamento de Férias.

Decisões já confirmadas pelo usuário:
- Bolsa de estagiário (8797/8813) do DES e do CC 16: **D 2910 / C 2526**; do ADM: D 2995 / C 2526.
- Contribuição assistencial é desconto: **D 2521 (ou 2523 na rescisão) / C conta de contribuição do grupo**.
- Adiantamento de férias (937) descontado na folha: **D 2524 / C 2463**.
- Vale-refeição não utilizado (657) na rescisão do Suporte (CC 8): **D 2523 / C 3146** (Ajuda de Custo do Suporte).
- Rescisão: proventos a crédito de **2523**; INSS da rescisão D 2523 / C 2531.

## Conferência obrigatória (extrato × TXT × balancete)

Com `scripts/extrato.py` somar por CC/funcionário/rubrica e comparar com o TXT da empresa:

1. Proventos e descontos totais do extrato (o "Resumo por Rubrica" fecha com a soma por funcionário).
2. **Líquido:** 2521 + 2524 + 2526 = Líquido Geral do extrato (a rubrica 51 LIQUIDO RESCISAO aparece como desconto; o líquido das rescisões vai para 2523).
3. INSS 2531 = "Total INSS" do extrato (segurados + empresa + RAT + terceiros + férias/rescisão). Diferença de centavos por arredondamento por CC é aceitável (≤ R$ 1).
4. FGTS 2530 = "Valor do FGTS"; conferir o FGTS rescisório à parte. IRRF 2533; consignado 3137 (rubricas 714/717/721/730/9750); adiantamento de férias 2463 (937).
5. Toda rubrica do extrato tem lançamento no TXT (procurar férias, rescisões e adiantamentos que não saíram).
6. Toda conta do TXT existe no plano Korp (ex.: 252/253 não existem — código truncado de 2523).
7. Após gerar o TXT: mesmo tamanho de registro (01=55, 02=165, 03=664, 05=138, 99=100), cp1252 + CRLF, nenhum CC numérico remanescente, passivos fechando com o extrato.

## Erros recorrentes da integração da Filial (verificar primeiro — 05 e 06/2026)

| CC | Rubrica | Como vem | Correto |
|---|---|---|---|
| 5 | 8781 Dias normais | D 2323 / C 2323 | D 2323 / C 2521 |
| 5 | INSS patronal (aba Empresa) | D 3143 | D 2332 |
| 5 | 690 Contrib. assistencial | C 2867 | C 3148 |
| 7, 13 | 8797 Bolsa auxílio | C 2521 | C 2526 |
| 7 | 8813 Bolsa dias afastamento | D 2884 / C 2521 | D 2910 / C 2526 |
| 8 | 690 Contrib. assistencial | C 2905 | C 2923 |
| 8 | 8870 Afast. doença | D 2521 / C 2900 (invertido) | D 2891 / C 2521 |
| 8 | Férias (8783, 931, 805, 806) / 812 INSS férias | 3017 / não exportado | D 3152 / C 2524; INSS D 2524 / C 2531 |
| todos | 937 Adiantamento de férias | não exportado | D 2524 / C 2463 |
| 8 (rescisão) | 8551 médias 13º, 302 HE | C 252 / C 253 | C 2523 |
| 9 | 302/250 Horas extras | D 2577 | D 3151 |
| 9 | 690 Contrib. assistencial | C 3148 | C 2911 |
| 14 | 690 Contrib. assistencial | D 3080 / C 2521 (invertido) | D 2521 / C 3080 |
| 13 | 8781 histórico | "DESC VALE REFEIÇÃO" | "DIAS NORMAIS" (só histórico) |
| 5 | 302 histórico | "HORAS EXTRAS 50%" | "HORAS EXTRAS 75%" (só histórico) |

Rescisões inteiras podem não sair no TXT (06/2026: Antônio Henrique, CC 7, demitido em 30/06) — conferir cada funcionário "Demitido" do extrato. O FGTS da rescisão está no "Valor FGTS" da linha do funcionário e no "Valor FGTS Rescisório" do total do extrato (fica fora do "Valor do FGTS" geral).

No Domínio a integração é por **centro de custo → lançamento (conta débito, conta crédito, histórico) → rubricas selecionadas**; abas Folha (rubricas), Rescisão, Empresa (encargos patronais), Provisão de Férias/13º etc. A planilha de correções indica CC + rubrica + aba para o usuário corrigir lá.

## Formato das planilhas

**Correções** (uma linha por CC + rubrica, com o CC como aparece no extrato): Valor · CC Domínio · Rubrica (código - nome do extrato) · Aba Domínio · Débito atual · Crédito atual · Débito sugerido · Crédito sugerido · Já ocorreu no mês anterior? · Nota · **Corrigido?** (Sim/Não, amarelo) · **Observação** (amarelo). Rodapé: total (fórmula) e "Corrigidos: X de N". "Não lançado" quando a rubrica não saiu no TXT; "Confirmar" (laranja) quando depende do usuário. Simples, sem poluição.

**Fechamento patrimonial** — contas 2521, 2523, 2524, 2526, 2530, 2531, 2533, 3137, 2463 (sem contas de resultado). Aba "Resumo" (contas × meses) + uma aba por mês com: Valor pela folha (extrato) · Valor no TXT · Diferença · Ajustes identificados · TXT após ajustes · Confere? · Composição dos ajustes. Valores = movimento do mês (crédito − débito).

## Scripts (`scripts/`)

- `extrato.py <extrato.xlsx> <saida.pkl>` — estrutura o extrato e imprime totais por CC.
- `txt_dominio.py <Folha.txt> [140|145]` — lista os lançamentos (seq, data, débito, crédito, valor, histórico, empresa).
- `gera_txt_korp.py <Folha.txt> <config.json> <saida.txt>` — gera o TXT da empresa: filtra pelo código, corrige contas por seq, exclui/inclui lançamentos, monta os 05 (Filial por blocos de seq; Matriz por `cc_map`), renumera e troca o cabeçalho. Ver docstring para o formato do `config.json`.
- `planilhas.py correcoes|fechamento <json> <saida.xlsx>` — gera as duas planilhas no padrão acima.

Dependências: `openpyxl`, `python-calamine` (`pip install python-calamine` se faltar).

## Layout do TXT (Domínio — lançamentos contábeis)

- Codificação **Windows-1252 (ANSI)**, quebras de linha **CRLF**. Nunca converter para UTF-8.
- `01` cabeçalho (código empresa col. 3–9, CNPJ col. 10–23) · `02` lote (data/usuário) · `03` lançamento (seq 3–9, débito 10–16, crédito 17–23, valor 24–38 com 2 decimais implícitas, histórico a partir da 46, código da empresa 558–564) · `05` rateio de CC (seq 3–9, CC débito 10–16, CC crédito 17–23, valor 24–38) · `99` trailer.
