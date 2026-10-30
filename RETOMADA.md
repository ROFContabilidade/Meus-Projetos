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

## Como a Rosangela atualiza skills (aprendido)
- Configurações > Skills > **+ Adicionar** > enviar **um zip por vez** (vários de uma vez falha).
- Enviar **só o zip**; nunca o SKILL.md solto (substitui a skill e apaga references/scripts).
- Conferir "atualizado agora" e o número em **Conteúdo**. O app guarda versões anteriores.
- Esta cópia das skills na sessão (`/root/.claude/skills/synced`) só se atualiza de tempos em tempos.

## Jeito de trabalhar com ela
Português simples, passos curtos, um de cada vez; pedir print quando for tela do app; mostrar antes de mexer; nunca alterar o Drive sem autorização.
