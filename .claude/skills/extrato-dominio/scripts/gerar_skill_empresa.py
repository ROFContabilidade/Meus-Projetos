#!/usr/bin/env python3
"""Gera a skill da empresa (rof-contabilidade-<empresa>) no padrão ROF, a partir do JSON da empresa.

A skill gerada é autossuficiente: SKILL.md com os dados e as regras da empresa, o JSON de
configuração, o registro da folha (se houver), as referências do padrão ROF e os scripts.

Uso:
  python gerar_skill_empresa.py empresas/60-kopp-industria.json [--folha empresas/60-kopp-folha.csv] \
      [--nome kopp-industria] -o saida/
Gera saida/rof-contabilidade-<nome>/ e saida/rof-contabilidade-<nome>.skill (zip para instalar).
"""
import argparse
import json
import re
import shutil
import unicodedata
import zipfile
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent  # pasta da skill extrato-dominio
NAO_INFORMADO = "_não informado: perguntar_"


def slug(texto):
    t = unicodedata.normalize("NFKD", texto).encode("ascii", "ignore").decode().lower()
    t = re.sub(r"\b(ltda|s/?s|s\.?a|eireli|me|epp|industria e comercio de|comercio de|de|do|da|e)\b", " ", t)
    return re.sub(r"[^a-z0-9]+", "-", t).strip("-")[:40] or "empresa"


def cnpj_num(c):
    return re.sub(r"\D", "", str(c or ""))


def tabela(cab, linhas):
    if not linhas:
        return NAO_INFORMADO + "\n"
    out = "| " + " | ".join(cab) + " |\n|" + "|".join("---" for _ in cab) + "|\n"
    for l in linhas:
        out += "| " + " | ".join(str(x if x not in (None, "") else "—").replace("|", "/") for x in l) + " |\n"
    return out


def nome_conta(emp, cod):
    return (emp.get("contas") or {}).get(str(cod), "")


def montar_skill_md(emp, nome_skill, tem_folha):
    razao = emp.get("razao_social", "")
    cnpj = emp.get("cnpj", "")
    cod = emp.get("codigo_empresa", "")
    lay = emp.get("layout_txt") or {}
    separar = emp.get("separar_pagar_receber", False)
    gatilhos = [razao, emp.get("nome_fantasia"), cnpj, cnpj_num(cnpj), f"empresa {cod}"]
    gatilhos += [b.get("conta") for b in emp.get("bancos") or [] if b.get("conta")]
    gatilhos = [g for g in gatilhos if g]
    bancos = emp.get("bancos") or []
    desc = (f"{razao}, CNPJ {cnpj}, código {cod} no Domínio, {emp.get('regime', 'regime não confirmado')}. "
            f"Lançamentos contábeis, conciliação bancária, conferência de folha e TXT para o Domínio desta empresa. "
            f"Usar automaticamente quando o usuário mencionar {razao.split()[0] if razao else 'a empresa'}, "
            f"o CNPJ {cnpj}, a empresa {cod}, ou enviar extrato, razão, balancete, folha ou guias dela.")

    md = [f"---\nname: {nome_skill}\ndescription: \"{desc}\"\n---\n",
          f"# ROF Contabilidade: {razao}: lançamentos contábeis e conciliação\n",
          "Skill gerada no **padrão ROF** (`references/padrao_rof.md`). As regras gerais de lá valem "
          "aqui; este arquivo traz os dados e as particularidades da empresa. Toda decisão nova da contadora "
          "deve ser registrada aqui e no `references/empresa.json`, com quem validou e quando.\n",
          "## Dados da Empresa\n",
          tabela(["Campo", "Informação"], [
              ["Razão social", razao], ["Nome fantasia", emp.get("nome_fantasia")],
              ["CNPJ", cnpj], ["CNPJ sem formatação", cnpj_num(cnpj)], ["Código no Domínio", cod],
              ["Atividade / CNAEs", emp.get("atividade")],
              ["Regime tributário", (emp.get('regime', '') + (' — desde ' + emp['regime_desde'] if emp.get('regime_desde') else ''))],
              ["Usa o Domínio", "Sim" if emp.get("usa_dominio", True) else f"Não: {emp.get('sistema_contabil', '')}"],
              ["Banco(s)", "; ".join(f"{b.get('banco', '')} {b.get('conta', '')} → **{b.get('conta_contabil', '?')}**" for b in bancos)],
              ["Pasta dos arquivos", emp.get("pasta_arquivos") or NAO_INFORMADO],
              ["Responsável pelo lançamento", emp.get("responsavel_lancamento") or NAO_INFORMADO],
          ]),
          "\n**Ativar esta skill** ao identificar: " + ", ".join(f"**{g}**" for g in gatilhos) +
          ". Não misturar dados, contas ou históricos de outras empresas. Cada empresa em uma conversa separada.\n",
          "## Sócios\n",
          tabela(["Sócio", "CPF", "Qualificação", "Conta(s)", "Pró-labore"],
                 [[s.get("nome"), s.get("cpf"), s.get("qualificacao"), s.get("conta_contabil"), s.get("pro_labore")]
                  for s in emp.get("socios") or []]),
          ]
    if emp.get("empresas_ligadas"):
        md.append("\n**Empresas ligadas:** " + "; ".join(emp["empresas_ligadas"]) + "\n")
    md += ["\n## Regras de Trabalho (acordo com a contadora)\n",
           "1. **Fidelidade total** aos dados enviados: não alterar nada sem consultar.\n"
           "2. **Consulta prévia** antes de qualquer alteração.\n"
           "3. **Base legal** sempre que sugerir ajuste.\n"
           "4. **Não inventar** dados, contas, regime ou alíquota.\n"
           "5. **Histórico**: texto do extrato" +
           (f" com o prefixo `{emp['prefixo_complemento']}`" if emp.get("prefixo_complemento") else "") + ".\n"
           "6. Razão antigo não conferido não é verdade quando contrariar as regras desta skill.\n"
           "7. Na dúvida, **perguntar**: nunca mandar para a conta transitória em silêncio.\n",
           "## Leiaute do Arquivo TXT para Domínio\n",
           f"```\n|0000|{cnpj_num(cnpj)}|\n|6000|X||||\n|6100|DD/MM/AAAA|CONTA_DEBITO|CONTA_CREDITO|VALOR||"
           f"{emp.get('prefixo_complemento', '')}HISTORICO||||\n```\n",
           f"- Pagamento: D despesa/passivo/ativo / C banco. Recebimento: D banco / C contrapartida.\n"
           f"- Encoding {lay.get('encoding', 'cp1252')}, CRLF, valor com vírgula decimal.\n"
           f"- Entrega: **{'dois arquivos, _PAGAR (saídas) e _RECEBER (entradas)' if separar else 'arquivo único por mês, em ordem de data'}**, "
           f"nome `{cod}_{slug(razao).upper()}_<AAAA-MM>`.\n"]
    if emp.get("fontes_extrato"):
        md += ["\n## Fontes do extrato\n", "\n".join(f"- {x}" for x in emp["fontes_extrato"]) + "\n"]

    usadas = []
    for r in emp.get("regras") or []:
        if str(r.get("conta")) not in usadas:
            usadas.append(str(r.get("conta")))
    for c in [emp.get("conta_banco"), emp.get("conta_transitoria")] + [b.get("conta_contabil") for b in bancos]:
        if c and str(c) not in usadas:
            usadas.insert(0, str(c))
    md += ["\n## Plano de Contas: Contas Operacionais\n",
           tabela(["Cód", "Classificação e nome"], [[c, nome_conta(emp, c)] for c in usadas if nome_conta(emp, c)]),
           "\nO plano completo está em `references/empresa.json` (campo `contas`).\n"]
    if emp.get("contas_nao_usar"):
        md += ["\n**Contas que NÃO devem ser usadas:**\n",
               "\n".join(f"- **{k}**: {v}" for k, v in emp["contas_nao_usar"].items()) + "\n"]

    md += ["\n## Regras Invioláveis\n",
           "- **Saldo por banco**: saldo final − saldo inicial = entradas − saídas lançadas. Se não fechar, "
           "o TXT definitivo não é entregue (`gerar` recusa; use `--previa` só para conferência).\n"
           "- **Aplicações, rendimentos, IOF e IRRF nunca são omitidos.**\n"
           "- **Só lançamentos CONFIRMADOS** no TXT definitivo (PROVÁVEL, NÃO CRUZADO e DIVERGENTE viram pergunta).\n"
           "- Não incluir movimento de outra competência.\n"]
    pr = emp.get("praticas") or {}
    if any(pr.values()):
        md += ["\n## Práticas da Empresa\n",
               tabela(["Tema", "Regra"], [[k.replace("_", " ").capitalize(), v] for k, v in pr.items() if v])]
    if tem_folha:
        md += ["\n## Folha de Pagamento\n",
               "O registro da folha (Extrato Mensal do Domínio) está em `references/folha.csv`. Todo mês:\n"
               "1. Acrescente o relatório novo: `python scripts/folha_extrato_mensal.py ler <PDF> -o references/folha.csv --acrescentar`.\n"
               "2. Confira e aplique as contas: `python scripts/folha_extrato_mensal.py conferir <classificado.csv> "
               "-f references/folha.csv -e references/empresa.json --aplicar <classificado_folha.csv>`.\n"
               "3. O líquido da rescisão sai na Folha Mensal (rubrica LIQUIDO RESCISAO). Pagamento que soma dois valores "
               "da mesma pessoa é dividido por conta.\n"
               "4. Pagamento sem correspondente ou líquido sem pagamento: pergunte. Pró-labore de sócio: líquido na conta "
               "de pró-labore; a diferença é retirada, e é preciso **avisar antes de lançar**.\n\n"
               + tabela(["Evento", "Conta"], [[k.replace("_", " ").capitalize(), f"{v} {nome_conta(emp, v)}"]
                                             for k, v in (emp.get("contas_folha") or {}).items() if v])]
    md += ["\n## Notas de Fornecedores\n",
           "Registro das notas (Acompanhamento de Entradas do Domínio) em `references/entradas.csv`. Todo mês: "
           "`python scripts/entradas_dominio.py ler <Entradas.xls> -o references/entradas.csv --acrescentar` e "
           "`python scripts/entradas_dominio.py conferir <classificado.csv> -n references/entradas.csv -e references/empresa.json "
           "--aplicar <classificado_nf.csv>`. Conta de fornecedores: "
           f"**{emp.get('conta_fornecedores') or 'a confirmar com a contadora'}**. Pagamento só pelo valor fica PROVÁVEL.\n"]
    md += ["\n## Impostos\n",
           "Registro das guias (demonstrativos e Resumo dos Impostos do Domínio) em `references/impostos.csv`. Todo mês: "
           "`python scripts/impostos_dominio.py ler <XLS/PDF> -o references/impostos.csv --acrescentar` e "
           "`python scripts/impostos_dominio.py conferir <classificado.csv> -i references/impostos.csv -e references/empresa.json "
           "--aplicar <classificado_impostos.csv>`. Guia sem demonstrativo: informar o usuário.\n\n"
           + tabela(["Imposto", "Conta"], [[k, f"{v} {nome_conta(emp, v)}"] for k, v in (emp.get("contas_impostos") or {}).items()])]
    md += ["\n## Classificações Recorrentes Confirmadas\n",
           tabela(["Descrição no extrato", "Tipo", "Conta", "Observação"],
                  [[", ".join(r.get("contem") or []) or r.get("regex", ""), r.get("tipo", ""),
                    f"{r.get('conta')} {nome_conta(emp, r.get('conta'))[:45]}",
                    r.get("nome", "") + (f" (dias {r.get('dia_de', 1)}–{r.get('dia_ate', 31)})" if "dia_de" in r else "")]
                   for r in emp.get("regras") or []]),
           "\nAs regras executáveis estão em `references/empresa.json` (a primeira que casa vence). "
           "Classificações recorrentes não substituem a verificação dos documentos do mês.\n"]
    if emp.get("particularidades_bancos"):
        md += ["\n## Particularidades dos Bancos\n", "\n".join(f"- {x}" for x in emp["particularidades_bancos"]) + "\n"]
    md += ["\n## Fluxo de Trabalho Mensal\n",
           "1. Confirmar empresa, CNPJ, competência e bancos; pedir extrato (OFX), saldos, guias e folha do mês.\n"
           "2. `python scripts/extrato_dominio.py ler <extrato> -o trabalho/normalizado.csv`\n"
           "3. `python scripts/extrato_dominio.py classificar trabalho/normalizado.csv -e references/empresa.json -o trabalho/classificado.csv`\n"
           "4. Para cada pendente, escrever a frase \"Foi feito um pagamento de R$ X, na data..., para...\", "
           "pesquisar o favorecido (`scripts/consulta_cnpj.py`), classificar como CONFIRMADO/PROVÁVEL/NÃO CRUZADO/DIVERGENTE "
           "e perguntar em lote.\n"
           "5. Conferir impostos com as guias e a folha com o Extrato Mensal.\n"
           "6. `python scripts/extrato_dominio.py analisar ...` e conferir saldo por banco.\n"
           "7. `python scripts/extrato_dominio.py gerar trabalho/classificado.csv -e references/empresa.json "
           "--saldo-inicial X --saldo-final Y -o <nome>.txt`\n"
           "8. Entregar TXT, resumo, perguntas em aberto e registrar aqui as decisões novas.\n",
           "\n## Pendências a Confirmar com a Contadora\n",
           ("\n".join(f"- {p}" for p in emp.get("pendencias") or []) or "- Nenhuma.") + "\n"]
    if emp.get("saldos_conferidos"):
        md += ["\n## Saldos Conferidos\n",
               tabela(["Data", "Banco", "Saldo"], [[s.get("data"), s.get("banco"), s.get("saldo")] for s in emp["saldos_conferidos"]])]
    if emp.get("observacoes"):
        md += ["\n## Histórico de Decisões\n", "\n".join(f"- {o}" for o in emp["observacoes"]) + "\n"]
    return "\n".join(md)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("empresa")
    ap.add_argument("--folha")
    ap.add_argument("--entradas", help="CSV de notas gerado por entradas_dominio.py ler")
    ap.add_argument("--impostos", help="CSV de impostos gerado por impostos_dominio.py ler")
    ap.add_argument("--socios", help="CSV acumulado de movimentos com sócios (socios_extrato.py --historico)")
    ap.add_argument("--nome", help="sufixo do nome da skill (padrão: derivado da razão social)")
    ap.add_argument("-o", "--saida", default=".")
    a = ap.parse_args()
    emp = json.load(open(a.empresa, encoding="utf-8"))
    nome_skill = "rof-contabilidade-" + (a.nome or slug(emp.get("razao_social", "")))
    destino = Path(a.saida) / nome_skill
    if destino.exists():
        shutil.rmtree(destino)
    (destino / "references").mkdir(parents=True)
    (destino / "scripts").mkdir()
    (destino / "SKILL.md").write_text(montar_skill_md(emp, nome_skill, bool(a.folha)), encoding="utf-8")
    shutil.copy(a.empresa, destino / "references" / "empresa.json")
    if a.folha:
        shutil.copy(a.folha, destino / "references" / "folha.csv")
        enc = Path(a.folha).with_name(Path(a.folha).stem + "-encargos.csv")
        if enc.exists():
            shutil.copy(enc, destino / "references" / "folha-encargos.csv")
    if a.entradas:
        shutil.copy(a.entradas, destino / "references" / "entradas.csv")
    if a.socios:
        shutil.copy(a.socios, destino / "references" / "socios.csv")
    if a.impostos:
        shutil.copy(a.impostos, destino / "references" / "impostos.csv")
    for ref in ("padrao_rof.md", "dominio.md", "classificacao.md"):
        shutil.copy(BASE / "references" / ref, destino / "references" / ref)
    for sc in ("extrato_dominio.py", "folha_extrato_mensal.py", "entradas_dominio.py", "impostos_dominio.py", "razao_dominio.py", "comprovantes_itau.py", "socios_extrato.py", "consulta_cnpj.py", "plano_contas.py"):
        shutil.copy(BASE / "scripts" / sc, destino / "scripts" / sc)
    pacote = Path(a.saida) / f"{nome_skill}.skill"
    with zipfile.ZipFile(pacote, "w", zipfile.ZIP_DEFLATED) as z:
        for f in sorted(destino.rglob("*")):
            if f.is_file():
                z.write(f, f.relative_to(destino.parent))
    print(f"Skill gerada: {destino}\nPacote para instalar: {pacote}")


if __name__ == "__main__":
    main()
