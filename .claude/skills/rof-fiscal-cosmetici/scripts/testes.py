"""Testes rápidos com dados sintéticos (não usam arquivos de cliente).  python testes.py"""
import copy
import datetime as dt
import json
import os
import sys
import tempfile
import zipfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import leitores  # noqa: E402
import txt_dominio  # noqa: E402
from apuracao import Apuracao  # noqa: E402

CFG = json.load(open(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'Cosmetici', 'Fiscal', 'config', 'cosmetici.json'), encoding='utf-8'))
CNPJ = CFG['empresa']['cnpj']


def nfe(chave, num, emit, dest, uf_dest, itens, data='2026-08-10', tpnf='1', fin='1'):
    det = ''
    for k, (cfop, ncm, vprod, picms, vipi, vst, cst_pis) in enumerate(itens, 1):
        vicms = round(vprod * picms / 100, 2)
        det += (f'<det nItem="{k}"><prod><cProd>{k}</cProd><xProd>P{k}</xProd><NCM>{ncm}</NCM><CFOP>{cfop}</CFOP><qCom>1</qCom>'
                f'<vProd>{vprod}</vProd></prod><imposto><ICMS><ICMS00><orig>0</orig><CST>00</CST><vBC>{vprod}</vBC><pICMS>{picms}</pICMS>'
                f'<vICMS>{vicms}</vICMS><vICMSST>{vst}</vICMSST></ICMS00></ICMS><IPI><IPITrib><CST>50</CST><vBC>{vprod}</vBC><pIPI>10</pIPI>'
                f'<vIPI>{vipi}</vIPI></IPITrib></IPI><PIS><PISAliq><CST>{cst_pis}</CST><vBC>{vprod}</vBC><pPIS>2.2</pPIS><vPIS>0</vPIS></PISAliq></PIS>'
                f'</imposto></det>')
    return (f'<nfeProc xmlns="http://www.portalfiscal.inf.br/nfe"><NFe><infNFe Id="NFe{chave}"><ide><mod>55</mod><serie>1</serie>'
            f'<nNF>{num}</nNF><dhEmi>{data}T10:00:00-03:00</dhEmi><tpNF>{tpnf}</tpNF><finNFe>{fin}</finNFe></ide>'
            f'<emit><CNPJ>{emit}</CNPJ><xNome>EMIT {emit[:4]}</xNome><enderEmit><UF>PR</UF></enderEmit></emit>'
            f'<dest><CNPJ>{dest}</CNPJ><xNome>DEST {dest[:4]}</xNome><enderDest><UF>{uf_dest}</UF></enderDest><indIEDest>1</indIEDest></dest>'
            f'{det}<total><ICMSTot><vNF>0</vNF></ICMSTot></total></infNFe></NFe>'
            f'<protNFe><infProt><cStat>100</cStat></infProt></protNFe></nfeProc>')


def cancelamento(chave):
    return (f'<procEventoNFe xmlns="http://www.portalfiscal.inf.br/nfe"><evento><infEvento><chNFe>{chave}</chNFe>'
            f'<dhEvento>2026-08-11T10:00:00-03:00</dhEvento><tpEvento>110111</tpEvento></infEvento></evento></procEventoNFe>')


def montar_zip(arquivos):
    d = tempfile.mkdtemp()
    p = os.path.join(d, 'm.zip')
    with zipfile.ZipFile(p, 'w') as z:
        for nome, txt in arquivos.items():
            z.writestr(nome, txt)
    return p


def teste_apuracao():
    ch = lambda n: f'412608{CNPJ}55001{n:09d}1000000{n % 10}'[:44].ljust(44, '0')
    forn = '11111111000191'
    arqs = {
        'v1.xml': nfe(ch(1), 1, CNPJ, '22222222000191', 'PR', [('5401', '33059000', 1000.0, 12, 143.0, 300.0, '02')]),
        'v2.xml': nfe(ch(2), 2, CNPJ, '33333333000191', 'SP', [('6124', '33059000', 2000.0, 12, 0, 0, '02')]),
        'v3.xml': nfe(ch(3), 3, CNPJ, '22222222000191', 'PR', [('5101', '33059000', 500.0, 19.5, 0, 0, '02')]),
        'c3.xml': cancelamento(ch(3)),
        'e1.xml': nfe(ch(9), 77, forn, CNPJ, 'PR', [('5101', '28470000', 400.0, 12, 0, 0, '01')]),
        'v5.xml': nfe(ch(5), 5, CNPJ, '22222222000191', 'SC', [('5102', '33059000', 100.0, 12, 0, 0, '02')]),
    }
    fontes = leitores.ler_xmls([montar_zip(arqs)])
    a = Apuracao(copy.deepcopy(CFG), '2026-08', fontes, {}).executar()
    assert len(a.saidas) == 3 and len(a.canceladas) == 1 and len(a.entradas) == 1, (len(a.saidas), len(a.canceladas), len(a.entradas))
    # faturamento = vendas (1000+143+300 + 100) + indus 2000 - ST 300 - IPI 143
    assert a.fat['liquido'] == 3100.0, a.fat
    # PIS: indus (2000-240)*0.65% + vendas (1443-120 + 100-12 - 143 - 300)*2.2%
    assert a.pc['base_industrializacao'] == 1760.0 and a.pc['base_vendas'] == 968.0, a.pc
    assert a.pc['pis'] == round(round(1760 * 0.0065, 2) + round(968 * 0.022, 2), 2)
    assert a.ic['debitos'] == 120 + 240 + 12 and a.ic['creditos_nfe'] == 48.0, a.ic
    assert a.st['recolher_pr'] == 300.0 and a.ip['recolher'] == 143.0
    tipos = {d[1] for d in a.div}
    assert 'CFOP x UF' in tipos, tipos                      # 5102 para SC
    assert 'Fornecedor sem histórico' in tipos, tipos
    assert any(d[1] == 'Numeração' and 'NF 4/' in d[2] for d in a.div), a.div   # número 4 faltando
    print('ok apuração')


def teste_irpj_trimestre():
    cfg = copy.deepcopy(CFG)
    a = Apuracao(cfg, '2026-06', {'nfe': {}, 'eventos': [], 'inut': [], 'cte': {}}, {})
    a.fat = {'liquido': 285690.16}
    r = a.irpj_csll()
    assert r['receita'] == 998642.37 and r['irpj'] == 13972.85 and r['csll'] == 10785.34, r   # DARFs do 2º tri/2026
    print('ok IRPJ/CSLL 2º trimestre = DARFs')


def teste_txt():
    cfg = copy.deepcopy(CFG)
    cfg['contas_dominio']['pis'].update(debito=111, credito=222)
    a = Apuracao(cfg, '2026-08', {'nfe': {}, 'eventos': [], 'inut': [], 'cte': {}}, {})
    a.pc = {'pis': 1234.5, 'cofins': 0}
    a.ip = {'recolher': 0}; a.ic = {'recolher': 0}; a.st = {'recolher_pr': 10.0}
    a.ir = {'fechamento': False, 'trimestre': '3º trimestre/2026'}
    d = tempfile.mkdtemp(); p = os.path.join(d, 't.txt')
    lanc, sem = txt_dominio.gerar(a, p)
    linhas = open(p, encoding='cp1252').read().splitlines()
    assert linhas == [f'|0000|{CNPJ}|', '|6000|X||||', '|6100|31/08/2026|111|222|1234,50||PROVISAO PIS S/ FATURAMENTO 08/2026||||'], linhas
    assert open(p, 'rb').read().count(b'\r\n') == 3 and sem == [('icms_st', 10.0)]
    print('ok TXT Domínio')


def teste_sieg_cte():
    from openpyxl import Workbook
    wb = Workbook(); ws = wb.active
    cab = ['Chave', 'Numero', 'Serie', 'Dt_Emissao', 'CNPJ_CPF_Emitente', 'Rz_Emit', 'Uf_Inicio', 'Uf_Final', 'CNPJ_CPF_Tomador',
           'CNPJ_CPF_Outro_Tomador', 'CNPJ_CPF_Dest', 'CNPJ_CPF_Rem', 'CFOP', 'Valor_Transporte', 'CST', 'ICMS_Base_Calculo', 'ICMS_Aliq', 'ICMS', 'Chave_NFe', 'Status']
    ws.append(['Relatorio_CTe.xlsx']); ws.append(cab)
    ws.append(['4' * 44, '2079446', '1', '21/09/2026', '00428307002301', 'TRANSP', 'PR', 'SC', CNPJ, '', '1', CNPJ, '6352', 'R$ 88.00', '00', 'R$ 84.21', 'R$ 12.00', 'R$ 10.11', '', 'Autorizado o uso do CTe'])
    ws.append(['5' * 44, '2', '1', '21/09/2026', '00428307002301', 'TRANSP', 'PR', 'SC', '', '17666331000168', '1', CNPJ, '6353', 'R$ 50.00', '00', 'R$ 50.00', 'R$ 12.00', 'R$ 6.00', '', 'Cancelamento'])
    p = os.path.join(tempfile.mkdtemp(), 'Relatorio_CTe.xlsx'); wb.save(p)
    c = leitores.ler_sieg_cte(p)
    x = c['4' * 44]
    assert x['vicms'] == 10.11 and x['toma_cnpj'] == CNPJ and x['data'] == dt.date(2026, 9, 21) and x['autorizada']
    assert not c['5' * 44]['autorizada'] and c['5' * 44]['toma_cnpj'] == '17666331000168'
    print('ok relatório SIEG de CT-e')


def teste_simples():
    from creditos import Credito
    def item(cfop, ncm, vprod, csosn, pcred=0.0, vcred=0.0, vicms=0.0, cst=None, vipi=0.0):
        return {'n_item': 1, 'xprod': 'X', 'ncm': ncm, 'cfop': cfop, 'vprod': vprod, 'vdesc': 0.0, 'vfrete': 0.0, 'vseg': 0.0, 'voutro': 0.0,
                'vipi': vipi, 'vst': 0.0, 'vfcpst': 0.0, 'vipidevol': 0.0, 'cst_icms': cst or csosn, 'csosn': csosn, 'pcredsn': pcred,
                'vcredsn': vcred, 'vicms': vicms}
    def nota(crt, it, uf='PR', cnpj='99999999000191'):
        return {'numero': 1, 'serie': '1', 'dhemi': dt.date(2026, 9, 5), 'emit_cnpj': cnpj, 'emit_nome': 'F', 'emit_uf': uf, 'emit_crt': crt,
                'finnfe': '1', 'propria': False, 'chave': 'x', 'itens': [it]}
    class A:  # apuração mínima
        cnpj = CNPJ; cfg = CFG; ctes = []
    casos = [
        (nota('1', item('5101', '39191090', 1000, '101', 2.86, 28.60)), 'insumo', 28.60, 0, 0),       # rótulo, Simples com crédito
        (nota('1', item('5101', '48211000', 1000, '102')), 'insumo', 0, 0, 0),                        # Simples sem permissão
        (nota('1', item('5102', '29221100', 1000, '101', 3.0, 0.0)), 'insumo', 0, 30.0, 0),           # % sem valor -> potencial
        (nota('1', item('5102', '64039190', 100, '102')), 'uso', 0, 0, 0),                             # EPI
        (nota('1', item('5901', '39233090', 500, '400')), 'remessa', 0, 0, 0),                         # insumo do cliente
        (nota('3', item('6101', '33029019', 1000, None, vicms=120, cst='00', vipi=50), 'SP'), 'insumo', 120, 0, 50),
        (nota('3', item('6102', '84439923', 1000, None, vicms=120, cst='00'), 'SP'), 'uso', 0, 0, 0),  # uso e consumo -> DIFAL
    ]
    A.entradas = [c[0] for c in casos]
    c = Credito(A, {}).analisar()
    for (n, nat, cred, pot, ipi), l in zip(casos, c.linhas):
        assert l['natureza'] == nat, (n['itens'][0]['ncm'], l['natureza'])
        assert round(l['cred_icms'] + l['cred_sn'], 2) == cred and l['pot_sn'] == pot and l['cred_ipi'] == ipi, l
    assert c.linhas[-1]['difal'] > 0
    print('ok crédito Simples/insumo/uso e consumo')


if __name__ == '__main__':
    teste_simples()
    teste_apuracao()
    teste_irpj_trimestre()
    teste_txt()
    teste_sieg_cte()
