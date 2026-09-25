---
name: lancar-extrato
description: Comando do escritório ROF para começar o lançamento mensal do extrato de uma empresa já cadastrada, a partir do CNPJ. Restaura a configuração da empresa (regras, plano de contas, folha, notas, impostos, saldos e decisões anteriores) do pacote rof-contabilidade-<empresa>.skill, carrega o padrão ROF e segue a mesma rotina dos meses anteriores até entregar o TXT do Domínio conferido. Use sempre que a usuária mandar um CNPJ para lançar o extrato, disser "/lancar-extrato <CNPJ>", "lançar o extrato de <mês>" de uma empresa já cadastrada, ou começar uma conversa nova para o mês seguinte.
---

# Lançar o extrato do mês a partir do CNPJ

Uso: `/lancar-extrato <CNPJ> [mês/ano]`. Exemplo: `/lancar-extrato 00.000.000/0000-00 09/2026`.

Este repositório é **público**. Os dados das empresas nunca ficam aqui: a pasta `empresas/`
está no `.gitignore` e começa **vazia** em toda conversa nova. A memória de cada empresa é o
pacote `rof-contabilidade-<empresa>.skill` que a usuária recebe no fim de cada mês.

## 1. Restaurar a empresa

1. Guarde o CNPJ só com números. Se o mês não foi informado, proponha o mês seguinte ao último
   lançado e confirme.
2. Peça o pacote `rof-contabilidade-<empresa>.skill` **mais recente**: anexado no chat, ou
   onde a usuária o guardou no Drive (baixe com o conector do Drive; decodifique o `content`
   base64 com Python quando o resultado vier salvo em arquivo).
3. Restaure e confira que é a empresa do CNPJ:
   `python3 .claude/skills/extrato-dominio/scripts/restaurar_empresa.py <pacote.skill> --cnpj <CNPJ>`
4. Sem pacote, não invente: pergunte se a empresa é nova (siga
   `.claude/skills/extrato-dominio/references/nova_empresa.md`) ou se o pacote está em outro lugar.

## 2. Carregar o padrão e o histórico

Leia, antes de lançar qualquer coisa:
- `.claude/skills/extrato-dominio/SKILL.md` (pipeline e scripts) e
  `.claude/skills/extrato-dominio/references/padrao_rof.md` (regras invioláveis);
- o `SKILL.md` de dentro do pacote (dados, regras e particularidades da empresa);
- no JSON restaurado: `rotina_mensal`, `observacoes` (decisões, quem validou e quando),
  `saldos_conferidos` (saldo inicial do banco e da aplicação), `meses_lancados`, `pendencias`,
  `praticas`, `particularidades_bancos` e `drive` (pastas onde ficam os arquivos do mês).

Diga à usuária, em poucas linhas: empresa, mês, saldos iniciais que vai usar e pendências
abertas do mês anterior.

## 3. Fazer o mês

Siga o `rotina_mensal` da empresa, na ordem. Em resumo, o mesmo roteiro dos meses anteriores:
1. Buscar no Drive a pasta `<MM_AAAA>/Extrato` do mês: extrato (OFX/PDF), extrato da
   aplicação, comprovantes, relatórios da empresa. Conferir se cada arquivo é do mês certo.
   Arquivos grandes demais para o conector: pedir para a usuária anexar no chat.
2. `extrato_dominio.py ler` → `comprovantes_itau.py ler/aplicar` (ou equivalente do banco) →
   `classificar` → `folha_extrato_mensal.py conferir --aplicar` →
   `entradas_dominio.py conferir --aplicar` → `impostos_dominio.py conferir --aplicar`.
3. Conferir aplicação, rendimentos, juros e guias (DCTFWeb e FGTS pelos comprovantes).
4. Tudo o que não estiver CONFIRMADO vai numa **lista única de perguntas, com proposta de
   conta**, e na planilha de conferência (amarelo = a decidir). Nunca lançar sem confirmação.
5. Com as respostas: `gerar ... --saldo-inicial` / `--saldo-final` conforme a empresa,
   `--separar` se a empresa usa _PAGAR/_RECEBER, e a auditoria completa (linhas 6100 válidas,
   CRLF, banco débito = crédito, conta transitória zerada, aplicação fechando com o extrato).
6. Planilha verde.

## 4. Fechar o mês (sempre)

1. Registrar no JSON restaurado as decisões novas em `observacoes` ("(Nome, DD/MM/AAAA)"),
   regras novas em `regras`, os saldos finais em `saldos_conferidos` e o mês em `meses_lancados`.
2. Gerar a skill da empresa de novo (o `restaurar_empresa.py` imprime o comando) e o pacote
   `extrato-dominio.skill`.
3. Enviar à usuária: TXT(s), planilha verde e o **novo** `rof-contabilidade-<empresa>.skill`,
   lembrando que é esse pacote que ela deve guardar (no Drive, na pasta da empresa) e anexar
   na próxima conversa.
4. Melhorias nos scripts ou no padrão (sem dados de clientes) vão para o repositório: commit
   e push no branch da sessão.
