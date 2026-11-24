"""Processa a pasta ESTUDOS TRIBUTÁRIOS inteira: cada subpasta de empresa com ENTRADA/ ganha RESULTADO/.
Empresas na mesma pasta de grupo têm a receita somada para o limite do Simples.

Estrutura:
  RAIZ/<Empresa ou Grupo>/ENTRADA            -> uma empresa
  RAIZ/<Grupo>/<Empresa>/ENTRADA             -> várias empresas do mesmo grupo (mesmos sócios)

Uso: python3 processar_pasta.py <RAIZ> [--so "<nome da pasta>"]
Gera RAIZ/PAINEL.md com o resumo de todas as empresas.
"""
import argparse, json, os, subprocess, sys

AQUI = os.path.dirname(os.path.abspath(__file__))
MOTOR = os.path.join(AQUI, "motor_estudo.py")


def brl(v):
    return "R$ " + f"{v:,.0f}".replace(",", "X").replace(".", ",").replace("X", ".")


def rodar(emp, grupo_outras=None):
    cmd = [sys.executable, MOTOR, os.path.join(emp, "ENTRADA"), os.path.join(emp, "RESULTADO")]
    if grupo_outras is not None:
        cmd += ["--grupo-outras", str(grupo_outras)]
    r = subprocess.run(cmd, capture_output=True, text=True)
    print(r.stdout.strip() or r.stderr.strip()[-500:])
    try:
        return json.load(open(os.path.join(emp, "RESULTADO", "resultado.json"), encoding="utf-8"))
    except Exception:
        return None


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("raiz"); ap.add_argument("--so")
    a = ap.parse_args()
    grupos = []
    for g in sorted(os.listdir(a.raiz)):
        gp = os.path.join(a.raiz, g)
        if not os.path.isdir(gp) or g.startswith(("_", ".")) or (a.so and a.so.lower() not in g.lower()):
            continue
        if os.path.isdir(os.path.join(gp, "ENTRADA")):
            grupos.append((g, [gp]))
        else:
            emps = [os.path.join(gp, e) for e in sorted(os.listdir(gp)) if os.path.isdir(os.path.join(gp, e, "ENTRADA"))]
            if emps:
                grupos.append((g, emps))
    painel = ["# Painel de estudos tributários", "", "| Grupo | Empresa | Regime atual | Receita/ano | Melhor regime | Economia/ano | Alertas altos | Pendências |", "|---|---|---|---|---|---|---|---|"]
    for g, emps in grupos:
        res = {e: rodar(e) for e in emps}
        if len(emps) > 1:  # soma do grupo para o limite do Simples
            tot = {e: (r or {}).get("resultado", {}).get("receita_total", 0) for e, r in res.items()}
            res = {e: rodar(e, sum(v for k, v in tot.items() if k != e)) for e in emps}
        for e, r in res.items():
            if not r:
                painel.append(f"| {g} | {os.path.basename(e)} | erro | | | | | |"); continue
            altos = sum(1 for n, _ in r["alertas"] if n == "alto")
            painel.append(f"| {g} | {r['empresa']} | {r['regime_atual']} | {brl(r['resultado']['receita_total'])} | {r['resultado']['melhor']} | {brl(r['resultado']['economia'])} | {altos} | {len(r['pendencias'])} |")
    open(os.path.join(a.raiz, "PAINEL.md"), "w", encoding="utf-8").write("\n".join(painel) + "\n")
    print("\n".join(painel))


if __name__ == "__main__":
    main()
