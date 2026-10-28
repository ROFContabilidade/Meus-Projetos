@echo off
chcp 65001 >nul
title ROF - Converter extratos
rem Sem arquivos: converte todos os extratos novos da pasta de entrada.
rem Com arquivos (arrastar e soltar, ou Enviar para): converte esses agora; se o .md ja existir grava "(2)".
set "F=%~dp0"
set "PY="
if exist "%F%python.txt" set /p PY=<"%F%python.txt"
if defined PY if not exist "%PY%" set "PY="
if defined PY goto python
powershell -NoProfile -ExecutionPolicy Bypass -File "%F%converter_sem_python.ps1" %*
goto fim
:python
"%PY%" "%F%conversor.py" --stats %*
:fim
echo.
pause
