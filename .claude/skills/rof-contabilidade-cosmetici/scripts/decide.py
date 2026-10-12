import re
GRUPO=[(r'COSMETICON','663','COSMETICON - conta-corrente unica de mutuo (663)'),
       (r'F\.?V\.?S\b','662','F.V.S - conta-corrente unica de mutuo (662)'),
       (r'CABELO MEU','670','CABELO MEU - mutuo (670)'),
       (r'GULA|FIQUE BEM','366','GULA/FIQUE BEM (mesmo CNPJ, empresa do grupo) - mutuo em EMPRESTIMOS A TERCEIROS (366); nao e fornecedor')]
PESSOA=re.compile(r'^(?!.*\b(LTDA|S\.?A\.?|EIRELI|ME|EPP|COMERCIO|INDUSTRIA|SERVICOS|SERVIÇOS|CONSULTORIA|ENGENHARIA|TRANSPORTES|DISTRIBUIDORA|ASSOCIA|SINDICATO|BANCO|FUNDO)\b).*$')
def decide(r,x):
    """r: linha (orig,hist,valor,atual,final); x: item cosmos (ou None). retorna (conta, motivo) ou None"""
    txt=(r['orig']+' '+r['hist']+' '+(x['nome'] if x else '')).upper()
    if 'PROTECTION' in txt: return '361','honorarios contabeis (Protection)'
    for pat,acc,mot in GRUPO:
        if re.search(pat,txt): return acc,mot
    if 'LINK BANK' in txt: return '506','boleto LINK BANK = parcela AMONEX (materia-prima), Cosmos 18/02 2.142,00'
    if not x: return None
    pf,nome,obs=x['pf'],x['nome'].upper(),(x['obs'] or '').upper()
    if pf==94: return '672','amortizacao de emprestimo de terceiros (Factoring A. Mazzoni/Selito/MRBS) - baixa passivo, nao e despesa'
    if pf==185: return '504','RNX FIDC - recompra/troca de boletos antecipados = baixa de clientes'
    if pf==184:
        if 'BEAUTY FAIR' in nome: return '643','Beauty Fair - acordo de contrato de feira/estande = propaganda'
        return '672','Claudia Rubin - devolucao de valores recebidos (53.200,00) - nao e despesa'
    if pf==45:
        if 'PROTECTION' in nome: return '361','honorarios contabeis'
        if 'PLUS SANTE' in nome: return '653','atendimento medico empregados'
        if 'DENTAL' in nome: return '628','plano odontologico'
        return None
    if pf==47:
        if re.search(r'CRMTECH|TECNOPONTO|VR BENEF|IGOR RENATO|BRUNO DE JESUS',nome): return '640','software/sistema (Cosmos cat. 47)'
        if 'COPEL TELECOM' in nome: return '555','internet'
        return None
    if pf==16:
        if 'SB DISTRIBUIDORA' in nome: return '360','material de limpeza'
        if 'EQUISUL' in nome: return '656','EPI'
        return '58','material de consumo industrial (filtro, resina, lenha caldeira)'
    if pf==35: return '492','vale transporte'
    if pf in (27,55): return '493','reembolso de despesas'
    if pf in (81,53,170,171,172,181) and r['final']=='506' and PESSOA.match(nome) and not re.search(r'DECORAR|JFC|INNOVARTH|ANDRADE|PENSU|JULIO',nome):
        return '362','pessoa fisica - servico/comissao sem nota no fiscal'
    return None
def decide_novo(r):
    """linhas jul/ago (sem cosmos) marcadas como pendencia"""
    d=(r['orig']+' '+r['hist']).upper()
    for pat,acc,mot in GRUPO:
        if re.search(pat,d): return acc,mot
    if 'CONDOMINIO' in d: return '320','condominio do imovel locado = ocupacao (alugueis)'
    if re.search(r'PIX ENVIADO (ANTONIA|CLARISSA|HERNANDEZ|MARCELLA|FILIPE|LUCIANO|LUIZ HENRIQ|THIAGO)',d): return '362','pessoa fisica - servicos'
    if re.search(r'LUCENA & AMO',d): return '365','Lucena & Amo - acordo juridico (Cosmos: acordo procurador)'
    return None
