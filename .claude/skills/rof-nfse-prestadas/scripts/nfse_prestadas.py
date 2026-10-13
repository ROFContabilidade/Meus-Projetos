"""Planilha padrão ROF de NFS-e PRESTADAS (modelo da empresa 41 - VF Chaveiro, v3).

Abas: "Notas Prestadas", "Inconsistências", "Empresa e CNAEs".

Uso típico:
    python nfse_prestadas.py --xml pasta_com_xmls --cnpj 22993076000106 \
        --empresa "LMP3 SOLUCOES LTDA" --competencia 2026-09 --saida NFSe_Prestadas_64_LMP3_09-2026.xlsx
ou, quando as notas já foram lidas em outro lugar:
    python nfse_prestadas.py --json notas.json --saida ...
"""
import argparse
import glob
import json
import math
import os
import re
import sys
import urllib.request
import xml.etree.ElementTree as ET
from collections import Counter, OrderedDict

from openpyxl import Workbook
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import column_index_from_string, get_column_letter

NS = {"n": "http://www.sped.fazenda.gov.br/nfse"}

# ---------------------------------------------------------------- estilo do modelo 41
FONTE = "Arial"
AZUL_CAB = "FFD9E1F2"
AMARELO = "FFFFF2CC"
CINZA = "FF666666"
FMT_VALOR = "#,##0.00;\\-#,##0.00;\\-"
_fino = Side(style="thin")
BORDA = Border(left=_fino, right=_fino, top=_fino, bottom=_fino)

COLUNAS = [  # (cabeçalho, chave, largura, quebra de linha, valor numérico)
    ("Nº", "numero", 7, False, False),
    ("Emissão", "emissao", 10, False, False),
    ("Compet.", "competencia", 9, False, False),
    ("Situação", "situacao", 10, False, False),
    ("CPF/CNPJ tomador", "doc_tomador", 17, False, False),
    ("Tomador", "tomador", 30, True, False),
    ("Município do tomador", "mun_tomador", 16, True, False),
    ("Local da prestação", "local_prestacao", 16, True, False),
    ("Município de incidência do ISS", "mun_incidencia", 16, True, False),
    ("Item LC 116 / cód.", "item", 10, False, False),
    ("Atividade prestada", "atividade", 30, True, False),
    ("Anexo Simples (atividade)", "anexo", 14, False, False),
    ("Discriminação", "discriminacao", 45, True, False),
    ("Informações complementares", "info", 40, True, False),
    ("Valor serviço", "valor", 12, False, True),
    ("Base ISS", "base_iss", 10, False, True),
    ("Alíq. ISS %", "aliq_iss", 7, False, True),
    ("ISS", "iss", 10, False, True),
    ("ISS retido?", "iss_retido", 9, False, False),
    ("IRRF", "irrf", 9, False, True),
    ("PIS", "pis", 9, False, True),
    ("COFINS", "cofins", 9, False, True),
    ("CSLL", "csll", 9, False, True),
    ("INSS", "inss", 9, False, True),
    ("Total retido", "total_retido", 10, False, True),
    ("Valor líquido", "liquido", 12, False, True),
    ("Status", "status", 10, False, False),
]
LETRA = {c[1]: get_column_letter(i + 1) for i, c in enumerate(COLUNAS)}

# Anexo do Simples pela atividade (item da LC 116). Itens fora da lista ficam "conferir".
ANEXO_ITEM = {
    "01.01": "V (Fator R)", "01.02": "V (Fator R)", "01.03": "V (Fator R)", "01.04": "V (Fator R)",
    "01.05": "V (Fator R)", "01.06": "V (Fator R)", "01.07": "III", "01.08": "V (Fator R)",
    "04.01": "V (Fator R)", "04.02": "III", "04.03": "III", "06.01": "III", "06.02": "III",
    "06.03": "III", "07.02": "IV", "07.10": "IV", "07.11": "IV", "08.01": "III", "08.02": "III",
    "11.02": "IV", "14.01": "III", "14.02": "III", "14.06": "III", "17.01": "V (Fator R)",
    "17.02": "III", "17.06": "V (Fator R)", "17.12": "III", "17.19": "III", "17.25": "III",
    "24.01": "III",
}


def _f(v):
    try:
        return float(v)
    except (TypeError, ValueError):
        return None


def fmt_doc(d):
    d = re.sub(r"\D", "", d or "")
    if len(d) == 14:
        return f"{d[:2]}.{d[2:5]}.{d[5:8]}/{d[8:12]}-{d[12:]}"
    if len(d) == 11:
        return f"{d[:3]}.{d[3:6]}.{d[6:9]}-{d[9:]}"
    return d


def fmt_nbs(c):
    c = re.sub(r"\D", "", c or "")
    return f"{c[0]}.{c[1:5]}.{c[5:7]}.{c[7:9]}" if len(c) == 9 else c


UF_IBGE = {"11": "RO", "12": "AC", "13": "AM", "14": "RR", "15": "PA", "16": "AP", "17": "TO", "21": "MA",
           "22": "PI", "23": "CE", "24": "RN", "25": "PB", "26": "PE", "27": "AL", "28": "SE", "29": "BA",
           "31": "MG", "32": "ES", "33": "RJ", "35": "SP", "41": "PR", "42": "SC", "43": "RS", "50": "MS",
           "51": "MT", "52": "GO", "53": "DF"}
_cache_uf = {}


def _get_json(url):
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (ROF Contabilidade)"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.load(r)


def _nome_proprio(nome):
    minus = {"de", "da", "do", "das", "dos", "e"}
    return " ".join(p if (i and p in minus) else p.capitalize() for i, p in enumerate(nome.lower().split()))


def municipio_ibge(cod):
    """'Nome/UF' do município pelo código IBGE (lista da BrasilAPI por UF). Sem rede, devolve o código."""
    if not cod:
        return ""
    uf = UF_IBGE.get(cod[:2])
    if not uf:
        return cod
    if uf not in _cache_uf:
        try:
            lista = _get_json(f"https://brasilapi.com.br/api/ibge/municipios/v1/{uf}")
            _cache_uf[uf] = {m["codigo_ibge"]: m["nome"] for m in lista}
        except Exception:
            _cache_uf[uf] = {}
    nome = _cache_uf[uf].get(cod)
    return f"{_nome_proprio(nome)}/{uf}" if nome else cod


# ---------------------------------------------------------------- leitura dos XMLs (NFS-e Nacional)
def ler_xml(path):
    raiz = ET.parse(path).getroot()
    g = lambda p: (raiz.find(p, NS).text if raiz.find(p, NS) is not None else None)
    inf = "n:infNFSe"
    dps = f"{inf}/n:DPS/n:infDPS"
    item_cod = g(f"{dps}/n:serv/n:cServ/n:cTribNac") or ""
    item = f"{item_cod[:2]}.{item_cod[2:4]}" if len(item_cod) >= 4 else item_cod
    tp_ret_iss = g(f"{dps}/n:valores/n:trib/n:tribMun/n:tpRetISSQN")
    tp_ret_pc = g(f"{dps}/n:valores/n:trib/n:tribFed/n:piscofins/n:tpRetPisCofins")
    pc_retido = tp_ret_pc not in (None, "0", "2")
    iss_valor = _f(g(f"{inf}/n:valores/n:vISSQN"))
    nbs = g(f"{dps}/n:serv/n:cServ/n:cNBS")
    info = []
    if nbs:
        info.append(f"NBS: {fmt_nbs(nbs)} - {g(f'{inf}/n:xNBS') or ''}".strip(" -"))
    if g(f"{dps}/n:serv/n:infoCompl/n:xInfComp"):
        info.append(g(f"{dps}/n:serv/n:infoCompl/n:xInfComp"))
    p_sn = g(f"{dps}/n:valores/n:trib/n:totTrib/n:pTotTribSN")
    if p_sn:
        info.append(f"Tributos aproximados: {float(p_sn):.2f}% (Simples Nacional)")
    c_stat = g(f"{inf}/n:cStat") or ""
    tom_doc = g(f"{dps}/n:toma/n:CNPJ") or g(f"{dps}/n:toma/n:CPF")
    irrf = _f(g(f"{dps}/n:valores/n:trib/n:tribFed/n:vRetIRRF")) or 0.0
    csll = _f(g(f"{dps}/n:valores/n:trib/n:tribFed/n:vRetCSLL")) or 0.0
    inss = _f(g(f"{dps}/n:valores/n:trib/n:tribFed/n:vRetCP")) or 0.0
    pis = (_f(g(f"{dps}/n:valores/n:trib/n:tribFed/n:piscofins/n:vPis")) or 0.0) if pc_retido else 0.0
    cofins = (_f(g(f"{dps}/n:valores/n:trib/n:tribFed/n:piscofins/n:vCofins")) or 0.0) if pc_retido else 0.0
    if pc_retido and csll and abs(csll - (pis + cofins)) > 0.005 and csll > pis + cofins:
        csll = round(csll - pis - cofins, 2)  # alguns emissores somam o PCC em vRetCSLL
    return {
        "numero": g(f"{inf}/n:nNFSe"),
        "emissao": (g(f"{dps}/n:dhEmi") or "")[:10],
        "competencia": (g(f"{dps}/n:dCompet") or "")[:7],
        "situacao": "Normal" if c_stat in ("100", "") else f"cStat {c_stat}",
        "doc_tomador": fmt_doc(tom_doc),
        "tomador": g(f"{dps}/n:toma/n:xNome") or "",
        "mun_tomador": municipio_ibge(g(f"{dps}/n:toma/n:end/n:endNac/n:cMun")),
        "local_prestacao": municipio_ibge(g(f"{dps}/n:serv/n:locPrest/n:cLocPrestacao")),
        "mun_incidencia": municipio_ibge(g(f"{inf}/n:cLocIncid")),
        "item": item,
        "atividade": g(f"{inf}/n:xTribNac") or "",
        "anexo": ANEXO_ITEM.get(item, "conferir"),
        "discriminacao": g(f"{dps}/n:serv/n:cServ/n:xDescServ") or "",
        "info": " | ".join(info),
        "nbs": nbs,
        "valor": _f(g(f"{dps}/n:valores/n:vServPrest/n:vServ")) or 0.0,
        "base_iss": _f(g(f"{inf}/n:valores/n:vBC")),
        "aliq_iss": _f(g(f"{inf}/n:valores/n:pAliqAplic")),
        "iss": iss_valor,
        "iss_retido": "Sim" if tp_ret_iss in ("2", "3") else "Não",
        "iss_retido_valor": iss_valor if tp_ret_iss in ("2", "3") else 0.0,
        "irrf": irrf, "pis": pis, "cofins": cofins, "csll": csll, "inss": inss,
        "status": "Conferir",
    }


def ler_pasta(pasta):
    notas = [ler_xml(p) for p in sorted(glob.glob(os.path.join(pasta, "**", "*.xml"), recursive=True))]
    notas = [n for n in notas if n["numero"]]
    return sorted(notas, key=lambda n: int(n["numero"]))


# ---------------------------------------------------------------- apontamentos automáticos
def apontamentos_automaticos(notas, competencia):
    out = []
    nums = [int(n["numero"]) for n in notas]
    dup = sorted(k for k, v in Counter(nums).items() if v > 1)
    falt = sorted(set(range(min(nums), max(nums) + 1)) - set(nums)) if nums else []
    if falt:
        out.append(("Geral", "", "", "ERRO", "Quebra de sequência - números não recebidos: "
                    + ", ".join(map(str, falt)) + " (pedir as notas ou confirmar cancelamento)"))
    if dup:
        out.append(("Geral", "", "", "ERRO", "Números duplicados: " + ", ".join(map(str, dup))))
    for n in notas:
        k = (n["numero"], n["emissao"], n["tomador"])
        if n["situacao"] != "Normal":
            out.append(k + ("ERRO", f"Nota com situação '{n['situacao']}' - não entra no faturamento."))
        if n["competencia"] != competencia:
            out.append(k + ("ALERTA", f"Competência {n['competencia']} diferente do mês {competencia}."))
        elif n["emissao"][:7] != competencia:
            out.append(k + ("ALERTA", f"Nota emitida em {n['emissao']} com competência {competencia} "
                            "(emissão retroativa). Entra no faturamento da competência."))
        if n["mun_tomador"] and n["local_prestacao"] and n["mun_tomador"] != n["local_prestacao"]:
            out.append(k + ("ALERTA", f"Local da prestação ({n['local_prestacao']}) diferente do município "
                            f"do tomador ({n['mun_tomador']}) - confirmar onde o serviço foi feito"))
        if not n.get("nbs"):
            out.append(k + ("APONTAMENTO", "Nota sem código NBS."))
        if n["anexo"] == "conferir":
            out.append(k + ("ALERTA", f"Item {n['item']} sem anexo padrão na tabela - definir o anexo do Simples."))
    return out


def empresa_brasilapi(cnpj):
    return _get_json("https://brasilapi.com.br/api/cnpj/v1/" + re.sub(r"\D", "", cnpj))


# ---------------------------------------------------------------- geração da planilha
def _altura(textos_larguras, minimo=12.0):
    linhas = 1
    for txt, larg in textos_larguras:
        if txt:
            linhas = max(linhas, math.ceil(len(str(txt)) / max(larg * 1.15, 1)))
    return max(minimo, 11.5 * linhas + 2)


def _titulo(ws, titulo, subtitulo):
    ws["A1"] = titulo
    ws["A1"].font = Font(name=FONTE, size=12, bold=True)
    ws.row_dimensions[1].height = 15.5
    ws["A2"] = subtitulo
    ws["A2"].font = Font(name=FONTE, size=9, color=CINZA)


def _cabecalho(ws, linha, nomes):
    for i, h in enumerate(nomes, 1):
        c = ws.cell(linha, i, h)
        c.font = Font(name=FONTE, size=9, bold=True)
        c.fill = PatternFill("solid", start_color=AZUL_CAB)
        c.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
        c.border = BORDA
    ws.row_dimensions[linha].height = 30


def gerar(saida, razao, cnpj, competencia, notas, inconsistencias, empresa, cnaes, conclusao, nota_rodape=None):
    wb = Workbook()
    # ---------------- Notas Prestadas
    ws = wb.active
    ws.title = "Notas Prestadas"
    nums = [int(n["numero"]) for n in notas]
    falt = sorted(set(range(min(nums), max(nums) + 1)) - set(nums)) if nums else []
    dup = sorted(k for k, v in Counter(nums).items() if v > 1)
    seq = (f"Sequência {min(nums)} a {max(nums)} | Faltando: {', '.join(map(str, falt)) or 'nenhuma'}"
           f" | Duplicadas: {', '.join(map(str, dup)) or 'nenhuma'}") if nums else "Sem notas no período"
    _titulo(ws, f"NFS-e PRESTADAS - {razao} - {competencia}", seq)
    _cabecalho(ws, 4, [c[0] for c in COLUNAS])
    for i, (_, _, larg, _, _) in enumerate(COLUNAS):
        ws.column_dimensions[LETRA[COLUNAS[i][1]]].width = larg
    r = 5
    for n in notas:
        for i, (_, chave, larg, quebra, numerico) in enumerate(COLUNAS, 1):
            if chave == "total_retido":
                v = f"=IF(S{r}=\"Sim\",R{r},0)+SUM(T{r}:X{r})"
            elif chave == "liquido":
                v = f"=O{r}-Y{r}"
            else:
                v = n.get(chave)
                if numerico and chave in ("irrf", "pis", "cofins", "csll", "inss") and not v:
                    v = None
            c = ws.cell(r, i, v)
            c.font = Font(name=FONTE, size=9)
            c.border = BORDA
            c.alignment = Alignment(vertical="top", wrap_text=quebra)
            if numerico:
                c.number_format = FMT_VALOR
            if chave == "status":
                c.fill = PatternFill("solid", start_color=AMARELO)
        ws.row_dimensions[r].height = _altura([(n.get(k), w) for _, k, w, q, _ in COLUNAS if q])
        r += 1
    ultima = r - 1
    ws.cell(r, 1, "TOTAL (sem canceladas)").font = Font(name=FONTE, size=9, bold=True)
    for chave in ("valor", "iss", "irrf", "pis", "cofins", "csll", "inss", "total_retido", "liquido"):
        L = LETRA[chave]
        c = ws.cell(r, column_index_from_string(L),
                    f'=SUMIFS({L}5:{L}{ultima},$D$5:$D${ultima},"Normal")' if notas else 0)
        c.font = Font(name=FONTE, size=9, bold=True)
        c.number_format = FMT_VALOR
    ws.freeze_panes = "A5"
    ws.auto_filter.ref = f"A4:AA{max(ultima, 4)}"

    # ---------------- Inconsistências
    wi = wb.create_sheet("Inconsistências")
    _titulo(wi, "Inconsistências e apontamentos",
            "ERRO = corrigir/esclarecer antes de apurar | ALERTA = conferir | APONTAMENTO = observação da leitura")
    _cabecalho(wi, 4, ["Nota", "Data", "Participante", "Gravidade", "Descrição", "Resolvido?", "Observação"])
    for col, w in zip("ABCDEFG", [10, 11, 34, 14, 90, 11, 30]):
        wi.column_dimensions[col].width = w
    ordem = {"ERRO": 0, "ALERTA": 1, "APONTAMENTO": 2}
    gerais = [x for x in inconsistencias if x[0] == "Geral"]
    por_nota = sorted((x for x in inconsistencias if x[0] != "Geral"),
                      key=lambda x: (int(x[0]) if str(x[0]).isdigit() else 0, ordem.get(x[3], 3)))
    r = 5
    for nota, data, part, grav, desc in gerais + por_nota:
        for i, v in enumerate([nota, data, part, grav, desc, None, None], 1):
            c = wi.cell(r, i, v)
            c.font = Font(name=FONTE, size=9)
            c.border = BORDA
            c.alignment = Alignment(vertical="top", wrap_text=i in (3, 5, 7))
            if nota == "Geral" or grav in ("ERRO", "ALERTA"):
                c.fill = PatternFill("solid", start_color=AMARELO)
        wi.row_dimensions[r].height = _altura([(desc, 90), (part, 34)], 23)
        r += 1
    wi.freeze_panes = "A5"
    wi.auto_filter.ref = f"A4:G{max(r - 1, 4)}"

    # ---------------- Empresa e CNAEs
    we = wb.create_sheet("Empresa e CNAEs")
    _titulo(we, f"{razao} - CNPJ {fmt_doc(cnpj)}", "Consulta: BrasilAPI (base da Receita Federal)")
    for col, w in zip("ABCDE", [12, 14, 60, 16, 70]):
        we.column_dimensions[col].width = w
    r = 4
    for rot, val in empresa:
        we.cell(r, 1, rot).font = Font(name=FONTE, size=9, bold=True)
        we.cell(r, 2, val).font = Font(name=FONTE, size=9)
        r += 1
    r += 1
    _cabecalho(we, r, ["Tipo", "CNAE", "Descrição", "Anexo sugerido", "Observação"])
    r += 1
    for linha in cnaes:
        for i, v in enumerate(linha, 1):
            c = we.cell(r, i, v)
            c.font = Font(name=FONTE, size=9)
            c.border = BORDA
            c.alignment = Alignment(vertical="top", wrap_text=i in (3, 5))
        we.row_dimensions[r].height = _altura([(linha[2], 60), (linha[4], 70)])
        r += 1
    r += 1
    _cabecalho(we, r, ["Anexo", "Item LC 116", "Atividade", "Faturamento do mês"])
    r += 1
    itens = OrderedDict()
    for n in notas:
        itens.setdefault(n["item"], (n["anexo"], n["atividade"]))
    for item, (anexo, ativ) in itens.items():
        vals = [anexo, item, ativ,
                f'=SUMIFS(\'Notas Prestadas\'!$O$5:$O${ultima},\'Notas Prestadas\'!$J$5:$J${ultima},B{r},'
                f'\'Notas Prestadas\'!$D$5:$D${ultima},"Normal")']
        for i, v in enumerate(vals, 1):
            c = we.cell(r, i, v)
            c.font = Font(name=FONTE, size=9)
            c.border = BORDA
            c.alignment = Alignment(vertical="top", wrap_text=i == 3)
            if i == 4:
                c.number_format = FMT_VALOR
        r += 1
    r += 1
    we.cell(r, 1, "CONCLUSÃO - ANEXO DE TRIBUTAÇÃO").font = Font(name=FONTE, size=9, bold=True)
    we.cell(r, 1).alignment = Alignment(vertical="top", wrap_text=True)
    we.merge_cells(start_row=r, start_column=2, end_row=r, end_column=5)
    c = we.cell(r, 2, conclusao)
    c.font = Font(name=FONTE, size=9)
    c.alignment = Alignment(vertical="top", wrap_text=True)
    we.row_dimensions[r].height = _altura([(conclusao, 155)], 30)
    r += 2
    we.cell(r, 1, nota_rodape or ('O anexo é da ATIVIDADE da nota (item da LC 116). "V (Fator R)" = Anexo V, '
                                  'ou III se o Fator R for >= 28%. Referência: art. 18 LC 123/2006 e Anexo VI '
                                  'da Res. CGSN 140/2018.')).font = Font(name=FONTE, size=9, color=CINZA)
    wb.save(saida)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--json", required=True, help="especificação (empresa, CNAEs, conclusão, apontamentos; ver SKILL.md)")
    ap.add_argument("--xml", help="pasta com os XMLs das NFS-e (se omitido, usa spec['notas'])")
    ap.add_argument("--saida", required=True)
    a = ap.parse_args()
    spec = json.load(open(a.json, encoding="utf-8"))
    notas = ler_pasta(a.xml) if a.xml else spec["notas"]
    for n in notas:
        n.setdefault("status", "Conferir")
        n.setdefault("anexo", ANEXO_ITEM.get(n.get("item"), "conferir"))
    inc = [tuple(x) for x in spec.get("inconsistencias", [])]
    if spec.get("automaticos", True):
        inc = [tuple(x) for x in apontamentos_automaticos(notas, spec["competencia"])] + inc
    gerar(a.saida, spec["razao"], spec["cnpj"], spec["competencia"], notas, inc,
          spec["empresa"], spec["cnaes"], spec["conclusao"], spec.get("rodape"))


if __name__ == "__main__":
    sys.exit(main())
