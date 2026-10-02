# Conferência de extratos bancários

Confere, empresa a empresa e banco a banco, quais extratos chegaram nas pastas do Google Drive
e quais ainda faltam, tendo como base a aba **Contabil** da planilha *Rotinas tarefas do mes.xlsm*.

## Como pedir ao Claude
> "Claude, confere os extratos do mês" (ou "quem ainda não mandou extrato?")

O Claude:
1. baixa a planilha da Rotina do Drive;
2. entra em cada pasta de empresa (Arquivos RENATA / ROF / PROTECTION Dominio) e olha a pasta `Extrato` do mês;
3. gera a planilha **Extratos_faltantes_AAAA-MM-DD.xlsx** em `relatorios/`.

## O que tem na planilha
- **Painel** — totais por mês (Recebido / FALTANDO / Verificar / S/MOV / —) e legenda de cores.
- **Resumo** — uma linha por empresa, uma coluna de status por mês, meses faltando e observações.
- **Skills prontas** — empresas que já têm skill de lançamento: mês a mês, se o extrato está na pasta e ainda não
  foi lançado ("Pronto para lançar" = fazer junto), já lançado ou faltando.
- **Detalhes** — uma linha por empresa e mês, com motivo e bancos encontrados.
- **Por banco** — cada linha de extrato da Rotina (Sicredi, Nubank...) e se o arquivo daquele banco foi achado.
- **Mensagens** — texto pronto para WhatsApp pedindo os extratos que faltam.
- **Arquivos encontrados** — lista dos arquivos vistos em cada pasta.

## Rodar manualmente
```
pip install openpyxl
python conferir_extratos.py "Rotinas tarefas do mes.xlsm" relatorios/snapshot_2026-10-02.json saida.xlsx skills_empresas.json
```
O snapshot (JSON) é a "fotografia" das pastas do Drive feita pelo Claude no dia da conferência.
