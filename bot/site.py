"""Gera a página de ofertas (o link da bio) em site/index.html."""
import html
from string import Template

from .config import CFG, SITE

PAGINA = Template("""<!doctype html>
<html lang="pt-BR">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>$titulo</title>
<link rel="icon" href="data:,">
<style>
:root{--fundo:#111114;--cartao:#1b1b21;--texto:#f4f4f6;--suave:#a9a9b4;--destaque:#ff6a2b}
*{box-sizing:border-box}
body{margin:0;background:var(--fundo);color:var(--texto);font-family:system-ui,-apple-system,"Segoe UI",Roboto,sans-serif}
header{padding:32px 16px 8px;text-align:center}
h1{margin:0;font-size:1.6rem}
header p{margin:6px 0 0;color:var(--suave)}
main{max-width:640px;margin:0 auto;padding:16px}
.card{display:flex;gap:14px;background:var(--cartao);border-radius:16px;padding:12px;margin-bottom:14px;align-items:center}
.card img{width:112px;height:112px;object-fit:cover;border-radius:12px;flex:none;background:#000}
.info{min-width:0;flex:1}
.info h2{margin:0 0 6px;font-size:1rem;line-height:1.25;font-weight:600;overflow:hidden;display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical}
.preco{margin:0 0 10px;font-size:1.3rem;font-weight:800;color:var(--destaque)}
.btn{display:inline-block;background:var(--destaque);color:#fff;text-decoration:none;font-weight:700;padding:10px 18px;border-radius:999px;font-size:.95rem}
.vazio{text-align:center;color:var(--suave);padding:40px 0}
footer{max-width:640px;margin:0 auto;padding:8px 16px 40px;color:var(--suave);font-size:.8rem;text-align:center}
</style>
</head>
<body>
<header><h1>$titulo</h1><p>$subtitulo</p></header>
<main>
$cartoes
</main>
<footer>$aviso</footer>
</body>
</html>
""")


def _cartao(p):
    nome = html.escape(p["nome"])
    preco = f'<p class="preco">{html.escape(p["preco"])}</p>' if p.get("preco") else ""
    link = html.escape(p["link"], quote=True)
    return (
        f'<article class="card"><img src="fotos/{p["id"]}.jpg" alt="{nome}" loading="lazy">'
        f'<div class="info"><h2>{nome}</h2>{preco}'
        f'<a class="btn" href="{link}" target="_blank" rel="sponsored nofollow noopener">Comprar na Shopee</a>'
        f"</div></article>"
    )


def gerar(estado):
    SITE.mkdir(parents=True, exist_ok=True)
    itens = [
        p for p in estado["produtos"]
        if p["status"] in ("agendado", "postado") and p.get("link") and not p.get("imagens_removidas")
    ]
    itens.sort(key=lambda p: p["id"], reverse=True)
    itens = itens[: CFG["max_produtos_na_pagina"]]
    cartoes = "\n".join(_cartao(p) for p in itens) or '<p class="vazio">Em breve, novos achadinhos por aqui.</p>'
    pagina = PAGINA.substitute(
        titulo=html.escape(CFG["titulo_site"]),
        subtitulo=html.escape(CFG["subtitulo_site"]),
        aviso=html.escape(CFG["aviso_afiliado"]),
        cartoes=cartoes,
    )
    (SITE / "index.html").write_text(pagina, encoding="utf-8")
    return len(itens)
