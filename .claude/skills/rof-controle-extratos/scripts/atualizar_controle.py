# -*- coding: utf-8 -*-
"""
ROF Contabilidade - Controle de Extratos e Lançamentos.

Lê as pastas das empresas no Drive (pasta Contabilidade, com as raízes
"Arquivos ROF Dominio", "Arquivos RENATA Dominio", ...), confere em cada mês:
  - se o extrato foi enviado (pasta MM_AAAA/Extrato com OFX/PDF/CSV/XLS...);
  - se já foi lançado (TXT de lançamento do escritório na pasta do mês);
e gera a planilha nova a partir da planilha anterior (que guarda os bancos da
Rotina, as skills, as confirmações manuais e o "Enviado?" das mensagens).

Uso:
  python atualizar_controle.py --contabilidade "G:/Meu Drive/Trabalho ROF/Contabilidade" \
      --base "Controle_de_Extratos_e_Lancamentos.xlsx" --fim 10_2026 \
      --saida "Controle_de_Extratos_e_Lancamentos_2026-11-16.xlsx" [--ajustes ajustes.json]

Nada é alterado no Drive: o script só lê.
"""
import argparse, datetime as dt, json, os, re, sys, unicodedata
from collections import Counter, defaultdict

import openpyxl
from openpyxl.styles import Alignment, Font, PatternFill
from openpyxl.utils import get_column_letter

AQUI = os.path.dirname(os.path.abspath(__file__))
MESES_PT = ['Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho', 'Julho',
            'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro']

GRUPO_DA_RAIZ = {  # trecho do nome da raiz -> grupo da planilha
    'ROF': 'ROF SERVIÇOS',
    'RENATA': 'KON CONTABILIDADE',
    'KON': 'KON CONTABILIDADE',
    'PROTECTION': 'PROTECTION CONTABILIDADE',
}

# ---------------------------------------------------------------- utilidades

def sem_acento(s):
    s = unicodedata.normalize('NFKD', str(s))
    return ''.join(c for c in s if not unicodedata.combining(c)).lower()


def numero_empresa(nome):
    m = re.match(r'^\s*(\d+)\s*[-_ ]', nome)
    return int(m.group(1)) if m else None


def chave_mes(mm_aaaa):
    mm, aa = mm_aaaa.split('_')
    return int(aa) * 100 + int(mm)


def rotulo(chave):
    return f'{MESES_PT[chave % 100 - 1]}/{str(chave // 100)[2:]}'


def rotulo_longo(chave):
    return f'{MESES_PT[chave % 100 - 1].lower()}/{chave // 100}'


def chave_do_rotulo(r):
    nome, aa = r.split('/')
    return (2000 + int(aa)) * 100 + MESES_PT.index(nome) + 1


def meses_entre(ini, fim):
    out, k = [], ini
    while k <= fim:
        out.append(k)
        k = k + 1 if k % 100 < 12 else (k // 100 + 1) * 100 + 1
    return out


def juntar(lista):
    lista = list(lista)
    if len(lista) <= 1:
        return ''.join(lista)
    return ', '.join(lista[:-1]) + ' e ' + lista[-1]


# ---------------------------------------------------------------- bancos

BANCOS_NOME = [  # (banco, palavras no nome do arquivo)
    ('Nubank', ['nubank', 'nu pagamentos', 'nu_', '_nu.', ' nu.', '_nu_', ' nu ', 'nu financeira', 'extrato nu', 'nu.ofx', 'nu.pdf']),
    ('Viacredi/Ailos', ['viacred', 'via cred', 'ailos']),
    ('Sicoob', ['sicoob']),
    ('Sicredi', ['sicredi', 'sicred']),
    ('Itaú', ['itau', 'itaú']),
    ('Santander', ['santander']),
    ('Inter', ['inter']),
    ('Cora', ['cora']),
    ('C6 Bank', ['c6']),
    ('Bradesco', ['bradesco']),
    ('Banco do Brasil', ['banco do brasil', 'bb_', '_bb', ' bb ', 'bb.', 'brasil']),
    ('Caixa', ['caixa', 'cef']),
    ('Mercado Pago', ['mercado pago', 'mercadopago', 'mercado_pago', 'mp_']),
    ('PagBank', ['pagbank', 'pagseguro', 'pag bank']),
    ('InfinitePay', ['infinite', 'infinitepay', 'cloudwalk']),
    ('Stone', ['stone']),
    ('Efí/Gerencianet', ['efi', 'efí', 'gerencianet']),
    ('Rendimento', ['rendimento']),
    ('Asaas', ['asaas']),
    ('Cresol', ['cresol']),
    ('Sisprime', ['sisprime']),
    ('XP Investimentos', ['xp ']),
    ('Bling', ['bling']),
]
BANCOS_CODIGO = {  # código COMPE do OFX -> banco
    '1': 'Banco do Brasil', '33': 'Santander', '77': 'Inter', '104': 'Caixa',
    '237': 'Bradesco', '260': 'Nubank', '341': 'Itaú', '336': 'C6 Bank',
    '748': 'Sicredi', '756': 'Sicoob', '85': 'Viacredi/Ailos', '133': 'Cresol',
    '323': 'Mercado Pago', '290': 'PagBank', '403': 'Cora', '364': 'Efí/Gerencianet',
    '197': 'Stone', '633': 'Rendimento', '461': 'Asaas', '542': 'InfinitePay',
    '84': 'Sisprime', '102': 'XP Investimentos', '348': 'XP Investimentos',
}


def bancos_do_nome(nome):
    n = ' ' + sem_acento(nome).replace('-', ' ') + ' '
    achados = set()
    for banco, palavras in BANCOS_NOME:
        for p in palavras:
            p = sem_acento(p)
            if banco == 'Inter' and re.search(r'\binter\b', n) is None:
                continue
            if banco == 'Cora' and re.search(r'\bcora\b', n) is None:
                continue
            if banco == 'Efí/Gerencianet' and re.search(r'\b(efi|gerencianet)\b', n) is None:
                continue
            if banco == 'Caixa' and re.search(r'\b(caixa|cef)\b', n) is None:
                continue
            if banco == 'C6 Bank' and re.search(r'\bc6', n) is None:
                continue
            if p in n:
                achados.add(banco)
                break
    return achados


def bancos_do_ofx(caminho):
    try:
        with open(caminho, 'rb') as f:
            txt = f.read(8000).decode('latin-1', 'ignore')
    except OSError:
        return set()
    achados = set()
    m = re.search(r'<BANKID>\s*0*(\d+)', txt, re.I)
    if m and m.group(1) in BANCOS_CODIGO:
        achados.add(BANCOS_CODIGO[m.group(1)])
    m = re.search(r'<ORG>\s*([^<\r\n]+)', txt, re.I)
    if m:
        achados |= bancos_do_nome(m.group(1))
    return achados


# ---------------------------------------------------------------- arquivos

EXT_EXTRATO = {'ofx', 'ofc', 'pdf', 'csv', 'xls', 'xlsx', 'zip', 'rar', 'qif', 'txt_banco'}
EXT_IMAGEM = {'png', 'jpg', 'jpeg', 'heic', 'webp', 'gif', 'bmp'}
PALAVRAS_ESCRITORIO = ['razao', 'razão', 'balancete', 'conciliacao', 'conferencia', 'saldo diario',
                       'saldo_diario', 'lancamentos', 'controle de extratos', 'plano de contas',
                       'relatorio de gestao']
PALAVRAS_NAO_LANCAMENTO = ['sped', 'efd', 'ecd', 'ecf', 'reinf', 'dctf', 'sintegra', 'folha', 'dirf',
                           'gfip', 'sefip', 'esocial', 'nfse', 'xml', 'dief', 'dime', 'gia']
PASTAS_FORA = ['folha', 'guia', 'fiscal', 'sped', 'nota', 'xml', 'doc', 'societ', 'certificado', 'relatorio']


def eh_txt_lancamento(nome):
    if not nome.lower().endswith('.txt'):
        return False
    n = sem_acento(nome)
    return not any(p in n for p in PALAVRAS_NAO_LANCAMENTO)


def tipo_arquivo(nome):
    n = sem_acento(nome)
    ext = n.rsplit('.', 1)[-1] if '.' in n else ''
    if ext == 'txt':
        return 'txt' if eh_txt_lancamento(nome) else 'outro'
    if ext in EXT_IMAGEM:
        return 'imagem'
    if n.startswith('~$') or ext in ('ini', 'tmp', 'lnk', 'db'):
        return 'ignorar'
    if any(sem_acento(p) in n for p in PALAVRAS_ESCRITORIO):
        return 'escritorio'
    if ext == 'pdf' and ('comprovante' in n or 'recibo' in n):
        return 'comprovante'
    if ext in EXT_EXTRATO:
        return 'extrato'
    return 'outro'


def listar(pasta):
    """(arquivos, subpastas) de uma pasta, sem erro se não existir."""
    arqs, subs = [], []
    try:
        with os.scandir(pasta) as it:
            for e in it:
                (subs if e.is_dir() else arqs).append(e.name)
    except OSError:
        pass
    return sorted(arqs), sorted(subs)


def arquivos_recursivo(pasta, max_prof=4):
    out = []
    def andar(p, prof, rel):
        a, s = listar(p)
        out.extend((os.path.join(p, x), os.path.join(rel, x) if rel else x) for x in a)
        if prof < max_prof:
            for x in s:
                andar(os.path.join(p, x), prof + 1, os.path.join(rel, x) if rel else x)
    andar(pasta, 0, '')
    return out


def pastas_de_mes(pasta_empresa, max_prof=5):
    """{chave: [caminhos]} de todas as pastas MM_AAAA dentro da empresa."""
    achadas = defaultdict(list)
    def andar(p, prof):
        _, subs = listar(p)
        for s in subs:
            cam = os.path.join(p, s)
            m = re.fullmatch(r'(\d{2})_(\d{4})', s.strip())
            if m and 1 <= int(m.group(1)) <= 12:
                achadas[chave_mes(s.strip())].append(cam)
            if prof < max_prof and not sem_acento(s).startswith(('inativ', 'lixo')):
                andar(cam, prof + 1)
    andar(pasta_empresa, 0)
    return achadas


def examinar_mes(caminhos_mes):
    """Olha a(s) pasta(s) do mês e devolve um dicionário com o que achou."""
    r = {'tem_extrato_pasta': False, 'arquivos': [], 'extratos': [], 'imagens': [], 'escritorio': [],
         'comprovantes': [], 'txts': [], 'bancos': set(), 'sem_bancos': 0}
    for cam in caminhos_mes:
        _, subs = listar(cam)
        pastas_extrato = [os.path.join(cam, s) for s in subs if sem_acento(s).startswith('extrato')]
        # pasta duplicada 08_2026/08_2026/Extrato
        for s in subs:
            if re.fullmatch(r'\d{2}_\d{4}', s.strip()):
                _, subs2 = listar(os.path.join(cam, s))
                pastas_extrato += [os.path.join(cam, s, x) for x in subs2 if sem_acento(x).startswith('extrato')]
        for pe in pastas_extrato:
            r['tem_extrato_pasta'] = True
            for completo, rel in arquivos_recursivo(pe):
                t = tipo_arquivo(rel)
                if t == 'ignorar':
                    continue
                r['arquivos'].append(rel)
                if t == 'extrato':
                    r['extratos'].append(rel)
                    b = bancos_do_nome(rel)
                    if rel.lower().endswith(('.ofx', '.ofc')):
                        b |= bancos_do_ofx(completo)
                    if b:
                        r['bancos'] |= b
                    else:
                        r['sem_bancos'] += 1
                elif t == 'txt':
                    r['txts'].append(rel)
                elif t == 'imagem':
                    r['imagens'].append(rel)
                elif t == 'escritorio':
                    r['escritorio'].append(rel)
                elif t == 'comprovante':
                    r['comprovantes'].append(rel)
        # TXT de lançamento fora da pasta Extrato (na pasta do mês ou subpastas que não sejam folha/fiscal)
        for completo, rel in arquivos_recursivo(cam, 2):
            partes = [sem_acento(p) for p in rel.replace('\\', '/').split('/')[:-1]]
            if partes and partes[0].startswith('extrato'):
                continue
            if any(any(pf in p for pf in PASTAS_FORA) for p in partes):
                continue
            if eh_txt_lancamento(rel):
                r['txts'].append(rel)
    return r


# ---------------------------------------------------------------- planilha base

def ler_base(caminho):
    wb = openpyxl.load_workbook(caminho, data_only=True)
    base = {'empresas': [], 'detalhes': {}, 'lanc': {}, 'bancos': defaultdict(list), 'mensagens': {},
            'situacoes': [], 'meses': []}
    ws = wb['Resumo']
    cab = [c.value for c in ws[1]]
    base['meses'] = [chave_do_rotulo(c) for c in cab if c and re.fullmatch(r'[A-Za-zçÇ]+/\d\d', str(c))]
    for row in ws.iter_rows(min_row=2, values_only=True):
        if row[1] is None:
            continue
        base['empresas'].append({'grupo': row[0], 'cod': int(row[1]), 'empresa': row[2], 'pasta': row[3],
                                 'obs_base': row[cab.index('Observações')] if 'Observações' in cab else None,
                                 'bancos_rotina': row[cab.index('Bancos na Rotina')] if 'Bancos na Rotina' in cab else None})
    ws = wb['Lançamentos']
    cab = [c.value for c in ws[1]]
    for row in ws.iter_rows(min_row=2, values_only=True):
        if row[1] is None:
            continue
        k = (row[0], int(row[1]))
        base['lanc'][k] = {'skill': row[3]}
        for i, c in enumerate(cab):
            if c and re.fullmatch(r'[A-Za-zçÇ]+/\d\d', str(c)):
                base['lanc'][k][chave_do_rotulo(c)] = row[i]
    # Detalhes: (cod, empresa, mês) -> (status, motivo)
    for row in wb['Detalhes'].iter_rows(min_row=2, values_only=True):
        if row[0] is None:
            continue
        base['detalhes'][(int(row[0]), row[1], chave_do_rotulo(row[2]))] = (row[3], row[4])
    for row in wb['Por banco'].iter_rows(min_row=2, values_only=True):
        if row[0] is None:
            continue
        base['bancos'][(int(row[0]), row[1])].append({'extrato': row[2], 'status_rotina': row[3], 'banco': row[4]})
    if 'Mensagens' in wb.sheetnames:
        for row in wb['Mensagens'].iter_rows(min_row=2, values_only=True):
            if row[0] is None:
                continue
            base['mensagens'][(int(row[0]), row[1])] = {'meses': row[2], 'enviado': row[4], 'data': row[5]}
    # Situações informadas do Painel
    ws = wb['Painel']
    lendo = False
    for row in ws.iter_rows(values_only=True):
        if row[0] == 'Situações informadas':
            lendo = True
            continue
        if lendo and row[0] is not None and row[1]:
            base['situacoes'].append((row[0], row[1]))
        elif lendo and row[0] is None:
            break
    return base


MOTIVOS_MANUAIS = ('confirmado', 'conferido', 'print', 'informad', 'exigido a partir', 'sem movimentação bancária',
                   'conta bancária aberta', 'sem movimento')


def eh_manual(motivo):
    return bool(motivo) and any(p in sem_acento(motivo) for p in map(sem_acento, MOTIVOS_MANUAIS))


# ---------------------------------------------------------------- principal

def localizar_raizes(contabilidade):
    _, subs = listar(contabilidade)
    raizes = []
    for s in subs:
        if sem_acento(s).startswith('arquivos'):
            grupo = None
            for trecho, g in GRUPO_DA_RAIZ.items():
                if re.search(r'\b' + trecho.lower() + r'\b', sem_acento(s)):
                    grupo = g
                    break
            raizes.append((os.path.join(contabilidade, s), grupo or s.upper()))
    return raizes


def indexar_empresas(raizes):
    idx = []  # (grupo, numero, nome_pasta, caminho)
    for raiz, grupo in raizes:
        _, subs = listar(raiz)
        for s in subs:
            n = numero_empresa(s)
            if n is not None:
                idx.append((grupo, n, s, os.path.join(raiz, s)))
    return idx


def achar_pasta(emp, idx):
    nome = (emp['pasta'] or '').strip()
    exatas = [x for x in idx if x[2].strip() == nome]
    if exatas:
        mesmo_grupo = [x for x in exatas if x[0] == emp['grupo']]
        return (mesmo_grupo or exatas)[0]
    cands = [x for x in idx if x[1] == emp['cod'] and x[0] == emp['grupo']]
    if not cands:
        return None
    pal = set(re.findall(r'[a-z]{3,}', sem_acento(emp['empresa'] + ' ' + nome)))
    cands.sort(key=lambda x: -len(pal & set(re.findall(r'[a-z]{3,}', sem_acento(x[2])))))
    return cands[0]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--contabilidade', required=True, help='pasta que contém "Arquivos ROF Dominio", "Arquivos RENATA Dominio"...')
    ap.add_argument('--base', required=True, help='planilha de controle anterior')
    ap.add_argument('--saida', required=True)
    ap.add_argument('--inicio', help='MM_AAAA (padrão: o 1º mês da planilha base)')
    ap.add_argument('--fim', help='MM_AAAA (padrão: o mês anterior ao atual)')
    ap.add_argument('--ajustes', help='JSON com ajustes informados pela usuária')
    ap.add_argument('--hoje', help='AAAA-MM-DD (padrão: hoje)')
    a = ap.parse_args()

    hoje = dt.date.fromisoformat(a.hoje) if a.hoje else dt.date.today()
    base = ler_base(a.base)
    ini = chave_mes(a.inicio) if a.inicio else min(base['meses'])
    if a.fim:
        fim = chave_mes(a.fim)
    else:
        fim = hoje.year * 100 + hoje.month - 1 if hoje.month > 1 else (hoje.year - 1) * 100 + 12
    meses = meses_entre(ini, fim)

    with open(os.path.join(AQUI, '..', 'references', 'skills_empresas.json'), encoding='utf-8') as f:
        mapa_skills = {k: v for k, v in json.load(f).items() if not k.startswith('_')}
    ajustes = {}
    if a.ajustes:
        with open(a.ajustes, encoding='utf-8') as f:
            ajustes = json.load(f)

    raizes = localizar_raizes(a.contabilidade)
    if not raizes:
        sys.exit(f'ERRO: nenhuma pasta "Arquivos ..." em {a.contabilidade}')
    idx = indexar_empresas(raizes)

    empresas = [dict(e) for e in base['empresas']]
    usados = set()
    for e in empresas:
        p = achar_pasta(e, idx)
        e['caminho'] = p[3] if p else None
        if p:
            e['pasta'] = p[2]
            usados.add(p[3])
    # empresas novas (pasta numerada no Drive que não está na planilha)
    conhecidos = {(e['grupo'], e['cod']) for e in empresas}
    for grupo, n, nome, cam in idx:
        if cam in usados or (grupo, n) in conhecidos:
            continue
        nome_emp = re.sub(r'^\s*\d+\s*[-_ ]+\s*', '', nome).upper()
        empresas.append({'grupo': grupo, 'cod': n, 'empresa': nome_emp, 'pasta': nome, 'caminho': cam,
                         'nova': True, 'bancos_rotina': None, 'obs_base': None})
        conhecidos.add((grupo, n))
    for nv in ajustes.get('empresas_novas', []):
        if (nv['grupo'], nv['cod']) not in conhecidos:
            empresas.append({'grupo': nv['grupo'], 'cod': nv['cod'], 'empresa': nv['empresa'],
                             'pasta': 'não encontrada', 'caminho': None, 'nova': True,
                             'bancos_rotina': ', '.join(nv.get('bancos', [])) or None, 'obs_base': None})

    # ajustes por empresa
    aj_emp = defaultdict(dict)
    for item in ajustes.get('empresas', []):
        aj_emp[(item.get('grupo'), int(item['cod']))] = item

    def aj(e):
        return aj_emp.get((e['grupo'], e['cod'])) or aj_emp.get((None, e['cod'])) or {}

    det, lanc, porbanco, arquivos = {}, {}, [], []
    for e in empresas:
        k = (e['grupo'], e['cod'])
        a_e = aj(e)
        # bancos da Rotina (da planilha anterior + ajustes)
        linhas_banco = list(base['bancos'].get((e['cod'], e['empresa']), []))
        for b in a_e.get('bancos_novos', []):
            linhas_banco.append({'extrato': f'Extrato bancario {b}', 'status_rotina': None, 'banco': b})
        for b in a_e.get('bancos_encerrados', []):
            linhas_banco = [l for l in linhas_banco if l['banco'] != b]
        e['linhas_banco'] = linhas_banco
        bancos_rotina = [l['banco'] for l in linhas_banco if l['banco'] and sem_acento(l['status_rotina'] or '') != 's/mov']
        if linhas_banco:
            e['bancos_rotina'] = ', '.join(dict.fromkeys(l['banco'] for l in linhas_banco if l['banco']))
        todas_smov = bool(linhas_banco) and all(sem_acento(l['status_rotina'] or '') == 's/mov' for l in linhas_banco)

        pm = pastas_de_mes(e['caminho']) if e['caminho'] else {}
        primeiro = min(pm) if pm else None
        inicio_inf = chave_mes(a_e['inicio']) if a_e.get('inicio') else None
        ultimo_base = max(base['meses'])
        for mes in meses:
            info = examinar_mes(pm.get(mes, [])) if mes in pm else None
            b_status, b_motivo = base['detalhes'].get((e['cod'], e['empresa'], mes), (None, None))
            bancos_achados = sorted(info['bancos']) if info else []
            if info:
                arquivos += [(e['cod'], e['empresa'], rotulo(mes), x) for x in info['arquivos']]
            # --- status do extrato
            if e['caminho'] is None:
                if sem_acento(e.get('pasta') or '').startswith('inativ'):
                    st, mot = '—', 'pasta da empresa em INATIVAS'
                else:
                    st, mot = '—', 'empresa nova, ainda sem pasta no Drive (conta a partir da 1ª pasta de mês criada)'
            elif info is None:
                if primeiro is None or mes < primeiro:
                    st, mot = '—', 'sem pasta do mês no Drive (ainda não era cliente ou pastas criadas depois)'
                else:
                    st, mot = 'FALTANDO', 'pasta do mês não criada'
            elif not info['tem_extrato_pasta']:
                st, mot = ('Recebido', 'já lançado (TXT do escritório na pasta); sem pasta Extrato') if info['txts'] \
                    else ('FALTANDO', 'sem pasta Extrato')
            elif info['extratos']:
                st, mot = 'Recebido', None
            elif info['txts']:
                st, mot = 'Recebido', 'já lançado (TXT do escritório na pasta); extrato original não está na pasta'
            elif info['imagens'] or info['comprovantes']:
                st, mot = 'Verificar', 'só imagem/comprovante na pasta Extrato'
            elif info['escritorio']:
                st, mot = 'Verificar', 'só arquivos gerados pelo escritório na pasta Extrato'
            elif info['arquivos']:
                st, mot = 'Verificar', 'arquivos que não parecem extrato na pasta Extrato'
            else:
                st, mot = 'FALTANDO', 'pasta Extrato vazia'
            # --- o que veio da planilha anterior / informado pela usuária
            if b_status == st and eh_manual(b_motivo):
                mot = b_motivo
            elif st != 'Recebido' and b_status and eh_manual(b_motivo):
                st, mot = b_status, b_motivo
            elif st != 'Recebido' and b_motivo == 'marcada S/MOV na Rotina':
                st, mot = 'S/MOV', b_motivo
            elif st in ('FALTANDO', '—') and mes > ultimo_base and (todas_smov or base['detalhes'].get(
                    (e['cod'], e['empresa'], ultimo_base), (None, None))[1] == 'marcada S/MOV na Rotina'):
                st, mot = 'S/MOV', 'marcada S/MOV na Rotina'
            elif st == 'FALTANDO' and b_status == 'Recebido':
                mot = f'{mot} (no controle anterior estava Recebido — conferir)'
            if inicio_inf and mes < inicio_inf:
                st, mot = '—', f'início informado: {a_e["inicio"]}'
            for s in a_e.get('sem_movimento', []):
                if mes in [chave_mes(x) for x in s.get('meses', [])] or \
                        (s.get('ate') and mes <= chave_mes(s['ate']) and (not s.get('de') or mes >= chave_mes(s['de']))):
                    st, mot = 'S/MOV', s.get('motivo', 'sem movimento informado')
            for s in a_e.get('status', []):
                if chave_mes(s['mes']) == mes:
                    st, mot = s['status'], s.get('motivo', 'informado pela usuária')
            nao_vistos = [b for b in dict.fromkeys(bancos_rotina) if b not in info['bancos']] if info and st == 'Recebido' else []
            det[(k, mes)] = {'status': st, 'motivo': mot, 'achados': ', '.join(bancos_achados) or None,
                             'nao_vistos': ', '.join(nao_vistos) or None, 'info': info}
            # --- lançamento
            b_l = base['lanc'].get(k, {}).get(mes)
            lancado = bool(info and info['txts']) or b_l == 'Já lançado' or \
                any(chave_mes(x) == mes for x in a_e.get('lancados', []))
            if lancado:
                ls = 'Já lançado'
            else:
                ls = {'Recebido': 'Pronto para lançar', 'FALTANDO': 'Falta extrato', 'Verificar': 'Verificar extrato',
                      'S/MOV': 'S/MOV', '—': '—'}.get(st, st)
            lanc[(k, mes)] = ls
        # --- por banco
        for l in linhas_banco:
            linha = [e['cod'], e['empresa'], l['extrato'], l['status_rotina'], l['banco']]
            for mes in meses:
                d = det[(k, mes)]
                if sem_acento(l['status_rotina'] or '') == 's/mov':
                    v = 'S/MOV'
                elif d['status'] != 'Recebido' or d['info'] is None:
                    v = d['status']
                elif l['banco'] in d['info']['bancos']:
                    v = 'Recebido'
                elif not d['info']['extratos'] and d['info']['txts']:
                    v = 'Já lançado (TXT)'
                elif d['info']['sem_bancos']:
                    v = 'Verificar — nome do arquivo não indica o banco'
                else:
                    v = 'FALTANDO'
                linha.append(v)
            porbanco.append(linha)

    gravar(a.saida, empresas, meses, det, lanc, porbanco, arquivos, base, mapa_skills, ajustes, hoje)
    # resumo no terminal
    print(f'Planilha gerada: {a.saida}')
    print(f'Meses: {rotulo(meses[0])} a {rotulo(meses[-1])} | empresas: {len(empresas)} | raízes: ' +
          ', '.join(os.path.basename(r) for r, _ in raizes))
    for mes in meses[-2:]:
        c = Counter(det[((e['grupo'], e['cod']), mes)]['status'] for e in empresas)
        cl = Counter(lanc[((e['grupo'], e['cod']), mes)] for e in empresas)
        print(f'  {rotulo(mes)}: ' + ', '.join(f'{k}={v}' for k, v in c.most_common()) +
              ' | ' + ', '.join(f'{k}={v}' for k, v in cl.most_common()))
    novas = [e for e in empresas if e.get('nova')]
    if novas:
        print('Empresas novas: ' + '; '.join(f"{e['cod']} {e['empresa']}" for e in novas))
    sem_pasta = [e for e in empresas if not e['caminho'] and not e.get('nova')]
    if sem_pasta:
        print('Sem pasta no Drive: ' + '; '.join(f"{e['cod']} {e['empresa']}" for e in sem_pasta))


# ---------------------------------------------------------------- gravação

CORES = {'Recebido': 'C6EFCE', 'Já lançado': 'C6EFCE', 'FALTANDO': 'FFC7CE', 'Falta extrato': 'FFC7CE',
         'Verificar': 'FFEB9C', 'Verificar extrato': 'FFEB9C', 'Pronto para lançar': 'BDD7EE',
         'S/MOV': 'D9D9D9', '—': 'EDEDED', 'Já lançado (TXT)': 'C6EFCE', 'Sim': 'C6EFCE', 'Não': 'FFC7CE'}
CAB_FILL = PatternFill('solid', fgColor='1F4E78')
CAB_FONT = Font(bold=True, color='FFFFFF')


def cor(c):
    v = c.value
    if isinstance(v, str):
        chave = 'Verificar' if v.startswith('Verificar —') else v
        if chave in CORES:
            c.fill = PatternFill('solid', fgColor=CORES[chave])


def aba(wb, titulo, cab, linhas, larguras, colorir=(), quebra=()):
    ws = wb.create_sheet(titulo)
    ws.append(cab)
    for c in ws[1]:
        c.fill, c.font = CAB_FILL, CAB_FONT
        c.alignment = Alignment(wrap_text=True, vertical='center')
    for l in linhas:
        ws.append(l)
    for i, w in enumerate(larguras, 1):
        ws.column_dimensions[get_column_letter(i)].width = w
    for row in ws.iter_rows(min_row=2):
        for c in row:
            if c.column - 1 in colorir:
                cor(c)
            if c.column - 1 in quebra:
                c.alignment = Alignment(wrap_text=True, vertical='top')
    ws.freeze_panes = 'A2'
    ws.auto_filter.ref = f'A1:{get_column_letter(len(cab))}{max(1, ws.max_row)}'
    return ws


def nome_bonito(s):
    t = str(s).title()
    return re.sub(r"\bLtda\b", 'Ltda', t)


def gravar(saida, empresas, meses, det, lanc, porbanco, arquivos, base, mapa_skills, ajustes, hoje):
    wb = openpyxl.Workbook()
    wb.remove(wb.active)
    rot = [rotulo(m) for m in meses]
    nm = len(meses)
    col_m = range(4, 4 + nm)

    def skill_de(e):
        return mapa_skills.get(f"{e['grupo']}|{e['cod']}") or base['lanc'].get((e['grupo'], e['cod']), {}).get('skill')

    # Painel ------------------------------------------------------------
    ws = wb.create_sheet('Painel')
    ws.append([f'Conferência de extratos — gerado em {hoje.isoformat()}'])
    ws['A1'].font = Font(bold=True, size=14)
    ws.append([])
    ws.append(['Mês', 'Recebido', 'FALTANDO', 'Verificar', 'S/MOV', '—', 'Total'])
    for m in meses:
        c = Counter(det[((e['grupo'], e['cod']), m)]['status'] for e in empresas)
        ws.append([rotulo(m), c['Recebido'], c['FALTANDO'], c['Verificar'], c['S/MOV'], c['—'], len(empresas)])
    ws.append([])
    ws.append(['Lançamento', 'Já lançado', 'Para lançar', 'Falta extrato', 'Verificar', 'S/MOV', '—'])
    for m in meses:
        c = Counter(lanc[((e['grupo'], e['cod']), m)] for e in empresas)
        ws.append([rotulo(m), c['Já lançado'], c['Pronto para lançar'], c['Falta extrato'], c['Verificar extrato'],
                   c['S/MOV'], c['—']])
    for row in ws.iter_rows():
        if row[0].value in ('Mês', 'Lançamento'):
            for c in row[:7]:
                c.fill, c.font = CAB_FILL, CAB_FONT
    ws.append([])
    ws.append(['Legenda'])
    ws.cell(ws.max_row, 1).font = Font(bold=True)
    for k, v in [('Recebido', 'extrato (OFX/PDF/CSV/XLS) na pasta Extrato do mês, ou já lançado/conciliado pelo escritório'),
                 ('FALTANDO', 'pasta Extrato vazia, sem pasta Extrato ou pasta do mês não criada — pedir ao cliente'),
                 ('Verificar', 'só imagem/comprovante ou só arquivos gerados pelo escritório'),
                 ('S/MOV', 'contas marcadas S/MOV na Rotina, ou print do banco na pasta dizendo que o período não teve movimento'),
                 ('—', 'antes do 1º mês da empresa: pasta do mês ainda não criada, empresa nova sem pasta, ou início informado'),
                 ('Já lançado', 'TXT de lançamento do escritório na pasta do mês (SPED, EFD, folha etc. não contam), ou confirmado pela Rosangela'),
                 ('Pronto para lançar', 'extrato na pasta e ainda sem TXT de lançamento')]:
        ws.append([k, v])
        cor(ws.cell(ws.max_row, 1))
    ws.append([])
    ws.append(['Situações informadas'])
    ws.cell(ws.max_row, 1).font = Font(bold=True)
    sits = list(base['situacoes']) + [(s.get('cod', ''), s['texto']) for s in ajustes.get('situacoes', [])]
    for s in dict.fromkeys(sits):
        ws.append(list(s))
    ws.column_dimensions['A'].width = 16
    for col in 'BCDEFG':
        ws.column_dimensions[col].width = 12

    # Resumo ------------------------------------------------------------
    linhas = []
    for e in empresas:
        k = (e['grupo'], e['cod'])
        sts = [det[(k, m)]['status'] for m in meses]
        falt = [rotulo(m) for m in meses if det[(k, m)]['status'] == 'FALTANDO']
        obs = ' | '.join(f"{rotulo(m)}: {det[(k, m)]['motivo']}" for m in meses
                         if det[(k, m)]['status'] in ('FALTANDO', 'Verificar') and det[(k, m)]['motivo'])
        if e.get('nova'):
            obs = ('EMPRESA NOVA no Drive — conferir na Rotina. ' + obs).strip(' |')
        linhas.append([e['grupo'], e['cod'], e['empresa'], e['pasta'] if e['caminho'] or e.get('pasta') else 'não encontrada',
                       *sts, ', '.join(falt) or None, obs or None, e.get('bancos_rotina')])
    aba(wb, 'Resumo', ['Grupo', 'Cód.', 'Empresa (Rotina)', 'Pasta no Drive', *rot, 'Meses faltando', 'Observações',
                       'Bancos na Rotina'], linhas, [14, 6, 34, 30] + [12] * nm + [22, 60, 30],
        colorir=set(range(4, 4 + nm)), quebra={4 + nm + 1})

    # Lançamentos -------------------------------------------------------
    linhas = []
    for e in empresas:
        k = (e['grupo'], e['cod'])
        ls = [lanc[(k, m)] for m in meses]
        linhas.append([e['grupo'], e['cod'], e['empresa'], skill_de(e), *ls,
                       ', '.join(rotulo(m) for m in meses if lanc[(k, m)] == 'Pronto para lançar') or None,
                       ', '.join(rotulo(m) for m in meses if lanc[(k, m)] == 'Falta extrato') or None,
                       ', '.join(rotulo(m) for m in meses if lanc[(k, m)] == 'Já lançado') or None])
    aba(wb, 'Lançamentos', ['Grupo', 'Cód.', 'Empresa', 'Skill', *rot, 'Para lançar (extrato na pasta)',
                            'Falta o cliente enviar', 'Já lançados'], linhas, [14, 6, 32, 30] + [14] * nm + [30, 30, 40],
        colorir=set(range(4, 4 + nm)), quebra={4 + nm, 5 + nm, 6 + nm})

    # Skills prontas ----------------------------------------------------
    linhas = []
    for e in empresas:
        s = skill_de(e)
        if not s:
            continue
        k = (e['grupo'], e['cod'])
        ls = [lanc[(k, m)] for m in meses]
        linhas.append([e['cod'], e['empresa'], s, *ls,
                       ', '.join(rotulo(m) for m in meses if lanc[(k, m)] == 'Pronto para lançar') or None])
    aba(wb, 'Skills prontas', ['Cód.', 'Empresa', 'Skill', *rot, 'Fazer juntos (extrato na pasta, não lançado)'],
        linhas, [6, 30, 36] + [16] * nm + [40], colorir=set(range(3, 3 + nm)), quebra={3 + nm})

    # Detalhes ----------------------------------------------------------
    linhas = []
    for e in empresas:
        k = (e['grupo'], e['cod'])
        for m in meses:
            d = det[(k, m)]
            linhas.append([e['cod'], e['empresa'], rotulo(m), d['status'], d['motivo'], d['achados'], d['nao_vistos']])
    aba(wb, 'Detalhes', ['Cód.', 'Empresa', 'Mês', 'Status', 'Motivo', 'Bancos achados', 'Bancos da Rotina não vistos'],
        linhas, [6, 32, 12, 12, 60, 34, 30], colorir={3})

    # Por banco ---------------------------------------------------------
    aba(wb, 'Por banco', ['Cód.', 'Empresa', 'Extrato (Rotina)', 'Status na Rotina', 'Banco reconhecido', *rot],
        porbanco, [6, 32, 40, 14, 18] + [16] * nm, colorir=set(range(5, 5 + nm)))

    # Mensagens ---------------------------------------------------------
    linhas = []
    for e in empresas:
        k = (e['grupo'], e['cod'])
        falt = [m for m in meses if det[(k, m)]['status'] == 'FALTANDO']
        if not falt:
            continue
        itens = []
        for l in e.get('linhas_banco', []):
            if sem_acento(l['status_rotina'] or '') == 's/mov' or not l['banco']:
                continue
            if 'aplica' in sem_acento(l['extrato'] or ''):
                itens.append(f"• Extrato da *aplicação financeira* no *{l['banco']}*")
            else:
                itens.append(f"• Extrato da conta *{l['banco']}*")
        itens = list(dict.fromkeys(itens)) or ['• Extratos de todas as contas bancárias da empresa']
        meses_txt = juntar([rotulo_longo(m) for m in falt])
        msg = (f"Olá, bom dia! Não identificamos o envio dos extratos bancários da *{nome_bonito(e['empresa'])}* "
               f"referentes a *{meses_txt}*:\n" + '\n'.join(itens) +
               "\n⚠️ O envio dos extratos nos formatos *PDF e OFX* é de *extrema importância* para o correto "
               "lançamento e a conciliação bancária da contabilidade. Se a empresa tiver outras contas ou "
               "aplicações financeiras, pedimos que envie também. Obrigada!")
        meses_pend = ', '.join(rotulo(m) for m in falt)
        ant = base['mensagens'].get((e['cod'], e['empresa']))
        enviado, data = ('Não', None)
        if ant and ant['meses'] == meses_pend:
            enviado, data = ant['enviado'] or 'Não', ant['data']
        linhas.append([e['cod'], e['empresa'], meses_pend, msg, enviado, data])
    ws = aba(wb, 'Mensagens', ['Cód.', 'Empresa', 'Meses pendentes', 'Mensagem (copiar e colar no WhatsApp)',
                               'Enviado?', 'Data envio'], linhas, [6, 30, 18, 90, 10, 12], colorir={4}, quebra={2, 3})
    from openpyxl.worksheet.datavalidation import DataValidation
    dv = DataValidation(type='list', formula1='"Sim,Não"', allow_blank=True)
    ws.add_data_validation(dv)
    if ws.max_row > 1:
        dv.add(f'E2:E{ws.max_row}')

    # Arquivos encontrados ---------------------------------------------
    aba(wb, 'Arquivos encontrados', ['Cód.', 'Empresa', 'Mês', 'Arquivo'], arquivos, [6, 32, 12, 70])
    wb.save(saida)


if __name__ == '__main__':
    main()
