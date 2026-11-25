# Como atualizar a Prestação de Contas 2026 do London Residence

Instruções para o Claude, em qualquer conversa nova. Pedido típico da Rosangela: **"vamos atualizar a prestação de contas"**.

## O que a Rosangela salva no Drive antes
Pasta `G:\Meu Drive\Trabalho ROF\London Residence\Diversos\2026\11_2026` (ID `160wJuzmV0VzOt7mN1GNyQdG1wQiTsBX_`):
1. **Balancete anual** do AcolWeb (12/2025 a 11/2026) – valores por conta e por mês.
2. **Balancete mensal – detalhado** (regime de caixa) – valores por fornecedor e o saldo de cada conta.
3. **Relatório do mês** (Extrato de Contas – Entradas e Saídas) até a data de corte.
4. **Extrato do Sicredi** 61921-3 atualizado (após 23/11/2026).
5. Se houver: relatório de inadimplência e a planilha `Diversos/Fundo de Pintura.xlsx` (aba "Conciliado").

## Passo a passo
1. Ler os relatórios novos com `read_file_content` (Google Drive). Baixar o extrato novo com `download_file_content` e salvar em `<pasta temporária>/extratos/12.pdf` junto com os 11 anteriores (IDs em `ANOTACOES_London_Residence.md`, seção 1, e na lista abaixo).
2. Regerar os lançamentos do razão:
   `python3 -I scripts/parse.py <pasta temporária> scripts/dados/lanc.json`
   (a pasta precisa ter a subpasta `extratos/` com 01.pdf … 12.pdf em ordem de mês; o script confere o saldo linha a linha e avisa se algo não bater).
   Rodar `python3 -I scripts/classify.py <pasta com lanc.json>` para ver lançamentos novos sem classificação (aparecem como `???`) e incluir a regra em `classify.py`.
3. Atualizar em `scripts/build.py` só o que mudou (os números de novembro):
   - `REC` e `DES` – coluna de nov/26 de cada conta (12º valor de cada lista), conforme o balancete anual novo;
   - `POUP_R` / `POUP_D` se houver movimento na poupança;
   - `DREC` / `DDES` – totais por competência e por fornecedor do balancete detalhado;
   - `ext` (aba Conciliação) – última linha: saldo final de novembro;
   - posição das contas (conta principal, poupança, fundo de reserva) na data de corte;
   - inadimplência (`280.54`) e, se a Rosangela confirmar, o bloco "FUNDO DE PINTURA" com os números da planilha dela (arrecadado R$ 81.000; saldo após a pintura −R$ 3.950).
4. Gerar e conferir:
   ```
   python3 London-Residence/scripts/build.py
   python3 <skill xlsx>/scripts/recalc.py London-Residence/Prestacao_Contas_2026_London_Residence.xlsx 90
   ```
   Conferir: total de despesas do Excel = balancete; saldo final = soma das contas; nenhum erro de fórmula.
5. PDF: `soffice --headless --convert-to pdf` (script `office/soffice.py` da skill xlsx) dentro da pasta `London-Residence`.
6. Relatório interno: atualizar a lista em `scripts/interno.py` se surgir divergência nova e rodar `python3 London-Residence/scripts/interno.py`. O PDF interno leva **só a aba "Pendências antes da AGO"**.
7. Enviar os arquivos à Rosangela, fazer commit e push.

## Regras de apresentação combinadas com a Rosangela
- Linguagem clara, profissional (não infantil); pronto para imprimir em A4.
- **Não mostrar comparação extrato × AcolWeb** na prestação: só "saldo conciliado". Divergências vão para o relatório interno.
- Nada de observações internas na prestação ("houve aditivo?", "sem nota fiscal", "confirmar").
- Números em preto; Excel primeiro, Word só se ela pedir.

## IDs dos extratos já usados (Google Drive)
12/2025 `1_N-y-ZsgKsr7NVuut5jmjtlofb2DMJze` · 01 `1Yy8_GehuRt0RMNSrh-o6tbX2tjoNxQBN` · 02 `1do_i-irfnIo5sKqz0i8ZFsOJu8qCmP8m` · 03 `1s4KEmm0m8hrX_0hGGzBxx1JrUrtbHIUA` · 04 `1dMrll8IB3vQFI7twFAFVY1fqIE-Gc3mP` · 05 `1VtsqfQ9pGkfWCu7_D1wD6IbBgnsYqAW3` · 06 `1byk8q5DVWID8tAlqVazjHekrYCinfjzT` · 07 `1ZT4Bxc3P-g9E5LAAof0P_Ht9d_nN1hR2` · 08 `1i_iBiRaBFciVMN4L6bGtaLlpNhREvzMz` · 09 `1VLx3TQuAENrz3nGtqJtF4TgYy6LNFN3j` · 10 `1_S1Trec9hFiYADO2-swilz0XUk-iLnv3` · 11 (até 19/11) `16qlBzG3b2JAsKPE0mRQ7UOmW4t0hbEyv`
