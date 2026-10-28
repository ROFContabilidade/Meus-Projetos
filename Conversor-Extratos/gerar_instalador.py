"""Monta INSTALAR_CONVERSOR.bat: um arquivo unico (nao precisa extrair ZIP) com os programas embutidos em base64.
Rodar de novo sempre que mudar qualquer arquivo da lista. Confere que todos voltam identicos."""
import base64
import re
from pathlib import Path

AQUI = Path(__file__).parent
ARQS = ['conversor.py', 'ocr_windows.ps1', 'converter_sem_python.ps1', 'agendar_tarefa.ps1', 'instalar.ps1',
        'CONVERTER_AGORA.bat', 'LEIA-ME.md', 'teste-escaneado.pdf']

CAB = r"""@echo off
chcp 65001 >nul
title ROF - Instalar o conversor de extratos
rem Arquivo unico: nao precisa extrair nada. Instala em <pasta EXTRATOS>\_ferramentas,
rem instala o Python (se faltar), cria a tarefa de 5 em 5 minutos e testa com um extrato de exemplo.
set "TMPI=%TEMP%\ROF-Conversor-instalar"
set "ESTE=%~f0"
echo.
echo  Preparando a instalacao ...
powershell -NoProfile -ExecutionPolicy Bypass -Command "$d=$env:TMPI; Remove-Item -LiteralPath $d -Recurse -Force -ErrorAction SilentlyContinue; New-Item -ItemType Directory -Force -Path $d | Out-Null; $nome=$null; $b=@{}; foreach($l in Get-Content -LiteralPath $env:ESTE){ if($l -match '^::ARQ (.+)$'){ $nome=$Matches[1]; $b[$nome]=New-Object Text.StringBuilder } elseif($nome -and $l -match '^::B (.+)$'){ [void]$b[$nome].Append($Matches[1]) } }; foreach($k in $b.Keys){ [IO.File]::WriteAllBytes((Join-Path $d $k),[Convert]::FromBase64String($b[$k].ToString())) }; Get-ChildItem -LiteralPath $d | Unblock-File; if($b.Count -lt %N%){ exit 1 }" || goto erro
powershell -NoProfile -ExecutionPolicy Bypass -File "%TMPI%\instalar.ps1" || goto erro
echo.
pause
exit /b 0

:erro
echo.
echo  ERRO na instalacao. Tire um print desta tela e envie.
pause
exit /b 1

"""


def main():
    partes = [CAB.replace('%N%', str(len(ARQS)))]
    for nome in ARQS:
        dados = base64.b64encode((AQUI / nome).read_bytes()).decode()
        partes.append(f'::ARQ {nome}\n' + ''.join(f'::B {dados[i:i + 76]}\n' for i in range(0, len(dados), 76)))
    texto = ''.join(partes).replace('\n', '\r\n')
    destino = AQUI / 'INSTALAR_CONVERSOR.bat'
    destino.write_bytes(texto.encode('ascii'))
    # conferencia: extrai como o .bat faz e compara
    b, nome = {}, None
    for l in destino.read_text(encoding='ascii').splitlines():
        if m := re.match(r'^::ARQ (.+)$', l):
            nome = m[1]
            b[nome] = []
        elif nome and (m := re.match(r'^::B (.+)$', l)):
            b[nome].append(m[1])
    for n in ARQS:
        assert base64.b64decode(''.join(b[n])) == (AQUI / n).read_bytes(), n
    print(f'{destino.name}: {len(ARQS)} arquivos conferidos, {destino.stat().st_size // 1024} KB')


if __name__ == '__main__':
    main()
