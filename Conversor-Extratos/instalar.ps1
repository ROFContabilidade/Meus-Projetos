<#
  Instalador do conversor de extratos (chamado pelo INSTALAR_CONVERSOR.bat).
  1) pergunta a pasta  2) copia os programas para EXTRATOS\_ferramentas  3) Python + pymupdf
  4) tarefa a cada 5 min  5) atalhos  6) regra para o Claude  7) teste com um extrato escaneado de exemplo
#>
$ErrorActionPreference = 'Stop'
$origem = $PSScriptRoot
$utf8 = New-Object System.Text.UTF8Encoding $false

# 1) pasta
$od = if ($env:OneDrive) { $env:OneDrive } else { Join-Path $env:USERPROFILE 'OneDrive' }
$padrao = Join-Path $od 'EXTRATOS'
Write-Host ''
Write-Host "  Pasta dos extratos: $padrao"
$r = Read-Host '  Enter para usar esta pasta, ou digite outra pasta'
$raiz = if ($r.Trim()) { $r.Trim().Trim('"') } else { $padrao }
$entrada = Join-Path $raiz '01 - Entrada'
$ferr = Join-Path $raiz '_ferramentas'
New-Item -ItemType Directory -Force -Path $entrada, $ferr | Out-Null

# 2) programas
Write-Host ''
Write-Host "  1/6  Copiando os programas para $ferr"
foreach ($f in 'conversor.py', 'ocr_windows.ps1', 'converter_sem_python.ps1', 'agendar_tarefa.ps1', 'CONVERTER_AGORA.bat', 'LEIA-ME.md') {
    Copy-Item -LiteralPath (Join-Path $origem $f) -Destination $ferr -Force
}
Get-ChildItem -LiteralPath $ferr | Unblock-File
# pastas dos clientes no Google Drive: o conversor olha so as subpastas "Extrato", arquivos desde 01/09/2026
$drive = @('G:\Meu Drive\Trabalho ROF\Contabilidade\Arquivos RENATA Dominio',
           'G:\Meu Drive\Trabalho ROF\Contabilidade\Arquivos ROF Dominio',
           'G:\Meu Drive\Trabalho ROF\Contabilidade\Arquivos PROTECTION Dominio\25 - Cosmetici')
$cfg = @{ entrada = $entrada; pastas_drive = $drive; desde = '2026-09-01' } | ConvertTo-Json
foreach ($d in $drive) {
    $ok = $false
    foreach ($l in 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z', 'D', 'E', 'F') {
        if (Test-Path -LiteralPath ($l + $d.Substring(1))) { $ok = $true; break }
    }
    Write-Host ('       Drive: {0} {1}' -f $(if ($ok) { 'OK      ' } else { 'NAO ACHEI' }), $d)
}
[IO.File]::WriteAllText((Join-Path $ferr 'config.json'), $cfg, $utf8)

# 3) Python
function Achar-Python {
    foreach ($tentativa in 1, 2) {
        try {
            $p = if ($tentativa -eq 1) { & py -3 -c 'import sys;print(sys.executable)' 2>$null } else { & python -c 'import sys;print(sys.executable)' 2>$null }
            $p = @($p)[0]
            if ($p -and (Test-Path -LiteralPath $p) -and $p -notmatch 'WindowsApps') { return $p }
        } catch { }
    }
    $c = @(Get-ChildItem "$env:LOCALAPPDATA\Programs\Python\Python3*\python.exe", "$env:ProgramFiles\Python3*\python.exe" -ErrorAction SilentlyContinue |
            Sort-Object FullName -Descending)
    if ($c) { return $c[0].FullName }
    return $null
}
Write-Host ''
Write-Host '  2/6  Verificando o Python ...'
$py = Achar-Python
if (-not $py) {
    Write-Host '       Python nao encontrado. Ele e gratuito e e o que monta a tabela e o "Confere".'
    $q = Read-Host '       Instalar o Python agora? (S/N)'
    if ($q -match '^[sS]') {
        if (Get-Command winget -ErrorAction SilentlyContinue) {
            & winget install -e --id Python.Python.3.12 --scope user --silent --accept-package-agreements --accept-source-agreements
            $py = Achar-Python
        } else {
            Write-Host '       Este Windows nao tem o winget. Baixe o Python em https://www.python.org/downloads/'
            Write-Host '       (marque "Add python.exe to PATH") e rode este instalador de novo.'
        }
    }
}
if ($py) {
    Write-Host "       Python: $py"
    Write-Host '       Instalando pymupdf e openpyxl (leitura de PDF e Excel) ...'
    $ErrorActionPreference = 'Continue'
    & $py -m pip install --user --upgrade --disable-pip-version-check --no-warn-script-location -q pymupdf openpyxl
    $ErrorActionPreference = 'Stop'
    $ok = $false
    try { & $py -c 'import pymupdf, openpyxl' 2>$null; $ok = ($LASTEXITCODE -eq 0) } catch { }
    if (-not $ok) { Write-Host '       ATENCAO: pymupdf nao instalou. Tire um print e envie.'; $py = $null }
}
if ($py) {
    [IO.File]::WriteAllText((Join-Path $ferr 'python.txt'), $py, $utf8)
} else {
    Remove-Item -LiteralPath (Join-Path $ferr 'python.txt') -ErrorAction SilentlyContinue
    Write-Host '       Sem Python: vou usar o plano B (so PDF, OCR de todas as paginas, sem tabela).'
}

# 4) tarefa agendada
Write-Host ''
Write-Host '  3/6  Criando a tarefa automatica ...'
& (Join-Path $ferr 'agendar_tarefa.ps1') -Python $py

# 5) atalhos
Write-Host ''
# limpeza: .md que a versao anterior criou para comprovantes, balancetes, planilhas... (pede SIM)
if ($py) {
    Write-Host '       Procurando .md antigos para refazer ...'
    $ErrorActionPreference = 'Continue'
    $lista = & $py (Join-Path $ferr 'conversor.py') --limpar
    $ErrorActionPreference = 'Stop'
    $ultima = @($lista)[-1]
    Write-Host "       $ultima"
    if ($ultima -match '^[1-9]|e [1-9]') {
        Write-Host '       (os apagados sao convertidos de novo, com a versao nova, em ate 5 minutos)'
        $q = Read-Host '       Apagar esses .md? Os originais NAO sao tocados (no Drive vao para a Lixeira). Digite SIM'
        if ($q -eq 'SIM') { & $py (Join-Path $ferr 'conversor.py') --limpar --apagar | Select-Object -Last 1 | ForEach-Object { Write-Host "       $_" } }
    }
}

Write-Host ''
Write-Host '  4/6  Criando atalhos ...'
$sh = New-Object -ComObject WScript.Shell
$bat = Join-Path $ferr 'CONVERTER_AGORA.bat'
foreach ($lnk in @(
        @{ P = Join-Path ([Environment]::GetFolderPath('Desktop')) 'Converter extratos agora.lnk'; D = 'Converte agora os extratos novos da pasta EXTRATOS\01 - Entrada' },
        @{ P = Join-Path ([Environment]::GetFolderPath('SendTo')) 'Converter extrato (ROF).lnk'; D = 'Converte o arquivo escolhido em _extrato.md' })) {
    $s = $sh.CreateShortcut($lnk.P); $s.TargetPath = $bat; $s.WorkingDirectory = $ferr; $s.Description = $lnk.D; $s.Save()
}
$s = $sh.CreateShortcut((Join-Path ([Environment]::GetFolderPath('Desktop')) 'EXTRATOS - Entrada.lnk')); $s.TargetPath = $entrada; $s.Save()
Write-Host '       Area de trabalho: "Converter extratos agora" e "EXTRATOS - Entrada"'
Write-Host '       Botao direito no arquivo > Enviar para > "Converter extrato (ROF)"'

# 6) regra permanente para o Claude
Write-Host ''
Write-Host '  5/6  Gravando a regra para o Claude (CLAUDE.md) ...'
$marca = '<!-- ROF-CONVERSOR-EXTRATOS -->'
$regra = @"
$marca
## Extratos bancários (conversor ROF)
- Para analisar um extrato, leia o ``<nome>_extrato.md`` que fica ao lado do original (em ``$entrada`` ou nas pastas ``Extrato`` dos clientes no Google Drive: Arquivos RENATA Dominio, Arquivos ROF Dominio e Arquivos PROTECTION Dominio\25 - Cosmetici). **Nunca** leia o PDF ou o OFX original.
- Na pasta Extrato também há ``_extrato.md`` de comprovantes/relatórios/planilhas: começam com ``# Documento - `` (texto limpo, sem Confere); use-os para conferir lançamentos.
- Só abra a imagem da página (pasta indicada na linha ``Origem`` do .md) quando a linha estiver marcada ``[OCR pN]`` e o valor parecer duvidoso, ou quando a linha ``Confere`` disser ``NÃO``.
- Se o ``_extrato.md`` ainda não existir, rode o conversor primeiro: ``"$py" "$ferr\conversor.py" "<arquivo>"`` (sem Python: ``powershell -File "$ferr\converter_sem_python.ps1" "<arquivo>"``).
- Programas e explicação: ``$ferr\LEIA-ME.md``.
"@
[IO.File]::WriteAllText((Join-Path $raiz 'CLAUDE.md'), "# Pasta EXTRATOS`r`n`r`n$regra`r`n", $utf8)
$dirClaude = Join-Path $env:USERPROFILE '.claude'
New-Item -ItemType Directory -Force -Path $dirClaude | Out-Null
$global = Join-Path $dirClaude 'CLAUDE.md'
$atual = if (Test-Path -LiteralPath $global) { [IO.File]::ReadAllText($global) } else { '' }
if ($atual -match [regex]::Escape($marca)) {
    $atual = [regex]::Replace($atual, "(?s)$([regex]::Escape($marca)).*?(?=\r?\n<!-- |\z)", { param($m) $regra.TrimEnd() })
    [IO.File]::WriteAllText($global, $atual, $utf8)
} else {
    [IO.File]::WriteAllText($global, $atual.TrimEnd() + "`r`n`r`n" + $regra + "`r`n", $utf8)
}
Write-Host "       $raiz\CLAUDE.md e $global"

# 7) teste
Write-Host ''
Write-Host '  6/6  Teste com um extrato ESCANEADO de exemplo (dados ficticios) ...'
$tdir = Join-Path $env:TEMP 'ROF-teste-conversor'
Remove-Item -LiteralPath $tdir -Recurse -Force -ErrorAction SilentlyContinue
New-Item -ItemType Directory -Force -Path $tdir | Out-Null
Copy-Item -LiteralPath (Join-Path $origem 'teste-escaneado.pdf') -Destination $tdir
$tpdf = Join-Path $tdir 'teste-escaneado.pdf'
if ($py) { & $py (Join-Path $ferr 'conversor.py') --stats $tpdf } else { & powershell.exe -NoProfile -ExecutionPolicy Bypass -File (Join-Path $ferr 'converter_sem_python.ps1') $tpdf }
$md = Join-Path $tdir 'teste-escaneado_extrato.md'
if (Test-Path -LiteralPath $md) {
    Write-Host ''
    Get-Content -LiteralPath $md -Encoding UTF8 -TotalCount 12 | ForEach-Object { Write-Host "     $_" }
    Write-Host ''
    Write-Host '  Esperado: 12 lancamentos e "Confere: sim". Se aparecer NAO ou ERRO, tire um print e envie.'
} else {
    Write-Host '  ATENCAO: o teste nao gerou o .md. Tire um print desta tela e envie.'
}
Write-Host ''
Write-Host "  PRONTO! Salve os extratos em: $entrada"
Write-Host '  Em ate 5 minutos aparece ao lado o arquivo <nome>_extrato.md.'
