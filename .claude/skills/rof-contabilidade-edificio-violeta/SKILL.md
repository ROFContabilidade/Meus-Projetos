---
name: rof-contabilidade-edificio-violeta
description: "EDIFICIO VIOLETA, CNPJ 52.178.386/0001-20, condomínio edilício em Governador Celso Ramos/SC, bancos Cora (8) e Sicoob (9, aplicação). Use para extrato, razão, entradas, conciliação ou TXT Domínio deste condomínio."
---

# ROF Contabilidade EDIFICIO VIOLETA — Lançamentos Contábeis e Conciliação

## Dados da Empresa

| Campo | Informação |
|---|---|
| Razão social | EDIFICIO VIOLETA |
| CNPJ | 52.178.386/0001-20 |
| CNPJ sem formatação | 52178386000120 |
| Natureza jurídica | 308-5 — Condomínio Edilício |
| CNAE principal | 81.12-5-00 — Condomínios prediais |
| CNAEs secundários | — |
| Endereço | Rua das Macieiras, 176, Palmas, Governador Celso Ramos/SC, CEP 88.190-000 |
| Situação | Ativa desde 16/12/2022 |
| Setor | Condomínio residencial |
| Regime tributário | Não se aplica (condomínio edilício; não optante Simples/MEI) |
| Receitas | Somente taxas condominiais (+ rendimentos de aplicação) |
| Banco(s) | Cora SCD conta 4303738-2 → **8** (movimento) · Sicoob conta 458327-2 → **9** (usado para aplicação; só tarifa mensal) · RDC Flexível Sicoob nº 3 → **48** · Poupança CEF → **11** (sem movimento) |
| Sistema | Domínio (gera TXT) |
| Cadastrado por | Elen (24/09/2026) |

## Sócios / Responsáveis

Condomínio **não tem sócios nem pró-labore**. Confirmado pela contadora: **não há síndico nem administradora**.
Não há funcionários CLT. Não há folha de pagamento.

## Regras de Trabalho (ACORDO COM A CONTADORA)

1. **Fidelidade total** aos dados enviados — não alterar nada sem consultar
2. **Consulta prévia** antes de qualquer alteração
3. **Base legal** sempre que sugerir algum ajuste
4. **Histórico**: padrão do razão = `REF. A ` + texto exatamente como aparece no extrato bancário (ex.: `REF. A PAGAMENTO RECEBIDO FERNANDO LUIS ZILIOTTO`, `REF. A BOLETO PAGO CELESC DISTRIBUICAO S.A`)

## Leiaute do Arquivo TXT para Domínio

```
|0000|52178386000120|
|6000|X||||
|6100|DD/MM/AAAA|CONTA_DEBITO|CONTA_CREDITO|VALOR||HISTORICO||||
```

- Uma linha `|6000|X||||` antes de **cada** `|6100|`
- Pagamento (saída): débito na conta de passivo/despesa, crédito no banco
- Recebimento (entrada): débito no banco, crédito na conta de contrapartida
- Arquivo único: pagamentos e recebimentos ordenados por data
- Valor com vírgula decimal, sem separador de milhar: ex. `1500,00`
- **Sanitizar histórico**: remover todo caractere `|` (`hist.replace('|',' ').strip()`), limitar a 60 caracteres
- Codificação: latin-1 (ANSI)
- Nome do arquivo: `EDIFICIO_VIOLETA_AAAAMM.txt`

## Plano de Contas — Contas Operacionais

| Cód | Classificação | Nome | Natureza |
|---|---|---|---|
| 5 | 1.1.10.100.1 | CAIXA GERAL | Ativo |
| 8 | 1.1.10.200.1 | CORA SCD SA - CONTA 4303738-2 | Ativo — banco principal |
| 9 | 1.1.10.200.2 | SICOOB - CONTA 458327-2 | Ativo — banco |
| 11 | 1.1.10.300.1 | POUPANÇA NA CAIXA ECONOMICA FEDERAL | Ativo — aplicação |
| 48 | 1.1.40.100.1 | APLICAÇÃO RDC FLEXIVEL SICOOB | Ativo — aplicação |
| 52 | 1.1.40.100.2 | APLICAÇÃO RDC PROGRESSIVO SICOOB | Ativo — aplicação |
| 504 | 1.1.20.100.1 | CONDOMINOS DIVERSOS | Ativo — taxas a receber |
| 31 | 1.1.30.800.3 | IRRF A RECUPERAR | Ativo |
| 506 | 2.1.30.100.1 | FORNECEDOR MODELO | Passivo — **SEMPRE** para fornecedores/prestadores com NF |
| 510 | 2.1.60.200.1 | HONORÁRIOS CONTÁBEIS | Passivo |
| 526 | 2.1.60.301.01 | ÁGUA E ESGOTO | Passivo |
| 527 | 2.1.60.301.02 | ENERGIA ELETRICA | Passivo |
| 530 | 2.1.60.301.03 | TELEFONE E INTERNET | Passivo |
| 535 | 2.1.60.301.04 | SEGURO PREDIAL | Passivo |
| 178 | 2.1.40.100.8 | IRRF A RECOLHER | Passivo |
| 184 | 2.1.40.101.4 | INSS RETIDO A RECOLHER | Passivo |
| 182 | 2.1.40.101.2 | CRF A RECOLHER | Passivo |
| 183 | 2.1.40.101.3 | ISS RETIDO A RECOLHER | Passivo |
| 531 | 2.3.50.100.6 | AJUSTE DE CONTA BANCARIA MES ANTERIOR | PL |
| 350 | 3.2.20.300.5 | TAXAS DIVERSAS | Despesa |
| 352 | 3.2.20.300.7 | MULTAS DE MORA | Despesa |
| 354 | 3.2.20.400.1 | ENERGIA ELÉTRICA | Despesa |
| 355 | 3.2.20.400.2 | ÁGUA E ESGOTO | Despesa |
| 356 | 3.2.20.400.3 | TELEFONE/INTERNET | Despesa |
| 357 | 3.2.20.400.4 | SERVIÇOS DE LIMPEZA | Despesa |
| 358 | 3.2.20.400.5 | SEGURO PREDIAL | Despesa |
| 359 | 3.2.20.400.6 | REFORMA PREDIAL | Despesa |
| 360 | 3.2.20.400.7 | MATERIAL DE HIGIENE E LIMPEZA | Despesa |
| 361 | 3.2.20.400.8 | ASSISTÊNCIA CONTÁBIL | Despesa |
| 362 | 3.2.20.400.9 | SERVIÇOS PRESTADOS POR TERCEIROS | Despesa |
| 363 | 3.2.20.401.0 | DESPESAS ADMINISTRATIVAS | Despesa |
| 364 | 3.2.20.401.1 | GÁS | Despesa |
| 365 | 3.2.20.401.2 | DESPESAS LEGAIS, JUDICIAIS E CARTORIO | Despesa |
| 366 | 3.2.20.401.3 | MATERIAIS PARA CONSERVAÇÃO | Despesa |
| 372 | 3.2.20.500.5 | JUROS DE MORA | Despesa |
| 539 | 3.2.20.500.9 | DESPESAS BANCARIAS | Despesa — tarifas |
| 411 | 4.1.10.200.1 | TAXAS CONDOMINIAIS | Receita |
| 432 | 4.1.30.100.1 | JUROS DE APLICAÇÕES | Receita financeira |
| 434 | 4.1.30.100.3 | (-) IRRF | Redutora receita financeira |
| 435 | 4.1.30.100.4 | (-) IOF | Redutora receita financeira |
| 475 | 4.1.30.100.5 | MULTA | Receita financeira |

**Fornecedores individuais existentes no plano — NÃO usar (orientação da contadora: FORNECEDOR MODELO 506 sempre):** 525/549 Singular Soluções, 528/533 Bastos Assessoria Contábil, 529 Baldança Supermercados, 532 João Batista Rodrigues, 534 Caroline Maria Vicente Inácio, 536 Distribuidora de Gás Vale do Rio Tijucas, 537 Wave Tech, 538 Construpalmas, 540 Primoris Seg, 541 RT Telecomunicações, 542 Celesc, 543 Balaroti, 544 SAMAE, 545 Henrique Mario dos Santos, 546 MT Desentupidora, 547 Beta Comercial Eletrônica, 548 Alumir Vidros, 550 KSE Smart, 551 MS2 Serviços.

## Regra de Classificação das Contrapartes

### Para cada lançamento do extrato, siga esta ordem:

1. Identificar natureza (entrada / saída)
2. Identificar favorecido/pagador (nome, CNPJ/CPF)
3. **Entrada de condômino** (PAGAMENTO RECEBIDO / PIX RECEBIDA de pessoa física) → D banco / C **504**
4. **Entrada ou saída entre contas do próprio condomínio** (EDIFICIO VIOLETA / CNPJ 52178386000120) → transferência: D banco destino / C banco origem — **um único lançamento**, nunca duplicar ao processar os dois extratos
5. Favorecido já listado em "Classificações Recorrentes Confirmadas" → usar a conta indicada
6. Prestador/fornecedor com **nota fiscal** → pagamento D **506** / C banco (a NF é provisionada à parte — ver regra abaixo)
7. Se tiver CNPJ novo → pesquisar na Receita Federal → verificar atividade → classificar conforme plano de contas e sinalizar para a contadora
8. Pessoa física não identificada → **sinalizar** para a contadora (não há conta PF genérica)
9. Histórico: `REF. A ` + texto do extrato

## Regra — Taxas Condominiais (fechamento do mês)

Padrão do razão:
- Cada recebimento no extrato: **D 8 (ou 9) / C 504** — histórico `REF. A PAGAMENTO RECEBIDO <NOME>`
- No **último dia do mês**: apropriação da receita pelo total recebido no mês: **D 504 / C 411** — histórico `TAXAS CONDOMINIAIS` — **SEMPRE incluir no TXT** (o Domínio não faz sozinho, confirmado pela contadora)
- Conferir: saldo da 504 deve zerar no fim do mês.

## Regra — Notas Fiscais de Prestadores e Compras (provisão)

Prestador de serviço só é pago com nota fiscal. Padrão de provisão do razão:

| Tipo | Débito | Crédito | Histórico padrão |
|---|---|---|---|
| Serviço tomado com NF | despesa (357/359/362/363/365…) | 506 | `SERVIÇO TOMADO NESTA DATA <nº NF> <FORNECEDOR>` |
| Compra para uso e consumo | 366 | 506 | `COMPRAS PARA USO E CONSUMO <nº NF> <FORNECEDOR>` |
| Pagamento da NF (extrato) | 506 | banco | `REF. A <texto do extrato>` |

### Fonte das NFs: relatório "Acompanhamento de Entradas" (Domínio Escrita Fiscal)

> **As provisões das NFs NÃO entram no TXT.** Confirmado pela contadora: o lançamento contábil das notas vem automaticamente da integração Escrita Fiscal → Contabilidade do Domínio. **Não gerar TXT de fornecedores.**

O relatório **Entradas.xls** (colunas: Código, Data, Nota, Série, Espécie, Código fornecedor, Fornecedor, CFOP, AC., UF, Valor Contábil…) serve só para **conferência**: confirmar que cada pagamento do extrato (D 506/510/527/530) tem a nota correspondente. Mapeamento que a integração usa (referência):

| Fornecedor (Entradas) | CFOP / AC. | Débito | Crédito | Histórico |
|---|---|---|---|---|
| CELESC DISTRIBUICAO S.A | 1252 / 151 | 354 | 527 | `ENERGIA ELETRICA  A PAGAR <Nota> CELESC DISTRIBUICAO S.A` |
| PAES E BASTOS CONTABILIDADE LTDA | 2933 / 801 | 361 | 510 | `HONORÁRIOS CONTÁBEIS <Nota> PAES E BASTOS CONTABILIDADE LTDA` |
| RT TELECOMUNICACOES LTDA | — | 356 | 530 | `TELEFONE E INTERNET A PAGAR <Nota> RT TELECOMUNICACOES LTDA` |
| Prestador de serviço (outros) | — | despesa conforme serviço | 506 | `SERVIÇO TOMADO NESTA DATA <Nota> <FORNECEDOR>` |
| Compra de material | — | 366 | 506 | `COMPRAS PARA USO E CONSUMO <Nota> <FORNECEDOR>` |

- Pagamento sem nota correspondente no relatório → **sinalizar** para a contadora (ela provisiona no balancete, ex.: RT Telecom em ago/2026).

## Regra — Contas de Consumo e Recorrentes (provisão + pagamento)

> No TXT entra **só o pagamento** (coluna da direita). As provisões vêm da Escrita Fiscal ou são feitas pela contadora no balancete (tabela abaixo só como referência).

| Item | Provisão (D / C) | Histórico da provisão | Pagamento (D / C) |
|---|---|---|---|
| Energia — CELESC | 354 / 527 | `ENERGIA ELETRICA  A PAGAR <nº fatura> CELESC DISTRIBUICAO S.A` | 527 / banco |
| Água — SAMAE Gov. Celso Ramos | 355 / 526 | `AGUA E ESGOTO DO MES` | 526 / banco |
| Telefone/Internet — RT Telecomunicações | 356 / 530 | `TELEFONE E INTERNET A PAGAR <nº> RT TELECOMUNICACOES LTDA` | 530 / banco |
| Seguro — Tokio Marine (não renovado após abr/2026, segundo a contadora) | 358 / 535 | `SEGUROS A PAGAR` | 535 / banco |
| Contabilidade — Paes e Bastos | 361 / 510 | `HONORÁRIOS CONTÁBEIS <nº> PAES E BASTOS CONTABILIDADE LTDA` | 510 / banco |

## Regra Inviolável — Conferência de Saldo

> Nunca entregar o TXT sem que os saldos do extrato estejam fechando.

1. Saldo anterior (abertura) informado no extrato
2. Saldo final (encerramento) informado no extrato
3. Diferença esperada = Saldo final − Saldo anterior
4. Somar todas as entradas lançadas no TXT
5. Somar todas as saídas lançadas no TXT
6. Diferença apurada = Total entradas − Total saídas

Se Diferença apurada ≠ Diferença esperada → NÃO entregar o TXT.

**Saldos de referência em 31/08/2026 (TXT ago/2026 conferido):** Cora (8) R$ 2.045,17 · Sicoob (9) R$ 425,92 · RDC Sicoob (48) R$ 1.023,42. O saldo de abertura do extrato do mês seguinte deve bater com esses valores; se não bater, sinalizar (conta 531 = ajuste de conta bancária do mês anterior).

## Regra Inviolável — Aplicações Financeiras e Rendimentos

> Nunca omitir movimentações de aplicação financeira do TXT.

| Movimento | Débito | Crédito | Histórico |
|---|---|---|---|
| Aplicação RDC | 48 | 9 | `REF. A APLICACAO RDC DOC. ...` |
| Resgate RDC | 9 | 48 | `REF. A RESGATE RDC DOC. ...` |
| Rendimento mensal RDC (último dia do mês) | 48 | 432 | `RENDIMENTO DE APLICAÇÃO` |
| IRRF sobre aplicação | 434 | 48 | `IRRF SOBRE APLICAÇAO` |
| Distribuição de sobras Sicoob | 9 | 432 | `REF. A CRED.DIST.SOBRAS DOC. ...` |

**Cálculo do rendimento mensal:** rendimento = "SALDO DISPONÍVEL EM <último dia>" do Extrato de Aplicações Sicoob − saldo contábil da conta 48 no mês anterior (já descontados resgates/IRRF do mês). Ex.: ago/2026 = 1.023,42 − 1.013,56 = 9,86.

Poupança CEF (11): sem movimento em 2026.

## Regra Inviolável — IOF e IRRF

> Nunca omitir IOF nem IRRF do TXT.

- IOF sobre aplicação → D **435** / C conta da aplicação — lançar separadamente
- IRRF sobre aplicação → D **434** / C conta da aplicação — nunca omitir por valor pequeno

## Regra — Sócios / Pró-labore

Não se aplica (condomínio edilício, sem sócios). Não há pró-labore nem retirada.

## Particularidades do Banco

**Cora (8)** — conta digital, sem tarifa de pacote identificada no razão. Recebe as taxas condominiais (boletos/PIX) e paga as contas.
**Sicoob (9)** — tarifa mensal `DEB PACOTE SERVICOS` (R$ 37,90) → D **539** / C 9. Aceita débito automático (ex.: `DEB.CONV.SANEAMENTO` → 526; `DEB.TIT.COMPE.EFETI` → 527 quando for fatura CELESC). Conta de aplicação RDC.

## Classificações Recorrentes Confirmadas

| Fornecedor / Descrição no extrato | Débito | Crédito |
|---|---|---|
| PAGAMENTO RECEBIDO / TRANSF PIX RECEBIDA de condômino (ex.: Fernando Luis Ziliotto, Daniela Pissaia, Sergio Murilo da Silva, Edson Sidney Figueiredo, Mateus Ogliari, Andre Luiz Sagaz, Thiago Cardoso Mac…, Cezar Almir Paludo) | 8 | 504 |
| BOLETO PAGO PAES E BASTOS CONTA(BILIDADE) | 510 | 8 |
| BOLETO PAGO RBA CONTABILIDADE LTDA (CNPJ 29.650.531/0001-01) — mesmo escritório da Paes e Bastos (confirmado pela contadora); honorários R$ 219,00 | 510 | 8 |
| BOLETO PAGO TOKIO MARINE SEGURA(DORA) — seguro provavelmente não renovado após abr/2026; se reaparecer, sinalizar | 535 | 8 |
| BOLETO PAGO RT TELECOMUNICACOES (valor pode variar, ex. 101,07 em ago/2026; quando não houver NF no relatório de Entradas, a contadora provisiona no balancete) | 530 | 8 |
| BOLETO PAGO SAMAE GOV CELSO RA(MOS) | 526 | 8 |
| BOLETO PAGO CELESC DISTRIBUICAO S.A | 527 | 8 |
| TRANSF PIX ENVIADA CARLOS ANDRE DA SILVA (limpeza) | 357 | 8 |
| TRANSF PIX ENVIADA LUCIANO XAVIER RI… (CNPJ 41.167.015/0001-26) | 362 | 8 |
| BOLETO PAGO MUNICIPIO DE GOVERN(ADOR CELSO RAMOS) (Bombeiro) | 363 | 8 |
| PGTO QR CODE PIX SIMPLES SOLUTION | 366 | 8 |
| BOLETO PAGO MF TINTAS ARMACAO LTDA (parcelas de NF) | 506 | 8 |
| PIX/QR CODE para prestador ou loja com NF (Maria Natalia da Silva, Ruan dos Santos 60.621.549, Baldança, Henrique Mario dos Santos) | 506 | banco |
| PIX REC. EDIFICIO VIOLETA 52178386000120 (transferência Cora → Sicoob) | 9 | 8 |
| DEB PACOTE SERVICOS (Sicoob) | 539 | 9 |

## Fluxo de Trabalho

1. Receber extrato da Cora, extrato conta corrente Sicoob, Extrato de Aplicações Sicoob e relatório de Entradas do mês
2. Para cada lançamento: identificar natureza → favorecido → classificar → registrar histórico
3. **Não** lançar provisões de NF (vêm da Escrita Fiscal). Usar o relatório de Entradas só para conferir; pagamento sem nota → sinalizar (contadora provisiona no balancete)
4. Incluir rendimento da aplicação e apropriação mensal D 504 / C 411 no último dia do mês
5. Sinalizar lançamentos não identificados para revisão
6. Verificar aplicações financeiras, IOF e IRRF
7. Conferir saldo de cada conta (8, 9, 48): entradas − saídas = variação do extrato
8. Gerar TXT único ordenado por data

## Observações

- **Balancete**: não é enviado (é mensal). A conferência usa o razão e o extrato.
- Sem pendências abertas em 24/09/2026.
