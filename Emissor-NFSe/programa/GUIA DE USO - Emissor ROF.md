# Emissor ROF de NFS-e — guia de instalação e uso

Versão 1.0, de 21/11/2026. O programa roda no computador de vocês, não usa IA e não gasta tokens.

## O que ele faz

1. Guarda a **ficha de cada cliente** (regime, serviços que pode faturar, modelo de descrição, tomadores).
2. Busca sozinho os dados de **CNPJ** e de **CEP**.
3. **Confere** a nota antes de enviar: CPF/CNPJ, valor, datas, descrição, serviço fora da ficha, nota repetida,
   procuração vencida, certificado vencido.
4. Mostra a **ficha de emissão** por tela (Pessoas, Serviço, Valores, Emitir) e só envia depois de a pessoa
   digitar **EMITIR**.
5. Monta o XML, valida no esquema oficial da Receita, assina com o certificado e envia direto à Sefin Nacional.
6. Salva o XML na pasta do cliente, registra no histórico e entrega o texto pronto para mandar ao tomador.

## O que esta versão ainda NÃO faz

- **Empresa fora do Simples Nacional** e **qualquer nota com competência de 2027 em diante**: bloqueadas, porque
  exigem o grupo IBS/CBS, que ainda não foi construído. Emitir pelo portal.
- **Retenções federais** (IRRF, INSS, PIS/Cofins/CSLL), deduções, obra, exportação, tomador no exterior.
- **Cancelamento e substituição** (fazer no portal).
- **PDF do DANFSe**: o programa tenta baixar; a Receita informa que esse serviço está suspenso desde 03/08/2026.
  Se não vier, baixar na consulta pública do portal com a chave de acesso.

## Antes do primeiro uso (uma vez só)

1. **Certificado A1 da ROF** (arquivo `.pfx`) salvo no computador de quem vai emitir, e a senha em mãos.
2. **Procuração eletrônica de cada cliente** para a ROF: o cliente entra em `servicos.receitafederal.gov.br`,
   "Nova Autorização", informa o CNPJ da ROF, a vigência e marca o serviço da **NFS-e**. Sem isso a Receita
   rejeita a nota (erro E0718).
3. **Pasta compartilhada** para as fichas e o histórico (sugestão: uma pasta no Google Drive da ROF).
4. **Uma série por computador**: Rosângela 1, Ellen 2, Gabi 3, Dr. Everton 4. Nunca repetir.

## Instalar

1. Copie `EmissorROF.exe` para o computador (por exemplo, para a Área de Trabalho).
2. Dois cliques. Na primeira vez o Windows pode mostrar "O Windows protegeu o computador" (o programa não tem
   assinatura de fabricante): clique em **Mais informações** e **Executar assim mesmo**.
3. Abre uma janela preta (deixe aberta) e a tela do programa no navegador.
4. Aba **Configuração**: nome de quem usa, série deste computador, pasta de dados compartilhada, caminho do
   certificado e senha. Clique em **Abrir certificado** e depois em **Testar conexão**.

A senha do certificado não fica gravada: é pedida toda vez que o programa abre.

## O primeiro teste (obrigatório antes de emitir de verdade)

O programa começa em **Produção Restrita**, o ambiente de testes da Receita, onde a nota não tem valor fiscal.

1. Cadastre a ficha de um cliente que já deu a procuração.
2. Emita uma nota de teste.
3. Se for **autorizada**: abra o XML salvo e confira com a Rosângela. Só então marque "Produção liberada" na
   ficha desse cliente e mude o ambiente para Produção.
4. Se for **rejeitada**: a tela mostra o código e o motivo. Anote e me passe.

**Esse teste ainda não foi feito.** Tudo o que não depende da Receita foi testado (ver abaixo). A conversa real
com o servidor só pode ser testada com o certificado da ROF, e três pontos precisam ser confirmados nela:

- o endereço exato do serviço (o botão Testar conexão experimenta as variações conhecidas);
- o nome dos campos da mensagem de envio e de resposta;
- o algoritmo da assinatura (o manual diz SHA-1; se rejeitar, trocar para SHA-256 na Configuração).

Em 21/11/2026 (sábado) o servidor de testes `sefin.producaorestrita.nfse.gov.br` não estava aceitando conexão
a partir do computador do Dr. Everton; o de produção estava. Vale tentar em dia útil.

## Emitir uma nota

1. Aba **Emitir nota**: escolha a empresa e o serviço.
2. Tomador: escolha um já usado ou digite. Para CNPJ, clique em **Buscar CNPJ**. Para o endereço, **Buscar** CEP.
3. Preencha beneficiário e datas e clique em **Montar pelo modelo da ficha**. Confira a descrição.
4. Valor e competência. Clique em **Conferir antes de emitir**.
5. Leia a ficha de emissão. Erros bloqueiam; avisos pedem atenção.
6. Digite **EMITIR** e clique em Emitir NFS-e.
7. Na tela de resultado: número da nota, chave, onde os arquivos foram salvos, o que falta fazer e a mensagem
   pronta para o tomador.

## Se algo der errado

| Situação na tela | O que aconteceu | O que fazer |
|---|---|---|
| BLOQUEADA | O programa não enviou nada. | Corrigir o que a tela aponta. |
| NAO_ENVIADA | Não conseguiu falar com a Receita. Nada foi emitido. | Tentar de novo mais tarde. |
| REJEITADA | A Receita recusou. Nada foi emitido. | Ler o código e o motivo; corrigir a ficha ou os dados. |
| **INCERTA** | O envio saiu e a resposta não voltou. A nota **pode** existir. | **Não emitir de novo.** Aba Histórico, botão **Conferir no servidor**. O programa trava novas notas dessa empresa até resolver. |
| AUTORIZADA com divergência | A nota saiu, mas algum dado devolvido difere do pedido. | Conferir o XML e decidir com a Rosângela se cancela ou substitui. |

## O que foi testado

21 testes automáticos, todos aprovados em 21/11/2026, com certificado de teste e servidor simulado:

- dígitos verificadores, valores e formação do identificador da DPS;
- 18 situações de erro, cada uma bloqueando a emissão;
- XML aprovado no esquema oficial de produção (v1.01) em três cenários;
- assinatura conferida por uma biblioteca independente, e adulteração detectada;
- emissão completa, rejeição, falta de rede, perda de resposta com conferência no servidor sem nota em dobro;
- bloqueio de nota repetida e de produção sem liberação;
- numeração que nunca repete.

O executável foi aberto sozinho, sem Python, e conferiu uma nota de ponta a ponta.

## Onde ficam as coisas

- Configuração e numeração deste computador: `%APPDATA%\EmissorROF`.
- Fichas, histórico e cópia de segurança dos XML: na pasta de dados.
- XML de cada nota: também na pasta do cliente indicada na ficha, numa subpasta por mês.
- Código-fonte, para quem for manter: pasta `03 - Programa Emissor ROF`.
