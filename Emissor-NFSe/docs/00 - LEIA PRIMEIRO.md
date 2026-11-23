# Sistema de NFS-e da ROF — leia primeiro

**O que é:** um programa próprio que emite as notas fiscais de serviço pela API oficial da Receita (padrão
nacional), com o certificado digital da empresa instalado no computador. Não paga mensalidade, não gasta IA por
nota, não passa pelo "Sou humano" do portal, e o PDF já sai com QR Code.

**Já funcionou:** em 21/11/2026 saíram 38 notas em produção (26 da Soares Advocacia FRG e 12 da Soares Curitiba /
Lucas Soares), todas autorizadas, com PDF salvo e enviado ao Drive da ROF.

## Como usar
- **Com o Claude:** abra o Claude nesta pasta e diga, por exemplo, "emite as notas de novembro da Soares Curitiba".
  Ele lê o `CLAUDE.md` e segue o `01 - PROCEDIMENTO PASSO A PASSO.md`. Ele mostra a lista antes e só emite com o
  seu "sim".
- **Sem o Claude:** abra `04 - Programa\Para instalar\EmissorROF.exe` (tela no navegador) ou use os comandos do
  procedimento.

## O que cada pessoa precisa fazer
- **Quem autoriza** (Dr. Everton): dizer "sim" à lista de notas do mês.
- **Certificado:** instalar uma vez por empresa no computador que vai emitir (a pessoa digita a senha; o Claude não).
- **Planilha de faturamento** do mês preenchida no Drive da ROF (é dela que saem as notas).

## Empresas já prontas
| Empresa | CNPJ | Certificado no computador do Dr. | Ficha |
|---|---|---|---|
| Soares Advocacia FRG | 43.174.172/0001-94 | sim, vence 03/01/2027 | `02 - EMPRESAS` |
| Soares Curitiba (Lucas Soares) | 49.325.547/0001-56 | sim, vence 01/10/2027 | `02 - EMPRESAS` |

Para um cliente novo da ROF: seguir o passo 1 do procedimento (certificado ou procuração, notas anteriores, ficha).

## Atenção
- Quem confirma a emissão responde pela nota: a conferência da lista continua sendo de uma pessoa.
- Os arquivos de certificado na pasta `Trabalho ROF > Certificados` estão com a senha no nome. Recomendo renomear.
- Antes de 01/01/2027 o programa precisa receber o grupo IBS/CBS da reforma tributária.

Achados da revisão e próximos passos: `03 - PENTE FINO E HISTORICO.md`.
