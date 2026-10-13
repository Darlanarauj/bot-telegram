"""Conversa com o Telegram (o bot é só a sua caixa de entrada de produtos)."""
import requests

from .config import env


def _token():
    t = env("TELEGRAM_TOKEN")
    if not t:
        raise RuntimeError("Falta o segredo TELEGRAM_TOKEN")
    return t


def chamar(metodo, **dados):
    r = requests.post(f"https://api.telegram.org/bot{_token()}/{metodo}", json=dados, timeout=30)
    try:
        j = r.json()
    except ValueError:
        j = {}
    if not j.get("ok"):
        raise RuntimeError(f"Telegram {metodo}: {j.get('description', r.status_code)}")
    return j["result"]


def atualizacoes(offset):
    return chamar("getUpdates", offset=offset, timeout=0, allowed_updates=["message"])


def enviar(chat_id, texto, responder_a=None):
    """Envia mensagem. Nunca derruba o programa se falhar. Devolve a mensagem enviada."""
    dados = {"chat_id": chat_id, "text": texto}
    if responder_a:
        dados["reply_parameters"] = {"message_id": responder_a, "allow_sending_without_reply": True}
    try:
        return chamar("sendMessage", **dados)
    except Exception as ex:  # noqa: BLE001
        print(f"Aviso: não consegui enviar mensagem no Telegram ({ex})")
        return None


def baixar_arquivo(file_id):
    info = chamar("getFile", file_id=file_id)
    r = requests.get(f"https://api.telegram.org/file/bot{_token()}/{info['file_path']}", timeout=60)
    if r.status_code != 200:
        raise RuntimeError(f"Não consegui baixar a foto (status {r.status_code})")
    return r.content
