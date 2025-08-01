from dash import html
import re
from datetime import datetime
from utils.helpers import clean_html, format_datetime


def render_comentarios(work_item, revisions):
    comentarios = _extrair_comentarios(revisions)

    if not comentarios:
        return html.P("Nenhum comentário encontrado.")

    cards = []
    for c in comentarios:
        cards.append(
            html.Div(
                [
                    html.H6(c["data_formatada"],
                            className="card-title text-primary fw-bold"),
                    html.Div(c["conteudo"],
                             className="card-text",
                             style={"whiteSpace": "pre-wrap"}),
                    html.Small(
                        [
                            html.Span("Responsável: "),
                            html.Span(c["responsavel"], className="responsavel"),
                        ],
                        className="fst-italic d-block mt-2",
                    ),
                ],
                className="comment",
            )
        )

    return html.Div(
        [
            html.H5("💬 Comentários (Histórico do Azure DevOps)",
                    className="mb-4 text-primary"),
            html.Div(cards),
        ]
    )

def _extrair_comentarios(revisions):
    """
    Constrói uma lista de dicionários:
        {
            "data":          "DD/MM/AAAA",
            "data_formatada":"DD/MM/AAAA",
            "conteudo":      str (com \n preservados),
            "responsavel":   str ("Quali IT", "Consigaz", …)
        }
    """
    comentarios = []

    def _normaliza_data(raw, ano_fallback="2025"):
        raw = raw.replace(".", "/").strip()
        d, m, *y = raw.split("/")
        d = d.zfill(2)
        m = m.zfill(2)
        y = y[0] if y else ano_fallback
        if len(y) == 2:
            y = f"20{y}"
        return f"{d}/{m}/{y}"

    def _detect_resp(texto):
        t = texto.strip().lower()
        if t in {"quali it / consigaz", "consigaz / quali it"}:
            return "Quali IT / Consigaz"
        if t == "quali it":
            return "Quali IT"
        if t == "consigaz":
            return "Consigaz"
        return "Quali IT"

    for rev in revisions:
        bruto = rev.get("fields", {}).get("System.History")
        if not bruto:
            continue

        texto = clean_html(bruto).strip()
        ano_fallback = format_datetime(
            rev.get("fields", {}).get("System.ChangedDate")
        ).split("/")[-1] or "2025"
        bloco_re = re.compile(
            r"(?:^|\n)(\d{1,2}[./]\d{1,2}(?:[./]\d{2,4})?)\s*(.*?)"
            r"(?=\n\d{1,2}[./]\d{1,2}(?:[./]\d{2,4})?|\Z)",
            re.S,
        )

        for data_raw, corpo in bloco_re.findall(texto):
            data = _normaliza_data(data_raw, ano_fallback)
            linhas = [l.rstrip() for l in corpo.splitlines()]

            while linhas and not linhas[0]:
                linhas.pop(0)
            while linhas and not linhas[-1]:
                linhas.pop()

            if not linhas:
                continue

            responsavel = _detect_resp(linhas[-1])
            if responsavel != "Quali IT":
                linhas = linhas[:-1]

            conteudo = "\n".join(linhas).strip()

            comentarios.append(
                {
                    "data": data,
                    "data_formatada": data,
                    "conteudo": conteudo,
                    "responsavel": responsavel,
                }
            )

    vistos = set()
    resultado = []
    for c in comentarios:
        chave = (c["data"], c["conteudo"], c["responsavel"])
        if chave not in vistos:
            vistos.add(chave)
            resultado.append(c)

    resultado.sort(
        key=lambda x: datetime.strptime(x["data"], "%d/%m/%Y"),
        reverse=True,
    )
    return resultado
