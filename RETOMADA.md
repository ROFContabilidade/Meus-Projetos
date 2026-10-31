# Retomada: skills ROF (economia de tokens e autonomia)

Resumo da sessão de 29/10/2026 (Rosangela). Ler só este arquivo para continuar; não precisa reler a conversa anterior.

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
- CORRIGIDO em `kit-rof/conversor/conversor.py` (30/10/2026, falta a Rosangela instalar em `_ferramentas`):
  Sicoob SISBR (leitor próprio `sicoob_sisbr`; depósito bloqueado vai para seção "## Depósito bloqueado", fora da tabela),
  Cresol (tabela para em "Totalizadores"/"Resumo"), Santander (saldo sem data no fim de extrato invertido não é saldo inicial),
  Sicredi ("Lançamentos Futuros" fora; "Saldo Atual" só vale se não há saldo por linha). Regressão: Bradesco, MP, Inter, BB, Cora, Sicoob Everton iguais.
- INSTALADO e refeito em 30/10/2026 ~19h (REFAZER_NAO.bat em `_ferramentas`; limpeza agora respeita o corte `desde`).
  Conferido no Drive: Pai e Filhos Sicoob set, Cross Cresol ago, SDM Santander set e Mohr Sicredi set = Confere sim.
- Ainda NÃO / sem tabela (próximos a olhar): CSV do Inter (Jungle "Extrato-01-07-2026-a-19-10-2026-CSV", 4 meses em 3 pastas;
  "INTER Extrato-01-09...-CSV"); C6 "Extato 6C_09.26.pdf" (dif. 39.525,33); "extrato pj agosto.pdf" (dif. -2.893,71) e
  "extrato setembro.pdf" (dif. 232,98) da 155 L R J Santos; "texto por página": Extrato Infiniti, Itaú Conta Garantida (Jungle),
  Cora FWL 07 e 08 (o de 09 sai certo).

## Como a Rosangela atualiza skills (aprendido)
- Configurações > Skills > **+ Adicionar** > enviar **um zip por vez** (vários de uma vez falha).
- Enviar **só o zip**; nunca o SKILL.md solto (substitui a skill e apaga references/scripts).
- Conferir "atualizado agora" e o número em **Conteúdo**. O app guarda versões anteriores.
- Esta cópia das skills na sessão (`/root/.claude/skills/synced`) só se atualiza de tempos em tempos.

## Jeito de trabalhar com ela
Português simples, passos curtos, um de cada vez; pedir print quando for tela do app; mostrar antes de mexer; nunca alterar o Drive sem autorização.
