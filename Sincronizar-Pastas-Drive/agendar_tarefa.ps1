<#
  Cria a tarefa no Agendador de Tarefas do Windows:
  todo dia 2 de cada mes as 07:00 roda sincronizar_pastas.ps1.
  Se o computador estiver desligado nesse horario, roda assim que for ligado.

  Executar uma vez:  clique direito -> "Executar com o PowerShell"
#>
$script  = Join-Path $PSScriptRoot 'sincronizar_pastas.ps1'
$nome    = 'ROF - Sincronizar pastas das empresas'
$horario = '07:00'

$acao = New-ScheduledTaskAction -Execute 'powershell.exe' `
    -Argument "-NoProfile -ExecutionPolicy Bypass -WindowStyle Hidden -File `"$script`""

# Gatilho mensal (dia 2, todos os meses) via objeto COM do Agendador
$svc = New-Object -ComObject 'Schedule.Service'; $svc.Connect()
$def = $svc.NewTask(0)
$def.RegistrationInfo.Description = 'Copia para I:\Meu Drive\EMPRESAS ATIVAS as pastas de meses que faltam (origem G:\...\Arquivos RENATA Dominio).'
$def.Settings.StartWhenAvailable = $true          # roda depois se o PC estava desligado
$def.Settings.DisallowStartIfOnBatteries = $false
$def.Settings.StopIfGoingOnBatteries = $false
$def.Settings.ExecutionTimeLimit = 'PT4H'
$def.Principal.LogonType = 3                      # so com o usuario logado (o Google Drive precisa estar aberto)

$gat = $def.Triggers.Create(4)                    # 4 = mensal
$gat.StartBoundary = (Get-Date -Format 'yyyy-MM-') + "02T$($horario):00"
$gat.DaysOfMonth = 2                              # bit do dia 2
$gat.MonthsOfYear = 4095                          # todos os 12 meses

$a = $def.Actions.Create(0)
$a.Path = $acao.Execute
$a.Arguments = $acao.Arguments

$svc.GetFolder('\').RegisterTaskDefinition($nome, $def, 6, $null, $null, 3) | Out-Null
Write-Host "Tarefa '$nome' criada: todo dia 2 as $horario."
Write-Host "Para testar agora: Start-ScheduledTask -TaskName '$nome'"
