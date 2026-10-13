"""Rode com:  python tests/test_parse.py"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from bot.parse import formatar_preco, link_valido, parse_legenda  # noqa: E402


def t(texto, nome, preco, link=None, detalhes=""):
    r = parse_legenda(texto)
    assert r["nome"] == nome, (texto, r)
    assert r["preco"] == preco, (texto, r)
    assert r["link"] == link, (texto, r)
    assert r["detalhes"] == detalhes, (texto, r)


t("Fone Bluetooth\n79,90", "Fone Bluetooth", "R$ 79,90")
t("Fone Bluetooth\nR$ 79,90\nhttps://s.shopee.com.br/abc123", "Fone Bluetooth", "R$ 79,90", "https://s.shopee.com.br/abc123")
t("Fone Bluetooth | 79,90", "Fone Bluetooth", "R$ 79,90")
t("Fone Bluetooth R$ 1.299,90 frete grátis", "Fone Bluetooth frete grátis", "R$ 1.299,90")
t("Fone Bluetooth\npreço: 79.90", "Fone Bluetooth", "R$ 79,90")
t("Fone Bluetooth\n79\nBateria dura 20h\nhttps://shope.ee/x.", "Fone Bluetooth", "R$ 79,00", "https://shope.ee/x", "Bateria dura 20h")
t("Só o nome do produto", "Só o nome do produto", None)
t("Kit 3 pares de meia\nR$ 19,9", "Kit 3 pares de meia", "R$ 19,90")

assert formatar_preco(1234.5) == "R$ 1.234,50"
assert link_valido("https://s.shopee.com.br/abc")
assert link_valido("https://shopee.com.br/produto")
assert link_valido("https://shope.ee/abc")
assert not link_valido("https://google.com/shopee.com.br")
assert not link_valido("https://evilshopee.com.br/x")
print("Todos os testes passaram.")
