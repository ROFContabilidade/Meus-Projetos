---
name: "estudo-tributario"
description: "ROF Contabilidade - ESTUDO TRIBUTÁRIO / planejamento de regime para 2027 (Simples Nacional × Lucro Presumido × Lucro Real) com a reforma tributária (CBS, IBS, Imposto Seletivo). Consulta o CNPJ, levanta sozinho o que dá com procuração/certificado (e-CAC, PGDAS, eSocial, Reinf, XMLs), pede ao cliente só o mínimo, preenche o simulador em Excel, aponta riscos (CNAE, Funrural, ICMS, limite do grupo, NCM) e entrega checklist de visita, relatório e proposta de honorários. Usar quando falarem em estudo tributário, planejamento tributário, mudar de regime, sair do Simples, Simples x Presumido x Real, simulação de regime, reforma tributária para um cliente, visita a cliente novo, proposta de honorários de estudo ou de terceirização (Renata), ou citarem Castelo Cafés / Royalty Cafés."
---

# Estudo Tributário — Simples × Presumido × Real (2027)

Objetivo: dar ao cliente **números para decidir o regime** antes de janeiro, com segurança e sem assustar.
Tom com a Rosangela: **conciso, cirúrgico, sem enrolação**. Documentos para cliente e parceiros: **diretos, pouco formais**.

Arquivos desta skill:

| Arquivo | Uso |
|---|---|
| `references/reforma-2027.md` | Regras de 2027: CBS/IBS, bares e restaurantes, cesta básica, Imposto Seletivo, Simples, ICMS-PR, Funrural, prazos |
| `references/ncm-cafe-bebidas.md` | NCMs de café e bebidas com o tratamento 2027 |
| `references/honorarios.md` | Valores, horas e o formato de proposta que a Rosangela aprovou |
| `references/caso-castelo-royalty.md` | 1º caso (cafeteria + atacado de café) — usar como exemplo |
| `scripts/gerar_simulador.py` | Gera o simulador Excel (`python3 gerar_simulador.py saida.xlsx`) |
| `scripts/html_para_pdf.js` | Converte HTML em PDF (Playwright): `node html_para_pdf.js /abs/entrada.html /abs/saida.pdf` |
| `modelos/` | Simulador pronto, checklist de visita, proposta e mensagem ao cliente (exemplos aprovados) |

## 1. Início — o que perguntar (uma mensagem só)
1. **CNPJ(s)** de todas as empresas do grupo (mesmos sócios contam juntos no limite do Simples).
2. **Atividades reais** (o que vende, se presta serviço, se industrializa — ex.: torra café?).
3. **Regime atual** declarado pelo cliente (conferir com a consulta — no caso Castelo/Royalty o cliente falava em Presumido e a Receita mostrou as duas no Simples).

## 2. Consulta do CNPJ (sempre, antes de qualquer análise)
```bash
python3 .claude/skills/rof-fiscal-notas-servico/scripts/consulta_cnpj.py <CNPJ>
```
Conferir e **apontar**: Simples (data de opção), CNAE principal × atividade real, **CNAEs faltando** (ex.: 5611-2/05 bar, 5620-1/02 bufê, 8230-0/01 eventos, 1081-3/02 torrefação), sócios em comum (limite global R$ 4,8 mi — LC 123, art. 3º, §4º, III), vedações (atacado de bebida alcoólica no Simples — LC 123, art. 17, X).

## 3. Coleta — buscar sozinho, pedir o mínimo
**Nós buscamos** (procuração eletrônica no e-CAC ou certificado A1; acesso à Receita/PR):
PGDAS-D e DAS · situação fiscal · eSocial/DCTFWeb (folha, pró-labore, empregados) · EFD-Reinf (R-2055 Funrural) ·
XMLs de NF-e/NFC-e emitidas e recebidas · NFS-e no portal do município · cartão CNPJ.

**Cliente passa só** (usar `modelos/mensagem_cliente.md`, tom leve):
1. procuração e-CAC + acesso Receita/PR (ou certificado A1); 2. extratos bancários do ano; 3. relatório do PDV por item;
4. aluguel (valor, locador PF ou PJ); 5. balancete/DRE ou contato do contador atual.
Perguntas rápidas por telefone: torra? compra de produtor de qual estado? eventos para empresas? planos para o ano?

Obs.: muitas vezes o cliente **só libera dados depois da proposta de honorários** — nesse caso fazer primeiro a proposta (seção 7) com base no CNPJ e na visita.

## 4. Simulação
1. Copiar `modelos/Simulador_Regime_Tributario_2027.xlsx` (uma cópia por CNPJ) ou gerar de novo com o script.
2. Preencher **só células amarelas**: `Dados de Entrada` (receita anual por linha, anexo, presunção, tratamento CBS ZERO/REST/CHEIA, ICMS-ST, carga efetiva de ICMS, ISS; folha) e `Compras e Despesas` (tipo de crédito ZERO/CHEIA/ALUGUEL/SIMPLES/MANUAL).
3. Conferir `Parâmetros` — **CBS 2027** (atualizar com a Resolução do Senado), RAT/FAP, terceiros, ISS do município.
4. Recalcular (skill xlsx: `recalc.py`) e conferir zero erros; validar 2–3 números à mão.
5. Ler `Comparativo`: total por regime, melhor regime, economia, alertas (limite do grupo, sublimite R$ 3,6 mi).

Limitações conhecidas (dizer no relatório): não simula IBS/CBS "por fora" do Simples; Lucro Real simplificado (sem LALUR/prejuízo); crédito presumido de produtor rural não considerado.

**O que mais decide** (nesta ordem): peso da folha (CPP dentro do DAS × ~27,8% fora) · mix de vendas (cesta básica zero × servido × álcool) · margem real (Real) · clientes PJ que querem crédito · ICMS.

## 5. Entregáveis
- **Checklist de visita** (PDF, 2–3 páginas) — base `modelos/checklist_visita.html`: quadro das empresas e alertas, tabela de NCMs, quanto se paga em 2027, bebidas/IS, o que falar, o que apontar, o que pedir, frase de fechamento, espaço de anotações. **Sem marca da ROF** no material do cliente.
- **Relatório do estudo** (2–3 páginas): quadro "quanto paga em cada regime", recomendação, riscos, próximos passos; planilha anexa.
- **Proposta** (seção 7).
PDF: escrever o HTML no scratchpad, `node scripts/html_para_pdf.js`, conferir com `pdftoppm -r 60 -png` e ajustar até não sobrar página quase vazia.

## 6. Prazos (calendário do estudo)
| Quando | O quê |
|---|---|
| Semana 1 | Proposta aceita, procuração, coleta |
| Até 05/12 | Dados completos |
| Até 15/12 | CBS oficial (Resolução do Senado) — atualizar Parâmetros |
| Até 19/12 | Relatório + reunião com o cliente; decisão até ~23/12 |
| Janeiro | Exclusão do Simples por opção até o **último dia útil de janeiro** (efeito 1º/01); CNAEs; PDV/cClassTrib; Domínio. Presumido: opção pelo 1º DARF de IRPJ; Real: estimativa (fev.) ou trimestral |

## 7. Honorários e proposta
Seguir `references/honorarios.md` (valores aprovados e o formato que a Rosangela quer: 1 página, título simples, sem "Oi/segue a proposta", só **nosso valor** + horas; sugestão de cobrança ao cliente **só no estudo**; sem margem do parceiro, sem 13ª, implantação, regularização ou condições de pagamento).

## 8. Cuidados
- Valores de 2027 ainda dependem de norma (CBS no Senado, MP 1.399 no Congresso, leiaute do PGDAS 2027): marcar como **"a confirmar"** e nunca afirmar número que não foi verificado.
- Café em pacote **já** tem PIS/COFINS zero hoje (Lei 10.925/2004, art. 1º, XXI) — a mudança para CBS zero é **neutra**; o impacto está no café **servido**.
- Regime de bares e restaurantes (redução de 40%) **não** vale no Simples nem para bebida alcoólica.
- Reduções e créditos só fazem sentido com **segregação real** das atividades — nada de fatiamento artificial.
- Fontes: citar com link quando trouxer dado novo de pesquisa.
