<#
  Plano B quando o computador nao tem Python: faz OCR do Windows em TODAS as paginas do PDF
  e grava <nome>_extrato.md com o texto limpo por pagina (sem tabela e sem "Confere").
  OFX/CSV/XLSX precisam do Python (rode o instalador de novo para instalar).

  Uso: converter_sem_python.ps1 [arquivo1.pdf arquivo2.pdf ...]   (sem arquivos = varre a pasta de entrada)
#>
param([Parameter(ValueFromRemainingArguments = $true)][string[]]$Arquivos, [switch]$Oculto)
$ErrorActionPreference = 'Stop'
$aqui = $PSScriptRoot
$log = Join-Path $aqui 'conversor.log'
$ocr = Join-Path $aqui 'ocr_windows.ps1'
$utf8 = New-Object System.Text.UTF8Encoding $false

function Msg($t) { if (-not $Oculto) { Write-Host $t } }
function Registrar($arq, $res) {
    $l = '{0}|{1}|{2}' -f (Get-Date -Format 'dd/MM/yyyy HH:mm'), $arq, $res
    try { [IO.File]::AppendAllText($log, $l + "`r`n", $utf8) } catch { }
}
function Chave($t) {
    $k = ($t.ToLowerInvariant() -replace '\s+', ' ').Trim()
    if ($k -match 'p.gina|emitido em|impresso em') { $k = $k -replace '\d', '#' }
    $k
}
function Destino($arq) {
    $base = Join-Path ([IO.Path]::GetDirectoryName($arq)) ([IO.Path]::GetFileNameWithoutExtension($arq) + '_extrato')
    $alvo = "$base.md"; $n = 2
    while (Test-Path -LiteralPath $alvo) { $alvo = "$base ($n).md"; $n++ }
    $alvo
}

function Converter($arq) {
    $t0 = Get-Date
    if ([IO.Path]::GetExtension($arq).ToLowerInvariant() -ne '.pdf') { throw 'sem Python so converte PDF (instale o Python para OFX/CSV/XLSX)' }
    $sha = [BitConverter]::ToString((New-Object Security.Cryptography.SHA1Managed).ComputeHash([Text.Encoding]::UTF8.GetBytes($arq))).Replace('-', '').Substring(0, 8).ToLower()
    $nome = [IO.Path]::GetFileNameWithoutExtension($arq); if ($nome.Length -gt 60) { $nome = $nome.Substring(0, 60) }
    $pasta = Join-Path $env:TEMP "ROF-Extratos-OCR\$nome-$sha"
    & powershell.exe -NoProfile -ExecutionPolicy Bypass -File $ocr -Pdf $arq -Saida $pasta | Out-Null
    if ($LASTEXITCODE -eq 2) { throw 'PDF protegido por senha ou danificado' }
    if ($LASTEXITCODE -eq 3) { throw 'OCR em portugues nao instalado no Windows' }
    $total = [int](& powershell.exe -NoProfile -ExecutionPolicy Bypass -File $ocr -Pdf $arq -Contar)
    $pags = @(); $cont = @{}
    for ($p = 1; $p -le $total; $p++) {
        $f = Join-Path $pasta "p$p.txt"
        $ls = if (Test-Path -LiteralPath $f) { @([IO.File]::ReadAllLines($f, $utf8) | Where-Object { $_.Trim() }) } else { @() }
        $pags += , $ls
        foreach ($k in ($ls | ForEach-Object { Chave $_ } | Select-Object -Unique)) { $cont[$k] = 1 + [int]$cont[$k] }
    }
    $out = New-Object System.Collections.Generic.List[string]
    $out.Add("# Extrato - $([IO.Path]::GetFileName($arq))")
    $out.Add('Banco: ? | Ag: ? | Conta: ? | Período: ?')
    $out.Add("Origem: $arq | $total página(s) | método: OCR | OCR: $total pág. (imagens: $pasta) | gerado em $(Get-Date -Format 'dd/MM/yyyy HH:mm')")
    $out.Add('Obs: computador sem Python: tabela e Confere não montados; texto limpo por página abaixo (rode o instalador de novo para instalar o Python)')
    $out.Add('')
    $vistos = @{}
    for ($p = 1; $p -le $total; $p++) {
        $out.Add("## Página $p [OCR]"); $n = 0
        foreach ($l in $pags[$p - 1]) {
            $k = Chave $l
            if ($k -match '^p.g(ina|\.)?\s*\d+\s*(de|/)\s*\d+$' -or $k -match 'ouvidoria|\bsac\b|0800|fale conosco') { continue }
            if ($total -ge 2 -and $cont[$k] -gt $total / 2) { if ($vistos[$k]) { continue }; $vistos[$k] = 1 }
            $out.Add($l); $n++
        }
        if ($n -eq 0) { $out.Add('(OCR sem texto: abrir a imagem da página)') }
    }
    $alvo = Destino $arq
    [IO.File]::WriteAllLines($alvo, [string[]]$out, $utf8)
    $res = 'ok OCR {0} pág. (sem Python, texto por página) | {1:N1}s -> {2}' -f $total, ((Get-Date) - $t0).TotalSeconds, [IO.Path]::GetFileName($alvo)
    Registrar $arq $res; Msg "$([IO.Path]::GetFileName($arq)): $res"
}

if ($Arquivos) {
    foreach ($a in $Arquivos) {
        try { Converter ((Resolve-Path -LiteralPath $a).ProviderPath) } catch { Registrar $a "ERRO: $($_.Exception.Message)"; Msg "$a : ERRO: $($_.Exception.Message)" }
    }
    exit 0
}

$cfg = Join-Path $aqui 'config.json'
$entrada = if (Test-Path -LiteralPath $cfg) { (Get-Content -LiteralPath $cfg -Raw -Encoding UTF8 | ConvertFrom-Json).entrada } else { Join-Path (Split-Path $aqui) '01 - Entrada' }
if (-not (Test-Path -LiteralPath $entrada)) { Registrar $entrada 'ERRO: pasta de entrada não encontrada'; exit 1 }
$feitos = 0
Get-ChildItem -LiteralPath $entrada -Recurse -File -Filter *.pdf | Where-Object {
    $_.FullName.Substring($entrada.Length) -notmatch '\\[._~][^\\]*\\' -and -not $_.Name.StartsWith('~$') -and
    -not (Test-Path -LiteralPath (Join-Path $_.DirectoryName ($_.BaseName + '_extrato.md'))) -and
    ((Get-Date) - $_.LastWriteTime).TotalSeconds -ge 20
} | ForEach-Object {
    $f = $_.FullName
    try { Converter $f; $feitos++ } catch { Registrar $f "ERRO: $($_.Exception.Message)"; Msg "$f : ERRO: $($_.Exception.Message)" }
}
if (-not $feitos) { Msg 'Nada novo para converter.' }
