---
name: rof-fiscal-motor-industria
description: Motor fiscal mensal para qualquer empresa INDUSTRIAL da ROF Contabilidade (Lucro Presumido/Real, Domínio). Do XML ao TXT de importação no Domínio - classifica cada item comprado pela atividade (insumo, embalagem, ferramenta, uso e consumo, revenda, ativo), decide crédito de ICMS/IPI, DIFAL e ICMS antecipado, trata canceladas, inutilizadas, CT-e e NFS-e com retenções, gera as planilhas de conferência e o TXT EFD que o Domínio aceita, e corrige pelo relatório de erros da importação. Usar quando for cadastrar uma indústria nova no motor fiscal, rodar o fechamento fiscal de uma indústria, gerar o TXT de importação de notas, ou analisar o relatório de erros/advertências da importação do Domínio. Piloto - Kopp Indústria (skill rof-fiscal-kopp-industria).
---

# Motor fiscal — indústria (XML → conferência → TXT Domínio)

Código em `Fiscal/scripts/`, regras por empresa em `Fiscal/empresas/<cod>-<nome>/regras.json`, modelo em
`Fiscal/empresas/_modelo-industria/regras.json`. Resultados do mês em `Fiscal/empresas/<cod>-<nome>/<AAAA-MM>/`
(pasta fora do git: dados de cliente nunca vão para o GitHub — só código e regras).
Passo a passo técnico dos scripts: skill `rof-fiscal-conferencia-notas`. Caso piloto: `rof-fiscal-kopp-industria`.

## 1. Empresa nova
1. `python3 Fiscal/scripts/nova_empresa.py --codigo <cód Domínio> --nome "..." --cnpj ... --uf PR --atividade "..."`
2. Preencher os campos `CONFERIR` do regras.json criado:
   - `empresa.atividade`: o que fabrica (NCM) e o que revende — é o critério de todo crédito.
   - acumuladores (`compras`, `compras_com_st`, `outras_operacoes`, `devolucoes_proprias`, `saidas`, `cte`,
     `servicos`): do "Resumo por acumulador" do Domínio e do 0400 do SPED anterior.
   - `contas_padrao` e contas de serviço: plano de contas da empresa (código reduzido no início).
   - `perfil_venda.capitulos`: capítulo NCM do que ela vende (x101 → INSUMO, x102 → REVENDA).
3. Pedir ao cliente/escritório: SPED ICMS/IPI de um mês já entregue (cabeçalho do TXT), Acompanhamento de
   Entradas dos meses anteriores (histórico), Resumo por acumulador, razão (contas por fornecedor), relatório de
   notas do ERP, lista de NFS-e recebidas, XML do mês (zip do cliente + DownloadDFe da SEFAZ).
4. 1ª rodada sai cheia de `FINALIDADE A DEFINIR`: propor, perguntar só a dúvida real, e gravar cada resposta
   como regra (`finalidade_por_item` / `_por_fornecedor` / `_por_ncm` / `_por_descricao`) + linha em `_decisoes`.

## 2. Rodada mensal
1. Pré-conferência (modo sem SPED) → `Pre_Conferencia_*.xlsx` com pendências; resolver as VERIFICAR.
2. Entregar à analista: `Entradas_para_conferencia` (aba "Todas as notas" + dentro/fora do estado, CT-e,
   serviços tomados com retenção em vermelho), `Saidas_MM-AAAA` (uma aba, por data de saída; canceladas em
   vermelho, inutilizadas em cinza), relação de acumuladores em uso.
   Relatório de serviços tomados `Servicos_Tomados_MM-AAAA.xlsx` (`relatorio_servicos.py`, sai sozinho com
   `--nfse-recebidas`) — modelo aprovado: LIMPO E CONCISO, nada que atrase a analista:
   - Resumo: com retenção / sem retenção / total a lançar / não lançar (notas, valor, cada imposto retido,
     total retido) + guias a recolher (IRRF DARF 1708 — 8045 propaganda via `servicos.darf_irrf_por_item`;
     PIS/COFINS/CSLL DARF 5952; INSS DCTFWeb; ISS guia do município), vencimento dia 20 do mês seguinte ao
     pagamento, EFD-Reinf R-4020 no mês do pagamento.
   - Todas as notas · Com retenção (valor, cada imposto, total retido, líquido a pagar, guia) · Sem retenção
     (observação só quando a retenção era esperada). Vermelho = com retenção, verde = sem, cinza = não lançar.
   - Só colunas de imposto que tiveram valor no mês; CSRF aberto em PIS 0,65 / COFINS 3 / CSLL 1.
3. `--txt-cabecalho <SPED anterior>` → `IMPORTACAO_DOMINIO_MMAAAA.TXT` + `_conferencia.xlsx`
   (+ `_SEM_NOTAS_DO_ZIP.TXT` se houver `importar_por_xml`, + `_CORRECAO.TXT` se houver `reimportar`).
4. Canceladas: zip só com os XML delas (nota + evento 110111) para subir pelo XML; relatório Excel
   Canceladas e inutilizadas (entrada/saída, protocolo, justificativa).
5. Importar → ler o relatório de erros (PDF) → corrigir o motor, nunca o arquivo à mão → repetir.
6. Depois da importação, conferir os totais (crédito ICMS/IPI das entradas, ICMS/IPI/DIFAL das saídas) com a
   planilha de confronto. Qualquer valor "estranho" → revisar nota a nota (base x alíquota x crédito).

## 3. Regras gerais de crédito (indústria)
| Finalidade | Crédito ICMS | Crédito IPI | Observação |
|---|---|---|---|
| INSUMO (matéria-prima, componente) | sim | sim | o que integra o produto fabricado |
| EMBALAGEM do produto vendido | sim | sim | pouch, tyvek, etiqueta de rastreabilidade, caixa de envio |
| FERRAMENTA de usinagem | prática do escritório: sim | sim | sinalizar: muitos fiscos tratam como uso e consumo |
| REVENDA (x102) | sim, se a saída é tributada | só se a empresa destaca IPI na revenda | conta de mercadoria para revenda |
| USO E CONSUMO (1556/1407/2556) | **não** | não | base e ICMS zerados; fora do estado gera **DIFAL** a recolher |
| ATIVO | CIAP | não | DIFAL se de fora |
| Bonificação recebida (1910) | conforme decisão da empresa (Kopp: sim) | — | |
- Crédito = **ICMS efetivamente cobrado**: diferimento parcial (CST 51) usa o vICMS, não base x 19,5%.
- Fornecedor do Simples: só com CSOSN 101 (vCredICMSSN/pCredSN); 102 não dá crédito.
- Entrada a 4% (importado) com crédito → ICMS antecipado (PR: 8% sobre a BC; E111 PR000080/PR020212).
- Item da atividade? Ver como a própria empresa fatura o mesmo item (perfil_venda) e se a saída é tributada.
- CT-e: só lança quando a empresa é a **tomadora**; com ICMS → acumulador com crédito, sem ICMS → sem.
- NFS-e: acumulador pelo item da LC 116; retenção (IRRF 1,5%, CSRF 4,65%, INSS, ISS) só escolhe entre
  acumuladores do mesmo item; notas com retenção vão para a EFD-Reinf (R-4020, mês do pagamento).
- XML prevalece sobre o relatório do ERP. Nunca afirmar irregularidade sem evidência na linha.

## 4. Documentos especiais
- **Cancelada** (evento 110111 / lista SEFAZ): lançar zerada, só participante e chave. Pelo TXT o Domínio
  troca o participante → `txt_importacao.canceladas = lancar_manual` e subir pelo XML.
- **Inutilizada**: número da série sem XML, sem SEFAZ e sem chave no relatório do ERP → C100 COD_SIT 05 na
  data das notas vizinhas. Se o ERP tem pedido com cliente/valor no número → amarelo + relatório para o cliente
  confirmar se a mercadoria saiu (e se inutilizou na SEFAZ — prazo até o dia 10 do mês seguinte).
- Série sem nenhuma NF-e (modelo 01 no ERP) não é NF-e: tratar como "ERP x fiscal", não inutilizar.
- Nota ativa cujo XML só veio no DownloadDFe (fora do zip do cliente): avisar e entregar o XML à parte.

## 4b. REGRA DE OURO: o TXT é fiel ao XML (Rosangela 13/10/2026)
CST, base, alíquota e valor de ICMS, ST e IPI vão EXATAMENTE como no XML, item a item — nada é recalculado nem
"ajustado" para o Domínio. Ex.: diferimento parcial no PR (CST 51, 19,5% com diferimento, ICMS cobrado 12%) vai com
base cheia, 19,5% e o vICMS do XML; Simples (CSOSN 101) com valor do item, pCredSN e vCredICMSSN; base de ICMS com
imposto zero (CST 00 do ERP) e base de IPI com IPI zero também vão (IPI só base: CST 49 na entrada — exige IPI no
acumulador). Únicas diferenças permitidas = regras de crédito do escritório (uso e consumo sem crédito: base/ICMS
zerados; IPI sem crédito no custo do item), e o valor da nota nunca muda. A aba "Conferência com o XML" do
_conferencia.xlsx compara campo a campo; qualquer "DIVERGENTE DO XML" bloqueia a entrega até ser corrigido no motor.
Validado: nota do Simples (Kopp 2153) importada fiel ao XML ficou correta no Domínio (13/10/2026).
IBS/CBS: o leiaute EFD ICMS/IPI aceito pelo Domínio não tem campo; ficam no XML (o Domínio lê ao importar XML).

## 5. TXT de importação no Domínio — o que aprendemos (Kopp 09/2026, aceito sem erros em 12/10/2026)
Leiaute EFD ICMS/IPI (latin-1, CRLF), modelo aceito = EFD da Ectas 08/2026. Erro do relatório → causa → correção:

| Mensagem do Domínio | Causa | Correção no motor |
|---|---|---|
| Nenhuma espécie para o modelo 01 / acumulador não definido / chave em branco | NFS-e como C100 mod. 01 sem espécie relacionada | `incluir_nfse=false` (ou relacionar 01 → espécie de serviço no Domínio) |
| CST do ICMS inválido "5101" | origem + CSOSN | CSOSN sem a origem |
| Valor contábil difere do somatório | Domínio rateia frete/seguro/outras pelo valor do item e confere cada C190 | C170 em todas as NF-e e C190 = item − desconto + rateio + IPI + ST |
| O imposto 2 não está relacionado no acumulador X | CST de IPI informado sem IPI | IPI sem crédito vai para o custo do item, CST IPI vazio |
| Valor do ICMS difere do valor contábil (diferença = frete) | frete fora do C190 | idem rateio |
| CEST inválido / incompatível com NCM | CEST do fornecedor | sem CEST no 0200 |
| Produto não aceita unidade diferente | Domínio corta o código em 14 caracteres → colisão | código de 10 caracteres (hash CNPJ+código+unidade) |
| Cancelada com participante errado / CFOP 2411 / "fornecedor 0,00" | Domínio ignora COD_PART em COD_SIT 02 | canceladas fora do TXT, pelo XML |
| CST do PIS/COFINS inválido "98" (saídas) | 98 é de entrada | notas próprias com CST/valores do XML |
| Total da nota ≠ soma dos itens (centavos) | arredondamento do emissor | sobra até R$ 1,00 em outras despesas |
| Valor do ICMS difere (diferença = IPI) | venda a consumidor final com IPI na base do ICMS | não há campo no leiaute: ajustar acumulador ou subir pelo XML |
| CFOP inválido para o estado / fora do estado | cadastro antigo do participante no Domínio | corrigir a UF do cadastro (o XML está certo) |
| O imposto 1 não está relacionado no acumulador | acumulador sem ICMS (mesmo com ICMS zero o C190 grava isentas/outras) | vincular ICMS ao acumulador no Domínio |
| Lançamento contábil na conta errada (ignora o COD_CTA) | o Domínio contabiliza a nota pela conta do ACUMULADOR (Contabilidade > Notas) | um acumulador por conta + `acumulador_por_conta`; depois Utilitários > regerar lançamentos |
| Crédito "estranho" depois de importar | suspeita de recálculo base x alíquota | NÃO ajustar a alíquota: manter fiel ao XML (regra de ouro) e conferir na nota do Domínio o ICMS gravado |
Outras: COD_NAT do C170 = código do acumulador (0400 com o nome); COD_CTA = conta reduzida; D100 (CT-e) não leva
acumulador — vale CFOP x acumulador da importação; venda a consumidor final de outra UF leva C101 (DIFAL);
COD_PART = CNPJ/CPF; série sem zeros; contadores com 9 dígitos.
Correção depois de importado: nunca reimportar o TXT inteiro por cima → `reimportar` gera `_CORRECAO.TXT` só com
as notas a excluir e importar de novo (ou excluir tudo do TXT e importar o completo).

## 6. Como o motor cresce
Toda decisão do escritório vira regra no `regras.json` da empresa (com `_motivo` e linha em `_decisoes`); o que
valer para qualquer indústria sobe para o modelo e para esta skill. Novo erro do Domínio → linha na tabela da
seção 5 + correção no `txt_dominio.py`, testada com o relatório de erros seguinte.
