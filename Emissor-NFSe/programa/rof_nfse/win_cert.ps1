# Ajudante do Emissor ROF: usa o certificado A1 instalado no Windows (repositorio "Pessoal"),
# sem exportar a chave e sem senha. Tres operacoes:
#   info  -> devolve o certificado publico (base64) e a validade
#   sign  -> assina bytes (RSA PKCS#1 v1.5, SHA1 ou SHA256) com a chave do certificado
#   http  -> faz um pedido HTTPS com autenticacao por certificado (mTLS)
# Saida sempre em JSON numa linha, no arquivo indicado em -Saida.
param(
    [Parameter(Mandatory = $true)][ValidateSet('info', 'sign', 'http')][string]$Op,
    [Parameter(Mandatory = $true)][string]$Thumb,
    [string]$Alg = 'sha1',
    [string]$Entrada = '',
    [string]$Saida = '',
    [string]$Metodo = 'GET',
    [string]$Url = '',
    [string]$Aceita = 'application/json',
    [int]$Limite = 60
)
$ErrorActionPreference = 'Stop'

function Escrever($obj) {
    $json = $obj | ConvertTo-Json -Compress -Depth 5
    [System.IO.File]::WriteAllText($Saida, $json, (New-Object System.Text.UTF8Encoding($false)))
}

try {
    $cert = Get-Item ("Cert:\CurrentUser\My\" + $Thumb)
    if ($Op -eq 'info') {
        Escrever @{ ok = $true; der = [Convert]::ToBase64String($cert.RawData); tem_chave = $cert.HasPrivateKey }
        exit 0
    }
    if ($Op -eq 'sign') {
        $dados = [System.IO.File]::ReadAllBytes($Entrada)
        $nomeHash = if ($Alg -eq 'sha256') { 'SHA256' } else { 'SHA1' }
        $assin = $null
        # 1) API moderna: serve para chave no provedor novo (CNG / Key Storage Provider) e no antigo (CSP)
        try {
            $rsaNova = [System.Security.Cryptography.X509Certificates.RSACertificateExtensions]::GetRSAPrivateKey($cert)
            if ($rsaNova) {
                $assin = $rsaNova.SignData($dados, [System.Security.Cryptography.HashAlgorithmName]::$nomeHash,
                    [System.Security.Cryptography.RSASignaturePadding]::Pkcs1)
            }
        } catch { $assin = $null }
        if ($assin) {
            Escrever @{ ok = $true; assinatura = [Convert]::ToBase64String($assin) }
            exit 0
        }
        # 2) caminho antigo (CSP), mantido por segurança
        $rsa = $cert.PrivateKey
        try {
            $assin = $rsa.SignData($dados, $nomeHash)
        } catch {
            # chave em provedor antigo (PROV_RSA_FULL) nao assina SHA256: reabre no provedor AES, mesmo conteiner
            $info = $rsa.CspKeyContainerInfo
            $p = New-Object System.Security.Cryptography.CspParameters(24, 'Microsoft Enhanced RSA and AES Cryptographic Provider', $info.KeyContainerName)
            if ($info.MachineKeyStore) { $p.Flags = [System.Security.Cryptography.CspProviderFlags]::UseMachineKeyStore }
            $p.KeyNumber = [int]$info.KeyNumber
            $rsa2 = New-Object System.Security.Cryptography.RSACryptoServiceProvider($p)
            $assin = $rsa2.SignData($dados, $nomeHash)
        }
        Escrever @{ ok = $true; assinatura = [Convert]::ToBase64String($assin) }
        exit 0
    }
    if ($Op -eq 'http') {
        [Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12
        $req = [System.Net.HttpWebRequest]::Create($Url)
        $req.Method = $Metodo
        $req.Accept = $Aceita
        $req.UserAgent = 'EmissorROF'
        $req.Timeout = $Limite * 1000
        $req.ReadWriteTimeout = $Limite * 1000
        [void]$req.ClientCertificates.Add($cert)
        $enviado = $false
        if ($Entrada -and (Test-Path $Entrada)) {
            $corpo = [System.IO.File]::ReadAllBytes($Entrada)
            $req.ContentType = 'application/json'
            $req.ContentLength = $corpo.Length
            $s = $req.GetRequestStream()
            $s.Write($corpo, 0, $corpo.Length)
            $s.Close()
        }
        $enviado = $true
        $resp = $null
        try {
            $resp = $req.GetResponse()
        } catch [System.Net.WebException] {
            if ($_.Exception.Response) { $resp = $_.Exception.Response }
            else {
                Escrever @{ ok = $false; erro = $_.Exception.Message; status_web = [string]$_.Exception.Status; enviado = $enviado }
                exit 0
            }
        }
        $ms = New-Object System.IO.MemoryStream
        $rs = $resp.GetResponseStream()
        if ($rs) { $rs.CopyTo($ms); $rs.Close() }
        $cab = @{}
        foreach ($k in $resp.Headers.AllKeys) { $cab[$k] = $resp.Headers[$k] }
        Escrever @{ ok = $true; status = [int]$resp.StatusCode; corpo = [Convert]::ToBase64String($ms.ToArray()); cabecalhos = $cab }
        $resp.Close()
        exit 0
    }
} catch {
    Escrever @{ ok = $false; erro = $_.Exception.Message; enviado = $false }
    exit 0
}
