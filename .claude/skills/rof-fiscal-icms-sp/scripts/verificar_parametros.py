"""Atualização obrigatória ANTES de cada conferência: consulta as fontes OFICIAIS da SEFAZ-SP e compara com a base
gravada da última verificação. Mostra só o que MUDOU - não precisa reler tudo.

python3 verificar_parametros.py                         # verifica tudo e compara com a base
python3 verificar_parametros.py --cest 01.075.00 --ncm 87084090 --data 2026-10-06   # + ST do produto na data
python3 verificar_parametros.py --gravar-base           # só depois que a analista conferiu as mudanças

Status: OK (igual à base e regras-chave presentes) | MUDOU (texto oficial diferente: ler as linhas mostradas e
revisar a skill) | REGRA? (texto não tem mais a frase-chave: a regra pode ter mudado) | FALHOU (sem acesso: NÃO afirmar
o parâmetro sem verificar - avisar a analista).
"""
import difflib, hashlib, html, json, os, re, sys, unicodedata, urllib.request
from datetime import date

AQUI = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.join(AQUI, '..', 'referencias', 'base_oficial')
BASE_JSON = os.path.join(BASE_DIR, 'base.json')
LEG = 'https://legislacao.fazenda.sp.gov.br/Paginas/'

FONTES = {
    'RICMS': LEG + 'textoricms.aspx',
    'CAT68': LEG + 'Portaria-CAT-68-de-2019.aspx',
    'DARE': 'https://portal.fazenda.sp.gov.br/servicos/cficms/paginas/como-pagar-valor-total-ou-parcial-%20dare%20icms.aspx',
}

# parâmetro -> (fonte, extrator, frases que TÊM de estar no texto, o que a regra significa para a skill)
PARAMETROS = [
    ('RICMS art. 2º (XVI e §6º - fato gerador do Simples)', 'RICMS', ('artigo', '2º'),
     ['XVI - na entrada em estabelecimento de contribuinte sujeito às normas do Regime',
      'diferença de cargas tributárias'],
     'Simples paga diferencial em toda entrada de mercadoria de outra UF'),
    ('RICMS art. 52 (alíquota interna 18%)', 'RICMS', ('artigo', '52'),
     ['18% (dezoito por cento)'], 'Alíquota interna padrão 18%'),
    ('RICMS art. 115 (XV-A prazo e cálculo do Simples, §8º 4%/12%)', 'RICMS', ('artigo', '115'),
     ['até o último dia do segundo mês subsequente ao da entrada',
      'industrialização ou comercialização, material de uso e consumo ou bem do ativo permanente',
      '4% (quatro por cento), nas operações com mercadorias abrangidas pela Resolução'],
     'Prazo: último dia do 2º mês após a entrada; qualquer destinação; 4% importado / 12% demais'),
    ('RICMS art. 117 (DIFAL RPA)', 'RICMS', ('artigo', '117'), ['uso, consumo ou integração no ativo imobilizado'],
     'RPA: DIFAL em uso/consumo/ativo'),
    ('RICMS art. 313-O (ST autopeças)', 'RICMS', ('artigo', '313-O'), ['autopeças indicadas em'],
     'ST de autopeças depende da portaria (CAT 68/19 Anexo XIV)'),
    ('RICMS art. 426-A (antecipação na entrada)', 'RICMS', ('artigo', '426-A'), ['antecipação'],
     'Antecipação na entrada p/ medicamentos, bebidas, perfumaria, higiene e limpeza'),
    ('Portaria CAT 68/19 - anexos de ST e revogações', 'CAT68', ('anexos',), ['ANEXO XIV'],
     'Lista de segmentos com ST em SP (anexo revogado = sem ST)'),
    ('DARE-SP - códigos do Simples', 'DARE', ('dare',),
     ['04602', 'Diferencial de Alíquota (DeSTDA - DIF) - Simples Nacional', '14603'],
     'Simples: diferencial 046-2/04602; antecipação ST 146-6/14603'),
]

_cache = {}


def baixar(nome):
    if nome not in _cache:
        erro = None
        for tentativa in range(4):  # a página do RICMS tem ~8 MB e às vezes chega cortada
            try:
                req = urllib.request.Request(FONTES[nome], headers={'User-Agent': 'Mozilla/5.0'})
                with urllib.request.urlopen(req, timeout=180) as r:
                    t = r.read().decode('utf-8', errors='ignore')
                break
            except Exception as e:
                erro = e
        else:
            raise erro
        t = re.sub(r'<(script|style)[^>]*>.*?</\1>', '', t, flags=re.S)
        t = re.sub(r'<br\s*/?>|</p>|</div>|</tr>|</li>', '\n', t)
        t = re.sub(r'</td>', ' | ', t)
        t = html.unescape(re.sub(r'<[^>]+>', '', t))
        t = re.sub(r'[ \t​\xa0]+', ' ', t)
        t = re.sub(r'\n\s*\n+', '\n', t)
        _cache[nome] = t
    return _cache[nome]


def extrair(texto, ext):
    if ext[0] == 'artigo':
        n = re.escape(ext[1])
        m = re.search(rf'\n\s*Artigo {n} -', texto)
        if not m:
            return None
        fim = re.search(rf'\n\s*Artigo (?!{n} -)[0-9][0-9A-Z\-º]* -', texto[m.end():])
        return texto[m.start():m.end() + (fim.start() if fim else 20000)].strip()
    if ext[0] == 'anexos':  # cabeçalhos dos anexos (com nota de revogação) + título do segmento
        out = []
        for m in re.finditer(r'\nANEXO [IVXL]+\b[^\n]*\n[^\n]*\n[^\n]*', texto):
            out.append(' '.join(m.group(0).split()))
        return '\n'.join(out)
    if ext[0] == 'dare':
        linhas = [l.strip() for l in texto.split('\n') if re.search(r'\b\d{3}-\d\b|\b\d{5}\b|Simples Nacional', l)]
        i = next((k for k, l in enumerate(linhas) if 'novos códigos' in l), 0)
        return '\n'.join(' '.join(l.split()) for l in linhas[i:i + 60])
    return None


def norm(s):
    return '\n'.join(' '.join(l.split()) for l in s.split('\n') if l.strip())


def verificar(gravar=False):
    os.makedirs(BASE_DIR, exist_ok=True)
    base = json.load(open(BASE_JSON, encoding='utf-8')) if os.path.exists(BASE_JSON) else {}
    nova = dict(base); res = []
    for nome, fonte, ext, chaves, sentido in PARAMETROS:
        ascii_ = unicodedata.normalize('NFKD', nome).encode('ascii', 'ignore').decode()
        arq = os.path.join(BASE_DIR, re.sub(r'[^A-Za-z0-9]+', '_', ascii_).strip('_')[:60] + '.txt')
        try:
            bloco = extrair(baixar(fonte), ext)
            if not bloco:
                res.append(('FALHOU', nome, 'trecho não encontrado na página oficial (layout mudou?)', [])); continue
        except Exception as e:
            res.append(('FALHOU', nome, f'sem acesso à fonte oficial ({e.__class__.__name__}: {e})', [])); continue
        bloco = norm(bloco)
        h = hashlib.sha256(bloco.encode()).hexdigest()
        faltam = [c for c in chaves if ' '.join(c.split()) not in bloco]
        antigo = base.get(nome)
        diff = []
        if antigo and antigo['hash'] != h and os.path.exists(arq):
            velho = open(arq, encoding='utf-8').read().split('\n')
            diff = [l for l in difflib.unified_diff(velho, bloco.split('\n'), lineterm='', n=0)
                    if l[:1] in '+-' and not l.startswith(('+++', '---'))]
        if faltam:
            st = 'REGRA?'; obs = 'frase-chave sumiu do texto oficial: ' + ' | '.join(faltam)
        elif not antigo:
            st = 'NOVO'; obs = 'sem base anterior - gravar base depois de conferir'
        elif antigo['hash'] != h:
            st = 'MUDOU'; obs = f"texto oficial mudou desde {antigo['data']} - ler as linhas alteradas"
        else:
            st = 'OK'; obs = f"igual à verificação de {antigo['data']} - {sentido}"
        res.append((st, nome, obs, diff))
        if gravar:
            open(arq, 'w', encoding='utf-8').write(bloco)
            nova[nome] = {'hash': h, 'data': date.today().isoformat(), 'fonte': FONTES[fonte]}
    if gravar:
        json.dump(nova, open(BASE_JSON, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    return res


def st_do_produto(cest, ncm, data_iso):
    """Procura o CEST/NCM nos anexos da Portaria CAT 68/19 e diz se o anexo está revogado na data."""
    t = baixar('CAT68')
    cab = [(m.start(), ' '.join(m.group(0).split())) for m in re.finditer(r'\nANEXO [IVXL]+\b[^\n]*\n[^\n]*\n[^\n]*', t)]
    alvos = [x for x in [cest, ncm[:4] if ncm else None] if x]
    achados = []
    for alvo in alvos:
        for m in re.finditer(re.escape(alvo), t):
            anexo = max([c for c in cab if c[0] < m.start()], default=(0, '?'))[1]
            achados.append((alvo, anexo, ' '.join(t[m.start() - 60:m.start() + 140].split())))
    if not achados:
        return [f'{cest or ncm}: não aparece em nenhum anexo da CAT 68/19 -> sem ST em SP (conferir CEST/NCM)']
    out, vistos = [], set()
    for alvo, anexo, trecho in achados:
        if (alvo, anexo) in vistos:
            continue
        vistos.add((alvo, anexo))
        rev = re.search(r'revogado[^;)]*?em vigor em (\d{1,2})º? de (\w+) de (\d{4})', anexo)
        situ = 'ANEXO VIGENTE -> produto COM ST em SP' if 'revogado' not in anexo.lower() else \
            f'anexo REVOGADO ({rev.group(0) if rev else "ver data"}) -> sem ST a partir dessa data'
        out.append(f'{alvo}: {anexo[:140]} | {situ} | trecho: {trecho[:160]}')
    if data_iso:
        out.append(f'Data da entrada analisada: {data_iso} - comparar com a vigência acima.')
    return out


if __name__ == '__main__':
    a = sys.argv[1:]
    gravar = '--gravar-base' in a
    res = verificar(gravar)
    print(f'Verificação das fontes oficiais SEFAZ-SP em {date.today():%d/%m/%Y}:')
    for st, nome, obs, diff in res:
        print(f'  [{st:6}] {nome}: {obs}')
        for l in diff[:25]:
            print('           ', l[:200])
        if len(diff) > 25:
            print(f'            ... mais {len(diff) - 25} linhas alteradas')
    if '--cest' in a or '--ncm' in a:
        cest = a[a.index('--cest') + 1] if '--cest' in a else None
        ncm = a[a.index('--ncm') + 1] if '--ncm' in a else None
        dt = a[a.index('--data') + 1] if '--data' in a else None
        print('ST do produto (Portaria CAT 68/19, texto oficial):')
        for l in st_do_produto(cest, ncm, dt):
            print('  ', l)
    ruins = [r for r in res if r[0] in ('MUDOU', 'REGRA?', 'FALHOU')]
    if ruins:
        print('\nATENÇÃO: há parâmetro mudado ou não verificado. Revisar ANTES de passar valor/guia/prazo à analista.')
    if gravar:
        print('Base gravada.')
