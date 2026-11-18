---
name: rof-contabilidade-oticas-34-118-mtz-fl
description: "ÓTICA VISOLUZ (matriz, empresa 34, CNPJ 24.026.777/0001-93, Sicredi 44846-8) e ÓTICA VISOUUP (filial, empresa 118, CNPJ 24.026.777/0002-74, Itaú 98896-9): ADRIANA R. DE PAULA LTDA, Simples Nacional Anexo I, comércio óptico em Colombo/PR. Uma skill para as duas contabilidades: lançamentos e conciliação do banco, folha da matriz, retiradas da sócia, ligação matriz↔filial na conta 544, mútuo Visoluk e um TXT do Domínio por empresa. Usar quando mencionarem Visoluz, VisouUP, Adriana R. de Paula, o CNPJ 24.026.777, as empresas 34 ou 118, matriz/filial da ótica, ou enviarem extrato, razão, balancete, folha ou guias delas."
---

# Óticas 34 (matriz) e 118 (filial): uma skill para as duas

**Primeiro leia `references/HANDOFF.md`** (estado do trabalho, pendências e próximo passo). Depois siga o roteiro do `rof-analista`.
Em conflito, a ordem é: decisão da contadora (`references/decisoes.md`) → cérebro → esta skill.

**Exceção ao cérebro:** 34 e 118 são a **mesma pessoa jurídica**. Por isso são trabalhadas juntas, na mesma conversa, e cada uma
tem o seu TXT. Nenhuma outra empresa entra aqui.

## Arquivos
- `references/estabelecimentos.json`: dados das duas empresas, bancos, pastas, Reinf travado.
- `references/contas_logicas.json`: conta lógica → código em cada empresa (os planos são diferentes: 152, 166, 540, 9, 325 e 492 mudam).
- `references/regras.json`: regras de classificação comuns (campo `estab`).
- `references/plano_34.csv`, `references/plano_118.csv`: planos de contas para validar cada código.
- `references/decisoes.md`: decisões validadas.
- `scripts/rotina_mes.py`: motor do mês (a escrever; especificação no HANDOFF, seção 5). `scripts/folha_csv.py`: Extrato Mensal da folha → CSV.

## Regras de ouro
1. **Ligação = 544 nas duas empresas** (1.1.1.04.001). Cada operação entre as lojas gera as duas pernas a partir do mesmo
   movimento. 544(34) + 544(118) = 0; se não der, a diferença precisa estar na lista de pendências.
2. **Despesa da matriz paga pela filial:** 118 D 544 / C 8; 34 D despesa / C 544.
3. **Conta lógica sempre.** Um código que não existe no plano da empresa trava a geração.
4. **Travas** (HANDOFF, seção 5.2): nenhum TXT sai se o banco não fechar, se a 544 não zerar sem explicação, se houver código
   inválido, CNPJ errado no `|0000|`, movimento duplicado, 506 devedora ou se for alterado mês da Reinf.
5. **Saídas:** `34_VISOLUZ_AAAA-MM.txt`, `118_VISOUUP_AAAA-MM.txt` e `Conferencia_Mtz_Fl_AAAA-MM.xlsx`.
