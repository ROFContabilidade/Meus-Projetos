# Sincronizar pastas mensais das empresas (Drive G: → Drive I:)

Copia as pastas mensais (`08_2026`, `09_2026`, ...) que faltam de
`G:\Meu Drive\Trabalho ROF\Contabilidade\Arquivos RENATA Dominio\<NUMERO - Nome>`
para `I:\Meu Drive\EMPRESAS ATIVAS\<NUMERO_Nome>\FISCAL\<ANO>\`.

- As empresas são casadas pelo **número** no início do nome (`67 - Ligiane Siqueira` ↔ `67_Ligiane Siqueira Estofados`).
- Na origem, as pastas `MM_AAAA` são procuradas em qualquer subpasta da empresa.
- Só copia meses que **ainda não existem** no destino. Nunca apaga nem sobrescreve nada.
- Outras pastas (ex.: `Demonstrações Contabeis`) não são copiadas.
- Grava um log de cada execução na pasta `logs`.

## Instalação (uma vez, no computador do escritório)

1. Baixe o arquivo **Sincronizar-Pastas-Drive.zip**.
2. Na pasta Downloads, clique com o botão direito no ZIP → **Extrair tudo...** → **Extrair**.
3. Na pasta extraída, dê dois cliques em **INSTALAR.bat**.
   (Se aparecer "O Windows protegeu o computador", clique em **Mais informações → Executar assim mesmo**.)
4. O instalador copia tudo para `C:\ROF\Sincronizar-Pastas-Drive`, cria a tarefa
   **"ROF - Sincronizar pastas das empresas"** (todo **dia 2 de cada mês às 07:00**) e mostra uma simulação.
5. Se a simulação estiver certa, abra `C:\ROF\Sincronizar-Pastas-Drive` e dê dois cliques em
   **EXECUTAR_AGORA.bat** para copiar já o que falta hoje.

## Requisitos

- O Google Drive para computador precisa estar aberto e logado nas duas contas (G: e I:).
- O computador precisa estar ligado e com o usuário logado. Se estiver desligado às 07:00 do dia 2,
  a tarefa roda assim que o computador for ligado.
- Para mudar o horário, altere `$horario` em `agendar_tarefa.ps1` e rode de novo.
