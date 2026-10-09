@echo off
rem Organiza a pasta fiscal da COSMETICI de um mes escolhido.
set /p MES=Digite o mes (MM_AAAA, ex.: 09_2026): 
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0organizar_fiscal_cosmetici.ps1" -Mes %MES%
pause
