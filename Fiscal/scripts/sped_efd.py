"""Leitura do SPED Fiscal (EFD ICMS/IPI): participantes, itens, naturezas
(acumuladores do Domínio, registro 0400) e documentos C100/C170/C190, D100/D190."""
from decimal import Decimal


def _dec(v):
    v = (v or '').strip()
    return Decimal(v.replace('.', '').replace(',', '.')) if v else Decimal('0')


def parse_sped(path):
    raw = open(path, 'rb').read()
    try:
        txt = raw.decode('utf-8')
    except UnicodeDecodeError:
        txt = raw.decode('latin-1')
    part, prod, nat = {}, {}, {}
    docs, cur = [], None
    ajustes, aj = [], None
    for line in txt.splitlines():
        if not line.startswith('|'):
            continue
        f = line.split('|')[1:-1]
        reg = f[0]
        if reg == '0150':
            part[f[1]] = {'nome': f[2], 'cnpj': f[4] or f[5], 'ie': f[6]}
        elif reg == '0200':
            prod[f[1]] = {'descr': f[2], 'ncm': f[7], 'tipo': f[6]}
        elif reg == '0400':
            nat[f[1]] = f[2]
        elif reg in ('C100', 'D100'):
            if reg == 'C100':
                cur = {'reg': reg, 'ind_oper': f[1], 'ind_emit': f[2], 'cod_part': f[3], 'mod': f[4],
                       'cod_sit': f[5], 'serie': f[6], 'numero': f[7], 'chave': f[8], 'dt_doc': f[9],
                       'dt_es': f[10], 'vl_doc': _dec(f[11]), 'vl_merc': _dec(f[15]),
                       'vl_desc': _dec(f[13]), 'vl_frt': _dec(f[17]),
                       'vl_bc_icms': _dec(f[20]), 'vl_icms': _dec(f[21]), 'vl_bc_st': _dec(f[22]),
                       'vl_st': _dec(f[23]), 'vl_ipi': _dec(f[24]), 'vl_pis': _dec(f[25]),
                       'vl_cofins': _dec(f[26]), 'itens': [], 'c190': []}
            else:
                cur = {'reg': reg, 'ind_oper': f[1], 'ind_emit': f[2], 'cod_part': f[3], 'mod': f[4],
                       'cod_sit': f[5], 'serie': f[6], 'numero': f[8], 'chave': f[9], 'dt_doc': f[10],
                       'dt_es': f[11], 'vl_doc': _dec(f[14]), 'vl_bc_icms': _dec(f[18]),
                       'vl_icms': _dec(f[19]), 'itens': [], 'c190': []}
            cur['part'] = part.get(cur['cod_part'], {})
            docs.append(cur)
        elif reg == 'C170' and cur is not None:
            cur['itens'].append({'n': f[1], 'cod_item': f[2], 'qtd': _dec(f[4]), 'vl_item': _dec(f[6]),
                                 'vl_desc': _dec(f[7]), 'cst_icms': f[9], 'cfop': f[10], 'cod_nat': f[11],
                                 'vl_bc_icms': _dec(f[12]), 'aliq_icms': _dec(f[13]), 'vl_icms': _dec(f[14]),
                                 'vl_bc_st': _dec(f[15]), 'vl_st': _dec(f[17]), 'cst_ipi': f[19],
                                 'vl_bc_ipi': _dec(f[21]), 'vl_ipi': _dec(f[23]),
                                 'cst_pis': f[24], 'cst_cofins': f[30]})
        elif reg in ('C190', 'D190') and cur is not None:
            cur['c190'].append({'cst': f[1], 'cfop': f[2], 'aliq': _dec(f[3]), 'vl_opr': _dec(f[4]),
                                'vl_bc_icms': _dec(f[5]), 'vl_icms': _dec(f[6]),
                                'vl_ipi': _dec(f[10]) if reg == 'C190' and len(f) > 10 else Decimal('0')})
        elif reg == 'E111':
            aj = {'codigo': f[1], 'descr': f[2], 'valor': _dec(f[3]), 'docs': []}
            ajustes.append(aj)
        elif reg == 'E113' and aj is not None:
            aj['docs'].append({'cod_part': f[1], 'numero': f[5], 'valor': _dec(f[8]), 'chave': f[9] if len(f) > 9 else ''})
    return {'participantes': part, 'produtos': prod, 'naturezas': nat, 'docs': docs, 'ajustes_e111': ajustes}
