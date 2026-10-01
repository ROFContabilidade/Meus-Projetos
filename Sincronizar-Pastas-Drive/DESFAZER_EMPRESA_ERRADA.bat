@echo off
chcp 65001 >nul
rem Apaga somente as pastas copiadas para a empresa errada na ultima execucao.
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0desfazer_copia.ps1"
pause
