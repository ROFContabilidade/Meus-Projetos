---
name: rof-contabilidade-lmp3
description: "LMP3 SOLUCOES LTDA, CNPJ 22.993.076/0001-06, código 64 no Domínio, Simples Nacional - Anexo III (manutenção e reparação de instrumentos de medida, teste e controle). Lançamentos contábeis, conciliação bancária, conferência de folha e TXT para o Domínio desta empresa. Usar automaticamente quando o usuário mencionar LMP3, o CNPJ 22.993.076/0001-06, a empresa 64, os sócios Marcos Parpineli Paes ou Luciana Pilz Paes, ou enviar extrato, razão, balancete, folha ou guias dela."
---

# ROF Contabilidade: LMP3 SOLUCOES LTDA — lançamentos contábeis e conciliação

**Antes de tudo, siga o roteiro do `rof-analista` (cérebro).** Ele traz a leitura de arquivos e extratos, o acordo de trabalho, a base legal e a ordem de decisão; em conflito, vale a decisão registrada da contadora, depois o cérebro, depois esta skill. Decisões já tomadas: `references/decisoes.md` (buscar pelo favorecido/valor, não ler inteiro).

Toda decisão nova da contadora deve ser registrada em `references/decisoes.md` e no `references/empresa.json`, com quem validou e quando.

## Dados da Empresa

| Campo | Informação |
|---|---|
| Razão social | LMP3 SOLUCOES LTDA |
| Nome fantasia | LMP3 SOLUCOES |
| CNPJ | 22.993.076/0001-06 |
| CNPJ sem formatação | 22993076000106 |
| Código no Domínio | 64 |
| Atividade / CNAEs | 3312-1/02 Manutenção e reparação de aparelhos e instrumentos de medida, teste e controle (principal). Secundários: 4751-2/01, 6201-5/01, 6202-3/00, 6204-0/00, 6209-1/00, 8211-3/00, 8219-9/99, 8599-6/04 |
| Regime tributário | Simples Nacional - Anexo III — optante desde 31/07/2015 (consulta 13/11/2026) |
| Endereço | Av. Marginal José de Anchieta, 488, salas 11 e 12, Guarani, Colombo/PR |
| Usa o Domínio | Sim |
| Banco(s) | **a confirmar** |
| Pasta dos arquivos | G:\Meu Drive\Trabalho ROF\Contabilidade\Arquivos RENATA Dominio\64 - LMP3\2026\Automoção Contabil |
| Responsável pelo lançamento | Elen |

**Ativar esta skill** ao identificar: **LMP3 SOLUCOES LTDA**, **LMP3**, **22.993.076/0001-06**, **22993076000106**, **empresa 64**. Não misturar dados de outras empresas; cada empresa em uma conversa separada.

## Sócios

| Sócio | CPF | Qualificação | Participação | Pró-labore |
|---|---|---|---|---|
| MARCOS APARECIDO PARPINELI PAES | 031.970.619-26 | Sócio-Administrador | 90% | a confirmar |
| LUCIANA PILZ PAES | 920.308.669-20 | Sócia | 10% | a confirmar |

Sócios com o mesmo sobrenome: todo PIX para eles ou para familiares precisa de natureza definida (pró-labore, lucro, adiantamento ou reembolso) antes de lançar.

## Perfil de custo (atividade)

Prestação de serviço técnico de manutenção/reparação/calibração:
- **Custo do serviço:** peças e materiais aplicados no conserto, calibração e serviços técnicos de terceiros, técnicos que executam o serviço, software ou equipamento de uso no serviço.
- **Despesa:** aluguel das salas, energia, internet, contador, tarifas, material de escritório, marketing.
- Revenda de equipamentos (CNAE 4751-2/01), se houver: mercadoria pela nota → estoque → CMV, e receita no Anexo I.

## Leiaute do Arquivo TXT para Domínio

```
|0000|22993076000106|
|6000|X||||
|6100|DD/MM/AAAA|CONTA_DEBITO|CONTA_CREDITO|VALOR||REF. A HISTORICO||||
```

- Encoding cp1252, CRLF, valor com vírgula decimal.
- Um único TXT do mês com tudo, ordenado por data. Nome: `64_LMP3-SOLUCOES_<AAAA-MM>.txt`.

## Plano de Contas

**Ainda não recebido.** Pedir o plano de contas do Domínio (Contas.xls) e gravar em `references/empresa.json` → `contas`. Padrões ROF: fornecedores **506**, serviços de terceiros sem nota **362** (vigiada).

## Fluxo de Trabalho Mensal

1. `python scripts/extrato_dominio.py ler <extrato> -o trabalho/normalizado.csv`
2. `python scripts/extrato_dominio.py classificar trabalho/normalizado.csv -e references/empresa.json -o trabalho/classificado.csv`
3. Cruzamento e perguntas em lote pelo roteiro do `rof-analista`.
4. `python scripts/extrato_dominio.py gerar trabalho/classificado.csv -e references/empresa.json --saldo-inicial X --saldo-final Y -o <nome>.txt`
5. Entregar TXT, planilhas dos sócios, parecer e registrar as decisões novas.

## Pendências a Confirmar

- Plano de contas do Domínio (códigos reduzidos).
- Bancos, contas e conta contábil de cada um.
- Pró-labore: quem presta o serviço, valores; há funcionários?
- Receita por competência ou caixa.
- Mês inicial dos lançamentos e saldo inicial (balancete e razão do último mês fechado).

## Saldos Conferidos

| Data | Banco | Saldo |
|---|---|---|

## Histórico de Decisões

Em `references/decisoes.md`.
