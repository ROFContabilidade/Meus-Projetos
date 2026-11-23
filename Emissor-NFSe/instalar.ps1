# Instalador do Emissor ROF de NFS-e (uma vez por computador).
# - Confere/instala o Python 3.12
# - Copia o programa para C:\EmissorROF\programa
# - Instala as bibliotecas e roda os 21 testes
# - Cria a configuracao (%APPDATA%\EmissorROF\config.json) e copia as fichas das empresas
# Nada aqui pede ou grava senha.
$ErrorActionPreference = 'Stop'
$Aqui    = Split-Path -Parent $MyInvocation.MyCommand.Path
$Destino = 'C:\EmissorROF'
$Local   = Join-Path $env:APPDATA 'EmissorROF'

function Passo($t) { Write-Host ''; Write-Host "=== $t ===" -ForegroundColor Cyan }

function Achar-Python {
    foreach ($c in @('py -3.12', 'py -3', 'python')) {
        try {
            $partes = @($c.Split(' '))
            $resto = @($partes | Select-Object -Skip 1)
            $v = & $partes[0] @resto --version 2>&1
            if ("$v" -match 'Python 3\.(1[0-9])') { return $c }
        } catch { }
    }
    return $null
}

Passo '1/5 Python'
$py = Achar-Python
if (-not $py) {
    Write-Host 'Python nao encontrado. Instalando o Python 3.12 pelo winget...'
    try {
        winget install -e --id Python.Python.3.12 --scope user --accept-package-agreements --accept-source-agreements
    } catch {
        Write-Host 'Nao consegui instalar sozinho. Baixe em https://www.python.org/downloads/ (marque "Add python.exe to PATH") e rode este instalador de novo.' -ForegroundColor Yellow
        exit 1
    }
    $env:Path = [Environment]::GetEnvironmentVariable('Path', 'User') + ';' + [Environment]::GetEnvironmentVariable('Path', 'Machine')
    $py = Achar-Python
    if (-not $py) { Write-Host 'Python instalado. Feche esta janela e rode o instalador de novo.' -ForegroundColor Yellow; exit 1 }
}
Write-Host "Usando: $py"
$PyExe  = @($py.Split(' '))[0]
$PyArgs = @(@($py.Split(' ')) | Select-Object -Skip 1)
function Py { & $PyExe @PyArgs @args }

Passo '2/5 Copiando o programa para C:\EmissorROF'
New-Item -ItemType Directory -Force -Path $Destino | Out-Null
foreach ($sub in @('programa', 'docs', 'modelos')) {
    New-Item -ItemType Directory -Force -Path (Join-Path $Destino $sub) | Out-Null
    Copy-Item -Recurse -Force (Join-Path $Aqui "$sub\*") (Join-Path $Destino $sub)
}
Get-ChildItem $Aqui -Filter '*.bat' | Copy-Item -Destination $Destino -Force
Get-ChildItem $Aqui -Filter '*.ps1' | Copy-Item -Destination $Destino -Force
foreach ($arq in @('CLAUDE.md', 'LEIA-ME.md', 'COMECE AQUI.txt')) { Copy-Item -Force (Join-Path $Aqui $arq) $Destino }
New-Item -ItemType Directory -Force -Path (Join-Path $Destino 'andamentos') | Out-Null
Set-Content -Path (Join-Path $Destino 'python.txt') -Value $py -Encoding ASCII

Passo '3/5 Bibliotecas'
Py -m pip install --upgrade pip --quiet
Py -m pip install -r (Join-Path $Destino 'programa\requirements.txt')
Py -m pip install openpyxl --quiet   # leitura das planilhas de faturamento no G:

Passo '4/5 Testes automaticos (devem dar OK)'
Push-Location (Join-Path $Destino 'programa')
Py emissor_rof.py --testes
Pop-Location

Passo '5/5 Configuracao e fichas das empresas'
New-Item -ItemType Directory -Force -Path (Join-Path $Local 'dados\empresas') | Out-Null
$cfg = Join-Path $Local 'config.json'
if (-not (Test-Path $cfg)) {
    # Serie 2 = computador da Rosangela (o do Dr. Everton usa a serie 1). Nunca repetir serie entre computadores.
    $json = '{ "pasta_dados": "", "serie": 2, "ambiente": "1", "caminho_pfx": "", "algoritmo_assinatura": "sha1", "urls": {}, "ca_bundle": "", "usuario": "' + $env:USERNAME + '" }'
    [System.IO.File]::WriteAllText($cfg, $json, (New-Object System.Text.UTF8Encoding($false)))
    Write-Host "Configuracao criada: $cfg (producao, serie 2)"
} else {
    Write-Host "Configuracao ja existia, mantida: $cfg"
}
foreach ($f in Get-ChildItem (Join-Path $Aqui 'fichas') -Filter '*.json') {
    $alvo = Join-Path $Local ('dados\empresas\' + $f.Name)
    if (Test-Path $alvo) { Write-Host "Ficha ja existia, mantida: $($f.Name)" }
    else { Copy-Item $f.FullName $alvo; Write-Host "Ficha instalada: $($f.Name)" }
}

Write-Host ''
Write-Host 'PRONTO. Proximo passo: 2_INSTALAR_CERTIFICADO.bat (para cada empresa).' -ForegroundColor Green
