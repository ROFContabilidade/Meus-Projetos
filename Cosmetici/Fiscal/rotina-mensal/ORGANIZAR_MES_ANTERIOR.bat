@echo off
rem Organiza a pasta fiscal da COSMETICI do MES ANTERIOR (cria subpastas, extrai ZIP, separa XML).
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0organizar_fiscal_cosmetici.ps1"
pause
