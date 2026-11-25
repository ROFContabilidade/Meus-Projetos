# ======== RAZÃO DIÁRIO e RAZÃO POR CONTA e ENTENDA ========
import json,sys
sys.path.insert(0,HERE)
from classify import classify
LANC=json.load(open(os.path.join(HERE,'dados','lanc.json')))
from datetime import datetime
MESN=['jan','fev','mar','abr','mai','jun','jul','ago','set','out','nov','dez']
wz=sheet('Razão diário','RAZÃO DIÁRIO – CONTA CORRENTE SICREDI 61921-3 (todos os lançamentos, em ordem de data)',SUB.replace(' conferido com extratos Sicredi 61921-3',''),[11,8,6,46,40,30,22,13,13,14])
r=4; hdr(wz,r,['Data','Mês','Nº','Histórico do banco','O que foi (em palavras simples)','Conta','Grupo','Entrada (R$)','Saída (R$)','Saldo (R$)'])
wz.freeze_panes='A6'
r=5; cell(wz,r,4,'SALDO ANTERIOR EM 30/11/2025',bold=True,bg=GOLD)
for c in (1,2,3,5,6,7,8,9): cell(wz,r,c,'',bg=GOLD)
cell(wz,r,10,7369.69,fmt=NUM,bold=True,color='000000',bg=GOLD)
D0=r+1
for i,x in enumerate(LANC,1):
    r+=1; g,cta,simp=classify(x); dt=datetime.strptime(x['data'],'%d/%m/%Y')
    cell(wz,r,1,dt,fmt='dd/mm/yyyy',align='center'); cell(wz,r,2,f"{MESN[dt.month-1]}/{str(dt.year)[2:]}",align='center',size=9); cell(wz,r,3,i,align='center',size=9)
    cell(wz,r,4,x['desc'],size=9); cell(wz,r,5,simp); cell(wz,r,6,cta,size=9); cell(wz,r,7,g,size=9,color=('808080' if g=='Movimentação entre contas' else '000000'))
    v=x['valor']
    cell(wz,r,8,v if v>0 else None,fmt=NUM,color='000000',bg=(GREEN if v>0 else None)); cell(wz,r,9,-v if v<0 else None,fmt=NUM,color='000000',bg=(RED if v<0 else None))
    cell(wz,r,10,f'=J{r-1}+N(H{r})-N(I{r})',fmt=NUM,bold=True)
D1=r
r+=1; cell(wz,r,4,'TOTAIS DO PERÍODO (01/12/2025 a 19/11/2026)',bold=True,bg=GREY)
for c in (1,2,3,5,6,7,10): cell(wz,r,c,'',bg=GREY)
cell(wz,r,8,f'=SUM(H{D0}:H{D1})',fmt=NUM,bold=True,bg=GREY); cell(wz,r,9,f'=SUM(I{D0}:I{D1})',fmt=NUM,bold=True,bg=GREY)
wz.auto_filter.ref=f'A4:J{D1}'
r+=2
for t in ['Como usar: clique na setinha do título da coluna "Mês" ou "Conta" para ver só um mês ou só um tipo de gasto.',
          'Fonte: extratos Sicredi de cada mês (pastas 12_2025 a 11_2026). Saldo conciliado lançamento a lançamento.',
          '"Movimentação entre contas" (cinza) é dinheiro que só trocou de lugar entre a conta corrente e a poupança do próprio condomínio. Não é receita nem despesa.',
          'Lançamentos até 19/11/2026, data do último extrato salvo.']:
    wz.merge_cells(start_row=r,start_column=1,end_row=r,end_column=10); c=wz.cell(r,1,t); c.font=font(italic=True,size=9,color='595959'); r+=1
wz.print_title_rows='4:4'

# ---- Razão por conta
wr=sheet('Razão por conta','RAZÃO POR CONTA – lançamentos da conta corrente agrupados por conta (R$)',SUB,[11,46,40,14,14,15])
DZ="'Razão diário'!"
order=[]
for x in LANC:
    k=classify(x)[:2]
    if k not in order: order.append(k)
gorder=['Receitas','Despesas administrativas','Manutenção predial','Serviços essenciais','Prestadores de serviço','Encargos','Aquisição de bens','Movimentação entre contas']
order.sort(key=lambda k:(gorder.index(k[0]),k[1]))
r=4; hdr(wr,r,['Data','Histórico do banco','Descrição','Entrada (R$)','Saída (R$)','Acumulado da conta (R$)']); wr.freeze_panes='A5'; r+=1
for g,cta in order:
    section(wr,r,f'{cta.upper()}   ·   {g}',6,color=(GREEN if g=='Receitas' else (GREY if g.startswith('Mov') else LIGHT))); r+=1; s=r
    for x in LANC:
        if classify(x)[:2]!=(g,cta): continue
        v=x['valor']; dt=datetime.strptime(x['data'],'%d/%m/%Y')
        cell(wr,r,1,dt,fmt='dd/mm/yyyy',align='center'); cell(wr,r,2,x['desc'],size=9); cell(wr,r,3,classify(x)[2],size=9)
        cell(wr,r,4,v if v>0 else None,fmt=NUM,color='000000'); cell(wr,r,5,-v if v<0 else None,fmt=NUM,color='000000')
        cell(wr,r,6,(f'=N(D{r})+N(E{r})' if r==s else f'=F{r-1}+N(D{r})+N(E{r})'),fmt=NUM); r+=1
    cell(wr,r,3,f'Total – {cta}',bold=True,bg=GREY); cell(wr,r,1,'',bg=GREY); cell(wr,r,2,'',bg=GREY)
    cell(wr,r,4,f'=SUM(D{s}:D{r-1})',fmt=NUM,bold=True,bg=GREY); cell(wr,r,5,f'=SUM(E{s}:E{r-1})',fmt=NUM,bold=True,bg=GREY); cell(wr,r,6,'',bg=GREY); r+=2
wr.print_title_rows='4:4'

# ---- VISÃO GERAL
we=wb.create_sheet('Visão geral',0); we.sheet_view.showGridLines=False
for i,wd_ in enumerate([3,50,20,3,44,20],1): we.column_dimensions[L(i)].width=wd_
we.page_setup.orientation='portrait'; we.page_setup.paperSize=we.PAPERSIZE_A4; we.sheet_properties.pageSetUpPr.fitToPage=True; we.page_setup.fitToWidth=1; we.page_setup.fitToHeight=1
we.merge_cells('A1:F1'); c=we['A1']; c.value='CONDOMÍNIO LONDON RESIDENCE – PRESTAÇÃO DE CONTAS 2026'; c.font=font(bold=True,size=16,color='FFFFFF'); c.fill=fill(NAVY); c.alignment=Alignment(horizontal='center',vertical='center'); we.row_dimensions[1].height=36
we.merge_cells('A2:F2'); c=we['A2']; c.value='Visão geral do período de 01/12/2025 a 30/11/2026 · Assembleia Geral Ordinária de 26/11/2026'; c.font=font(italic=True,size=11,color='595959'); c.alignment=Alignment(horizontal='center')
M="'Mês a mês'!"
cards=[('Receitas do período',f"={M}N{R['REC']}",'Taxas condominiais, fundo de reserva, multas e acordo judicial recebidos em 12 meses.',GREEN,NUM),
       ('Despesas do período',f"={M}N{R['DES']}",'Todas as despesas pagas no período, incluindo a pintura predial.',RED,NUM),
       ('Pintura predial',f"={M}N{R['Pintura predial']}",'Fachada e estacionamento, aprovadas na AGO de 01/12/2025 (7º assunto).',LIGHT,NUM),
       ('Resultado do período',f"={M}N{R['RES']}+{M}N{R['POUP']}",'Despesas maiores que as receitas por causa da pintura. A diferença foi coberta com a reserva aplicada em poupança.',GOLD,NUM),
       ('Resultado sem a pintura',f"={M}N{R['REC']}-{M}N{R['ORD']}",'Receitas menos despesas do dia a dia. O excedente, que inclui o fundo de pintura, ajudou a pagar a obra.',GREEN,NUM),
       ('Saldo disponível',"='Conciliação bancária'!C"+str(POS_TOT),'Conta corrente + poupança + fundo de reserva, na posição de 23/11/2026.',GOLD,NUM),
       ('Saldos bancários','Conciliado','Saldos da conta do condomínio conferidos com os extratos do Sicredi em todos os 12 meses.',GREEN,'@'),
       ('Inadimplência',"='Inadimplência'!B4",'Total em aberto em 30/11/2026. A maior dívida foi quitada por acordo judicial em 11/2026.',LIGHT,NUM)]
r=4
for i,(q,f,expl,bg,fmt_) in enumerate(cards):
    col=1 if i%2==0 else 4
    if i%2==0 and i>0: r+=4
    we.merge_cells(start_row=r,start_column=col+1,end_row=r,end_column=col+2)
    c=we.cell(r,col+1,q); c.font=font(bold=True,size=12,color=NAVY); c.fill=fill(bg); c.alignment=Alignment(indent=1)
    c2=we.cell(r+1,col+1,'R$' if fmt_==NUM else ''); c2.font=font(size=11,color='595959'); c2.fill=fill(bg); c2.alignment=Alignment(horizontal='right')
    c3=we.cell(r+1,col+2,f); c3.font=font(bold=True,size=18,color=NAVY); c3.fill=fill(bg); c3.number_format=fmt_
    we.merge_cells(start_row=r+2,start_column=col+1,end_row=r+2,end_column=col+2)
    c4=we.cell(r+2,col+1,expl); c4.font=font(size=9,color='404040'); c4.fill=fill(bg); c4.alignment=Alignment(wrap_text=True,vertical='top',indent=1)
    we.row_dimensions[r+1].height=28; we.row_dimensions[r+2].height=32
r+=5
we.merge_cells(start_row=r,start_column=2,end_row=r,end_column=6); c=we.cell(r,2,'DISTRIBUIÇÃO DAS DESPESAS – a cada R$ 100,00 gastos'); c.font=font(bold=True,size=12,color='FFFFFF'); c.fill=fill(BLUE); c.alignment=Alignment(indent=1); we.row_dimensions[r].height=22
r+=1
hdr(we,r,['','Grupo de despesa','Valor no período (R$)','R$ por 100','',''],c0=1); 
for cc in (1,): we.cell(r,cc).fill=PatternFill(None); we.cell(r,cc).border=Border()
we.merge_cells(start_row=r,start_column=5,end_row=r,end_column=6); we.row_dimensions[r].height=20; r+=1; b0=r
G="'Mês a mês'!N"
cats=[('Pintura predial (fachada e estacionamento)',f"={G}{R['Pintura predial']}"),
      ('Administração: síndico, administradora, jurídico, banco e sistema',f"={G}{grp_rows['Despesas administrativas']}"),
      ('Água, energia, gás e seguro predial',f"={G}{grp_rows['Serviços essenciais']}"),
      ('Manutenção: elevador, portão, telhado, câmeras, limpeza e outros',f"={G}{grp_rows['Manutenção predial']}-{G}{R['Pintura predial']}"),
      ('Prestadores: zeladora, jardinagem e eletricista',f"={G}{grp_rows['Prestadores de serviço']}"),
      ('Outros: retenção de imposto e carrinho de compras',f"={G}{grp_rows['Encargos']}+{G}{grp_rows['Aquisição de bens']}")]
for n,f in cats:
    cell(we,r,2,n,size=10,wrap=True); cell(we,r,3,f,fmt=NUM,size=10)
    cell(we,r,4,f'=C{r}/C${b0+len(cats)}*100',fmt='0.00',bold=True,size=10,align='center',color=NAVY)
    we.merge_cells(start_row=r,start_column=5,end_row=r,end_column=6)
    cell(we,r,5,f'=REPT("█",ROUND(D{r}/1.5,0))',color='2E75B6',size=10); we.row_dimensions[r].height=26; r+=1
cell(we,r,2,'Total',bold=True,bg=GREY); cell(we,r,3,f'=SUM(C{b0}:C{r-1})',fmt=NUM,bold=True,bg=GREY); cell(we,r,4,f'=SUM(D{b0}:D{r-1})',fmt='0.00',bold=True,bg=GREY,align='center')
we.merge_cells(start_row=r,start_column=5,end_row=r,end_column=6); cell(we,r,5,'',bg=GREY)
we.column_dimensions['D'].width=11
r+=2
we.merge_cells(start_row=r,start_column=2,end_row=r,end_column=6); c=we.cell(r,2,'CUSTO MENSAL DO CONDOMÍNIO (sem a pintura)'); c.font=font(bold=True,size=12,color='FFFFFF'); c.fill=fill(BLUE); c.alignment=Alignment(indent=1); r+=1
for n,f in [('Despesa média por mês',f"={M}O{R['ORD']}"),('Despesa média por apartamento por mês (20 unidades)',f"={M}O{R['ORD']}/20"),('Receita média por mês',f"={M}O{R['REC']}")]:
    cell(we,r,2,n,size=10); cell(we,r,3,f,fmt=NUM,bold=True,size=11); r+=1
r+=1
we.merge_cells(start_row=r,start_column=2,end_row=r+2,end_column=6)
c=we.cell(r,2,'Conclusão: as receitas cobriram todas as despesas do dia a dia em todos os meses do período. A pintura predial foi paga com o fundo de pintura e com a reserva aplicada em poupança, conforme aprovado em assembleia. Os saldos bancários estão conciliados em todos os meses. O detalhe de cada pagamento está nas abas "Razão diário" e "Razão por conta".')
c.font=font(size=10,bold=True,color='375623'); c.fill=fill(GREEN); c.alignment=Alignment(wrap_text=True,vertical='center',indent=1)
for k in range(3): we.row_dimensions[r+k].height=22
