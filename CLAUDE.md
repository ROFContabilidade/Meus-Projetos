# ROF Contabilidade: instruções para o Claude

Escritório de contabilidade. Responsáveis pelos lançamentos: **Elen** e **Rosangela**. Sistema contábil: **Domínio**.

## Padrão para toda skill nova
Toda skill criada neste repositório segue o **padrão ROF**, em
`.claude/skills/extrato-dominio/references/padrao_rof.md`. Os modelos são as skills validadas
`rof-contabilidade-kopp` (Kopp Instituto, empresa 133) e `rof-contabilidade-fwsgoncalves`
(F W S Gonçalves, empresa 82). Em resumo:
- fidelidade total aos dados, consulta prévia, base legal, nunca inventar;
- perguntar sempre que houver dúvida, em lote, e registrar a decisão (quem validou e quando);
- regras invioláveis de conferência (saldos, nada omitido, só itens confirmados na entrega);
- uma skill por empresa (`rof-contabilidade-<empresa>`), gerada por
  `scripts/gerar_skill_empresa.py`, com as seções da seção 9 do padrão;
- planilhas de controle: verde = OK, amarelo = a fazer; conferir se nada ficou de fora.

## Nova empresa
Siga `.claude/skills/extrato-dominio/references/nova_empresa.md`: responsável (Elen ou
Rosangela) → CNPJ e cartão CNPJ → usa o Domínio? → perguntas → balancete, relatório de
entradas, razão, folha → confirmação → skill da empresa.

## Lançamento mensal (conversa nova)
Quando a usuária mandar o CNPJ de uma empresa já cadastrada (ou `/lancar-extrato <CNPJ>`), use a skill
`.claude/skills/lancar-extrato`: peça o pacote `rof-contabilidade-<empresa>.skill` mais recente, restaure
com `scripts/restaurar_empresa.py`, carregue o padrão ROF e o histórico da empresa e siga a rotina do mês.
No fim, entregue o pacote atualizado para ela guardar.

## Sigilo
Este repositório é **público**. Nunca faça commit de dados de clientes (CPF, folha, extratos,
plano de contas, TXT de lançamentos, JSON de empresas). A pasta `empresas/` está no `.gitignore`;
esses arquivos são entregues ao usuário diretamente.
