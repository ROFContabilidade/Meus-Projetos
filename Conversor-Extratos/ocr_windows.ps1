<#
  OCR do proprio Windows (sem internet): renderiza paginas de um PDF em imagem (Windows.Data.Pdf)
  e le o texto em portugues (Windows.Media.Ocr).

  Para cada pagina N grava na pasta -Saida:
    pN.png  imagem da pagina (para conferir valores e datas)
    pN.txt  texto lido, uma linha por linha do extrato
    pN.tsv  mesmo texto com a posicao de cada palavra (usado pelo conversor.py para achar as colunas)

  Uso: powershell -File ocr_windows.ps1 -Pdf "C:\...\extrato.pdf" -Saida "C:\...\pasta" [-Paginas "1,3"]
       sem -Paginas = todas as paginas.  -Contar = so mostra o numero de paginas.
  Codigos de saida: 0 ok | 2 PDF nao abriu (senha?) | 3 sem OCR em portugues instalado
#>
param(
    [Parameter(Mandatory = $true)][string]$Pdf,
    [string]$Saida = '',
    [string]$Paginas = '',
    [double]$Escala = 2.5,
    [switch]$Contar
)
$ErrorActionPreference = 'Stop'
Add-Type -AssemblyName System.Runtime.WindowsRuntime
$null = [Windows.Storage.StorageFile, Windows.Storage, ContentType = WindowsRuntime]
$null = [Windows.Storage.Streams.InMemoryRandomAccessStream, Windows.Storage.Streams, ContentType = WindowsRuntime]
$null = [Windows.Data.Pdf.PdfDocument, Windows.Data.Pdf, ContentType = WindowsRuntime]
$null = [Windows.Data.Pdf.PdfPageRenderOptions, Windows.Data.Pdf, ContentType = WindowsRuntime]
$null = [Windows.Graphics.Imaging.BitmapDecoder, Windows.Foundation, ContentType = WindowsRuntime]
$null = [Windows.Graphics.Imaging.SoftwareBitmap, Windows.Foundation, ContentType = WindowsRuntime]
$null = [Windows.Media.Ocr.OcrEngine, Windows.Foundation, ContentType = WindowsRuntime]
$null = [Windows.Globalization.Language, Windows.Globalization, ContentType = WindowsRuntime]

$metodos = [System.WindowsRuntimeSystemExtensions].GetMethods()
$asTaskOp = $metodos | Where-Object { $_.Name -eq 'AsTask' -and $_.GetParameters().Count -eq 1 -and
    $_.GetParameters()[0].ParameterType.Name -eq 'IAsyncOperation`1' } | Select-Object -First 1
$asTaskAcao = $metodos | Where-Object { $_.Name -eq 'AsTask' -and $_.GetParameters().Count -eq 1 -and
    $_.GetParameters()[0].ParameterType.Name -eq 'IAsyncAction' } | Select-Object -First 1
function Esperar($op, [Type]$tipo) {
    $t = $asTaskOp.MakeGenericMethod($tipo).Invoke($null, @($op)); $t.Wait(-1) | Out-Null; $t.Result
}
function EsperarAcao($acao) { $t = $asTaskAcao.Invoke($null, @($acao)); $t.Wait(-1) | Out-Null }

$Pdf = (Resolve-Path -LiteralPath $Pdf).ProviderPath
try {
    $arq = Esperar ([Windows.Storage.StorageFile]::GetFileFromPathAsync($Pdf)) ([Windows.Storage.StorageFile])
    $doc = Esperar ([Windows.Data.Pdf.PdfDocument]::LoadFromFileAsync($arq)) ([Windows.Data.Pdf.PdfDocument])
} catch {
    [Console]::Error.WriteLine("PDF nao abriu (protegido por senha ou danificado): $($_.Exception.Message)")
    exit 2
}
$total = [int]$doc.PageCount
if ($Contar) { Write-Output $total; exit 0 }
if (-not $Saida) { throw 'Informe -Saida' }
New-Item -ItemType Directory -Force -Path $Saida | Out-Null

$motor = $null
foreach ($tag in 'pt-BR', 'pt-PT', 'pt') {
    try {
        $lang = New-Object Windows.Globalization.Language $tag
        if ([Windows.Media.Ocr.OcrEngine]::IsLanguageSupported($lang)) { $motor = [Windows.Media.Ocr.OcrEngine]::TryCreateFromLanguage($lang); break }
    } catch { }
}
if (-not $motor) {
    [Console]::Error.WriteLine('OCR em portugues nao instalado: Configuracoes > Hora e idioma > Idioma > Portugues (Brasil) > Opcoes > Reconhecimento optico de caracteres')
    exit 3
}

$lista = if ($Paginas) { $Paginas -split ',' | ForEach-Object { [int]$_ } } else { 1..$total }
$utf8 = New-Object System.Text.UTF8Encoding $false
$maxDim = [double][Windows.Media.Ocr.OcrEngine]::MaxImageDimension
$cult = [Globalization.CultureInfo]::InvariantCulture

foreach ($p in $lista) {
    if ($p -lt 1 -or $p -gt $total) { continue }
    $pg = $doc.GetPage([uint32]($p - 1))
    $w = $pg.Size.Width * $Escala; $h = $pg.Size.Height * $Escala
    $f = [Math]::Min(1.0, [Math]::Min($maxDim / $w, $maxDim / $h))
    $opt = New-Object Windows.Data.Pdf.PdfPageRenderOptions
    $opt.DestinationWidth = [uint32]($w * $f); $opt.DestinationHeight = [uint32]($h * $f)
    $mem = New-Object Windows.Storage.Streams.InMemoryRandomAccessStream
    EsperarAcao ($pg.RenderToStreamAsync($mem, $opt))
    $pg.Dispose()

    # imagem da pagina (PNG) para conferencia
    $png = Join-Path $Saida "p$p.png"
    $ent = [System.IO.WindowsRuntimeStreamExtensions]::AsStreamForRead($mem.GetInputStreamAt(0))
    $fs = [IO.File]::Create($png); $ent.CopyTo($fs); $fs.Close(); $ent.Dispose()

    [void]$mem.Seek(0)
    $dec = Esperar ([Windows.Graphics.Imaging.BitmapDecoder]::CreateAsync($mem)) ([Windows.Graphics.Imaging.BitmapDecoder])
    $bmp = Esperar ($dec.GetSoftwareBitmapAsync()) ([Windows.Graphics.Imaging.SoftwareBitmap])
    $res = Esperar ($motor.RecognizeAsync($bmp)) ([Windows.Media.Ocr.OcrResult])
    $larg = [double]$bmp.PixelWidth

    # junta as palavras pela altura na pagina (as colunas do extrato ficam na mesma linha)
    $pal = foreach ($l in $res.Lines) { foreach ($wd in $l.Words) {
            $r = $wd.BoundingRect
            [pscustomobject]@{ T = $wd.Text; X0 = $r.X; X1 = $r.X + $r.Width; C = $r.Y + $r.Height / 2; H = [Math]::Max($r.Height, 1) } } }
    $linhas = New-Object System.Collections.ArrayList
    foreach ($wd in ($pal | Sort-Object C, X0)) {
        $u = if ($linhas.Count) { $linhas[$linhas.Count - 1] } else { $null }
        if ($u -and [Math]::Abs($wd.C - $u.C) -le 0.5 * [Math]::Min($wd.H, $u.H)) {
            [void]$u.W.Add($wd); $u.C = ($u.C * ($u.W.Count - 1) + $wd.C) / $u.W.Count
        } else {
            $n = [pscustomobject]@{ C = $wd.C; H = $wd.H; W = (New-Object System.Collections.ArrayList) }
            [void]$n.W.Add($wd); [void]$linhas.Add($n)
        }
    }
    $txt = New-Object System.Collections.Generic.List[string]
    $tsv = New-Object System.Collections.Generic.List[string]
    foreach ($ln in $linhas) {
        $ws = $ln.W | Sort-Object X0
        $txt.Add((($ws | ForEach-Object { $_.T }) -join ' '))
        $tsv.Add((($ws | ForEach-Object { '{0} {1} {2}' -f ($_.X0 / $larg).ToString('0.####', $cult), ($_.X1 / $larg).ToString('0.####', $cult), $_.T }) -join "`t"))
    }
    [IO.File]::WriteAllLines((Join-Path $Saida "p$p.txt"), [string[]]$txt, $utf8)
    [IO.File]::WriteAllLines((Join-Path $Saida "p$p.tsv"), [string[]]$tsv, $utf8)
    $mem.Dispose()
    Write-Output "p$p $($txt.Count) linhas"
}
exit 0
