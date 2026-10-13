"""Tabelas de apoio: CNAE -> anexo do Simples Nacional e regras de retenção (serviços tomados).

ATENÇÃO: a tabela de anexos é um ATALHO. A referência oficial é o Anexo VI da Resolução CGSN 140/2018
e o art. 18 da LC 123/2006 (§§ 5º-B a 5º-I, 5º-J e 5º-M - Fator R). Sempre que vier "conferir", olhar a
norma e o histórico do DAS da empresa antes de afirmar o anexo.
"""

# Subclasse (7 dígitos, sem pontuação) ou prefixo (2 a 5 dígitos) -> (anexo, observação)
# Busca do mais específico para o mais genérico.
ANEXOS = {
    # --- Anexo III direto
    '6920601': ('III', 'Escritório de contabilidade (LC 123 art. 18 §5º-B XIV)'),
    '6622300': ('III', 'Corretagem de seguros (§5º-B)'),
    '6821801': ('III', 'Corretagem na compra e venda de imóveis'),
    '6821802': ('III', 'Corretagem no aluguel de imóveis'),
    '6822600': ('III', 'Gestão e administração de imóveis - conferir (pode ser V se "administração")'),
    '8650004': ('III', 'Fisioterapia (§5º-B IX)'),
    '8640202': ('III', 'Laboratório clínico (§5º-D)'),
    '8640205': ('III', 'Diagnóstico por imagem (§5º-D)'),
    '8640207': ('III', 'Diagnóstico por imagem sem radiação (§5º-D)'),
    '3250706': ('III', 'Prótese dentária (§5º-D - serviços de prótese em geral)'),
    '6201501': ('III', 'Software sob encomenda (§5º-D, se feito no estabelecimento) - conferir com o tratamento usado pelo escritório (Fator R)'),
    '6202300': ('III', 'Software customizável (§5º-D) - conferir'),
    '6203100': ('III', 'Software não customizável (§5º-D) - conferir'),
    '6204000': ('V/III Fator R', 'Consultoria em TI (§5º-I) - Fator R'),
    '6209100': ('V/III Fator R', 'Suporte técnico em TI (§5º-I VI) - Fator R'),
    '6311900': ('III', 'Tratamento de dados/hospedagem - conferir'),
    '6319400': ('III', 'Portais e provedores de conteúdo - conferir'),
    '6201502': ('III', 'Web design (§5º-D - páginas eletrônicas no estabelecimento) - conferir'),
    '7420001': ('III', 'Fotografia'), '7420004': ('III', 'Filmagem de festas e eventos'),
    '6911701': ('IV', 'Advocacia (§5º-C VII)'),
    '6920602': ('V/III Fator R', 'Consultoria e auditoria contábil e tributária (§5º-I IX)'),
    '7319002': ('V/III Fator R', 'Promoção de vendas - conferir'),
    '7319003': ('V/III Fator R', 'Marketing direto (§5º-I X)'),
    '7490104': ('V/III Fator R', 'Intermediação e agenciamento de serviços e negócios (§5º-I VII/XI)'),
    '8630501': ('V/III Fator R', 'Atividade médica ambulatorial com procedimentos (§5º-I I)'),
    '8630502': ('V/III Fator R', 'Atividade médica ambulatorial com exames (§5º-I I)'),
    '8630503': ('V/III Fator R', 'Atividade médica ambulatorial restrita a consultas (§5º-I I)'),
    '8630504': ('V/III Fator R', 'Odontologia (§5º-I III)'),
    '8650001': ('V/III Fator R', 'Enfermagem (§5º-I I)'),
    '8650002': ('V/III Fator R', 'Nutrição (§5º-I IV)'),
    '8650003': ('V/III Fator R', 'Psicologia e psicanálise (§5º-I IV)'),
    '8650005': ('V/III Fator R', 'Terapia ocupacional (§5º-I IV)'),
    '8650006': ('V/III Fator R', 'Fonoaudiologia (§5º-I IV)'),
    '8650007': ('V/III Fator R', 'Terapia de nutrição enteral/parenteral - conferir'),
    '8690901': ('V/III Fator R', 'Práticas integrativas - conferir (acupuntura §5º-I IV)'),
    '8690903': ('V/III Fator R', 'Acupuntura (§5º-I IV)'),
    '8690904': ('V/III Fator R', 'Podologia (§5º-I IV)'),
    '7500100': ('V/III Fator R', 'Medicina veterinária (§5º-I II)'),
    '8130300': ('IV', 'Paisagismo (§5º-C)'),
    '8011101': ('IV', 'Vigilância e segurança privada (§5º-C)'),
    '8011102': ('IV', 'Segurança privada - transporte de valores - conferir'),
    '8121400': ('IV', 'Limpeza em prédios e domicílios (§5º-C)'),
    '8129000': ('IV', 'Limpeza não especificada (§5º-C)'),
    '8111700': ('IV', 'Serviços combinados para apoio a edifícios (limpeza/conservação) - conferir'),
    '7810800': ('IMPEDITIVO?', 'Seleção e agenciamento de mão de obra - conferir (cessão de mão de obra é vedada fora do Anexo IV)'),
    '7820500': ('IMPEDITIVO', 'Locação de mão de obra temporária (cessão de mão de obra - LC 123 art. 17 XII)'),
    '7830200': ('IMPEDITIVO', 'Fornecimento e gestão de RH para terceiros (cessão de mão de obra)'),
    '6462000': ('IMPEDITIVO', 'Holding de instituições não financeiras'),
    '6463800': ('IMPEDITIVO', 'Outras sociedades de participação'),
    '6619302': ('V/III Fator R', 'Correspondente de instituição financeira - conferir'),
    '4520001': ('III + I', 'Manutenção mecânica de veículos: serviço III, peças I'),
    '5611201': ('I', 'Restaurante (fornecimento de alimentação = comércio)'),
    '5611203': ('I', 'Lanchonete'),
    '5620101': ('I', 'Fornecimento de alimentos para empresas - conferir'),
    '5510801': ('III', 'Hotel'),
    '4930202': ('III', 'Transporte rodoviário de cargas intermunicipal (ICMS, sem ISS)'),
    '4930201': ('III', 'Transporte rodoviário de cargas municipal (ISS)'),
    '8599604': ('III', 'Treinamento em desenvolvimento profissional'),
    '8211300': ('III', 'Serviços combinados de escritório'),
    '8219999': ('III', 'Preparação de documentos e apoio administrativo'),
    '9602501': ('III', 'Cabeleireiros, manicure e pedicure'),
    '9602502': ('III', 'Estética e cuidados com a beleza'),
    '9313100': ('III', 'Academia de condicionamento físico (§5º-D)'),
    '8591100': ('III', 'Ensino de esportes (§5º-D)'),
    '8592999': ('III', 'Ensino de arte e cultura'),
    '8593700': ('III', 'Ensino de idiomas'),
    '7911200': ('III', 'Agência de viagens (§5º-B)'),
    # --- Prefixos (divisões/grupos)
    '461': ('V/III Fator R', 'Representação comercial / intermediação (§5º-I VII)'),
    '41': ('IV', 'Construção de edifícios (§5º-C)'), '42': ('IV', 'Obras de infraestrutura (§5º-C)'),
    '43': ('IV', 'Serviços especializados para construção (§5º-C) - conferir instalação/manutenção (pode ser III)'),
    '45': ('I', 'Comércio de veículos/peças (serviço de manutenção = III)'),
    '46': ('I', 'Comércio atacadista'), '47': ('I', 'Comércio varejista'),
    '49': ('III', 'Transporte terrestre - conferir municipal x intermunicipal'),
    '33': ('III', 'Manutenção e reparação de máquinas'),
    '58': ('III', 'Edição - conferir (pode ser II se gráfica/industrial)'),
    '59': ('III', 'Audiovisual (produções artísticas e culturais)'),
    '69': ('V/III Fator R', 'Atividades jurídicas/contábeis - conferir subclasse'),
    '70': ('V/III Fator R', 'Consultoria em gestão (§5º-I IX)'),
    '71': ('V/III Fator R', 'Arquitetura, engenharia, testes e análises técnicas (§5º-I VI)'),
    '72': ('V/III Fator R', 'Pesquisa e desenvolvimento (§5º-I VI)'),
    '731': ('V/III Fator R', 'Publicidade (§5º-I X)'),
    '732': ('V/III Fator R', 'Pesquisa de mercado (§5º-I VI/IX)'),
    '741': ('V/III Fator R', 'Design e decoração de interiores - conferir (decoração de interiores = IV §5º-C)'),
    '749': ('V/III Fator R', 'Atividades profissionais/técnicas (§5º-I) - conferir'),
    '77': ('III', 'Locação de bens móveis (§5º-B)'),
    '82': ('III', 'Serviços de escritório e apoio administrativo'),
    '85': ('III', 'Educação (§5º-B)'),
    '86': ('V/III Fator R', 'Saúde - conferir subclasse'),
    '90': ('III', 'Atividades artísticas e culturais'),
    '93': ('III', 'Esporte e lazer'),
    '95': ('III', 'Reparação de equipamentos e objetos'),
    '96': ('III', 'Serviços pessoais'),
}
# Indústria em geral (divisões 10 a 33, exceto as acima) -> Anexo II
for d in range(10, 33):
    ANEXOS.setdefault(f'{d:02d}', ('II', 'Indústria'))


def anexo_cnae(cnae):
    c = ''.join(ch for ch in str(cnae) if ch.isdigit()).zfill(7)
    for n in (7, 5, 4, 3, 2):
        if c[:n] in ANEXOS:
            return ANEXOS[c[:n]]
    return ('?', 'CNAE fora da tabela - consultar Anexo VI da Resolução CGSN 140/2018')


def fmt_cnae(cnae):
    c = ''.join(ch for ch in str(cnae) if ch.isdigit()).zfill(7)
    return f'{c[:4]}-{c[4]}/{c[5:]}'


# ---------------------------------------------------------------- Retenções em serviços TOMADOS
# enquadramento -> (IRRF %, CSRF %, INSS %, descrição/base legal)
# INSS 11% só quando houver CESSÃO DE MÃO DE OBRA ou EMPREITADA (IN RFB 2.110/2022 arts. 108 a 120).
RETENCOES = {
    'servico_profissional': (1.5, 4.65, 0, 'Serviço profissional (RIR/2018 art. 714 §1º; Lei 10.833/03 art. 30)'),
    'limpeza_conservacao': (1.0, 4.65, 11, 'Limpeza/conservação (RIR art. 716; Lei 10.833 art. 30; INSS cessão/empreitada)'),
    'seguranca_vigilancia': (1.0, 4.65, 11, 'Segurança/vigilância (RIR art. 716; Lei 10.833 art. 30; INSS cessão)'),
    'locacao_mao_obra': (1.0, 4.65, 11, 'Locação/cessão de mão de obra (RIR art. 716; Lei 10.833 art. 30; INSS)'),
    'manutencao': (0, 4.65, 0, 'Manutenção (Lei 10.833 art. 30) - INSS 11% se houver cessão de mão de obra/empreitada'),
    'assessoria_credito_mercadologica': (1.5, 4.65, 0, 'Assessoria creditícia/mercadológica, gestão de crédito, factoring (Lei 10.833 art. 30)'),
    'comissao_representacao': (1.5, 0, 0, 'Comissão/corretagem/representação comercial (RIR art. 718)'),
    'propaganda_publicidade': (1.5, 0, 0, 'Propaganda e publicidade (RIR art. 718) - conferir se é serviço profissional'),
    'construcao_empreitada': (0, 0, 11, 'Construção civil por empreitada/subempreitada (INSS 11%; ISS no local da obra)'),
    'transporte': (0, 0, 0, 'Transporte (sem IRRF/CSRF; INSS só se cessão de mão de obra)'),
    'sem_retencao': (0, 0, 0, 'Atividade sem retenção federal'),
}
DISPENSA = 10.00  # IRRF e CSRF: dispensado quando o valor a reter for <= R$ 10,00; INSS: < R$ 10,00


def retencoes_esperadas(nota):
    """Calcula IRRF/CSRF/INSS esperados para uma nota tomada.
    nota: dict com valor_servico, base_inss (opcional), enquadramento, prestador_simples (bool),
          prestador_mei (bool), prestador_anexo_iv (bool), cessao_mao_obra (bool, opcional)."""
    enq = nota.get('enquadramento') or 'sem_retencao'
    ir, cs, inss, desc = RETENCOES.get(enq, (0, 0, 0, 'enquadramento desconhecido'))
    obs = [desc]
    if enq == 'manutencao' and nota.get('cessao_mao_obra'):
        inss = 11
    v = float(nota.get('valor_servico') or 0)
    if nota.get('prestador_mei'):
        ir = cs = inss = 0; obs.append('Prestador MEI: sem retenção de IRRF/CSRF/INSS (conferir cessão de mão de obra p/ MEI)')
    elif nota.get('prestador_simples'):
        if ir or cs:
            obs.append('Prestador do Simples: sem IRRF (IN SRF 765/2007) e sem CSRF (IN SRF 459/2004 art. 3º)')
        ir = cs = 0
        if inss and not nota.get('prestador_anexo_iv'):
            inss = 0; obs.append('Simples fora do Anexo IV: sem retenção de INSS 11%')
    base_inss = float(nota.get('base_inss') or v)
    r = {'irrf': round(v * ir / 100, 2), 'csrf': round(v * cs / 100, 2), 'inss': round(base_inss * inss / 100, 2)}
    if 0 < r['irrf'] <= DISPENSA: obs.append(f"IRRF {r['irrf']:.2f} <= R$ 10,00: dispensado"); r['irrf'] = 0
    if 0 < r['csrf'] <= DISPENSA: obs.append(f"CSRF {r['csrf']:.2f} <= R$ 10,00: dispensada"); r['csrf'] = 0
    if 0 < r['inss'] < DISPENSA: obs.append(f"INSS {r['inss']:.2f} < R$ 10,00: dispensado"); r['inss'] = 0
    r['aliquotas'] = f'IRRF {ir}% | CSRF {cs}% | INSS {inss}%'
    r['obs'] = '; '.join(obs)
    return r
