"""Conferência de extratos bancários — ROF Contabilidade.

Cruza a aba "Contabil" da planilha "Rotinas tarefas do mes.xlsm" com a varredura
das pastas do Google Drive (snapshot JSON gerado pelo Claude) e gera uma planilha
mostrando, empresa a empresa e banco a banco, quais extratos chegaram e quais faltam.

Uso:
    python conferir_extratos.py "Rotinas tarefas do mes.xlsm" snapshot.json saida.xlsx [skills_empresas.json] [regras_empresas.json]

skills_empresas.json (opcional): {"rof-contabilidade-xxx": [["KON CONTABILIDADE", 62]], ...} — empresas que já têm
skill de lançamento; gera a aba "Skills prontas" (extrato na pasta e ainda não lançado = fazer junto).

Formato do snapshot (montado pelo Claude ao varrer o Drive):
    {
      "gerado_em": "2026-10-02",
      "meses": ["04_2026", ..., "09_2026"],
      "empresas": [
        {"raiz": "Arquivos RENATA Dominio", "pasta": "17 - AP Transportes",
         "meses": {"08_2026": {"pasta_mes": true, "pasta_extrato": true,
                               "arquivos": ["sicredi_123.ofx", ...], "obs": "...",
                               "sem_movimento": false, "extrato_conferido": ""}}}
      ],
      "inativas_no_drive": ["68 - Face Doctor", ...]
    }

"lancado_confirmado": "quem/quando" quando a Rosangela confirma que o mês já foi lançado mas o TXT
não está na pasta Extrato — a aba Lançamentos passa a mostrar "Já lançado".
"extrato_conferido": "motivo" quando o Claude abriu um arquivo com nome de comprovante/imagem e
confirmou que é o extrato do mês (ex.: extrato salvo como "comprovante...pdf") — o mês vira Recebido.
"sem_movimento": true quando o Claude abriu um print/imagem da pasta Extrato e ele diz que o
período não teve movimento (ex.: "não houve movimentações") — o mês vira S/MOV.
Meses anteriores à primeira pasta de mês da empresa aparecem como "—" (ainda não era cliente
ou a estrutura de pastas foi criada depois).
"""
import json
import re
import sys
import unicodedata
from collections import OrderedDict

import openpyxl
from openpyxl.styles import Alignment, Font, PatternFill
from openpyxl.utils import get_column_letter

GRUPO_RAIZ = {
    "KON CONTABILIDADE": "Arquivos RENATA Dominio",
    "ROF SERVIÇOS": "Arquivos ROF Dominio",
    "PROTECTION CONTABILIDADE": "Arquivos PROTECTION Dominio",
}

MESES_PT = {"01": "janeiro", "02": "fevereiro", "03": "março", "04": "abril",
            "05": "maio", "06": "junho", "07": "julho", "08": "agosto",
            "09": "setembro", "10": "outubro", "11": "novembro", "12": "dezembro"}

# Banco -> (palavras na descrição da Rotina, regex no nome do arquivo)
BANCOS = OrderedDict([
    ("Nubank", (["nubank", " nu"], r"nubank|^nu[_ ]|^[0-9a-f]{8}-(?:[0-9a-f]{4}-){3}[0-9a-f]{12}-20\d\d-\d\d-\d\d|^[0-9a-f]{8}-20\d\d-\d\d-\d\d-20\d\d")),
    ("Sicredi", (["sicred"], r"sicredi|relato_rio")),
    ("Sicoob", (["sicoob"], r"sicoob")),
    ("Viacredi/Ailos", (["viacred", "via cred"], r"via ?cred|ailos")),
    ("Itaú", (["itau", "itaú"], r"ita[uú]|emps_extrato|entradas_saidas|extrato_\d{4}_\d{5,}_\d\d-\d\d-20\d\d")),
    ("Bradesco", (["bradesco"], r"bradesco")),
    ("Santander", (["santander"], r"santander|sant\.|extrato-pj-")),
    ("Mercado Pago", (["mercado pago"], r"mercado ?pago|account_statement")),
    ("PagBank", (["pagbank", "pagseguro"], r"pagbank|pagseguro")),
    ("C6 Bank", (["c6"], r"extrato-da-sua-conta|c6")),
    ("Inter", (["inter"], r"extrato-\d\d-\d\d-20\d\d-a-|inter")),
    ("Cora", (["cora"], r"_\d{8}_a_\d{8}|cora")),
    ("InfinitePay", (["infinitepay", "infinity", "infinite"], r"infinit")),
    ("Stone", (["stone"], r"stone")),
    ("Rendimento", (["rendimento"], r"rend")),
    ("Banco do Brasil", (["banco do brasil"], r"banco ?do ?brasil|bb_")),
    ("Caixa", (["caixa"], r"caixa")),
    ("Cresol", (["cresol", "credsol"], r"cresol")),
    ("Asaas", (["asaas", "asass"], r"asaas")),
    ("Bling", (["bling"], r"bling")),
    ("Efí/Gerencianet", (["gerencianet", "efi"], r"gerencianet|efi")),
    ("XP Investimentos", (["xpinvest", "xp "], r"xp")),
    ("Sisprime", (["sisprime"], r"sisprime")),
    ("Unicred", (["unicred"], r"unicred")),
])

# Arquivos produzidos pelo escritório (não são extrato enviado pelo cliente)
GERADO_ESCRITORIO = re.compile(
    r"\.txt$|retirad|concilia|pagamentos_soci|lancamentos|balancete|_txt_|dominio|prolabore|^\[pasta\]",
    re.I)
PLANILHA_CONCILIACAO = re.compile(r"retirad|concilia|prolabore|pro_labore|lancamentos", re.I)
COMPROVANTE = re.compile(r"comprovante|comprov\.|^nf_|danfe|energia", re.I)
IMAGEM = re.compile(r"\.(jpe?g|png|heic)$", re.I)
EXTRATO = re.compile(r"\.(ofx|pdf|csv|xlsx?|zip)$", re.I)

FILL = {
    "Recebido": PatternFill("solid", fgColor="C6EFCE"),
    "FALTANDO": PatternFill("solid", fgColor="FFC7CE"),
    "Verificar": PatternFill("solid", fgColor="FFEB9C"),
    "S/MOV": PatternFill("solid", fgColor="D9D9D9"),
    "—": PatternFill("solid", fgColor="EDEDED"),
}


def sem_acento(s):
    return "".join(c for c in unicodedata.normalize("NFD", s) if unicodedata.category(c) != "Mn").lower()


def numero_pasta(nome):
    m = re.match(r"\s*(\d+)\s*[-_ ]", nome)
    return int(m.group(1)) if m else None


def nome_curto(nome_rotina):
    return re.sub(r"\s*\(?CNPJ.*$", "", nome_rotina, flags=re.I).strip(" -")


def ler_rotina(caminho):
    """Empresas da aba Contabil com suas linhas de extrato."""
    wb = openpyxl.load_workbook(caminho, data_only=True)
    ws = wb["Contabil"]
    empresas, atual, grupo = [], None, None
    for r in ws.iter_rows(min_row=2, values_only=True):
        if r[0]:
            grupo = str(r[0]).strip()
        if r[2]:
            atual = {"grupo": grupo, "cod": r[3], "nome": re.sub(r"\s+", " ", str(r[2])).strip(),
                     "extratos": []}
            empresas.append(atual)
        desc = r[4]
        if atual and desc and "xtrato" in str(desc):
            atual["extratos"].append({"descricao": str(desc).strip(), "status": (r[5] or "").strip(),
                                      "obs": (r[7] or "").strip() if isinstance(r[7], str) else ""})
    return [e for e in empresas if e["extratos"]]


def banco_da_descricao(desc):
    d = " " + sem_acento(desc) + " "
    for banco, (chaves, _) in BANCOS.items():
        if any(c in d for c in chaves):
            return banco
    return None


def bancos_nos_arquivos(arquivos):
    achados = set()
    for a in arquivos:
        if GERADO_ESCRITORIO.search(a) or COMPROVANTE.search(a):
            continue
        n = sem_acento(a)
        for banco, (_, rx) in BANCOS.items():
            if re.search(rx, n, re.I):
                achados.add(banco)
    return achados


def status_mes(info):
    """Devolve (status, motivo, arquivos_de_extrato)."""
    if info is None or not info.get("pasta_mes"):
        return "FALTANDO", "pasta do mês não criada", []
    arquivos = [a for a in info.get("arquivos", []) if not a.startswith("[pasta]")]
    extratos = [a for a in arquivos if EXTRATO.search(a) and not GERADO_ESCRITORIO.search(a)
                and not COMPROVANTE.search(a)]
    imagens = [a for a in arquivos if IMAGEM.search(a) or COMPROVANTE.search(a)]
    if extratos:
        return "Recebido", "", extratos
    if info.get("extrato_conferido"):
        return "Recebido", info["extrato_conferido"], arquivos
    if info.get("sem_movimento"):
        return "S/MOV", info.get("obs") or "print do banco na pasta: período sem movimento", []
    if not info.get("pasta_extrato") and not arquivos:
        return "FALTANDO", info.get("obs") or "sem pasta Extrato", []
    if any(re.search(r"\.txt$", a, re.I) for a in arquivos):
        return "Recebido", "já lançado (TXT do escritório na pasta); extrato original não está na pasta", []
    if any(PLANILHA_CONCILIACAO.search(a) for a in arquivos) and not imagens:
        return "Recebido", "já conciliado (planilha de retiradas/conciliação na pasta); extrato original não está na pasta", []
    if imagens:
        return "Verificar", "só imagem/comprovante na pasta Extrato", []
    if arquivos:
        return "Verificar", "só arquivos do escritório, sem o extrato original", []
    return "FALTANDO", info.get("obs") or "pasta Extrato vazia", []


def casar_pastas(empresas, snap):
    """Liga cada empresa da Rotina à pasta do Drive pelo número (e pela raiz do grupo)."""
    pastas = snap["empresas"]
    for e in empresas:
        raiz = GRUPO_RAIZ.get(e["grupo"])
        candidatos = [p for p in pastas if numero_pasta(p["pasta"]) == e["cod"]]
        if raiz:
            mesma_raiz = [p for p in candidatos if p["raiz"] == raiz]
            candidatos = mesma_raiz or candidatos
        e["drive"] = candidatos[0] if candidatos else None
        e["inativa"] = any(numero_pasta(n) == e["cod"] for n in snap.get("inativas_no_drive", []))


def montar(empresas, snap, regras=None):
    meses = snap["meses"]
    regras = {(r["grupo"], r["cod"]): r for r in (regras or {}).get("regras", [])}
    linhas = []
    for e in empresas:
        regra = regras.get((e["grupo"], e["cod"]), {})
        so_smov = all(x["status"].upper() == "S/MOV" for x in e["extratos"])
        bancos_esperados = []
        for x in e["extratos"]:
            b = banco_da_descricao(x["descricao"])
            if b and b not in bancos_esperados:
                bancos_esperados.append(b)
        lin = {"empresa": e, "bancos_esperados": bancos_esperados, "meses": {}}
        meses_txt = set()
        for info in (e["drive"]["meses"].values() if e["drive"] else []):
            for a in (info or {}).get("arquivos", []):
                tag = MES_NO_TXT.search(a)
                if tag and txt_lancamento(a):
                    meses_txt.add(f"{tag.group(2)}_{tag.group(1)}")
        inicio = None
        if e["drive"]:
            inicio = next((m for m in meses if (e["drive"]["meses"].get(m) or {}).get("pasta_mes")), None)
        if regra.get("inicio") and (not inicio or chave_mes(regra["inicio"]) > chave_mes(inicio)):
            inicio = regra["inicio"]
        for m in meses:
            if inicio and chave_mes(m) < chave_mes(inicio):
                mot = regra.get("obs") if regra.get("inicio") else "sem pasta do mês no Drive (ainda não era cliente ou pastas criadas depois)"
                lin["meses"][m] = {"status": "—", "motivo": mot, "arquivos": [], "bancos": [], "bancos_nao_vistos": []}
                continue
            if e["drive"] is None and not e["inativa"] and not so_smov:
                lin["meses"][m] = {"status": "—", "motivo": "empresa nova, ainda sem pasta no Drive (conta a partir da 1ª pasta de mês criada)",
                                   "arquivos": [], "bancos": [], "bancos_nao_vistos": []}
                continue
            if e["drive"] is None:
                st, mot, arqs = ("S/MOV", "marcada S/MOV na Rotina", []) if so_smov else (
                    "FALTANDO", "empresa inativa no Drive" if e["inativa"] else "pasta da empresa não encontrada no Drive", [])
            else:
                st, mot, arqs = status_mes(e["drive"]["meses"].get(m))
                if st in ("FALTANDO", "Verificar") and so_smov:
                    st, mot = "S/MOV", "marcada S/MOV na Rotina"
            if m in regra.get("nao_e_extrato", []) and st in ("Verificar", "Recebido") and not arqs_extrato(arqs):
                st, mot = "FALTANDO", regra.get("obs") or "arquivo na pasta não é extrato (informado)"
            if regra.get("smov_ate") and chave_mes(m) <= chave_mes(regra["smov_ate"]) and st in ("FALTANDO", "Verificar"):
                st, mot = "S/MOV", regra.get("obs") or "sem movimentação bancária (informado)"
            achados = bancos_nos_arquivos(arqs)
            faltam = [b for b in bancos_esperados if b not in achados] if st == "Recebido" else []
            todos = ((e["drive"]["meses"].get(m) or {}).get("arquivos", [])) if e["drive"] else []
            info_m = (e["drive"]["meses"].get(m) or {}) if e["drive"] else {}
            if info_m.get("lancado_confirmado"):
                mot = (mot + " | " if mot else "") + "lançado: " + info_m["lancado_confirmado"]
            lin["meses"][m] = {"status": st, "motivo": mot, "arquivos": arqs, "todos": todos, "mes": m,
                               "lancado_outra_pasta": m in meses_txt,
                               "lancado_confirmado": info_m.get("lancado_confirmado"),
                               "bancos": sorted(achados), "bancos_nao_vistos": faltam}
        linhas.append(lin)
    return linhas


def arqs_extrato(arqs):
    """Arquivos que são extrato de banco (OFX/PDF/CSV/XLS), sem contar comprovantes."""
    return [a for a in arqs if not re.search(r"comprovante", a, re.I)
            and re.search(r"\.(ofx|csv|xlsx?)$", a, re.I)]


def chave_mes(m):
    mm, aa = m.split("_")
    return (int(aa), int(mm))


def rotulo_mes(m):
    mm, aa = m.split("_")
    return f"{MESES_PT[mm].capitalize()}/{aa[2:]}"


def mensagem(lin, meses_faltando):
    e = lin["empresa"]
    nome = nome_curto(e["nome"]).title()
    periodo = [f"{MESES_PT[m.split('_')[0]]}/{m.split('_')[1]}" for m in meses_faltando]
    per = periodo[0] if len(periodo) == 1 else ", ".join(periodo[:-1]) + " e " + periodo[-1]
    itens = []
    for x in e["extratos"]:
        if x["status"].upper() == "S/MOV":
            continue
        b = banco_da_descricao(x["descricao"])
        aplic = "aplica" in sem_acento(x["descricao"])
        if b:
            itens.append(f"• Extrato da {'*aplicação financeira* no' if aplic else 'conta'} *{b}*")
    itens = list(OrderedDict.fromkeys(itens)) or ["• Extratos de *todas as contas bancárias* da empresa"]
    return ("Olá, bom dia! Não identificamos o envio dos extratos bancários da *" + nome +
            "* referentes a *" + per + "*:\n" + "\n".join(itens) +
            "\n⚠️ O envio dos extratos nos formatos *PDF e OFX* é de *extrema importância* para o correto "
            "lançamento e a conciliação bancária da contabilidade. Se a empresa tiver outras contas ou "
            "aplicações financeiras, pedimos que envie também. Obrigada!")


def ajustar(ws, larguras):
    for i, w in enumerate(larguras, 1):
        ws.column_dimensions[get_column_letter(i)].width = w
    for c in ws[1]:
        c.font = Font(bold=True, color="FFFFFF")
        c.fill = PatternFill("solid", fgColor="1F4E78")
        c.alignment = Alignment(wrap_text=True, vertical="center")
    ws.freeze_panes = "A2"
    ws.auto_filter.ref = ws.dimensions


def pintar(cell):
    for k, f in FILL.items():
        if str(cell.value).startswith(k):
            cell.fill = f
            break


# TXT de lançamento do escritório (solto ou zipado). O "Extrato-dd-mm-aaaa-a-...-TXT.txt" é exportação do banco Inter.
TXT_LANCAMENTO = re.compile(r"\.txt$|txt.*\.zip$|_(pagar|receber)\.zip$", re.I)
TXT_DO_BANCO = re.compile(r"^extrato-\d\d-\d\d-\d{4}-a-", re.I)
# Mês escrito no nome do TXT (ex.: ..._2026-05_PAGAR.txt). O TXT conta para a pasta onde está e também para
# esse mês (ex.: TXT de maio salvo na pasta de junho). O mês do nome às vezes vem errado, por isso não substitui a pasta.
MES_NO_TXT = re.compile(r"(20\d\d)-(\d\d)_(pagar|receber)", re.I)


def txt_lancamento(a):
    return bool(TXT_LANCAMENTO.search(a) and not TXT_DO_BANCO.search(a))

CORES_SITUACAO = {"Pronto para lançar": "BDD7EE", "Já lançado": "C6EFCE", "Falta extrato": "FFC7CE",
                  "Verificar extrato": "FFEB9C", "S/MOV": "D9D9D9", "—": "EDEDED"}


def situacao_skill(d):
    """Situação de lançamento de um mês: já lançado, pronto para lançar, falta extrato..."""
    if d["status"] != "Recebido":
        return {"FALTANDO": "Falta extrato", "Verificar": "Verificar extrato"}.get(d["status"], d["status"])
    if d.get("lancado_confirmado"):
        return "Já lançado"
    if d.get("lancado_outra_pasta"):
        return "Já lançado"
    lancado = any(txt_lancamento(a) or PLANILHA_CONCILIACAO.search(a)
                  for a in d["todos"])
    if lancado or not d["arquivos"]:
        return "Já lançado"
    return "Pronto para lançar"


def aba_skills(wb, linhas, meses, skills):
    por_empresa = {}
    for skill, empresas in skills.items():
        for grupo, cod in empresas:
            por_empresa[(grupo, cod)] = skill
    ws = wb.create_sheet("Skills prontas", 1)
    ws.append(["Cód.", "Empresa", "Skill"] + [rotulo_mes(m) for m in meses] + ["Fazer juntos (extrato na pasta, não lançado)"])
    cores = CORES_SITUACAO
    for lin in linhas:
        e = lin["empresa"]
        skill = por_empresa.get((e["grupo"], e["cod"]))
        if not skill:
            continue
        sit = {m: situacao_skill(lin["meses"][m]) for m in meses}
        prontos = [rotulo_mes(m) for m in meses if sit[m] == "Pronto para lançar"]
        ws.append([e["cod"], nome_curto(e["nome"]), skill] + [sit[m] for m in meses] + [", ".join(prontos)])
        for i, m in enumerate(meses):
            c = ws.cell(ws.max_row, 4 + i)
            if sit[m] in cores:
                c.fill = PatternFill("solid", fgColor=cores[sit[m]])
    ajustar(ws, [6, 30, 36] + [16] * len(meses) + [40])
    return ws


def aba_lancamentos(wb, linhas, meses, skills):
    """Todas as empresas: o que já foi lançado, o que tem extrato para lançar e o que falta o cliente enviar."""
    por_empresa = {}
    for skill, empresas in (skills or {}).items():
        for grupo, cod in empresas:
            por_empresa[(grupo, cod)] = skill
    ws = wb.create_sheet("Lançamentos", 1)
    ws.append(["Grupo", "Cód.", "Empresa", "Skill"] + [rotulo_mes(m) for m in meses]
              + ["Para lançar (extrato na pasta)", "Falta o cliente enviar", "Já lançados"])
    totais = {m: {} for m in meses}
    for lin in linhas:
        e = lin["empresa"]
        sit = {m: situacao_skill(lin["meses"][m]) for m in meses}
        for m in meses:
            totais[m][sit[m]] = totais[m].get(sit[m], 0) + 1
        lista = lambda k: ", ".join(rotulo_mes(m) for m in meses if sit[m] == k)
        ws.append([e["grupo"], e["cod"], nome_curto(e["nome"]), por_empresa.get((e["grupo"], e["cod"]), "")]
                  + [sit[m] for m in meses] + [lista("Pronto para lançar"), lista("Falta extrato"), lista("Já lançado")])
        for i, m in enumerate(meses):
            c = ws.cell(ws.max_row, 5 + i)
            if sit[m] in CORES_SITUACAO:
                c.fill = PatternFill("solid", fgColor=CORES_SITUACAO[sit[m]])
    ajustar(ws, [14, 6, 32, 30] + [16] * len(meses) + [30, 30, 30])
    return totais


def gerar_xlsx(linhas, snap, saida, skills=None, regras=None):
    meses = snap["meses"]
    wb = openpyxl.Workbook()

    # Resumo: uma linha por empresa, uma coluna de status por mês
    ws = wb.active
    ws.title = "Resumo"
    ws.append(["Grupo", "Cód.", "Empresa (Rotina)", "Pasta no Drive"] + [rotulo_mes(m) for m in meses]
              + ["Meses faltando", "Observações", "Bancos na Rotina"])
    for lin in linhas:
        e = lin["empresa"]
        row = [e["grupo"], e["cod"], nome_curto(e["nome"]),
               e["drive"]["pasta"] if e["drive"] else ("INATIVAS" if e["inativa"] else "não encontrada")]
        row += [lin["meses"][m]["status"] for m in meses]
        falt = [rotulo_mes(m) for m in meses if lin["meses"][m]["status"] == "FALTANDO"]
        obs = [f"{rotulo_mes(m)}: {lin['meses'][m]['motivo']}" for m in meses
               if lin["meses"][m]["motivo"] and lin["meses"][m]["status"] not in ("—",)]
        row += [", ".join(falt), " | ".join(obs), ", ".join(lin["bancos_esperados"])]
        ws.append(row)
        for i, _ in enumerate(meses):
            c = ws.cell(ws.max_row, 5 + i)
            c.alignment = Alignment(horizontal="center")
            pintar(c)
    ajustar(ws, [14, 6, 34, 30] + [11] * len(meses) + [24, 70, 26])

    # Detalhes: uma linha por empresa x mês
    wsd = wb.create_sheet("Detalhes")
    wsd.append(["Cód.", "Empresa", "Mês", "Status", "Motivo", "Bancos achados", "Bancos da Rotina não vistos"])
    for lin in linhas:
        e = lin["empresa"]
        for m in meses:
            d = lin["meses"][m]
            wsd.append([e["cod"], nome_curto(e["nome"]), rotulo_mes(m), d["status"], d["motivo"],
                        ", ".join(d["bancos"]), ", ".join(d["bancos_nao_vistos"])])
            pintar(wsd.cell(wsd.max_row, 4))
    ajustar(wsd, [6, 32, 12, 12, 60, 24, 24])

    # Por banco
    wb2 = wb.create_sheet("Por banco")
    wb2.append(["Cód.", "Empresa", "Extrato (Rotina)", "Status na Rotina", "Banco reconhecido"]
               + [f"{rotulo_mes(m)}" for m in meses])
    for lin in linhas:
        e = lin["empresa"]
        for x in e["extratos"]:
            b = banco_da_descricao(x["descricao"])
            row = [e["cod"], nome_curto(e["nome"]), x["descricao"], x["status"], b or "?"]
            for m in meses:
                d = lin["meses"][m]
                if x["status"].upper() == "S/MOV":
                    row.append("S/MOV")
                elif d["status"] != "Recebido":
                    row.append(d["status"])
                elif b and b in d["bancos"]:
                    row.append("Recebido")
                elif not d["arquivos"]:
                    row.append("Recebido (já lançado)")
                else:
                    row.append("Verificar — nome do arquivo não indica o banco")
            wb2.append(row)
            for i, _ in enumerate(meses):
                pintar(wb2.cell(wb2.max_row, 6 + i))
    ajustar(wb2, [6, 32, 40, 14, 16] + [22] * len(meses))

    # Mensagens
    ws3 = wb.create_sheet("Mensagens")
    ws3.append(["Cód.", "Empresa", "Meses pendentes", "Mensagem (copiar e colar no WhatsApp)", "Enviado?", "Data envio"])
    for lin in linhas:
        falt = [m for m in meses if lin["meses"][m]["status"] == "FALTANDO"
                and "não encontrada" not in lin["meses"][m]["motivo"]
                and "inativa" not in lin["meses"][m]["motivo"]]
        if not falt:
            continue
        e = lin["empresa"]
        ws3.append([e["cod"], nome_curto(e["nome"]), ", ".join(rotulo_mes(m) for m in falt),
                    mensagem(lin, falt), "Não", ""])
        ws3.cell(ws3.max_row, 4).alignment = Alignment(wrap_text=True, vertical="top")
    ajustar(ws3, [6, 30, 18, 90, 10, 12])

    # Arquivos
    ws4 = wb.create_sheet("Arquivos encontrados")
    ws4.append(["Cód.", "Empresa", "Mês", "Arquivo"])
    for lin in linhas:
        e = lin["empresa"]
        for m in meses:
            for a in lin["meses"][m]["arquivos"]:
                ws4.append([e["cod"], nome_curto(e["nome"]), rotulo_mes(m), a])
    ajustar(ws4, [6, 32, 12, 70])

    if skills:
        aba_skills(wb, linhas, meses, skills)
    totais_lanc = aba_lancamentos(wb, linhas, meses, skills)

    # Painel
    ws5 = wb.create_sheet("Painel", 0)
    ws5.append([f"Conferência de extratos — gerado em {snap['gerado_em']}"])
    ws5["A1"].font = Font(bold=True, size=14)
    ws5.append([])
    ws5.append(["Mês", "Recebido", "FALTANDO", "Verificar", "S/MOV", "—", "Total"])
    for m in meses:
        cont = {k: 0 for k in ["Recebido", "FALTANDO", "Verificar", "S/MOV", "—"]}
        for lin in linhas:
            cont[lin["meses"][m]["status"]] += 1
        ws5.append([rotulo_mes(m)] + list(cont.values()) + [sum(cont.values())])
    ws5.append([])
    ws5.append(["Lançamento", "Já lançado", "Para lançar", "Falta extrato", "Verificar", "S/MOV", "—"])
    lin_cab = ws5.max_row
    for c in ws5[lin_cab]:
        c.font = Font(bold=True)
    for i, k in enumerate(["Já lançado", "Pronto para lançar", "Falta extrato", "Verificar extrato", "S/MOV", "—"], 2):
        ws5.cell(lin_cab, i).fill = PatternFill("solid", fgColor=CORES_SITUACAO[k])
    for m in meses:
        t = totais_lanc[m]
        ws5.append([rotulo_mes(m)] + [t.get(k, 0) for k in ["Já lançado", "Pronto para lançar", "Falta extrato",
                                                            "Verificar extrato", "S/MOV", "—"]])
    ws5.append([])
    ws5.append(["Legenda"])
    for k, t in [("Recebido", "extrato (OFX/PDF/CSV/XLS) na pasta Extrato do mês, ou já lançado/conciliado pelo escritório"),
                 ("FALTANDO", "pasta Extrato vazia, sem pasta Extrato ou pasta do mês não criada — pedir ao cliente"),
                 ("Verificar", "só imagem/comprovante ou só arquivos gerados pelo escritório"),
                 ("S/MOV", "contas marcadas S/MOV na Rotina, ou print do banco na pasta dizendo que o período não teve movimento"),
                 ("—", "antes do 1º mês da empresa: pasta do mês ainda não criada, empresa nova sem pasta, ou início informado")]:
        ws5.append([k, t])
        ws5.cell(ws5.max_row, 1).fill = FILL[k]
        ws5.merge_cells(start_row=ws5.max_row, start_column=2, end_row=ws5.max_row, end_column=10)
    for c in ws5[3]:
        c.font = Font(bold=True)
    for i, k in enumerate(["Recebido", "FALTANDO", "Verificar", "S/MOV", "—"], 2):
        ws5.cell(3, i).fill = FILL[k]
    if regras and regras.get("regras"):
        ws5.append([])
        ws5.append(["Situações informadas"])
        ws5.cell(ws5.max_row, 1).font = Font(bold=True)
        for r in regras["regras"]:
            ws5.append([r["cod"], r.get("obs", "")])
            ws5.merge_cells(start_row=ws5.max_row, start_column=2, end_row=ws5.max_row, end_column=10)
        ws5.append(["novas", "empresa sem pasta no Drive: '—' até a pasta do 1º mês ser criada (esse é o 1º mês de atividade)"])
        ws5.merge_cells(start_row=ws5.max_row, start_column=2, end_row=ws5.max_row, end_column=10)
    ws5.column_dimensions["A"].width = 16
    for col in "BCDEFG":
        ws5.column_dimensions[col].width = 12
    wb.save(saida)


def main():
    rotina, snapshot, saida = sys.argv[1:4]
    skills = json.load(open(sys.argv[4], encoding="utf-8")) if len(sys.argv) > 4 else None
    regras = json.load(open(sys.argv[5], encoding="utf-8")) if len(sys.argv) > 5 else None
    snap = json.load(open(snapshot, encoding="utf-8"))
    empresas = ler_rotina(rotina)
    casar_pastas(empresas, snap)
    linhas = montar(empresas, snap, regras)
    gerar_xlsx(linhas, snap, saida, skills, regras)
    for m in snap["meses"]:
        falt = [f"{l['empresa']['cod']} {nome_curto(l['empresa']['nome'])}" for l in linhas
                if l["meses"][m]["status"] == "FALTANDO"]
        print(f"{rotulo_mes(m)}: {len(falt)} faltando")
    print("Planilha:", saida)


if __name__ == "__main__":
    main()
