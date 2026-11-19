"""Tabelas e regras de ICMS para destinatário em SÃO PAULO.

Tudo aqui é ATALHO para o auditor, não a palavra final: a palavra final é do RICMS/SP (Decreto 45.490/2000),
da Lei 6.374/1989, da LC 87/1996, da LC 123/2006 e das Respostas à Consulta da SEFAZ-SP.
Quando a analista confirmar uma regra diferente, atualizar esta tabela (vale para as próximas empresas).
"""

ALIQ_INTERNA_SP_PADRAO = 18.0  # RICMS/SP art. 52, I

# Alíquota interestadual para mercadoria destinada a SP (Res. Senado 22/1989 e 13/2012).
# Qualquer UF -> SP = 12%. (7% só sai de S/SE, exceto ES, para N/NE/CO/ES - nunca entra em SP.)
UFS = {'AC', 'AL', 'AP', 'AM', 'BA', 'CE', 'DF', 'ES', 'GO', 'MA', 'MT', 'MS', 'MG', 'PA', 'PB', 'PR', 'PE', 'PI',
       'RJ', 'RN', 'RS', 'RO', 'RR', 'SC', 'SP', 'SE', 'TO'}

# Origem da mercadoria (tabela A do CST / campo orig da NF-e)
ORIGEM = {
    '0': ('Nacional', 12.0),
    '1': ('Estrangeira - importação direta', 4.0),
    '2': ('Estrangeira - adquirida no mercado interno', 4.0),
    '3': ('Nacional com conteúdo de importação > 40% e <= 70%', 4.0),
    '4': ('Nacional - processos produtivos básicos (PPB)', 12.0),
    '5': ('Nacional com conteúdo de importação <= 40%', 12.0),
    '6': ('Estrangeira - importação direta sem similar nacional (lista CAMEX)', 12.0),
    '7': ('Estrangeira - mercado interno sem similar nacional (lista CAMEX)', 12.0),
    '8': ('Nacional com conteúdo de importação > 70%', 4.0),
}


def aliq_interestadual(orig):
    """Alíquota interestadual correta para entrar em SP, pela origem."""
    return ORIGEM.get(str(orig), ('?', 12.0))[1]


# NCM (prefixo) cuja alíquota interna em SP provavelmente NÃO é 18%, ou que tem benefício/redução.
# Gera ALERTA para a analista confirmar (o script usa 18% até ela confirmar em "aliquota_interna" do config).
NCM_ALIQ_ALERTA = [
    ('2203', 'Cerveja/chope - SP 20% (art. 54-A) - conferir'),
    ('2204', 'Vinhos - SP 25% - conferir'), ('2205', 'Vermutes - 25% - conferir'), ('2206', 'Fermentadas - 25% - conferir'),
    ('2208', 'Destiladas - SP 25% - conferir'),
    ('24', 'Fumo e derivados - SP 25% (+ adicional) - conferir'),
    ('3303', 'Perfumes - SP 25% - conferir'),
    ('27', 'Combustíveis - monofásico/ST (LC 192) - não é DIFAL comum'),
    ('8703', 'Automóveis - SP 12% (art. 54, VII) / redução - conferir'),
    ('8704', 'Veículos de carga - SP 12% - conferir'),
    ('8711', 'Motocicletas - conferir alíquota/ST'),
    ('84', 'Máquinas/equipamentos - possível redução de base (RICMS/SP Anexo II art. 12) - conferir carga interna'),
    ('85', 'Máquinas/aparelhos elétricos - possível redução de base (Anexo II art. 12) ou 12% - conferir'),
    ('8471', 'Computadores/informática - SP 12% ou redução (Anexo II) - conferir'),
    ('9018', 'Equipamentos médicos - possível isenção/redução (Conv. 01/99) - conferir'),
    ('0201', 'Carnes - SP 7%/12% ou isenção - conferir'), ('0207', 'Aves - 7% - conferir'),
    ('1006', 'Arroz - 7% - conferir'), ('0713', 'Feijão - 7% - conferir'),
    ('1101', 'Farinha de trigo - 7% - conferir'), ('1905', 'Pães/biscoitos - 7%/12% - conferir'),
    ('3101', 'Adubos/fertilizantes - Conv. 100/97 - conferir'), ('3102', 'Adubos - Conv. 100/97 - conferir'),
    ('3808', 'Defensivos - Conv. 100/97 - conferir'),
    ('6802', 'Pedras/mármores - conferir'), ('2523', 'Cimento - ST em SP - conferir'),
]

# NCM (prefixo) com grande chance de SUBSTITUIÇÃO TRIBUTÁRIA em SP (RICMS/SP arts. 313-A a 313-Z20 e Portarias SRE/CAT).
# Para revenda: se o fornecedor não reteve (sem acordo PR-SP ou sem IE-ST), o destinatário paulista pode ter de recolher
# por antecipação na entrada (art. 426-A, lista do §2º) ou como responsável. Sempre ALERTA para conferir CEST/NCM.
NCM_ST_ALERTA = [
    ('3003', 'Medicamentos (art. 313-A / art. 426-A §2º)'), ('3004', 'Medicamentos (art. 313-A / art. 426-A §2º)'),
    ('2203', 'Cerveja/chope'), ('2202', 'Refrigerantes/águas/energéticos'), ('2201', 'Água mineral'),
    ('2204', 'Vinhos - bebidas alcoólicas (art. 426-A §2º)'), ('2205', 'Bebidas alcoólicas'), ('2206', 'Bebidas alcoólicas'),
    ('2208', 'Bebidas alcoólicas (art. 426-A §2º)'), ('24', 'Fumo/cigarros'),
    ('3303', 'Perfumaria (art. 426-A §2º)'), ('3304', 'Cosméticos/maquiagem (art. 426-A §2º)'),
    ('3305', 'Produtos capilares (art. 426-A §2º)'), ('3306', 'Higiene bucal (art. 426-A §2º)'),
    ('3307', 'Desodorantes/higiene (art. 426-A §2º)'), ('3401', 'Sabões (art. 426-A §2º)'),
    ('3402', 'Detergentes/limpeza (art. 426-A §2º)'), ('4818', 'Papel higiênico/fraldas (art. 426-A §2º)'),
    ('9619', 'Fraldas/absorventes (art. 426-A §2º)'),
    ('4011', 'Pneus'), ('4013', 'Câmaras de ar'),
    ('8507', 'Baterias/acumuladores (conferir vigência: SRE 10/2026)'),
    ('2710', 'Lubrificantes/combustíveis'), ('2523', 'Cimento'),
    ('3208', 'Tintas e vernizes'), ('3209', 'Tintas e vernizes'), ('3210', 'Tintas e vernizes'),
    ('3214', 'Massas/vedantes'), ('8539', 'Lâmpadas'), ('2105', 'Sorvetes'), ('1806', 'Chocolates (conferir vigência)'),
    ('2309', 'Ração pet'), ('9404', 'Colchões (conferir vigência)'), ('8536', 'Materiais elétricos (conferir)'),
    ('8544', 'Fios/cabos (conferir)'), ('7214', 'Vergalhões (conferir)'), ('3917', 'Tubos plásticos - construção (conferir)'),
    ('6907', 'Revestimentos cerâmicos (conferir)'), ('7318', 'Parafusos (conferir)'),
]


# Segmentos que SAÍRAM da ST em SP (não alertar ST; alertar CST/CFOP de ST indevidos e estoque).
# Autopeças (CEST 01.xxx, Anexo XIV da Portaria CAT 68/2019): fora da ST em SP desde 01/10/2026 (Portaria SRE 34/2026)
# e SP excluído do Protocolo ICMS 41/2008 (Protocolo ICMS 93/2026). Estoque: Portaria CAT 28/2020.
SAIRAM_ST = [
    {'cest_prefixo': '01', 'desde': '2026-10-01',
     'texto': 'Autopeças (CEST 01) fora da ST em SP desde 01/10/2026 (Portaria SRE 34/2026; SP fora do Prot. ICMS 41/2008 '
              'pelo Prot. 93/2026): sem ST e sem antecipação na entrada'},
]


def saiu_st(cest, data_iso):
    for r in SAIRAM_ST:
        if (cest or '').startswith(r['cest_prefixo']) and (data_iso or '') >= r['desde']:
            return r['texto']
    return None


def busca_prefixo(ncm, tabela):
    ncm = (ncm or '').replace('.', '')
    hits = [(p, t) for p, t in tabela if ncm.startswith(p)]
    if not hits:
        return None
    return max(hits, key=lambda h: len(h[0]))[1]  # prefixo mais longo vence


# CFOP do FORNECEDOR (saída interestadual 6.xxx) -> leitura do auditor
CFOP_FORNECEDOR = {
    '6101': 'Venda de produção do estabelecimento', '6102': 'Venda de mercadoria adquirida de terceiros',
    '6105': 'Venda de produção que não deva por ele transitar', '6106': 'Venda de mercadoria que não deva por ele transitar',
    '6107': 'Venda de produção a NÃO contribuinte', '6108': 'Venda de mercadoria a NÃO contribuinte',
    '6109': 'Venda produção destinada à ZFM', '6110': 'Venda mercadoria destinada à ZFM',
    '6116': 'Venda produção - entrega futura', '6117': 'Venda mercadoria - entrega futura',
    '6118': 'Venda produção entregue a terceiro (venda à ordem)', '6119': 'Venda mercadoria entregue a terceiro (venda à ordem)',
    '6120': 'Venda à ordem - adquirente originário', '6122': 'Venda produção remetida para industrialização',
    '6152': 'Transferência de mercadoria', '6151': 'Transferência de produção',
    '6401': 'Venda produção com ST (substituto)', '6403': 'Venda mercadoria com ST (substituto)',
    '6404': 'Venda com ST já retido anteriormente', '6551': 'Venda de bem do ativo imobilizado',
    '6552': 'Transferência de bem do ativo', '6556': 'Devolução de compra de uso/consumo', '6557': 'Transferência de uso/consumo',
    '6901': 'Remessa para industrialização', '6902': 'Retorno de industrialização', '6908': 'Remessa em comodato',
    '6909': 'Retorno de comodato', '6910': 'Bonificação/doação/brinde', '6911': 'Amostra grátis',
    '6912': 'Remessa para demonstração', '6913': 'Retorno de demonstração', '6915': 'Remessa para conserto',
    '6916': 'Retorno de conserto', '6920': 'Remessa de vasilhame', '6921': 'Retorno de vasilhame',
    '6922': 'Simples faturamento - venda futura', '6923': 'Remessa por conta e ordem de terceiros',
    '6924': 'Remessa para industrialização por conta e ordem', '6949': 'Outra saída não especificada',
    '6202': 'Devolução de compra para comercialização', '6201': 'Devolução de compra para industrialização',
}

# CFOP que NÃO geram DIFAL (remessas com retorno, simples faturamento, devoluções etc.)
CFOP_SEM_DIFAL = {'6116', '6117', '6901', '6902', '6908', '6909', '6912', '6913', '6915', '6916', '6920', '6921',
                  '6922', '6924', '6201', '6202', '6556'}
CFOP_NAO_CONTRIB = {'6107', '6108'}
CFOP_ST = {'6401', '6403', '6404'}
CFOP_ESTRANHO = {'6949': 'CFOP genérico 6.949 - exigir a natureza real da operação',
                 '6911': 'Amostra grátis - conferir se é mesmo amostra (DIFAL se for uso/consumo)',
                 '6910': 'Bonificação/brinde - DIFAL é devido se a mercadoria for para uso/consumo/ativo'}

# CFOP de ENTRADA que a empresa paulista deve escriturar, por destinação
CFOP_ENTRADA = {
    'revenda': ('2102', '2403 (com ST)'), 'industrializacao': ('2101', '2401 (com ST)'),
    'uso_consumo': ('2556', '2407 (com ST)'), 'ativo': ('2551', '2406 (com ST)'),
}

CST_SEM_DESTAQUE = {'40', '41', '50', '51', '60'}
CSOSN_DESC = {'101': 'Simples com permissão de crédito', '102': 'Simples sem permissão de crédito',
              '103': 'Simples - isenção por faixa', '201': 'Simples com crédito e ST', '202': 'Simples sem crédito e com ST',
              '203': 'Simples isenção com ST', '300': 'Imune', '400': 'Não tributada', '500': 'ICMS cobrado anteriormente por ST',
              '900': 'Outros'}

DESTINACOES = ('revenda', 'industrializacao', 'uso_consumo', 'ativo')
REGIMES = {
    'rpa': 'Regime Periódico de Apuração (RPA) - contribuinte do ICMS',
    'simples': 'Simples Nacional - contribuinte do ICMS',
    'mei': 'MEI',
    'nao_contribuinte': 'Não contribuinte do ICMS (prestador de serviço sem IE, PF, órgão público etc.)',
}

# Recolhimento
GUIA_SIMPLES = ('DARE-SP, código 063-2 (recolhimentos especiais - diferencial de alíquota/equalização do Simples Nacional), '
                'até o último dia do 2º mês subsequente ao da entrada, em TODA compra interestadual não sujeita a ST, '
                'qualquer que seja a destinação (RICMS/SP art. 115, XV-A, "a"; RC 26911/2023). '
                'Fora do DAS - o DAS NÃO cobre o DIFAL (LC 123 art. 13 §1º XIII "h").')
GUIA_RPA = ('Lançar na apuração do mês da entrada (EFD ICMS/IPI): débito pela alíquota interna sobre a base "por dentro" '
            'e crédito pela alíquota interestadual - RICMS/SP art. 117 e art. 37, VI (Lei 6.374/89 art. 24). '
            'Recolhe junto com o ICMS do mês (código 046-2).')
