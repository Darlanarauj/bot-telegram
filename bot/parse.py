"""Entende a legenda que você manda junto com a foto no Telegram.

Exemplos aceitos:
    Fone Bluetooth TWS
    79,90
    https://s.shopee.com.br/abc123

    Fone Bluetooth TWS | R$ 79,90
    Fone Bluetooth R$ 79,90 https://s.shopee.com.br/abc123
"""
import re
from urllib.parse import urlparse

URL_RE = re.compile(r"https?://[^\s<>\"']+", re.I)
NUM = r"(\d(?:[\d.,]*\d)?)"
LINHA_PRECO_RE = re.compile(rf"^\s*(?:pre[cç]o\s*:?\s*)?(?:r\$\s*)?{NUM}\s*$", re.I)
RS_RE = re.compile(rf"r\$\s*{NUM}", re.I)
DOMINIOS_SHOPEE = ("shopee.com.br", "shopee.com", "shope.ee", "shp.ee")


def _para_float(txt):
    t = txt.strip()
    if "," in t and "." in t:
        t = t.replace(".", "").replace(",", ".")
    elif "," in t:
        t = t.replace(",", ".")
    elif "." in t and re.fullmatch(r"\d{1,3}(\.\d{3})+", t):
        t = t.replace(".", "")
    try:
        v = float(t)
    except ValueError:
        return None
    return v if 0 < v < 100000 else None


def formatar_preco(v):
    s = f"{v:,.2f}"  # 1,299.90
    return "R$ " + s.replace(",", "_").replace(".", ",").replace("_", ".")


def _tirar_preco(linhas):
    """Procura o preço nas linhas. Devolve (valor, linhas sem o preço)."""
    for i, l in enumerate(linhas):
        m = LINHA_PRECO_RE.match(l)
        if m:
            v = _para_float(m.group(1))
            if v:
                return v, linhas[:i] + linhas[i + 1:]
    for i, l in enumerate(linhas):
        if "|" in l:
            *resto, ultimo = [x.strip() for x in l.split("|")]
            m = LINHA_PRECO_RE.match(ultimo)
            if m and resto:
                v = _para_float(m.group(1))
                if v:
                    return v, linhas[:i] + [" | ".join(resto)] + linhas[i + 1:]
    for i, l in enumerate(linhas):
        m = RS_RE.search(l)
        if m:
            v = _para_float(m.group(1))
            if v:
                nova = " ".join((l[:m.start()] + " " + l[m.end():]).split()).strip(" -–—:|·,")
                return v, linhas[:i] + ([nova] if nova else []) + linhas[i + 1:]
    return None, linhas


def parse_legenda(texto):
    texto = texto or ""
    urls = [u.rstrip(".,;)") for u in URL_RE.findall(texto)]
    sem_urls = URL_RE.sub(" ", texto)
    linhas = [" ".join(l.split()) for l in sem_urls.splitlines()]
    linhas = [l for l in linhas if re.search(r"\w", l)]
    valor, linhas = _tirar_preco(linhas)
    linhas = [re.sub(r"^(nome|produto)\s*:\s*", "", l, flags=re.I) for l in linhas]
    nome = linhas[0][:90] if linhas else ""
    detalhes = " ".join(linhas[1:])[:300]
    return {
        "nome": nome,
        "preco": formatar_preco(valor) if valor else None,
        "detalhes": detalhes,
        "link": urls[0] if urls else None,
    }


def link_valido(url):
    try:
        host = (urlparse(url).hostname or "").lower()
    except ValueError:
        return False
    return any(host == d or host.endswith("." + d) for d in DOMINIOS_SHOPEE)
