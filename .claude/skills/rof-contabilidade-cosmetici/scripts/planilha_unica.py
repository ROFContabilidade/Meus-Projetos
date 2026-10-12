import json,collections,re,sys
sys.path.insert(0,'../tools'); from saida import txt,head,AM
from decide import decide,decide_novo
from openpyxl import Workbook
from openpyxl.styles import Font,PatternFill
from openpyxl.worksheet.datavalidation import DataValidation
NOMES={}
for ln in open('balancete.csv',encoding='utf-8',errors='replace'):
    p=ln.split(';')
    if len(p)>2 and p[0].strip().isdigit(): NOMES[p[0].strip()]=p[1].strip()
NOMES.setdefault('11','APLICAÇÃO ITAU')
ents=json.load(open('razao_ents.json')); cr=json.load(open('cruz.json'))
by={x['rz_i']:x for x in cr if x.get('rz_i') is not None}
G=re.compile(r'COSMETICON|F\.V\.S|GULA|FIQUE BEM|CABELO MEU',re.I)
GSUG={'COSMETICON':'663','F.V.S':'662','GULA':'672','FIQUE BEM':'672','CABELO MEU':'670'}
rows=[]
for i,e in enumerate(ents):
    h=e['hist'].upper()
    if e['cp']=='11' or (e['cp']=='432' and 'RES APLIC' in h): continue   # aplicacao nao segregada
    v=round(e['d']-e['c'],2); x=by.get(i)
    st,sug,mot,cos='SEM COSMOS',e['cp'],'',''
    if x:
        cos=f"{x['nome']} | {x['op']}/{x['pf']} | {x['obs'][:120]}"
        st=x['nivel']; mot=x['motivo']; sug=x['sug'] or e['cp']
    m=G.search(h) or (x and G.search(x['nome'].upper()))
    if m:
        k=m.group(0).upper(); st='DECIDIR-GRUPO'; sug=GSUG.get(k,e['cp']); mot=f'empresa do grupo ({k}): hoje entradas e saidas vao para contas diferentes; sugestao = uma conta-corrente unica de mutuo por empresa'
    if 'LINK BANK' in h: st,sug,mot='DECIDIR','506','nao esta no Cosmos; provavel parcela AMONEX (MP) - Cosmos 18/02 2.142,00'
    final=sug if st=='CORRIGIR' else e['cp']
    if st in ('DECIDIR','DECIDIR-GRUPO'):
        dd=decide(dict(orig=e['hist'],hist=e['hist'],valor=v,final=final),x)
        if dd: final,mot=dd; st='AJUSTADO'
        else: st='MANTIDO'; mot=(mot+' | ' if mot else '')+'mantida a conta atual (sem informacao que justifique troca)'
    # ajustes 2a rodada (orientacao Rosangela)
    if x and x['pf']==53: final,mot,st='308','comissao sobre vendas -> 308 COMISSOES (conta existente no plano)','AJUSTADO'
    if 'BEAUTY FAIR' in (h+cos.upper()) and v<0: final,mot,st='688','Beauty Fair -> 688 FEIRAS E EVENTOS','AJUSTADO'
    if 'MAZZONI' in (h+' '+cos.upper()): final,mot,st=e['cp'],'socios Mazzoni (fora do contrato social) - mantido como estava','MANTIDO'
    hist=e['hist']
    if x and len(x['nome'])>3 and not x['nome'].startswith('OUTRAS'): hist=x['nome']+(' - '+x['obs'][:80] if x['obs'] else '')
    hist=re.sub(r'^REF\.? ?A ','',hist.strip())
    rows.append(dict(data=e['data'],orig=e['hist'],hist=hist,valor=v,atual=e['cp'],sug=sug,final=final,st=st,mot=mot,cos=cos))
for z in json.load(open('hist/ext06.json'))['mov']:
    if z['desc'].upper().startswith('REND'):
        rows.append(dict(data=z['data'],orig=z['desc'],hist='RENDIMENTO APLICACAO AUTOMATICA ITAU',valor=z['valor'],atual='(faltava)',sug='432',final='432',st='CORRIGIR',mot='rendimento de jun/26 nao lancado no TXT de junho',cos=''))
rows.sort(key=lambda r:(r['data'][6:],r['data'][3:5],r['data'][:2]))
for mes in ['Julho','Agosto']:
    for z in json.load(open(f'class_{mes}.json')):
        st='DECIDIR' if (z['how'].startswith('padrao') or 'varias' in z['how'] or (z['nota'] and 'retificado' not in z['nota'])) else ('CORRIGIDO' if z['nota'] and 'retificado' in z['nota'] else 'OK')
        if G.search(z['desc'].upper()): st='DECIDIR-GRUPO'
        m=G.search(z['desc'].upper()); sug=GSUG.get(m.group(0).upper(),z['cp']) if m else z['cp']
        fin=z['cp']; mt=z['nota'] or ''
        if st in ('DECIDIR','DECIDIR-GRUPO'):
            dd=decide_novo(dict(orig=z['desc'],hist=z['hist']))
            if dd: fin,mt=dd; st='AJUSTADO'
            else: st='MANTIDO'
        cu=(z['erp'] or '').upper()
        if 'COMISS' in cu: fin,mt,st='308','comissao sobre vendas -> 308','AJUSTADO'
        if 'BEAUTY FAIR' in (z['desc']+z['hist']).upper() and z['valor']<0: fin,mt,st='688','Beauty Fair -> 688 FEIRAS E EVENTOS','AJUSTADO'
        rows.append(dict(data=z['data'],orig=z['desc'],hist=z['hist'],valor=z['valor'],atual='(novo)',sug=sug,final=fin,st=st,mot=mt,cos=z['erp']))
json.dump(rows,open('linhas_jan_ago.json','w'),ensure_ascii=False)
# planilha
wb=Workbook(); ws=wb.active; ws.title='LANCAMENTOS jan-ago'
head(ws,['Nº','Data','Histórico extrato/razão (original)','Valor (+ entrada / - saída)','Conta atual no Domínio','Descrição conta atual','CONTA FINAL (vai no TXT)','Descrição conta final','Sugestão','Status','Motivo','Relatório Cosmos (fornecedor | OP/PF | descrição)','Histórico que vai no TXT'])
cores={'CORRIGIR':'F8CBAD','AJUSTADO':'FCE4D6','MANTIDO':'FFF2CC','CORRIGIDO':'E2EFDA'}
for n,r in enumerate(rows,1):
    ws.append([n,r['data'],r['orig'],r['valor'],r['atual'],NOMES.get(r['atual'],''),r['final'],None,r['sug'],r['st'],r['mot'],r['cos'],r['hist'][:150]])
    ws.cell(ws.max_row,8).value=f'=IFERROR(VLOOKUP(G{ws.max_row}&"",PLANO!A:B,2,FALSE),"CONTA NAO EXISTE NO PLANO")'
    if r['st'] in cores:
        for c in ws[ws.max_row]: c.fill=PatternFill('solid',fgColor=cores[r['st']])
    ws.cell(ws.max_row,7).font=Font(bold=True)
for col,w in zip('ABCDEFGHIJKLM',[6,11,34,14,9,28,10,28,9,15,60,70,50]): ws.column_dimensions[col].width=w
ws.auto_filter.ref=f'A1:M{ws.max_row}'
for r in ws.iter_rows(min_row=2,min_col=4,max_col=4):
    for c in r: c.number_format='#,##0.00;[Red]-#,##0.00'
# resumo por status
rs=wb.create_sheet('RESUMO',0)
rs.append(['Como usar']); rs['A1'].font=Font(bold=True,size=12)
for t in ['TXT único jan-ago/2026 pronto para importar. A coluna G (CONTA FINAL) da aba LANCAMENTOS é o que está no TXT - não precisa preencher nada.',
          'Cores: vermelho = corrigido pelo Cosmos; salmão = ajustado por decisão (regras na aba DECISOES); verde = jul/ago; amarelo = mantida a conta atual; sem cor = OK.',
          'No Domínio: excluir TODOS os lançamentos do Itaú (conta 8) de 01/01 a 30/06/2026 e importar o TXT único (jan a ago).',
          'Aplicação automática Itaú não segregada: conta 8 = saldo total (C/C + aplicação); aplicações/resgates fora; rendimentos na 432.',
          'Saldo calculado = extrato Itaú em todos os meses (aba CONCILIACAO).']:
    rs.append([t])
rs.append([]); rs.append(['Status','Qtde','Valor absoluto'])
for c in rs[rs.max_row]: c.font=Font(bold=True)
cnt=collections.Counter(); vv=collections.Counter()
for r in rows: cnt[r['st']]+=1; vv[r['st']]+=abs(r['valor'])
for k in cnt: rs.append([k,cnt[k],round(vv[k],2)])
rs.column_dimensions['A'].width=150
# conciliação mensal
cc=wb.create_sheet('CONCILIACAO')
head(cc,['Mês','Saldo inicial','Entradas','Saídas','Saldo final calculado','Saldo final extrato Itaú (C/C + aplicação)','Diferença'])
fim={'01':-3915.09,'02':-38533.72,'03':-21916.33,'04':2486.01,'05':-8520.05,'06':-1254.93,'07':8386.26,'08':-3506.09}
s=-32080.74; ok=True
for m in ['01','02','03','04','05','06','07','08']:
    l=[r for r in rows if r['data'][3:5]==m]; E=round(sum(r['valor'] for r in l if r['valor']>0),2); S=round(-sum(r['valor'] for r in l if r['valor']<0),2)
    f=round(s+E-S,2); cc.append([m+'/2026',s,E,S,f,fim[m],round(f-fim[m],2)]); print(m,f,fim[m],round(f-fim[m],2)); s=f
for col in 'ABCDEFG': cc.column_dimensions[col].width=22
# grupo
gw=wb.create_sheet('EMPRESAS DO GRUPO')
head(gw,['Empresa','Mês','Entradas (recebido)','Saídas (enviado)','Líquido','Contas usadas hoje'])
agg=collections.defaultdict(lambda:[0,0,set()])
for r in rows:
    m=G.search((r['orig']+' '+r['cos']).upper())
    if m:
        k=m.group(0).upper().replace('FIQUE BEM','GULA/FIQUE BEM').replace('GULA','GULA/FIQUE BEM') if m.group(0).upper() in ('GULA','FIQUE BEM') else m.group(0).upper()
        a=agg[(k,r['data'][3:5])]
        if r['valor']>0: a[0]+=r['valor']
        else: a[1]+=-r['valor']
        a[2].add(r['atual'] if r['atual']!='(novo)' else r['final'])
for (k,m),(e,s_,c) in sorted(agg.items()): gw.append([k,m+'/2026',round(e,2),round(s_,2),round(e-s_,2),', '.join(sorted(c))])
gw.append([]); gw.append(['Sugestão (decidir): uma conta-corrente de mútuo por empresa do grupo, usada tanto na entrada quanto na saída -> COSMETICON 663, F.V.S 662, CABELO MEU 670, GULA/FIQUE BEM sem conta própria (672 EMPRESTIMO DE TERCEIRO ou criar conta). Recebimento de NOTA de venda dessas empresas continua baixando o cliente (664/671).'])
for col,w in zip('ABCDEF',[18,10,18,18,16,30]): gw.column_dimensions[col].width=w
dc=wb.create_sheet('DECISOES',1)
head(dc,['Assunto','Regra aplicada','Base'])
for l in [('Empresas do grupo','Uma conta-corrente de mútuo por empresa, entradas e saídas na mesma conta: COSMETICON 663, F.V.S 662, CABELO MEU 670, GULA/FIQUE BEM 366','Cosmos lança como OUTRAS ENTRADAS/SAÍDAS (não é venda/compra com nota). Protection faz a contabilidade de Cosmetici, Cosmeticon, FVS e Gula = grupo. Fique Bem tem o mesmo CNPJ da Gula (30.415.972/0001-08).'),
          ('Pagamentos à GULA/FIQUE BEM','Saem de Fornecedores (506) e vão para 366','Não há compra com nota; explica parte do saldo devedor de 180 mil da 506.'),
          ('Amortização de empréstimos (Selito Kosdra, MRBS)','672 EMPRESTIMO DE TERCEIRO (antes despesa 362/364/493)','Cosmos: parcelas de empréstimos de 116.000 / 300.000 / 60.000. Juros desses empréstimos ficam em 375.'),
          ('Claudia A. Rubin - devolução de 53.200,00 (estande Beauty Fair)','688 FEIRAS E EVENTOS (antes 362)','Cosmos: devolução referente a 30% do estande da Beauty Fair comprado pelos chineses = custo da feira.'),
          ('Beauty Fair - acordo','688 FEIRAS E EVENTOS (antes 506)','Contrato de feira/estande.'),
          ('Comissões sobre vendas (Cosmos cat. 53)','308 COMISSÕES','Conta existente no plano (balancete 2025).'),
          ('RNX FIDC - troca de boletos/antecipação','504 CLIENTES DIVERSOS','Recompra de títulos antecipados.'),
          ('LINK BANK 3 x 2.142,00 (jan/fev)','506 (antes 432 rendimentos)','Parcelas AMONEX (matéria-prima) - Cosmos 18/02.'),
          ('Pessoas físicas pagas como serviço/comissão','362 (antes 506/25/187/493)','Sem nota no fiscal; empresa sem folha desde 03/26.'),
          ('Sistemas (CRMTECH, Tecnoponto, VR ponto, desenvolvedores)','640','Cosmos cat. 47.'),
          ('Protection','361','Honorários contábeis.'),
          ('Material de limpeza / EPI / filtros-resina-lenha','360 / 656 / 58','Cosmos cat. 16.'),
          ('Matéria-prima, embalagem, fretes, água, internet, FGTS, VA etc.','Conforme categoria do Cosmos (aba RESUMO: CORRIGIR)','Cosmos.'),
          ('Família Mazzoni (Carlos Alexandre, Michel, Marcelo, Factoring Alexandre Mazzoni)','Mantido EXATAMENTE como estava no razão','Sócios de fato, fora do contrato social: não cabe pró-labore nem retirada de sócio.'),
          ('Aplicação automática Itaú','Não segregada','Orientação do escritório: conta 8 = saldo total.')]:
    dc.append(list(l))
for col,w in zip('ABC',[45,70,90]): dc.column_dimensions[col].width=w
# plano
pl=wb.create_sheet('PLANO')
for k,v in sorted(NOMES.items(),key=lambda x:int(x[0])): pl.append([k,v])
pl.column_dimensions['B'].width=60
wb.save('out/COSMETICI_planilha_correcao_jan-ago2026.xlsx')
# TXT unico
lin=[]
for r in rows:
    if r['valor']<0: lin.append((r['data'],r['final'],'8',r['valor'],r['hist']))
    else: lin.append((r['data'],'8',r['final'],r['valor'],r['hist']))
txt('out/COSMETICI_TXT_UNICO_jan-ago2026.txt',lin)
print(len(rows),dict(cnt))
