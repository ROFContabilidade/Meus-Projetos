<#
  Organiza os arquivos fiscais do mes da COSMETICI (empresa 25 no Dominio)
  Pasta: I:\Meu Drive\EMPRESAS ATIVAS\25_<Nome>\FISCAL(-CONTABIL)\AAAA\MM_AAAA

  1. Cria a pasta do mes (se nao existir) e as subpastas padrao:
       01_XML_Saidas  02_XML_Entradas  03_Eventos  04_CTe  05_NFSe_Tomadas
       06_SPED  07_Guias  08_Relatorios  09_Apuracao
  2. Extrai os ZIP que estiverem soltos na pasta do mes (o ZIP fica onde esta).
  3. Separa cada XML pelo CONTEUDO (nao pelo nome):
       NF-e emitida pela COSMETICI -> 01_XML_Saidas | NF-e de fornecedor/cliente -> 02_XML_Entradas
       evento/cancelamento/CC-e/inutilizacao -> 03_Eventos | CT-e -> 04_CTe | NFS-e -> 05_NFSe_Tomadas
  4. Move SPED (.txt/.REC), guias (DARF/ICMS/GR .pdf) e relatorios SIEG (.xlsx) para a subpasta certa.
  Nunca apaga nem sobrescreve: arquivo que ja existe no destino fica onde esta (aparece no log).

  Uso:
    .\organizar_fiscal_cosmetici.ps1                     -> mes anterior
    .\organizar_fiscal_cosmetici.ps1 -Mes 09_2026        -> mes informado
    .\organizar_fiscal_cosmetici.ps1 -Simular            -> so mostra o que faria
#>
param(
    [string]$Mes = '',
    [string]$Raiz = 'I:\Meu Drive\EMPRESAS ATIVAS',
    [int]$NumeroEmpresa = 25,
    [string]$NomeContem = 'COSMETIC',
    [string]$Cnpj = '33039048000162',
    [string[]]$SubpastasFiscal = @('FISCAL-CONTABIL', 'FISCAL'),
    [string]$PastaMes = '',
    [switch]$Simular
)

$ErrorActionPreference = 'Stop'
Add-Type -AssemblyName System.IO.Compression.FileSystem
$pastaLogs = Join-Path $PSScriptRoot 'logs'
New-Item -ItemType Directory -Force -Path $pastaLogs | Out-Null
$log = Join-Path $pastaLogs ("organizar_{0:yyyy-MM-dd_HHmm}.log" -f (Get-Date))

function Escrever([string]$msg) {
    $linha = "{0:dd/MM/yyyy HH:mm:ss}  {1}" -f (Get-Date), $msg
    Write-Host $linha
    Add-Content -Path $log -Value $linha -Encoding UTF8
}

$SUB = [ordered]@{
    Saidas = '01_XML_Saidas'; Entradas = '02_XML_Entradas'; Eventos = '03_Eventos'; CTe = '04_CTe'
    NFSe = '05_NFSe_Tomadas'; SPED = '06_SPED'; Guias = '07_Guias'; Relatorios = '08_Relatorios'; Apuracao = '09_Apuracao'
}

if (-not $Mes) { $Mes = (Get-Date).AddMonths(-1).ToString('MM_yyyy') }
if ($Mes -notmatch '^\d{2}_\d{4}$') { Escrever "ERRO: mes invalido '$Mes' (use MM_AAAA, ex.: 09_2026)"; exit 1 }
$ano = $Mes.Substring(3, 4)
Escrever "==== Organizar fiscal COSMETICI $Mes $(if ($Simular) {'(SIMULACAO - nada sera alterado)'}) ===="

# ---------------------------------------------------------------- pasta do mes
if (-not $PastaMes) {
    if (-not (Test-Path -LiteralPath $Raiz)) { Escrever "ERRO: pasta nao encontrada: $Raiz (o Google Drive esta aberto e logado?)"; exit 1 }
    $empresas = @(Get-ChildItem -LiteralPath $Raiz -Directory | Where-Object {
        $_.Name -match '^\s*(\d+)\s*[-_ ]' -and [int]$Matches[1] -eq $NumeroEmpresa })
    if ($empresas.Count -gt 1) { $empresas = @($empresas | Where-Object { $_.Name.ToUpper().Contains($NomeContem) }) }
    if ($empresas.Count -ne 1) {
        Escrever "ERRO: nao achei uma unica pasta da empresa $NumeroEmpresa em $Raiz (achei $($empresas.Count)). Use -PastaMes."
        exit 1
    }
    $fiscal = $null
    foreach ($s in $SubpastasFiscal) {
        $p = Join-Path $empresas[0].FullName $s
        if (Test-Path -LiteralPath $p) { $fiscal = $p; break }
    }
    if (-not $fiscal) { $fiscal = Join-Path $empresas[0].FullName $SubpastasFiscal[-1] }
    $PastaMes = Join-Path (Join-Path $fiscal $ano) $Mes
}
Escrever "Pasta do mes: $PastaMes"
if (-not (Test-Path -LiteralPath $PastaMes)) {
    Escrever "Criando a pasta do mes"
    if (-not $Simular) { New-Item -ItemType Directory -Force -Path $PastaMes | Out-Null }
}
foreach ($s in $SUB.Values) {
    $p = Join-Path $PastaMes $s
    if (-not (Test-Path -LiteralPath $p)) {
        Escrever "  + subpasta $s"
        if (-not $Simular) { New-Item -ItemType Directory -Force -Path $p | Out-Null }
    }
}

$cont = @{}
foreach ($k in $SUB.Keys) { $cont[$k] = 0 }
$cont['Ignorado'] = 0; $cont['JaExiste'] = 0

function Classificar-Xml([string]$texto) {
    if ($texto -match '<procEventoNFe|<envEvento|<retEnvEvento|<procInutNFe|<inutNFe|<retInutNFe|<procEventoCTe') { return 'Eventos' }
    if ($texto -match '<cteProc|<infCte[ >]') { return 'CTe' }
    if ($texto -match '<NFSe[ >]|<CompNfse|<Nfse[ >]|<ConsultarNfse') { return 'NFSe' }
    if ($texto -match '<nfeProc|<NFe[ >]') {
        if ($texto -match '<emit>\s*<CNPJ>(\d{14})</CNPJ>') {
            if ($Matches[1] -eq $Cnpj) { return 'Saidas' }
        }
        return 'Entradas'
    }
    return $null
}

function Classificar-Arquivo([System.IO.FileInfo]$f) {
    $n = $f.Name.ToUpper()
    switch -Regex ($f.Extension.ToLower()) {
        '^\.xml$' { return Classificar-Xml ([System.IO.File]::ReadAllText($f.FullName)) }
        '^\.(txt|rec)$' { if ($n -match 'SPED|EFD|PISCOFINS') { return 'SPED' } }
        '^\.pdf$' {
            if ($n -match '^(DARF|ICMS|GR|GNRE|GUIA|DAS|ISS|RECIBO)') { return 'Guias' }
            if ($n -match 'SPED') { return 'SPED' }
        }
        '^\.(xlsx|xls|csv)$' {
            if ($n -match '^RELATORIO|DEMONST') { return 'Relatorios' }
            if ($n -match '^APURACAO_FISCAL') { return 'Apuracao' }
        }
    }
    return $null
}

function Mover([string]$origem, [string]$tipo, [string]$nome) {
    $dest = Join-Path (Join-Path $PastaMes $SUB[$tipo]) $nome
    if (Test-Path -LiteralPath $dest) { $script:cont['JaExiste']++; return }
    Escrever "  $nome -> $($SUB[$tipo])"
    if (-not $Simular) { Move-Item -LiteralPath $origem -Destination $dest }
    $script:cont[$tipo]++
}

function Gravar([byte[]]$bytes, [string]$tipo, [string]$nome) {
    $dest = Join-Path (Join-Path $PastaMes $SUB[$tipo]) $nome
    if (Test-Path -LiteralPath $dest) { $script:cont['JaExiste']++; return }
    if (-not $Simular) { [System.IO.File]::WriteAllBytes($dest, $bytes) }
    $script:cont[$tipo]++
}

function Extrair-Zip([string]$caminho, [string]$rotulo) {
    $z = [System.IO.Compression.ZipFile]::OpenRead($caminho)
    try {
        foreach ($e in $z.Entries) {
            if (-not $e.Name) { continue }
            $ms = New-Object System.IO.MemoryStream
            $s = $e.Open(); $s.CopyTo($ms); $s.Close()
            $bytes = $ms.ToArray()
            if ($e.Name.ToLower().EndsWith('.zip')) {
                $tmp = [System.IO.Path]::GetTempFileName()
                [System.IO.File]::WriteAllBytes($tmp, $bytes)
                Extrair-Zip $tmp "$rotulo!$($e.Name)"
                Remove-Item -LiteralPath $tmp
            } elseif ($e.Name.ToLower().EndsWith('.xml')) {
                $tipo = Classificar-Xml ([System.Text.Encoding]::UTF8.GetString($bytes))
                if ($tipo) { Gravar $bytes $tipo $e.Name } else { $script:cont['Ignorado']++ }
            }
        }
    } finally { $z.Dispose() }
}

if (Test-Path -LiteralPath $PastaMes) {
    $zips = @(Get-ChildItem -LiteralPath $PastaMes -File -Filter *.zip)
    foreach ($zf in $zips) {
        $antes = ($cont.Values | Measure-Object -Sum).Sum
        Extrair-Zip $zf.FullName $zf.Name
        Escrever "  ZIP $($zf.Name): $((($cont.Values | Measure-Object -Sum).Sum) - $antes) arquivo(s) analisado(s)"
    }
    foreach ($f in @(Get-ChildItem -LiteralPath $PastaMes -File)) {
        if ($f.Extension.ToLower() -eq '.zip') { continue }
        $tipo = Classificar-Arquivo $f
        if ($tipo) { Mover $f.FullName $tipo $f.Name } else { $cont['Ignorado']++; Escrever "  (fica na pasta do mes) $($f.Name)" }
    }
}

Escrever ("Resumo: " + (($SUB.Keys | ForEach-Object { "$($SUB[$_])=$($cont[$_])" }) -join '  ') + "  | ja existiam=$($cont['JaExiste'])  sem classificacao=$($cont['Ignorado'])")
Escrever "==== Fim ===="
