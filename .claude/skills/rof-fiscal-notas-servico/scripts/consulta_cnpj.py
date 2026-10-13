"""Consulta CNPJ (BrasilAPI; reserva: publica.cnpj.ws) e sugere o anexo do Simples para cada CNAE.

python consulta_cnpj.py 29.650.531/0001-01 [--json saida.json]
"""
import json, re, sys, urllib.request, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from tabelas import anexo_cnae, fmt_cnae


def _get(url):
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 ROF'})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read().decode('utf-8'))


def consulta(cnpj):
    c = re.sub(r'\D', '', cnpj)
    try:
        d = _get(f'https://brasilapi.com.br/api/cnpj/v1/{c}')
        cnaes = [(d['cnae_fiscal'], d.get('cnae_fiscal_descricao', ''), 'Principal')]
        cnaes += [(s['codigo'], s['descricao'], 'Secundário') for s in d.get('cnaes_secundarios') or [] if s.get('codigo')]
        return {'cnpj': c, 'razao_social': d.get('razao_social'), 'nome_fantasia': d.get('nome_fantasia'),
                'situacao': d.get('descricao_situacao_cadastral'), 'municipio': f"{d.get('municipio')}/{d.get('uf')}",
                'natureza_juridica': d.get('natureza_juridica'), 'porte': d.get('porte'),
                'simples': d.get('opcao_pelo_simples'), 'data_opcao_simples': d.get('data_opcao_pelo_simples'),
                'data_exclusao_simples': d.get('data_exclusao_do_simples'),
                'mei': d.get('opcao_pelo_mei'), 'abertura': d.get('data_inicio_atividade'),
                'fonte': 'BrasilAPI (base da Receita Federal)', **_cnaes(cnaes)}
    except Exception as e:  # reserva
        d = _get(f'https://publica.cnpj.ws/cnpj/{c}')
        est = d['estabelecimento']
        cnaes = [(est['atividade_principal']['id'], est['atividade_principal']['descricao'], 'Principal')]
        cnaes += [(s['id'], s['descricao'], 'Secundário') for s in est.get('atividades_secundarias') or []]
        sn = d.get('simples') or {}
        return {'cnpj': c, 'razao_social': d.get('razao_social'), 'nome_fantasia': est.get('nome_fantasia'),
                'situacao': est.get('situacao_cadastral'), 'municipio': f"{est['cidade']['nome']}/{est['estado']['sigla']}",
                'natureza_juridica': d['natureza_juridica']['descricao'], 'porte': (d.get('porte') or {}).get('descricao'),
                'simples': sn.get('simples') == 'Sim', 'data_opcao_simples': sn.get('data_opcao_simples'),
                'data_exclusao_simples': sn.get('data_exclusao_simples'), 'mei': sn.get('mei') == 'Sim',
                'abertura': est.get('data_inicio_atividade'), 'fonte': f'publica.cnpj.ws (BrasilAPI falhou: {e})', **_cnaes(cnaes)}


def _cnaes(lst):
    out = []
    for cod, desc, tipo in lst:
        an, obs = anexo_cnae(cod)
        out.append({'cnae': fmt_cnae(cod), 'descricao': desc, 'tipo': tipo, 'anexo_sugerido': an, 'obs_anexo': obs})
    return {'cnaes': out}


if __name__ == '__main__':
    r = consulta(sys.argv[1])
    if '--json' in sys.argv:
        json.dump(r, open(sys.argv[sys.argv.index('--json') + 1], 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print(f"{r['razao_social']} ({r['nome_fantasia'] or '-'}) - CNPJ {r['cnpj']} - {r['situacao']} - {r['municipio']}")
    print(f"Simples: {r['simples']} (opção {r['data_opcao_simples']}, exclusão {r['data_exclusao_simples']}) | MEI: {r['mei']} | {r['natureza_juridica']}")
    for c in r['cnaes']:
        print(f"  {c['tipo']:10} {c['cnae']}  {c['descricao'][:70]:70}  Anexo {c['anexo_sugerido']} - {c['obs_anexo']}")
