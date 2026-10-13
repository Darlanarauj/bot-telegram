"""Escolhe os produtos do próximo post e atualiza a página da bio."""
import json

from . import cartoes, estado as est, site
from .config import CFG, SELECAO, SITE, modo_teste


def _limpar_antigos(e):
    postados = sorted(est.por_status(e, est.POSTADO), key=lambda p: p.get("postado_em", ""), reverse=True)
    for p in postados[CFG["manter_imagens"]:]:
        if p.get("imagens_removidas"):
            continue
        for pasta in ("fotos", "cards"):
            (SITE / pasta / f"{p['id']}.jpg").unlink(missing_ok=True)
        p["imagens_removidas"] = True


def main():
    e = est.carregar()
    n = max(1, min(int(CFG["produtos_por_post"]), 9))
    candidatos = est.por_status(e, est.AGENDADO) + est.por_status(e, est.PRONTO)
    escolhidos = candidatos[:n]
    if not modo_teste():
        for p in escolhidos:
            if p["status"] == est.PRONTO:
                p["status"] = est.AGENDADO
                p["agendado_em"] = est.agora()
    cartoes.salvar_jpg(cartoes.cartao_final(CFG["instagram"]), SITE / "cards" / "final.jpg")
    _limpar_antigos(e)
    qtd = site.gerar(e)
    SELECAO.write_text(json.dumps({"ids": [p["id"] for p in escolhidos]}, indent=2) + "\n", encoding="utf-8")
    est.salvar(e)
    print(f"Selecionados para o próximo post: {[p['id'] for p in escolhidos] or 'nenhum'}. Produtos na página: {qtd}.")


if __name__ == "__main__":
    main()
