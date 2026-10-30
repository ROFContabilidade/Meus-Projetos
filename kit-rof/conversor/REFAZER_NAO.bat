@echo off
chcp 65001 >nul
title ROF - Refazer extratos com Confere NAO
rem Lista os _extrato.md com Confere NAO (e os de documentos que nao sao extrato), pergunta,
rem apaga (vao para a Lixeira do Drive) e converte de novo com a versao atual do conversor.py.
set "F=%~dp0"
set "PY="
if exist "%F%python.txt" set /p PY=<"%F%python.txt"
if not defined PY set "PY=python"
"%PY%" "%F%conversor.py" --limpar
echo.
set "R="
set /p R=Apagar esses .md e converter de novo? Digite S e Enter (ou so Enter para cancelar): 
if /i not "%R%"=="S" goto fim
"%PY%" "%F%conversor.py" --limpar --apagar
"%PY%" "%F%conversor.py" --stats
:fim
echo.
pause
