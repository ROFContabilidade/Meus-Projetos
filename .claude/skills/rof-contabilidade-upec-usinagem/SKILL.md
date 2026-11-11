---
name: rof-contabilidade-upec-usinagem
description: "UPEC USINAGEM E COMERCIO LTDA, CNPJ 64.847.331/0001-44, aberta em 02/02/2026 em Pinhais/PR, Simples Nacional desde a abertura, comércio de ferragens, ferramentas, peças e máquinas (Anexo I) com usinagem/tornearia/solda (Anexo II ou III, a confirmar). Mesmo grupo da FWL Indústria (sócia Fabiane Oliveira Demo): movimento entre elas sem nota é mútuo. Lançamentos, conciliação, folha e TXT Domínio. Usar quando mencionarem UPEC, UPEC Usinagem, o CNPJ 64.847.331/0001-44 ou enviarem extrato, razão, balancete, notas, folha ou guias dela, sempre junto com o rof-analista."
---

# UPEC USINAGEM E COMERCIO LTDA

**Antes de tudo, siga o roteiro do `rof-analista` (cérebro).** Esta skill só traz o que é da empresa.
- Dados: `references/empresa.json` · Decisões já tomadas (buscar com grep, não ler inteiro): `references/decisoes.md`
- Padrão de TXT e leiaute Domínio: `references/padrao_rof.md` · scripts em `scripts/`

**Situação do cadastro (11/11/2026):** código no Domínio, responsável, bancos, plano de contas, regime de
receita (caixa/competência), pró-labore e funcionários **ainda não confirmados**. Enquanto o campo estiver
"A CONFIRMAR" no `empresa.json`, perguntar antes de gerar o primeiro TXT.

## Particularidades

1. **Atividade mista: comércio + usinagem.** Mercadoria para revenda (ferragens, ferramentas, peças, máquinas,
   lubrificantes, aço, sucata) entra pela nota → estoque → CMV. Na usinagem, matéria-prima, energia da
   produção, manutenção e depreciação de torno/fresa/solda e a mão de obra da oficina são **custo**.
   Escritório, vendas e administração são despesa.
2. **Segregação no PGDAS-D (LC 123, art. 18, §4º):** revenda = Anexo I; usinagem = Anexo II quando for
   industrialização por encomenda para empresa que segue produzindo ou revendendo (ICMS/IPI, CFOP 5.124/5.125)
   e Anexo III quando for serviço ao usuário final (ISS Pinhais, LC 116 item 14.05). Tema controverso:
   **decisão da contadora, registrar em `decisoes.md`**. Comissão de representação = Anexo III.
3. **Monofásico e ST:** autopeças (Lei 10.485/2002) e lubrificantes têm PIS/COFINS monofásico; ferramentas,
   autopeças e lubrificantes costumam ter ICMS-ST no PR. Conferir pelo NCM das notas de saída e segregar
   a receita no PGDAS-D, senão paga imposto em dobro.
4. **Grupo econômico (sócia Fabiane Oliveira Demo):** FWL IND MEC (42.089.203/0001-46, Lucro Presumido em
   2026), Jogo Rápido Usinagem (05.424.870/0001-01) e DMO Ind. e Com. (45.879.023/0001-56). Movimento com
   essas empresas **sem nota = mútuo** (espelho da decisão da FWL de 10/11/2026: D Mútuo a receber / C banco
   na saída; D banco / C Mútuo na entrada). Com nota = 504/506. Conferir IOF do mútuo (Decreto 6.306/2007,
   art. 7º) e pedir o contrato. **Os saldos de mútuo têm que bater com os da FWL.**
5. **Limite do Simples no grupo (LC 123, art. 3º, §4º, III e IV):** a sócia participa com mais de 10% da FWL,
   que está fora do Simples em 2026, e é administradora das demais. Se a receita bruta **somada** das empresas
   passar de R$ 4,8 mi no ano, a UPEC perde o Simples. Conferir todo mês o acumulado (FWL projetada em
   cerca de R$ 2 mi em 2026) e a participação dela na Jogo Rápido e na DMO.
6. **Retirada da sócia = só PIX/TED da empresa para o CPF da Fabiane** (mesmo critério da FWL). Gastos pessoais
   ou familiares: classificar pela natureza ou perguntar. Planilha de sócios do cérebro todo mês.
7. **Honorários RBA:** contrato de 01/09/2026, R$ 2.450,00/mês para as 4 empresas. Lançar na UPEC só a parte dela.
