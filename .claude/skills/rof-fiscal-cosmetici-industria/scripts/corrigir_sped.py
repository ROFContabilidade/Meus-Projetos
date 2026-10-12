"""Corrige o SPED EFD ICMS/IPI gerado pelo Domínio antes de validar no PVA (erros vistos em 09/2026):
- C170 de entrada (CFOP 1/2/3) com CST_IPI >= 50 (CST de saída do fornecedor) -> tabela de entrada (cst_ipi_entrada);
- E510 das entradas reagrupado pelo CST novo (valores somados, nada recalculado);
- E116 / E250 com o código de receita do PR usado em 07 e 08/2026 (config: cod_receita_icms 1015, cod_receita_st 100099);
- E990, 9900 e 9999 recontados. Nenhum outro valor é alterado.
Uso: python corrigir_sped.py <sped.txt> <saida.txt> [--cod-icms 1015] [--cod-st 100099]"""
import argparse, collections
from sped_importacao import cst_ipi_entrada


def corrigir(linhas, cod_icms='1015', cod_st='100099'):
    num = lambda x: float(x.replace(',', '.')) if x else 0.0
    fmt = lambda v: f'{v:.2f}'.replace('.', ',')
    log, mapa, out = [], collections.defaultdict(set), []
    for l in linhas:
        p = l.split('|')
        if p[1] == 'C170' and p[11][:1] in '123' and p[20] and p[20] >= '50':
            novo = cst_ipi_entrada(p[20], num(p[24]))
            mapa[(p[11], p[20])].add(novo)
            log.append(f'C170 CFOP {p[11]} item {p[2]} {p[3]}: CST IPI {p[20]} -> {novo}')
            p[20] = novo
        elif p[1] == 'E116' and p[5] != cod_icms:
            log.append(f'E116 código de receita {p[5]} -> {cod_icms}'); p[5] = cod_icms
        elif p[1] == 'E250' and p[5] != cod_st:
            log.append(f'E250 código de receita {p[5]} -> {cod_st}'); p[5] = cod_st
        out.append('|'.join(p))
    # E510: entradas com CST >= 50 relabeladas e somadas ao grupo de mesmo CFOP/CST
    e510 = collections.OrderedDict()
    for p in (l.split('|') for l in out if l.startswith('|E510|')):
        cst = p[3]
        if p[2][:1] in '123' and cst >= '50':
            novos = mapa.get((p[2], cst)) or {cst_ipi_entrada(cst, num(p[6]))}
            assert len(novos) == 1, f'E510 {p[2]}/{cst} mistura CSTs de entrada {novos} - revisar à mão'
            cst = novos.pop()
            log.append(f'E510 CFOP {p[2]}: CST {p[3]} -> {cst}')
        g = e510.setdefault((p[2], cst), [0.0, 0.0, 0.0])
        for k in range(3):
            g[k] += num(p[4 + k])
    novos510 = [f'|E510|{cf}|{cst}|{fmt(g[0])}|{fmt(g[1])}|{fmt(g[2])}|' for (cf, cst), g in sorted(e510.items())]
    i = next(k for k, l in enumerate(out) if l.startswith('|E510|'))
    out = [l for l in out if not l.startswith('|E510|')]
    out[i:i] = novos510
    # totais dos blocos
    cont = collections.Counter(l.split('|')[1] for l in out)
    blocoE = sum(v for r, v in cont.items() if r.startswith('E'))
    out = [f'|E990|{blocoE}|' if l.startswith('|E990|') else l for l in out]
    out = [f'|9900|E510|{cont["E510"]}|' if l.startswith('|9900|E510|') else l for l in out]
    out = [f'|9999|{len(out)}|' if l.startswith('|9999|') else l for l in out]
    return out, log


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('entrada'); ap.add_argument('saida')
    ap.add_argument('--cod-icms', default='1015'); ap.add_argument('--cod-st', default='100099')
    a = ap.parse_args()
    linhas = open(a.entrada, encoding='latin-1', newline='').read().replace('\r\n', '\n').rstrip('\n').split('\n')
    out, log = corrigir(linhas, a.cod_icms, a.cod_st)
    open(a.saida, 'w', encoding='latin-1', newline='').write('\r\n'.join(out) + '\r\n')
    print('\n'.join(log)); print(f'{len(log)} correções')
