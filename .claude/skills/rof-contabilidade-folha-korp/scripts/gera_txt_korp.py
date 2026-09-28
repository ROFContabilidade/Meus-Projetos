"""Gera o TXT corrigido para a Korp a partir do TXT exportado do Domínio.

Uso: python gera_txt_korp.py Folha.txt config.json saida.txt

config.json:
{
  "empresa": "0000145",                 # código Domínio (140 Matriz, 145 Filial) - filtra os lançamentos
  "cnpj": "03623045000291",             # CNPJ do cabeçalho (registro 01)
  "cc_blocos": [[700, 708, "CC345"]],   # faixas de seq (registro 03 original) -> CC Korp  (Filial: sem 05 no Domínio)
  "cc_map": {"0000001": "CC337"},       # OU: troca de CC numérico existente (Matriz: 05 já vem do Domínio)
  "sem_cc": ["2530","2531","2533","3137"],
  "corrigir": {"752": [null, 2521]},    # seq -> [nova conta débito|null, nova conta crédito|null]
  "excluir": [734, 736],                # seq a remover
  "incluir": [{"apos": 844, "modelo": 830, "d": 3152, "c": 2524, "v": 483.87, "hist": "DIAS FERIAS", "cc": "CC345"}]
}
Mantém cp1252 + CRLF e o tamanho de cada registro; renumera a sequência.
"""
import json, sys
from txt_dominio import parse

def A(n): return '%07d' % int(n)

def main(src, cfg_path, dst):
    cfg = json.load(open(cfg_path, encoding='utf-8'))
    L, ents = parse(src)
    hdr = L[0]; trailer = [l for l in L if l[:2] == '99'][0]
    emp = cfg['empresa']; sem_cc = {A(a) for a in cfg.get('sem_cc', ['2530', '2531', '2533', '3137'])}
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
    out = [hdr[:2] + emp + cfg['cnpj'] + hdr[23:]]
    k = 0
    for e in E:
        k += 1; out.append(e['l02'][:2] + '%07d' % k + e['l02'][9:])
        k += 1; out.append('03' + '%07d' % k + e['d'] + e['c'] + e['l03'][23:])
        if e['ccK']:                                   # CC reconstruído (Filial)
            cc = e['ccK'].ljust(7)
            if e['d'] not in sem_cc: k += 1; out.append('05' + '%07d' % k + cc + '0000000' + '%015d' % e['v'] + ' ' * 100)
            if e['c'] not in sem_cc: k += 1; out.append('05' + '%07d' % k + '0000000' + cc + '%015d' % e['v'] + ' ' * 100)
        else:                                          # CC original do Domínio (Matriz), com troca de código
            M = cfg.get('cc_map', {})
            for d, c, v in e['cc']:
                d2 = M.get(d, d).ljust(7) if d != '0000000' else d
                c2 = M.get(c, c).ljust(7) if c != '0000000' else c
                k += 1; out.append('05' + '%07d' % k + d2 + c2 + '%015d' % v + ' ' * 100)
    out += [trailer, '']
    for x in out: assert len(x) in (0, 55, 100, 138, 165, 664), (len(x), x[:20])
    open(dst, 'wb').write('\r\n'.join(out).encode('cp1252'))
    print(f'{len(E)} lançamentos -> {dst}')

if __name__ == '__main__':
    main(*sys.argv[1:4])
