<#
  Sincronizar pastas das empresas
  Origem : G:\Meu Drive\Trabalho ROF\Contabilidade\Arquivos RENATA Dominio
  Destino: I:\Meu Drive\EMPRESAS ATIVAS

  Para cada empresa da origem (pasta "NUMERO - NOME"), procura no destino a
  pasta com o MESMO NUMERO e copia somente o que estiver faltando
  (pastas de meses e arquivos novos). Nunca apaga nem sobrescreve nada no destino.

  Uso:
    .\sincronizar_pastas.ps1            -> copia o que falta
    .\sincronizar_pastas.ps1 -Simular   -> so mostra o que seria copiado
#>
param(
    [string]$Origem  = 'G:\Meu Drive\Trabalho ROF\Contabilidade\Arquivos RENATA Dominio',
    [string]$Destino = 'I:\Meu Drive\EMPRESAS ATIVAS',
    [switch]$Simular
)

$ErrorActionPreference = 'Stop'
$pastaLogs = Join-Path $PSScriptRoot 'logs'
New-Item -ItemType Directory -Force -Path $pastaLogs | Out-Null
$log = Join-Path $pastaLogs ("sincronizacao_{0:yyyy-MM-dd_HHmm}.log" -f (Get-Date))

function Escrever([string]$msg) {
    $linha = "{0:dd/MM/yyyy HH:mm:ss}  {1}" -f (Get-Date), $msg
    Write-Host $linha
    Add-Content -Path $log -Value $linha -Encoding UTF8
}

# Numero da empresa = digitos no inicio do nome da pasta ("012 - EMPRESA" -> 12)
function NumeroEmpresa([string]$nome) {
    if ($nome -match '^\s*(\d+)') { return [int]$Matches[1] }
    return $null
}

Escrever "==== Inicio $(if ($Simular) {'(SIMULACAO)'}) ===="

# O Google Drive para desktop pode demorar para montar as unidades apos ligar o PC
foreach ($p in @($Origem, $Destino)) {
    $tentativas = 0
    while (-not (Test-Path -LiteralPath $p) -and $tentativas -lt 20) {
        Escrever "Aguardando a pasta ficar disponivel: $p"
        Start-Sleep -Seconds 30
        $tentativas++
    }
    if (-not (Test-Path -LiteralPath $p)) {
        Escrever "ERRO: pasta nao encontrada: $p  (o Google Drive esta aberto e logado?)"
        exit 1
    }
}

# Indexa as empresas do destino pelo numero
$destinos = @{}
foreach ($d in Get-ChildItem -LiteralPath $Destino -Directory) {
    $n = NumeroEmpresa $d.Name
    if ($null -ne $n -and -not $destinos.ContainsKey($n)) { $destinos[$n] = $d.FullName }
}

$copiadas = 0; $semDestino = @()
foreach ($emp in Get-ChildItem -LiteralPath $Origem -Directory | Sort-Object Name) {
    $n = NumeroEmpresa $emp.Name
    if ($null -eq $n) { Escrever "Ignorada (nome sem numero): $($emp.Name)"; continue }
    if (-not $destinos.ContainsKey($n)) { $semDestino += $emp.Name; continue }

    $alvo = $destinos[$n]
    $faltando = Get-ChildItem -LiteralPath $emp.FullName -Directory |
        Where-Object { -not (Test-Path -LiteralPath (Join-Path $alvo $_.Name)) }
    foreach ($f in $faltando) { Escrever "  [$($emp.Name)] pasta faltando: $($f.Name)" }

    # /E subpastas | /XC /XN /XO nunca sobrescreve arquivos existentes | /XX nao apaga nada
    $opcoes = @('/E', '/XC', '/XN', '/XO', '/XX', '/R:2', '/W:10', '/NP', '/NDL', '/NJH', '/NJS')
    if ($Simular) { $opcoes += '/L' }
    $saida = & robocopy $emp.FullName $alvo @opcoes
    $codigo = $LASTEXITCODE
    $arquivos = @($saida | Where-Object { $_ -match '\S' })

    if ($codigo -ge 8) {
        Escrever "ERRO robocopy (codigo $codigo) em $($emp.Name)"
        $arquivos | ForEach-Object { Escrever "    $_" }
    } elseif ($arquivos.Count -gt 0) {
        $copiadas++
        Escrever "[$($emp.Name)] -> $alvo : $($arquivos.Count) arquivo(s) $(if ($Simular) {'seriam copiados'} else {'copiados'})"
        $arquivos | ForEach-Object { Escrever "    $($_.Trim())" }
    }
}

if ($semDestino.Count -gt 0) {
    Escrever "ATENCAO: empresas sem pasta correspondente em '$Destino' (nada foi copiado):"
    $semDestino | ForEach-Object { Escrever "    $_" }
}
Escrever "==== Fim: $copiadas empresa(s) com arquivos novos. Log: $log ===="
