# Estudo Tributário — Simples × Lucro Presumido × Lucro Real (2027)

Base do escritório para estudos de regime tributário. Use uma cópia por CNPJ.

| Arquivo | Para que serve |
|---|---|
| `Simulador_Regime_Tributario_2027.xlsx` | Modelo do simulador (vem com dados de EXEMPLO). Preencha as células amarelas. |
| `gerar_simulador.py` | Gera o modelo de novo (`python gerar_simulador.py saida.xlsx`). Altere aqui para mudar a estrutura. |
| `Mensagem_Cliente_Estudo_Tributario.md` | Pedido enxuto ao cliente (só o que não conseguimos sozinhos). |

## Roteiro
1. Mandar a mensagem ao cliente e pedir a procuração no e-CAC / acesso à Receita/PR.
2. Buscar com procuração ou certificado: PGDAS-D, DAS, eSocial/DCTFWeb (folha), EFD-Reinf, XMLs de NF-e/NFC-e/NFS-e.
3. Preencher `Dados de Entrada` e `Compras e Despesas`; conferir `Parâmetros` (CBS 2027 após a Resolução do Senado).
4. Ler o `Comparativo` e montar o relatório de 2 a 3 páginas para a reunião.

## Prazos
- Sair do Simples com efeito em 1º/01: comunicar até o último dia útil de janeiro.
- Presumido: opção pelo 1º DARF de IRPJ do ano. Real: estimativa mensal (fevereiro) ou trimestral.
