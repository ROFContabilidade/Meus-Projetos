"""Monta notas.json a partir de lidas.tsv (transcrição dos DANFSe de 09/2026 - VF Chaveiro)."""
import json, csv
INFO = "NBS: 1.2606.00.00 - Serviços pessoais não classificados em posições anteriores Totais Aproximados dos Tributos cfe. Lei nº 12.741/2012: 6.00% sobre o valor do serviço (Simples Nacional);"
ITEM_TXT = "Item 24.01 (chaveiros) não corresponde ao serviço descrito ({}) - o código adequado seria 14.01 (manutenção/conservação) ou 14.06 (instalação e montagem de aparelhos). O anexo continua III."
MERC = {311: 'fontes, baterias, câmera e DVR', 313: 'botoeiras', 314: 'roldanas', 315: 'refletores LED', 316: 'interfone', 319: 'central do motor',
        320: 'porteiro eletrônico e fonte', 322: 'câmeras IP, fonte, fotocélulas e roteador', 325: 'fonte e bateria', 327: 'controle e tag',
        328: 'luminárias LED', 330: 'módulo relé', 331: '10 controles (R$ 70) e 10 tags (R$ 40)', 332: '2 controles (R$ 60) e 5 tags (R$ 25)',
        334: 'caixa de proteção, porta-cadeado, cadeado e suporte', 335: '3 suportes do motor', 336: 'fotocélula', 337: 'botoeira',
        338: 'central e capacitor do motor', 339: 'cabos de alta tensão e bateria', 345: 'painel de tag/senha e bateria', 347: 'câmera e conectores',
        348: 'fechadura elétrica'}
EXTRA = {
    311: ['Descrição traz forma de pagamento (R$ 2.400 à vista + R$ 1.220 em 01/10); nota pelo valor total, o que está correto pela competência. Conferir o recebimento de outubro.'],
    315: ['Serviço prestado em São José dos Pinhais (tomador de SJP), com ISS para Curitiba. Correto para o item 24.01, pois não está no art. 3º da LC 116. Se o serviço for reclassificado (por exemplo, instalação elétrica 7.02/14.06), conferir o município do ISS.'],
    322: ['Descrição diz "valor do saldo de 50% do valor do serviço". Conferir se a nota dos outros 50% foi emitida (mês anterior?) e se o total fecha com o orçamento.'],
    333: ['Nota sem código NBS (as demais trazem 1.2606.00.00).', 'Serviço realizado em 11/09 e nota emitida em 21/09, dentro do mês; sem efeito na competência.'],
    338: ['ALERTA: Tomador em Colombo/PR, mas o local da prestação foi informado como Curitiba. Confirmar onde o serviço foi feito (condomínio em Colombo?) e corrigir o local da prestação se for o caso.'],
    347: ['Erro de digitação na discriminação ("CONECOTORES").'],
    348: ['ALERTA: Tomador em Colombo/PR, mas o local da prestação foi informado como Curitiba. Confirmar onde o serviço foi feito e corrigir o local da prestação se for o caso.'],
    358: ['ALERTA: Nota emitida em 06/10/2026 com competência 21/09/2026 (emissão retroativa). Entra no faturamento de SETEMBRO. Conferir se o PGDAS-D de 09/2026 já considerou e se as notas 349 a 357 (outubro) não têm competência de setembro.'],
}
notas = []
for r in csv.reader(open('lidas.tsv', encoding='utf-8'), delimiter='\t'):
    num, dps, dt, toma, nome, desc, val = r[:7]
    flag = r[7] if len(r) > 7 else ''
    n = int(num)
    ap = [ITEM_TXT.format(desc.lower()[:70] + ('...' if len(desc) > 70 else ''))]
    if n in MERC:
        ap.append(f'ALERTA: A nota inclui peças ou equipamentos ({MERC[n]}). Pela LC 116, item 14.01, peças e partes empregadas ficam sujeitas ao ICMS: separar o material em NF-e (Anexo I, comércio) e deixar na NFS-e só a mão de obra (Anexo III). A empresa não tem CNAE de comércio.')
    ap += EXTRA.get(n, [])
    notas.append({
        'arquivo': f'{num}.pdf', 'layout': 'NFS-e Nacional', 'numero': num, 'serie_dps': '70000', 'numero_dps': dps,
        'data_emissao': '2026-10-06' if n == 358 else dt, 'competencia': dt, 'situacao': 'Autorizada',
        'prestador_cnpj': '46870723000142', 'prestador_nome': 'LUANNA GVM FERREIRA LTDA', 'prestador_regime_sn': 'ME/EPP Simples',
        'tomador_doc': toma, 'tomador_nome': nome, 'item_lc116': '24.01.01',
        'atividade': 'Serviços de chaveiros, confecção de carimbos e congêneres.',
        'nbs': '' if flag == 'SEM_NBS' else '1.2606.00.00', 'descricao': desc,
        'info_complementar': INFO.split('posições anteriores ')[1] if flag == 'SEM_NBS' else INFO,
        'valor_servico': float(val), 'base_iss': None, 'aliquota_iss': None, 'valor_iss': None, 'iss_retido': 'Não',
        'irrf': None, 'csll': None, 'pis': None, 'cofins': None, 'inss': None, 'valor_liquido': float(val),
        'anexo': 'III', 'apontamentos': ap})
json.dump(notas, open('notas.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print(len(notas), round(sum(x['valor_servico'] for x in notas), 2),
      round(sum(x['valor_servico'] for x in notas if int(x['numero']) in MERC), 2))
