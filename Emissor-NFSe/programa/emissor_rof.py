# -*- coding: utf-8 -*-
"""Emissor ROF de NFS-e - ponto de entrada.

Abre a tela no navegador. Para encerrar, feche esta janela preta.
Uso:  python emissor_rof.py            (abre o programa)
      python emissor_rof.py --testes   (roda os testes automáticos)
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def main():
    if "--testes" in sys.argv:
        import runpy
        sys.argv = [sys.argv[0]]
        runpy.run_path(os.path.join(os.path.dirname(os.path.abspath(__file__)), "testes", "testar_tudo.py"), run_name="__main__")
        return
    from rof_nfse import regras, servidor
    srv, url = servidor.iniciar(abrir_navegador="--sem-navegador" not in sys.argv,
                                porta=int(os.environ.get("EMISSOR_ROF_PORTA") or 0))
    print("=" * 62)
    print("  EMISSOR ROF DE NFS-e  -  versão " + regras.VERSAO)
    print("=" * 62)
    print("  A tela abriu no seu navegador. Se não abriu, acesse:")
    print("  " + url)
    print()
    print("  Deixe esta janela aberta enquanto usa o programa.")
    print("  Para encerrar, feche esta janela.")
    print("=" * 62)
    try:
        srv.serve_forever()
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
