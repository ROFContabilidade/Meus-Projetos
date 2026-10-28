<#
  Cria a tarefa "ROF - Converter extratos" no Agendador de Tarefas do Windows:
  roda ao entrar no Windows e a cada 5 minutos, oculta, com o usuario logado (o OneDrive precisa estar aberto).
  Com Python: pythonw.exe (nao abre janela). Sem Python: PowerShell oculto (plano B, so PDF).
#>
param([string]$Python = '')
$aqui = $PSScriptRoot
$nome = 'ROF - Converter extratos'

if ($Python -and (Test-Path -LiteralPath $Python)) {
    $pyw = Join-Path (Split-Path $Python) 'pythonw.exe'
    if (-not (Test-Path -LiteralPath $pyw)) { $pyw = $Python }
    $exe = $pyw
    $arg = "`"$(Join-Path $aqui 'conversor.py')`" --oculto"
} else {
    $exe = 'powershell.exe'
    $arg = "-NoProfile -NonInteractive -ExecutionPolicy Bypass -WindowStyle Hidden -File `"$(Join-Path $aqui 'converter_sem_python.ps1')`" -Oculto"
}

$svc = New-Object -ComObject 'Schedule.Service'; $svc.Connect()
$def = $svc.NewTask(0)
$def.RegistrationInfo.Description = 'Converte os extratos (PDF/OFX/CSV/XLSX) da pasta EXTRATOS\01 - Entrada em <nome>_extrato.md. Tudo local; o original nao e alterado.'
$def.Settings.StartWhenAvailable = $true
$def.Settings.DisallowStartIfOnBatteries = $false
$def.Settings.StopIfGoingOnBatteries = $false
$def.Settings.ExecutionTimeLimit = 'PT1H'
$def.Settings.MultipleInstances = 2          # se a anterior ainda estiver rodando, nao abre outra
$def.Settings.Hidden = $true
$def.Principal.LogonType = 3                 # so com o usuario logado
$def.Principal.UserId = "$env:USERDOMAIN\$env:USERNAME"

$g = $def.Triggers.Create(1)                 # 1 = horario: a partir de agora, repete a cada 5 min para sempre
$g.StartBoundary = (Get-Date).AddMinutes(1).ToString("yyyy-MM-dd'T'HH:mm:ss")
$g.Repetition.Interval = 'PT5M'
$g.Repetition.Duration = ''
$g2 = $def.Triggers.Create(9)                # 9 = ao fazer logon (ao ligar o computador)
$g2.UserId = "$env:USERDOMAIN\$env:USERNAME"
$g2.Delay = 'PT1M'

$a = $def.Actions.Create(0)
$a.Path = $exe
$a.Arguments = $arg
$a.WorkingDirectory = $aqui

try {
    $svc.GetFolder('\').RegisterTaskDefinition($nome, $def, 6, $null, $null, 3) | Out-Null
} catch {
    # alguns Windows nao deixam criar o gatilho de logon sem administrador: fica so o de 5 em 5 minutos
    $def.Triggers.Remove(2)
    $svc.GetFolder('\').RegisterTaskDefinition($nome, $def, 6, $null, $null, 3) | Out-Null
    Write-Host '  (sem gatilho de logon: o de 5 em 5 minutos ja cobre o computador recem-ligado)'
}
Write-Host "  Tarefa '$nome' criada: ao entrar no Windows e a cada 5 minutos."
