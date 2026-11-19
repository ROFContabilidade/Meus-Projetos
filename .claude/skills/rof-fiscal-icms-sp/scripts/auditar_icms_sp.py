"""Auditoria de ICMS das ENTRADAS de empresa paulista: DIFAL, alíquota interestadual, ST, CFOP, CST/CSOSN e cadastro.

python3 auditar_icms_sp.py notas.json config.json "ICMS_SP_<Empresa>_MM-AAAA.xlsx"

config.json:
{
 "empresa": {"cnpj": "...", "razao_social": "...", "ie": "...", "regime": "rpa|simples|mei|nao_contribuinte"},
 "competencia": "AAAA-MM",
 "destinacao_padrao": null,                       # ou "uso_consumo" / "ativo" / "revenda" / "industrializacao"
 "destinacao": {"<chave ou nº da nota>": "uso_consumo" | {"*": "revenda", "3": "uso_consumo"}},
 "aliquota_interna": {"<NCM ou prefixo>": 12},   # confirmada pela analista (padrão 18%)
 "data_entrada": {"<chave ou nº>": "AAAA-MM-DD"} # padrão: data de saída/entrada da NF, senão emissão
}
"""
import calendar, json, os, sys
from collections import Counter, defaultdict
from datetime import date

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import tabelas_icms as T

ERRO, ALERTA, APONT = 'ERRO', 'ALERTA', 'APONTAMENTO'
r2 = lambda x: round(x + 1e-9, 2)


def chave_cfg(mapa, nota, default=None):
    for k in (nota['chave'], nota['numero'], f"{nota['emit_cnpj']}-{nota['numero']}"):
        if k in (mapa or {}):
            return mapa[k]
    return default


def destinacao_item(cfg, nota, it):
    d = chave_cfg(cfg.get('destinacao'), nota)
    if isinstance(d, dict):
        return d.get(str(it['nItem']), d.get('*', cfg.get('destinacao_padrao')))
    return d or cfg.get('destinacao_padrao')


def aliq_interna(cfg, ncm):
    mapa = cfg.get('aliquota_interna') or {}
    hits = [p for p in mapa if (ncm or '').startswith(p)]
    if hits:
        return float(mapa[max(hits, key=len)]), True
    return T.ALIQ_INTERNA_SP_PADRAO, False


def ultimo_dia_2o_mes(d):
    y, m = d.year, d.month + 2
    if m > 12:
        y, m = y + 1, m - 12
    return date(y, m, calendar.monthrange(y, m)[1])


def data_entrada(cfg, nota):
    s = chave_cfg(cfg.get('data_entrada'), nota) or nota.get('saida_entrada') or nota.get('emissao')
    try:
        return date.fromisoformat(s[:10])
    except Exception:
        return None


def auditar(dados, cfg):
    emp = cfg['empresa']
    regime = emp.get('regime')
    if regime not in T.REGIMES:
        raise SystemExit(f'regime da empresa inválido: {regime!r} - use {list(T.REGIMES)}')
    cnpj_emp = ''.join(c for c in emp.get('cnpj', '') if c.isdigit())
    ie_emp = ''.join(c for c in emp.get('ie', '') if c.isdigit())
    comp = cfg.get('competencia')
    incons, itens_out, notas_out = [], [], []
    chaves = Counter(n['chave'] for n in dados['notas'])

    def add(g, nota, item, txt):
        incons.append({'gravidade': g, 'nota': nota['numero'], 'emitente': nota['emit_nome'], 'item': item or '',
                       'apontamento': txt, 'chave': nota['chave']})

    for e in dados.get('erros_leitura', []):
        incons.append({'gravidade': ALERTA, 'nota': '', 'emitente': '', 'item': '', 'apontamento': e, 'chave': ''})

    for n in sorted(dados['notas'], key=lambda x: (x['emissao'], x['emit_nome'], x['numero'])):
        tot_difal = 0.0
        interestadual = n['emit_uf'] != 'SP'
        # ---------- cabeçalho da nota ----------
        if chaves[n['chave']] > 1:
            add(ERRO, n, '', 'Nota em DUPLICIDADE no lote - escriturar uma vez só')
        if n['modelo'] and n['modelo'] != '55':
            add(ALERTA, n, '', f"Modelo {n['modelo']} - esta auditoria é para NF-e modelo 55")
        if n['tpNF'] == '0':
            add(ALERTA, n, '', 'tpNF=0 (nota de ENTRADA emitida pelo próprio emitente) - conferir se é devolução/importação')
        if n['protocolo_cStat'] in ('', None):
            add(ALERTA, n, '', 'XML sem protocolo de autorização - consultar a chave no portal da NF-e antes de escriturar')
        elif n['protocolo_cStat'] not in ('100', '150'):
            add(ERRO, n, '', f"Protocolo cStat {n['protocolo_cStat']} - nota NÃO autorizada (denegada/cancelada) - não escriturar")
        if '110111' in n.get('eventos', []):
            add(ERRO, n, '', 'Evento de CANCELAMENTO no XML - nota cancelada, não pode entrar')
        if n['finNFe'] in ('2', '3'):
            add(APONT, n, '', f"Finalidade {n['finNFe']} (complementar/ajuste) - tratar junto com a nota original")
        if n['finNFe'] == '4':
            add(ALERTA, n, '', 'Nota de DEVOLUÇÃO - não é compra; DIFAL não se aplica (estornar o DIFAL da compra, se houve)')
        if cnpj_emp and n['dest_cnpj'] != cnpj_emp:
            add(ERRO, n, '', f"Destinatário da nota ({n['dest_cnpj']}) não é a empresa ({cnpj_emp}) - nota de outro estabelecimento/empresa?")
        if n['dest_uf'] != 'SP':
            add(ERRO, n, '', f"UF do destinatário na nota = {n['dest_uf']} (esperado SP)")
        if ie_emp and n['dest_ie'] and ''.join(c for c in n['dest_ie'] if c.isdigit()) != ie_emp:
            add(ERRO, n, '', f"IE do destinatário na nota ({n['dest_ie']}) diferente da IE da empresa ({emp.get('ie')})")
        contrib = regime in ('rpa', 'simples', 'mei')
        if contrib and n['dest_indIEDest'] == '9':
            add(ERRO, n, '', 'indIEDest=9: o fornecedor tratou a empresa como NÃO contribuinte (DIFAL pode ter sido cobrado '
                              'dele para SP via GNRE e a nota sai sem IE) - pedir carta de correção/substituição; conferir DIFAL em dobro')
        if contrib and not n['dest_ie']:
            add(ERRO, n, '', 'Nota sem a IE do destinatário - empresa é contribuinte em SP')
        if regime == 'nao_contribuinte' and n['dest_indIEDest'] == '1':
            add(ALERTA, n, '', 'indIEDest=1 (contribuinte) mas a empresa foi informada como NÃO contribuinte - conferir cadastro (IE ativa?)')
        if interestadual and n['idDest'] != '2':
            add(ERRO, n, '', f"Emitente em {n['emit_uf']} e idDest={n['idDest']} (esperado 2 - interestadual)")
        if comp and n['emissao'][:7] != comp:
            add(ALERTA, n, '', f"Emissão {n['emissao']} fora da competência {comp} - conferir data de ENTRADA (o DIFAL é da entrada)")
        if not interestadual:
            add(APONT, n, '', 'Operação INTERNA (emitente em SP) - não há DIFAL; conferir só alíquota interna, ST e crédito')
        if n['emit_crt'] == '4':
            add(APONT, n, '', 'Emitente MEI (CRT 4) - nota sem destaque; DIFAL calculado pela alíquota interestadual (art. 117 §6º)')
        soma = sum(i['vProd'] for i in n['itens'])
        if abs(soma - n['vProd']) > 0.05:
            add(ERRO, n, '', f"Soma dos itens (R$ {soma:,.2f}) ≠ vProd da nota (R$ {n['vProd']:,.2f})")

        ent = data_entrada(cfg, n)
        tem_difal_nota = False

        # ---------- itens ----------
        for it in n['itens']:
            ni = it['nItem']
            dest = destinacao_item(cfg, n, it)
            if dest not in T.DESTINACOES:
                add(ERRO, n, ni, f"Destinação do item não informada ({it['descricao'][:40]}) - revenda, industrialização, "
                                  f"uso/consumo ou ativo? (DIFAL calculado como USO/CONSUMO até a analista responder)")
                dest_calc = 'uso_consumo'; pend = True
            else:
                dest_calc = dest; pend = False
            cfop = it['cfop']
            inter_ok = T.aliq_interestadual(it['orig'])
            p_int, int_conf = aliq_interna(cfg, it['ncm'])
            simples_emit = n['emit_crt'] in ('1', '2', '4')

            # CFOP
            if interestadual and not cfop.startswith('6'):
                add(ERRO, n, ni, f'CFOP {cfop} em operação interestadual (deveria começar com 6)')
            if cfop in T.CFOP_NAO_CONTRIB and regime in ('rpa', 'simples'):
                add(ERRO, n, ni, f'CFOP {cfop} = venda a NÃO contribuinte, mas a empresa é contribuinte em SP - '
                                  f'conferir se o fornecedor recolheu DIFAL a SP (GNRE) e pedir correção')
            if cfop in T.CFOP_ESTRANHO:
                add(ALERTA, n, ni, T.CFOP_ESTRANHO[cfop])
            if cfop in T.CFOP_ST and it['vICMSST'] == 0 and cfop != '6404':
                add(ERRO, n, ni, f'CFOP {cfop} (com ST) sem ICMS-ST destacado')
            if cfop == '6404' or it['cst'] == '60' or it['csosn'] == '500':
                add(ALERTA, n, ni, 'Interestadual com "ST já retida anteriormente" (CFOP 6404/CST 60/CSOSN 500): o ST recolhido em '
                                    'outra UF NÃO vale para SP - conferir se há acordo PR-SP p/ o produto ou se a empresa deve recolher ST/antecipação')
            sem_difal_cfop = cfop in T.CFOP_SEM_DIFAL

            # Regime do emitente x leiaute
            if n['emit_crt'] == '3' and it['icms_grupo'].startswith('ICMSSN'):
                add(ERRO, n, ni, 'Emitente regime normal (CRT 3) usando grupo do Simples (CSOSN)')
            if simples_emit and it['icms_grupo'] and not it['icms_grupo'].startswith('ICMSSN') and n['emit_crt'] != '2':
                add(ALERTA, n, ni, f"Emitente do Simples (CRT {n['emit_crt']}) com CST {it['cst']} - conferir regime do fornecedor")

            # Alíquota interestadual
            orig_desc = T.ORIGEM.get(it['orig'], ('origem ?',))[0]
            if it['orig'] not in T.ORIGEM:
                add(ERRO, n, ni, f"Origem da mercadoria inválida/ausente ({it['orig']!r})")
            if interestadual and it['pICMS'] > 0:
                if abs(it['pICMS'] - inter_ok) > 0.001:
                    g = ERRO if it['pICMS'] > inter_ok else ALERTA
                    add(g, n, ni, f"Alíquota destacada {it['pICMS']:.2f}% ≠ interestadual correta {inter_ok:.0f}% "
                                  f"(origem {it['orig']} - {orig_desc}; Res. Senado 22/89 e 13/2012). "
                                  + ('Crédito limitado a ' + f'{inter_ok:.0f}%; exigir nota correta.' if it['pICMS'] > inter_ok else
                                     'Destaque a menor: conferir benefício na origem.'))
            if it['orig'] in ('3', '5', '8') and 'FCI' not in (it['infAdProd'] + n['infCpl']).upper():
                add(ALERTA, n, ni, f"Origem {it['orig']} sem número da FCI nas informações do item (Ajuste SINIEF 19/2012)")
            if n['emit_crt'] == '3' and it['cst'] in T.CST_SEM_DESTAQUE and it['cst'] != '60':
                add(ALERTA, n, ni, f"CST {it['cst']} (sem tributação) em venda interestadual de regime normal - qual isenção/benefício? "
                                    f"Exigir dispositivo legal na nota; conferir se SP concede o mesmo (senão DIFAL cheio)")
            if it['pRedBC'] > 0:
                add(ALERTA, n, ni, f"Redução de base na origem ({it['pRedBC']:.2f}%) - conferir convênio; crédito só do destacado")
            if n['emit_crt'] == '3' and it['cst'] in ('00', '20') and it['vBC'] > 0 and abs(it['vBC'] * it['pICMS'] / 100 - it['vICMS']) > 0.05:
                add(ERRO, n, ni, f"vICMS {it['vICMS']:.2f} ≠ vBC × alíquota ({it['vBC'] * it['pICMS'] / 100:.2f})")

            # NCM
            if len(it['ncm']) != 8:
                add(ALERTA, n, ni, f"NCM inválido/ausente ({it['ncm']!r})")
            a_aliq = T.busca_prefixo(it['ncm'], T.NCM_ALIQ_ALERTA)
            if a_aliq and not int_conf and dest_calc in ('uso_consumo', 'ativo'):
                add(ALERTA, n, ni, f"NCM {it['ncm']}: {a_aliq}. DIFAL calculado com 18% até a analista confirmar")
            a_st = T.busca_prefixo(it['ncm'], T.NCM_ST_ALERTA)
            st_retido = it['vICMSST'] > 0
            if a_st and not it['cest']:
                add(ALERTA, n, ni, f"NCM {it['ncm']} ({a_st}) sem CEST - mercadoria com cara de ST exige CEST (Conv. 142/2018)")
            if a_st and dest_calc in ('revenda', 'industrializacao') and not st_retido and interestadual:
                add(ALERTA if dest_calc == 'revenda' else APONT, n, ni,
                    f"NCM {it['ncm']} - {a_st}: possível ST em SP e o fornecedor NÃO reteve. "
                    f"Se houver ST em SP p/ esse NCM/CEST, o destinatário paulista recolhe na entrada "
                    f"(RICMS/SP art. 426-A ou regra do produto; DARE 063-2). Industrialização costuma ser dispensada (art. 426-A §6º)")
            if st_retido:
                if not n['emit_iest']:
                    add(ALERTA, n, ni, f"ICMS-ST R$ {it['vICMSST']:,.2f} retido e emitente SEM IE de substituto em SP: "
                                        f"a GNRE paga tem de acompanhar a mercadoria - exigir comprovante")
                if dest_calc in ('uso_consumo', 'ativo'):
                    add(APONT, n, ni, 'ST retida em mercadoria de uso/consumo/ativo: conferir se o ST já cobre o DIFAL (não pagar em dobro)')

            # ---------- DIFAL ----------
            V = it['vProd'] + it['vFrete'] + it['vSeg'] + it['vOutro'] - it['vDesc'] + it['vIPI']
            difal = 0.0; bc_dest = 0.0; icms_orig = 0.0; regra = ''
            if not interestadual:
                regra = 'Interna - sem DIFAL'
            elif sem_difal_cfop:
                regra = f'CFOP {cfop} - remessa/retorno/devolução, sem DIFAL'
            elif dest_calc in ('revenda', 'industrializacao') and regime != 'nao_contribuinte':
                regra = f'{dest_calc} - sem DIFAL (conferir ST/antecipação)'
            elif st_retido and dest_calc in ('uso_consumo', 'ativo'):
                regra = 'ST retida pelo fornecedor - conferir se já cobre o DIFAL (não calculado)'
            else:
                if it['pICMS'] > 0 and n['emit_crt'] == '3':
                    icms_orig = min(it['vICMS'], (it['vBC'] or V) * inter_ok / 100)
                elif n['emit_crt'] == '3' and it['cst'] in T.CST_SEM_DESTAQUE:
                    icms_orig = 0.0
                else:  # Simples/MEI ou sem destaque: alíquota interestadual "virtual" (art. 117 §5º e §6º)
                    icms_orig = V * inter_ok / 100
                if regime == 'rpa':
                    bc_dest = (V - icms_orig) / (1 - p_int / 100)
                    difal = bc_dest * p_int / 100 - icms_orig
                    regra = f'RPA - base dupla (por dentro): BC = (V - ICMS origem)/(1 - {p_int:g}%) - art. 117 + art. 37 VI'
                elif regime in ('simples', 'mei'):
                    bc_dest = V
                    difal = V * (p_int - inter_ok) / 100
                    regra = f'Simples - base única: V × ({p_int:g}% - {inter_ok:g}%) - art. 2º XVI e 115 XV-A (RC 29508/2024)'
                    if regime == 'mei':
                        add(ALERTA, n, ni, 'Empresa MEI: confirmar se o DIFAL é exigido do MEI no caso (calculado como Simples, para conferência)')
                else:  # não contribuinte: DIFAL é do REMETENTE (EC 87/2015, LC 190/2022)
                    bc_dest = (V - V * inter_ok / 100) / (1 - p_int / 100)
                    esperado = bc_dest * p_int / 100 - V * inter_ok / 100
                    regra = 'Não contribuinte - DIFAL do REMETENTE (EC 87/LC 190), base dupla; conferir grupo ICMSUFDest'
                    if n['emit_crt'] == '3':
                        if not it['tem_ICMSUFDest']:
                            add(ERRO, n, ni, f'Venda a não contribuinte de SP sem grupo ICMSUFDest: remetente não recolheu o DIFAL '
                                              f'(esperado ~R$ {esperado:,.2f}). SP pode cobrar; exigir GNRE do fornecedor')
                        elif abs(it['ufdest_v'] - esperado) > max(0.05, esperado * 0.01):
                            add(ALERTA, n, ni, f"vICMSUFDest R$ {it['ufdest_v']:,.2f} ≠ esperado R$ {esperado:,.2f} (base dupla) - conferir")
                    else:
                        add(APONT, n, ni, 'Remetente do Simples vendendo a não contribuinte: DIFAL EC 87 não exigido do Simples (STF ADI 5464)')
                    difal = 0.0  # não é débito da empresa
                difal = max(0.0, difal)
                if pend:
                    regra = 'PENDENTE (destinação não informada) - ' + regra
                if regime in ('simples', 'mei') and it['pRedBC'] > 0:
                    add(APONT, n, ni, 'Simples: SEFAZ-SP não aceita redução de base no cálculo do DIFAL (conferir orientação vigente)')
                if difal > 0:
                    tem_difal_nota = True
                if dest_calc == 'ativo' and regime == 'rpa':
                    add(APONT, n, ni, 'Ativo imobilizado (RPA): crédito do ICMS (origem + DIFAL) em 1/48 pelo CIAP (art. 61 §10)')
            tot_difal += difal
            ent_cfop = T.CFOP_ENTRADA.get(dest_calc, ('', ''))
            itens_out.append({
                'nota': n['numero'], 'emissao': n['emissao'], 'emitente': n['emit_nome'], 'uf': n['emit_uf'],
                'crt': n['emit_crt'], 'item': ni, 'codigo': it['codigo'], 'descricao': it['descricao'], 'ncm': it['ncm'],
                'cest': it['cest'], 'cfop_forn': cfop, 'cfop_entrada': ent_cfop[1] if st_retido else ent_cfop[0],
                'orig': it['orig'], 'cst': it['cst'] or it['csosn'], 'destinacao': dest or 'NÃO INFORMADA',
                'valor_operacao': r2(V), 'vIPI': it['vIPI'], 'vBC_orig': it['vBC'], 'p_destacado': it['pICMS'],
                'p_inter_ok': inter_ok, 'vICMS_destacado': it['vICMS'], 'icms_origem_difal': r2(icms_orig),
                'p_interna': p_int, 'bc_destino': r2(bc_dest), 'difal': r2(difal), 'vICMSST': it['vICMSST'],
                'credito_pCredSN': it['pCredSN'], 'vCredICMSSN': it['vCredICMSSN'], 'regra': regra,
            })
        if tem_difal_nota and n['modFrete'] in ('1', '2'):
            add(ALERTA, n, '', 'Frete por conta do destinatário/terceiro (modFrete 1/2): se o transporte interestadual foi contratado '
                               'pela empresa, há DIFAL também sobre o CT-e (serviço de transporte p/ uso/consumo) - pedir o CT-e')
        if tem_difal_nota and 'DIFAL' in (n['infCpl'] + n['infAdFisco']).upper():
            add(APONT, n, '', 'Informações complementares citam DIFAL - conferir se o fornecedor já recolheu (GNRE) para não pagar em dobro')
        notas_out.append({'nota': n['numero'], 'serie': n['serie'], 'emissao': n['emissao'],
                          'entrada': ent.isoformat() if ent else '', 'emitente': n['emit_nome'], 'cnpj': n['emit_cnpj'],
                          'uf': n['emit_uf'], 'crt': n['emit_crt'], 'natureza': n['natureza'], 'vNF': n['vNF'],
                          'vICMS': n['vICMS'], 'vST': n['vST'], 'vIPI': n['vIPI'], 'difal': r2(tot_difal),
                          'vencimento': (ultimo_dia_2o_mes(ent).isoformat() if ent and regime in ('simples', 'mei') and tot_difal > 0
                                         else ('apuração do mês' if tot_difal > 0 else '')),
                          'chave': n['chave'], 'modFrete': n['modFrete']})
    return notas_out, itens_out, incons


# ----------------------------------------------------------------------------------- planilha
def planilha(notas, itens, incons, cfg, dst):
    from openpyxl import Workbook
    from openpyxl.styles import Font, PatternFill, Alignment
    from openpyxl.utils import get_column_letter
    wb = Workbook()
    F = {ERRO: PatternFill('solid', fgColor='F8CBAD'), ALERTA: PatternFill('solid', fgColor='FFE699'),
         APONT: PatternFill('solid', fgColor='DDEBF7')}
    H = PatternFill('solid', fgColor='1F4E78')
    money = '#,##0.00'

    def tabela(ws, linha, cabec, dados, moedas=(), larg=None, cor=None):
        for j, h in enumerate(cabec, 1):
            c = ws.cell(linha, j, h); c.font = Font(bold=True, color='FFFFFF'); c.fill = H
            c.alignment = Alignment(wrap_text=True, vertical='center')
        for i, row in enumerate(dados, linha + 1):
            for j, v in enumerate(row, 1):
                c = ws.cell(i, j, v)
                if j - 1 in moedas: c.number_format = money
                if cor and cor(row): c.fill = cor(row)
        for j, w in enumerate(larg or [], 1):
            ws.column_dimensions[get_column_letter(j)].width = w
        ws.freeze_panes = ws.cell(linha + 1, 1)

    emp = cfg['empresa']; reg = emp['regime']
    ws = wb.active; ws.title = 'Resumo'
    ws['A1'] = f"Auditoria ICMS SP - entradas - {emp.get('razao_social', '')}"; ws['A1'].font = Font(bold=True, size=14)
    ws['A2'] = f"CNPJ {emp.get('cnpj', '')}  IE {emp.get('ie', '')}  Regime: {T.REGIMES[reg]}  Competência: {cfg.get('competencia', '')}"
    tot = sum(i['difal'] for i in itens)
    cont = Counter(x['gravidade'] for x in incons)
    linhas = [('Notas lidas', len(notas)), ('Itens', len(itens)), ('DIFAL a recolher (R$)', r2(tot)),
              ('ERROS', cont[ERRO]), ('ALERTAS', cont[ALERTA]), ('Apontamentos', cont[APONT]),
              ('Itens sem destinação informada', sum(1 for i in itens if i['destinacao'] == 'NÃO INFORMADA'))]
    for k, (a, b) in enumerate(linhas, 4):
        ws.cell(k, 1, a).font = Font(bold=True); c = ws.cell(k, 2, b)
        if 'R$' in a: c.number_format = money
    k += 2
    ws.cell(k, 1, 'Como recolher').font = Font(bold=True)
    ws.cell(k, 2, T.GUIA_SIMPLES if reg in ('simples', 'mei') else T.GUIA_RPA if reg == 'rpa'
            else 'Não contribuinte: DIFAL é do REMETENTE (GNRE). A empresa não recolhe; exigir comprovação.')
    ws.cell(k, 2).alignment = Alignment(wrap_text=True)
    k += 2
    ws.cell(k, 1, 'DIFAL por vencimento').font = Font(bold=True)
    por_venc = defaultdict(float)
    for n in notas:
        if n['difal']: por_venc[n['vencimento']] += n['difal']
    for v, s in sorted(por_venc.items()):
        k += 1; ws.cell(k, 1, v); ws.cell(k, 2, r2(s)).number_format = money
    ws.column_dimensions['A'].width = 34; ws.column_dimensions['B'].width = 110

    ws = wb.create_sheet('Itens e DIFAL')
    cab = ['Nota', 'Emissão', 'Emitente', 'UF', 'CRT', 'Item', 'Código', 'Descrição', 'NCM', 'CEST', 'CFOP forn.',
           'CFOP entrada', 'Orig', 'CST/CSOSN', 'Destinação', 'Valor operação', 'IPI', 'BC origem', '% destacado',
           '% interest. correto', 'ICMS destacado', 'ICMS origem p/ DIFAL', '% interna SP', 'BC destino', 'DIFAL', 'ICMS-ST',
           'pCredSN', 'Crédito SN', 'Regra aplicada']
    ks = ['nota', 'emissao', 'emitente', 'uf', 'crt', 'item', 'codigo', 'descricao', 'ncm', 'cest', 'cfop_forn',
          'cfop_entrada', 'orig', 'cst', 'destinacao', 'valor_operacao', 'vIPI', 'vBC_orig', 'p_destacado', 'p_inter_ok',
          'vICMS_destacado', 'icms_origem_difal', 'p_interna', 'bc_destino', 'difal', 'vICMSST', 'credito_pCredSN',
          'vCredICMSSN', 'regra']
    tabela(ws, 1, cab, [[i[x] for x in ks] for i in itens], moedas=(15, 16, 17, 20, 21, 23, 24, 25, 27),
           larg=[8, 11, 28, 4, 4, 5, 10, 34, 10, 9, 8, 9, 5, 7, 13, 13, 9, 11, 8, 8, 11, 11, 8, 12, 11, 10, 7, 9, 60],
           cor=lambda r: F[ALERTA] if r[14] == 'NÃO INFORMADA' else None)
    n = len(itens) + 2
    ws.cell(n, 24, 'TOTAL').font = Font(bold=True)
    ws.cell(n, 25, f'=SUM(Y2:Y{n - 1})').number_format = money

    ws = wb.create_sheet('Notas')
    cab = ['Nota', 'Série', 'Emissão', 'Entrada', 'Emitente', 'CNPJ', 'UF', 'CRT', 'Natureza', 'Valor NF', 'ICMS', 'ICMS-ST',
           'IPI', 'DIFAL', 'Vencimento DIFAL', 'modFrete', 'Chave']
    ks = ['nota', 'serie', 'emissao', 'entrada', 'emitente', 'cnpj', 'uf', 'crt', 'natureza', 'vNF', 'vICMS', 'vST', 'vIPI',
          'difal', 'vencimento', 'modFrete', 'chave']
    tabela(ws, 1, cab, [[x[k] for k in ks] for x in notas], moedas=(9, 10, 11, 12, 13),
           larg=[8, 5, 11, 11, 30, 16, 4, 4, 26, 12, 10, 10, 10, 11, 15, 8, 46])

    ws = wb.create_sheet('Inconsistências')
    ordem = {ERRO: 0, ALERTA: 1, APONT: 2}
    rows = [[x['gravidade'], x['nota'], x['emitente'], x['item'], x['apontamento'], '', '', x['chave']]
            for x in sorted(incons, key=lambda x: (ordem[x['gravidade']], str(x['nota'])))]
    tabela(ws, 1, ['Gravidade', 'Nota', 'Emitente', 'Item', 'Apontamento', 'Resolvido?', 'Observação da analista', 'Chave'],
           rows, larg=[13, 8, 28, 5, 110, 11, 40, 46], cor=lambda r: F[r[0]])
    for row in ws.iter_rows(min_row=2, min_col=5, max_col=5):
        for c in row: c.alignment = Alignment(wrap_text=True, vertical='top')

    ws = wb.create_sheet('Regras e base legal')
    regras = [
        ('Alíquota interestadual p/ SP', '12% de qualquer UF; 4% para importados (origem 1, 2, 3, 8) - Res. Senado 22/1989 e 13/2012'),
        ('Alíquota interna SP', '18% regra geral (RICMS/SP art. 52, I); 7%, 12%, 25% e reduções de base conforme produto - confirmar por NCM'),
        ('DIFAL - contribuinte RPA', 'Uso/consumo e ativo: base dupla ("por dentro") desde 03/2022 - RICMS/SP art. 2º VI, art. 37 VI, '
                                     'art. 117 (Lei 6.374/89 art. 24; Decreto 66.559/2022). Lança débito/crédito na apuração do mês da entrada'),
        ('DIFAL - remetente do Simples', 'Calcular como se o remetente não fosse optante, com 4%/12% (art. 117 §5º e §6º; RC 31674/2025)'),
        ('DIFAL - optante do Simples em SP', 'Uso/consumo e ativo: base única, V × (interna - interestadual), sem redução de base; '
                                             'DARE-SP 063-2 até o último dia do 2º mês seguinte à entrada (art. 2º XVI, 115 XV-A; RC 29508/2024)'),
        ('DIFAL - não contribuinte', 'Devido pelo REMETENTE a SP (CF art. 155 §2º VII/VIII "b", EC 87/2015, LC 190/2022), base dupla; '
                                     'remetente do Simples dispensado (STF ADI 5464)'),
        ('Revenda / industrialização', 'Sem DIFAL. Conferir ST: sem retenção pelo remetente, o destinatário paulista pode responder '
                                       '(art. 426-A - medicamentos, bebidas alcoólicas, perfumaria, higiene e limpeza - e regras de cada produto)'),
        ('Crédito', 'Uso/consumo: sem crédito até 2032 (LC 87 art. 33, I). Ativo: 1/48 no CIAP. Revenda/industrialização: crédito do destacado '
                    'limitado à alíquota interestadual correta; Simples remetente: crédito do pCredSN (CSOSN 101) - LC 123 art. 23'),
        ('Frete (CT-e)', 'Transporte interestadual contratado pela empresa para mercadoria de uso/consumo também gera DIFAL do serviço'),
        ('Reforma tributária', '2026: teste de IBS/CBS nas notas; ICMS segue integral até 2028; de 2029 a 2032 fica em 90/80/70/60% das alíquotas; extinto em 2033 (EC 132/2023, LC 214/2025)'),
        ('ATENÇÃO', 'Tabelas são atalho. Prevalece o texto vigente do RICMS/SP e as Respostas à Consulta da SEFAZ-SP. Na dúvida, pesquisar e registrar.'),
    ]
    tabela(ws, 1, ['Tema', 'Regra'], regras, larg=[30, 150])
    for row in ws.iter_rows(min_row=2, min_col=2, max_col=2):
        for c in row: c.alignment = Alignment(wrap_text=True, vertical='top')
    wb.save(dst)


def main():
    dados = json.load(open(sys.argv[1], encoding='utf-8'))
    cfg = json.load(open(sys.argv[2], encoding='utf-8'))
    dst = sys.argv[3]
    notas, itens, incons = auditar(dados, cfg)
    planilha(notas, itens, incons, cfg, dst)
    c = Counter(x['gravidade'] for x in incons)
    print(f"{len(notas)} notas, {len(itens)} itens. DIFAL total R$ {sum(i['difal'] for i in itens):,.2f}. "
          f"ERROS {c[ERRO]} | ALERTAS {c[ALERTA]} | APONTAMENTOS {c[APONT]} -> {dst}")
    for x in incons:
        if x['gravidade'] == ERRO:
            print(f"  ERRO nota {x['nota']} item {x['item']}: {x['apontamento']}")


if __name__ == '__main__':
    main()
