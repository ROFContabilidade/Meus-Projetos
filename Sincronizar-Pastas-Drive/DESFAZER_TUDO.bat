@echo off
chcp 65001 >nul
rem Apaga TODAS as pastas copiadas na ultima execucao (volta como estava antes).
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0desfazer_copia.ps1" -Tudo
pause
