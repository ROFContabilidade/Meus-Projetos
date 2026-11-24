---
name: "rof-fiscal-fator-r"
description: "ROF Contabilidade - análise do FATOR R do Simples Nacional (Anexo III x Anexo V) para qualquer empresa ou cliente novo: diz se a atividade/CNAE é alcançada pelo Fator R (LC 123/2006, art. 18, §§ 5º-B, 5º-D, 5º-I, 5º-J, 5º-K, 5º-M, 24 a 26), calcula o Fator R mês a mês, o pró-labore mínimo para ficar no Anexo III, compara o DAS no III e no V e explica o que muda em 2027 com a Reforma Tributária (CBS no DAS, opção por IBS/CBS por fora, reduções da saúde e profissões regulamentadas). Também orienta abertura de empresa (MEI x ME, escolha de CNAE) quando o Fator R entra na decisão. Usar quando falarem em Fator R, folha x receita, 28%, pró-labore para Anexo III, Anexo V, planejamento de pró-labore, abertura de CNPJ de profissional de saúde/serviços, ou Simples Nacional em 2027."
---

# ROF - Fator R (Simples Nacional): hoje e em 2027

Entrega: **parecer curto em linguagem simples** (para o cliente) + **quadro técnico** (para a analista), e,
quando houver números, a **planilha/saída do script** `fator_r.py`.

## 1. Perguntas antes de analisar (uma mensagem só)

1. CNPJ (se já existe) **ou** descrição exata do que o cliente faz / vai fazer (o serviço real, não só o CNAE).
2. Faturamento mensal dos últimos 12 meses (ou previsto, se for abertura).
3. Folha mensal dos últimos 12 meses: pró-labore, salários, 13º, férias, FGTS, INSS patronal (se houver).
4. Quem são os clientes (pessoa física, clínicas/empresas do Lucro Presumido/Real, órgão público) - pesa na decisão de 2027.
5. Data de início de atividade (se tiver menos de 12 meses).

Se a empresa tem skill própria (`rof-contabilidade-<empresa>`), ler o anexo/regime registrado lá primeiro.

## 2. A atividade é alcançada pelo Fator R? (base legal - LC 123/2006, art. 18)

O texto da lei não usa o nome "Fator R": é a **razão folha de salários ÷ receita bruta** (§5º-J e §5º-M),
medida nos **12 meses anteriores ao período de apuração** (§5º-K). **≥ 28% → Anexo III; < 28% → Anexo V.**

### 2.1 Grupo A - Anexo V, vai para o III se folha ≥ 28% (§5º-I + §5º-J)
| Inciso §5º-I | Atividade |
|---|---|
| II | Medicina veterinária |
| V | Serviços de comissaria, despachantes, tradução e interpretação |
| VI | Engenharia, medição, cartografia, topografia, geologia, geodésia, testes, suporte e análises técnicas e tecnológicas, pesquisa, design, desenho e agronomia |
| VII | Representação comercial e demais atividades de intermediação de negócios e serviços de terceiros |
| VIII | Perícia, leilão e avaliação |
| IX | Auditoria, economia, consultoria, gestão, organização, controle e administração |
| X | Jornalismo e publicidade |
| XI | Agenciamento, exceto de mão de obra |
| XII | Outras atividades de natureza intelectual, técnica, científica, desportiva, artística ou cultural, profissão regulamentada ou não, que não sejam do Anexo III ou IV |

(Incisos I, III e IV do §5º-I foram revogados pela LC 155/2016 e as atividades passaram para o §5º-B, abaixo.)

### 2.2 Grupo B - Anexo III, cai para o V se folha < 28% (§5º-M)
**§5º-M, I - incisos do §5º-B:**
| Inciso §5º-B | Atividade |
|---|---|
| XVI | Fisioterapia |
| XVIII | Arquitetura e urbanismo |
| XIX | Medicina, inclusive laboratorial, e enfermagem |
| XX | Odontologia e prótese dentária |
| XXI | Psicologia, psicanálise, terapia ocupacional, acupuntura, podologia, fonoaudiologia, clínicas de nutrição e de vacinação e bancos de leite |

**§5º-M, II - todo o §5º-D:**
| Inciso §5º-D | Atividade |
|---|---|
| I | Administração e locação de imóveis de terceiros |
| II | Academias de dança, capoeira, ioga e artes marciais |
| III | Academias de atividades físicas, desportivas, natação e escolas de esportes |
| IV | Elaboração de programas de computador, inclusive jogos, desenvolvidos no estabelecimento do optante |
| V | Licenciamento ou cessão de direito de uso de programas de computação |
| VI | Planejamento, confecção, manutenção e atualização de páginas eletrônicas, no estabelecimento do optante |
| IX | Empresas montadoras de estandes para feiras |
| XII | Laboratórios de análises clínicas ou de patologia clínica |
| XIII | Tomografia, diagnóstico por imagem, registros gráficos e métodos óticos, ressonância magnética |
| XIV | Serviços de prótese em geral |

> Atenção: pela letra do §5º-M, II o §5º-D inteiro está sujeito ao Fator R (inclusive locação/administração de
> imóveis de terceiros e academias). Parte do mercado ainda trata academias e administração de imóveis como Anexo III
> direto. Antes de afirmar, conferir o **Anexo VI da Resolução CGSN 140/2018** (tabela CNAE x anexo) e o histórico
> do DAS da empresa; se houver divergência, dizer que há divergência e recomendar manter folha ≥ 28% por segurança.

### 2.3 NÃO alcançadas pelo Fator R
- **Anexo III direto:** creche e ensino, agência de correios, agência de viagem, autoescola, lotérica, instalação/reparos/
  manutenção, transporte municipal, **escritórios contábeis**, produções culturais, **corretagem de seguros** (§5º-B XVII),
  **estética e beleza** (9602-5/01 e 9602-5/02) e os serviços residuais do §5º-F.
- **Anexo IV** (§5º-C): construção civil, vigilância, limpeza, paisagismo, **advocacia** - CPP fora do DAS, sem Fator R.
- **MEI:** não tem Fator R (DAS fixo).

### 2.4 Casos frequentes no escritório
| Caso | Conclusão |
|---|---|
| Massoterapia / práticas integrativas (8690-9/01) | Não está listada no §5º-B XXI (salvo acupuntura). Tende ao Anexo III direto (residual). Divergência no mercado → recomendar pró-labore ≥ 28% por segurança. Não é permitida ao MEI. |
| Massagem estética (9602-5/02) | Anexo III direto; permitida ao MEI. |
| Fisioterapia | Fator R (§5º-M, I + §5º-B XVI). |
| Médico, dentista, psicólogo, nutricionista, fono | Fator R (§5º-B XIX a XXI). |
| Software / TI | Desenvolvimento e licenciamento: §5º-D IV/V (Fator R); consultoria/suporte em TI: §5º-I VI/IX (Fator R). |
| Representação comercial | §5º-I VII (Fator R). |
| Contabilidade | Anexo III direto (§5º-B XIV), sem Fator R. |

O anexo é da **atividade efetivamente prestada em cada nota** (item da LC 116 + discriminação), não só do CNAE principal.

## 3. O que entra na folha (§§ 24 a 26 do art. 18)

**Entra** (efetivamente pago nos 12 meses anteriores ao mês de apuração): salários, **pró-labore**, 13º, férias + 1/3,
horas extras e demais remunerações a pessoas físicas por trabalho, **FGTS** recolhido e **contribuição patronal
previdenciária (CPP/INSS patronal)** recolhida. Só valem remunerações declaradas no eSocial/DCTFWeb (art. 32, IV, Lei 8.212/91 - §25).

**Não entra** (§26): **distribuição de lucros** e **aluguéis**. Também não entram RPA de prestador PJ, estagiário
sem declaração, retiradas não declaradas.

## 4. Cálculo

```bash
S=.claude/skills/rof-fiscal-fator-r/scripts
python3 $S/fator_r.py --receitas receitas.csv --folhas folhas.csv --mes 2026-12
python3 $S/fator_r.py --simular --receita-mensal 8000           # abertura / planejamento
```

- `receitas.csv` / `folhas.csv`: `AAAA-MM;valor` por linha.
- O script mostra RBT12, folha 12 meses, Fator R, anexo, alíquota efetiva no III e no V, DAS de cada um,
  **pró-labore mínimo** para chegar a 28% e a economia mensal.
- Pró-labore mínimo (sem funcionários, Anexo III com CPP dentro do DAS): `0,28 × RBT12 ÷ 12` por mês.
  Somar ao custo o INSS de 11% do sócio (até o teto) e o IRRF da tabela progressiva - comparar **custo total**, não só o DAS.
- **Início de atividade** (art. 18, §2º): RBT12 proporcional = média da receita dos meses de atividade × 12
  (no 1º mês, a receita do próprio mês × 12). Fazer o mesmo com a folha. Conferir a regra vigente da Resolução CGSN 140
  para os primeiros meses (ver §5 sobre a mudança anunciada para 2027).

Fórmulas: Fator R = folha12 ÷ RBT12. Alíquota efetiva = (RBT12 × alíquota nominal − parcela a deduzir) ÷ RBT12.

## 5. O que muda em 2027 (Reforma Tributária - EC 132/2023, LC 214/2025 e LC 227/2026)

**O que NÃO muda:** o Fator R continua. A lista de atividades, os 28%, a composição da folha (§§ 5º-J, 5º-K, 5º-M, 24-26)
não foram alterados pela LC 214/2025 (conferido no texto compilado da LC 123 no Planalto). A LC 214 alterou o conceito
de receita bruta (art. 3º, §1º e §19 da LC 123) - isso mexe no **denominador** do Fator R; conferir caso a caso.

**O que muda:**
1. **CBS no lugar do PIS/Cofins dentro do DAS** a partir de 01/2027. A partilha do DAS muda, mas a alíquota total
   do anexo continua sendo escolhida pelo Fator R. IBS entra no DAS gradualmente no lugar de ICMS/ISS de 2029 a 2033.
2. **Opção por recolher IBS/CBS por fora do DAS (regime regular / "híbrido")**: semestral. Para efeitos em 2027 a
   janela foi em setembro/2026 (fontes divergem nos prazos - confirmar no Portal do Simples). Quem opta paga IBS/CBS
   com alíquota cheia e crédito pleno; o **Fator R passa a valer só para o restante do DAS** (IRPJ, CSLL, CPP e ISS/ICMS
   enquanto existirem). MEI não tem essa opção.
3. **Clientes PJ (clínicas, empresas do Lucro Real/Presumido):** no DAS, o crédito de IBS/CBS que o cliente toma é só
   o valor efetivamente recolhido no DAS (baixo). Se o cliente pressionar por crédito, simular o regime regular.
4. **Reduções do regime regular** (só importam se optar por fora do DAS): serviços de saúde do Anexo III da LC 214
   com **redução de 60%**; profissões intelectuais regulamentadas (medicina, odontologia, fisioterapia, psicologia,
   engenharia, arquitetura, contabilidade etc.) com **redução de 30%**. Massoterapia e terapias não regulamentadas
   **não** têm redução garantida - conferir a lista.
5. **Período de apuração / primeiros meses:** fontes de mercado (2026) falam em deslocar a janela de 12 meses
   (ex.: DAS de jan/2027 usando dez/2025 a nov/2026) e em Fator R fixo de 0,28 nos 2 primeiros meses de atividade,
   por regulamentação do CGSN. **Não confirmado no texto da LC 123** - antes de usar, conferir a Resolução CGSN
   vigente e o PGDAS-D. Até confirmar, calcular pela regra atual e avisar.

## 6. Como entregar

1. **Parecer para o cliente** (curto, sem juridiquês): a atividade é ou não Fator R; qual pró-labore mínimo;
   quanto paga no III x V; o que muda em 2027 para ele.
2. **Quadro técnico:** atividade → dispositivo legal → anexo; cálculo mês a mês; alertas.
3. **Alertas obrigatórios:** atividade da nota diferente do CNAE; folha não declarada no eSocial; distribuição de lucros
   sendo usada como "pró-labore"; Fator R oscilando perto de 28% (risco de cair no V num mês); divergência de
   interpretação (dizer que é divergência).
4. Quando a analista decidir uma interpretação (ex.: academias Anexo III direto), registrar aqui na seção 2.4.
