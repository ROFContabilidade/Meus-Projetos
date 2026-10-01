@echo off
rem Mostra o que seria copiado, sem copiar nada.
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0sincronizar_pastas.ps1" -Simular
pause
