---
name: "rof-sincronizar-pastas"
description: "Rotina mensal da ROF Contabilidade que copia as pastas de meses (MM_AAAA) que faltam de G:\\Meu Drive\\Trabalho ROF\\Contabilidade\\Arquivos RENATA Dominio para I:\\Meu Drive\\EMPRESAS ATIVAS\\<NUM_Nome>\\FISCAL\\<ANO>, todo dia 2 às 07:00 (Agendador de Tarefas do Windows). Usar quando falarem em sincronizar/copiar/extrair pastas das empresas do G: para o I:, pasta EMPRESAS ATIVAS, Arquivos RENATA Dominio, rotina do dia 2, INSTALAR_E_COPIAR, log de sincronização, ou empresa que não recebeu o mês."
---

# ROF — Sincronizar pastas mensais (G: → I:)

Programa em `Sincronizar-Pastas-Drive/` deste repositório. Roda no computador do escritório (Windows),
onde o Google Drive para computador monta **G:** (conta rosangelaoliveirafurtado025@gmail.com) e **I:** (outra conta).
O conector Google Drive desta sessão só enxerga o **G:**; o **I:** não é acessível daqui.

## Regras (sincronizar_pastas.ps1)

- Empresa = número no início do nome, **seguido de espaço, `-` ou `_`** (`67 - Ligiane` ↔ `67_Ligiane Siqueira Estofados`).
  `01.2_Backup Acessórias` **não** é a empresa 01 (ponto depois do número).
- Mais de uma pasta com o mesmo número no I: (ex.: `01_Paes e Bastos` e `1_RBA Contabilidade`):
  usa a de número escrito igual (`01`↔`01`, `1`↔`1`); se empatar, a com mais palavras do nome em comum; senão ignora com ATENCAO.
- Origem: procura pastas `MM_AAAA` em qualquer subpasta da empresa no G: (normalmente `<ANO>\MM_AAAA`).
- Destino: `<empresa no I:>\FISCAL-CONTABIL\<ANO>\MM_AAAA` (ou `FISCAL`, a primeira das duas que já tiver meses).
- Copia **só meses depois do último mês que já existe** em `FISCAL\*\` no I: e **antes do mês atual**.
- Empresa com `FISCAL` sem nenhum mês → ignorada (ATENCAO: copiar o primeiro mês à mão).
- Nunca apaga nem sobrescreve (robocopy `/E /XC /XN /XO /XX`). Log em `C:\ROF\Sincronizar-Pastas-Drive\logs`.

## Instalação / reinstalação

- Arquivo único **`INSTALAR_E_COPIAR.bat`** (não precisa extrair): instala em `C:\ROF\Sincronizar-Pastas-Drive`,
  cria a tarefa **"ROF - Sincronizar pastas das empresas"** (dia 2, 07:00, roda depois se o PC estava desligado),
  mostra a conferência e **só copia se digitar SIM + Enter**.
- Ao mudar qualquer `.ps1`/`.bat`, **regerar** o `INSTALAR_E_COPIAR.bat` (os arquivos vão embutidos em base64
  nas linhas `::ARQ <nome>` / `::B <dados>`; o cabeçalho termina em `exit /b 1`) e conferir que os 8 arquivos voltam idênticos.
- Usuária não técnica: passos curtos, um de cada vez; não pedir para extrair ZIP (rodar de dentro do ZIP falha).

## Cuidados (aprendidos em 01/10/2026)

- **Nunca** alterar/apagar nada nas pastas do Drive sem autorização explícita da Rosangela.
- Sempre rodar/mostrar a **simulação** antes de copiar quando o programa mudar; o código não é testável aqui (sem Windows).
- `DESFAZER_TUDO.bat` / `DESFAZER_EMPRESA_ERRADA.bat` apagam só pastas criadas pela última execução (lendo o log), pedem `SIM`.

## Pendências conhecidas (01/10/2026)

- `0 - Prestação de Serviços` não tem pasta no I: (aviso inofensivo).
- `12 - E J S`: G: tem `2026\05..08_2026`, mas não recebeu na 1ª execução — verificar no I: (`FISCAL\2026` sem mês, mês ≥ 08 já existente, ou nome/número da pasta diferente).
- 07 (DC Grup) e 10 (Lucas Romano): usuária corrigiu as pastas no I:; conferir se passaram a receber.
