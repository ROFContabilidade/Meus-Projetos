#!/bin/bash
# Uso: preparar_xlsx.sh EXTRATO.xlsx RAZAO.xlsx PASTA_DE_TRABALHO
# Os .xlsx do Korp têm cores inválidas em xl/styles.xml (openpyxl falha). Gera a.xlsx (extrato) e b.xlsx (razão) corrigidos.
set -e
W="$3"; mkdir -p "$W"
for p in "a:$1" "b:$2"; do k=${p%%:*}; f=${p#*:}; mkdir -p "$W/$k"; unzip -oq "$f" -d "$W/$k"; sed -i 's/rgb="[^"]*"/rgb="FF000000"/g' "$W/$k/xl/styles.xml"; (cd "$W/$k" && zip -qr ../$k.xlsx .); done
echo "OK: $W/a.xlsx (extrato) e $W/b.xlsx (razão)"
