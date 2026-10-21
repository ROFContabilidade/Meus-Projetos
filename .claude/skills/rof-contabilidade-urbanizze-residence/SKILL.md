---
name: "rof-contabilidade-urbanizze-residence"
description: "URBANIZZE RESIDENCE (condomínio edilício em Governador Celso Ramos/SC), CNPJ 56.236.808/0001-27, código 79 no Domínio, banco Cora ag. 0001 conta 5155857-9 (conta contábil 8). Lançamentos do extrato Cora, conciliação bancária e TXT mensal para o Domínio (URBANIZZE_CORA_MES_AAAA.txt) para o balancete mensal. Usar automaticamente quando o usuário mencionar URBANIZZE, Urbanizze Residence, o CNPJ 56.236.808/0001-27, a empresa 79, ou enviar extrato Cora, balancete ou notas de serviço dele."
---

# ROF Contabilidade — URBANIZZE RESIDENCE (Domínio 79)

Condomínio residencial (sem fins lucrativos, sem folha). Receita = taxas condominiais pagas pelos condôminos via Cora; despesas = água, luz, seguro, limpeza, administração, contabilidade e manutenção.

## Cadastro

| Item | Valor |
|---|---|
| Razão social | URBANIZZE RESIDENCE |
| CNPJ (registro 0000 do TXT) | 56.236.808/0001-27 → `56236808000127` |
| Código no Domínio | 79 (pasta Drive "79 - Urbanizze") |
| Município | Governador Celso Ramos/SC (Samae Gov Celso Ramos, Celesc) |
| Banco | Cora SCD — agência 0001, conta 5155857-9 → **conta contábil 8** |
| Contabilidade | RBA Contabilidade Ltda (29.650.531/0001-01) — NFS-e mensal tomada |

## Onde ficam os arquivos (Google Drive)

`79 - Urbanizze / 2026 / MM_AAAA /` com as subpastas `Extrato` (Extrato Cora.pdf), `Doc's` (faturas Celesc, boletos), `Relatorio` (relação de NFS-e recebidas, Entradas.xls), `Guias`. O balancete do mês fica na pasta do mês (`Balancete Urbanizze MM_AAAA.pdf`).

Buscar com `search_files` (`parentId` da pasta do mês) e ler o PDF com `read_file_content`. O TXT entregue fica no repositório em `Urbanizze/AAAA-MM/` (enviar ao usuário com SendUserFile; não subir pelo conector do Drive para não perder o ANSI).

## Plano de contas usado

| Conta | Descrição | Uso no extrato |
|---|---|---|
| 8 | CORA SCD SA - CONTA 5155857-9 | banco |
| 504 | CONDOMINOS DIVERSOS (Taxas condominiais a receber) | **D 8 / C 504** — todo "Pagamento recebido" de condômino |
| 411 | TAXAS CONDOMINIAIS (receita) | provisão da receita (D 504 / C 411) — feita fora do extrato |
| 510 | HONORÁRIOS CONTÁBEIS (a pagar) | D 510 / C 8 — boleto RBA Contabilidade (provisão pela NFS-e: D 361 / C 510) |
| 526 | ÁGUA E ESGOTO (a pagar) | D 526 / C 8 — boleto Samae Gov Celso Ramos (provisão D 355 / C 526) |
| 527 | ENERGIA ELÉTRICA (a pagar) | D 527 / C 8 — boleto Celesc (provisão D 354 / C 527) |
| 535 | seguro Tokio Marine (a pagar) | D 535 / C 8 — boleto Tokio Marine Seguradora 33.164.021/0001-00 (padrão dos TXTs dez/2025–fev/2026) |
| 506 | FORNECEDOR MODELO | D 506 / C 8 — Pix Singular Soluções 27.101.405/0001-72 (provisionado pela nota) |
| 363 | SERVIÇOS ADMINISTRATIVOS | D 363 / C 8 — Pix Cezar Almir Paludo 733.475.409-30 (direto na despesa) |
| 357 | SERVIÇOS DE LIMPEZA | D 357 / C 8 — Pix Carlos André da Silva 591.670.339-20 (direto na despesa) |
| 362 | SERVIÇOS PRESTADOS POR TERCEIROS | D 362 / C 8 — manutenção avulsa (ex.: Henrique Mario, Construpalmas) |
| 364 | GÁS | D 364 / C 8 — distribuidora de gás |
| 366 / 58 | Materiais para conservação / outros materiais de consumo | compras de material |
| 358 | SEGURO PREDIAL | despesa do seguro |
| 352 / 372 | Multas de mora / juros de mora | encargos de boleto pago em atraso |

### Decisões da Rosangela (out/2026)

- **Tokio Marine → D 535 / C 8** está correto; a contrapartida (provisão do seguro) a Rosangela lança no Domínio. Não precisa apontar.
- **9,00C antigo na conta 510** (diferença RBA): saldo conhecido, antigo — **não apontar** como pendência.
- **Fornecedor sem pagamento no mês (506 Singular etc.)**: segue credor até o pagamento, aí faz a baixa (D 506 / C 8). Não é inconsistência.

Lançamento que não se encaixa na tabela → **perguntar** antes de gerar o TXT (não inventar conta). Registrar aqui toda decisão nova.

## Leiaute do TXT (igual ao de agosto/2026 importado)

- Arquivo `URBANIZZE_CORA_<MÊS>_<AAAA>.txt` (ex.: `URBANIZZE_CORA_SETEMBRO_2026.txt`), **ANSI (latin-1) e CRLF**.
- Primeira linha `|0000|56236808000127|`; cada lançamento = `|6000|X||||` + `|6100|DD/MM/AAAA|débito|crédito|valor||histórico||||`.
- Valor com vírgula decimal, sem separador de milhar. Histórico = texto do extrato Cora (nome + CPF/CNPJ).
- Ordem cronológica, como no extrato (o PDF da Cora lista do mais recente para o mais antigo — inverter).

## Rotina do mês

1. Ler `Extrato Cora.pdf` da pasta do mês e o balancete do mês anterior.
2. Conferir **saldo inicial do extrato = saldo da conta 8 no balancete anterior** e que entradas − saídas fecham no saldo final.
3. Classificar pela tabela acima; conferir que os pagamentos de 510/526/527/506 batem com o saldo credor dessas contas no balancete anterior (provisão do mês anterior). Diferença = apontar.
4. Gerar o TXT, salvar em `Urbanizze/AAAA-MM/`, commit/push, enviar o arquivo e resumir o fechamento.
5. Atualizar o Histórico abaixo.

## Histórico

| Mês | Saldo inicial | Entradas | Saídas | Saldo final | Observações |
|---|---|---|---|---|---|
| 08/2026 | 9.336,59 | 3.015,64 | 1.922,82 | 10.429,41 | Balancete 08/2026: 506 = 180,00C; 510 = 9,00C; 526 = 505,26C; 527 = 154,31C. |
| 09/2026 | 10.429,41 | 3.090,14 | 2.323,64 | 11.195,91 | 6 taxas condominiais (D 8 / C 504). Pagos RBA 219,00 (= nota de agosto; 9,00C antigo segue em 510), Samae 505,26 e Celesc 154,31 (zeram as provisões de agosto), Tokio Marine 555,07 em 535 (confirmado; contrapartida lançada pela Rosangela), Cezar 540,00 (363), Carlos André 350,00 (357). Singular Soluções sem pagamento no mês (506 segue 180,00C até a baixa). **TXT confirmado pela Rosangela.** |
