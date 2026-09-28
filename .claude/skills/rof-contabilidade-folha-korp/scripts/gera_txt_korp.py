"""Gera o TXT corrigido para a Korp a partir do TXT exportado do Domínio.

Uso: python gera_txt_korp.py Folha.txt config.json saida.txt

config.json:
{
  "empresa": "0000145",                 # código Domínio (140 Matriz, 145 Filial) - filtra os lançamentos
  "cnpj": "03623045000291",             # CNPJ do cabeçalho (registro 01)
  "cc_blocos": [[700, 708, "CC345"]],   # faixas de seq (registro 03 original) -> CC Korp  (Filial: sem 05 no Domínio)
  "cc_map": {"0000001": "CC337"},       # OU: troca de CC numérico existente (Matriz: 05 já vem do Domínio)
  "cc_seq": {"2": "CC644"},             # CC para lançamento que o Domínio exportou sem nenhum 05 (seq original)
  "complemento": ["2530","2531"],       # opcional: gera só os lançamentos com essas contas e só o lado delas (ver abaixo)
  "corrigir": {"752": [null, 2521]},    # seq -> [nova conta débito|null, nova conta crédito|null]
  "excluir": [734, 736],                # seq a remover
  "incluir": [{"apos": 844, "modelo": 830, "d": 3152, "c": 2524, "v": 483.87, "hist": "DIAS FERIAS", "cc": "CC345"}]
}
Mantém cp1252 + CRLF e o tamanho de cada registro; renumera a sequência.

REGRA KORP (confirmada em 09/2026): a Korp só grava o lado do lançamento que tem registro 05.
Por isso TODO lado de TODO lançamento recebe 05 com centro de custo (inclusive 2530, 2531, 2533, 3137);
o lado sem CC no Domínio herda o CC do outro lado.
"complemento": para um TXT já importado sem o 05 de alguns lados, gera só os lançamentos que têm essas
contas, com 05 apenas no lado dessas contas -> a Korp grava só o lado que faltou, sem duplicar o outro.
"""
import json, sys
from txt_dominio import parse

def A(n): return '%07d' % int(n)

def main(src, cfg_path, dst):
    cfg = json.load(open(cfg_path, encoding='utf-8'))
    L, ents = parse(src)
    hdr = L[0]; trailer = [l for l in L if l[:2] == '99'][0]
    emp = cfg['empresa']; comp = {A(a) for a in cfg.get('complemento', [])}
    E = [e for e in ents if e['e'] == emp and e['seq'] not in set(cfg.get('excluir', []))]
    def cc_bloco(s):
        for a, b, cc in cfg.get('cc_blocos', []):
            if a <= s <= b: return cc
        return None
    for e in E:
        fx = cfg.get('corrigir', {}).get(str(e['seq']))
        if fx:
            if fx[0]: e['d'] = A(fx[0])
            if fx[1]: e['c'] = A(fx[1])
        e['ccK'] = cc_bloco(e['seq'])
    for n in cfg.get('incluir', []):
        base = next(x for x in ents if x['seq'] == n['modelo'])
        l03 = base['l03'][:9] + A(n['d']) + A(n['c']) + '%015d' % round(n['v'] * 100) + '0000000' + n['hist'].ljust(512)[:512]
        l03 = l03 + base['l03'][len(l03):]
        pos = max(i for i, x in enumerate(E) if x['seq'] is not None and x['seq'] <= n['apos']) + 1
        while pos < len(E) and E[pos].get('novo'): pos += 1
        E.insert(pos, dict(l02=base['l02'], l03=l03, seq=None, d=A(n['d']), c=A(n['c']), v=round(n['v'] * 100), cc=[], ccK=n.get('cc'), novo=True))
    if comp: E = [e for e in E if e['d'] in comp or e['c'] in comp]
    out = [hdr[:2] + emp + cfg['cnpj'] + hdr[23:]]
    k = 0
    for e in E:
        k += 1; out.append(e['l02'][:2] + '%07d' % k + e['l02'][9:])
        k += 1; out.append('03' + '%07d' % k + e['d'] + e['c'] + e['l03'][23:])
        M = cfg.get('cc_map', {})
        if e['ccK']:                                   # Filial: CC pelo bloco
            ccD = ccC = e['ccK']
        else:                                          # Matriz: CC original do Domínio, com troca de código
            ds = [M.get(d, d) for d, c, v in e['cc'] if d != '0000000']
            cs = [M.get(c, c) for d, c, v in e['cc'] if c != '0000000']
            ccD = ds[0] if ds else (cs[0] if cs else None)
            ccC = cs[0] if cs else ccD
        if not (ccD and ccC):                          # Domínio exportou sem 05 (ex.: INSS de rescisão, compensação sal.-maternidade)
            forc = cfg.get('cc_seq', {}).get(str(e['seq']))
            if forc: ccD = ccC = forc
            else:                                      # herda do lançamento vizinho do mesmo bloco e avisa
                i = E.index(e); viz = [x for x in E[i - 1::-1] + E[i + 1:] if x['cc'] or x['ccK']]
                v0 = viz[0]; x0 = next(d if d != '0000000' else c for d, c, _ in v0['cc']) if v0['cc'] else None; cv = v0['ccK'] or M.get(x0, x0)
                ccD = ccC = cv.strip()
                assert ccD, f"seq {e['seq']}: não achei CC vizinho"
                print(f"AVISO: seq {e['seq']} ({e['l03'][45:80].strip()}) veio sem CC do Domínio -> {ccD} (vizinho); confirmar ou usar cc_seq")
        lados = [('D', ccD), ('C', ccC)]
        if comp: lados = [x for x in lados if (e['d'] if x[0] == 'D' else e['c']) in comp]
        for lado, cc in lados:
            cc = cc.ljust(7); k += 1
            out.append('05' + '%07d' % k + (cc + '0000000' if lado == 'D' else '0000000' + cc) + '%015d' % e['v'] + ' ' * 100)
    out += [trailer, '']
    for x in out: assert len(x) in (0, 55, 100, 138, 165, 664), (len(x), x[:20])
    open(dst, 'wb').write('\r\n'.join(out).encode('cp1252'))
    print(f'{len(E)} lançamentos -> {dst}')

if __name__ == '__main__':
    main(*sys.argv[1:4])
