# Emissor ROF de NFS-e — instalação no Windows da Rosângela

Programa próprio da ROF (criado com o Dr. Everton em 21/11/2026) que emite NFS-e no padrão nacional pela API
oficial da Receita, assinando com o certificado A1 instalado no Windows. Serve para qualquer empresa do
escritório: basta o certificado dela (ou a procuração eletrônica para a ROF) e a ficha da empresa.

## Instalar (uma vez neste computador)
1. **`1_INSTALAR.bat`** (dois cliques). Ele instala o Python 3.12, se faltar, e copia o programa para
   `C:\EmissorROF`. Depois instala as bibliotecas, roda os 21 testes (todos devem dar OK) e cria a configuração
   (produção, **série 2**) com as fichas da Soares FRG e da Soares Curitiba.
2. **`2_INSTALAR_CERTIFICADO.bat`**: escolha o `.pfx` da empresa (abre em `G:\Meu Drive\Trabalho ROF\Certificados`)
   e **digite você mesma a senha**. Ele mostra a **impressão digital**: anote.
3. **`4_VER_CERTIFICADOS.bat`**: confere os certificados instalados.

## Usar
- **Tela do programa:** `C:\EmissorROF\3_ABRIR_EMISSOR.bat` (abre no navegador).
- **Em lote, com o Claude:** abra o Claude Code na pasta `C:\EmissorROF` e siga o `docs\01 - PROCEDIMENTO PASSO A PASSO.md`.

## Série por computador (importante)
O computador do Dr. Everton usa a **série 1**. Este usa a **série 2**. Nunca repita uma série em dois
computadores, porque a numeração da DPS colide. Ellen: 3; Gabi: 4.

## Empresa nova
1. Instalar o certificado dela (passo 2) ou cadastrar a procuração eletrônica da empresa para a ROF (serviço NFS-e).
2. Criar a ficha: na tela do programa (aba Empresas), ou copiar `modelos\ficha_empresa_MODELO` para
   `%APPDATA%\EmissorROF\dados\empresas\<CNPJ>.json`. Os campos que mais dão erro estão no procedimento, passo 1.
3. Se a empresa já emitiu notas em outro sistema na mesma série, preencher `dps_ja_usadas`.

## Limites desta versão
Só Simples Nacional, sem retenções federais, sem cancelamento (cancelar pelo portal) e competência até 2026.
Antes de 01/01/2027 o programa precisa receber o grupo IBS/CBS da reforma tributária.
