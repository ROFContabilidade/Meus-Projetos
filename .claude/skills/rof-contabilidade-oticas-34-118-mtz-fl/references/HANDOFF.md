# Passagem de bastão (estado em 18/11/2026, motor escrito e rodado no fim do dia)

Leia este arquivo inteiro antes de qualquer ação. Ele resume a sessão "Otica visoluz" (que fez a matriz e criou a ligação)
e a sessão "VisouUP" (que fez a filial 07-09). As duas foram encerradas e daqui em diante tudo é feito por esta skill.

## 1. Quem é quem
- **PJ única:** ADRIANA R. DE PAULA LTDA, CNPJ básico 24.026.777. Simples Nacional Anexo I, DAS único pago pela matriz.
  A Receita mostra exclusão do Simples em 31/12/2026 e há um planejamento de Lucro Presumido na pasta. Confirmar o regime de 2027.
- **Matriz = empresa 34** (0001-93), Sicredi 44846-8 (conta 8). Itaú 0098929-8 (conta 9) inativo no Domínio desde 28/07/2026. Tem folha (6 empregados).
- **Filial = empresa 118** (0002-74, "Ótica VisouUP"), Itaú 3702/98896-9 (conta 8). Sem folha. Contabilidade separada (descentralizada).
- Sócia Adriana Rodrigues de Paula (CPF final -42). Pró-labore 1.621,00 bruto / 1.442,69 líquido (folha da 34).
- Ótica Visoluk (49.192.337/0001-37), de Pedro Jefferson Luiz: mútuo (152 na 34; 166 na 118).

## 2. O que já foi feito
- Skills: `rof-contabilidade-otica-visoluz` (34) neste repositório, branch `claude/upbeat-bohr-9mmted`. Tem um classificador que
  funciona (`scripts/classificar_visoluz.py` + `references/regras.json`) e serve de base para o motor desta skill. A skill da filial
  (`rof-contabilidade-otica-visouup`, branch `claude/bold-einstein-fmzmcg`) será apagada.
- **TXT provisórios 07-09/2026 da matriz** gerados e entregues (com a regra da 544, os espelhos da filial e o controle da 506).
  Extratos Sicredi fecham: 07 -1.802,79 → -2.125,56; 08 → 8.520,47; 09 → -2.267,37. Saldo inicial igual ao razão em 30/06.
- **TXT 07-09 da filial** feitos pela sessão VisouUP (v2, no Drive em 118/2026/Relatorios Claude). Fecham com o Itaú:
  324,60 → 19,78 → 543,97 → 539,49. Usam a **152** para a ligação: precisam ser refeitos com a **544**.
- Decisões da contadora: `references/decisoes.md` (todas as perguntas foram respondidas em 18/11/2026).
- **Decidido refazer o banco de 01 a 09/2026 nas duas empresas** com esta skill (TXT completo por mês; no Domínio apagar só os
  lançamentos de banco; folha e fiscal ficam).

## 3. Achados que motivaram o refazimento (razão 01-06)
- 34: salários pagos por PIX lançados em 362/527 com a folha já lançando o salário (despesa em dobro; 362 R$ 137,8 mil; 187 credora R$ 66,5 mil).
- 34: 24 transferências Itaú→Sicredi lançadas como 504 (Sicredi) e 362/527 (Itaú): R$ 53.992,20. 17 PIX da filial na 504: R$ 30.130,00.
- 34: Hoya e Visoluk pagos direto em 470 (custo em dobro); adiantamento D25 no banco com a folha também D25/C5 (caixa 5 credor R$ 32,7 mil).
- 118: pagamentos de fornecedor (SISPAG) em 527 (R$ 70,8 mil) com a 506 nunca baixada; despesas da matriz em 362/192.
- Ambas: 504 credora (recebe mais do que fatura): risco Lei 9.430 art. 42. 34: 538 R$ 1,2 milhão e estoque "produtos acabados/em elaboração" vêm de anos anteriores (precisa do balancete 2025 e de decisão sobre a conta 528).
- Encargos em aberto (relatório 18/11): FGTS 06-11/2026, consignado Crédito do Trabalhador descontado e não repassado (R$ 2.508,06), tributos federais 06. DAS 06 e 08 sem pagamento.

## 4. Pendências abertas (pedir/acompanhar)
1. **Conta da matriz sem extrato:** a Rosangela está perguntando à Adriana (18/11). Evidências: a filial recebeu PIX do CNPJ 0001-93
   que não saem do Sicredi (07: 13/07 416,19; 13/07 1.250,89; 20/07 637,50; 27/07 1.536,19; 29/07 210,80 = 4.051,57 |
   08: 03/08 170,00; 12/08 512,06; 19/08 1.461,82; 26/08 760,93; 27/08 314,50; 31/08 428,00 = 3.647,31 |
   09: 09/09 241,23; 14/09 188,63; 17/09 943,98; 24/09 1.131,91; 28/09 178,99 = 2.684,74). Pela Receita, o DAS 07 (20/08) e
   o parcelamento de 31/07 (550,39 + 573,05) também foram pagos fora do Sicredi, assim como os salários de 07 (R$ 7.494,39).
   Quando o extrato chegar, essa conta entra como banco da 34 e os PIX à filial viram D 544 / C <banco>. Assim a 544 zera.
2. Relatório SISPAG do Itaú da filial 01-06: R$ 11.050 da ligação dentro de lotes (24/02 500; 12/03 2.900; 06/04 1.000; 13/04 250; 20/04 1.400; 18/05 1.000; 25/05 4.000).
3. Faturas do cartão Sicredi 01-09. Guias dos DARF sem par (seção "Propostas" de decisoes.md).
4. Confirmar a criação da conta 545 (cotas Sicredi) na 34. Até lá o motor trava nos meses com INTEGR.CAPITAL.
5. Shopping Popular pago pela filial: confirmar se é aluguel da matriz (espelho 34 D 320 / C 544).
6. Balancete 2025 da 34 (saldos de abertura: 538, estoque, 504).

## 5. Próximo passo (o que esta sessão deve fazer agora)
1. **Escrever `scripts/rotina_mes.py`** (motor único), partindo de `rof-contabilidade-otica-visoluz/scripts/classificar_visoluz.py`, que
   já faz: regras por texto/CPF; folha (líquido do mês anterior → 187; adiantamento → 5; janela 15-25 → 5; ≥200 → 187; pequeno → VA);
   sócia 188 até 1.442,69 e excedente 531; contas mantidas como no razão (`--manter 531,188,539` para a Reinf); guias da Receita
   separadas em principal, multa e juros (`--receita pagamentos_receita.csv`); controle da 506 (`--saldo-506 --notas-506`); espelhos da filial (`--filial`).
   O que falta: ler `estabelecimentos.json`, `contas_logicas.json` e `regras.json` (filtro por `estab`, conta `@logica`); processar as duas
   empresas no mesmo comando; parear as transferências 34↔118 (mesma data e valor) e as transferências entre contas da própria 34
   (Itaú↔Sicredi, uma vez só); gerar as duas pernas dos espelhos; e as **travas** abaixo.
2. **Travas (não gerar TXT se falhar):** (a) cada banco fecha com o extrato (saldo inicial = razão anterior; entradas/saídas iguais);
   (b) 544(34) + 544(118) = 0, ou a diferença 100% explicada na lista de pendências; (c) todo código existe como analítica no plano da
   empresa (`plano_34.csv` / `plano_118.csv`); (d) `|0000|` e nome do arquivo com o CNPJ/código certos; (e) nenhum movimento nos
   dois TXT fora as pernas da ligação; (f) 506 nunca devedora (por empresa); (g) meses em `reinf_travado`: 531 líquido igual ao declarado.
3. Saídas por mês: `34_VISOLUZ_AAAA-MM.txt`, `118_VISOUUP_AAAA-MM.txt` e `Conferencia_Mtz_Fl_AAAA-MM.xlsx` (abas Resumo/Travas,
   Matriz, Filial, Ligação 544, Pendências).
4. Rodar de **01/2026 a 09/2026** em ordem, encadeando os saldos (banco e 506). Fonte de 01-06 = movimentos de banco do razão
   (contas 8 e 9 da 34; conta 8 da 118), que já fecham com os extratos; 07-09 = `_extrato.md` do Conversor ROF.

## 6. Onde estão os arquivos (Google Drive, conector)
- Pasta 34: `34 - Otica Visoluz` id 1viVs0syBWej6FBX8CeryaXobA2AsL175; 2026 id 1DLIm7gHZjM1ttb8ZicmkZ1fqwzVm5dOT;
  Automoção Contabil id 1W00IJz_KoQeVxIWGkeD7sW3EgBXHXb-W (Contas.xls 1SdFURfopOezvnUeJQzFXKjBDwc8iuG6D; Razão.xls 01-09
  1_j4Rr4lkv8SecMTXASuyeB1RGxdP7Ej-; Extrato Mensal folha 01-09 10lVdY442vidnzKCHaUj9927IDD5rAEVo);
  Relatorio Claude (dentro de Automoção) id 1X7gDYJ3OZvwbVvf-Ccskks99AkIEx94z: Razão_Visoluz.xls até 10
  (133H_wlLJ03fWWePyNH6MH1Mvc7XC3tPo), Balancete até 10, Extrato Mensal 06-10, pagamentos_receita.pdf (1H-MSrmJzZ_-lCmc6LKJ1vgBfPhptoppL),
  Pagamento de Encargos, Resumo de impostos, GR-PR.
  Extratos Sicredi `_extrato.md`: 07 1coqo9goP9kjfHuFCnEei26WHzkB-o5N_; 08 14PHF-BzA1mjTHKk9P2bILTZTuK08vLYU; 09 1Hc_GppRS5mmYfH33wjoCYTmVxOxSD6WJ.
- Pasta 118: `118 - Otica VisouUP` id 10CnUDd-KudEhvIhbMfAKvCuaDvBOIbfJ; 2026 id 1Ufr-_xYJBMJHd5WkuWJ3pmTn73YPEkyZ;
  Relatorios Claude id 1HOcbaS1xhpZfFxKsPcTk-3f5r8NyqSfp (Plano de Contas.pdf, Razão.pdf 02-06, Balancete até 10, GR-PR).
  Extratos Itaú `_extrato.md`: 07 1tnw6jPfQp8QVt3T7t1z-CcBE1QfuWuRW; 08 1qoTfe5c8euEceV5NR3El2vmk7i5trN_f; 09 15YzW21_CjupXpgf4PsvjuVrDOypLkGo9.
- Arquivos baixados pelo conector ficam em disco: processar com script (`pdfplumber`; .xls do Domínio pelo LibreOffice: `soffice --headless --convert-to csv`).

## 7. Cuidados que custaram retrabalho
- Conferir sempre o **CNPJ do arquivo**, não a pasta: houve relatório da matriz salvo na pasta da filial.
- Os planos são diferentes (152, 166, 540, 9, 325, 492): sempre usar a conta lógica.
- O Itaú da matriz não traz CPF no histórico: reconhecer empregado pelo nome.
- O razão antigo não é gabarito: ele tem os erros da seção 3.
- O cérebro (`rof-analista`) bloqueia misturar empresas na mesma conversa. **Exceção documentada aqui:** 34 e 118 são a mesma PJ.

## 8. Situação depois do motor (18/11/2026, fim do dia)
- `scripts/rotina_mes.py` escrito e rodado de 01 a 09/2026 (as duas empresas, saldos encadeados). Arquivos de trabalho:
  razão 34 (.xls → `razao-xls`), razão 118 (.pdf → texto → `razao-pdf`), folha.csv, receita.csv (relatório de pagamentos), `_extrato.md` 07-09.
- **Bancos fecham em todos os meses**: 34 Sicredi -862,44 → -1.802,79 (06) → -2.267,37 (09); Itaú 9 zera em 06; 118 Itaú 0 → 324,60 (06) → 539,49 (09).
- **Pareamentos:** 24 Itaú→Sicredi da 34 (lançados uma vez, D 8 / C 9); 16 transferências 34↔118 de mesmo valor; 7 SISPAG da filial com o
  mesmo valor da entrada no Sicredi; 7 entradas dentro de lote SISPAG (os R$ 11.050 da pendência 2, rateados 544 + 506).
- **544:** 34 -55.993,03 e 118 +44.763,42 em 30/09; a diferença (11.229,61) é exatamente a soma dos PIX que a filial recebeu do CNPJ
  0001-93 por conta sem extrato (06: 845,99; 07: 4.051,57; 08: 3.647,31; 09: 2.684,74). Trava (b) passa como "explicada".
- **506:** controle por empresa, nunca devedora; excedente sem nota vai para 470 (34: 1.630,24; 118: 31.891,54, quase tudo SISPAG).
- **TXT ainda BLOQUEADOS** (só prévias): (c) conta 545 não existe no plano da 34 (cotas Sicredi, 1 lanç./mês); (c) 07: PIX de 196,98 do
  próprio CNPJ vindo de conta sem extrato. A trava (g) de 06/2026 foi resolvida: o Razão_531 emitido pela Rosangela (Relatorio Claude,
  18/11) dá -942,69; o -942,62 anotado era erro de digitação.
- Sem prova (perguntar): boletos "SICREDI COS GERAIS" (15/01 9.202,27; 19/02 5.773,81; 12/03 6.385,92; 22/04 10.259,39, hoje 527);
  Poder Judiciário/cartório de protesto (1.769,74; 1.769,70; 1.765,45); 7 PIX do Itaú da matriz sem favorecido no razão (12.050,18);
  Sul Distribuidora (6.382 + 3.096), Gilmar Bontorin 4.500, MSO Indústria 1.643,14, Zoop 1.476; saque 30/04 3.000 "aluguel Ótica VisouUP"
  (é despesa da FILIAL paga pela matriz? proposta: 34 D 544 / C 8 e 118 D 341 / C 544); DARF sem guia (já em decisoes.md).

## 9. Próximo passo (combinado em 18/11/2026, fim do dia)
- TXT finais entregues: 01-06, 08 e 09/2026 (34 e 118; a 118 não tem 01). 07 travado só pelo PIX de 196,98 (conta da matriz sem extrato).
- A Rosangela vai salvar na pasta Relatorio Claude da 34: **Extrato Mensal da folha 12/2025** e **balancetes 31/12/2025 da 34 e da 118**.
  1. FEITO (18/11): folha 11-12/2025 incluída; só Karine 267,54 bateu exato. Achado: Jeniffer admitida em 23/02/2026 recebeu 9 PIX antes (362).
     de dezembro pagos em janeiro passam de PROVAVEL a PROVADO). Reentregar o TXT 34 de 01 se algo mudar.
  2. Com os balancetes 2025: análise de fechamento (538 ~R$ 1,2 mi, estoque "produtos acabados/em elaboração", 504 credora), fora dos TXT.
- Quando chegar o extrato da conta sem extrato: incluir como banco da 34 em `fontes_2026.json` e gerar o 07 (08 e 09 não mudam).
