---
name: rof-contabilidade-artsu
description: "Lançamentos contábeis e conciliação bancária da empresa ARTSU BRAZILIAN JIU-JITSU LTDA (CNPJ 36.021.287/0001-83, Simples Nacional, academia de jiu-jitsu e comércio esportivo) para o sistema Domínio (Thomson Reuters). Use quando o usuário pedir para conciliar extrato, cruzar movimentações bancárias, classificar lançamentos no plano de contas ou gerar o arquivo TXT no leiaute Domínio da ARTSU. Recebe extrato bancário (OFX ou PDF), plano de contas, relatório de gestão, folha de pagamento e razão do banco; cruza por valor, data e nome; e gera TXT único com pagamentos e recebimentos ordenados por data."
---

# ROF Contabilidade — ARTSU BRAZILIAN JIU-JITSU LTDA

## Dados da Empresa

| Campo             | Valor                          |
|-------------------|-------------------------------|
| Razão Social      | ARTSU BRAZILIAN JIU-JITSU LTDA |
| CNPJ              | 36021287000183                 |
| Regime Tributário | Simples Nacional               |

**CNAEs:**
- 8599-6/04 — Treinamento em desenvolvimento profissional e gerencial
- 4729-6/99 — Comércio varejista de outros produtos alimentícios n.e.
- 8591-1/00 — Ensino de esportes

**Sócio Único:** JULIO CEZAR DIEDZITS — CPF 058.491.719-83

---

## Contas Bancárias

| Banco | Agência | Conta | Código no plano |
|-------|---------|-------|-----------------|
| BANCO SANTANDER | 1535 | 13001106-4 | **34** (1.1.1.02.004) |
| NU PAGAMENTOS S.A. | — | 7300364-7 | **8** (1.1.1.02.001) |
| PAGSEGURO INTERNET S/A | — | 35878323-1 | **6** (1.1.1.02.003) |

---

## Plano de Contas — Principais Contas Operacionais

| Código | Classificação | Nome |
|--------|--------------|------|
| 5 | 1.1.1.01.001 | CAIXA GERAL |
| 8 | 1.1.1.02.001 | NU PAGAMENTOS S.A - CONTA 7300364-7 |
| 6 | 1.1.1.02.003 | PAGSEGURO INTERNET S/A - CONTA 35878323-1 |
| 34 | 1.1.1.02.004 | BANCO SANTANDER - CONTA 130011064 |
| 504 | 1.1.2.01.001 | CLIENTES DIVERSOS - SERVIÇOS |
| 531 | 1.1.2.01.002 | CLIENTES DIVERSOS - VENDAS |
| 55 | 1.1.5.01.001 | MERCADORIAS PARA REVENDA |
| 532 | 1.2.2.04.0001 | JULIO CESAR DIEDZITS (058.491.719-83) |
| 152 | 2.1.1.01.001 | EMPRÉSTIMO BANCO SANTANDER |
| 479 | 2.1.4.01.015 | SIMPLES NACIONAL A RECOLHER |
| 188 | 2.1.5.01.002 | PRÓ-LABORE A PAGAR |
| 191 | 2.1.5.02.001 | INSS A RECOLHER |
| 510 | 2.1.6.02.001 | HONORÁRIOS CONTÁBEIS |
| 292 | 3.1.2.07.001 | COMBUSTÍVEL |
| 299 | 3.2.1.01.002 | PRÓ-LABORE (Despesa) |
| 350 | 3.2.2.03.005 | TAXAS DIVERSAS |
| 352 | 3.2.2.03.007 | MULTAS DE MORA |
| 354 | 3.2.2.04.001 | ENERGIA ELÉTRICA |
| 356 | 3.2.2.04.003 | TELEFONE |
| 357 | 3.2.2.04.004 | DESPESAS COM CARTÃO DE CRÉDITO |
| 359 | 3.2.2.04.006 | DESPESAS ADMINISTRATIVAS |
| 361 | 3.2.2.04.008 | ASSISTÊNCIA CONTÁBIL |
| 362 | 3.2.2.04.009 | SERVIÇOS PRESTADOS POR TERCEIROS |
| 366 | 3.2.2.04.013 | DÍZIMOS E OFERTAS |
| 493 | 3.2.2.04.014 | DESPESAS DIVERSAS |
| 537 | 3.2.2.04.016 | DESPESAS COM DESLOCAMENTO |
| 521 | 3.2.2.04.017 | DESPESAS COM ALIMENTAÇÃO |
| 541 | 3.2.2.04.019 | DESPESA COM SISTEMAS |
| 370 | 3.2.2.05.003 | TARIFAS BANCÁRIAS |
| 372 | 3.2.2.05.005 | JUROS DE MORA |
| 533 | 3.2.2.05.009 | IOF |
| 408 | 4.1.1.01.003 | VENDA DE MERCADORIAS |
| 411 | 4.1.1.02.001 | SERVIÇOS PRESTADOS |
| 480 | 4.1.2.03.008 | (-) SIMPLES NACIONAL |
| 432 | 4.1.3.01.001 | JUROS DE APLICAÇÕES |

---

## Leiaute do Arquivo TXT para Domínio

```
|0000|36021287000183|
|6000|X||||
|6100|DD/MM/AAAA|CONTA_DEBITO|CONTA_CREDITO|VALOR||HISTORICO||||
```

- **Um `|6000|X||||` por lançamento** — não por data, não por banco: um por linha `|6100|`
- O campo tipo deve ser literalmente a letra **X** — campos vazios não são aceitos
- Pagamento (saída): débito na conta de despesa, crédito no banco
- Recebimento (entrada): débito no banco, crédito na conta de receita
- **Arquivo único:** pagamentos e recebimentos compilados juntos, ordenados por data
- Separador decimal: vírgula (ex: 1234,56)
- Sanitizar o histórico antes de gravar: remover caracteres `|` e limitar a 60 caracteres

---

## Pergunta Obrigatória a Cada Mês

> **"O pró-labore do Julio neste mês é 1 salário mínimo vigente ou houve alteração?"**

Fazer essa pergunta ANTES de classificar qualquer movimentação em nome do sócio.

---

## Regras Especiais — Sócio (JULIO CEZAR DIEDZITS)

### Regra 1 — SAÍDA em nome do sócio (empresa paga para ele)

Os pagamentos ao Julio são feitos parcelados ao longo do mês, em diferentes bancos. O controle é **acumulado cronologicamente entre todos os bancos**:

**Salário mínimo vigente 2026: R$ 1.621,00 | INSS 11%: R$ 178,31 | Pró-labore líquido: R$ 1.442,69**

**Lógica de rateio acumulado:**
1. Somar todos os pagamentos ao Julio (todos os bancos, em ordem cronológica)
2. Enquanto o acumulado **não atingir R$ 1.442,69** → lançar em **D-188 / C-Banco**
3. Quando o acumulado **ultrapassar R$ 1.442,69**:
   - A parcela que completa o pró-labore → **D-188 / C-Banco**
   - O excedente → **D-532 / C-Banco**
4. Todos os pagamentos subsequentes no mesmo mês → **D-532 / C-Banco**

~~**Se pró-labore variável (informado pela contadora):** lançar tudo na conta 532 — contadora ajusta o rateio manualmente.~~ **Substituído em 24/09/2026:** perguntar o valor do pró-labore do mês e aplicar o rateio 188/532 com esse valor.

### Regra 2 — ENTRADA em nome do sócio (ele paga para a empresa)

- Lançar tudo na conta 532: **D-Banco / C-532**

### Esposa do sócio — DANIELE GONCALVES GARCIA DIEDZITS

- Pagamentos e recebimentos em nome dela → **conta 532**
- Histórico: incluir nome dela E nome do sócio
  - Ex: "REF. A PIX ENVIADO DANIELE GONCALVES GARCIA DIEDZITS (SOCIO JULIO CEZAR DIEDZITS)"

---

## Regras de Classificação de Recebimentos (Receita)

- **Pix recebido de pessoa física ou jurídica identificável como aluno/cliente direto** (mensalidade paga por Pix) → **conta 504** (CLIENTES DIVERSOS - SERVIÇOS). Esta é a conta padrão para receita via Pix — não usar a conta 411 para isso.
- **Recebimentos via intermediador de pagamento/cartão** — PJBANK PAGAMENTOS, PAGHIPER, Antecipação/Pagamento Cartão REDE (Visa/Master/Elo/Maestro) → **conta 531** (CLIENTES DIVERSOS - VENDAS). Padrão já validado, manter.
- **Valor de Pix recebido fora do padrão habitual de mensalidade** (muito acima do normal, ou de pessoa jurídica que não é claramente uma aluna) — não assumir automaticamente que é receita de serviço rotineira; sinalizar para o usuário/contadora, ou seguir a indicação já dada por ele para aquele nome específico em sessão anterior.
- **Estorno de mensalidade para pessoa física que também é pagante recorrente:** antes de lançar um envio de Pix para essa pessoa como pagamento a terceiro (conta 362), verificar se ela também tem recebimentos (pagamentos dela para a empresa) no mesmo período. Se tiver, é mais provável que seja estorno/devolução de mensalidade → lançar como **D-504 / C-Banco** (estorno de receita) em vez de D-362/C-Banco. Só manter a regra literal de pagamento a PF (362) se não houver recebimento correspondente dela no período.

## Regras de Classificação de Pagamentos (Despesa)

### Pessoa Física
- Qualquer pagamento a pessoa física → **conta 362** (Serviços Prestados por Terceiros)
- **Exceções:** sócio Julio e esposa Daniele têm regras próprias (ver acima); e o caso de estorno de mensalidade descrito acima

### Empresas (Pessoa Jurídica)
- Avaliar se a despesa **condiz com a atividade da Artsu** (academia de jiu-jitsu / comércio esportivo)
- Se condizer → conta conforme plano de contas (362, 356, 354, etc.)
- Se **não** condizer → lançar na conta que reflete a natureza real da despesa
  - Exemplo: supermercado/mercado/panificadora → **conta 521 (Despesas com Alimentação)**
- **Fornecedor PJ novo, sem classificação prévia confirmada na lista de recorrentes abaixo:** verificar o CNPJ/nome e avaliar primeiro se a despesa é de natureza administrativa/operacional genérica (mensalidade de sistema, taxa de associação, aluguel de equipamento, conta de consumo/utilidade, serviço distrital, etc.) — nesse caso lançar em **conta 359 (Despesas Administrativas)**. Reservar a **conta 493 (Despesas Diversas)** apenas para fornecedores já confirmados explicitamente na lista de recorrentes (ex: R.M. Empreendimentos, São João Farmácias) ou quando a contadora confirmar esse destino especificamente. Ou seja: 359 é o "catch-all" padrão para PJ não identificada; 493 é reservada para casos já validados.

---

## Regras Especiais — Transferências Internas entre Bancos

Quando há transferência entre contas da própria Artsu (ex: Nubank ↔ Santander):
- **Um único lançamento** direto banco a banco
- Santander → Nubank: **D-8 / C-34**
- Nubank → Santander: **D-34 / C-8**
- **NÃO usar conta 5 (CAIXA GERAL) como passagem**
- Identificar cruzando os dois extratos por valor + data + menção ao nome/CNPJ da própria Artsu no memo

---

## Regras Especiais — Pix no Crédito (Nubank)

Quando o Nubank usa cartão de crédito para pagar despesas (aparece como "Valor adicionado" no extrato):
1. **D-8 / C-357** — valor adicionado (crédito liberado pelo cartão)
   - Histórico: "REF. A VALOR ADICIONADO PIX CREDITO NUBANK - [FAVORECIDO]"
2. **D-Despesa / C-8** — pagamento da despesa

---

## Regras Especiais — iFood/Uber Estorno

Quando há entrada e estorno (iFood, Uber ou similar) no mesmo dia (zerando):
- Registrar **as duas movimentações** na mesma conta de despesa correspondente ao fornecedor (ex: 521 Alimentação para iFood, 537 Deslocamento para Uber)
- D-Banco/C-Despesa (entrada/devolução) e D-Despesa/C-Banco (estorno/pagamento original)

---

## DARF — Atenção ao Tipo de Tributo

Um DARF pago pela empresa **não é necessariamente Simples Nacional**. Antes de lançar em 479 (Simples Nacional a Recolher), conferir o comprovante/código de recolhimento:
- **Código 1099 (Contrib Prev Descontada de Segurado Contribuinte Individual)** = INSS sobre pró-labore do sócio → **conta 191 (INSS A RECOLHER)**, não 479
- Simples Nacional (DAS) → **conta 479**
- **Sempre separar em lançamentos distintos quando o comprovante discrimina:** principal na conta do tributo (191 ou 479), multa na **conta 352 (MULTAS DE MORA)**, juros na **conta 372 (JUROS DE MORA)** — nunca lançar o valor total do DARF em uma única conta se o comprovante mostra principal/multa/juros separados

---

## Classificações Recorrentes Confirmadas pelo Razão

| Fornecedor / Descrição | Conta |
|------------------------|-------|
| PJBANK PAGAMENTOS (recebimento) | 531 |
| PAGHIPER SERV ONLINE EIRELI (recebimento) | 531 |
| Cartão REDE (Visa/Master/Elo/Maestro) recebimento | 531 |
| Antecipação Credenciadora REDE | 531 |
| TIM S.A. | 356 |
| CLIENT CO SERVICOS DE REDE (Oi Fibra) | 356 |
| COPELDIS / Copel Distribuição | 354 |
| UBER DO BRASIL TECNOLOGIA | 537 |
| COMUNHÃO CRISTÃ ABBA | 366 |
| OPK VEST E ACESSORIOS | 506 |
| KIMONOS YAMA | 506 |
| MASTER CAMISETAS (2) | 506 |
| THALIS CONFECÇÕES | 506 |
| ERICK VIEIRA RODRIGUES (saídas) | 362 |
| LEICHINOSKI CIA LTDA | 362 |
| ALESSANDRA REGINA DIEDZITS | 362 |
| ROSANA APARECIDA CAMARGO | 362 |
| MARCIO POLONES ASSESSORIA | 362 |
| NATALINA ANZOLIN | 362 |
| ALEXANDRE DE OLIVEIRA JANUARIO | 362 |
| PJBANK (boleto taxa) | 357 |
| TUNA PAGAMENTOS LTDA | 357 |
| Cartão crédito (fatura/débito automático/boleto) | 357 |
| IOF / IOF Adicional | 533 |
| Tarifa Mensalidade / Tarifa Avulsa Pix / Tarifa Restritivo | 370 |
| Juros Saldo Utiliz Ate Limite | 372 |
| Rendimento Contamax | 432 |
| SAO JOAO FARMACIAS | 493 |
| STAR PROTECAO VEICULAR | 493 |
| R.M. EMPREENDIMENTOS IMOB (aluguel) | 493 |
| A F DOS SANTOS COMERCIO L (artigos banho/uso) | 493 |
| PIX MARKETPLACE (peças moto) | 493 |
| SERVIÇO DISTRITAL DO PINHEIRO(...) | 359 |
| CONNECTAMAIS | 359 |
| SANEPAR (água e esgoto) | 359 |
| CLICK LOC LOCAÇÕES DE EQUIPAMENTOS | 359 |
| FUNDO DE URBANIZAÇÃO | 359 |
| ASSOCIAÇÃO METROCARD | 359 |
| VITRU EDUCAÇÃO | 359 |
| Restaurante / Alimentação / Panificadora / Supermercado | 521 |
| GOVERNO DO PARANA (taxas) | 350 |
| HONORÁRIOS CONTÁBEIS (Paes e Bastos) | 510 |
| NOVA EMBALAGENS | 58 |
| POSTO AVENIDA BRASIL LTDA | 292 |
| VANESSA LEVANDOSKI DE CAMARGO (aluna — recebimento) | 504 |
| Empréstimo/Financiamento (Prest. De Emprest.) | 152 (principal; se o boleto discriminar juros, segregar em 372) |

---

## Fluxo de Trabalho

1. **Perguntar sobre o pró-labore do mês** antes de iniciar os lançamentos
2. **Receber arquivos:** extrato bancário (OFX ou PDF), relatório de gestão, folha de pagamento (quando houver), razão do banco
3. **Cruzar movimentações** por valor, data e nome do fornecedor/cliente
4. **Classificar** usando as regras acima e o histórico de classificações recorrentes
5. **Gerar TXT único** no leiaute Domínio (pagamentos + recebimentos juntos, ordenados por data)
6. **Sinalizar** lançamentos não identificados para revisão da contadora antes de finalizar — mas evitar jogar tudo em "Despesas Diversas" (493) por padrão; preferir 359 (Despesas Administrativas) como catch-all para PJ não identificada, conforme regra acima

---

## Observações Gerais

- Regras do sócio se aplicam em qualquer conta bancária, independente do banco
- Histórico dos lançamentos: usar fontes de referência (relatório de gestão, folha de pagamento, razão) — **NUNCA** o texto do extrato bancário, quando essas fontes estiverem disponíveis. Se só o extrato bancário for enviado, usar o memo do extrato (limpo de CPF/CNPJ) e sinalizar ao usuário que o histórico ideal viria do relatório de gestão/razão
- Usar o extrato que vier do banco (OFX ou PDF) — o que importa é ser **fiel a todas as movimentações**, sem omitir nenhuma
- Dúvidas ou divergências: pontuar para a contadora **ANTES** de prosseguir
- Cada empresa deve ser trabalhada em conversa separada

---

## Padrão ROF — Pró-labore, Retiradas e Relatório do Sócio

> Regra validada pela contadora Rosangela em 24/09/2026 para todas as empresas do escritório.
> As regras específicas desta empresa descritas acima **continuam valendo**. Este bloco completa o que faltar e **não substitui** nenhuma conta, exceção ou classificação já confirmada. Em caso de conflito, prevalece a regra específica da empresa.

### Parâmetros desta empresa

| Sócio | CPF | Pró-labore | Conta pró-labore a pagar | Conta do sócio (retirada / aporte) |
|---|---|---|---|---|
| Julio Cezar Diedzits | ver acima | Variável — perguntar todo mês | **188** | **532** |

> Pró-labore variável: perguntar o valor do mês e aplicar a regra com esse valor (substitui o antigo "lançar tudo na 532").

### Pergunta obrigatória antes de escriturar cada competência

> **Antes de lançar qualquer movimento do mês, perguntar à contadora e aguardar a resposta:**
> - Empresa **com** pró-labore → **"Qual o valor do pró-labore de <sócio> em <mês/ano>?"** (o valor pode variar de um mês para outro)
> - Empresa **sem** pró-labore → **"A empresa continua sem pró-labore em <mês/ano>?"**
>
> Aplicar a regra abaixo com o valor informado (base informada − INSS 11% = limite líquido).
>
> **Simples Nacional com Fator R:** o pró-labore é definido pela contadora conforme a estratégia do Fator R (folha de salários 12 meses ÷ receita bruta 12 meses ≥ 28% → Anexo III; abaixo → Anexo V). Ao perguntar, lembrar desse ponto e oferecer o cálculo do Fator R se a contadora enviar folha e receita dos últimos 12 meses. Nunca definir ou sugerir o valor do pró-labore por conta própria. Se a resposta mudar a situação da empresa (passou a ter ou deixou de ter pró-labore), registrar na tabela de parâmetros acima. Esta pergunta substitui qualquer tratamento antigo de "pró-labore variável" (confirmado pela contadora em 24/09/2026).

### Regra de lançamento

1. **Pró-labore líquido do mês** = valor bruto informado pela contadora para o mês − INSS 11%. **Não existe valor padrão**: o pró-labore varia por empresa e por mês. Nunca presumir salário mínimo nem repetir o valor do mês anterior. Valores fixos citados em outras partes desta skill (ex.: R$ 1.442,69) são apenas histórico ou exemplo — o limite do mês é sempre o informado pela contadora.
2. **Identificar o sócio pelo CPF** (ou nome completo) no favorecido. Sem identificação segura → sinalizar, não presumir.
3. **Acumular cronologicamente** todos os pagamentos ao sócio no mês, **somando todos os bancos**. Cada sócio tem seu próprio acumulado.
4. **Com pró-labore:**
   - Até completar o pró-labore líquido → **D conta de pró-labore a pagar / C banco**
   - O que exceder → **D conta do sócio (retirada) / C banco**
   - Pagamento único que atravessa o limite → **duas linhas `|6100|`** na mesma data (uma para cada débito), ambas creditando o banco, somando o valor total.
5. **Sem pró-labore:** toda saída ao sócio → **D conta do sócio / C banco**.
6. **Entrada do sócio na empresa** (devolução ou aporte) → **D banco / C conta do sócio** (reduz o saldo de retiradas).
7. **INSS do pró-labore** (DARF código 1099) → **D 191 (INSS a recolher) / C banco**, salvo conta diferente definida acima.
8. Pagamento ao sócio **nunca** vai para fornecedores, serviços de terceiros ou despesa.
9. **Provisão do pró-labore e do INSS NÃO entra no TXT** (D despesa / C pró-labore a pagar; D INSS / C 191). Ela é importada da **folha do Domínio**; não existe provisão manual. O TXT registra somente o **pagamento** (baixa). Esta regra prevalece sobre qualquer instrução antiga de provisão nesta skill (confirmado pela contadora em 24/09/2026).

### Relatório de Pró-labore e Retiradas — ENTREGA OBRIGATÓRIA

> Toda competência entrega **sempre dois arquivos juntos**: o TXT do Domínio **e** a planilha XLSX do sócio. O TXT nunca é entregue sozinho. Gerar sem esperar pedido — inclusive quando o mês não teve retirada (informar "sem movimentação do sócio no mês").

**Arquivo:** `<Empresa>_ProLabore_Retiradas_AAAAMM.xlsx` (se esta empresa já define nome ou formato próprio acima, usar o da empresa).

**Aba "Resumo"**
- Empresa, CNPJ, competência e bancos considerados
- Parâmetros: base do pró-labore, INSS 11% e pró-labore líquido
- Por sócio: total pago no mês · pró-labore pago (conta de pró-labore) · retiradas (conta do sócio) · devoluções/aportes · **retirada líquida do mês** · INSS recolhido no mês · pró-labore líquido não pago no mês (se o total pago ficou abaixo do limite)

**Uma aba por sócio**, uma linha por movimento, em ordem de data:
Data · Banco · Cód. conta bancária · Histórico do extrato · Tipo (Pró-labore / Retirada / Aporte-Devolução) · Valor · Acumulado no mês · Parcela pró-labore · Parcela retirada · Conta débito · Conta crédito

- Usar fórmulas: `Parcela pró-labore = MÍN(valor; limite − acumulado anterior)` e `Parcela retirada = valor − parcela pró-labore`
- Linhas divididas em duas no TXT aparecem como **uma linha** na planilha, com as duas parcelas preenchidas
- Aportes/devoluções com cor diferenciada; subtotais por tipo
- Nota de rodapé quando algum extrato estiver incompleto

**Conferência obrigatória antes de entregar:**
- Soma da planilha = soma das linhas do TXT nas contas de pró-labore e do sócio
- Nenhum pagamento ao sócio ficou fora do relatório
- Apresentar também no chat um resumo curto por sócio (pró-labore · retirada · aporte · líquido)
