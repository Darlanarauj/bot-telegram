"""Caminhos e configurações do projeto."""
import json
import os
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
DATA = RAIZ / "data"
SITE = RAIZ / "site"
ESTADO = DATA / "estado.json"
SELECAO = DATA / "selecao.json"

PADRAO = {
    "titulo_site": "Achadinhos do Dia",
    "subtitulo_site": "Os melhores achadinhos da Shopee",
    "instagram": "",
    "produtos_por_post": 3,
    "max_produtos_na_pagina": 40,
    "hashtags": ["#publi", "#achadinhos", "#shopee"],
    "aviso_afiliado": "Publicidade: links de afiliado. Posso receber comissão se você comprar.",
    "max_tentativas": 3,
    "manter_imagens": 80,
    "modelo_gemini": "gemini-2.5-flash",
    "versao_api_instagram": "v23.0",
}


def _carregar():
    cfg = dict(PADRAO)
    arq = RAIZ / "config.json"
    if arq.exists():
        try:
            cfg.update(json.loads(arq.read_text(encoding="utf-8")))
        except ValueError as ex:
            raise SystemExit(f"config.json está com erro de formato: {ex}")
    return cfg


CFG = _carregar()


def env(nome, padrao=""):
    return os.environ.get(nome, padrao).strip()


def modo_teste():
    return env("TESTE") == "1"


def url_base_site():
    """Endereço público da página (GitHub Pages) a partir de GITHUB_REPOSITORY."""
    repo = env("GITHUB_REPOSITORY")
    if "/" not in repo:
        return env("SITE_URL", "http://localhost:8000").rstrip("/")
    dono, nome = repo.split("/", 1)
    dono = dono.lower()
    if nome.lower() == f"{dono}.github.io":
        return f"https://{dono}.github.io"
    return f"https://{dono}.github.io/{nome}"
