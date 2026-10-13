"""Lê as mensagens novas do Telegram e coloca os produtos na fila."""
from . import cartoes, estado as est, telegram
from .config import SITE, env
from .parse import link_valido, parse_legenda

AJUDA = (
    "Oi! Eu guardo seus achadinhos e posto no Instagram.\n\n"
    "1) Mande a FOTO do produto com esta legenda:\n"
    "Nome do produto\n"
    "79,90\n"
    "(e o link de afiliado, se já tiver)\n\n"
    "2) Se ainda não tem o link, depois mande o link RESPONDENDO a minha mensagem de confirmação.\n\n"
    "/fila - ver o que está na fila\n"
    "/apagar - responda a um produto com isso para cancelar"
)


def _resumo(p):
    preco = f" - {p['preco']}" if p.get("preco") else ""
    return f"{p['id']} {p['nome']}{preco}"


def _fila_texto(e):
    prontos = est.por_status(e, est.PRONTO, est.AGENDADO)
    esperando = est.por_status(e, est.AGUARDANDO_LINK)
    partes = [f"Prontos para postar: {len(prontos)} | Esperando link: {len(esperando)}"]
    partes += ["✅ " + _resumo(p) for p in prontos[:10]]
    partes += ["⏳ " + _resumo(p) for p in esperando[:10]]
    return "\n".join(partes)


def _guardar_foto(p, file_id):
    foto = cartoes.abrir_foto(telegram.baixar_arquivo(file_id))
    cartoes.salvar_jpg(foto, SITE / "fotos" / f"{p['id']}.jpg")
    cartoes.salvar_jpg(cartoes.cartao_produto(foto, p["nome"], p.get("preco")), SITE / "cards" / f"{p['id']}.jpg")


def _responder(chat_id, p, texto, msg_id):
    enviado = telegram.enviar(chat_id, texto, responder_a=msg_id)
    if enviado:
        p["msg_ids"].append(enviado["message_id"])


def _tratar_foto(e, msg, chat_id, texto):
    dados = parse_legenda(texto)
    if not dados["nome"]:
        telegram.enviar(chat_id, "Mande a foto com uma legenda: nome do produto e preço (e o link, se já tiver).", msg["message_id"])
        return
    aviso = ""
    link = dados["link"]
    if link and not link_valido(link):
        aviso = "\n⚠️ Esse link não parece ser da Shopee, então não guardei. Mande o link de afiliado depois."
        link = None
    p = est.novo_produto(
        e, nome=dados["nome"], preco=dados["preco"], detalhes=dados["detalhes"], link=link,
        status=est.PRONTO if link else est.AGUARDANDO_LINK,
    )
    p["msg_ids"].append(msg["message_id"])
    try:
        _guardar_foto(p, msg["photo"][-1]["file_id"])
    except Exception as ex:  # noqa: BLE001
        p["status"] = est.CANCELADO
        telegram.enviar(chat_id, f"Não consegui processar essa foto ({ex}). Tente enviar de novo.", msg["message_id"])
        return
    sem_preco = "" if p["preco"] else "\n(Não achei o preço. Se quiser, mande a foto de novo com o preço em uma linha.)"
    if p["status"] == est.PRONTO:
        _responder(chat_id, p, f"✅ Na fila: {_resumo(p)}{sem_preco}{aviso}", msg["message_id"])
    else:
        _responder(chat_id, p, f"📸 Guardei: {_resumo(p)}\nFalta o link de afiliado: responda esta mensagem com o link.{sem_preco}{aviso}", msg["message_id"])


def _tratar_texto(e, msg, chat_id, texto):
    dados = parse_legenda(texto)
    if not dados["link"]:
        telegram.enviar(chat_id, "Não entendi. Mande uma foto com o nome e o preço, ou um link de afiliado respondendo a um produto. /start mostra a ajuda.", msg["message_id"])
        return
    if not link_valido(dados["link"]):
        telegram.enviar(chat_id, "Esse link não parece ser da Shopee. Mande o link de afiliado (s.shopee.com.br/...).", msg["message_id"])
        return
    alvo = None
    resp = msg.get("reply_to_message")
    if resp:
        alvo = est.achar_por_msg(e, resp["message_id"])
    if alvo is None:
        esperando = est.por_status(e, est.AGUARDANDO_LINK)
        alvo = esperando[-1] if esperando else None
    if alvo is None or alvo["status"] not in (est.AGUARDANDO_LINK, est.PRONTO):
        telegram.enviar(chat_id, "Não achei produto esperando link. Mande primeiro a foto com nome e preço.", msg["message_id"])
        return
    alvo["link"] = dados["link"]
    alvo["status"] = est.PRONTO
    _responder(chat_id, alvo, f"✅ Link guardado, na fila: {_resumo(alvo)}", msg["message_id"])


def _tratar(e, msg, chat_id):
    texto = (msg.get("text") or msg.get("caption") or "").strip()
    if texto.startswith(("/start", "/ajuda", "/help")):
        telegram.enviar(chat_id, AJUDA)
    elif texto.startswith("/fila"):
        telegram.enviar(chat_id, _fila_texto(e))
    elif texto.startswith("/apagar"):
        resp = msg.get("reply_to_message")
        p = est.achar_por_msg(e, resp["message_id"]) if resp else None
        if p and p["status"] != est.POSTADO:
            p["status"] = est.CANCELADO
            telegram.enviar(chat_id, f"🗑️ Cancelado: {_resumo(p)}")
        else:
            telegram.enviar(chat_id, "Responda a mensagem do produto com /apagar. Produto já postado não dá para cancelar.")
    elif msg.get("photo"):
        _tratar_foto(e, msg, chat_id, texto)
    elif texto:
        _tratar_texto(e, msg, chat_id, texto)


def main():
    if not env("TELEGRAM_TOKEN"):
        print("TELEGRAM_TOKEN não configurado, pulando.")
        return
    e = est.carregar()
    dono = env("TELEGRAM_CHAT_ID")
    novas = telegram.atualizacoes(e["update_offset"])
    if not dono:
        for up in novas:
            msg = up.get("message")
            if msg:
                cid = msg["chat"]["id"]
                print(f"Recebi mensagem do chat {cid}. Coloque esse número no segredo TELEGRAM_CHAT_ID.")
                telegram.enviar(cid, f"Seu número de chat é {cid}. Coloque ele no GitHub, no segredo TELEGRAM_CHAT_ID, e rode de novo.")
                break
        else:
            print("Nenhuma mensagem nova.")
        return  # não consome as mensagens enquanto o dono não estiver configurado
    for up in novas:
        e["update_offset"] = up["update_id"] + 1
        msg = up.get("message")
        if not msg or str(msg["chat"]["id"]) != dono:
            continue
        try:
            _tratar(e, msg, msg["chat"]["id"])
        except Exception as ex:  # noqa: BLE001
            print(f"Erro tratando mensagem {msg.get('message_id')}: {ex}")
    est.salvar(e)
    print(f"{len(novas)} atualização(ões) processada(s).")


if __name__ == "__main__":
    main()
