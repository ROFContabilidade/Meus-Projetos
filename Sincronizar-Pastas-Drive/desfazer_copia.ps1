<#
  Desfaz a copia feita por EXECUTAR_AGORA, lendo o log da ultima execucao real.
  Apaga SOMENTE as pastas de mes que aquela execucao criou (linhas "para:" do log).
  No Google Drive, o que for apagado vai para a Lixeira do Drive (recuperavel por 30 dias).

  Uso:
    .\desfazer_copia.ps1          -> apaga so as copias que foram para a EMPRESA ERRADA
    .\desfazer_copia.ps1 -Tudo    -> apaga TODAS as pastas que aquela execucao copiou
#>
param(
    [string]$Destino = 'I:\Meu Drive\EMPRESAS ATIVAS',
    [switch]$Tudo
)

function NumeroEmpresa([string]$nome) {
    if ($nome -match '^\s*(\d+)\s*[-_ ]') { return [int]$Matches[1] }
    return $null
}

# O EXECUTAR_AGORA pode ter sido rodado da pasta extraida (Downloads/Desktop): procura os logs la tambem
$locais = @((Join-Path $PSScriptRoot 'logs'), 'C:\ROF',
            (Join-Path $env:USERPROFILE 'Downloads'), (Join-Path $env:USERPROFILE 'Desktop'),
            [Environment]::GetFolderPath('Desktop'))
$todos = foreach ($l in $locais | Select-Object -Unique) {
    if (Test-Path -LiteralPath $l) { Get-ChildItem -LiteralPath $l -Filter 'sincronizacao_*.log' -Recurse -ErrorAction SilentlyContinue }
}
Write-Host "Logs encontrados: $(@($todos).Count)"
$logs = $todos |
    Where-Object { Select-String -LiteralPath $_.FullName -Pattern 'arquivo\(s\) copiando' -Quiet } |
    Sort-Object LastWriteTime -Descending
if (-not $logs) { Write-Host 'Nenhum log de copia encontrado.'; exit 1 }
$log = $logs[0].FullName
Write-Host "Log usado: $log`n"

$apagar = @(); $empresa = $null
foreach ($linha in Get-Content -LiteralPath $log -Encoding UTF8) {
    if ($linha -match '\[(.+?)\] (\d{2}_\d{4}): \d+ arquivo\(s\) copiando') { $empresa = $Matches[1]; continue }
    if ($linha -match '^\S+ \S+\s+para: (.+)$' -and $empresa) {
        $alvo = $Matches[1].Trim()
        if (-not $alvo.StartsWith($Destino, [StringComparison]::OrdinalIgnoreCase)) { continue }
        if ($alvo -notmatch '\\\d{2}_\d{4}$') { continue }
        $pastaEmpresa = $alvo.Substring($Destino.Length).TrimStart('\').Split('\')[0]
        $errada = (NumeroEmpresa $empresa) -ne (NumeroEmpresa $pastaEmpresa)
        if (($Tudo -or $errada) -and (Test-Path -LiteralPath $alvo)) {
            $apagar += [pscustomobject]@{ Origem = $empresa; Pasta = $alvo; Errada = $errada }
        }
        $empresa = $null
    }
}

if ($apagar.Count -eq 0) { Write-Host 'Nada para apagar.'; exit 0 }
Write-Host "Pastas que serao APAGADAS ($($apagar.Count)):"
$apagar | ForEach-Object { Write-Host ("  {0}  (veio de: {1}){2}" -f $_.Pasta, $_.Origem, $(if ($_.Errada) {'  <- EMPRESA ERRADA'} else {''})) }
Write-Host ''
$resp = Read-Host 'Digite SIM para apagar essas pastas (qualquer outra coisa cancela)'
if ($resp -ne 'SIM') { Write-Host 'Cancelado. Nada foi apagado.'; exit 0 }

foreach ($a in $apagar) {
    try {
        Remove-Item -LiteralPath $a.Pasta -Recurse -Force
        Write-Host "  apagada: $($a.Pasta)"
        # remove a pasta do ano se ficou vazia (criada pela copia)
        $ano = Split-Path $a.Pasta -Parent
        if (-not (Get-ChildItem -LiteralPath $ano -Force)) { Remove-Item -LiteralPath $ano -Force }
    } catch { Write-Host "  ERRO ao apagar $($a.Pasta): $_" }
}
Write-Host "`nConcluido."
