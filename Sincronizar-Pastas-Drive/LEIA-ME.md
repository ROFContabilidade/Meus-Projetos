# Sincronizar pastas das empresas (Drive G: → Drive I:)

Copia as subpastas (meses) que faltam de
`G:\Meu Drive\Trabalho ROF\Contabilidade\Arquivos RENATA Dominio`
para `I:\Meu Drive\EMPRESAS ATIVAS`, casando as empresas pelo **número** no início do nome da pasta
(ex.: `012 - EMPRESA X` na origem ↔ `12 - EMPRESA X` no destino).

- Só **copia** o que falta (pastas e arquivos novos). Nunca apaga nem sobrescreve nada no destino.
- Grava um log de cada execução na pasta `logs`.
- Empresas que não têm pasta no destino aparecem no log como "ATENÇÃO" (não são criadas automaticamente).

## Instalação (uma vez, no computador do escritório)

1. Copie esta pasta para o computador (ex.: `C:\ROF\Sincronizar-Pastas-Drive`).
2. Dê dois cliques em **TESTAR_SIMULACAO.bat** — mostra o que seria copiado, sem copiar nada. Confira.
3. Se estiver certo, dê dois cliques em **EXECUTAR_AGORA.bat** para copiar o que falta hoje.
4. Clique com o botão direito em **agendar_tarefa.ps1** → *Executar com o PowerShell*.
   Isso cria a tarefa **"ROF - Sincronizar pastas das empresas"**: todo **dia 2 de cada mês às 07:00**.

## Requisitos

- O Google Drive para computador precisa estar aberto e logado nas duas contas (G: e I:).
- O computador precisa estar ligado e com o usuário logado. Se estiver desligado às 07:00 do dia 2,
  a tarefa roda assim que o computador for ligado.
- Para mudar o horário, altere `$horario` em `agendar_tarefa.ps1` e rode de novo.
