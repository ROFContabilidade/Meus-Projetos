## Leitura de Arquivos (padrão ROF, economia de tokens)

Regra obrigatória antes de abrir qualquer documento (validado por Rosangela, 29/10/2026). Ler sempre na ordem:

1. **MD** (`.md`): ler direto.
2. **OFX ou XML**: ler direto ou pelo script da skill.
3. **Planilha** (`.xlsx`, `.xls`, `.csv`): ler pelo script da skill.
4. **PDF**: **nunca abrir o PDF direto** (gasta muitos tokens). Antes:
   - se esta skill tem script que lê aquele PDF (ex.: `extrato_dominio.py ler`), usar o script;
   - senão, converter: `python scripts/ler_documento.py converter <arquivo.pdf>` (o `.md` fica salvo ao lado do PDF) e ler o `.md`.
5. **Nada funcionou** (PDF escaneado, conversão vazia): **parar e avisar a Rosangela**; não ler o PDF direto.

Para uma pasta inteira: `python scripts/ler_documento.py escolher <pasta>` mostra o que ler, na ordem, e o que ignorar (ex.: se existe `Entradas.xlsx`, o `Entradas.pdf` é ignorado).
