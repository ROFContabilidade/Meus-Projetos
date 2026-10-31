# Retomada: skills ROF (economia de tokens e autonomia)

Resumo das sessões de 29 e 30/10/2026 (Rosangela). Ler só este arquivo para continuar; não precisa reler a conversa anterior.

## Objetivo
Skills de ~140 empresas (cada empresa com a sua skill e a sua cultura) gastando menos tokens e mais autônomas, para depois rodarem por rotinas agendadas.

## Já feito e instalado no claude.ai (conferido)
- **Regra de leitura** em 50 skills (49 `rof-*` + `extrato-dominio`): MD > OFX/XML > planilha > PDF; PDF nunca direto, converter antes (`scripts/ler_documento.py`); se não converter, avisar a Rosangela.
- **Regra do Conversor de extratos ROF** em 45 skills de contabilidade: ler sempre o `<nome>_extrato.md`; Confere "NÃO", tabela não montada ou [OCR] duvidoso → avisar antes de lançar.
- **Motor** `extrato_dominio.py` (26 skills) lê o `_extrato.md` e recusa quando o Confere não é "sim".
- **extrato-dominio** (gerador) cria skills novas já com tudo isso.
- Código e regras em `kit-rof/` (`aplicar_leitura.py`, `leitura_arquivos.md`, `leitura_extratos.md`, `patches/extrato_md.py`, `scripts/ler_documento.py`).

## Piloto de economia: SDM (rof-contabilidade-sdm-compensados, v6 instalada)
- SKILL.md de ~30 mil para ~3,9 mil tokens, sem perder regra. Modelo "capa + anexos":
  - fica no SKILL.md: dados, sócios, regras de trabalho, leiaute, regras invioláveis, práticas, **Regras de decisão da contadora** (resumo das decisões do histórico), folha, notas, impostos, fluxo, pendências, último saldo, tabela de anexos;
  - vai para `references/`: `classificacoes_empresa.md` (tabela palavra→conta; o script usa o `empresa.json`), `decisoes.md` (histórico datado), `plano_contas.md`, `saldos.md`, `leitura.md`.
- Descrição menciona "SDM"; pasta do Drive registrada (`Arquivos RENATA Dominio\147 - Gabriela Martins Comercio\<AAAA>\<MM_AAAA>\` com Extrato, Relatorio, Guias, Doc's, SPED); saldo inicial/final vem do Confere do `_extrato.md`.
- Decisão nova (29/10/2026): **cartão de crédito (fatura, qualquer banco) → 357, sempre** (substitui 603). Regra criada no `empresa.json`; cartão de débito não muda.
- A versão instalada é o modelo: copiar de `/root/.claude/skills/synced/*/rof-contabilidade-sdm-compensados`.

## Em andamento / próximos passos
1. **Teste da SDM** em aba separada (sessão "SDM", competência 09/2026): conferir se buscou os `_extrato.md` no Drive sozinha, usou o saldo do Confere e aplicou as regras. A aba precisa do conector Google Drive ligado.
2. Se o teste aprovar: **segundo piloto** (Kopp Indústria ~20 mil tokens ou VF Chaveiro ~18 mil) e depois automatizar o modelo para as outras skills (script no `kit-rof/`).
3. Depois: descrições curtas em todas; comando único `rotina_mes.py` (resumo curto do mês); converter as 18 skills de formato antigo (só texto) para ficha (`empresa.json`).
4. Pendente: liberar sites do governo na rede do ambiente (Planalto bloqueado; sugerido `*.gov.br` e `gov.br` em Domínios permitidos, modo Custom, mantendo a lista padrão).
5. Achados a tratar: regra genérica "PIX ENVIADO" CONFIRMADO em JL Mangoni, Aphrodite, Vivare (362) e JS de Moraes (525); DC GRUP e DCK são a mesma empresa em duas skills.

## Conversor de extratos: ocorrido de 30/10/2026
- A "limpeza" de 29/10 07:37 apagou os `.md` com Confere NÃO, mas o conversor só refaz a partir de `desde` (config.json) = 2026-09-01. Julho/agosto ficaram sem `.md` (ex.: 148 Mercado Pago 08).
- Corrigido: `desde` passou para `2026-07-01` (30/10 14:08). Em 30/10 15:07-15:13 converteu 246 arquivos: 68 Confere sim, 60 NÃO, 10 ERRO, 108 texto/OFX sem saldo.
- 148: 07 e 08 Mercado Pago agora Confere sim. 147 (SDM) 08: Mercado Pago NÃO (R$ 299,90) e Inter NÃO (R$ 10.261,40).
- ERROS de julho: OFX com `decimal.ConversionSyntax` (Aphrodite, Vivare), .xls antigo (Kopp Comércio, Mohr), PDF com senha (JNK Prado, Raissa, Andre Viana, Mark 1), xlsx inválido (Andre Viana).
- Arquivo único sem `.md`: arrastar o original sobre `CONVERTER_AGORA.bat`.
- Cuidado: o `conversor.lock` fica na pasta do OneDrive; se travar, bloqueia por até 1 h ("Outra conversão já está rodando"). O Bloco de Notas do Windows 11 só grava com Ctrl+S (conferir a data do arquivo).
- Pendente: decidir se volta `desde` para 2026-09-01; tratar os NÃO de julho/agosto quando a competência for trabalhada.

## Validação do conversor por banco (30/10/2026)
Método: PDF original do Drive passado na mesma versão do conversor + saldo linha a linha + comparação com OFX do mesmo mês (data+valor).
- OK, linhas corretas: Bradesco (148 set: 231/231 = OFX), Mercado Pago (148 set: 473 linhas, releitura independente sem divergência), Santander (147 set: 128/128 = OFX), Inter (RBA set), Sicredi (Mohr set), BB (Marca Metal set), Cora (FWL set), Sicoob layout Everton (set).
- Linhas certas, cabeçalho errado (Confere NÃO falso): Santander (vem de trás para frente; pegou "Saldo Disponível" do dia da emissão como saldo inicial; correto −37.879,41); Sicredi Mohr (extrato até 10/10; saldo final pego errado).
- ERRO REAL nas linhas: Sicoob layout "SISBR" (Pai e Filhos, conta 92.010-0): valor e letra C/D em linhas diferentes perdem o sinal (ex. PIX EMIT 1.400,00 D virou +1.400); depósito bloqueado (valor com *) contado e depois "LIBER.DEPÓSITO BLOQ" contado de novo; histórico deslocado (DOC/CPF da linha anterior grudado na seguinte); saldo final pegou "conta capital" 60,64 (real 32.017,47). Confere NÃO pegou.
- Cresol (Cross ago): extrato de trás para frente; quadro de resumo do rodapé (Limite de crédito 2.000,00, IOF, juros acumulados) virou lançamento. Confere NÃO pegou.
- Não validados (PDF escaneado, dependem do OCR do Windows): Caixa (FWL), C6 (Catia), Nubank (Everton). Itaú PDF da Mohr sai como "texto por página" (sem tabela).
- CORRIGIDO em `kit-rof/conversor/conversor.py` (30/10/2026):
  Sicoob SISBR (leitor próprio `sicoob_sisbr`; depósito bloqueado vai para seção "## Depósito bloqueado", fora da tabela),
  Cresol (tabela para em "Totalizadores"/"Resumo"), Santander (saldo sem data no fim de extrato invertido não é saldo inicial),
  Sicredi ("Lançamentos Futuros" fora; "Saldo Atual" só vale se não há saldo por linha). Regressão: Bradesco, MP, Inter, BB, Cora, Sicoob Everton iguais.
- INSTALADO e refeito em 30/10/2026 ~19h (REFAZER_NAO.bat em `_ferramentas`; limpeza agora respeita o corte `desde`).
  Conferido no Drive: Pai e Filhos Sicoob set, Cross Cresol ago, SDM Santander set e Mohr Sicredi set = Confere sim.
- Ainda NÃO / sem tabela em 30/10: tratados em 31/10 (ver a seção abaixo).

## Conversor: correções de 31/10/2026 (sessão sozinha, Rosangela fora)
Prova usada: o PDF/CSV original do Drive (só leitura), a versão antiga e a nova lado a lado, o saldo linha a linha e, quando há, o OFX do mesmo mês (data + valor).
Commits na branch `claude/affectionate-edison-id48dx`: 7d461c4, 9c1ffb1, 34a0c8b, 583f70a.

| Extrato | Antes | Depois | Prova |
|---|---|---|---|
| Jungle Inter CSV "Extrato-01-07-2026-a-19-10-2026-CSV" (07, 08 e 09) | NÃO (−83.419,40) | **sim** (inicial 44.177,33, final 2.401,33) | 450/450 lançamentos = OFX |
| "INTER Extrato-01-09-2026-a-30-09-2026-CSV" (Jungle 09) | NÃO (29.807,70) | **sim** (inicial 610,91, final 15.198,78) | saldo linha a linha; = linhas de set. do CSV grande |
| 155 "extrato pj agosto.pdf" (Caixa) | NÃO (−2.893,71) | **sim** (inicial 2.120,23, final 0,00) | saldo linha a linha; sem OFX na pasta |
| 155 "extrato setembro.pdf" (Caixa) | NÃO (232,98) | **sim** (inicial 0,00, final 1.516,96) | saldo linha a linha; inicial = final de agosto |
| Cora FWL 07 | texto por página | **sim** (1.333,32 → 578,70) | 56/56 = OFX |
| Cora FWL 08 | texto por página | **sim** (578,70 → 1.686,97) | 49/49 = OFX |
| "Extrato Infiniti.pdf" (LG dos Santos 07, InfinitePay) | texto por página | **sim** (0,45 → 891,62) | créditos 69.393,86 e débitos 68.502,69 = resumo do PDF; 21 "Saldo do dia" sem quebra (o OFX da pasta é do Itaú, outra conta) |
| "Extrato Itau Conta Garantida.pdf" (Jungle 09) | texto por página | **sim** (−6.700,00 → −6.700,00) | mês sem nenhum lançamento: só saldo anterior e atual |

O que era cada erro:
- CSV do Inter vem do mais novo para o mais antigo: as linhas estavam certas, só o Confere lia na ordem errada.
- Caixa (155): os dias vêm do mais novo para o mais antigo, mas dentro de cada dia a ordem é normal. As linhas estavam certas; agora o conversor escolhe a ordem em que o saldo fecha.
- Cora 07/08: o PDF foi regravado (Ghostscript) e perdeu o mapa de letras da fonte ("!"#$%"). Agora cada letra é reconhecida pelo desenho, usando como referência a mesma fonte do PDF de setembro (que tem o mapa). O texto também vinha desenhado duas vezes (negrito simulado); entra uma vez só. Só é usado quando o texto normal sai embaralhado. O .md avisa: "fonte sem mapa de caracteres... recuperado pelo desenho das letras".
- Infiniti: layout próprio (data "01 Jul, 2026", nome quebrado em 2 linhas) → leitor próprio `infinitepay`.
- Itaú conta garantida: sem nenhum lançamento a tabela era recusada; agora sai com "sem lançamentos no período".

NÃO corrigido (e por quê):
- C6 "Extato 6C_09.26.pdf" (empresa 152, 09/2026): o PDF foi feito pelo "Microsoft Print to PDF" e não tem NENHUM texto (as letras viraram desenho). Só o OCR do Windows lê, e aqui não dá para rodar nem conferir; não há OFX na pasta. Não forcei. Sugestão: baixar de novo no app do C6 o extrato em PDF original ou OFX/CSV.
- Regressão: o Santander da SDM (147) set não foi achado no Drive (a pasta 09_2026 da 147 só tem Bradesco, Mercado Pago e Inter). Os outros 9 da lista (Bradesco e Mercado Pago 148, Inter RBA, Sicredi Mohr, BB Marca Metal, Cora FWL 09, Sicoob Everton, Sicoob Pai e Filhos, Cresol Cross 08) saíram IDÊNTICOS na versão antiga e na nova, em todos os commits.

### Para a Rosangela instalar (5 minutos)
1. No Chrome, abra: `https://github.com/rofcontabilidade/meus-projetos/raw/claude/affectionate-edison-id48dx/kit-rof/conversor/conversor.py`
2. Se aparecer a barra de tradução, clique em "Mostrar original" / desligue a tradução (senão o código fica em português e quebra).
3. Ctrl+S → pasta `C:\Users\User\OneDrive\EXTRATOS\_ferramentas` → nome `conversor.py` → Tipo: **Todos os arquivos** → Salvar → Substituir.
4. Conferir na pasta: o arquivo `conversor` tem que estar como **Python File** (não "Documento de Texto"; se estiver, o Windows escondeu um ".txt": renomear tirando o .txt) e com data/hora de agora.
5. Dois cliques em `REFAZER_NAO` → ele lista os .md com Confere NÃO e os "tabela NÃO montada" (texto por página: Cora FWL 07 e 08, Infiniti, Itaú Conta Garantida) → responder **S** → espera terminar.
6. Se algum não voltar (pasta de mês antes de 07/2026, fora do corte `desde`): arrastar o original sobre `CONVERTER_AGORA.bat`. Se travar com "Outra conversão já está rodando", esperar ou apagar o `conversor.lock`.
7. Mandar o `conversor` (log) arrastando para a conversa.

## Como trabalhar no conversor (para a próxima sessão)
- Código: `kit-rof/conversor/conversor.py` (branch `claude/affectionate-edison-id48dx`). No PC dela fica em `C:\Users\User\OneDrive\EXTRATOS\_ferramentas` (com `config.json`, `estado.json`, `conversor.log`, `CONVERTER_AGORA.bat`, `REFAZER_NAO.bat`).
- Testar aqui: baixar o original pelo conector do Drive, `pip install pymupdf pdfplumber` num venv e rodar `python -I conversor.py arquivo.pdf`; comparar com OFX/CSV do mesmo mês e conferir saldo linha a linha. Antes de entregar, rodar a versão antiga e a nova nos extratos que já davam "sim" (não pode mudar nada).
- Entregar para ela: link raw do GitHub (`https://github.com/rofcontabilidade/meus-projetos/raw/claude/affectionate-edison-id48dx/kit-rof/conversor/conversor.py`), Ctrl+S em `_ferramentas`, Tipo "Todos os arquivos". Cuidado: o Chrome traduz o código (desligar tradução) e o Windows esconde ".txt" (conferir Tipo = Python File / Arquivo em Lotes).
- Depois de instalar: dois cliques em `REFAZER_NAO` (lista, ela confirma com S, refaz). Log ela manda arrastando `conversor` (Documento de Texto) para a conversa.

## Como a Rosangela atualiza skills (aprendido)
- Configurações > Skills > **+ Adicionar** > enviar **um zip por vez** (vários de uma vez falha).
- Enviar **só o zip**; nunca o SKILL.md solto (substitui a skill e apaga references/scripts).
- Conferir "atualizado agora" e o número em **Conteúdo**. O app guarda versões anteriores.
- Esta cópia das skills na sessão (`/root/.claude/skills/synced`) só se atualiza de tempos em tempos.

## Jeito de trabalhar com ela
Português simples, passos curtos, um de cada vez; pedir print quando for tela do app; mostrar antes de mexer; nunca alterar o Drive sem autorização.
