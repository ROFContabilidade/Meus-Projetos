---
name: "rof-contabilidade-folha-korp"
description: "KORP INFORMÁTICA (CNPJ 03.623.045/0001-00): converte o TXT de folha exportado do Domínio para importar na Korp, trocando os centros de custo numéricos (1–6) pelos códigos Korp (CC337 etc.) no registro 05."
---

# ROF Contabilidade — Folha Korp (Domínio → Korp)

Use quando Everton/Rosangela enviar o TXT da folha de pagamento exportado do Domínio para a empresa KORP INFORMÁTICA LTDA EPP, ou o retorno de erro da Korp (`Problemas_Importacao_DOMINIO.txt` com "Centro de Custo: 000000X Não cadastrado no Sistema"). Executar direto, sem pedir confirmação.

## Empresa

| Campo | Informação |
|---|---|
| Razão social | KORP INFORMÁTICA LTDA EPP |
| CNPJ | 03.623.045/0001-00 (03623045000100) |
| Código da empresa no Domínio | 0000140 (aparece no registro 01 e no final do registro 03) |
| Problema | Domínio exporta centro de custo numérico (7 dígitos); a Korp só aceita os códigos alfanuméricos dela |

## Tabela de-para (Centros de Custo)

| Domínio | Descrição Domínio | Korp | Descrição Korp |
|---|---|---|---|
| 0000001 | Desenvolvedores | **CC337** | DESENVOLVIMENTO EM GERAL |
| 0000002 | Qualidade | **CC506** | QUALIDADE |
| 0000003 | Suporte | **CC345** | SUPORTE EM GERAL (Service Desk) |
| 0000004 | Consultores (Implantação/Consultoria) | **CC644** | CONSULTORIA |
| 0000005 | Administrativos / Diretoria / Financeiro | **CC320** | ADM GERAL |
| 0000006 | Comercial | **CC379** | COMERCIAL GERAL |

Se surgir código não listado: NÃO inventar. Converter o resto, deixar o código novo intacto e pedir ao usuário o código Korp correspondente.

## Layout do TXT (Domínio — lançamentos contábeis)

- Codificação **Windows-1252 (ANSI)**, quebras de linha **CRLF**. Nunca converter para UTF-8.
- Registros: `01` cabeçalho · `02` lote (data/usuário) · `03` lançamento (contas, valor, histórico) · `05` rateio centro de custo · `99` trailer.
- **Registro 05** (138 caracteres):

| Colunas | Conteúdo |
|---|---|
| 1–2 | `05` |
| 3–9 | Sequencial |
| **10–16** | **Centro de custo DÉBITO** (7) |
| **17–23** | **Centro de custo CRÉDITO** (7) |
| 24–38 | Valor (15, 2 decimais implícitas) |

ATENÇÃO: o suporte do Domínio informa só "colunas 10 a 16", mas a Korp valida **os dois campos**. Sempre converter 10–16 **e** 17–23. Em cada linha só um vem preenchido; o outro fica `0000000` e deve permanecer `0000000`.

**Preenchimento:** código Korp alinhado à esquerda com espaços à direita até 7 caracteres (`CC337  `). Formato validado na importação real (set/2026).

## Script de conversão

```python
from collections import Counter
MAP = {'0000001':'CC337','0000002':'CC506','0000003':'CC345',
       '0000004':'CC644','0000005':'CC320','0000006':'CC379'}
src, dst = 'Folha.txt', 'Folha_Korp.txt'
raw = open(src,'rb').read()
lines = raw.decode('cp1252').split('\r\n')
out, cnt, faltam = [], Counter(), Counter()
for l in lines:
    if l[:2] == '05':
        f = []
        for c in (l[9:16], l[16:23]):
            if c == '0000000': f.append(c)
            elif c in MAP: f.append(MAP[c].ljust(7)); cnt[MAP[c]] += 1
            else: f.append(c); faltam[c] += 1
        n = l[:9] + f[0] + f[1] + l[23:]
        assert len(n) == len(l)
        l = n
    out.append(l)
res = '\r\n'.join(out).encode('cp1252')
assert len(res) == len(raw)
open(dst,'wb').write(res)
print(cnt, 'SEM DE-PARA:', faltam)
```

## Conferência obrigatória

1. Tamanho do arquivo final = tamanho do original (mesmos bytes).
2. Só mudam as colunas 10–23 das linhas `05`; todas as outras linhas idênticas.
3. Total convertido = total de campos de CC não zerados. Se houver retorno de erro da Korp, o número de linhas do retorno deve bater com esse total.
4. Nenhum código `0000001`–`0000006` remanescente no arquivo final.

## Entrega

Arquivo `Folha_Korp.txt` + tabela resumo (código Domínio → Korp → quantidade de linhas) + lista de códigos sem de-para, se houver.