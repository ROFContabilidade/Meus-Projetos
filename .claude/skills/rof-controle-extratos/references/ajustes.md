# ajustes_controle_extratos.json

O que a usuária informa e que não aparece nas pastas. Fica ao lado da planilha e vai crescendo:
acrescente itens, não apague os antigos. Os meses são escritos no formato `MM_AAAA`.

```json
{
  "empresas": [
    {"grupo": "KON CONTABILIDADE", "cod": 92,
     "sem_movimento": [{"de": "09_2026", "ate": "10_2026", "motivo": "DJC: sem movimentação bancária até 10/2026"}]},
    {"grupo": "PROTECTION CONTABILIDADE", "cod": 25,
     "lancados": ["07_2026", "08_2026"]},
    {"grupo": "KON CONTABILIDADE", "cod": 139, "inicio": "07_2026",
     "bancos_novos": ["Inter"], "bancos_encerrados": ["Bradesco"]},
    {"grupo": "KON CONTABILIDADE", "cod": 94,
     "status": [{"mes": "09_2026", "status": "Recebido", "motivo": "extrato em imagem conferido pela Rosangela"}]}
  ],
  "empresas_novas": [
    {"grupo": "KON CONTABILIDADE", "cod": 170, "empresa": "NOME DA EMPRESA LTDA", "bancos": ["Cora"]}
  ],
  "situacoes": [
    {"cod": 92, "texto": "DJC: sem movimentação bancária até 10/2026"}
  ]
}
```

Campos de cada item de `empresas`. `grupo` pode faltar se o código não se repete; o código 25 existe
em KON e em PROTECTION, então nesse caso informe o grupo.

| campo | efeito |
|---|---|
| `sem_movimento` | lista de `{de, ate}` ou `{meses: [...]}` com `motivo` → status `S/MOV` |
| `lancados` | meses marcados `Já lançado`, mesmo sem TXT na pasta |
| `inicio` | meses antes dele ficam `—` |
| `bancos_novos` / `bancos_encerrados` | muda a lista de contas usada em Por banco e nas mensagens |
| `status` | força o status do extrato num mês (use para casos conferidos à mão) |

`situacoes` aparece no Painel, em "Situações informadas".
