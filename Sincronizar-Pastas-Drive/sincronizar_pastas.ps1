<#
  Sincronizar pastas mensais das empresas
  Origem : G:\Meu Drive\Trabalho ROF\Contabilidade\Arquivos RENATA Dominio\<NUMERO - Nome>\...\MM_AAAA
  Destino: I:\Meu Drive\EMPRESAS ATIVAS\<NUMERO_Nome>\FISCAL\AAAA\MM_AAAA

  Para cada empresa da origem, procura no destino a pasta com o MESMO NUMERO.
  Procura (em qualquer subpasta da empresa na origem) as pastas mensais no
  formato MM_AAAA (ex.: 08_2026) e copia para FISCAL\AAAA somente os meses
  POSTERIORES ao ultimo mes que ja existe no destino e anteriores ao mes atual.
  Meses que ja existem no destino nao sao alterados.
  Nunca apaga nem sobrescreve nada.

  Uso:
    .\sincronizar_pastas.ps1            -> copia os meses que faltam
    .\sincronizar_pastas.ps1 -Simular   -> so mostra o que seria copiado
#>
param(
    [string]$Origem  = 'G:\Meu Drive\Trabalho ROF\Contabilidade\Arquivos RENATA Dominio',
    [string]$Destino = 'I:\Meu Drive\EMPRESAS ATIVAS',
    # Subpasta dos meses na empresa do destino: usa a primeira que existir (ex.: FISCAL-CONTABIL, senao FISCAL)
    [string[]]$SubpastasDestino = @('FISCAL-CONTABIL', 'FISCAL'),
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

# Numero da empresa = digitos no inicio do nome, seguidos de " ", "-" ou "_"
# ("67 - X" ou "67_X" -> 67). "01.2_Backup" NAO vira 1.
function NumeroEmpresa([string]$nome) {
    if ($nome -match '^\s*(\d+)\s*[-_ ]') { return [int]$Matches[1] }
    return $null
}

# 08_2026 -> 202608
function ChaveMes([string]$nome) { return [int]$nome.Substring(3, 4) * 100 + [int]$nome.Substring(0, 2) }

Escrever "==== Inicio $(if ($Simular) {'(SIMULACAO - nada sera copiado)'}) ===="

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

# Indexa as empresas do destino pelo numero (pode haver mais de uma: "01_Paes e Bastos" e "1_RBA")
$destinos = @{}
foreach ($d in Get-ChildItem -LiteralPath $Destino -Directory) {
    $n = NumeroEmpresa $d.Name
    if ($null -eq $n) { continue }
    if (-not $destinos.ContainsKey($n)) { $destinos[$n] = @() }
    $destinos[$n] += $d
}
$mesAtual = (Get-Date).Year * 100 + (Get-Date).Month

# Quando ha mais de uma pasta com o mesmo numero no destino:
#  1o) usa a que tem o numero escrito igual ("01" com "01", "1" com "1")
#  2o) senao, a que tem mais palavras do nome em comum ("Paes", "Bastos"...)
#  senao, nao escolhe (empresa ignorada)
function EscolherDestino($emp, $lista) {
    if ($lista.Count -eq 1) { return $lista[0].FullName }
    $null = $emp.Name -match '^\s*(\d+)'; $txt = $Matches[1]
    $iguais = @($lista | Where-Object { $_.Name -match "^\s*$txt\s*[-_ ]" })
    if ($iguais.Count -eq 1) { return $iguais[0].FullName }
    $palavras = @(($emp.Name -replace '^\s*\d+\s*[-_ ]\s*', '').ToLower() -split '[^\p{L}\p{N}]+' | Where-Object { $_.Length -ge 3 })
    $notas = foreach ($c in $lista) {
        $nomeC = $c.Name.ToLower()
        [pscustomobject]@{ Pasta = $c.FullName; Nota = @($palavras | Where-Object { $nomeC.Contains($_) }).Count }
    }
    $melhor = @($notas | Sort-Object Nota -Descending)
    if ($melhor[0].Nota -gt 0 -and ($melhor.Count -eq 1 -or $melhor[0].Nota -gt $melhor[1].Nota)) { return $melhor[0].Pasta }
    return $null
}

$totalMeses = 0; $semDestino = @(); $erros = 0
foreach ($emp in Get-ChildItem -LiteralPath $Origem -Directory | Sort-Object Name) {
    $n = NumeroEmpresa $emp.Name
    if ($null -eq $n) { Escrever "Ignorada (nome sem numero): $($emp.Name)"; continue }
    if (-not $destinos.ContainsKey($n)) { $semDestino += $emp.Name; continue }

    $alvoEmpresa = EscolherDestino $emp $destinos[$n]
    if (-not $alvoEmpresa) {
        Escrever "  ATENCAO [$($emp.Name)] mais de uma pasta com o numero $n em '$Destino' e nao deu para saber qual e a certa - empresa ignorada"
        continue
    }

    # Ultimo mes que ja existe no destino (FISCAL\AAAA\MM_AAAA). So copia meses DEPOIS dele.
    # Usa a primeira subpasta (FISCAL-CONTABIL, depois FISCAL) que ja tenha meses MM_AAAA
    $SubpastaDestino = $null; $existentes = @()
    foreach ($sub in $SubpastasDestino) {
        $chaves = @(Get-ChildItem -LiteralPath (Join-Path $alvoEmpresa $sub) -Directory -ErrorAction SilentlyContinue |
            Get-ChildItem -Directory -ErrorAction SilentlyContinue |
            Where-Object { $_.Name -match '^(0[1-9]|1[0-2])_(\d{4})$' } | ForEach-Object { ChaveMes $_.Name })
        if ($chaves.Count -gt 0) { $SubpastaDestino = $sub; $existentes = $chaves; break }
    }
    if (-not $SubpastaDestino) {
        Escrever "  ATENCAO [$($emp.Name)] nenhum mes em '$alvoEmpresa\($($SubpastasDestino -join ' ou '))' - empresa ignorada (copie o primeiro mes manualmente)"
        continue
    }
    $ultimo = ($existentes | Measure-Object -Maximum).Maximum
    $meses = Get-ChildItem -LiteralPath $emp.FullName -Directory -Recurse -ErrorAction SilentlyContinue |
        Where-Object { $_.Name -match '^(0[1-9]|1[0-2])_(\d{4})$' } |
        Sort-Object Name, FullName

    $vistos = @{}
    foreach ($m in $meses) {
        $ano = $m.Name.Substring(3, 4)
        $alvoMes = Join-Path (Join-Path (Join-Path $alvoEmpresa $SubpastaDestino) $ano) $m.Name
        if ($vistos.ContainsKey($alvoMes)) {
            Escrever "  ATENCAO [$($emp.Name)] mes $($m.Name) aparece em mais de um lugar na origem; usado: $($vistos[$alvoMes]) | ignorado: $($m.FullName)"
            continue
        }
        $vistos[$alvoMes] = $m.FullName
        $chave = ChaveMes $m.Name
        if ($chave -le $ultimo -or $chave -ge $mesAtual) { continue }   # mes antigo ou mes em andamento
        if (Test-Path -LiteralPath $alvoMes) { continue }                # mes ja existe no destino

        $arquivos = @(Get-ChildItem -LiteralPath $m.FullName -File -Recurse -ErrorAction SilentlyContinue)
        $totalMeses++
        Escrever "[$($emp.Name)] $($m.Name): $($arquivos.Count) arquivo(s) $(if ($Simular) {'seriam copiados'} else {'copiando'})"
        Escrever "    de:   $($m.FullName)"
        Escrever "    para: $alvoMes"
        if ($Simular) { continue }

        # /E subpastas | /XC /XN /XO nunca sobrescreve | /XX nunca apaga
        & robocopy $m.FullName $alvoMes /E /XC /XN /XO /XX /R:2 /W:10 /NP /NFL /NDL /NJH /NJS | Out-Null
        if ($LASTEXITCODE -ge 8) {
            $erros++
            Escrever "    ERRO robocopy (codigo $LASTEXITCODE) ao copiar $($m.Name)"
        } else {
            Escrever "    OK"
        }
    }
}

if ($semDestino.Count -gt 0) {
    Escrever "ATENCAO: empresas sem pasta com o mesmo numero em '$Destino' (nada foi copiado):"
    $semDestino | ForEach-Object { Escrever "    $_" }
}
Escrever "==== Fim: $totalMeses pasta(s) de mes $(if ($Simular) {'a copiar'} else {'copiada(s)'}), $erros erro(s). Log: $log ===="
