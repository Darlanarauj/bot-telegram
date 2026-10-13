"""Gera as imagens do carrossel (1080x1350, formato 4:5 do Instagram)."""
import io

from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageFont, ImageOps

W, H = 1080, 1350
FOTO_H = 900
COR_FUNDO = (20, 20, 24)
COR_DESTAQUE = (255, 106, 43)

_FONTES = [
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
    "/usr/share/fonts/truetype/freefont/FreeSansBold.ttf",
    "C:\\Windows\\Fonts\\arialbd.ttf",
    "/System/Library/Fonts/Supplemental/Arial Bold.ttf",
]


def fonte(tam):
    for caminho in _FONTES:
        try:
            return ImageFont.truetype(caminho, tam)
        except OSError:
            continue
    return ImageFont.load_default(size=tam)


def abrir_foto(dados):
    img = Image.open(io.BytesIO(dados))
    img = ImageOps.exif_transpose(img).convert("RGB")
    img.thumbnail((1600, 1600), Image.LANCZOS)
    return img


def salvar_jpg(img, caminho):
    caminho.parent.mkdir(parents=True, exist_ok=True)
    img.save(caminho, "JPEG", quality=88, optimize=True)


def _quebrar(draw, texto, fnt, largura, max_linhas):
    linhas, atual = [], ""
    for palavra in texto.split():
        teste = f"{atual} {palavra}".strip()
        if draw.textlength(teste, font=fnt) <= largura:
            atual = teste
        else:
            if atual:
                linhas.append(atual)
            atual = palavra
    if atual:
        linhas.append(atual)
    if len(linhas) > max_linhas:
        linhas = linhas[:max_linhas]
        ultima = linhas[-1]
        while ultima and draw.textlength(ultima + "…", font=fnt) > largura:
            ultima = ultima[:-1]
        linhas[-1] = ultima.rstrip() + "…"
    return linhas


def cartao_produto(foto, nome, preco):
    img = Image.new("RGB", (W, H), COR_FUNDO)
    fundo = ImageOps.fit(foto, (W, FOTO_H), Image.LANCZOS).filter(ImageFilter.GaussianBlur(28))
    img.paste(ImageEnhance.Brightness(fundo).enhance(0.55), (0, 0))
    m = 40
    frente = ImageOps.contain(foto, (W - 2 * m, FOTO_H - 2 * m), Image.LANCZOS)
    img.paste(frente, ((W - frente.width) // 2, (FOTO_H - frente.height) // 2))

    d = ImageDraw.Draw(img)
    fn = fonte(54)
    y = FOTO_H + 40
    for linha in _quebrar(d, nome, fn, W - 120, 2):
        d.text((60, y), linha, font=fn, fill="white")
        y += 66
    if preco:
        d.text((60, 1085), preco, font=fonte(104), fill=COR_DESTAQUE)
    texto, fp = "LINK NA BIO", fonte(34)
    w = d.textlength(texto, font=fp)
    x0, y0 = 60, 1245
    d.rounded_rectangle((x0, y0, x0 + w + 60, y0 + 70), radius=35, fill=COR_DESTAQUE)
    d.text((x0 + 30, y0 + 35), texto, font=fp, fill="white", anchor="lm")
    return img


def cartao_final(instagram=""):
    img = Image.new("RGB", (W, H))
    d = ImageDraw.Draw(img)
    topo, base = (255, 106, 43), (190, 40, 70)
    for y in range(H):
        t = y / (H - 1)
        d.line([(0, y), (W, y)], fill=tuple(int(topo[i] + (base[i] - topo[i]) * t) for i in range(3)))
    d.text((W / 2, 470), "Gostou?", font=fonte(130), fill="white", anchor="mm")
    d.text((W / 2, 650), "Link na bio", font=fonte(104), fill="white", anchor="mm")
    d.text((W / 2, 780), "e escolha seu achadinho", font=fonte(52), fill="white", anchor="mm")
    if instagram:
        d.text((W / 2, 1000), "@" + instagram.lstrip("@"), font=fonte(48), fill="white", anchor="mm")
    d.text((W / 2, 1260), "Publi  |  link de afiliado", font=fonte(32), fill=(255, 235, 225), anchor="mm")
    return img
