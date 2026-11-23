@echo off
chcp 65001 >nul
set /p PY=<"%~dp0python.txt"
cd /d "%~dp0programa"
%PY% emissor_rof.py
pause
