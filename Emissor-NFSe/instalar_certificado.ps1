# Instala o certificado A1 (.pfx) de uma empresa no Windows (repositorio Pessoal do usuario),
# com a chave NAO exportavel. A senha e digitada pela pessoa, nao fica gravada em lugar nenhum.
$ErrorActionPreference = 'Stop'
Add-Type -AssemblyName System.Windows.Forms

$dlg = New-Object System.Windows.Forms.OpenFileDialog
$dlg.Title  = 'Escolha o certificado A1 (.pfx) da empresa'
$dlg.Filter = 'Certificado A1 (*.pfx;*.p12)|*.pfx;*.p12'
$ini = 'G:\Meu Drive\Trabalho ROF\Certificados'
if (Test-Path $ini) { $dlg.InitialDirectory = $ini }
if ($dlg.ShowDialog() -ne 'OK') { Write-Host 'Nenhum arquivo escolhido.'; exit 1 }

$senha = Read-Host -AsSecureString 'Digite a senha do certificado (nao aparece na tela)'
$c = Import-PfxCertificate -FilePath $dlg.FileName -CertStoreLocation 'Cert:\CurrentUser\My' -Password $senha
$senha = $null

foreach ($x in $c) {
    if ($x.HasPrivateKey) {
        Write-Host ''
        Write-Host 'Certificado instalado:' -ForegroundColor Green
        Write-Host ('  Titular  : ' + $x.Subject.Split(',')[0])
        Write-Host ('  Vence em : ' + $x.NotAfter.ToString('dd/MM/yyyy'))
        Write-Host ('  Impressao digital (thumb): ' + $x.Thumbprint) -ForegroundColor Yellow
    }
}
Write-Host ''
Write-Host 'Guarde a impressao digital: e ela que o programa usa para emitir.'
