# details.py (100% funcional com login persistente via storage local)
import dash
from dash import html, dcc, callback, Input, Output, State
import dash_bootstrap_components as dbc
from dash.exceptions import PreventUpdate
from utils.api import get_work_item, get_revisions
from components.resultado import render_resultado
from components.comentarios import render_comentarios
from components.barra_entrega import build_barra_entrega

dash.register_page(__name__, path="/feature")

layout = html.Div([
    dcc.Location(id="url-location", refresh=False),

    html.Div(id="theme-wrapper-feature", className="light-mode", children=[
        html.Div(id="alert-area-feature"),
        html.Div(id="barra-entrega-dinamica"),
        dbc.Container([
            html.Div(id="feature-conteudo"),
            html.Div([
                html.Button(
                    "📄 Imprimir Página Completa",
                    id="btn-print-page",
                    className="btn btn-primary",
                    n_clicks=0
                ),
            ], style={"marginTop": "30px", "textAlign": "center"})
        ], fluid=True)
    ])
])

@callback(
    Output("store-workitem-data-global", "data"),
    Output("store-revisions-data", "data"),
    Output("store-workitem-data-global", "data", allow_duplicate=True),
    Output("alert-area-feature", "children"),
    Input("url-location", "pathname"),
    Input("url-location", "search"),
    State("store-user-session", "data"),
    prevent_initial_call=True
)
def carregar_dados_feature(pathname, search, user):
    if pathname != "/feature" or not search or "?id=" not in search:
        return None, None, None, dbc.Alert("❌ ID da Feature não informado.", color="danger")

    if not user or not user.get("email"):
        raise PreventUpdate

    wi_id = search.split("?id=")[-1]
    if not wi_id.isdigit():
        return None, None, None, dbc.Alert("❌ ID inválido.", color="danger")

    try:
        wi_data = get_work_item(wi_id)
        if not wi_data:
            return None, None, None, dbc.Alert("❌ Work Item não encontrado.", color="danger")

        area_path = wi_data.get("fields", {}).get("System.AreaPath", "")
        email = user["email"].lower()

        if not email.endswith("@qualiit.com.br"):
            cliente = email.split("@")[1].split(".")[0].upper()
            if cliente not in area_path.upper():
                return None, None, None, dbc.Alert("🔒 Acesso negado a esta feature.", color="warning")

        rev_data = get_revisions(wi_id)
        return wi_data, rev_data, wi_data, ""

    except Exception as e:
        return None, None, None, dbc.Alert(f"❌ Erro ao carregar dados: {str(e)}", color="danger")


@callback(
    Output("feature-conteudo", "children"),
    Input("store-workitem-data-global", "data"),
    Input("store-revisions-data", "data")
)
def exibir_detalhes(wi_data, rev_data):
    if not wi_data:
        raise PreventUpdate
    return html.Div([
        render_resultado(wi_data),
        html.Hr(),
        render_comentarios(wi_data, rev_data)
    ])


@callback(
    Output("barra-entrega-dinamica", "children"),
    Input("store-workitem-data-global", "data"),
)
def mostrar_barra_entrega(wi_data):
    if not wi_data:
        raise PreventUpdate
    percent_raw = wi_data["fields"].get("Custom.PorcentagemEntrega", "0")
    percent = int(str(percent_raw).replace("%", "").strip())
    return build_barra_entrega(percent)


@callback(
    Output("theme-wrapper-feature", "className"),
    Input("theme-store", "data"),
    allow_duplicate=True
)
def aplicar_tema_feature(theme):
    return f"{theme}-mode"
