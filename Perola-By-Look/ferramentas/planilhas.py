import json,collections,openpyxl
from openpyxl.styles import Font,PatternFill,Alignment
o=json.load(open('out/motor.json'))
NOME={'504':'CLIENTES DIVERSOS','470':'CMV - MERCADORIA SEM NF / ACIMA DA NF','320':'ALUGUEIS','362':'SERV. PESSOA FISICA SEM NF','506':'FORNECEDORES (BAIXA DE NF)',
'188':'PRO-LABORE A PAGAR','48':'CDB PAGBANK','551':'CONTA CORRENTE SOCIA','8':'PAGBANK','9':'ITAU','312':'FRETES/EXCURSAO COMPRAS','356':'TELEFONE','493':'DESPESAS DIVERSAS',
'521':'ALIMENTACAO','354':'ENERGIA','191':'INSS A RECOLHER','479':'SIMPLES A RECOLHER','558':'SISTEMAS','361':'ASSIST. CONTABIL','APLIC_ITAU':'APLICACAO AUTOMATICA ITAU (CRIAR)',
'510':'HONORARIOS CONTABEIS A PAGAR','574':'MARKETING','512':'ICMS ANTECIPADO','359':'DESP. ADMINISTRATIVAS','58':'MAT. CONSUMO/EMBALAGENS','360':'MAT. LIMPEZA','352':'MULTAS DE MORA','372':'JUROS DE MORA','432':'JUROS DE APLICACOES'}
wb=openpyxl.Workbook(); B=Font(bold=True); F=PatternFill('solid',fgColor='DDEBF7')
def head(ws,cols):
    ws.append(cols)
    for c in ws[1]: c.font=B; c.fill=F
    ws.freeze_panes='A2'
# 1 resumo
ws=wb.active; ws.title='Resumo por conta'
meses=['01','02','03','04','05','06','07','08','09','10']
t=collections.defaultdict(lambda:collections.Counter())
for l in o['L']:
    for c,v,h in l['partes']: t[c][l['d'][5:7]]+=(-v if l['entrada'] else v)
for e in o['EX']:
    t[e['deb']][e['d'][5:7]]+=e['v']; t[e['cred']][e['d'][5:7]]-=e['v']
head(ws,['Conta','Descricao']+[f'{m}/2026' for m in meses]+['Total 01-10'])
for c in sorted(t,key=lambda c:-abs(sum(t[c].values()))):
    ws.append([c,NOME.get(c,'')]+[round(t[c][m],2) for m in meses]+[round(sum(t[c].values()),2)])
ws.append([]); ws.append(['','Sinal: positivo = debito; negativo = credito (contrapartidas dos bancos)'])
# 2 movimentos
ws=wb.create_sheet('Movimentos classificados'); head(ws,['Data','Banco','Entrada/Saida','Valor','Historico do extrato','Conta','Valor partida','Historico do lancamento'])
for l in sorted(o['L'],key=lambda l:(l['d'],l['banco'])):
    for c,v,h in l['partes']:
        ws.append([l['d'],'PagBank' if l['banco']=='8' else 'Itau','E' if l['entrada'] else 'S',l['total'],l['orig'],c,v,h])
for e in o['EX']: ws.append([e['d'],'-','-',e['v'],'(sem banco)',f"D {e['deb']} / C {e['cred']}",e['v'],e['h']])
# 3 controle 506
ws=wb.create_sheet('Controle 506 por NF'); head(ws,['Emissao','Tipo','Nota','Fornecedor','CNPJ raiz','Valor NF','Pago (baixa)','Em aberto','Pagamentos (data/banco/valor)','Observacao'])
for n in sorted(o['NF'],key=lambda n:n['em']):
    pago=round(sum(p[2] for p in n['pags']),2)
    obs=n.get('obs','')
    if n['aberto']>0 and n['em']<'2026': obs='NF de 2025: pagamento nao localizado em 2026 (pode ter sido pago em 2025 - conferir razao 506 de 2025)'
    ws.append([n['em'],n['tipo'],n['nota'],n['forn'],n['root'],n['v'],pago,n['aberto'],'; '.join(f"{p[0]} {('PagBank' if p[1]=='8' else 'Itau' if p[1]=='9' else 'desc. repasse')} {p[2]:.2f}" for p in n['pags']),obs])
# 4 pagamentos acima / sem NF por fornecedor (470)
ws=wb.create_sheet('470 por favorecido'); head(ws,['Favorecido (extrato)','Qtde','Total levado a 470'])
c=collections.defaultdict(lambda:[0,0.0])
for l in o['L']:
    for cc,v,h in l['partes']:
        if cc=='470': k=l['orig'][:55]; c[k][0]+=1; c[k][1]+=v
for k,v in sorted(c.items(),key=lambda z:-z[1][1]): ws.append([k,v[0],round(v[1],2)])
ws=wb.create_sheet('362 por favorecido'); head(ws,['Favorecido (extrato)','Qtde','Total levado a 362'])
c=collections.defaultdict(lambda:[0,0.0])
for l in o['L']:
    for cc,v,h in l['partes']:
        if cc=='362': k=l['orig'][:55]; c[k][0]+=1; c[k][1]+=v
for k,v in sorted(c.items(),key=lambda z:-z[1][1]): ws.append([k,v[0],round(v[1],2)])
for w in wb.worksheets:
    for col in w.columns:
        w.column_dimensions[col[0].column_letter].width=min(60,max(10,max(len(str(x.value or '')) for x in col[:200])+2))
wb.save('out/PEROLA_49_Reprocessamento_01-10_2026.xlsx'); print('ok')
