"""Gera exemplos de carrossel na pasta previa/ para você ver o visual (sem Telegram, sem Instagram).

Uso:  python -m bot.demo
"""
from PIL import Image, ImageDraw

from . import cartoes
from .config import CFG, RAIZ


def _foto_exemplo(cor):
    img = Image.new("RGB", (900, 1200), (235, 235, 240))
    d = ImageDraw.Draw(img)
    d.ellipse((150, 250, 750, 850), fill=cor)
    d.rectangle((380, 850, 520, 1050), fill=cor)
    return img


def main():
    pasta = RAIZ / "previa"
    exemplos = [
        ("Fone de Ouvido Bluetooth Sem Fio TWS com Cancelamento de Ruído", "R$ 79,90", (255, 106, 43)),
        ("Organizador de Gaveta Kit 6 Peças", "R$ 24,50", (60, 140, 220)),
    ]
    for i, (nome, preco, cor) in enumerate(exemplos, 1):
        cartoes.salvar_jpg(cartoes.cartao_produto(_foto_exemplo(cor), nome, preco), pasta / f"exemplo{i}.jpg")
    cartoes.salvar_jpg(cartoes.cartao_final(CFG["instagram"] or "seuperfil"), pasta / "final.jpg")
    print(f"Imagens de exemplo em {pasta}")


if __name__ == "__main__":
    main()
