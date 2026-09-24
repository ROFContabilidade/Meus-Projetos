---
name: rof-contabilidade-dck
description: "Corrige leiaute TXT Domínio (um |6000|X| por lançamento) e registra nome fantasia WEB41"
---

# ROF Contabilidade DCK — Lançamentos Contábeis e Conciliação

## Dados da Empresa

| Campo | Informação |
|---|---|
| Razão social | D C GRUP DUNK'S LTDA |
| Nome fantasia | WEB41 – AGÊNCIA DE MARKETING DIGITAL |
| CNPJ | 14.757.847/0001-20 |
| CNPJ sem formatação | 14757847000120 |
| CNAE principal | 6201-5/02 |
| CNAEs secundários | 1412-6/01 · 7319-0/03 |
| Setor | Serviços |
| Regime tributário | Lucro Presumido |
| Banco | EFI Bank — Conta 274012-5 → código contábil **8** |
| Cadastrado por | Rosangela |

## Sócios

| Sócio | CPF | Conta no Domínio |
|---|---|---|
| Denios da Cunha Leite | 074.775.859-02 | **566** (1.2.2.04.0101 — Sócios e Administradores) |

## Regras de Trabalho (ACORDO COM A CONTADORA)

1. **Fidelidade total** aos dados enviados — não alterar nada sem consultar
2. **Consulta prévia** antes de qualquer alteração de classificação
3. **Base legal** sempre que sugerir algum ajuste
4. **Histórico**: copiar exatamente do extrato bancário, mantendo o prefixo "REF. A" antes do texto

## Leiaute do Arquivo TXT para Domínio

> ⚠️ **REGRA OBRIGATÓRIA**: cada lançamento (`|6100|`) deve ter seu próprio bloco `|6000|X||||` imediatamente antes. Nunca agrupar múltiplos `|6100|` sob um único `|6000|` — o Domínio rejeita com erro "Não é permitido ter mais de um lançamento no tipo 'um débito para um crédito'".

```
|0000|14757847000120|
|6000|X||||
|6100|DD/MM/AAAA|CONTA_DEBITO|CONTA_CREDITO|VALOR||HISTORICO||||
|6000|X||||
|6100|DD/MM/AAAA|CONTA_DEBITO|CONTA_CREDITO|VALOR||HISTORICO||||
```

- **Pagamento (saída):** débito na conta de despesa/ativo, crédito no banco (8)
- **Recebimento (entrada):** débito no banco (8), crédito na conta de receita/ativo
- **Arquivo único:** pagamentos e recebimentos ordenados por data — NÃO gerar dois arquivos separados
- Valor com vírgula decimal: ex. `1500,00`

## Plano de Contas — Contas Operacionais

| Cód | Classificação | Nome | Natureza |
|---|---|---|---|
| **8** | 1.1.1.02.001 | Banco EFI Bank - Conta 274012-5 | Ativo |
| **504** | 1.1.2.01.001 | Clientes Diversos | Ativo |
| **566** | 1.2.2.04.0101 | Denios da Cunha Leite (sócio) | Ativo NC |
| **506** | 2.1.3.01.001 | Fornecedor Modelo | Passivo |
| **510** | 2.1.6.02.001 | Honorários Contábeis | Passivo |
| **173** | 2.1.4.01.003 | ISS a Recolher | Passivo |
| **176** | 2.1.4.01.006 | Imposto de Renda a Recolher | Passivo |
| **177** | 2.1.4.01.007 | Contribuição Social a Recolher | Passivo |
| **179** | 2.1.4.01.009 | PIS a Recolher | Passivo |
| **180** | 2.1.4.01.010 | COFINS a Recolher | Passivo |
| **573** | 2.3.5.01.006 | Distribuição de Lucros | Patrimônio Líquido |
| **292** | 3.1.2.07.001 | Combustível | Custo |
| **521** | 3.2.2.01.012 | Despesas com Alimentação | Despesa |
| **356** | 3.2.2.04.003 | Telefone | Despesa |
| **357** | 3.2.2.04.004 | Suporte em Informática | Despesa |
| **362** | 3.2.2.04.009 | Serviços Prestados por Terceiros | Despesa |
| **550** | 3.2.2.05.009 | Tarifas Bancárias | Despesa |
| **596** | 3.2.2.04.016 | Despesa com Cartão de Crédito | Despesa |
| **411** | 4.1.1.02.001 | Serviços Prestados | Receita |

## Regra de Classificação das Contrapartes — LEIA ANTES DE CLASSIFICAR

### Para cada lançamento do extrato, siga esta ordem:

1. Identifique o favorecido (nome, CNPJ/CPF)
2. Se for **Denios da Cunha Leite** → aplicar **Regra de Retiradas/Devoluções do Sócio**
3. Se tiver CNPJ → pesquisar no portal da Receita Federal (https://www.receita.fazenda.gov.br/PessoaJuridica/CNPJ/cnpjreva/Cnpjreva_Solicitacao2.asp) → verificar atividade → classificar conforme plano
4. Se for Pessoa Física (exceto sócio) → verificar natureza do pagamento e classificar conforme plano
5. **Histórico**: copiar exatamente do extrato bancário mantendo "REF. A" no início

## Regra Inviolável — Conferência de Saldo Antes da Entrega

> **Nunca entregar o TXT sem que os saldos do extrato estejam fechando.**

Antes de gerar o arquivo final, conferir obrigatoriamente:

1. Saldo anterior (abertura) informado no extrato
2. Saldo final (encerramento) informado no extrato
3. Diferença esperada = Saldo final − Saldo anterior
4. Somar todas as entradas lançadas no TXT
5. Somar todas as saídas lançadas no TXT
6. Diferença apurada = Total entradas − Total saídas

Se Diferença apurada ≠ Diferença esperada → **NÃO entregar o TXT**. Identificar e corrigir a divergência antes de qualquer entrega.

## Regra Inviolável — Aplicações Financeiras e Rendimentos

> Esta empresa **não possui aplicação financeira cadastrada**. Verificar no plano de contas a cada competência se isso mudou.

## Regra Inviolável — IOF e IRRF

> **Nunca omitir IOF do TXT.**

### IOF
- Conta: **550** (Tarifas Bancárias) — lançar com histórico contendo "IOF"
- Lançar separadamente — não embutir no valor principal

### IRRF
- Não identificado no razão Jan–Jun/2026. Se aparecer no extrato, sinalizar para a contadora antes de classificar.

## Regra Mensal — Retiradas e Devoluções do Sócio

> Esta empresa **não possui pró-labore estruturado**. Todas as movimentações do sócio seguem a regra de retirada direta.

### Denios da Cunha Leite — Conta 566

**Retirada (saída do banco para o sócio):**

| Débito | Crédito |
|---|---|
| **566** (Denios da Cunha Leite) | **8** (EFI Bank) |

**Devolução / Aporte (entrada do sócio para o banco):**

| Débito | Crédito |
|---|---|
| **8** (EFI Bank) | **566** (Denios da Cunha Leite) |

> O crédito na conta 566 (ativo) **reduz o saldo devedor** que o sócio tem com a empresa. Não há limite ou teto — todo valor enviado ao sócio vai para 566, independente do montante.

> ANTES DE LANÇAR: confirmar com a contadora o total pago no mês e se houve pagamentos parciais.

## Regra — Pagamento de Tributos (Lucro Presumido)

Os tributos **passam pelo extrato bancário**. Ao identificar pagamento de tributo, classificar:

| Tributo | Débito | Crédito |
|---|---|---|
| IRPJ | **176** | **8** |
| CSLL | **177** | **8** |
| PIS | **179** | **8** |
| COFINS | **180** | **8** |
| ISS | **173** | **8** |

> Identificar pelo histórico do extrato (ex.: "DARF", "ISS", "PIS/COFINS"). Sinalizar para a contadora antes de lançar qualquer tributo com histórico ambíguo.

## Particularidades do Banco — EFI Bank

### Tarifas de Confirmação Boleto / Bolix
- Saída → D **550** (Tarifas Bancárias) / C **8**
- Histórico: copiar conforme extrato ("REF. A TARIFA CONFIRMACAO BOLETO...")

### IOF
- Saída → D **550** (Tarifas Bancárias) / C **8** — com histórico contendo "IOF"

### Cartão EFI Final 9490

**Recarga (saída do banco para o cartão):**
- D **356** (Telefone) / C **8**
- Histórico: "REF. A RECARGA PARA CARTAO EFI FINAL 9490..."

**Resgate (entrada do cartão de volta ao banco):**
- ⚠️ **PENDENTE** — não ocorreu no extrato 07/2026. Confirmar com a contadora quando aparecer.
- No razão Jun/2026, o resgate apareceu classificado em **596** (Despesa com Cartão de Crédito), mas a regra definitiva ainda não foi confirmada.
- **Não lançar o resgate sem consultar a contadora.**

### Pagamento de Fatura Cartão de Crédito
- Saída → D **596** (Despesa com Cartão de Crédito) / C **8**
- Histórico: "REF. A PAGAMENTO DE FATURA CARTAO DE CREDITO MES REFERENCIA MM/AAAA"

## Classificações Recorrentes Confirmadas pelo Razão (Jan–Jun/2026)

| Favorecido / Descrição | Conta | Natureza |
|---|---|---|
| Denios da Cunha Leite (entrada — aporte) | **566** (C) | Devolução sócio |
| Denios da Cunha Leite (saída — retirada) | **566** (D) | Retirada sócio |
| Centerrol Indústria e Com | **504** | Cliente |
| Sindicato de Hotéis e Similares de Curitiba | **504** | Cliente |
| PF F L Eireli ME | **504** | Cliente |
| Associação M Paraná | **504** | Cliente |
| Contabil Sologica Contadores Associados SS Ltda ME | **504** | Cliente |
| Jornal Aqui Regional Ltda / Eireli | **504** | Cliente |
| De Biasi Sociedade Individual de Advocacia | **504** | Cliente |
| Seripar Comunicação Visual Ltda | **504** | Cliente |
| SWT Teleinformática e Manutenção Ltda | **504** | Cliente |
| Cunha Assessoria Jurídica Ltda | **504** | Cliente |
| Silsi de Oliveira Mendes H Barbosa Soc. Individual de Advocacia | **504** | Cliente |
| Moldurama Imp Exp Ltda / Moldurama do Brasil Ind e Com | **504** | Cliente |
| Idealmed Clínica Médica e Segurança do Trabalho Ltda | **504** | Cliente |
| Distribuidora Real Econômico Ltda | **504** | Cliente |
| RT Comércio Importação e GF Ltda | **504** | Cliente |
| Thiago Calandrini Soc. Individual de Advocacia | **504** | Cliente |
| Lemes Teixeira Socie (Soc. Individual) | **504** | Cliente |
| Fonseca Alves Tecnologia Ltda | **504** | Cliente |
| Vinicola Araucária Ltda | **504** | Cliente |
| Odesclean Odontologia e Estética Ltda | **504** | Cliente |
| Água Dourada Distribuidor / Distribuidora de Alimentos Ltda | **504** | Cliente |
| Clube de Benefícios A Aproville | **504** | Cliente |
| Paypal do Brasil Instituição de Pagamento Ltda | **504** | Cliente |
| BOM Mineiro Distribuidora de Alimentos Ltda | **504** | Cliente |
| Matheus Cajaiba Soc. Individual de Advocacia | **504** | Cliente |
| Handel Equipamentos e Locação Ltda | **504** | Cliente |
| Renata Bastos Amado | **510** | Honorários Contábeis |
| Lapola Serviços Administrativos Ltda | **506** | Fornecedor |
| Baratão Combustíveis | **292** | Combustível |
| Arcos Dourados Comércio de Alimentos SA (McDonalds) | **521** | Alimentação |
| TIM S.A. | **356** | Telefone |
| Recarga Cartão EFI Final 9490 | **356** | Telefone |
| Tarifas confirmação boleto / bolix | **550** | Tarifas Bancárias |
| Pagamento Fatura Cartão de Crédito | **596** | Cartão de Crédito |

## Fluxo de Trabalho

1. Receber extrato bancário (PDF, CSV ou OFX) e confirmar período
2. Para cada lançamento:
   - a. Identificar natureza (entrada/saída)
   - b. Identificar favorecido
   - c. Aplicar regras de classificação na ordem acima
   - d. Registrar histórico copiando do extrato (com "REF. A")
3. Sinalizar lançamentos não identificados para revisão **antes** de finalizar
4. Verificar IOF e tributos — nada pode ficar de fora
5. Conferir saldo: entradas − saídas = variação do extrato
6. Gerar TXT único ordenado por data, com `|6000|X||||` antes de cada `|6100|`

## Parâmetros Adicionais

- O razão (Jan–Jun/2026) serve como referência histórica de classificação
- Qualquer dúvida ou divergência: pontuar para a contadora ANTES de prosseguir
- Cada empresa deve ser trabalhada em conversa separada
- Não há funcionários CLT nesta empresa

## Pendências a Confirmar com a Contadora

- [ ] **Resgate Cartão EFI Final 9490**: não ocorreu em 07/2026 — confirmar classificação quando aparecer (no razão Jun/2026 apareceu em conta 596 — confirmar se é regra definitiva ou exceção)
- [ ] **IRRF**: não identificado no período Jan–Jul/2026 — se aparecer no extrato, consultar contadora antes de classificar

---

## Padrão ROF — Pró-labore, Retiradas e Relatório do Sócio

> Regra validada pela contadora Rosangela em 24/09/2026 para todas as empresas do escritório.
> As regras específicas desta empresa descritas acima **continuam valendo**. Este bloco completa o que faltar e **não substitui** nenhuma conta, exceção ou classificação já confirmada. Em caso de conflito, prevalece a regra específica da empresa.

### Parâmetros desta empresa

| Sócio | CPF | Pró-labore | Conta pró-labore a pagar | Conta do sócio (retirada / aporte) |
|---|---|---|---|---|
| Denios da Cunha Leite | ver acima | **Não há** | — | **566** |

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
