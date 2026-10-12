"""Cria a pasta e o regras.json de uma empresa nova a partir do modelo de indústria.

Uso:
  python3 nova_empresa.py --codigo 73 --nome "EMPRESA LTDA" --cnpj 00000000000100 --uf PR \
      --regime "Lucro Presumido" --atividade "fabrica X (NCM ...), revende Y"
Depois: conferir os campos "CONFERIR" do regras.json (acumuladores, contas, perfil_venda) com o
"Resumo por acumulador" do Domínio, o 0400 do SPED e o plano de contas.
"""
import argparse
import json
import os
import re
import unicodedata

AQUI = os.path.dirname(os.path.abspath(__file__))
MODELO = os.path.join(AQUI, '..', 'empresas', '_modelo-industria', 'regras.json')


def slug(nome):
    n = unicodedata.normalize('NFKD', nome).encode('ascii', 'ignore').decode().lower()
    n = re.sub(r'\b(ltda|me|epp|eireli|s/?a|industria|comercio|e|de|do|da|dos|das)\b', ' ', n)
    return '-'.join(re.findall(r'[a-z0-9]+', n)[:3]) or 'empresa'


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--codigo', type=int, required=True)
    p.add_argument('--nome', required=True)
    p.add_argument('--cnpj', required=True)
    p.add_argument('--uf', default='PR')
    p.add_argument('--regime', default='Lucro Presumido')
    p.add_argument('--atividade', default='')
    p.add_argument('--aliq-interna', type=float, default=19.5)
    a = p.parse_args()
    r = json.load(open(MODELO, encoding='utf-8'))
    r.pop('_modelo', None)
    r['empresa'].update(codigo_dominio=a.codigo, nome=a.nome, cnpj=re.sub(r'\D', '', a.cnpj), uf=a.uf,
                        regime=a.regime, aliq_interna_icms=a.aliq_interna)
    if a.atividade:
        r['empresa']['atividade'] = a.atividade
    pasta = os.path.join(AQUI, '..', 'empresas', f'{a.codigo}-{slug(a.nome)}')
    os.makedirs(pasta, exist_ok=True)
    destino = os.path.join(pasta, 'regras.json')
    if os.path.exists(destino):
        raise SystemExit(f'Já existe: {destino}')
    json.dump(r, open(destino, 'w', encoding='utf-8'), ensure_ascii=False, indent=2)
    pend = [k for k, v in r.items() if 'CONFERIR' in json.dumps(v, ensure_ascii=False)]
    print(f'Criado {os.path.relpath(destino)}\nConferir antes da 1ª rodada: {", ".join(pend)}')


if __name__ == '__main__':
    main()
