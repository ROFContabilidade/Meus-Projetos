@echo off
chcp 65001 >nul
echo Instalando o Emissor ROF de NFS-e...
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0instalar.ps1"
pause
