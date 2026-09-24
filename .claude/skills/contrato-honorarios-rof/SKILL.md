---
name: "contrato-honorarios-rof"
description: "Gera contratos de honorários contábeis da ROF Contabilidade (Rosangela de Oliveira Furtado da Silva) para novos clientes de prestação de serviços. Use sempre que Everton pedir um \"contrato de honorários\", \"contrato de honorários contábeis\", \"contrato da ROF\" para uma empresa nova, mencionar CNPJ/contrato social de um cliente novo da contabilidade da esposa dele, ou disser algo como \"preciso de um contrato de honorários pra [empresa]\". Não usar para empresas de indústria (valores e condições são diferentes, tratar à parte) nem para outros tipos de contrato (ex: gestão de tráfego, prestação de serviços de outra natureza)."
---


# Contrato de Honorários Contábeis — ROF Contabilidade

Gera o "Instrumento Particular de Contrato de Prestação de Serviços Profissionais Contábeis" que a ROF Contabilidade (escritório da esposa do Everton, Rosangela) usa com todo cliente novo de prestação de serviços. O modelo abaixo foi validado com um caso real (Arkontech Soluções Digitais Ltda, jul/2026) e reflete exatamente a estrutura, cláusulas e regras de precificação que o escritório usa.

**Só serve para empresas de prestação de serviços.** Se a empresa for indústria, avise o Everton que os valores e condições são diferentes e pergunte como ele quer proceder — não aplique este modelo automaticamente.

## Dados fixos da CONTRATADA (nunca mudam)

ROSANGELA DE OLIVEIRA FURTADO DA SILVA, brasileira, casada, contadora, portadora da CRC/PR nº PR-083429/0-9, atuando profissionalmente na Rua Santo Agostinho, nº 145, Santa Terezinha, Fazenda Rio Grande/PR, CEP 83829-162, telefone (41) 99967-0199, endereço eletrônico suporte@rofcontabilidade.com.br.

## O que perguntar antes de gerar (não presuma nada disso)

Antes de montar o contrato, extraia o que puder do Cartão CNPJ / Contrato Social anexados, e pergunte ao Everton (numa lista só, sem gerar rascunho antes da resposta):

1. **Percentual dos honorários** sobre o salário mínimo nacional vigente. Não presuma 30% — cada cliente pode ter um valor diferente. Depois de saber o percentual, confira o valor do salário mínimo do ano corrente (buscar na web se não tiver certeza) e calcule o R$ mensal.
2. **Data de vigência/assinatura** do contrato — normalmente a data de abertura da empresa (Cartão CNPJ), mas confirme; pode ser outra data.
3. **Parâmetros da cláusula 4.2.5** — quantidade estimada de notas fiscais/mês. Não invente números.
4. **Se o quadro atual do cliente é só sócio(s), sem empregados** — se sim, inclua a cláusula 4.2.6 (ver abaixo) prevendo acréscimo de R$ 30,00/colaborador quando a empresa contratar alguém, cobrindo folha de pagamento/eSocial/departamento pessoal. Se o cliente já tem empregados, não inclua essa cláusula — pergunte se quer tratar isso de outra forma.
5. **Dados do(s) sócio(s) representante(s)** que não estejam no Contrato Social (e-mail e telefone pessoais, se diferentes dos da empresa).

Depois de reunir tudo isso, monte o rascunho e **sempre apresente para correção antes de finalizar** — não gere o arquivo definitivo sem o Everton validar os dados e o valor.

## Estrutura do contrato (texto de referência)

Use exatamente esta estrutura e este texto, substituindo apenas os campos entre `{{...}}`. As cláusulas 1, 2, 3, 5 e 6 são fixas (não mudam de cliente para cliente, exceto a data em 5.1 e o foro em 6, que normalmente é a cidade da sede do cliente — confirme se for diferente de Fazenda Rio Grande/PR).

### Abertura

```
Instrumento Particular de Contrato de Prestação de Serviços Profissionais Contábeis

CONTRATADA: ROSANGELA DE OLIVEIRA FURTADO DA SILVA, brasileira, casada, contadora, portadora da CRC/PR nº PR-083429/0-9, atuando profissionalmente na Rua Santo Agostinho, nº 145, Santa Terezinha, Fazenda Rio Grande/PR, CEP 83829-162, telefone (41) 99967-0199, endereço eletrônico suporte@rofcontabilidade.com.br.

CONTRATANTE: {{RAZAO_SOCIAL}}, pessoa jurídica de direito privado, inscrita no CNPJ sob nº {{CNPJ}}, com sede na {{ENDERECO_EMPRESA}}, telefone {{TELEFONE_EMPRESA}}, endereço eletrônico: {{EMAIL_EMPRESA}}, representad{{O_A}} por {{SEU_SUA}} sócio{{_A}} {{NOME_SOCIO}}, {{QUALIFICACAO_SOCIO}} (brasileiro(a), estado civil, regime de bens se casado), devidamente inscrito(a) no CPF/MF sob o nº {{CPF_SOCIO}}, residente e domiciliado(a) na {{ENDERECO_SOCIO}}, telefone {{TELEFONE_SOCIO}}, endereço eletrônico: {{EMAIL_SOCIO}}.

Pelo presente instrumento particular, as partes acima, devidamente qualificadas, doravante denominadas, simplesmente, CONTRATADA e CONTRATANTE, na melhor forma de direito, ajustam e contratam a prestação de serviços profissionais, segundo as cláusulas e condições adiante arroladas.
```

### CLÁUSULA PRIMEIRA – DO OBJETO (fixa)

O objeto do presente consiste na prestação pela CONTRATADA à CONTRATANTE dos seguintes serviços profissionais:

**1.1. ÁREA CONTÁBIL**
1.1.1. Classificação e escrituração da Contabilidade de acordo com as normas e princípios contábeis vigentes.
1.1.2. Apuração de balancetes.
1.1.3. Balanço Anual e Demonstrações Contábeis.

**1.2. ÁREA FISCAL**
1.2.1. Orientação e controle da aplicação dos dispositivos legais vigentes, sejam federais, estaduais ou municipais.
1.2.2. Escrituração dos registros fiscais do IPI, ICMS, ISS e elaboração das guias de informação e de recolhimento dos tributos devidos.
1.2.3. Atendimento das demais exigências previstas em atos normativos, bem como de eventuais procedimentos de fiscalização tributária.

**1.3. ÁREA DO IMPOSTO DE RENDA PESSOA JURÍDICA**
1.3.1. Orientação e controle de aplicação dos dispositivos legais vigentes.
1.3.2. Elaboração da declaração anual de rendimentos e documentos correlatos.
1.3.3. Atendimento das demais exigências previstas em atos normativos, bem como de eventuais procedimentos de fiscalização.

**1.4. ÁREA TRABALHISTA E PREVIDENCIÁRIA**
1.4.1. Orientação e controle da aplicação dos preceitos da Consolidação das Leis do Trabalho, bem como aqueles atinentes à Previdência Social, PIS, FGTS e outros aplicáveis às relações de emprego mantidas pela CONTRATANTE.
1.4.2. Manutenção dos Registros de Empregados e serviços correlatos.
1.4.3. Elaboração da Folha de Pagamento dos empregados e de Pró-Labore, bem como das guias de recolhimento dos encargos sociais e tributos afins.
1.4.4. Atendimento das demais exigências previstas na legislação, bem como de eventuais procedimentos de fiscalização.

### CLÁUSULA SEGUNDA – DAS CONDIÇÕES DE EXECUÇÃO DOS SERVIÇOS (fixa)

Os serviços serão executados nas dependências da CONTRATADA, em obediência às seguintes condições:

2.1. A documentação indispensável para o desempenho dos serviços arrolados na Cláusula Primeira será fornecida pela CONTRATANTE, consistindo, basicamente, em:
2.1.1. Boletim de caixa e documentos nele constantes.
2.1.2. Extratos de todas as contas correntes bancárias, inclusive aplicações; e documentos relativos aos lançamentos, tais como depósitos, cópias de cheques, borderôs de cobrança, descontos, contratos de crédito, avisos de créditos, débitos, etc.
2.1.3. Notas fiscais de compra (entradas) e de venda (saídas), bem como comunicação de seu eventual cancelamento.
2.1.4. Controle de frequência dos empregados e eventual comunicação para concessão de férias, admissão ou rescisão contratual, bem como correções salariais espontâneas.

2.2. A documentação deverá ser enviada pela CONTRATANTE de forma completa e em boa ordem nos seguintes prazos:
2.2.1. Até 5 (cinco) dias após o encerramento do mês, os documentos relacionados nos itens 2.1.1 e 2.1.2, acima.
2.2.2. Semanalmente, os documentos mencionados no item 2.1.3 acima, sendo que os relativos à última semana do mês, no 1° (primeiro) dia útil do mês seguinte.
2.2.3. Até o dia 25 do mês de referência quando se tratar dos documentos do item 2.1.4, para elaboração da folha de pagamento.
2.2.4. No mínimo, 48 (quarenta e oito) horas antes a comunicação para dação de aviso de férias e aviso prévio de rescisão contratual de empregados acompanhada do Registro de Empregados.

2.3. A CONTRATADA compromete-se a cumprir todos os prazos estabelecidos na legislação de regência quanto aos serviços contratados, especificando-se, porém, os prazos abaixo:
2.3.1. A entrega das guias de recolhimento de tributos e encargos trabalhistas à CONTRATANTE far-se-á com antecedência de 2 (dois) dias do vencimento da obrigação.
2.3.2. A entrega da Folha de Pagamento, recibos de pagamento salarial, de férias e demais obrigações trabalhistas far-se-á até 72 (setenta e duas) horas após o recebimento dos documentos mencionados no item 2.1.4.
2.3.3. A entrega de Balancete far-se-á até o dia 20 do 2° (segundo) mês subsequente ao período a que se referir.
2.3.4. A entrega do Balanço Anual far-se-á até 30 (trinta) dias após a entrega de todos os dados necessários à sua elaboração, principalmente o Inventário Anual de Estoques, por escrito, cuja execução é de responsabilidade da CONTRATANTE.

2.4. A remessa de documentos entre os contratantes deverá ser feita sempre sob protocolo.

### CLÁUSULA TERCEIRA – DOS DEVERES DA CONTRATADA (fixa)

3.1. A CONTRATADA desempenhará os serviços enumerados na Cláusula Primeira com todo zelo, diligência e honestidade, observada a legislação vigente, resguardando os interesses da CONTRATANTE, sem prejuízo da dignidade e independência profissionais, sujeitando-se, ainda, às normas do Código de Ética Profissional do Contador, aprovado pela Resolução CFC nº 1.307/10 do Conselho Federal de Contabilidade.
3.2. Responsabilizar-se-á a CONTRATADA por todos os prepostos que atuarem nos serviços ora contratados, indenizando à CONTRATANTE, em caso de culpa ou dolo.
3.2.1. A CONTRATADA assume integral responsabilidade por eventuais multas fiscais decorrentes de imperfeições ou atrasos nos serviços ora contratados, excetuando-se os ocasionados por força maior ou caso fortuito, assim definidos em lei, depois de esgotados os procedimentos de defesa administrativa, sempre observado o disposto no item 3.5.
3.2.1.1. Não se incluem na responsabilidade assumida pela CONTRATADA os juros e a correção monetária de qualquer natureza, visto que não se tratam de apenamento pela mora, mas, sim, de recomposição e remuneração do valor não-recolhido.
3.3. Obriga-se a CONTRATADA a fornecer à CONTRATANTE, no escritório dessa e dentro do horário normal de expediente, todas as informações relativas ao andamento dos serviços ora contratados, desde que solicitado com antecedência e prazo razoável para ajuntamento das informações.
3.4. Responsabilizar-se-á a CONTRATADA por todos os documentos a ela entregues pela CONTRATANTE, enquanto permanecerem sob sua guarda para a consecução dos serviços pactuados, respondendo pelo seu mau uso, perda, extravio ou inutilização, salvo comprovado caso fortuito ou força maior, mesmo se tal ocorrer por ação ou omissão de seus prepostos ou quaisquer pessoas que a eles tenham acesso.
3.5. A CONTRATADA não assume nenhuma responsabilidade pelas consequências de informações, declarações ou documentação inidôneas ou incompletas que lhe forem apresentadas, bem como por omissões próprias da CONTRATANTE ou decorrentes do desrespeito à orientação prestada.

### CLÁUSULA QUARTA – DOS DEVERES DA CONTRATANTE (aqui entram os dados variáveis)

4.1. Obriga-se a CONTRATANTE a fornecer à CONTRATADA todos os dados, documentos e informações que se façam necessários ao bom desempenho dos serviços ora contratados, em tempo hábil; nenhuma responsabilidade caberá à segunda caso recebidos intempestivamente.

4.2. Para a execução dos serviços constantes da Cláusula Primeira, a CONTRATANTE pagará à CONTRATADA, os honorários profissionais correspondentes a R$ {{VALOR_NUMERO}} ({{VALOR_EXTENSO}}) mensais neste ano de {{ANO}}, equivalente à {{PERCENTUAL}}% ({{PERCENTUAL_EXTENSO}} por cento) do salário mínimo nacional vigente, até o dia 15 (quinze) do mês subsequente ao vencido, podendo a cobrança ser veiculada por meio da respectiva duplicata de serviços, mantida em carteira ou via cobrança bancária.

4.2.1. Além da parcela acima avençada, a CONTRATANTE pagará à CONTRATADA uma adicional, anual, correspondente ao valor de uma parcela mensal, para atendimento ao acréscimo de serviços e encargos próprios do período final do exercício, tais como o encerramento das demonstrações contábeis anuais, Declaração de Rendimentos da Pessoa Jurídica, DFC, elaboração de informes de rendimento, RAIS, Folhas de Pagamento do 13° Salário, DIRF e demais.
4.2.1.1. A mensalidade adicional mencionada no item anterior será paga em duas parcelas vencíveis nos dias 20 de novembro e 15 de dezembro de cada exercício, e seu valor será equivalente ao dos honorários vigentes no mês de pagamento.
4.2.1.2. Mesmo no caso de início do contrato em qualquer mês do exercício, a parcela adicional será devida integralmente.
4.2.1.3. Caso o presente envolva a recuperação de serviços não-realizados – atrasados – a mensalidade adicional será, integralmente, devida desde o primeiro mês de atualização.

4.2.2. Os honorários pagos após a data avençada no item 4.2. acarretarão à CONTRATANTE o acréscimo de multa de 10% (dez por cento), sem prejuízo de juros moratórios de 1% (um por cento) ao mês ou fração e juros remuneratório de 3% (três por cento) ao mês.

4.2.3. Os honorários estão estabelecidos em {{PERCENTUAL}}% ({{PERCENTUAL_EXTENSO}} por cento) do salário mínimo nacional vigente, sendo reajustados automaticamente de ano em ano, segundo a variação anual aplicada ao salário mínimo nacional em janeiro de cada ano.

> Se o percentual combinado com o cliente tiver um degrau de transição (ex: X% neste ano, subindo pra Y% no ano seguinte — como aconteceu no contrato da LUMUS), adapte esta cláusula pra descrever os dois percentuais e o ano de transição em vez do texto acima. Pergunte ao Everton se é esse o caso antes de decidir.

4.2.4. O valor dos honorários previstos no item 4.2. foi estabelecido segundo o volume de notas fiscais e de lançamentos contábeis da CONTRATANTE, abaixo relacionados no item 4.2.5, ficando certo que se a média trimestral for superior aos parâmetros mencionados na proporção de 20% (vinte por cento), passará a viger nova mensalidade no mesmo patamar de aumento do volume de serviço, automaticamente, a partir do primeiro dia após o trimestre findo.

4.2.5. Os parâmetros de fixação dos honorários tiveram como base o volume de papéis e informações fornecidas pela CONTRATANTE, como segue:
Quantidade de Notas Fiscais/mês (Entrada/Saída/Serviços): {{QTD_NOTAS_FISCAIS}}.
Quantidade de Lançamentos Contábeis: conforme o volume de movimentação mensal apurado pela CONTRATADA.

> Não inclua "Quantidade de Funcionários" nessa lista a menos que o Everton peça — o padrão atual (desde o contrato da Arkontech) é não fixar um número de funcionários aqui, e tratar isso pela cláusula 4.2.6 abaixo quando aplicável.

**4.2.6. (só incluir se o quadro do cliente for só sócios, sem empregados — perguntar ao Everton)**
Os honorários ora pactuados foram estabelecidos considerando que, neste momento, os serviços são executados exclusivamente pelos integrantes do quadro societário da CONTRATANTE, sem colaboradores contratados. Caso a CONTRATANTE venha a admitir colaborador(es), sujeitando a CONTRATADA à execução da folha de pagamento, administração do eSocial e demais obrigações próprias do departamento pessoal, será acrescido aos honorários mensais o valor de R$ 30,00 (trinta reais) por colaborador admitido, a partir do mês de admissão.

> Se incluir 4.2.6, os itens seguintes (reembolso de materiais e serviços extraordinários) viram 4.3, 4.4 e 4.4.1. Se NÃO incluir, eles ficam 4.3, 4.4 e 4.4.1 do mesmo jeito — a numeração desses dois itens finais da cláusula 4 é sempre a mesma, o que muda é só ter ou não o 4.2.6 antes deles.

4.3. A CONTRATANTE reembolsará à CONTRATADA o custo de todos os materiais utilizados na execução dos serviços ora ajustados, tais como formulários contínuos, impressos fiscais, trabalhistas e contábeis, bem como livros fiscais, pastas, cópias reprográficas, autenticações, reconhecimento de firmas, custas, emolumentos e taxas exigidos pelos serviços públicos, sempre que utilizados e mediante recibo discriminado, acompanhado dos respectivos comprovantes de desembolso.

4.4. Os serviços solicitados pela CONTRATANTE não-especificados na Cláusula Primeira serão cobrados pela CONTRATADA em apartado, como extraordinários, segundo valor específico constante de orçamento previamente aprovado pela primeira, englobando nessa previsão toda e qualquer inovação da legislação relativamente ao regime tributário, trabalhista ou previdenciário.

4.4.1. São considerados serviços extraordinários ou paracontábeis, exemplificativamente: 1) alteração contratual; 2) abertura de empresa; 3) certidões negativas do INSS, FGTS, Federais, ICMS e ISS; 4) Certidão negativa de falências ou protestos; 5) Homologação na DRT; 6) Autenticação/Registro de Livros; 7) Encadernação de livros; 8) Declaração de ajuste do imposto de renda pessoa física; 9) Preenchimento de fichas cadastrais/ IBGE e outros que vierem a ser instituídos e necessários.

### CLÁUSULA QUINTA – DA VIGÊNCIA E RESCISÃO (fixa, exceto a data em 5.1)

5.1. O presente contrato vigora a partir de {{DATA_VIGENCIA}} por prazo indeterminado, podendo, a qualquer tempo, ser rescindido mediante pré-aviso de 60 (sessenta) dias, por escrito, sendo devido os respectivos honorários ajustados.
5.1.1. A parte que não comunicar, por escrito, a rescisão ou efetuá-la de forma sumária, desrespeitando o pré-aviso previsto, ficará obrigada ao pagamento de multa compensatória no valor de 2 (duas) parcelas mensais dos honorários vigentes à época, acrescida do mês em curso.
5.1.2. No caso de rescisão, a dispensa pela CONTRATANTE da execução de quaisquer serviços, seja qual for a razão, durante o prazo do pré-aviso, deverá ser feita por escrito, não a desobrigando do pagamento dos honorários integrais até o termo final do contrato.
5.2. Ocorrendo a transferência dos serviços para outra Empresa Contábil ou Contabilista, a CONTRATANTE deverá informar à CONTRATADA, por escrito, seu nome, endereço, nome do responsável e número da inscrição no Conselho Regional de Contabilidade, sem o que não será possível à CONTRATADA cumprir as formalidades fiscais e ético-profissionais, inclusive a transmissão de dados e informações necessárias à continuidade dos serviços, em relação às quais, diante da eventual inércia da CONTRATANTE, estará desobrigada de cumprimento.
5.2.1. Entre os dados e informações a serem fornecidos não se incluem detalhes técnicos dos sistemas de informática da CONTRATADA, os quais são de sua exclusiva propriedade.
5.3. A falta de entrega de documentos ou pagamento de qualquer parcela de honorários faculta à CONTRATADA suspender, imediatamente, a execução dos serviços ora pactuados, bem como considerar, rescindido o presente, independentemente de notificação judicial ou extrajudicial, sem prejuízo do previsto no item 4.2.2, mediante notificação prévia da suspensão.
5.4. A falência da CONTRATANTE facultará a rescisão do presente pela CONTRATADA, independentemente de notificação judicial ou extrajudicial, não estando incluídos nos serviços ora pactuados a elaboração das peças contábeis arroladas nos artigos 51 e 105 da Lei nº 11.101-05 e demais decorrentes.
5.5. Considerar-se-á rescindido o presente contrato, independentemente de notificação judicial ou extrajudicial, caso qualquer das partes CONTRATANTES venha a infringir cláusula ora convencionada.
5.5.1. Fica estipulada a multa contratual de uma parcela mensal vigente relativa aos honorários, exigível por inteiro em face da parte que der causa à rescisão motivada, sem prejuízo da penalidade específica do item 4.2.2., se o caso.

### CLÁUSULA SEXTA – DO FORO

Fica eleito o Foro da Cidade de {{CIDADE_FORO}}, com expressa renúncia a qualquer outro, por mais privilegiado que seja, para dirimir as questões oriundas da interpretação e execução do presente contrato.

> Padrão é Fazenda Rio Grande/PR (cidade da CONTRATADA). Só muda se o Everton pedir explicitamente o foro do cliente.

### Encerramento e assinaturas

```
Isto posto, firma-se este instrumento em 2 (duas) vias de igual teor, na presença de duas testemunhas.

{{CIDADE_FORO}}, {{DATA_ASSINATURA_EXTENSO}}.


___________________________________________________
ROSANGELA DE OLIVEIRA FURTADO DA SILVA
CONTRATADA


________________________________________________
{{RAZAO_SOCIAL}}
CONTRATANTE


______________________________________
Testemunha


______________________________________
Testemunha
```

## Como montar o arquivo .docx

Não há um .docx-modelo anexado a esta skill (não dá pra empacotar arquivos binários aqui) — gere o documento do zero em Python com `python-docx`, replicando a formatação:

- Fonte Arial, tamanho 12pt no corpo.
- Parágrafos justificados, espaçamento entre linhas ~1.5 (`line_spacing = 1.5`).
- Nomes de partes e títulos de cláusula em **negrito**.
- Numeração das cláusulas digitada manualmente no texto (não precisa configurar lista automática do Word) — seguindo exatamente os números do template acima, incluindo o ajuste de 4.2.6 quando aplicável.
- Depois de gerar, renderize em PDF (`soffice --headless --convert-to pdf`, depois `pdftoppm -jpeg`) e leia as imagens de cada página antes de entregar, pra conferir visualmente que não sobrou nenhum `{{placeholder}}` sem substituir e que a formatação ficou legível.
- Sempre mostre o rascunho pro Everton e pergunte se precisa corrigir algo antes de considerar definitivo.
- Salve o arquivo final com nome tipo `Contrato de Honorários Contábeis ROF e {{NOME_CLIENTE}}.docx`, na pasta do cliente se houver uma conectada, ou na pasta de saída padrão se não houver.

