# Pérola By Look (49): reprocessamento dos bancos, 01 a 10/2026

## Arquivos
- `PEROLA_49_01_JANEIRO_2026.txt` … `PEROLA_49_10_OUTUBRO_2026.txt`: um TXT por mês, PagBank (8) e Itaú (9) juntos, em ordem de data. Layout Domínio, ANSI, CRLF.
- `PEROLA_49_Reprocessamento_01-10_2026.xlsx`: resumo por conta e mês · todos os movimentos com a classificação · **controle da 506 por NF** · 470 e 362 por favorecido.

## Antes de importar 01 a 06
1. No Domínio, **excluir os lançamentos de 01/01 a 30/06/2026 que movimentam as contas 8 e 9** (os lotes importados dos extratos). São 1.211 movimentos; os totais estão no razão de 23/10.
2. Excluir também o lançamento **D 576 / C 551 de 9.867,19 (30/06, "RETIRADA DE SÓCIO")**. Com o PL negativo não há lucro a distribuir. As retiradas agora estão na 188 e na 551.
3. **Não excluir** os lançamentos que vêm da integração fiscal (NF de entrada D 55/366/359 C 506), nem os da folha e do Simples. Eles continuam valendo.
4. Outubro: trocar `APLIC_ITAU` pelo código da conta "Aplicação automática Itaú" que for criada (13 linhas).

## Conferência (script `ferramentas/valida.py`)
- Os extratos de 01 a 06 foram lidos dos PDFs originais. Os 12 meses-banco batem com o razão em quantidade, débitos e créditos.
- Saldos de fim de mês gerados pelos TXT = saldos dos extratos, todos os meses. 31/10: PagBank 5.869,96 · Itaú 1,00 (+ 882,33 na aplicação automática).
- CDB PagBank (48): 22.666,55 → 6.756,55 em 31/10, igual ao saldo líquido informado pela cliente. Rendimentos lançados: 3.278,33.
- Nenhum lote desbalanceado.

## Regras aplicadas (decisões em `../decisoes.md`)
- Pagamento a fornecedor com NF: D 506 até o saldo em aberto da nota (casamento pelo CNPJ ou nome, valor exato primeiro, depois a nota mais antiga). O excedente vai para a **470**.
- PJ sem NF: CNAE consultado na Receita. Vestuário, cosméticos ou bijuteria → 470. Confeitaria → 521. Agência de viagens (excursão) → 312. Intermediador de pagamento → 493. Etiquetas → 58. Apoio administrativo → 359.
- PF sem NF, fora da folha, que não é a sócia → 362. Família da sócia → 551.
- Sócia: 188 até zerar o pró-labore líquido acumulado; o excesso → 551.
- DARF → 191 · SEFAZ → 512 · DAS → 479 (o de 08/2025 em lote: 185,12 + multa 37,02 na 352 + juros 8,42 na 372).
- Senff: a comissão é descontada do repasse → D 506 / C 504.
- Transferências entre PagBank e Itaú: um único lançamento (D banco que recebe / C banco que paga).
