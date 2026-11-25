---
name: rof-contabilidade-rja-oliveira
description: "R J A OLIVEIRA LTDA (VOCE ENTREGA TECNOLOGIA), CNPJ 24.725.950/0001-41, código 83 no Domínio, Simples Nacional desde 01/01/2025 (MEI até 31/12/2023). Lançamentos contábeis, conciliação bancária (Inter, Mercado Pago, Nubank) e TXT para o Domínio desta empresa. Usar automaticamente quando o usuário mencionar R J A, RJA, Raul Jose Alves de Oliveira, Voce Entrega, o CNPJ 24.725.950/0001-41, a empresa 83, ou enviar extrato, razão, balancete, notas ou guias dela."
---

# ROF Contabilidade: R J A OLIVEIRA LTDA (empresa 83)

**Antes de tudo, siga o roteiro do `rof-analista` (cérebro).** Esta skill só traz o que é da empresa.
Em conflito, vale: decisão registrada da contadora → cérebro → esta skill.

- Dados: `references/empresa.json`
- Classificação: `references/classificacao.md`
- Decisões já tomadas: `references/decisoes.md` (procure pelo favorecido ou pelo valor, sem ler o arquivo inteiro)
- Plano de contas do Domínio (exportado em 25/11/2026): `references/plano_contas.csv`
- Leiaute TXT e padrão ROF: `references/dominio.md`, `references/padrao_rof.md`

## Dados da empresa

| Campo | Informação |
|---|---|
| Razão social | R J A OLIVEIRA LTDA |
| Nome fantasia | VOCE ENTREGA TECNOLOGIA |
| CNPJ | 24.725.950/0001-41 (24725950000141) |
| Código Domínio | 83 |
| Endereço | Rua Laudelina Ferreira Colere, 4, casa, Maracanã, Colombo/PR, CEP 83408-505 |
| Abertura | 04/05/2016 · capital social R$ 30.000,00 |
| Regime | Simples Nacional desde 01/01/2025 (Receita, consultado em 25/11/2026). Foi MEI de 04/05/2016 a 31/12/2023. **O regime de 2024 não foi confirmado.** |
| CNAE principal | 74.90-1-04 Intermediação e agenciamento de serviços e negócios em geral |
| CNAEs secundários | 47.52-1, 47.53-9, 47.59-8-99, 47.89-0-01 (comércio varejista); 49.23-0-02 (transporte com motorista); 53.20-2-02 (entrega rápida); 62.01-5-01, 62.02-3, 62.09-1, 63.19-4 (TI e software); 70.20-4, 71.19-7-04, 73.19-0-02, 73.19-0-03, 82.11-3, 85.99-6-04 |
| Perfil de custo | `servico_intelectual` (intermediação e plataforma de entregas). **Perfil provisório:** a contadora ainda precisa confirmar se a empresa entrega por conta própria (então combustível e motoboy entram no custo) |
| Funcionários | Não tem |
| Pró-labore | Não tem. Sem folha, o Fator R é zero: atividade do Anexo V é tributada no Anexo V |
| Responsável | **Elen** |
| Pasta | `G:\Meu Drive\Trabalho ROF\Contabilidade\Arquivos RENATA Dominio\83 - R J A` (Drive: "83 - R J A"; meses em `MM_AAAA\Extrato`, `Guias`, `Relatorio`, `Doc's\Prestados` e `Tomados`; cadastro em `Automoção Contabil`) |

## Sócio

| Sócio | CPF | Participação | Conta | Pró-labore |
|---|---|---|---|---|
| RAUL JOSE ALVES DE OLIVEIRA | (no cadastro do Domínio) | 100% (30.000 quotas integralizadas), sócio-administrador | 530 (adiantamento) / 532 (distribuição de lucros) | não tem |

## Bancos

| Banco | Conta | Conta contábil |
|---|---|---|
| Banco Inter | 11010929-5 | **8** |
| Mercado Pago | 37145088328 | **9** |
| Mercado Pago, poupança/rendimento | — | **11** |
| Nu Pagamentos (Nubank) | 21535714-6 | **6** (arquivos `5ef4f441-…`) |
| Cora | não cadastrada no plano ("Cora sem movimento") | **perguntar** |

## Particularidades

- A receita entra pela Escrita Fiscal (NFS-e prestadas). No banco, o recebimento é D banco / C 504. Se não houver nota integrada, a conta 504 fica credora: **alerta, não é normal**.
- Notas tomadas (Gaudium, software da plataforma, cerca de R$ 207 por mês) entram pela Escrita Fiscal: D 362 / C 506. O pagamento baixa a 506, **nunca vai para despesa de novo**.
- Pix ao sócio Raul vai para a 530. No fim do semestre ou do ano, a 530 é transferida para a 532 com lucro apurado (cuidado: em 2026 ainda não há lucro contábil, veja `decisoes.md`).
- TXT: um arquivo por mês, `83_RJA-OLIVEIRA_<AAAA-MM>.txt`, cabeçalho `|0000|24725950000141|`, cp1252, CRLF, histórico com prefixo `REF A `.
