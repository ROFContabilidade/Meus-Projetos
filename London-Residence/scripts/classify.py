import json,sys
def classify(x):
    d=x['desc'].upper(); v=x['valor']; dt=x['data']
    E=v>0
    # returns (grupo, conta, simples)
    if 'TRANSFERENCIA DA POUPANCA' in d: return ('Movimentação entre contas','Resgate da poupança','Dinheiro tirado da poupança do condomínio')
    if 'APLICACAO POUPANCA' in d: return ('Movimentação entre contas','Aplicação na poupança','Dinheiro guardado na poupança')
    if E:
        if 'LIQ.COBRANCA' in d: return ('Receitas','Taxas condominiais (boletos)','Boletos pagos pelos moradores')
        if 'EVERTON' in d: return ('Receitas','Acordo judicial (repasse do advogado)','Dívida antiga paga na Justiça')
        if 'DILERVALDO' in d: return ('Receitas','Estorno','Prestador devolveu dinheiro')
        return ('Receitas','Taxas condominiais (PIX)','Taxa paga pelo morador por PIX')
    if 'TARIFA' in d or 'MANUTENCAO DE TITULOS' in d: return ('Despesas administrativas','Despesas bancárias','Tarifas do banco')
    if 'CESTA DE RELACIONAMENTO' in d: return ('Despesas administrativas','Despesas bancárias','Tarifas do banco')
    if 'MARCOS ANTONIO' in d: 
        if abs(v+268.22)<0.01: return ('Despesas administrativas','Cartório (registro da ata)','Registro da ata no cartório (reembolso ao síndico)')
        return ('Despesas administrativas','Salário do síndico','Pagamento do síndico')
    if 'ROF CONTABILIDADE' in d: return ('Despesas administrativas','Honorários administrativos (ROF)','Administradora (contabilidade)')
    if 'EVERTON' in d: return ('Despesas administrativas','Assessoria jurídica','Advogado')
    if 'GROUP SO' in d or 'ASSOCIACAO' in d: return ('Despesas administrativas','Software de gestão e certificado','Sistema de boletos e certificado digital')
    if 'DIRECT INTERNET' in d: return ('Despesas administrativas','Internet','Internet do prédio')
    if 'CHAVEIRO' in d or 'LEANDRO' in d: return ('Despesas administrativas','Chaves de acesso','Cópia de chaves')
    if 'UPY' in d: return ('Despesas administrativas','Despesas de assembleia','Cadeiras para a assembleia')
    if 'SANTOS ALELUIA' in d or 'TINTAS VERGINIA' in d: return ('Manutenção predial','Pintura predial','Pintura do prédio')
    if 'FIDELIDADE' in d:
        if abs(v+1500)<0.01 or abs(v+1680)<0.01: return ('Manutenção predial','Manutenção de áreas comuns','Conserto e limpeza das áreas comuns')
        return ('Manutenção predial','Pintura predial','Pintura do prédio')
    if 'TK ELEVADORES' in d: return ('Manutenção predial','Elevador (TK)','Manutenção do elevador')
    if 'DARF' in d or 'RECEITA FEDERAL' in d: return ('Encargos','Retenção na fonte (TK – DARF 0385)','Imposto retido do elevador')
    if 'ASSET' in d:
        if abs(v+700)<0.01 or abs(v+610.30)<0.01: return ('Manutenção predial','Câmeras de segurança','Câmeras de segurança')
        return ('Manutenção predial','Portão de entrada','Portão da garagem')
    if 'DILERVAL' in d:
        if dt.endswith('/09/2026'): return ('Manutenção predial','Portão de entrada','Portão da garagem')
        return ('Manutenção predial','Manutenção de áreas comuns','Conserto e limpeza das áreas comuns')
    if 'LUIZ MARCELO' in d or 'TELHADAO' in d: return ('Manutenção predial','Telhado e calhas','Telhado e calhas')
    if 'DEDETIZADORA' in d or 'MELIPONARIO' in d: return ('Manutenção predial','Dedetização','Dedetização e remoção de vespas')
    if 'ECOLIMP' in d: return ('Manutenção predial','Material de limpeza','Produtos de limpeza')
    if 'PLATINA' in d: return ('Manutenção predial','Sistema contra incêndio','Extintores e mangueiras')
    if 'ANTONIO PEREIRA' in d: return ('Manutenção predial',"Bomba d'água","Bomba d'água")
    if 'ELETRORASTRO' in d: return ('Manutenção predial','Material elétrico','Lâmpadas e material elétrico')
    if 'CAZAMA' in d: return ('Manutenção predial','Manutenção de áreas comuns','Conserto e limpeza das áreas comuns')
    if 'BRENER' in d:
        if abs(v+200)<0.01: return ('Manutenção predial','Manutenção de áreas comuns','Conserto do playground')
        return ('Prestadores de serviço','Jardinagem','Jardim')
    if 'SANEPAR' in d or 'RODRIGUES AGUA' in d: return ('Serviços essenciais','Água e esgoto','Água')
    if 'COPEL' in d: return ('Serviços essenciais','Energia elétrica (Copel)','Luz')
    if 'BR DIST' in d or 'DISTRIBUIDO' in d: return ('Serviços essenciais','Gás','Gás')
    if 'HDI' in d or 'HDISEGU' in x['doc']: return ('Serviços essenciais','Seguro predial obrigatório (HDI)','Seguro do prédio')
    if 'ARACELI' in d: return ('Prestadores de serviço','Zeladora','Zeladora')
    if 'JARDINAGEM' in d or 'LUCAS AU' in d or 'ARGEMIRO' in d: return ('Prestadores de serviço','Jardinagem','Jardim')
    if 'GILVAN' in d: return ('Prestadores de serviço','Eletricista','Eletricista')
    if 'MARKETPLACE' in d: return ('Aquisição de bens','Cartão de acesso do carrinho de compras','Cartão do carrinho de compras')
    return ('???','???','???')
if __name__=='__main__':
    L=json.load(open(sys.argv[1]+'/lanc.json'))
    import collections; t=collections.defaultdict(float)
    for x in L:
        g,c,s=classify(x); t[(g,c)]+=x['valor']
        if g=='???': print('UNCLASS',x)
    for k in sorted(t): print(f'{k[0]:28} {k[1]:42} {t[k]:12.2f}')
