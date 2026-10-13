"""Publica carrossel no Instagram (API do Instagram com login do Instagram)."""
import time

import requests

from .config import CFG, env


def _base():
    return f"https://graph.instagram.com/{CFG['versao_api_instagram']}"


def _chamar(metodo, caminho, **params):
    params["access_token"] = env("IG_TOKEN")
    url = f"{_base()}/{caminho}"
    if metodo == "GET":
        r = requests.get(url, params=params, timeout=60)
    else:
        r = requests.post(url, data=params, timeout=60)
    try:
        j = r.json()
    except ValueError:
        j = {"resposta": r.text[:300]}
    if r.status_code >= 400 or "error" in j:
        raise RuntimeError(f"Instagram ({caminho}): {j.get('error', j)}")
    return j


def id_conta():
    fixo = env("IG_USER_ID")
    if fixo:
        return fixo
    j = _chamar("GET", "me", fields="user_id,username")
    return str(j.get("user_id") or j.get("id"))


def aguardar_url(url, tentativas=20, pausa=15):
    """O GitHub Pages leva alguns instantes para publicar a imagem nova."""
    for _ in range(tentativas):
        try:
            r = requests.get(url, timeout=20)
            if r.status_code == 200 and r.headers.get("content-type", "").startswith("image"):
                return
        except requests.RequestException:
            pass
        time.sleep(pausa)
    raise RuntimeError(f"A imagem não ficou disponível no site: {url}")


def _esperar(container_id, tentativas=30):
    for _ in range(tentativas):
        status = _chamar("GET", container_id, fields="status_code").get("status_code")
        if status == "FINISHED":
            return
        if status in ("ERROR", "EXPIRED"):
            raise RuntimeError(f"O Instagram recusou a mídia {container_id} (status {status})")
        time.sleep(4)
    raise RuntimeError(f"Tempo esgotado esperando a mídia {container_id}")


def publicar_carrossel(urls, legenda):
    conta = id_conta()
    filhos = []
    for u in urls:
        filhos.append(_chamar("POST", f"{conta}/media", image_url=u, is_carousel_item="true")["id"])
    for f in filhos:
        _esperar(f)
    carrossel = _chamar("POST", f"{conta}/media", media_type="CAROUSEL", children=",".join(filhos), caption=legenda)["id"]
    _esperar(carrossel)
    return _chamar("POST", f"{conta}/media_publish", creation_id=carrossel)["id"]
