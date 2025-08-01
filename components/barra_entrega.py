from dash import html
from components.utils import get_progress_color

def build_barra_entrega(percent_entrega: int):
    cor = get_progress_color(percent_entrega)

    return html.Div(
        style={"position": "relative", "height": "30px", "margin": "0px"},

        children=[
            html.Div(
                style={
                    "width": f"{percent_entrega}%",
                    "backgroundColor": cor,
                    "height": "100%",
                    "borderRadius": "0px",
                    "transition": "width 0.4s ease-in-out, background-color 0.4s ease-in-out"
                },
                className="progress-indicator"
            ),

            html.Div(
                f"{percent_entrega}% concluído",
                style={
                    "position": "absolute",
                    "top": "50%",
                    "left": "50%",
                    "transform": "translate(-50%, -50%)",
                    "fontWeight": "normal",
                    "fontSize": "18px",
                    "color": "var(--barra-entrega-texto, #000)",
                    "textShadow": "6px 6px 6px rgba(0,0,0,0.5)"
                }
            )
        ]
    )