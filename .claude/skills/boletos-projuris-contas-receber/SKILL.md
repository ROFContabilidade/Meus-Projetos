---
name: boletos-projuris-contas-receber
description: Gerar e baixar em lote os boletos das contas a receber no Projuris (Financeiro > Contas a Receber) para um período de vencimento, no padrão do escritório.
---

# Boletos em lote no Projuris

Usar quando a Rosangela pedir (ou uma tarefa agendada disparar) a geração e o download dos boletos de contas a receber para um período de vencimento. Trabalha-se pelo Claude in Chrome em https://app.projuris.com.br/app (Financeiro > Contas a Receber).

## Períodos e agenda
- Dia 21 de cada mês, ou o primeiro dia útil depois dele se o 21 cair em fim de semana ou feriado nacional: gerar o período de 01 a 20 do MÊS SEGUINTE.
- Primeiro dia útil do mês: gerar o período de 21 ao último dia (30/31, ou 28/29 em fevereiro) do MÊS ATUAL.
- Se o dia não for o previsto, não fazer nada e avisar em uma linha.

## Autorização
A Rosangela autorizou gerar todos os boletos do período sem pedir confirmação item a item, e baixar todos os PDFs para a pasta Downloads do navegador. Se aparecer login/senha ou CAPTCHA, parar e avisar: nunca digitar senhas. Nunca duplicar boleto, nunca excluir nem cancelar nada.

## Padrão do boleto
- Juros ao mês: 4% (campo mascarado: digitar "400" vira 4,00%)
- Multa: 3% (digitar "300" vira 3,00%)
- Instruções: "Pagamentos fora do prazo sujeito a protesto - Não receber após 10 dias do vencimento - Pagar preferencialmente via Pix QRcode. Continue abençoado!"
- Seguir o padrão do primeiro boleto já gerado.

## Passo a passo: gerar
1. Em Contas a Receber, filtrar Data entre início e fim do período (campos de data em ~(322,140) e ~(450,140); o calendário aceita clique no dia). Conferir o total de itens e a paginação (15 por página).
2. Itens com ícone de código de barras já têm boleto; os sem boleto precisam ser gerados. Item com check verde já está pago: pular e avisar.
3. Abrir o item (clicar na linha/ícone), ir à seção de boleto, preencher Juros, Multa e Instruções e clicar em "Gerar boleto".

## Problemas conhecidos
- Erro "CEP com formato inválido" com Estado/Cidade em branco: clicar no campo CEP, End, BackSpace, redigitar o último dígito e Tab. O erro some e "Gerar boleto" funciona mesmo com Estado/Cidade vazios.
- Campo Nome mostra "Selecione um nome": fechar o modal (X) e reabrir; o nome carrega.
- Se abrir o formulário de edição por engano, cancelar sem salvar.
- Evitar clicar no balão de chat no canto inferior direito.
- Não trabalhar na mesma aba que a Rosangela estiver usando ao mesmo tempo.

## Passo a passo: baixar
Para cada linha com boleto (página por página):
1. Clicar nos 3 pontinhos da linha (x≈1374) e em "Visualizar boleto" (≈26px abaixo). "Baixar anexo" NÃO serve: é a Confissão de dívida, não o boleto.
2. O PDF (asaas.com/b/pdf/...) abre em nova aba. Esperar ~5 s para carregar, ler o id da nova aba no Tab Context, clicar no ícone de download do visualizador (≈(1173,27)), aguardar ~2 s e fechar a aba com tabs_close_mcp.
3. Linhas perto da borda inferior ficam sob o balão de chat: rolar a página antes.
4. Não é possível verificar a pasta Downloads: pedir à Rosangela para conferir; arquivos com "(1)" no fim são cópias duplicadas.

## Resumo final
Informar: quantos boletos foram gerados e baixados, quais foram pulados (já pagos) e quaisquer falhas ou itens não verificados.
