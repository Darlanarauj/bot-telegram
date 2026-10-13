"""Escreve a legenda do post (até 150 caracteres + aviso de publicidade + hashtags)."""
import re

import requests

from .config import CFG, env


def _cortar(texto, limite=150):
    texto = " ".join(texto.split())
    if len(texto) <= limite:
        return texto
    corte = texto[: limite - 1].rsplit(" ", 1)[0].rstrip(",.;:-!? ")
    return corte + "…"


def _gemini(produtos):
    chave = env("GEMINI_API_KEY")
    if not chave:
        return None
    linhas = []
    for p in produtos:
        item = f"- {p['nome']}"
        if p.get("preco"):
            item += f" ({p['preco']})"
        if p.get("detalhes"):
            item += f" - {p['detalhes']}"
        linhas.append(item)
    prompt = (
        "Você escreve legendas de Instagram em português do Brasil para um perfil de achadinhos da Shopee.\n"
        "Escreva UMA legenda com no máximo 150 caracteres sobre estes produtos:\n"
        + "\n".join(linhas)
        + "\n\nRegras: tom animado e natural, no máximo 1 emoji, sem hashtags, sem links, "
        "diga que o link está na bio, e NÃO invente características que não estão na lista. "
        "Responda só com a legenda."
    )
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{CFG['modelo_gemini']}:generateContent"
    r = requests.post(
        url,
        headers={"x-goog-api-key": chave, "Content-Type": "application/json"},
        json={"contents": [{"parts": [{"text": prompt}]}]},
        timeout=40,
    )
    r.raise_for_status()
    texto = r.json()["candidates"][0]["content"]["parts"][0]["text"]
    texto = re.sub(r"https?://\S+|#\w+", "", texto).strip().strip('"“”\'')
    return texto or None


def _padrao(produtos):
    if len(produtos) == 1:
        p = produtos[0]
        preco = f" por {p['preco']}" if p.get("preco") else ""
        return f"Achadinho do dia: {p['nome']}{preco}! Link na bio 👆"
    nomes = ", ".join(p["nome"] for p in produtos[:3])
    return f"Achadinhos do dia: {nomes}. Link na bio 👆"


def montar(produtos):
    try:
        principal = _gemini(produtos)
    except Exception as ex:  # noqa: BLE001
        print(f"Aviso: o Gemini falhou ({type(ex).__name__}); usando legenda padrão.")
        principal = None
    principal = _cortar(principal or _padrao(produtos))
    if "bio" not in principal.lower():
        principal = _cortar(principal, 150 - len(" Link na bio!")) + " Link na bio!"
    return f"{principal}\n\nPublicidade | link de afiliado\n{' '.join(CFG['hashtags'])}"
