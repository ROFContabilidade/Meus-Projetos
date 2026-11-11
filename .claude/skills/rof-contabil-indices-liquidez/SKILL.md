---
name: "rof-contabil-indices-liquidez"
description: "ROF Contabilidade - monta as demonstrações contábeis e os ÍNDICES DE LIQUIDEZ de qualquer cliente a partir da ECD (SPED Contábil): Balanço Patrimonial comparativo dos 2 últimos exercícios, DRE, DLPA e a página de índices com Liquidez Geral, Liquidez Corrente, Liquidez Seca e Solvência Geral (componentes e índices lado a lado, ano anterior | ano atual), com assinatura da contadora e do sócio. Entrega planilha Excel e PDF no padrão aceito em licitações (qualificação econômico-financeira). Usar quando pedirem índices de liquidez, liquidez geral/corrente/seca, solvência geral, qualificação econômico-financeira, balanço para licitação, demonstrações para edital, análise de balanço ou mandarem uma ECD para tirar balanço e índices."
---

# ROF - Demonstrações e índices de liquidez (licitações)

Serve para **qualquer cliente**. A fonte é a **ECD** (o arquivo `.txt` do SPED Contábil), porque é o livro
transmitido à Receita e é ele que a comissão de licitação confere. PDF de balanço do Domínio ou de outro
escritório só serve de apoio: se ele não bater com a ECD, **vale a ECD** e a diferença vai como alerta para a contadora.

## 1. Perguntar antes (numa mensagem só)

1. **A ECD do último exercício** (obrigatória) e, se o edital pedir 2 anos de DRE, **a ECD do exercício anterior**.
   A ECD do ano N já traz o Balanço de 31/12/N e o de 31/12/N−1 (saldo de abertura), mas a DRE é só do ano N.
2. **Nome do sócio que assina** (administrador). Se não souberem, consulte o CNPJ
   (`consulta_cnpj.py` da skill `rof-fiscal-notas-servico`) e use o sócio-administrador.
3. **Contadora que assina:** padrão **RENATA AMADO BASTOS — Contadora** (assina com certificado digital).
   Pergunte se querem o CRC abaixo do nome.
4. **PL mínimo do edital** (item que diz "caso algum índice seja igual ou menor que 1, comprovar PL mínimo de R$ X").
   Usado só na análise interna.

## 2. Rodar

```bash
S=.claude/skills/rof-contabil-indices-liquidez/scripts
python3 $S/ler_ecd.py "<ECD ano N>.txt" -o dados_N.json
python3 $S/ler_ecd.py "<ECD ano N-1>.txt" -o dados_N-1.json        # se houver
python3 $S/gerar_demonstracoes.py dados_N.json --socio "NOME DO SÓCIO" \
    [--dre-anterior dados_N-1.json] [--crc "PR-000000/O-0"] [--pl-minimo 46337.30] \
    -o "<Empresa>_Demonstracoes_Indices"
```

- `ler_ecd.py` lê J005/J100/J150 (leiaute 9 ou posterior). ECD com vários blocos J005 (Lucro Presumido trimestral,
  semestral) é tratada: o Balanço de abertura é o saldo inicial do 1º bloco, o de encerramento é o saldo final do
  último, e a DRE do ano é a **soma dos blocos**. Ele imprime os componentes (AC, Estoques, RLP, AT, PC, ELP, PL).
- `gerar_demonstracoes.py` grava a planilha e o PDF (LibreOffice). Sem LibreOffice: abrir no Excel e exportar a
  pasta de trabalho inteira em PDF. Para a planilha abrir com os índices já calculados em qualquer leitor, rode o
  `recalc.py` da skill xlsx sobre o `.xlsx`.
- Confira as páginas do PDF (imagem) antes de entregar.

## 3. Padrão aprovado do arquivo (Rosangela, 11/2026 — não mudar sem pedido)

| Página | Conteúdo |
|---|---|
| **Balanço Patrimonial** | Única página com **nome da empresa e CNPJ** (sem cidade). Colunas: data atual, data anterior. Grupos, contas e "Total do …" |
| **Demonstração do Resultado do Exercício** | Só o título. Uma coluna por exercício que **exista**: sem a DRE do ano anterior, a coluna não aparece (nada de "n/d") |
| **Demonstração de Lucros ou Prejuízos Acumulados** | Saldo inicial, lucro do exercício, lucros distribuídos, saldo final |
| **Índices de Liquidez e Solvência** | Página deitada. Tabela de **componentes à esquerda** e **índices à direita, na mesma altura**, colunas **ano anterior | ano atual**. Índice com 2 casas (ex.: 1,11), não em percentual |

Em **todas** as páginas, no rodapé, com espaço entre elas: linha + **RENATA AMADO BASTOS / Contadora** e, mais abaixo,
linha + **NOME DO SÓCIO / Sócio-Administrador**.

**Não colocar** no arquivo (vai para a comissão do cliente): fonte (ECD, SPED, registro J100), finalidade ou nome do
órgão da licitação, notas explicativas de saldo invertido, fórmulas, "atende > 1", "PL comprova o mínimo", conferências.
Números no padrão brasileiro (1.001.909,55), negativos entre parênteses, Arial, tudo em preto.

## 4. Fórmulas (as do edital padrão)

| Índice | Fórmula |
|---|---|
| Liquidez Geral (LG) | (Ativo Circulante + Realizável a Longo Prazo) ÷ (Passivo Circulante + Exigível a Longo Prazo) |
| Liquidez Corrente (LC) | Ativo Circulante ÷ Passivo Circulante |
| Liquidez Seca (LS) | (Ativo Circulante − Estoques) ÷ Passivo Circulante |
| Solvência Geral (SG) | Ativo Total ÷ (Passivo Circulante + Exigível a Longo Prazo) |

Se o edital trouxer fórmula diferente (ex.: SG com Patrimônio Líquido), siga o edital e ajuste `montar_indices`.
Realizável a Longo Prazo = Ativo Não Circulante sem Investimentos, Imobilizado, Intangível e Diferido.

## 5. Os números são os da ECD, sem correção

O arquivo sai **exatamente** com os saldos da ECD, mesmo que os índices fiquem abaixo de 1 ou negativos
(decisão da contadora, 11/2026). Nunca reclassificar, compensar ou "inverter" saldo por conta própria para passar no edital.
Se o edital tem a regra do PL mínimo, a empresa se habilita pelo PL: isso se diz **à operadora no chat**, não no arquivo.

## 6. Análise interna (só no chat, para a contadora)

O script imprime no terminal; leve para a resposta, curto:
- os 4 índices dos 2 anos;
- AC, PC ou PL negativos;
- conta com saldo invertido (cliente credor, fornecedor devedor, banco credor): a causa mais comum de índice negativo;
  corrigir de verdade exige retificar a ECD;
- PL de cada ano contra o mínimo do edital;
- DLPA com movimentação além do lucro (vai como "Lucros Distribuídos": confirmar se é distribuição mesmo);
- falta da DRE do ano anterior (pedir a ECD N−1).
Se houver PDF de balanço do cliente ou de outro escritório, compare com a ECD e aponte as contas que não batem.

## 7. Sem ECD

Se só houver balancete/balanço em PDF, monte o `dados.json` no mesmo formato que o `ler_ecd.py` grava
(`empresa`, `data_atual`, `data_anterior`, `exercicio`, `balanco` [cod, tipo T/D, nivel, sup, grp A/P, descr, atual,
anterior], `componentes`, `dre` [cod, tipo, nivel, descr, valor], `lucro_liquido`) e rode o `gerar_demonstracoes.py`.
Avise que o balanço não foi conferido com o SPED.
