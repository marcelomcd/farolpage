from dash import Dash, dcc, html, Input, Output, State, page_container, ctx, ClientsideFunction
import dash_bootstrap_components as dbc
from components.navbar import navbar_padrao, build_navbar
from cache_config import cache
import pandas as pd
from utils.helpers import FAROIS_CARDS_COLORS, get_card_class_farol
from dash.exceptions import PreventUpdate

app = Dash(
    __name__,
    use_pages=True,
    suppress_callback_exceptions=True,
    external_stylesheets=[dbc.themes.BOOTSTRAP],
)
app.title = "Farol Operacional"

cache.init_app(app.server, config={
    "CACHE_TYPE": "SimpleCache",
    "CACHE_DEFAULT_TIMEOUT": 600
})

app.layout = html.Div(id="body-wrapper", children=[
    html.Div(id="alert-area-feature", style={"display": "none"}),
    dcc.Store(id="store-user-session", storage_type="local"),
    dcc.Store(id="store-workitem-data-global", data=None),
    dcc.Store(id="store-revisions-data", data=None),

    html.Div(style={"minHeight": "100vh", "backgroundColor": "inherit"}, children=[
        html.Div(id="navbar-dinamica", children=navbar_padrao),
        html.Div(id="wrap-cards-farol"),


        html.Div(id="div-pagina-completa", children=[
            dcc.Loading(
                id="loading-page-container",
                type="circle",
                fullscreen=False,
                children=page_container
            )
        ])
    ])
])

@app.callback(
    Output("navbar-dinamica", "children"),
    Input("store-workitem-data-global", "data"),
    Input("store-user-session", "data"),
    Input("_pages_location", "pathname"),
)
def atualizar_navbar_global(wi_data, user_data, pathname):
    if pathname == "/":
        return None
    if pathname == "/feature" and wi_data:
        status = wi_data["fields"].get("Custom.StatusProjeto", "")
        return build_navbar(status, user_data)
    return build_navbar(None, user_data)


@app.callback(
    Output("cards-farol-app", "children"),
    Input("store-features-ativas", "data"),
    Input("dropdown-clientes", "value"),
    prevent_initial_call=True
)

def exibir_cards_farol_na_home(data, cliente):
    if not data:
        raise PreventUpdate

    df = pd.DataFrame(data)
    if "FarolTexto" not in df.columns:
        raise PreventUpdate

    if cliente:
        df = df[df["Cliente"] == cliente]

    cards = []
    farol_counts = df["FarolTexto"].value_counts()

    for farol, count in farol_counts.items():
        cor = FAROIS_CARDS_COLORS.get(farol, "#999")
        cor_texto = "#fff" if farol.lower() != "sem problema" else "#000"
        cards.append(
            html.Div(
                str(count),
                id={"type": "filtro-card", "campo": "FarolTexto", "valor": farol},
                className=f"fade-in {get_card_class_farol(farol)}",
                style={
                    "cursor": "pointer"
                }
            )
        )

    return html.Div(
        cards,
        className="d-flex justify-content-center align-items-center flex-wrap",
        style={"gap": "24px"}
    )

@app.callback(
    Output("wrap-cards-farol", "children"),
    Input("_pages_location", "pathname")
)
def renderizar_cards_se_necessario(pathname):
    if pathname == "/farol":
        return dbc.Row([
            dbc.Col(
                html.Div(
                    id="cards-farol-app",
                    className="d-flex justify-content-center flex-wrap",
                    style={"gap": "24px"}
                ),
                width=12,
                className="d-flex justify-content-center align-items-center position-relative"
            )
        ], className="px-4 pt-4")
    return None

app.clientside_callback(
    """
    function(n_clicks) {
        if (n_clicks > 0) {
            window.print();
        }
        return '';
    }
    """,
    Output("btn-print-page", "title"),
    Input("btn-print-page", "n_clicks"),
    prevent_initial_call=True
)

app.clientside_callback(
    ClientsideFunction("clientside", "abrirNovaAba"),
    Output("dummy-output", "children"),
    Input("tabela-modal-detalhada", "active_cell"),
    State("tabela-modal-detalhada", "data"),
    prevent_initial_call=True
)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8050, debug=False)

__all__ = ["app", "cache"]

server = app.server