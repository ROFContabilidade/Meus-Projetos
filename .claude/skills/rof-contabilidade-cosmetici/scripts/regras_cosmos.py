import re
NF={6,9,78,52,116,133}          # fornecedores com NF (MP, embalagem, etc.)
FIX={4:'312',97:'312',11:'320',12:'355',13:'354',14:'555',39:'192',86:'642',84:'375',124:'350',156:'350',128:'350',106:'350',34:'659',93:'659',89:'628',85:'576',87:'357',168:'357',37:'653',31:'512',42:'365',28:'350'}
SERV={81,53,170,171,172,181}
DECIDE={33:'pro-labore: plano nao tem conta de PRO-LABORE (hoje 362)',94:'amortizacao de emprestimo de terceiros (Factoring Alexandre/Selito/MRBS) - deveria baixar passivo, mas emprestimo nao esta no passivo (672 zerada)',182:'Marcelo H. Mazzoni - compra de marcas (intangivel?) / parcela',184:'acordos/devolucao (Beauty Fair, Claudia Rubin 53.200)',185:'RNX FIDC - troca de boletos/antecipacao',17:'folha/convenio farmacia desconto em folha',99:'PR (participacao nos resultados) 2024-2025',45:'servicos diversos (lavanderia, dedetizacao, contabilidade, Plus Sante)',47:'sistemas/VR beneficios/desenvolvimento',16:'filtros/equipamentos (manutencao?)',8:'material laboratorio/embalagem consumo',103:'material laboratorio/contratipagem',104:'nitrogenio/materiais',105:'material laboratorio',27:'reembolso',55:'reembolso combustivel',62:'ST s/ NFe',35:'vale transporte',123:'OUTRAS SAIDAS (sem identificacao no Cosmos)',122:'OUTRAS ENTRADAS (sem identificacao no Cosmos)'}
def sugerir(op,pf,cp,obs,nome):
    """retorna (conta_sugerida, nivel, motivo) ; nivel: OK | CORRIGIR | DECIDIR"""
    o=(obs or '').upper(); n=(nome or '').upper()
    if op==115 and pf==56:
        t='625' if 'IOF' in o and 'TAR' not in o else '626'
        return (t,'OK' if cp in ('625','626') else 'CORRIGIR','tarifa/IOF bancario')
    if op==115 and pf==122:
        return (cp,'OK','juros limite (375/625)') if cp in ('375','625','372') else ('375','CORRIGIR','juros limite conta')
    if op in (115,113) and pf in NF:
        if cp=='506': return ('506','OK','fornecedor com NF')
        return ('506','CORRIGIR' if cp in ('365','493','56','364','555','350','362') else 'DECIDIR','fornecedor com NF (Cosmos: compra MP/embalagem) - pagamento deve baixar fornecedores 506')
    if op==115 and pf in FIX:
        t=FIX[pf]; return (t,'OK' if cp==t else 'CORRIGIR','categoria Cosmos %d'%pf)
    if op==115 and pf in SERV:
        if cp=='362': return ('362','OK','servico prestado')
        if cp in ('25','187','493','361','364'): return ('362','CORRIGIR','Cosmos: servicos prestados/comissao (nao e folha/adiantamento)')
        return ('362','DECIDIR','Cosmos: servicos/comissao lancado em %s - se houver NFS-e lancada no fiscal, 506 esta certo'%cp)
    if pf in DECIDE or op in (122,123):
        return (cp,'DECIDIR',DECIDE.get(pf) or DECIDE.get(op))
    return (cp,'DECIDIR','categoria Cosmos %d/%d sem regra'%(op,pf))
