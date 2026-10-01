@echo off
chcp 65001 >nul
title Instalar - Sincronizar pastas das empresas
set "DESTINO=C:\ROF\Sincronizar-Pastas-Drive"

echo.
echo  1/3  Copiando os arquivos para %DESTINO% ...
if not exist "%DESTINO%" mkdir "%DESTINO%"
copy /Y "%~dp0sincronizar_pastas.ps1" "%DESTINO%\" >nul || goto erro
copy /Y "%~dp0agendar_tarefa.ps1"     "%DESTINO%\" >nul || goto erro
copy /Y "%~dp0EXECUTAR_AGORA.bat"     "%DESTINO%\" >nul
copy /Y "%~dp0TESTAR_SIMULACAO.bat"   "%DESTINO%\" >nul
copy /Y "%~dp0LEIA-ME.md"             "%DESTINO%\" >nul
powershell -NoProfile -ExecutionPolicy Bypass -Command "Get-ChildItem '%DESTINO%' | Unblock-File"

echo.
echo  2/3  Criando a tarefa mensal (todo dia 2 as 07:00) ...
powershell -NoProfile -ExecutionPolicy Bypass -File "%DESTINO%\agendar_tarefa.ps1" || goto erro

echo.
echo  3/3  SIMULACAO - mostra o que seria copiado (nada e copiado agora):
echo.
powershell -NoProfile -ExecutionPolicy Bypass -File "%DESTINO%\sincronizar_pastas.ps1" -Simular

echo.
echo  PRONTO! Instalado em %DESTINO%
echo  Para copiar agora o que falta, abra essa pasta e de dois cliques em EXECUTAR_AGORA.bat
echo.
pause
exit /b 0

:erro
echo.
echo  ERRO na instalacao. Tire um print desta tela e envie.
echo  Dica: o ZIP precisa ser EXTRAIDO antes (botao direito - Extrair tudo).
pause
exit /b 1
