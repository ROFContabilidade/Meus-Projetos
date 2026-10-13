---
name: "rof-nfse-prestadas"
description: "Planilha PADRÃO da ROF Contabilidade para NFS-e PRESTADAS (serviços prestados) de QUALQUER empresa, no modelo da empresa 41 (VF Chaveiro / LUANNA GVM FERREIRA, arquivo NFSe_Prestadas_41_VF_Chaveiro_09-2026_v3.xlsx): abas Notas Prestadas, Inconsistências e Empresa e CNAEs, salva na pasta Relatorio do mês no Drive. Usar sempre que pedirem para ler/analisar/conferir notas de serviço prestadas, NFS-e emitidas, faturamento de serviços, anexo do Simples das notas, ou gerar a planilha de serviços prestados de uma empresa."
---

# ROF — Planilha de NFS-e prestadas (modelo 41)

Toda planilha de serviços prestados segue o modelo da empresa 41 (v3). Não inventar outro layout.

## Onde ler e onde salvar (Google Drive)

- Notas: `<NN - Empresa>/<ANO>/<MM_AAAA>/Doc's/Prestados` (XML do Emissor Nacional + PDF).
  Relatórios de conferência, quando existirem: `<MM_AAAA>/Relatorio` (relatório da prefeitura, planilha "Emitidas - Completa" do portal nacional).
- **Salvar sempre em `<MM_AAAA>/Relatorio`**, nome `NFSe_Prestadas_<NN>_<Nome>_<MM>-<AAAA>.xlsx`.
- Upload com `create_file` (base64, `disableConversionToGoogleType: true`) e **conferir que o `fileSize` devolvido é igual ao tamanho local**; se diferente, mandar o arquivo para a lixeira e reenviar.
- Ao substituir uma versão antiga, mandar a antiga para a lixeira (nunca apagar definitivo).

## Estrutura (gerada por `scripts/nfse_prestadas.py`)

1. **Notas Prestadas** — título `NFS-e PRESTADAS - <RAZÃO> - <AAAA-MM>`; linha 2 com
   `Sequência X a Y | Faltando: ... | Duplicadas: ...`; cabeçalho na linha 4 (Arial 9 negrito, fundo `D9E1F2`, bordas finas);
   27 colunas: Nº, Emissão, Compet., Situação, CPF/CNPJ tomador, Tomador, Município do tomador, Local da prestação,
   Município de incidência do ISS, Item LC 116 / cód., Atividade prestada, Anexo Simples (atividade), Discriminação,
   Informações complementares, Valor serviço, Base ISS, Alíq. ISS %, ISS, ISS retido?, IRRF, PIS, COFINS, CSLL, INSS,
   Total retido, Valor líquido, Status ("Conferir", fundo `FFF2CC`). Linha `TOTAL (sem canceladas)` com SUMIFS por Situação = Normal.
2. **Inconsistências** — Nota | Data | Participante | Gravidade | Descrição | Resolvido? | Observação.
   Gravidade: `ERRO` (corrigir antes de apurar), `ALERTA` (conferir), `APONTAMENTO` (observação). Linhas "Geral" primeiro;
   linhas Geral/ERRO/ALERTA com fundo `FFF2CC`.
   Automáticos do script: quebra de sequência, duplicadas, situação ≠ Normal, competência ≠ mês, emissão em outro mês
   (retroativa), local da prestação ≠ município do tomador, nota sem NBS, item sem anexo padrão.
   Manuais (sempre pensar neles): conferência com relatório da prefeitura/portal (ou ALERTA se não houver),
   item LC 116 x CNAE x serviço descrito, peças/materiais na NFS-e (ICMS / Anexo I), parcelas e saldos,
   serviço de outro período, tomador em recuperação judicial, NF-e de remessa/retorno que não é receita.
3. **Empresa e CNAEs** — dados da BrasilAPI (situação, município, natureza, porte, Simples, MEI, início),
   tabela de CNAEs com anexo sugerido, faturamento do mês por anexo/item (SUMIFS na aba de notas) e
   **CONCLUSÃO - ANEXO DE TRIBUTAÇÃO** (texto, célula mesclada B:E), rodapé sobre Fator R.

## Como gerar

```bash
python3 -I scripts/nfse_prestadas.py --json spec.json --xml <pasta_com_XMLs> --saida NFSe_Prestadas_<NN>_<Nome>_<MM>-<AAAA>.xlsx
python3 <skill xlsx>/scripts/recalc.py NFSe_Prestadas_...xlsx   # tem que dar status success, 0 erros
```

`spec.json`: `razao`, `cnpj`, `competencia` (AAAA-MM), `empresa` (lista [rótulo, valor]), `cnaes`
(lista [Tipo, CNAE, Descrição, Anexo, Observação]), `conclusao`, `inconsistencias` manuais
(lista [nota|"Geral", data, participante, gravidade, descrição]) e, sem `--xml`, `notas` (dicts com as chaves de `COLUNAS`).
`empresa_brasilapi(cnpj)` e `municipio_ibge(cod)` (BrasilAPI, precisa de User-Agent) ajudam a montar o spec.

Os valores das NFS-e do Simples ficam sem Base/Alíq./ISS (ISS no DAS); preencher só quando o XML destacar ISS.
Total retido = ISS (se retido) + IRRF + PIS + COFINS + CSLL + INSS; líquido = valor − total retido (fórmulas).
