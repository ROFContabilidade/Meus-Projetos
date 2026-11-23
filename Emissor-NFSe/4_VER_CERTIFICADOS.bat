@echo off
chcp 65001 >nul
set /p PY=<"%~dp0python.txt"
cd /d "%~dp0programa"
echo Certificados instalados neste Windows (impressao digital ^| validade ^| titular):
%PY% ferramentas_nfse.py certificados
pause
