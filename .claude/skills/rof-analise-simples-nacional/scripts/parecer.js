// Parecer em Word para o CLIENTE a partir do resumo.json do estudo_simples.py.
// Uso: node parecer.js resumo.json PARECER.docx [textos.json]
// textos.json (opcional): {"cliente": "Nome (fantasia) – CNPJ", "regime": "Simples Nacional – Anexo I...", "data": "30 de outubro de 2026",
//   "resumo_extra": ["..."], "puro_hibrido_extra": ["..."], "premissas_extra": ["..."], "recomendacao": "texto que substitui a automática"}
const fs = require('fs');
const { Document, Packer, Paragraph, TextRun, Table, TableRow, TableCell, WidthType, AlignmentType, ShadingType, BorderStyle,
  HeadingLevel, LevelFormat, Footer, PageNumber } = require('docx');
const [, , resPath, outPath, txtPath] = process.argv;
const R = JSON.parse(fs.readFileSync(resPath, 'utf8'));
const X = txtPath ? JSON.parse(fs.readFileSync(txtPath, 'utf8')) : {};
const brl = v => v.toLocaleString('pt-BR', { minimumFractionDigits: 2, maximumFractionDigits: 2 });
const pct = (v, d = 2) => (v * 100).toLocaleString('pt-BR', { minimumFractionDigits: d, maximumFractionDigits: d }) + '%';
const M = R.meses, sum = k => M.reduce((s, m) => s + m[k], 0);
const totRpa = sum('rpa'), totDas = sum('das'), totDas27 = sum('das27');
const aumAno = R.das27_ano - R.das_ano;
const hoje = new Date().toLocaleDateString('pt-BR', { day: 'numeric', month: 'long', year: 'numeric' });
const periodo = `${M[0].mes} a ${M[M.length - 1].mes}`;
const hibridoMelhor = R.hibrido_confiavel && R.dif_hibrido < 0;

const FONT = 'Calibri', AZUL = '1F4E78', CINZA = 'F2F2F2', CLARO = 'DEEAF6';
const t = text => new TextRun({ text, font: FONT, size: 22 });
const b = text => new TextRun({ text, bold: true, font: FONT, size: 22 });
const p = (runs, align) => new Paragraph({ spacing: { after: 120, line: 276 }, alignment: align || AlignmentType.JUSTIFIED,
  children: (Array.isArray(runs) ? runs : [runs]).map(x => typeof x === 'string' ? t(x) : x) });
const h1 = text => new Paragraph({ heading: HeadingLevel.HEADING_1, spacing: { before: 240, after: 120 },
  children: [new TextRun({ text, bold: true, font: FONT, size: 26, color: AZUL })] });
const bullet = runs => new Paragraph({ numbering: { reference: 'bul', level: 0 }, spacing: { after: 80, line: 276 },
  children: (Array.isArray(runs) ? runs : [runs]).map(x => typeof x === 'string' ? t(x) : x) });
const gap = () => new Paragraph({ spacing: { after: 60 }, children: [] });
const bd = { style: BorderStyle.SINGLE, size: 4, color: 'BFBFBF' }, borders = { top: bd, bottom: bd, left: bd, right: bd };
function table(header, rows, widths, opts = {}) {
  const cell = (txt, w, { head, bold, fill, align } = {}) => new TableCell({ width: { size: w, type: WidthType.DXA }, borders,
    shading: head ? { type: ShadingType.CLEAR, fill: AZUL, color: 'auto' } : (fill ? { type: ShadingType.CLEAR, fill, color: 'auto' } : undefined),
    margins: { top: 60, bottom: 60, left: 100, right: 100 },
    children: [new Paragraph({ alignment: align || (head ? AlignmentType.CENTER : AlignmentType.RIGHT),
      children: [new TextRun({ text: txt, font: FONT, size: 19, bold: head || bold, color: head ? 'FFFFFF' : '000000' })] })] });
  return new Table({ width: { size: widths.reduce((a, c) => a + c, 0), type: WidthType.DXA }, columnWidths: widths, rows: [
    new TableRow({ tableHeader: true, children: header.map((h, i) => cell(h, widths[i], { head: true })) }),
    ...rows.map((r, ri) => { const tot = opts.totalLast && ri === rows.length - 1;
      return new TableRow({ children: r.map((v, i) => cell(v, widths[i], { bold: tot, fill: tot ? CLARO : (ri % 2 ? CINZA : undefined),
        align: (i === 0 || opts.textLeft) ? AlignmentType.LEFT : undefined })) }); })] });
}
const tabMensal = table(['Competência', 'Receita bruta', '% monofásico', 'DAS pago', 'DAS regra 2027', 'Aumento R$', 'Aumento %'],
  [...M.map(m => [m.mes + (m.estimado ? '*' : ''), brl(m.rpa), pct(m.mono / m.rpa, 1), brl(m.das), brl(m.das27), brl(m.das27 - m.das), pct(m.das27 / m.das - 1, 1)]),
   ['Total', brl(totRpa), pct(R.mono_pct, 1), brl(totDas), brl(totDas27), brl(totDas27 - totDas), pct(totDas27 / totDas - 1, 1)]],
  [1250, 1450, 1150, 1450, 1550, 1338, 1450], { totalLast: true });
const tabAnual = table(['Item', 'Hoje (2026)', '2027 – Simples puro', 'Diferença'],
  [['Faturamento 12 meses (mesma base)', brl(R.fat12), brl(R.fat12), '–'],
   ['Fatia PIS/COFINS → CBS/IBS na receita monofásica', 'zerada', 'cobrada', '–'],
   ['DAS anual', brl(R.das_ano), brl(R.das27_ano), '+ ' + brl(aumAno)],
   ['DAS médio mensal', brl(R.das_ano / 12), brl(R.das27_ano / 12), '+ ' + brl(aumAno / 12)],
   ['Carga do DAS sobre o faturamento', pct(R.carga26), pct(R.carga27), '+ ' + pct(R.carga27 - R.carga26)]], [3838, 1900, 2000, 1900]);
const cen = [['Só impostos (com margem de ' + pct(R.margem, 0) + ')', R.reajustes[0]],
  [`Impostos + ${R.canal.toLowerCase()} (${pct(R.canal_pct, 1)})`, R.reajustes[1]],
  [`Impostos + ${R.canal.toLowerCase()} + ${R.despesas.toLowerCase()} (${pct(R.despesas_pct, 1)})`, R.reajustes[2]]];
const tabReaj = table(['Cenário', 'Reajuste necessário', 'R$ 100,00 passa a', 'R$ 250,00 passa a'],
  cen.map(([n, r]) => [n, pct(r), 'R$ ' + brl(100 * (1 + r)), 'R$ ' + brl(250 * (1 + r))]), [3938, 1900, 1900, 1900]);
const tabHib = table(['Cenário para 2027', 'Carga sobre o faturamento', 'Valor anual estimado'],
  [['Simples puro (IBS/CBS dentro do DAS)', pct(R.carga27), 'R$ ' + brl(R.das27_ano)],
   ['Híbrido (IBS/CBS fora do DAS, regime regular)', R.hibrido_confiavel ? pct(R.hibrido) : 'não calculável', R.hibrido_confiavel ? 'R$ ' + brl(R.hibrido * R.fat12) : '–'],
   ['Diferença (híbrido – puro)', R.hibrido_confiavel ? pct(R.hibrido - R.carga27) : '–', R.hibrido_confiavel ? 'R$ ' + brl(R.dif_hibrido) : '–']],
  [4438, 2600, 2600], { totalLast: true });
const leg = [
  ['Segregação da receita monofásica (regra atual)', 'LC 123/2006, art. 18, §4º-A, I'],
  ['Segregação a partir de 2027 (só monofásico e IBS/CBS por substituição)', 'LC 123, art. 18, §4º-A, I, na redação do art. 517 da LC 214/2025'],
  ['Partilha 2027-2028: PIS+COFINS viram CBS e IBS (Anexo I: CBS 15,33% e IBS 0,17%)', 'LC 214/2025, Anexo XVIII'],
  ['IBS de 0,05% + 0,05% e CBS reduzida em 0,1 p.p. em 2027-2028', 'LC 214/2025, arts. 344 e 347'],
  ['Simples fora do teste de 2026', 'LC 214/2025, art. 348, III, "c"'],
  ['Opção do Simples pelo regime regular de IBS/CBS (híbrido)', 'LC 214/2025, art. 41, §§ 3º e 4º; LC 123, art. 13, §§ 9º a 11'],
  ['Crédito de quem compra de empresa do Simples = valor cobrado no DAS', 'LC 123, art. 23, §1º-A (redação LC 227/2026)'],
  ['Prazos da opção para o 1º semestre de 2027: até 30/10/2026; cancelamento de 03/11 a 20/12/2026', 'Resolução CGSN 186/2026, art. 2º, com a redação da Resolução CGSN 194/2026']];
const recom = X.recomendacao || (hibridoMelhor
  ? `o regime híbrido sai cerca de R$ ${brl(-R.dif_hibrido)} por ano mais barato pela estimativa. Antes de optar, confirmar o perfil dos clientes (empresas que aproveitam crédito) e a alíquota de referência.`
  : `permanecer no Simples Nacional puro (IBS e CBS dentro do DAS).` + (R.hibrido_confiavel ? ` O regime híbrido custaria cerca de R$ ${brl(R.dif_hibrido)} a mais por ano.` : ''));
const doc = new Document({ creator: 'ROF Contabilidade', title: `Parecer – ${R.empresa} – Simples Nacional 2027`,
  styles: { default: { document: { run: { font: FONT, size: 22 } } } },
  numbering: { config: [{ reference: 'bul', levels: [{ level: 0, format: LevelFormat.BULLET, text: '•', alignment: AlignmentType.LEFT,
    style: { paragraph: { indent: { left: 540, hanging: 270 } } } }] }] },
  sections: [{ properties: { page: { margin: { top: 1134, bottom: 1134, left: 1134, right: 1134 } } },
    footers: { default: new Footer({ children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [
      new TextRun({ text: `ROF Contabilidade – Parecer tributário – ${R.empresa} – página `, font: FONT, size: 16, color: '7F7F7F' }),
      new TextRun({ children: [PageNumber.CURRENT], font: FONT, size: 16, color: '7F7F7F' })] })] }) },
    children: [
      new Paragraph({ alignment: AlignmentType.CENTER, spacing: { after: 60 }, children: [new TextRun({ text: 'PARECER TRIBUTÁRIO', bold: true, font: FONT, size: 32, color: AZUL })] }),
      new Paragraph({ alignment: AlignmentType.CENTER, spacing: { after: 240 }, border: { bottom: { style: BorderStyle.SINGLE, size: 8, color: AZUL, space: 6 } },
        children: [new TextRun({ text: 'Reforma Tributária: impacto no Simples Nacional a partir de 2027', font: FONT, size: 24, color: AZUL })] }),
      p([b('Cliente: '), t(X.cliente || `${R.empresa} – CNPJ ${R.cnpj}`)], AlignmentType.LEFT),
      p([b('Regime: '), t(X.regime || 'Simples Nacional')], AlignmentType.LEFT),
      p([b('Data: '), t(X.data || hoje)], AlignmentType.LEFT),
      h1('1. Resumo'),
      p(R.mono_pct > 0.05
        ? `Hoje ${pct(R.mono_pct, 0)} da venda da empresa é de produtos com PIS e COFINS monofásicos: esses tributos são pagos pelo fabricante/importador e saem zerados no DAS. A partir de 1º de janeiro de 2027 o PIS e a COFINS são substituídos pela CBS e pelo IBS, que não mantêm esse tratamento dentro do Simples. A parte do DAS que hoje fica zerada passa a ser cobrada.`
        : `Só ${pct(R.mono_pct, 1)} da venda da empresa é de produtos com PIS e COFINS monofásicos, por isso o efeito da troca de PIS/COFINS por CBS/IBS em 2027 é pequeno.`),
      bullet([b('Aumento do DAS: '), t(`cerca de ${pct(R.das27_ano / R.das_ano - 1, 1)}, ou R$ ${brl(aumAno / 12)} por mês (R$ ${brl(aumAno)} por ano), mantido o mesmo faturamento.`)]),
      bullet([b('Reajuste de preço para compensar: '), t(`de ${pct(R.reajustes[0])} a ${pct(R.reajustes[2])}, conforme os custos sobre a venda (item 4).`)]),
      bullet([b('Recomendação: '), t(recom)]),
      ...(X.resumo_extra || []).map(s => bullet(s)),
      h1(`2. Situação atual × 2027, mês a mês (${periodo})`),
      p('Valores de cada mês (relatórios do Domínio e guias DAS) comparados com o mesmo mês recalculado pela regra de 2027: mesmo faturamento, mesma faixa e mesma alíquota efetiva, apenas com a fatia de CBS/IBS cobrada sobre a receita que hoje é monofásica.'),
      tabMensal, gap(),
      ...(R.meses_estimados.length ? [p(`* Mês estimado (sem relatório na pasta): ${R.meses_estimados.join(', ')}.`)] : []),
      h1('3. Projeção anual com a mesma base de faturamento'),
      p('Faturamento dos últimos 12 meses aplicado como se já estivéssemos em 2027:'), tabAnual, gap(),
      p('A alíquota nominal e a parcela a deduzir das faixas continuam as mesmas em 2027 e 2028. Muda a partilha: a fatia que hoje é PIS e COFINS passa a ser CBS e IBS.'),
      h1('4. Quanto aumentar o preço'),
      p('O reajuste mantém o mesmo valor líquido por venda depois do DAS. Quando há custos cobrados em percentual do preço (comissão, taxa de cartão, frete), o reajuste precisa ser um pouco maior, porque esses custos sobem junto com o preço.'),
      tabReaj, gap(),
      h1('5. Simples puro ou híbrido'),
      p(`A lei permite que a empresa do Simples pague IBS e CBS fora do DAS, pelo regime regular, com débito sobre as vendas e crédito sobre as compras. Premissa: alíquota de IBS + CBS de ${pct(R.aliq_regular, 1)} e crédito integral sobre compras (${pct(R.compras_pct, 1)} do faturamento) e fretes (${pct(R.fretes_pct, 1)}).`),
      tabHib, gap(),
      ...(R.hibrido_confiavel ? [] : [p('As compras registradas superam o faturamento declarado no período; com isso a comparação com o regime híbrido não é confiável e não deve ser usada para decidir.')]),
      bullet('O regime híbrido só costuma compensar quando a maior parte dos clientes é empresa que aproveita crédito de IBS/CBS e as compras com crédito são altas.'),
      ...(X.puro_hibrido_extra || []).map(s => bullet(s)),
      p([b('Conclusão: '), t(recom + ' Caso a opção pelo regime regular tenha sido feita por engano, ela pode ser cancelada de 03/11 a 20/12/2026 no Portal do Simples Nacional.')]),
      h1('6. Base legal'), table(['Assunto', 'Base legal'], leg, [4638, 5000], { textLeft: true }), gap(),
      h1('7. Premissas e limitações'),
      bullet('Faturamento de 2027 igual ao dos últimos 12 meses e mesmo mix de produtos.'),
      bullet(`Percentuais de ${R.canal.toLowerCase()}, ${R.despesas.toLowerCase()} e margem são estimativas, ajustáveis na planilha.`),
      bullet('A comparação com o regime híbrido é estimativa: depende da alíquota de referência e do crédito efetivo das compras.'),
      ...(X.premissas_extra || []).map(s => bullet(s)),
      p([b('ROF Contabilidade')], AlignmentType.RIGHT)] }] });
Packer.toBuffer(doc).then(buf => { fs.writeFileSync(outPath, buf); console.log('ok', outPath); });
