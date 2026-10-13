"""Tabelas de apoio: CNAE -> anexo do Simples Nacional e regras de retenção (serviços tomados).

ATENÇÃO: a tabela de anexos é um ATALHO. A referência oficial é o Anexo VI da Resolução CGSN 140/2018
e o art. 18 da LC 123/2006 (§§ 5º-B a 5º-I, 5º-J e 5º-M - Fator R). Sempre que vier "conferir", olhar a
norma e o histórico do DAS da empresa antes de afirmar o anexo.
"""
import re

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
    '7319002': ('III', 'Promoção de vendas (padrão do escritório: Anexo III)'),
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


# ---------------------------------------------------------------- Item da LC 116 -> anexo do Simples e enquadramento de retenção
# item -> (anexo, descrição resumida, enquadramento sugerido para TOMADO)
# "V (Fator R)" = Anexo V, ou III se o Fator R >= 28% (não calculamos o Fator R aqui).
VFR = 'V (Fator R)'
ITENS_LC116 = {
    '1.01': (VFR, 'Análise e desenvolvimento de sistemas - conferir (III se elaboração de programa no estabelecimento, §5º-D)', 'servico_profissional'),
    '1.02': ('III', 'Programação (§5º-D)', 'sem_retencao'),
    '1.03': ('III', 'Processamento, armazenamento, hospedagem de dados', 'sem_retencao'),
    '1.04': ('III', 'Elaboração de programas de computador (§5º-D)', 'sem_retencao'),
    '1.05': ('III', 'Licenciamento/cessão de uso de programas (§5º-D)', 'sem_retencao'),
    '1.06': (VFR, 'Assessoria e consultoria em informática (§5º-I)', 'servico_profissional'),
    '1.07': (VFR, 'Suporte técnico em informática (§5º-I VI)', 'servico_profissional'),
    '1.08': ('III', 'Páginas eletrônicas (§5º-D)', 'sem_retencao'),
    '1.09': ('III', 'Disponibilização de conteúdo pela internet (streaming)', 'sem_retencao'),
    '2.01': (VFR, 'Pesquisa e desenvolvimento (§5º-I VI)', 'servico_profissional'),
    '3.02': ('?', 'Cessão de direito de uso de marcas - conferir', 'sem_retencao'),
    '3.03': ('III', 'Salões de festas, centros de convenções, espaços', 'sem_retencao'),
    '3.04': ('III', 'Locação/cessão de espaço, postes, dutos', 'sem_retencao'),
    '3.05': ('III', 'Cessão de andaimes, palcos, estruturas temporárias', 'sem_retencao'),
    '4.01': (VFR, 'Medicina e biomedicina (§5º-I I)', 'servico_profissional'),
    '4.02': ('III', 'Análises clínicas, imagem, radiologia (§5º-D)', 'servico_profissional'),
    '4.03': (VFR, 'Hospitais, clínicas, ambulatórios - conferir', 'servico_profissional'),
    '4.04': (VFR, 'Instrumentação cirúrgica', 'servico_profissional'),
    '4.05': (VFR, 'Acupuntura (§5º-I IV)', 'servico_profissional'),
    '4.06': (VFR, 'Enfermagem (§5º-I I)', 'servico_profissional'),
    '4.07': (VFR, 'Serviços farmacêuticos - conferir', 'servico_profissional'),
    '4.08': ('III / ' + VFR, 'Fisioterapia = III (§5º-B); terapia ocupacional e fono = V (Fator R)', 'servico_profissional'),
    '4.09': (VFR, 'Terapias diversas - conferir', 'servico_profissional'),
    '4.10': (VFR, 'Nutrição (§5º-I IV)', 'servico_profissional'),
    '4.11': (VFR, 'Obstetrícia', 'servico_profissional'),
    '4.12': (VFR, 'Odontologia (§5º-I III)', 'servico_profissional'),
    '4.13': (VFR, 'Ortóptica', 'servico_profissional'),
    '4.14': ('III', 'Próteses sob encomenda (§5º-D)', 'sem_retencao'),
    '4.15': (VFR, 'Psicanálise (§5º-I IV)', 'servico_profissional'),
    '4.16': (VFR, 'Psicologia (§5º-I IV)', 'servico_profissional'),
    '4.17': ('III', 'Casas de repouso, creches, asilos', 'sem_retencao'),
    '4.18': (VFR, 'Inseminação artificial, fertilização', 'servico_profissional'),
    '4.19': (VFR, 'Bancos de sangue, leite, pele, olhos', 'servico_profissional'),
    '4.20': ('III', 'Coleta de sangue, leite, tecidos', 'sem_retencao'),
    '4.21': ('III', 'Unidade de atendimento/remoção de pacientes - conferir', 'sem_retencao'),
    '4.22': ('?', 'Planos de medicina de grupo - conferir', 'sem_retencao'),
    '4.23': ('?', 'Planos de saúde - conferir', 'sem_retencao'),
    '5.01': (VFR, 'Medicina veterinária (§5º-I II)', 'servico_profissional'),
    '5.02': (VFR, 'Hospitais e clínicas veterinárias', 'servico_profissional'),
    '5.03': (VFR, 'Laboratório de análise veterinária', 'servico_profissional'),
    '5.04': ('III', 'Inseminação animal', 'sem_retencao'),
    '5.05': ('III', 'Bancos de sangue animal', 'sem_retencao'),
    '5.06': ('III', 'Coleta de sangue animal', 'sem_retencao'),
    '5.07': ('III', 'Unidade de atendimento veterinário', 'sem_retencao'),
    '5.08': ('III', 'Guarda, banho, tosa, adestramento de animais', 'sem_retencao'),
    '5.09': ('?', 'Planos de atendimento veterinário - conferir', 'sem_retencao'),
    '6.01': ('III', 'Barbearia, cabeleireiros, manicure', 'sem_retencao'),
    '6.02': ('III', 'Esteticistas, tratamento de pele', 'sem_retencao'),
    '6.03': ('III', 'Banhos, saunas, massagens', 'sem_retencao'),
    '6.04': ('III', 'Ginástica, dança, esportes, artes marciais (§5º-D)', 'sem_retencao'),
    '6.05': ('III', 'Centros de emagrecimento, spa', 'sem_retencao'),
    '6.06': ('III', 'Tatuagens, piercings', 'sem_retencao'),
    '7.01': (VFR, 'Engenharia, arquitetura, geologia, urbanismo (§5º-I VI)', 'servico_profissional'),
    '7.02': ('IV', 'Execução de obras de construção civil (§5º-C)', 'construcao_empreitada'),
    '7.03': (VFR, 'Projetos e planos de engenharia (§5º-I VI)', 'servico_profissional'),
    '7.04': ('IV', 'Demolição (§5º-C)', 'construcao_empreitada'),
    '7.05': ('IV', 'Reparação, conservação e reforma de edifícios (§5º-C)', 'construcao_empreitada'),
    '7.06': ('IV', 'Colocação de tapetes, pisos, cortinas, divisórias - conferir', 'construcao_empreitada'),
    '7.07': ('IV', 'Recuperação, raspagem, polimento de pisos - conferir', 'construcao_empreitada'),
    '7.08': ('IV', 'Calafetação', 'construcao_empreitada'),
    '7.09': ('IV', 'Varrição, coleta e tratamento de lixo (limpeza §5º-C)', 'limpeza_conservacao'),
    '7.10': ('IV', 'Limpeza, manutenção e conservação de imóveis (§5º-C)', 'limpeza_conservacao'),
    '7.11': ('IV', 'Decoração e jardinagem, paisagismo (§5º-C)', 'limpeza_conservacao'),
    '7.12': ('III', 'Controle e tratamento de efluentes/agentes físicos - conferir', 'sem_retencao'),
    '7.13': ('III', 'Dedetização, desinfecção, desratização - conferir', 'limpeza_conservacao'),
    '7.16': ('III', 'Florestamento, reflorestamento - conferir', 'sem_retencao'),
    '7.17': ('IV', 'Escoramento, contenção de encostas (§5º-C)', 'construcao_empreitada'),
    '7.18': ('IV', 'Limpeza e dragagem de rios, portos, canais', 'limpeza_conservacao'),
    '7.19': (VFR, 'Acompanhamento e fiscalização de obras de engenharia', 'servico_profissional'),
    '7.20': (VFR, 'Aerofotogrametria, cartografia, topografia (§5º-I VI)', 'servico_profissional'),
    '7.21': (VFR, 'Pesquisa, perfuração, exploração de petróleo/gás', 'servico_profissional'),
    '7.22': ('III', 'Nucleação e bombardeamento de nuvens', 'sem_retencao'),
    '8.01': ('III', 'Ensino regular (§5º-B)', 'sem_retencao'),
    '8.02': ('III', 'Instrução, treinamento, cursos, avaliação de conhecimentos', 'sem_retencao'),
    '9.01': ('III', 'Hospedagem', 'sem_retencao'),
    '9.02': ('III', 'Agenciamento de turismo / agência de viagens (§5º-B)', 'sem_retencao'),
    '9.03': ('III', 'Guias de turismo', 'sem_retencao'),
    '10.01': (VFR, 'Agenciamento/corretagem de câmbio, seguros, planos (corretagem de SEGUROS = III)', 'comissao_representacao'),
    '10.02': (VFR, 'Agenciamento/corretagem de títulos e valores mobiliários', 'comissao_representacao'),
    '10.03': (VFR, 'Agenciamento/corretagem de direitos de propriedade', 'comissao_representacao'),
    '10.04': ('IMPEDITIVO?', 'Arrendamento mercantil / faturização (factoring) - conferir', 'assessoria_credito_mercadologica'),
    '10.05': (VFR, 'Intermediação de bens móveis/imóveis (corretagem de IMÓVEIS = III)', 'comissao_representacao'),
    '10.06': (VFR, 'Agenciamento marítimo', 'comissao_representacao'),
    '10.07': (VFR, 'Agenciamento de notícias', 'comissao_representacao'),
    '10.08': (VFR, 'Agenciamento de publicidade e propaganda', 'propaganda_publicidade'),
    '10.09': (VFR, 'Representação de qualquer natureza / representação comercial (§5º-I VII)', 'comissao_representacao'),
    '10.10': (VFR, 'Distribuição de bens de terceiros', 'comissao_representacao'),
    '11.01': ('III', 'Guarda e estacionamento de veículos', 'sem_retencao'),
    '11.02': ('IV', 'Vigilância, segurança ou monitoramento (§5º-C)', 'seguranca_vigilancia'),
    '11.03': ('IV', 'Escolta - conferir', 'seguranca_vigilancia'),
    '11.04': ('III', 'Armazenamento, depósito, carga e descarga', 'sem_retencao'),
    '12': ('III', 'Diversões, lazer, entretenimento, shows, eventos', 'sem_retencao'),
    '13.02': ('III', 'Fonografia, gravação de sons', 'sem_retencao'),
    '13.03': ('III', 'Fotografia e cinematografia', 'sem_retencao'),
    '13.04': ('III', 'Reprografia, microfilmagem, digitalização', 'sem_retencao'),
    '13.05': ('III', 'Composição gráfica, clicheria (sob encomenda) - conferir', 'sem_retencao'),
    '14': ('III', 'Manutenção, conserto, assistência técnica, instalação e montagem', 'manutencao'),
    '15': ('?', 'Serviços bancários/financeiros - conferir', 'sem_retencao'),
    '16': ('III', 'Transporte municipal', 'transporte'),
    '17.01': (VFR, 'Assessoria ou consultoria (§5º-I IX)', 'servico_profissional'),
    '17.02': ('III', 'Datilografia, digitação, apoio administrativo, secretaria', 'sem_retencao'),
    '17.03': (VFR, 'Planejamento, coordenação, programação ou organização técnica, financeira ou administrativa', 'servico_profissional'),
    '17.04': (VFR, 'Recrutamento, agenciamento, seleção de mão de obra - conferir', 'servico_profissional'),
    '17.05': ('IMPEDITIVO', 'Fornecimento de mão de obra (cessão - vedada fora do Anexo IV)', 'locacao_mao_obra'),
    '17.06': ('III', 'Propaganda e publicidade, promoção de vendas (padrão do escritório: Anexo III)', 'propaganda_publicidade'),
    '17.08': ('?', 'Franquia (franchising) - conferir', 'sem_retencao'),
    '17.09': (VFR, 'Perícias, laudos, exames técnicos (§5º-I VIII)', 'servico_profissional'),
    '17.10': ('III', 'Planejamento e organização de feiras, congressos, eventos', 'sem_retencao'),
    '17.11': ('III', 'Organização de festas, bufê', 'sem_retencao'),
    '17.12': (VFR, 'Administração em geral (§5º-I IX)', 'servico_profissional'),
    '17.13': (VFR, 'Leilão (§5º-I VIII)', 'servico_profissional'),
    '17.14': ('IV', 'Advocacia (§5º-C VII)', 'servico_profissional'),
    '17.15': (VFR, 'Arbitragem', 'servico_profissional'),
    '17.16': (VFR, 'Auditoria (§5º-I IX)', 'servico_profissional'),
    '17.17': (VFR, 'Análise de organização e métodos', 'servico_profissional'),
    '17.18': (VFR, 'Atuária e cálculos técnicos', 'servico_profissional'),
    '17.19': ('III', 'Contabilidade (§5º-B XIV)', 'servico_profissional'),
    '17.20': (VFR, 'Consultoria e assessoria econômica ou financeira (§5º-I IX)', 'servico_profissional'),
    '17.21': (VFR, 'Estatística', 'servico_profissional'),
    '17.22': ('III', 'Cobrança em geral - conferir', 'assessoria_credito_mercadologica'),
    '17.23': ('IMPEDITIVO?', 'Assessoria/análise de crédito, factoring - conferir', 'assessoria_credito_mercadologica'),
    '17.24': (VFR, 'Apresentação de palestras, conferências, seminários', 'servico_profissional'),
    '17.25': ('III', 'Inserção de textos, imagens em mídia - conferir', 'propaganda_publicidade'),
    '18.01': (VFR, 'Regulação de sinistros, inspeção e avaliação de riscos', 'servico_profissional'),
    '19.01': ('?', 'Loterias, bingos - conferir', 'sem_retencao'),
    '20': ('III', 'Serviços portuários, aeroportuários, ferroportuários, terminais', 'sem_retencao'),
    '22.01': ('III', 'Exploração de rodovia', 'sem_retencao'),
    '23.01': (VFR, 'Programação e comunicação visual, desenho industrial (design §5º-I VI)', 'servico_profissional'),
    '24.01': ('III', 'Chaveiros, carimbos, placas, sinalização visual', 'sem_retencao'),
    '25': ('III', 'Serviços funerários', 'sem_retencao'),
    '26.01': ('III', 'Coleta, remessa ou entrega de correspondências (courier)', 'transporte'),
    '27.01': ('III', 'Assistência social - conferir', 'sem_retencao'),
    '28.01': (VFR, 'Avaliação de bens e serviços (§5º-I VIII)', 'servico_profissional'),
    '29.01': (VFR, 'Biblioteconomia', 'servico_profissional'),
    '30.01': (VFR, 'Biologia, biotecnologia e química', 'servico_profissional'),
    '31.01': (VFR, 'Técnicos em edificações, eletrônica, mecânica, telecomunicações', 'servico_profissional'),
    '32.01': (VFR, 'Desenhos técnicos (§5º-I VI)', 'servico_profissional'),
    '33.01': (VFR, 'Desembaraço aduaneiro, despachantes (§5º-I V)', 'servico_profissional'),
    '34.01': ('III', 'Investigações particulares, detetives - conferir', 'sem_retencao'),
    '35.01': (VFR, 'Reportagem, assessoria de imprensa, jornalismo, relações públicas (§5º-I X)', 'servico_profissional'),
    '36.01': (VFR, 'Meteorologia', 'servico_profissional'),
    '37.01': ('III', 'Artistas, atletas, modelos, manequins - conferir', 'sem_retencao'),
    '38.01': (VFR, 'Museologia', 'servico_profissional'),
    '39.01': ('III', 'Ourivesaria e lapidação (material do tomador)', 'sem_retencao'),
    '40.01': ('III', 'Obras de arte sob encomenda - conferir', 'sem_retencao'),
}
# ISS: itens em que o TOMADOR pessoa jurídica é responsável pela retenção (LC 116 art. 6º §2º II),
# além dos serviços do art. 3º prestados no município do tomador e da lei de cada município.
ITENS_RETENCAO_ISS = {'3.05', '7.02', '7.04', '7.05', '7.09', '7.10', '7.12', '7.16', '7.17', '7.19',
                      '11.02', '17.05', '17.10'}


def item_lc116(cod):
    """'171901' / '17.19' / '1719' / '7.02' / '070201' -> '17.19' / '7.02'."""
    c = str(cod or '').strip()
    if not c:
        return ''
    if '.' in c:
        a, b = c.split('.')[:2]
        return f'{int(a)}.{re.sub(r"\D", "", b)[:2].zfill(2)}' if a.isdigit() else ''
    d = re.sub(r'\D', '', c)
    if len(d) == 3: d = '0' + d
    if len(d) < 4: return ''
    return f'{int(d[:2])}.{d[2:4]}'


def anexo_item(cod):
    """Retorna (item, anexo, descrição, enquadramento sugerido)."""
    it = item_lc116(cod)
    if not it:
        return ('', '?', 'Item da LC 116 não identificado', '')
    for k in (it, it.split('.')[0]):
        if k in ITENS_LC116:
            return (it,) + ITENS_LC116[k]
    return (it, '?', 'Item fora da tabela - conferir na LC 116 e no Anexo VI da Res. CGSN 140/2018', '')


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
