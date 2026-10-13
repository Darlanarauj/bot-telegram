"""Monta a legenda e posta o carrossel no Instagram."""
import json
import sys

from . import estado as est, instagram, legenda, telegram
from .config import CFG, SELECAO, env, modo_teste, url_base_site


def _avisar(texto):
    chat = env("TELEGRAM_CHAT_ID")
    if chat and env("TELEGRAM_TOKEN"):
        telegram.enviar(chat, texto)


def main():
    e = est.carregar()
    ids = json.loads(SELECAO.read_text(encoding="utf-8")).get("ids", []) if SELECAO.exists() else []
    produtos = [p for p in e["produtos"] if p["id"] in ids]
    if not produtos:
        print("Fila vazia: nada para postar agora.")
        return
    texto = legenda.montar(produtos)
    base = url_base_site()
    urls = [f"{base}/cards/{p['id']}.jpg" for p in produtos] + [f"{base}/cards/final.jpg"]
    print("---- LEGENDA ----")
    print(texto)
    print("---- IMAGENS ----")
    print("\n".join(urls))
    if modo_teste():
        print("MODO TESTE: não postei no Instagram.")
        return
    if not env("IG_TOKEN"):
        sys.exit("Falta o segredo IG_TOKEN.")
    try:
        for u in urls:
            instagram.aguardar_url(u)
        media_id = instagram.publicar_carrossel(urls, texto)
    except Exception as ex:  # noqa: BLE001
        print(f"ERRO ao postar: {ex}")
        for p in produtos:
            p["tentativas"] = p.get("tentativas", 0) + 1
            p["ultimo_erro"] = str(ex)[:300]
            if p["tentativas"] >= CFG["max_tentativas"]:
                p["status"] = est.ERRO
        est.salvar(e)
        _avisar(f"⚠️ Não consegui postar no Instagram: {str(ex)[:300]}")
        sys.exit(1)
    for p in produtos:
        p["status"] = est.POSTADO
        p["postado_em"] = est.agora()
        p["ig_media_id"] = media_id
    est.salvar(e)
    SELECAO.write_text(json.dumps({"ids": []}) + "\n", encoding="utf-8")
    _avisar(f"🚀 Postado no Instagram: {', '.join(p['nome'] for p in produtos)}")
    print("Postado com sucesso:", media_id)


if __name__ == "__main__":
    main()
