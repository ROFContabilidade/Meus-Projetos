"""Trecho inserido em scripts/extrato_dominio.py: leitura do _extrato.md do Conversor de extratos ROF."""

ORIGINAL_MD5 = "a9d70ad4108fd89a307df5de9e118a5e"  # extrato_dominio.py das skills em 29/10/2026

FUNCAO = r'''
def ler_extrato_md(texto):
    """Lê o _extrato.md do Conversor de extratos ROF (tabela data|histórico|doc|valor|saldo).

    Recusa (SystemExit) se o Confere não for "sim" ou se a tabela não foi montada:
    nesses casos a Rosangela precisa ser avisada antes de lançar.
    """
    linhas_md = texto.splitlines()
    titulo = linhas_md[0].strip() if linhas_md else ""
    if not titulo.startswith("# Extrato -"):
        raise SystemExit("AVISAR A ROSANGELA: o arquivo não começa com '# Extrato -' (é documento, não extrato).")
    cab, i = [], 1
    while i < len(linhas_md) and not linhas_md[i].lower().startswith("data|"):
        cab.append(linhas_md[i].strip())
        i += 1
    cabecalho = " | ".join(cab)
    origem = next((c[len("Origem:"):].split("|")[0].strip() for c in cab if c.startswith("Origem:")), "")
    if i >= len(linhas_md):
        raise SystemExit("AVISAR A ROSANGELA: tabela do extrato NÃO montada pelo conversor (sem Confere). "
                         f"Não lançar; ver a imagem da página em: {origem}")
    m = re.search(r"Confere:\s*([^|]+)", cabecalho)
    confere = (m.group(1).strip() if m else "")
    if normalizar_texto(confere) != "SIM":
        raise SystemExit(f"AVISAR A ROSANGELA: Confere = '{confere or 'ausente'}'. Não lançar antes de conferir; "
                         f"imagem da página em: {origem}")
    colunas = [normalizar_texto(c) for c in linhas_md[i].split("|")]
    pos = {nome: colunas.index(nome) for nome in ("DATA", "HISTORICO", "DOC", "VALOR", "SALDO") if nome in colunas}
    linhas, ocr = [], []
    for bruta in linhas_md[i + 1:]:
        if not bruta.strip() or bruta.startswith("#"):
            break
        partes = bruta.split("|")
        campo = lambda nome: partes[pos[nome]].strip() if nome in pos and pos[nome] < len(partes) else ""
        valor = parse_valor(campo("VALOR").replace("[OCR]", ""))
        if valor is None:  # "Saldo do dia" e linhas só de saldo
            continue
        data = parse_data(campo("DATA"))
        if data is None:
            raise SystemExit(f"AVISAR A ROSANGELA: data inválida na linha do extrato: {bruta}")
        desc = campo("HISTORICO").replace("[OCR]", "").strip()
        if "[OCR]" in bruta:
            ocr.append(f"{data:%d/%m/%Y} {desc} {fmt_brl(valor)}")
        linhas.append({"data": data.strftime("%d/%m/%Y"), "descricao": desc,
                       "documento": campo("DOC"), "valor": str(valor), "id": ""})
    info = {"conversor": cabecalho[:300], "confere": confere}
    if ocr:
        info["ATENCAO_OCR"] = (f"{len(ocr)} linha(s) lida(s) por OCR; conferir com a Rosangela antes de lançar: "
                               + "; ".join(ocr[:10]) + f" | imagem em: {origem}")
    return linhas, info

'''

DESPACHO_ANTES = '    if texto.lstrip().startswith("|0000|"):\n'
DESPACHO_DEPOIS = (
    '    if texto.lstrip().startswith("# Extrato -") or texto.lstrip().startswith("# Documento -"):\n'
    '        linhas, info = ler_extrato_md(texto.lstrip())\n'
    '        origem = "Conversor de extratos ROF (_extrato.md)"\n'
    '    elif texto.lstrip().startswith("|0000|"):\n'
)
ANCORA_FUNCAO = "def cmd_ler(a):\n"


def aplicar(codigo):
    """Devolve o código com a leitura do _extrato.md (sem duplicar)."""
    if "def ler_extrato_md(" in codigo:
        return codigo
    if DESPACHO_ANTES not in codigo or ANCORA_FUNCAO not in codigo:
        raise ValueError("extrato_dominio.py com estrutura diferente: não alterado")
    codigo = codigo.replace(ANCORA_FUNCAO, FUNCAO.lstrip("\n") + "\n" + ANCORA_FUNCAO, 1)
    return codigo.replace(DESPACHO_ANTES, DESPACHO_DEPOIS, 1)
