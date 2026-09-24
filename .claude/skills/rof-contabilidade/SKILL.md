---
name: rof-contabilidade
description: "Motor genérico de lançamentos e conciliação para todas as empresas do escritório ROF Contabilidade, com lista atualizada de empresas cadastradas."
---

# ROF Contabilidade — Motor de Lançamentos e Conciliação

Este é o **motor genérico** do escritório. Ele contém o fluxo de trabalho, o leiaute do arquivo Domínio e as regras comuns a **todas** as empresas. As particularidades de cada cliente (CNPJ, regime, plano de contas, contas bancárias) ficam em `references/<empresa>.md`.

## Como usar este motor

1. **Identifique a empresa** da conversa (o usuário informa, ou infere-se pelo CNPJ/nome nos arquivos).
2. **Carregue o arquivo da empresa** em `references/<empresa>.md` e siga as particularidades de lá.
3. Se **não existir** arquivo para a empresa, colete os dados cadastrais e **crie um novo** a partir de `references/_MODELO.md`, confirmando com o usuário antes.
4. Aplique o **fluxo de trabalho** e o **leiaute** abaixo.

> Cada empresa deve ser trabalhada em **conversa separada**.

## Leiaute do Arquivo TXT para Domínio
```
|0000|CNPJ_SEM_FORMATACAO|
|6000|X||||
|6100|DD/MM/AAAA|CONTA_DEBITO|CONTA_CREDITO|VALOR||HISTORICO||||
```
- Linha `|0000|` = identificação da empresa (CNPJ sem formatação)
- Linha `|6000|X||||` = separador entre lançamentos
- Linha `|6100|` = lançamento: data, conta débito, conta crédito, valor, histórico
- Conta **8** = conta bancária (salvo exceções por empresa)
- **Pagamento (saída):** débito na conta de despesa, crédito no banco (8)
- **Recebimento (entrada):** débito no banco (8), crédito na conta de receita
- **Arquivo único:** pagamentos e recebimentos compilados juntos, ordenados por data (sem separação em dois arquivos)

## Regras de Trabalho (ACORDO COM A CONTADORA)
1. **Fidelidade total** aos dados enviados pela contadora — não alterar nada sem consultar
2. **Consulta prévia** antes de qualquer alteração
3. **Base legal** sempre que sugerir algum ajuste

## Fluxo de Trabalho
1. **Receber arquivos da contadora (até 20 por interação, 50MB cada):**
   - Extrato bancário (PDF ou OFX)
   - Plano de contas (Excel)
   - Relatório de gestão do cliente
   - Folha de pagamento (quando aplicável)
   - Razão do banco dos últimos 3 meses (parâmetro de classificação)
   - *Ressalva de precisão:* arquivos pesados (ex.: extrato longo + razão de 3 meses) devem ser enviados em lote menor para preservar a fidelidade do cruzamento — recomendação técnica, não regra rígida.
2. **Cruzar movimentações do extrato com as fontes de referência:**
   - Buscar correspondência por valor, data e/ou nome do fornecedor/funcionário
   - Utilizar o histórico do relatório de gestão ou folha de pagamento (NUNCA do extrato bancário)
   - Se for pagamento de funcionário, cruzar com a folha de pagamento
3. **Classificar no plano de contas** (usar o plano específico da empresa):
   - Adiantamento de salário → conta de adiantamento (Ativo Circulante)
   - Pagamento da folha → conta de salários a pagar/remunerações (Passivo/Despesa)
   - Fornecedores, tarifas, impostos, etc. → conforme plano de contas da empresa
4. **Gerar TXT único** no leiaute Domínio (pagamentos + recebimentos juntos)
5. **Sinalizar** lançamentos não cruzados para revisão da contadora antes de finalizar

## Regra Padrão do Escritório — Pró-labore, Retiradas e Relatório do Sócio

> Validada pela contadora Rosangela em 24/09/2026. Vale para **todas** as empresas. Cada skill de empresa traz o bloco "Padrão ROF — Pró-labore, Retiradas e Relatório do Sócio" com os sócios e contas dela.

1. **Pergunta obrigatória antes de escriturar cada competência** (aguardar resposta):
   - Empresa com pró-labore → "Qual o valor do pró-labore de <sócio> em <mês/ano>?" (pode variar mês a mês)
   - Empresa sem pró-labore → "A empresa continua sem pró-labore em <mês/ano>?"
2. **Pró-labore líquido** = valor bruto informado pela contadora no mês − INSS 11%. **Não existe valor padrão** — varia por empresa e por mês, em especial no Simples Nacional com Fator R (folha 12m ÷ receita bruta 12m ≥ 28% → Anexo III). Nunca presumir salário mínimo nem repetir o mês anterior; oferecer o cálculo do Fator R quando a contadora enviar folha e receita de 12 meses.
3. **Acumular** os pagamentos a cada sócio no mês, em ordem de data, **somando todos os bancos**; sócio identificado por CPF.
4. Até o líquido → **D pró-labore a pagar (188) / C banco**; excedente → **D conta do sócio / C banco**; pagamento que atravessa o limite vira **duas linhas `|6100|`**.
5. Sem pró-labore → toda saída ao sócio **D conta do sócio / C banco**.
6. Entrada do sócio (devolução/aporte) → **D banco / C conta do sócio**.
7. INSS do pró-labore (DARF 1099) → **D 191 / C banco**.
8. **Provisão do pró-labore e do INSS não entra no TXT** — é importada da folha do Domínio. O TXT registra só o pagamento.
9. **Relatório XLSX de Pró-labore e Retiradas é entrega obrigatória junto com todo TXT**, mesmo sem movimentação do sócio no mês: aba Resumo (parâmetros e totais por sócio: pró-labore, retiradas, aportes, retirada líquida, INSS, pró-labore não pago) + uma aba por sócio com cada movimento, acumulado e rateio por fórmula. A soma da planilha deve bater com as linhas do TXT nas contas de pró-labore e do sócio.

## Regra Padrão do Escritório — Quem recebeu ou pagou (análise de favorecido)

> Validada pela contadora Rosangela em 24/09/2026. Analisar **cada lançamento como analista contábil experiente**, não só por palavra-chave.

1. **Pessoa física** que não é sócio nem colaborador → **362 (Serviços Prestados por Terceiros)**. Sócio → regra de pró-labore/retirada. Colaborador (lista CLT da skill da empresa ou pasta Folha de PGTO) → salários a pagar (187).
2. **CNPJ identificado no extrato** → **consultar a atividade (CNAE) do CNPJ** e julgar se é fornecedor coerente com o ramo da empresa:
   - Coerente (ex.: confecção pagando malharia; loja de roupa pagando atacado de vestuário) → **conta de fornecedores** (506, ou a conta de fornecedor definida na skill da empresa).
   - Não coerente → classificar pela **natureza da despesa**. Ex.: transportadora pagando farmácia → despesas diversas; supermercado/padaria → alimentação; posto → combustível/deslocamento; salão/estética → despesas diversas; advogado/software/cobrança → serviços de terceiros ou despesas administrativas.
3. A atividade do CNPJ **prevalece sobre o histórico** quando o histórico não fizer sentido para o ramo. Toda reclassificação vai para a aba "Conferir" com a atividade encontrada.

## Regra Padrão do Escritório — Transferências entre Contas da Própria Empresa

- Processar todos os extratos da empresa juntos e parear saída × entrada (mesmo valor, data D+0/D+1, CNPJ próprio ou "mesma titularidade").
- **Lançamento único direto: D banco destino / C banco origem.** Ignorar a contrapartida no outro extrato (não lançar em dobro). Nunca em conta de resultado.
- Par que não fecha (sem contrapartida ou valor diferente) → pendência para a contadora.

## Regra Padrão do Escritório — Impostos: conferir sempre na pasta Guias

> Definida pela contadora Rosangela em 24/09/2026. Vale para **todas** as empresas.

- Todo pagamento de imposto no extrato (DAS, INSS/DCTFWeb, FGTS, ICMS antecipado/ST, GR-PR, GNRE, DARF etc.) deve ser **identificado pela guia** na pasta `Guias` antes de classificar.
- Ao lançar a competência **MM/AAAA**, olhar as guias da **competência anterior** (MM−1), porque o imposto apurado num mês é pago no mês seguinte. Ex.: lançando 08/2026 → pasta `07_2026\Guias`. Se o valor não bater, procurar também em meses anteriores (guias pagas em atraso, com multa e juros).
- Conferir valor, vencimento e composição (principal, multa, juros). Guia paga com atraso: registrar a composição na aba "Conferir".
- Guia do mês anterior que **não aparece paga** no extrato → sinalizar à contadora (possível débito em aberto).
- Pagamento de imposto sem guia correspondente → sinalizar; não presumir o tributo pelo valor.

## Regra Padrão do Escritório — Leitura de Extratos em PDF (Python 3.12)

> Combinado com a contadora Rosangela em 24/09/2026. **Nunca** subir extrato para site de conversão (sigilo/LGPD) e **não** ler o PDF como imagem.

- **No PC do escritório (Claude desktop):** usar o **Python 3.12** instalado (winget, python.org) com `pdfplumber` e `openpyxl`, e as rotinas em `G:\Meu Drive\Trabalho ROF\Diversos\rotinas\`:
  - `pdf_texto.py arquivo.pdf [saida.txt]` → extrai o texto do PDF localmente (linhas com data, histórico, CPF/CNPJ, valor, saldo)
  - `ler_ofx.py arquivo.ofx` → transações + saldo final do OFX
  - `motor_lancamentos.py` → gera o TXT Domínio (`|0000|`, `|6000|X||||`, `|6100|`), planilha de sócios e `conferir_saldo()` por banco
  - scripts por empresa em `rotinas\empresas\<empresa>_AAAAMM.py`
- **Em sessão na nuvem (sem acesso ao PC):** ler o PDF como **texto** pelo conector do Google Drive (`read_file_content`) ou, se o arquivo for enviado na conversa, com `pdfplumber` na própria sessão.
- Com OFX e PDF do mesmo banco: **OFX para os lançamentos, PDF para os saldos**.
- PDF escaneado/foto (sem texto): avisar a contadora e pedir o PDF baixado do app/internet banking ou o OFX.
- Em qualquer caso, o TXT só é entregue com o **saldo fechando no centavo por banco**.

## Parâmetros Adicionais
- Razão do Banco dos últimos 3 meses como referência histórica de classificação
- Qualquer dúvida ou divergência: pontuar para a contadora ANTES de prosseguir
- Caso exceda 20 arquivos: processar em duas mensagens dentro da mesma conversa

## Empresas cadastradas
Cada skill de empresa contém o plano de contas, regras de sócios e classificações confirmadas.

| Skill | Empresa | Regime | Banco |
|---|---|---|---|
| `rof-contabilidade-aptransportes` | ADRIANA PINHEIRO TRANSPORTES LTDA — AP TRANSPORTES (CNPJ 46.293.830/0001-55, transporte) | Simples Nacional | Sicredi / Nu Financeira / C6Bank |
| `rof-contabilidade-artsu` | ARTSU BRAZILIAN JIU-JITSU LTDA (CNPJ 36.021.287/0001-83) | Simples Nacional | — |
| `rof-contabilidade-cosmetici` | COSMETICI (indústria de cosméticos) | Lucro Presumido | — |
| `rof-contabilidade-edificio-violeta` | EDIFICIO VIOLETA (CNPJ 52.178.386/0001-20, condomínio edilício) | — | Cora / Sicoob (aplicação) |
| `rof-contabilidade-dck` | DCK / WEB41 | — | — |
| `rof-contabilidade-fwsgoncalves` | F W S GONCALVES LTDA (CNPJ 22.147.527/0001-86, móveis) | Simples Nacional | Sicredi / SicrediInvest |
| `rof-contabilidade-imperiobaggio` | MARIA P S BAGGIO RESTAURANTE — Império Baggio (CNPJ 20.632.522/0001-13) | Simples Nacional | Sicredi |
| `rof-contabilidade-jar-almeida` | J A R DE ALMEIDA LTDA (CNPJ 59.888.774/0001-43, doces) — ROF 110 Cacau Ribeiro (BR Cacau); não é a 85 Letícia Doces | Simples Nacional | — |
| `rof-contabilidade-kopp` | INSTITUTO KOPP S/S LTDA. (CNPJ 08.109.599/0001-08, clínica odontológica) | Lucro Presumido | Sisprime / Stone |
| `rof-contabilidade-lucasromano` | LUCAS ROMANO SANTOS LTDA (CNPJ 43.534.615/0001-00, serviços) | Simples Nacional | Nubank |
| `rof-contabilidade-lumus` | LUMUS ESPECIALIDADES TERAPÊUTICAS (CNPJ 50.724.260/0001-88, saúde) | Simples Nacional | Mercado Pago |
| `rof-contabilidade-mohrgroup` | MOHR GROUP | — | — |
| `rof-contabilidade-ribeiro` | RIBEIRO FAST FASHION LTDA — Guria Chic | — | — |