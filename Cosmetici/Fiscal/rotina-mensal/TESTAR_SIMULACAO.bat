@echo off
rem So mostra o que seria feito no mes anterior - nao move nada.
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0organizar_fiscal_cosmetici.ps1" -Simular
pause
