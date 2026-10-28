"""Gera teste-escaneado.pdf (dados ficticios): 1 pagina so com imagem, usada no teste do instalador."""
import io
from decimal import Decimal

import pymupdf

LANC = [('01/10/2026', 'PIX RECEBIDO CLIENTE EXEMPLO', '100201', '1.500,00'),
        ('02/10/2026', 'TARIFA PACOTE SERVICOS', '', '-45,90'),
        ('03/10/2026', 'PAGTO BOLETO ENERGIA', '553201', '-312,47'),
        ('05/10/2026', 'TED RECEBIDA EMPRESA TESTE', '778812', '2.350,00'),
        ('06/10/2026', 'PIX ENVIADO FORNECEDOR', '100877', '-980,00'),
        ('08/10/2026', 'DEB AUTOMATICO SEGURO', '', '-129,90'),
        ('10/10/2026', 'PIX RECEBIDO CLIENTE DOIS', '101455', '640,00'),
        ('13/10/2026', 'PAGTO BOLETO ALUGUEL', '553980', '-1.800,00'),
        ('15/10/2026', 'RENDIMENTO APLICACAO', '', '12,38'),
        ('20/10/2026', 'PIX RECEBIDO CLIENTE TRES', '102033', '925,50'),
        ('27/10/2026', 'SAQUE ATM', '445120', '-200,00'),
        ('30/10/2026', 'TARIFA TED', '', '-10,50')]


def br(d):
    s = f'{abs(d):,.2f}'.replace(',', '#').replace('.', ',').replace('#', '.')
    return ('-' if d < 0 else '') + s


def dec(s):
    return Decimal(s.replace('.', '').replace(',', '.'))


src = pymupdf.open()
pg = src.new_page()
t = lambda x, y, s, f=10: pg.insert_text((x, y), s, fontsize=f)  # noqa: E731
t(40, 50, 'BANCO EXEMPLO S.A. - EXTRATO DE CONTA CORRENTE (DADOS FICTICIOS)', 11)
t(40, 70, 'Agencia: 0001  Conta: 12345-6  Titular: EMPRESA TESTE LTDA')
t(40, 86, 'Periodo: 01/10/2026 a 31/10/2026')
for x, s in [(40, 'Data'), (115, 'Historico'), (330, 'Docto'), (410, 'Valor'), (495, 'Saldo')]:
    t(x, 112, s)
saldo = Decimal('3.210,45'.replace('.', '').replace(',', '.'))
t(40, 132, '30/09/2026'); t(115, 132, 'SALDO ANTERIOR'); t(495, 132, br(saldo))
y = 150
for d, h, doc, v in LANC:
    saldo += dec(v)
    for x, s in [(40, d), (115, h), (330, doc), (410, v), (495, br(saldo))]:
        t(x, y, s)
    y += 18
t(115, y, 'SALDO FINAL'); t(495, y, br(saldo))
pix = src[0].get_pixmap(dpi=200, colorspace=pymupdf.csGRAY)
jpg = pix.tobytes('jpg', jpg_quality=70)
out = pymupdf.open()
p = out.new_page(width=pg.rect.width, height=pg.rect.height)
p.insert_image(p.rect, stream=jpg)
out.save('teste-escaneado.pdf', garbage=4, deflate=True)
print('saldo final', br(saldo), 'bytes', len(out.tobytes()))
