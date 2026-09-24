---
name: rof-contabilidade-kopp
description: "INSTITUTO KOPP S/S LTDA., CNPJ 08.109.599/0001-08, Lucro Presumido, clínica odontológica em Curitiba/PR, banco principal: Sisprime (conta 930946) + Stone (1870071-6). Usar automaticamente quando o usuário enviar extratos, razão, balancete ou pedir lançamentos, conciliação ou TXT Domínio do Instituto Kopp (empresa 133)."
---

# ROF Contabilidade INSTITUTO KOPP — Lançamentos Contábeis e Conciliação

## Dados da Empresa

| Campo | Informação |
|---|---|
| Razão social | INSTITUTO KOPP S/S LTDA. (fantasia: INSTITUTO ODONTOLOGICO KOPP) |
| CNPJ | 08.109.599/0001-08 |
| CNPJ sem formatação | 08109599000108 |
| Código no Domínio | 133 |
| CNAE principal | 86.30-5-04 — Atividade odontológica |
| CNAEs secundários | 72.10-0-00 · 85.33-3-00 · 85.99-6-04 · 85.99-6-99 · 86.40-2-04 · 86.40-2-05 |
| Endereço | Av. Senador Souza Naves, 991, Cristo Rei, Curitiba/PR, CEP 80.050-152 |
| Natureza jurídica | 224-0 Sociedade Simples Limitada — Microempresa — Capital R$ 52.000,00 |
| Setor | Clínica odontológica |
| Regime tributário | **Lucro Presumido** (excluída do Simples Nacional em 30/04/2026). Jan–abr/2026 foi Simples. |
| Banco(s) | Sisprime conta 930946 → **8** · Stone conta 1870071-6 → **9** (não existe C6 Bank) |
| Pasta dos arquivos | `G:\Meu Drive\Trabalho ROF\Contabilidade\Arquivos RENATA Dominio\133 - Kopp Instituto\<ano>\<MM_AAAA>\Extrato` |
| Cadastrado por | Elen (24/09/2026) |

## Sócios

| Sócio | CPF | Part. | Conta de retirada | Conta de empréstimo |
|---|---|---|---|---|
| Fernanda Carolina Troetsch Kopp | 090.796.799-09 | 90% | **562** (1.2.2.04.002) | **582** (1.1.3.02.002) |
| Gino Kopp | 552.626.519-68 | 10% | **531** (1.2.2.04.001) | **581** (1.1.3.02.001) |

## Regras de Trabalho (ACORDO COM A CONTADORA)

1. **Fidelidade total** aos dados enviados — não alterar nada sem consultar
2. **Consulta prévia** antes de qualquer alteração
3. **Base legal** sempre que sugerir algum ajuste
4. **Histórico**: copiar o texto exatamente como aparece no extrato bancário
5. Os lançamentos de jan–jun/2026 **não foram conferidos** — não usar o razão antigo como verdade quando contrariar as regras abaixo (ex.: salários na 362, impostos na 359).

## Leiaute do Arquivo TXT para Domínio

Confirmado pelo TXT Otimizza da empresa (cada lançamento precedido de `|6000|X||||`):

```
|0000|08109599000108|
|6000|X||||
|6100|DD/MM/AAAA|CONTA_DEBITO|CONTA_CREDITO|VALOR||HISTORICO||||
```

- Pagamento (saída): débito na conta de despesa/ativo/passivo, crédito no banco
- Recebimento (entrada): débito no banco, crédito na contrapartida
- Arquivo único por mês (Sisprime + Stone), ordenado por data, CRLF, codificação Windows-1252
- Valor com vírgula decimal: ex. 1500,00
- Salvar em `<MM_AAAA>\Extrato\KOPP_Dominio_<MM>-<AAAA>.txt`

## Fontes do extrato

- **Sisprime**: usar o OFX `extratoContaCorrente*.ofx` — cada lançamento tem 2 tags `<MEMO>` (tipo + favorecido) e `<CHECKNUM>` (documento). O histórico = MEMO1 + " " + MEMO2 (omitir "Sem complemento"). O XLS `extratoContaCorrente*.xls` tem a mesma informação (coluna Descrição).
- **Stone**: OFX/PDF "Comprovante de Extrato". O período do arquivo costuma passar do mês — filtrar pelas datas do mês.

## Plano de Contas — Contas Operacionais

| Cód | Classificação | Nome | Uso |
|---|---|---|---|
| 8 | 1.1.1.02.001 | SISPRIME DO BRASIL - CONTA 930946 | Banco |
| 9 | 1.1.1.02.002 | STONE INSTITUIÇÃO DE PAGAMENTOS - 1870071-6 | Banco |
| 48 | 1.1.4.01.001 | COTA CAPITAL SISPRIME | Única aplicação ("Integr Cota Capital") |
| 504 | 1.1.2.01.001 | CLIENTES DIVERSOS | Recebimentos de pacientes/cartão |
| 531 | 1.2.2.04.001 | GINO KOPP (552.626.519-68) | Retirada sócio |
| 562 | 1.2.2.04.002 | FERNANDA CAROLINA TROETSCH (090.796.799-09) | Retirada sócia |
| 581 | 1.1.3.02.001 | EMPRESTIMO DE SOCIO GINO | Excedente > R$ 50 mil/mês |
| 582 | 1.1.3.02.002 | EMPRESTIMO DE SOCIO FERNANDA | Excedente > R$ 50 mil/mês |
| 506 | 2.1.3.01.001 | FORNECEDOR MODELO | Fornecedores com NF |
| 510 | 2.1.6.02.001 | HONORÁRIOS CONTÁBEIS | Paes e Bastos |
| 173 | 2.1.4.01.003 | ISS A RECOLHER | DAM ISS (Curitiba) |
| 176 | 2.1.4.01.006 | IMPOSTO DE RENDA A RECOLHER | DARF IRPJ trimestral |
| 177 | 2.1.4.01.007 | CONTRIBUIÇÃO SOCIAL A RECOLHER | DARF CSLL trimestral |
| 178 | 2.1.4.01.008 | IRRF A RECOLHER | DARF IRRF |
| 179 | 2.1.4.01.009 | PIS A RECOLHER | DARF PIS |
| 180 | 2.1.4.01.010 | COFINS A RECOLHER | DARF COFINS |
| 182 | 2.1.4.01.012 | CRF A RECOLHER | DARF CSRF (5952) |
| 183 | 2.1.4.01.013 | ISS RETIDO A RECOLHER | DAM ISS retido |
| 184 | 2.1.4.01.014 | INSS RETIDO A RECOLHER | DARF INSS retido |
| 187 | 2.1.5.01.001 | SALÁRIOS E ORDENADOS A PAGAR | Líquido da folha |
| 572 | 2.1.5.01.004 | FERIAS A PAGAR | Férias / adiantamento de férias |
| 576 | 2.1.5.01.005 | RESCISÃO A PAGAR | Rescisões |
| 191 | 2.1.5.02.001 | INSS A RECOLHER | DCTFWeb |
| 192 | 2.1.5.02.002 | FGTS A RECOLHER | FGTS Digital (Caixa) |
| 530 | 2.1.5.02.004 | CREDITO EMPRESTIMO EMPREGADO | Consignado (Crédito do Trabalhador) |
| 339 | 3.2.2.01.009 | ASSISTÊNCIA MÉDICA E SOCIAL | Nossa Saúde, Unimed Seg |
| 521 | 3.2.2.01.012 | DESPESAS COM ALIMENTAÇÃO | iFood, alimentação |
| 348 | 3.2.2.03.003 | IPTU | IPTU |
| 352 | 3.2.2.03.007 | MULTAS DE MORA | Multa em guia paga em atraso |
| 372 | 3.2.2.05.005 | JUROS DE MORA | Juros em guia paga em atraso |
| 354 / 355 / 356 | 3.2.2.04.001-003 | ENERGIA / ÁGUA / TELEFONE | Copel / Sanepar / Vivo-Claro |
| 357 | 3.2.2.04.004 | PROPAGANDA E PUBLICIDADE | Facebook, Rabbit Agency |
| 359 | 3.2.2.04.006 | DESPESAS ADMINISTRATIVAS | Gerais |
| 362 | 3.2.2.04.009 | SERVIÇOS PRESTADOS POR TERCEIROS | Dentistas / profissionais PF |
| 366 | 3.2.2.04.013 | DESPESA COM CARTÃO DE CREDITO | Fatura cartão Sisprime |
| 467 | 3.2.1.06.007 | CUSTOS DOS SERVIÇOS PRESTADOS | Laboratórios / protéticos |
| 493 | 3.2.2.04.014 | DESPESAS DIVERSAS | Diversas |
| 550 | 3.2.2.04.015 | MONITORAMENTO E VIGILANCIA | VSegurança |
| 575 | 3.2.2.04.016 | DESPESA COM USO E CONSUMO | Materiais sem NF / marketplace |
| 580 | 3.2.2.04.020 | CONSELHO FEDERAL DE ODONTOLOGIA | CRO/CFO |
| 583 | 3.2.2.04.021 | DEDETIZAÇÃO E LIMPEZA | Real Dedetizadora |
| 532 | 3.2.2.05.009 | TARIFAS BANCARIAS | Tarifa PIX, manutenção CC |
| 432 | 4.1.3.01.001 | JUROS DE APLICAÇÕES | Rendimento automático Stone |

**Contas que NÃO devem ser usadas:**
- **577 / 578** (Despesas Gino / Dra. Fernanda) — serão renomeadas pela contadora
- **539** (Distribuição de lucros) — conta de lucro declarado na REINF
- **188 / 275** (Pró-labore) — pró-labore parou quando a empresa foi para o Presumido
- **479 / 480** (Simples Nacional) — só até abr/2026

## Regra de Classificação das Contrapartes

### Para cada lançamento do extrato, siga esta ordem:

1. Identificar natureza (entrada / saída)
2. Identificar favorecido (MEMO2 do OFX + CHECKNUM)
3. Se tiver CNPJ → pesquisar na Receita Federal → verificar atividade → classificar conforme plano de contas
4. Se Pessoa Física profissional (dentista, auxiliar autônoma) → **362**
5. Se funcionário CLT → **187** (ou 572 férias / 576 rescisão — conferir com o extrato da folha)
6. Se sócio → aplicar Regra de Retiradas
7. Transferência entre Sisprime e Stone → **8 ↔ 9** (lançar UMA vez só)
8. Histórico: copiar exatamente como aparece no extrato

## Regra Inviolável — Conferência de Saldo

> Nunca entregar o TXT sem que os saldos do extrato estejam fechando — conferir **por banco** (8 e 9).

1. Saldo anterior (abertura) informado no extrato
2. Saldo final (encerramento) informado no extrato
3. Diferença esperada = Saldo final − Saldo anterior
4. Somar todas as entradas lançadas no TXT
5. Somar todas as saídas lançadas no TXT
6. Diferença apurada = Total entradas − Total saídas

Se Diferença apurada ≠ Diferença esperada → NÃO entregar o TXT.

Saldos conferidos:

| Data | Sisprime (8) | Stone (9) |
|---|---|---|
| 30/06/2026 (razão) | 171.846,03 | 9.585,83 |
| 31/07/2026 | 216.472,94 | 1.666,18 |
| 31/08/2026 | 220.629,20 | 1.666,18 |

## Regra Inviolável — Aplicações Financeiras e Rendimentos

> Nunca omitir movimentações de aplicação financeira do TXT.

- "Integr Cota Capital" (Sisprime) → D **48** / C 8 — é a única aplicação da empresa
- "Rendimento automático" (Stone) → D 9 / C **432**

## Regra Inviolável — IOF e IRRF

> Nunca omitir IOF nem IRRF do TXT.

- Não há conta de IOF despesa no plano; se aparecer IOF no extrato → consultar a contadora antes de lançar
- IRRF → conta **178** — nunca omitir por valor pequeno

## Regra — Impostos (Lucro Presumido)

Cada guia na sua conta de passivo. Conferir o valor com as guias em `<MM_AAAA>\Guias` (competência anterior ao mês do pagamento).

| Guia | Débito |
|---|---|
| DARF PIS | 179 |
| DARF COFINS | 180 |
| DARF IRPJ (trimestral) | 176 |
| DARF CSLL (trimestral) | 177 |
| DARF IRRF | 178 |
| DARF CRF / CSRF | 182 |
| DARF INSS retido | 184 |
| DCTFWeb (INSS folha) | 191 |
| FGTS (Caixa) | 192 |
| DAM ISS | 173 |
| DAM ISS retido | 183 |

Guia paga com acréscimo: principal na conta do imposto, **multa → 352**, **juros → 372** (valores da própria guia).
Pagamentos aparecem no extrato como "Pagamento Pix MINISTERIO DA FAZEND", "Débito Darf DARF", "Pagamento Pix MUNICIPIO DE CURITIB" e "Pagamento Pix CAIXA ECONOMICA FEDE".

## Regra — Folha de Pagamento

- 8 empregados CLT em 07/2026 (Lediane, Kerolayne, Larissa, Kelly, Eric, Maria Sueli, Pamela, Sávia). Conferir com o "Extrato Mensal" da folha do Domínio.
- PIX do líquido do mês → **187**. Adiantamento/pagamento de férias → **572**. Rescisão → **576**.
- A **187 acumulou 73.990,24 C** até jul/2026 porque os salários de jan–jun foram lançados na 362 (a regularizar pela contadora).

## Regra Mensal — Retiradas dos Sócios

> ANTES DE LANÇAR qualquer pagamento a sócio: confirmar com a contadora o total pago no mês.

**Sem pró-labore** desde a entrada no Lucro Presumido.

| Situação | Débito | Crédito |
|---|---|---|
| Retiradas do sócio no mês até R$ 50.000,00 | 531 (Gino) / 562 (Fernanda) | 8 |
| Excedente acima de R$ 50.000,00 no mês (por sócio) | 581 (Gino) / 582 (Fernanda) | 8 |

- O limite de R$ 50 mil/mês por sócio acompanha a retenção de 10% de IRRF sobre lucros e dividendos acima de R$ 50 mil/mês para a mesma pessoa física (Lei 15.270/2025, art. 6º-A da Lei 9.250/1995).
- Somar no mês **todos** os pagamentos em favor do sócio, inclusive contas pessoais pagas pela empresa (ex.: cartão Santander Unique).

## Regra — Devolução / Aporte do Sócio

Quando o sócio deposita valores **na empresa** (entrada no extrato):

| Débito | Crédito |
|---|---|
| 8 | 531 (Gino) / 562 (Fernanda) |

Despesa pessoal paga e reembolsada pelo sócio no mesmo dia (ex.: 20/07/2026, Gino reembolsou 22,58 e 80,00) → saída D 531 e entrada C 531.

## Particularidades do Banco

- **Sisprime (8)**: tarifa de R$ 1,00 por PIX enviado ("Tar utilização PIX") e "Deb Tarifa Manut CC" R$ 80,00 no dia 10 → 532. Cartões Stone liquidados direto na Sisprime ("Venda Crédito" / CHECKNUM "Stone Paga") → C 504.
- **Stone (9)**: recebe vendas de cartão (C 504) e rendimento automático (C 432). O saldo é zerado por transferência PIX para a Sisprime ("INSTITUTO KOPP S/S LTDA. - Transferência | Pix" na Stone = "Crédito Pix INSTITUTO ODONTOLOGI" na Sisprime) → D 8 / C 9, lançado **uma vez só**.
- "Crédito Pix INSTITUTO KOPP S/S L" (CHECKNUM 08109599) na Sisprime = repasses de recebimentos da clínica → C 504 (padrão do razão).

## Classificações Recorrentes Confirmadas

| Fornecedor / Descrição | Conta |
|---|---|
| Venda Crédito (Stone Paga), Crédito Pix de pacientes | 504 |
| Medsul / Dental Med Sul, Speed, Quantity, Cremer, Neodent/JJGC, Concorde, Clinicorp, Scanderra, Prorad, Ambserv, Flexx Medicina, Dixi Vext, Attune/Biomistic, Surguide, Clear/Clearcorrect, Surya Dental Comer | 506 |
| Empresa Brasileira D (Caju — benefícios), Fundo de Urbanização (URBS — VT), Instituto D E D TR (aux. funeral), Contabilista Suprime, AIBR | 506 |
| Carmen Lucia Mueller, Anae Olsen Lampe, Ingrid Andor, Allan Gustavo Nagata, Amanda Dambrosio, Fernanda Cristina, Lara Cristian Nesi, Renato Domiciano, Kamila Karoline, Osvaldo José, Leonel Pires, Mauro Sergio, Marcelo Batista, Rodrigo Berto, Alberto Westphal, Quali Dental, "SURYA" (Liq.) | 362 |
| Alfortodontia, Vieira Lab (Marcelo Vieira), Blue Digital Laboratório, Suzzi Lab, Align | 467 |
| Pix Marketplace, Bionovatti, RD/RS Papéis, Carrefour, Leroy Merlin, Casas Bahia, Renner, Shopee | 575 |
| Orthosiso | 493 |
| VKS, Raia Drogasil, Cia Beal (flores), 99 Tecnologia, Sindicato, Tabelionato, Lucas Lin (MEI), Emanueli (MEI) | 359 |
| Facebook, Rabbit Agency | 357 |
| Nossa Saúde, Unimed Seg | 339 |
| iFood, JHD Alimentos | 521 |
| Telefônica/Vivo, Claro | 356 |
| Copel | 354 |
| Sanepar | 355 |
| Paes e Bastos | 510 |
| Fat cartão Sisprime | 366 |
| Conselho Federal de Odontologia | 580 |
| Real Dedetizadora | 583 |
| VSegurança | 550 |

## Fluxo de Trabalho

1. Ler OFX Sisprime + OFX/PDF Stone da pasta `<MM_AAAA>\Extrato`
2. Para cada lançamento: identificar natureza → favorecido → classificar → registrar histórico
3. Conferir impostos com as guias da pasta `Guias` e salários com o extrato da folha
4. Aplicar a regra dos R$ 50 mil por sócio no mês
5. Sinalizar lançamentos não identificados para revisão
6. Verificar aplicações financeiras, IOF e IRRF
7. Conferir saldo por banco: entradas − saídas = variação do extrato
8. Gerar TXT único ordenado por data

## Pendências a Confirmar com a Contadora

- 187 com saldo credor de 73.990,24 (salários de jan–jun lançados na 362) — regularizar
- DCTFWeb paga em 21/07 (10.128,48) e 17/08 (3.300,07) sem guia na pasta — lançadas na 191; confirmar se inclui IRRF/CRF
- Pagamentos ao Município de Curitiba de 1.280,73 (22/07) e 1.259,84 (17/08) sem guia — lançados como IPTU (348)
- Cartão Santander Unique (10/08: 18.673,31 + 1.830,63) — confirmar se é da Dra. Fernanda; lançado 562/582 pela regra dos R$ 50 mil
- Favorecidos novos lançados provisoriamente (ver relatório do mês)
- Renomear 577/578
