@echo off
rem Copia agora as pastas/arquivos que faltam.
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0sincronizar_pastas.ps1"
pause
