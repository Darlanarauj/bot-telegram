"""Lê e grava o estado (fila de produtos) em data/estado.json."""
import json
from datetime import datetime, timezone

from .config import DATA, ESTADO

AGUARDANDO_LINK = "aguardando_link"
PRONTO = "pronto"
AGENDADO = "agendado"
POSTADO = "postado"
ERRO = "erro"
CANCELADO = "cancelado"


def agora():
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def carregar():
    e = json.loads(ESTADO.read_text(encoding="utf-8")) if ESTADO.exists() else {}
    e.setdefault("update_offset", 0)
    e.setdefault("proximo_id", 1)
    e.setdefault("produtos", [])
    return e


def salvar(e):
    DATA.mkdir(parents=True, exist_ok=True)
    ESTADO.write_text(json.dumps(e, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def novo_produto(e, **campos):
    p = {"id": f"p{e['proximo_id']:04d}", "criado_em": agora(), "tentativas": 0, "msg_ids": []}
    e["proximo_id"] += 1
    p.update(campos)
    e["produtos"].append(p)
    return p


def achar_por_msg(e, message_id):
    for p in e["produtos"]:
        if message_id in p["msg_ids"]:
            return p
    return None


def por_status(e, *status):
    return [p for p in e["produtos"] if p["status"] in status]
