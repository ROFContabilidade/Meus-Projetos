---
name: "rof-contabilidade-folha-korp"
description: "KORP INFORMÁTICA — Matriz (Domínio 140, CNPJ 03.623.045/0001-00) e Filial (Domínio 145, CNPJ 03.623.045/0002-91): avalia a folha exportada do Domínio contra o extrato mensal e o plano de contas Korp e entrega sempre 3 arquivos — planilha de correções da integração, planilha de fechamento das contas patrimoniais e o TXT corrigido (com centros de custo Korp CC337, CC345, CC379, CC506, CC644, CC320) para importar na Korp. Usar quando mencionarem Folha Korp, Korp Matriz/Filial, TXT da folha, extrato da folha, centro de custo Korp ou retorno de erro da Korp."
---

# ROF Contabilidade — Folha Korp (Domínio → Korp)

Use quando Everton/Rosangela enviarem o TXT da folha exportado do Domínio para a KORP INFORMÁTICA LTDA EPP (Matriz ou Filial), o extrato da folha, o balancete, ou o retorno de erro da Korp (`Problemas_Importacao_DOMINIO.txt`, ex.: "Centro de Custo: 000000X Não cadastrado no Sistema").

## Entregas padrão (sempre as 3, para Matriz e Filial)

1. **Planilha de correções** da integração no Domínio — `Integracao_Dominio_Korp_<Empresa>_MM-AAAA.xlsx`
2. **Planilha de fechamento das contas patrimoniais** — `Fechamento_Folha_Korp_<Empresa>_MM-AAAA.xlsx` (um arquivo por mês)
3. **TXT corrigido** — `Folha_Korp_<Empresa>_MM-AAAA.txt` (só a empresa em questão)

**Quando os erros restantes forem poucos** (ex.: 09/2026: 2 obrigatórios + 2 avisos) e o TXT já tiver sido gerado/importado, a usuária pode pedir só a **planilha de lançamentos a corrigir manualmente** (`Korp/Correcoes_Manuais_Folha_Korp_MM-AAAA.xlsx`): empresa, Seq do registro 03, data, débito/crédito atual, valor, histórico, CC, débito/crédito correto, ação (excluir / trocar conta / conferir), motivo, e colunas amarelas "Corrigido?" e "Observação". Aba "Conferência" com os saldos patrimoniais depois das correções.

**Planilhas sempre com valores já calculados** (o visualizador do app/Drive não calcula fórmulas; só o contador "Corrigidos: X de N" é fórmula). **Não gravar abas dentro do `Extrato Mensal` do Domínio** — o fechamento é arquivo próprio.

**Cada mês é separado — não misturar meses.** Os 3 arquivos de cada mês ficam em `Korp/<Matriz|Filial>/<AAAA-MM>/` no repositório; fazer commit/push e enviar os arquivos ao usuário (SendUserFile). O TXT não vai para o Google Drive pelo conector (tamanho + precisa manter ANSI).

O TXT de um mês pode trazer lançamentos de competência de outro mês (rescisão com demissão no último dia exportada no mês seguinte; férias pagas no fim do mês para gozo no mês seguinte; rescisão que só sai no TXT do mês seguinte). **Não mover lançamentos entre TXTs**: o TXT corrigido de cada mês contém o que o Domínio exportou naquele mês (com as contas corrigidas). Na planilha de fechamento esses valores ficam na coluna "Competência de outros meses", e na planilha de correções como nota.

Antes de gerar o TXT, **avaliar os lançamentos e apresentar as correções**; perguntar só o que não dá para decidir (CC novo, lançamento sem origem no extrato, conta inexistente no grupo). Não inventar conta nem centro de custo.

## Passo a passo de cada mês (Matriz e Filial)

1. **Pedir/receber:** TXT do Domínio (`Folha.txt`, vem com Matriz 140 e Filial 145 juntas) e balancete do mês (`Balancete_MM.AA.xls`). **Buscar no Google Drive** o extrato da folha: `Filial_Extrato Mensal_MM.AA.xlsx` / `Matriz_Extrato Mensal_MM.AA.xlsx` (pasta Korp, id `1qjpoKwo5uI4PtIKBkCLpuE7tf9h6tNcY`; o xlsx vem em base64 — salvar a resposta em arquivo e decodificar com `python -I`). Pedir também a **Relação de Rescisões Calculadas** da Matriz e da Filial (período = mês anterior + mês; é o que mostra quem foi demitido e não saiu no TXT) e ter à mão o **Extrato Mensal do mês anterior** (detalhe das verbas das rescisões que atrasaram).
2. **Separar a empresa** pedida (colunas 558–564 do registro 03) — nunca misturar Matriz e Filial.
3. `scripts/extrato.py` no extrato e `scripts/txt_dominio.py <Folha.txt> 145|140` no TXT; mapear os blocos de CC (Filial) e comparar funcionário × rubrica × conta.
4. **Primeiro verificar a tabela de erros recorrentes** (abaixo) e as **pendências do mês anterior** (seção Histórico); depois procurar erros novos: conta errada para o grupo, lançamento invertido, conta inexistente, rubrica que não saiu, rescisões/férias/adiantamentos.
5. Apresentar as correções e perguntar só o que não dá para decidir. Registrar aqui toda decisão nova do usuário.
6. Montar `txt_config.json`, `correcoes.json`, `fechamento.json` e gerar as 3 entregas (`gera_txt_korp.py`, `planilhas.py`). Conferir: CC nos 2 lados, simulação do que a Korp grava = coluna "TXT corrigido" do fechamento, "Confere? = Sim" em todas as contas.
7. Salvar em `Korp/<Empresa>/<AAAA-MM>/` (as 3 entregas) e `.../config/` (os 3 JSON + `Folha_Dominio_original.txt`), commit/push, enviar os arquivos (SendUserFile) e **atualizar a seção Histórico** desta skill com status e pendências.

## REGRA OBRIGATÓRIA — centro de custo nos DOIS lados de TODO lançamento (Matriz e Filial)

**A Korp só grava o lado do lançamento que tem registro 05 (centro de custo).** Lado sem 05 = valor que não entra na Korp. Confirmado em 09/2026: Filial 05/2026 importada sem CC nas contas 2530/2531/2533/3137 → a Korp gravou só os débitos (ex.: lançamento 150672 com D 2885 56,80 e sem o C 2531) e ficaram de fora os créditos de FGTS, INSS, IRRF e consignado; Matriz 08/2026 → 3 lançamentos sem nenhum 05 tiveram de ser lançados à mão.

Vale igualmente para **Matriz e Filial**, em todo TXT gerado:
1. Cada registro 03 leva **dois** registros 05: um com o CC no lado débito e outro com o CC no lado crédito.
2. **Todas as contas** levam CC — inclusive **2530 FGTS, 2531 INSS, 2533 IRRF, 3137 consignado**, 2521, 2523, 2524, 2526 e 2463.
3. O lado que vem **sem CC do Domínio** herda o CC do outro lado do mesmo lançamento (ex.: D 2885 CC337 / C 2531 CC337). Na Matriz o Domínio manda o CC só de um lado nesses lançamentos — completar sempre.
4. Lançamento que o Domínio exporta **sem nenhum 05** (ex.: compensação de salário-maternidade D 2531 / C 2996; INSS de rescisão D 2523 / C 2531): dar o CC do funcionário/bloco (`cc_seq` no config; se não houver, o gerador herda do lançamento vizinho e imprime AVISO — conferir).
5. Completar o CC **não altera valor nenhum**: ao regerar um TXT já entregue, comparar com a versão anterior — mesmos lançamentos 03 (contas, valores, datas, históricos, cabeçalho) e só registros 05 a mais. Os saldos de 2530/2531/2533/3137 na Korp sobem porque passam a entrar, não porque mudaram.
6. Se um TXT já foi importado sem esses 05: o preferido é **apagar a importação na Korp e subir o TXT completo corrigido** (feito em 05/2026 da Filial). Se não der para apagar, gerar o **complemento** (`"complemento": [contas]` no `gera_txt_korp.py`), que traz só os lados que faltaram — nunca reimportar o TXT inteiro por cima.

O `scripts/gera_txt_korp.py` já aplica os itens 1–4 automaticamente para as duas empresas.

## Empresas

| | Matriz | Filial |
|---|---|---|
| Código Domínio | 0000140 | 0000145 |
| CNPJ (registro 01) | 03623045000100 | 03623045000291 |
| Registro 05 (CC) no TXT do Domínio | vem com CC 1–6, mas só de um lado em FGTS/INSS/IRRF/consignado e às vezes ausente — completar os dois lados | **não vem** — reconstruir os dois lados |

O Domínio exporta **um único TXT com as duas empresas** sob o cabeçalho da Matriz. O código da empresa está no final do histórico do registro 03 (**colunas 558–564**). Separar por empresa e gerar um TXT para cada, com o cabeçalho (código + CNPJ) da própria empresa.

## Fontes de dados

| Arquivo | Onde | Como ler |
|---|---|---|
| Extrato Mensal da folha (`Filial_Extrato Mensal_MM.AA.xlsx` / `Matriz_Extrato Mensal_MM.AA.xlsx`) | Google Drive, pasta Korp (buscar pelo título; baixar com `download_file_content` e decodificar o base64) | `scripts/extrato.py` — CC, funcionário, rubrica (código, nome, P/D), encargos por CC |
| TXT da folha (`Folha.txt`) | anexo do usuário | `scripts/txt_dominio.py` — registros 02/03/05, cp1252 |
| Relação de Rescisões Calculadas (`Relação de Rescisões Calculadas.xls`, uma por empresa) | anexo do usuário | LibreOffice `--convert-to xlsx` + openpyxl; só totais por pessoa |
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
| 1 | GERAL (estagiário, contas do ADM) | CC320 |
| 14 | QUALIDADE | CC506 |

CC novo sem de-para: não inventar — perguntar ao usuário e acrescentar aqui.

**Formato:** código Korp alinhado à esquerda com espaços até 7 caracteres (`CC337  `). Cada lançamento 03 leva **dois** registros 05: um com o CC no lado débito (col. 10–16, crédito `0000000`) e outro com o CC no lado crédito (col. 17–23, débito `0000000`) — ver a REGRA OBRIGATÓRIA acima.

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
- Reembolso (617) pago ao funcionário do Suporte na folha: **D 2891 / C 2521** (mantido).
- Vale-refeição não utilizado (657) na rescisão do Suporte (CC 8): **D 2523 / C 3146** (Ajuda de Custo do Suporte).
- Rescisão: proventos (saldo, aviso, férias, 13º, médias, HE, ajuda) a crédito de **2523** — mesmo quando o Domínio manda para 2521/2524/2525; descontos da rescisão (contribuição, faltas, VR/VA/ajuda não utilizados, INSS) a débito de **2523**. FGTS da rescisão (inclusive de aviso prévio) C **2530**.
- VR/VA/ajuda de custo não utilizados na rescisão: **D 2523 / C Ajuda de Custo do grupo** (DES 2888; Suporte 3146).
- Consignado (crédito do trabalhador) com provisão/estorno (9752/9754) e "PROVISAO DESC. EMP. CRED. TRAB." no cálculo de férias: **excluir do TXT** a provisão e o estorno; manter só os descontos efetivos (9750/9751, 714/717/721/730) — o 3137 tem de fechar com o extrato (confirmado em 08/2026).
- Diferença de férias paga na folha (940/8112/8189): D conta de férias do grupo / **C 2521**.
- **Consignado com estorno sem provisão (Filial, 09/2026):** excluir só o estorno (D 3137 / C 2521 459,65); o 3137 do mês tem de ser Σ dos descontos efetivos. (A anotação anterior de "manter o estorno em 09" estava errada.)
- **Adiantamento de férias (937) de férias pagas em mês anterior:** não relançar (baixa já feita no TXT daquele mês); fica no fechamento como "competência de outros meses" negativa (09/2026: Matheus e Ana, 3.542,61 na Filial).
- **Adiantamento salarial na rescisão (695 "VALE")**: D 2523 / C 2464.
- **Aviso prévio reavido (rubrica 49, pedido de demissão sem cumprir aviso):** desconto da rescisão, D 2523 / C salário do grupo.
- **Rescisão do comercial com 2900/2924 (Qualidade):** manter as contas do Domínio e o CC do funcionário; só avisar e sugerir corrigir no Domínio.
- **Matriz — CC pelo número do registro 05, não pelo CC do extrato** (a numeração do extrato é outra: DES WEB e DES BACKOFFICE = Desenvolvimento → CC337).
- **VA diferença CCT (25/09):** fora do extrato mensal; manter no TXT e anotar como "outros cálculos".

## Conferência obrigatória (extrato × TXT × balancete)

Com `scripts/extrato.py` somar por CC/funcionário/rubrica e comparar com o TXT da empresa:

1. Proventos e descontos totais do extrato (o "Resumo por Rubrica" fecha com a soma por funcionário).
2. **Líquido:** 2521 + 2524 + 2526 = Líquido Geral do extrato (a rubrica 51 LIQUIDO RESCISAO aparece como desconto; o líquido das rescisões vai para 2523).
3. INSS 2531 = "Total INSS" do extrato (segurados + empresa + RAT + terceiros + férias/rescisão). Diferença de centavos por arredondamento por CC é aceitável (≤ R$ 1).
4. FGTS 2530 = "Valor do FGTS"; conferir o FGTS rescisório à parte. IRRF 2533; consignado 3137 (rubricas 714/717/721/730/9750); adiantamento de férias 2463 (937).
5. Toda rubrica do extrato tem lançamento no TXT (procurar férias, rescisões e adiantamentos que não saíram).
6. Toda conta do TXT existe no plano Korp (ex.: 252/253 não existem — código truncado de 2523).
7. Após gerar o TXT: **todo lançamento com 05 nos dois lados (Matriz e Filial)**; simular o que a Korp grava (somar só os lados com 05) e bater com o fechamento; mesmo tamanho de registro (01=55, 02=165, 03=664, 05=138, 99=100), cp1252 + CRLF, nenhum CC numérico remanescente, passivos fechando com o extrato.

8. **3137 consignado = Σ dos descontos efetivos do extrato** (9750/9751 e 714/717/721/730), nunca depois de provisão/estorno: 9752 (provisão) e 9754 (estorno) se anulam no extrato. Se o Domínio exportar o estorno **sem** a provisão (09/2026, Filial, Ana: D 3137 / C 2521 459,65), **excluir o estorno**. Se o lançamento D 3137 / C 2521 não tiver provisão correspondente nem for estorno (09/2026, Matriz, Maria Fernanda 1.234,27), conferir contra o extrato: se o saldo só fecha invertendo, é desconto invertido → D 2521 / C 3137.
9. **Cada rescisão da Relação de Rescisões Calculadas** (proventos, descontos, líquido, FGTS rescisório) precisa bater com os lançamentos: proventos = créditos em 2523 de despesa; descontos = débitos em 2523; líquido = saldo de 2523; FGTS = créditos em 2530.
10. **Conta de despesa × CC:** conferir cada lançamento de despesa contra o grupo do CC (tabela "Grupos de contas"). Exceção conhecida e só avisada: rescisão do comercial que o Domínio exporta com 2900/2924 (Qualidade) — manter o CC do funcionário.

## Erros recorrentes da integração da Filial (verificar primeiro — vistos de 05 a 08/2026; enquanto o Domínio não for corrigido, repetem todo mês)

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

Erros novos em 07/2026 (Filial):

| CC | Rubrica | Como vem | Correto |
|---|---|---|---|
| 5 | 853 Reflexo comissões DSR | C 2524 | C 2521 |
| 5 | 940/8112/8189 Diferença de férias | D 2867 / C 2524 | D 2576 / C 2521 |
| 5, 8 | 812 INSS férias (cálculo de férias) | C conta de despesa (2576/3017) | C 2531 |
| 8 | Férias pagas no fim do mês (cálculo de férias) | D 3017 | D 3152 |
| 7 (rescisão) | 250 Reflexo extras DSR | D 2905 | D 2904 |
| 10 | 8490/8496 Bolsa auxílio férias (rescisão estágio) | D 3017 / C 2524 | D 2995 / C 2526 |
| 16 | 8490/8496/8797 (rescisão estágio) | D 3146 / C 2521 | D 2910 / C 2526 |

Erros novos em 08/2026 (Filial): rescisão (CC 7) com verbas creditadas em 2521/2524/2525; INSS da rescisão (826) D 2885; VR não utilizado (657) D 2888 / C 2934 (invertido e em conta da Qualidade); FGTS de aviso prévio C 2533 (IRRF); conta **2855** inexistente no INSS patronal (é 2885); FGTS férias D 2885 (é 2886); horas extras do ADM (CC 10) C 2524; adiantamentos de férias (937) não exportados; consignado com provisão/estorno lançados no cálculo de férias.

Erros novos em 09/2026 (Filial): salário do CC 5 (Bruno) D 2323 / **C 2531** (é C 2521); afastamento por doença do DES D 2521 / C 2884 invertido; INSS terceiros 13º do ADM C 2521 (é 2531); rescisão da Isabele (CC 10) com INSS em D 2998, verbas em 2521/2524/2525 e VR/multa de estabilidade em D 2521 (tudo em 2523); bolsa afastamento do estagiário C 2521 (é 2526); ajuda de custo dos estagiários C 2521 (é 2526, dividir quando o bloco mistura CLT); consignado da Ana com estorno e **sem** a provisão (excluir o estorno); adiantamento salarial da rescisão do Enzo (rubrica 695 "VALE") lançado D 2464 / C 2521 (é D 2523 / C 2464); FGTS de aviso prévio C 2533 (é 2530).

Erros novos em 09/2026 (Matriz): rescisão do Augusto com verbas em 2521/2524/2525 (→ 2523), FGTS de rescisão e de aviso prévio C 2533 (→ 2530), IRRF 13º da rescisão D 2525 / C 2531 (→ D 2523 / C 2533); FGTS de férias C 2533 (→ 2530) e com débito em 2885 (→ 2886); INSS de férias C 2885 (→ C 2531) ou D 2885 (→ D 2524); horas extras 100% D 2521 / C 2917 invertidas; VT D 3144 / C 2521 invertido; desconto troco de férias D 2524 / C 2907 (→ D 2521); média horas férias D 2524 / C 3098 invertida; desconto consignado D 3137 / C 2521 invertido (ver conferência 8); 5 lançamentos sem `05` (INSS/IRRF da rescisão e compensação do salário-maternidade) — completar com o CC do funcionário (rescisão do Augusto: CC337; compensação: CC320).

Rescisões inteiras podem não sair no TXT (06/2026: Antônio Henrique, CC 7, demitido em 30/06) — conferir cada funcionário "Demitido" do extrato. O FGTS da rescisão está no "Valor FGTS" da linha do funcionário e no "Valor FGTS Rescisório" do total do extrato (fica fora do "Valor do FGTS" geral).

## Rescisões de meses anteriores que o Domínio não exportou (aprendido em 09/2026)

1. A **Relação de Rescisões Calculadas** (período de 2 meses) lista quem foi demitido. Para cada demitido, procurar a rescisão no TXT do mês; se não estiver, **procurar no TXT já importado do mês da demissão** (ex.: Kelyanne, Matriz, demitida em 28/08, já estava no TXT de 08 — **não** relançar em 09) e só então tratar como pendente.
2. A relação traz só **totais** (proventos, descontos, líquido, FGTS rescisório). O **detalhe das verbas** vem do **Extrato Mensal do mês da demissão** (Drive): seção de cada funcionário "Demitido" (rubricas P/D) e o "Resumo por Rubricas do Centro de Custo". Em CC com mais de um demitido o Domínio exporta as verbas **somadas por CC** (Enzo + Wellington, CC 8): aceitável, o resultado contábil é o mesmo.
3. Montar: D despesa do grupo / C 2523 (proventos); D 2523 / C conta do desconto (INSS 826/989 → 2531, consignado 714/717/721/730 → 3137, adiantamento 695 → 2464, VR/ajuda não utilizados → ajuda de custo do grupo); FGTS D despesa / C 2530. CC pelo extrato (CC 4 COM → CC379; CC 8 → CC345). Lançar no TXT do mês em que o Domínio exportou (ou no mês que o usuário definir) e tratar como "competência de outros meses" no fechamento.
4. Validar sempre: proventos, descontos, líquido, FGTS e INSS por pessoa/CC contra a relação **e** contra o extrato (conferência 9).
5. Se o INSS patronal (Empresa/Terceiros/RAT) do CC no extrato do mês da demissão já bate com os lançamentos do TXT daquele mês, não falta patronal da rescisão.

No Domínio a integração é por **centro de custo → lançamento (conta débito, conta crédito, histórico) → rubricas selecionadas**; abas Folha (rubricas), Rescisão, Empresa (encargos patronais), Provisão de Férias/13º etc. A planilha de correções indica CC + rubrica + aba para o usuário corrigir lá.

## Histórico e status (atualizar a cada mês)

**Filial (145)** — arquivos em `Korp/Filial/<AAAA-MM>/`; configs para regerar em `.../config/` (regerar com `gera_txt_korp.py config/Folha_Dominio_original.txt config/txt_config.json saída.txt` reproduz o TXT entregue byte a byte).

| Mês | Situação | Observações |
|---|---|---|
| 05/2026 | TXT corrigido **reimportado** na Korp (a 1ª importação, sem CC em 2530/2531/2533/3137, foi apagada) | Férias da Atalia e adiantamentos de férias (Ana, Atalia, Fernanda) incluídos; Fernanda com férias lançadas em 3017 → 3152 |
| 06/2026 | TXT corrigido entregue (CC nos 2 lados) | Horas extras 100% do Bruno (165,36 + DSR 39,37) mantidas por decisão, apesar de fora do extrato; rescisão do Antônio Henrique (competência 06) saiu no TXT de 07; VR não utilizado do CC 8 → C 3146 |
| 07/2026 | TXT corrigido entregue | Contém a rescisão do Antônio (09/07, competência 06) e as férias da Fernanda pagas em 31/07 (gozo em 08); faltou a rescisão de estágio da Isabele (veio no TXT de 08); reembolso 617 mantido em 2891; CC 1 GERAL = CC320 |
| 08/2026 | TXT corrigido entregue | Consignado da Ana: estorno (459,65) e provisão de férias (919,30) excluídos; rescisão Alyson/Wendel reclassificada para 2523; adiantamentos (Matheus, Ana, Fernanda) incluídos; Isabele recontratada em 03/08 como celetista no CC 10 (contas ADM 2994/2996/2997/3144) |
| 09/2026 | TXT da outra SKILL (231 lançamentos, CC nos 2 lados) validado; **2 correções manuais** (planilha `Korp/Correcoes_Manuais_Folha_Korp_09-2026.xlsx`) + 2 avisos | Rescisões de agosto (Guilherme CC379, Enzo/Wellington CC345) entraram no TXT de 09 com detalhe do Extrato 08.26 (líquido 24.700,80, FGTS 4.254,19, INSS 1.023,65, consignado do Enzo 2.416,71, adiantamento 1.769,67 em 2464); Isabele (rescisão 03/09, líquido 0,00) em 2523; excluir o estorno do consignado da Ana (seq 510); avisos: Guilherme com 2900 (3,00) e 2924 (251,00) |

**Pendências para 10/2026 (Filial) — conferir no TXT de outubro:**
- Confirmar se as correções manuais de 09 foram feitas na Korp (estorno da Ana excluído) — o 3137 de 09 tem de ficar em 3.811,33 (folha 1.394,62 + Enzo 2.416,71, competência 08).
- Férias do **Matheus** e da **Ana** (pagas em 08 e 09) e qualquer férias paga no fim de 09 com gozo em 10: não duplicar baixas de adiantamento (conferência acima).
- Pedir a **Relação de Rescisões Calculadas** (09 e 10) e conferir cada demitido contra o TXT de 10 e contra o TXT já importado de 09 antes de dar como pendente.
- Integração do Domínio ainda com os erros recorrentes (tabelas acima) — verificar se a usuária já corrigiu na origem; os erros novos de 09 estão listados.
- Isabele (CC 10, ADM) saiu em 03/09 — não deve haver lançamentos dela em 10.

**Matriz (140)** — extratos no Drive: `Matriz_Extrato Mensal_05.26/06.26/07.26/08.26/09.26.xlsx`.

| Mês | Situação | Observações |
|---|---|---|
| até 08/2026 | Importados na Korp pelo padrão antigo (só troca de CC 1–6 → Korp) | Contrapartidas sem CC não entraram e foram **lançadas à mão** pela usuária — **não gerar complemento** para esses meses (duplicaria) |
| 08/2026 | `Folha_Korp_140_corrigida.txt` (cópia em `Korp/Matriz/2026-08/config/`) | 248 de 251 lançamentos com CC nos 2 lados; 3 sem nenhum 05 ficaram fora e foram lançados à mão: compensação de salário-maternidade D 2531 / C 2996 8.124,60 (CC644) e INSS de rescisão D 2523 / C 2531 319,41 + 230,81 (CC337). Observação a revisar: rescisão com conta 3012 (Provisões Qualidade) e CC337 (Desenvolvimento) — conta e CC de grupos diferentes |
| 09/2026 | TXT da outra SKILL (291 lançamentos, CC nos 2 lados, sem divergência do CC do Domínio) validado; **1 correção manual** (seq 1062, FGTS de férias D 2885 → D 2886, 25,35) | Rescisão do Augusto (DES WEB, CC337, 30/09): líquido 34.579,17 = saldo de 2523; FGTS rescisório 10.204,15; descontos 3.621,61. Consignado: lançamento D 3137 / C 2521 1.234,27 era desconto invertido (3137 = 2.427,67 = extrato). Compensação do salário-maternidade 4.062,30 → CC320. **Kelyanne** (demitida 28/08) já estava no TXT de 08 — não pendente; em 08 as verbas ficaram em 2524/2525/2521 (padrão antigo), então o líquido 9.352,58 não aparece em 2523 na Korp (reclassificação opcional, não feita) |
| 10/2026 em diante | Gerar pelo padrão completo (3 entregas) com `cc_map` 1–6 e CC nos dois lados | Config de exemplo: `{"empresa":"0000140","cnpj":"03623045000100","cc_map":{"0000001":"CC337","0000002":"CC506","0000003":"CC345","0000004":"CC644","0000005":"CC320","0000006":"CC379"}}` |

## Formato das planilhas

**Correções** (uma linha por CC + rubrica, com o CC como aparece no extrato): Valor · CC Domínio · Rubrica (código - nome do extrato) · Aba Domínio · Débito atual · Crédito atual · Débito sugerido · Crédito sugerido · Já ocorreu no mês anterior? · Nota · **Corrigido?** (Sim/Não, amarelo) · **Observação** (amarelo). Rodapé: total (valor) e "Corrigidos: X de N" (fórmula). "Não lançado" quando a rubrica não saiu no TXT; "Confirmar" (laranja) quando depende do usuário. Simples, sem poluição.

**Fechamento patrimonial** (um arquivo por mês) — contas 2521, 2523, 2524, 2526, 2530, 2531, 2533, 3137, 2463 (sem contas de resultado). Colunas: Valor pela folha (extrato do mês) · Valor no TXT do Domínio · Correções de conta · TXT corrigido (lançado na Korp) · Competência de outros meses no TXT · Confere? (folha + outros meses = TXT corrigido, tolerância R$ 1) · Composição. Valores = movimento do mês (crédito − débito).

## Scripts (`scripts/`)

- `extrato.py <extrato.xlsx> <saida.pkl>` — estrutura o extrato e imprime totais por CC.
- `txt_dominio.py <Folha.txt> [140|145]` — lista os lançamentos (seq, data, débito, crédito, valor, histórico, empresa).
- `gera_txt_korp.py <Folha.txt> <config.json> <saida.txt>` — gera o TXT da empresa: filtra pelo código, corrige contas por seq, exclui/inclui lançamentos, monta os 05 (Filial por blocos de seq; Matriz por `cc_map`), renumera e troca o cabeçalho. Ver docstring para o formato do `config.json`.
- `planilhas.py correcoes|fechamento <json> <saida.xlsx>` — gera as duas planilhas no padrão acima.

As planilhas gravam **valores já calculados** (não fórmulas): o visualizador do app/Drive não calcula fórmulas e mostrava as colunas vazias. Só o contador "Corrigidos: X de N" é fórmula.

Dependências: `openpyxl`, `python-calamine` (`pip install python-calamine` se faltar).

## Layout do TXT (Domínio — lançamentos contábeis)

- Codificação **Windows-1252 (ANSI)**, quebras de linha **CRLF**. Nunca converter para UTF-8.
- `01` cabeçalho (código empresa col. 3–9, CNPJ col. 10–23) · `02` lote (data/usuário) · `03` lançamento (seq 3–9, débito 10–16, crédito 17–23, valor 24–38 com 2 decimais implícitas, histórico a partir da 46, código da empresa 558–564) · `05` rateio de CC (seq 3–9, CC débito 10–16, CC crédito 17–23, valor 24–38) · `99` trailer.
