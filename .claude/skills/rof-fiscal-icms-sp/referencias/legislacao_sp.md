# Textos legais LIDOS no site oficial (legislacao.fazenda.sp.gov.br)

Só entra aqui texto copiado da fonte oficial, com a data em que foi lido. Resumo de blog, de consultoria ou de
ferramenta NÃO é base legal: serve para achar a norma, nunca para fundamentar.

## RICMS/SP (Decreto 45.490/2000) - art. 115, XV-A - lido em 19/11/2026
"XV-A - na entrada em estabelecimento de contribuinte sujeito às normas do Regime Especial Unificado de Arrecadação de
Tributos e Contribuições devidos pelas Microempresas e Empresas de Pequeno Porte - "Simples Nacional", até o último dia
do segundo mês subsequente ao da entrada:" (caput: Decreto 59.967/2013, efeitos a partir de 01-01-2014)

"a) de mercadoria destinada a industrialização ou comercialização, material de uso e consumo ou bem do ativo permanente,
remetido por contribuinte localizado em outro Estado ou no Distrito Federal, o valor resultante da multiplicação do
percentual correspondente à diferença entre a alíquota interna e a interestadual pela base de cálculo, quando a alíquota
interestadual for inferior à interna (Lei Complementar federal 123/2006, art. 13, § 1°, XIII);" (Decreto 52.858/2008)

"b) de petróleo, inclusive lubrificantes e combustíveis líquidos e gasosos dele derivados, bem como energia elétrica,
oriundos de outro Estado ou Distrito Federal, quando não destinados à comercialização ou industrialização, calculado pela
alíquota interna."

§ 8º "Para fins do disposto na alínea "a" do inciso XV-A, a alíquota interestadual a ser adotada será a de:
1 - 4% (quatro por cento), nas operações com mercadorias abrangidas pela Resolução do Senado Federal nº 13, de 25 de abril de 2012;
2 - 12% (doze por cento), nas demais operações." (Decreto 58.923/2013, efeitos desde 01-01-2013)

Leitura: o Simples paga em QUALQUER destinação (industrialização, comercialização, uso/consumo, ativo); a alíquota
interestadual é a do § 8º (4% ou 12%), não a do remetente. O texto diz "pela base de cálculo" sem definir: usar o valor
da operação com frete/seguro/despesas cobrados do destinatário (LC 87 art. 13 §1º II) - base única (RC 26911/2023).
Não diz nada sobre ST: mercadoria com ST segue a ST (art. 426-A / regra do produto) - conferir caso a caso.

## RICMS/SP - art. 313-O (autopeças) - lido em 19/11/2026
Caput (Decreto 64.552/2019): ST "Na saída das autopeças indicadas em portaria da Coordenadoria da Administração
Tributária, com destino a estabelecimento localizado em território paulista". Inciso III: responsável "qualquer
estabelecimento localizado em território paulista que receber mercadoria referida neste artigo diretamente de outro Estado
sem a retenção antecipada do imposto." -> só vale para autopeça que ESTÁ na portaria.

## Portaria SRE 34, de 29/06/2026 (DOE 30-06-2026) - lida em 19/11/2026
Art. 1º revoga "os Anexos VII, VIII, XIV, XVIII e XXI e os itens 2 ao 10 e o item 15 do Anexo XXII da Portaria CAT 68/19"
(relação de mercadorias com ST em SP) e, no inciso II, "a Portaria SRE 16/23 ... que estabelece a base de cálculo na saída
de autopeças, a que se refere o artigo 313-P". Art. 2º: estoque segue a Portaria CAT 28/20. Art. 3º: "entra em vigor em
1º de outubro de 2026". Também saíram: pneus (SRE 15/24), tintas/vernizes (SRE 46/24), materiais elétricos (SRE 86/24),
ferramentas (SRE 78/25), baterias (SRE 10/26) e itens 2 a 11 de eletrônicos/eletrodomésticos (SRE 32/26).

## Portaria CAT 68/2019 - Anexo XIV - lido em 19/11/2026
Cabeçalho oficial: "ANEXO XIV (Anexo revogado pela Portaria SRE-34/26, de 29-06-2026; DOE 30-06-2026; em vigor em
1º de outubro de 2026) AUTOPEÇAS (artigo 313-O do RICMS)". Item 77: "CEST 01.075.00 | NCM 8708 | Partes e acessórios
dos veículos automóveis das posições 8701 a 8705". O NCM 8708 não aparece em nenhum outro anexo da CAT 68/19
(só no item 92 do próprio Anexo XIV - fitas refletivas 8708.29.99). Conclusão: autopeça CEST 01.xxx entrada a partir de
01/10/2026 não tem ST em SP -> Simples paga a equalização do art. 115 XV-A "a".

## RICMS/SP art. 2º, XVI e § 6º - lido em 19/11/2026 (Decreto 52.104/2007)
"XVI - na entrada em estabelecimento de contribuinte sujeito às normas do Regime Especial Unificado [...] "Simples
Nacional", de mercadorias, oriundas de outro Estado ou do Distrito Federal."
"§ 6º - Na hipótese do inciso XVI, a obrigação do contribuinte consiste, afinal, em pagar o imposto correspondente à
diferença de cargas tributárias entre a operação interna e a interestadual precedente."
-> o fato gerador do Simples não depende da destinação: toda entrada de mercadoria de outra UF.

## RICMS/SP art. 52, I - lido em 19/11/2026
"I - nas operações ou prestações internas, ainda que iniciadas no exterior, 18% (dezoito por cento);"

## Monitoramento automático
`scripts/verificar_parametros.py` guarda em `referencias/base_oficial/` o texto oficial de cada parâmetro e avisa quando
mudar. Rodar antes de toda conferência (PASSO ZERO da SKILL.md).

## Códigos do DARE-SP - portal oficial SEFAZ-SP ("Como pagar valor total ou parcial - DARE ICMS") - lido em 19/11/2026
"Para os contribuintes do Simples Nacional, foram criados os novos códigos de serviço 04602 (DeSTDA-DIF), 14602 (DeSTDA-ST)
e 14603 (DeSTDA-RAST). Na emissão do DARE diretamente pelo PFE [...] o documento já está sendo emitido com os novos códigos."
| Receita | Serviço | Descrição |
| 046-2 | 04601 | ICMS - Operações Próprias - RPA |
| 046-2 | 04602 | ICMS - Diferencial de Alíquota (DeSTDA - DIF) - Simples Nacional |  <- equalização/DIFAL do Simples
| 146-6 | 14602 | ICMS - Substituição Tributária (DeSTDA - ST) - Simples Nacional |
| 146-6 | 14603 | ICMS - Recolhimento Antecipado de ST (DeSTDA - RAST) - Simples Nacional |  <- art. 426-A no Simples
| 063-2 | 06304 | ICMS - Outros Recolhimentos Especiais - RPA |
| 063-2 | 06305/06306/06307/06308 | Leilão / Produtor rural e PF / Regime especial OPP / Regime especial ST |
Portaria CAT 125/2011 art. 7º-M (red. Portaria SRE 76/2023): 046-2 e 063-2 só por DARE-SP desde 01/07/2024.
ERRO anterior desta skill (corrigido em 19/11/2026 pela Rosangela): indicava 063-2 para o Simples.

## NÃO lidos no texto oficial ainda (só fonte secundária - tratar como "a confirmar")
- RICMS/SP art. 117 §5º/§6º; art. 37 VI; art. 49 (base dupla RPA) - via Respostas à Consulta.
- "SEFAZ-SP veda redução de base no DIFAL do Simples" - notícia de 2026, sem a RC lida.
- Alíquotas internas por NCM em tabelas_icms.py (cerveja, fumo, perfumes, máquinas) - todas "conferir".
- Lei 6.374/89: se a equalização do Simples tem previsão em LEI estadual (relevante para o STF Tema 456).
