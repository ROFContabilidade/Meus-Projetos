---
name: "rof-fiscal-prumo"
description: "PRUMO COMERCIAL LTDA (empresa 272 no Domínio, CNPJ 41.751.764/0001-04, IE 9089050321, Curitiba-PR): conferência mensal das notas fiscais - cruza os XML (NF-e e CT-e) x relatório Acompanhamento de Entradas do Domínio x relatórios do Sieg (NF-e e CT-e) x PLANILHA DE VENDAS PRISMA (série 0) e entrega planilha colorida por situação com a sequência das saídas série 0 (sistema próprio) e série 1 (Mercado Livre), entradas de fornecedores, devoluções/entradas próprias e CT-e (somente Prumo tomadora), com chave de acesso, canceladas, inutilizadas e não localizadas. Usar quando falarem em Prumo, 272_Prumo, notas da Prumo, sequência de notas, PRISMA, Mercado Livre da Prumo, CT-e da Prumo ou conferência XML x Domínio da Prumo."
---

# PRUMO COMERCIAL LTDA - Conferência de notas (XML x Sieg x PRISMA x Domínio)

**Empresa:** PRUMO COMERCIAL LTDA - código **272** no Domínio - CNPJ **41.751.764/0001-04** - IE 9089050321 -
Rua O Brasil para Cristo, 719, Curitiba/PR. Comércio (CRT 3, regime normal), vende para construtoras (MRV etc.) e no Mercado Livre.

O cerne do trabalho: **validar se toda nota XML da pasta está no Domínio** (e se tudo que está no Domínio tem XML),
cruzando **XML x relatórios do Domínio x relatórios do Sieg/cliente**, e conferir a **sequência** das notas emitidas.
Ser detalhista: apontar tudo, nota por nota.

## 1. Onde ficam os arquivos

`G:\Meu Drive\Trabalho ROF\Contabilidade\Arquivos PRECISION Domínio\<ANO>\<MM_AAAA>\272_Prumo\`
(no Google Drive: pasta `MM_AAAA` > `272_Prumo`). Subpastas:

| Pasta | O que tem |
|---|---|
| `Doc's` | ZIPs de XML: `PRUMO.zip` (saídas série 0), `PRUMO DEVOLUÇÃO.zip` (entradas emitidas pela Prumo), `XML.zip` (Mercado Livre série 1, subpastas Autorizadas/Canceladas), `DownloadDFe_NNN.zip` (NF-e baixadas da SEFAZ), `xmls_AAAAMMDD_*.zip` (Sieg: NF-e de entrada ou CT-e + eventos) |
| `Relatorios` | `Entradas_Domino.xls` (Domínio: Acompanhamento de Entradas), `Relatorio_Relatorio_Basico.xlsx` (Sieg NF-e), `Relatorio_CTe.xlsx` (Sieg CT-e), `emission_report_*.xlsx` (Mercado Livre), ICMS Antec. + ST, Serviços Tomados |
| pasta do mês (fora da 272_Prumo) | **`PLANILHA DE VENDAS PRISMA - <MÊS> <ANO>.xlsx`** - vendas de **todo o grupo**, inclusive as notas série 0 da Prumo |

Meses anteriores servem de modelo: `FAT. MM.AAAA_Prumo.xlsx` e `NF Entrada_MM.AA_Prumo.xlsx` (pasta Relatorio).

### Como baixar do Drive (cloud)
Usar o conector Google Drive: `search_files` (`title contains '272_Prumo'`, depois `parentId = '<id>'`) e
`download_file_content`. O conteúdo vem em base64; quando é grande o harness salva em
`tool-results/*.txt` → `jq -r .content arquivo | base64 -d > arquivo.zip`.
**Limites:** arquivo acima de ~3-4 MB derruba a conexão (pedir para dividir o ZIP); arquivo muito pequeno (< ~30 KB)
volta inline na conversa e não é salvo (pedir para juntar num ZIP maior). Pasta de trabalho: scratchpad.
`.xls` do Domínio não abre no xlrd: o script converte com `soffice --headless --convert-to xlsx`.

## 2. Regras da Prumo (aprendidas na conferência)

**Saídas série 0 (sistema próprio)**
- Numeração própria (ex.: set/2026 = 35512 a 36116). A **PLANILHA PRISMA tem as notas de todas as empresas do grupo**
  (outras faixas: 14xxx, 46xxx, 53xxx...): usar **só a faixa de numeração da Prumo**. Linha da PRISMA com numeração
  parecida mas fora da faixa (ex.: 30453) → apontar para confirmar a empresa.
- PRISMA: colunas DATA, DANFE, VALOR, CLIENTE, VENDEDOR, VAN/ROB/SUSI, **CANC, DEV, REME**. Devoluções aparecem como
  cliente "DEVOLUÇÃO" com valor em DEV.
- **PRISMA registra só o valor dos produtos**: diferença XML x PRISMA igual ao `vFrete` da nota = frete destacado (não é erro, mas apontar).
- Arquivos `NFe<chave>_Inutilizacao.xml` (no PRUMO.zip e no PRUMO DEVOLUÇÃO.zip) são **números inutilizados** (XML sem
  protocolo): a nota não existe. `_Distribuicao` = autorizada; `_Dist_Cancelamento` = evento de cancelamento;
  `_Dist_Carta_Correcao` = CC-e.
- As **entradas emitidas pela Prumo** (devoluções CFOP 1202/2202 com finNFe 4, retorno de armazém 1906) usam a **mesma
  série 0** e ficam no `PRUMO DEVOLUÇÃO.zip` → contam na sequência.
- Erro já encontrado: **número inutilizado lançado como entrada no Domínio** (tentativas repetidas da mesma devolução; só uma
  foi autorizada). Comparar sempre o status do XML.

**Saídas série 1 (Mercado Livre)** - `XML.zip`. Sequência própria (ex.: 7501 a 7902). As entradas emitidas no ML
(devoluções 1202/2202 e retornos simbólicos 2949 com EBAZAR) usam a mesma série e **não vêm no XML.zip** → aparecem como
"entrada própria sem XML". O `emission_report` do ML pode vir de outro mês: conferir as datas.

**Entradas NF-e** - XMLs de fornecedores (`DownloadDFe_*`, `xmls_*`) = relatório Sieg `Relatorio_Relatorio_Basico`
(coluna `Chave`). Casar com o Domínio por número + série (+ valor). Diferença de ICMS XML x Domínio é normal em CFOP de ST
(5401/5403/5405/6403 - sem crédito) e notas mistas; emitente do Simples com CSOSN 101 dá crédito do `vCredICMSSN`.

**CT-e - considerar SOMENTE os que têm a PRUMO como TOMADORA.** No `Relatorio_CTe` do Sieg:
tomadora = `CNPJ_CPF_Tomador` ou `CNPJ_CPF_Outro_Tomador` = 41751764000104 (os demais - frete do remetente, José Osvaldo,
Ebazar etc. - são desconsiderados e não se lançam). `Status` "Cancelamento" = cancelado. No XML, tomador = `toma3/toma`
(0 rem, 1 exped, 2 receb, 3 dest) ou `toma4`. Erro já encontrado: **CT-e cancelado lançado com valor e crédito de ICMS**.

**Domínio** - relatório "Acompanhamento de Entradas": espécie 36 = NF-e, 38 = CT-e, 39 = serviço. Linhas de
continuação (SUBTRI, ICMSA) pertencem ao lançamento de cima. Saídas: pedir o relatório de saídas para checar canceladas
e inutilizadas no livro de saídas.

## 3. Executar

```bash
S=.claude/skills/rof-fiscal-prumo/scripts
# extrair cada ZIP numa pasta própria dentro de uma pasta só (ex.: allxml/PRUMO, allxml/XML, allxml/DownloadDFe_102...)
python3 -I $S/conferencia_prumo.py --xml allxml --dominio Entradas_Domino.xls \
   --sieg-nfe Relatorio_Relatorio_Basico.xlsx --sieg-cte Relatorio_CTe.xlsx \
   --prisma "PLANILHA DE VENDAS PRISMA - SETEMBRO 2026.xlsx" --competencia 09/2026 \
   --saida Conferencia_Notas_09.2026_Prumo.xlsx
```

O script classifica cada XML pelo conteúdo (emitente/destinatário Prumo, série, tpNF, tomador do CT-e, eventos 110111/110110),
elimina duplicados pela chave e imprime o resumo. **Depois de rodar, ler o resumo e as linhas coloridas** e investigar o que
apareceu (abrir o XML, ver infCpl, vFrete, protocolo). Conferir que o total da aba ENTRADAS = total do relatório do Domínio.

## 4. Planilha entregue (formato aprovado pela Rosangela)

Uma aba por assunto, cada uma com **LEGENDA no topo** (cor, situação, quantidade, valor e o que significa) e
**chave de acesso logo depois do número da nota** (formato texto, 44 dígitos):

1. **Resumo** - números e listas de notas por situação.
2. **SAÍDAS Série 0** - toda a sequência, número a número, com XML x PRISMA x Domínio.
3. **SAÍDAS Série 1 (ML)** - toda a sequência do Mercado Livre.
4. **ENTRADAS** - NF-e de fornecedores + notas próprias de entrada + **CT-e só Prumo tomadora** juntos.
5. ICMS XML x Domínio (informativo) e a base do Domínio.

Cores: branco = autorizada/OK; verde claro = CT-e OK; lilás = remessa/retorno; azul claro = devolução própria;
azul = entrada própria sem XML; amarelo = divergência com a PRISMA; laranja = cancelada; cinza = inutilizada;
rosa = ERRO cancelado lançado com valor; vermelho escuro = ERRO inutilizada lançada; vermelho = não localizada / não lançada.

Entregar com `SendUserFile` (o arquivo fica no scratchpad). **Não commitar a planilha no repositório** (dados fiscais do
cliente) - só se a Rosangela pedir.

## 5. Na resposta

Começar pelos erros (com notas e valores), depois o que foi conferido e está OK, e por fim o que ficou pendente
(arquivo que não abriu, XML faltando, relatório que precisa) e o que pedir ao cliente/analista. Sempre dizer quais
arquivos foram lidos e quais não.
