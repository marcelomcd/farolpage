# pages/request.py (nova página para exibir detalhes de uma Request)
import dash
from dash import html, dcc, callback, Input, Output, State
import dash_bootstrap_components as dbc
from dash.exceptions import PreventUpdate
from utils.api import get_work_item, get_revisions
from components.requests import render_request

dash.register_page(__name__, path="/request")

layout = html.Div([
    dcc.Location(id="url-location", refresh=False),
    dcc.Store(id="store-request-data"),
    dcc.Store(id="store-request-revisions"),

    html.Div(id="theme-wrapper-request", className="light-mode", children=[
        html.Div(id="alert-area-request"),

        dbc.Container([
            html.Div(id="request-conteudo"),
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
    Output("store-request-data", "data"),
    Output("store-request-revisions", "data"),
    Output("store-request-data", "data", allow_duplicate=True),
    Output("alert-area-request", "children"),
    Input("url-location", "pathname"),
    Input("url-location", "search"),
    State("store-user-session", "data"),
    prevent_initial_call=True
)
def carregar_dados_request(pathname, search, user):
    if pathname != "/request" or not search or "?id=" not in search:
        return None, None, None, dbc.Alert("❌ ID da Request não informado.", color="danger")

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
                return None, None, None, dbc.Alert("🔒 Acesso negado a esta request.", color="warning")

        rev_data = get_revisions(wi_id)
        return wi_data, rev_data, wi_data, ""

    except Exception as e:
        return None, None, None, dbc.Alert(f"❌ Erro ao carregar dados: {str(e)}", color="danger")

@callback(
    Output("request-conteudo", "children"),
    Input("store-request-data", "data"),
    Input("store-request-revisions", "data")
)
def exibir_detalhes(wi_data, rev_data):
    if not wi_data:
        raise PreventUpdate
    return html.Div([
        render_request(wi_data)
    ])

@callback(
    Output("theme-wrapper-request", "className"),
    Input("theme-store", "data"),
    allow_duplicate=True
)
def aplicar_tema_request(theme):
    return f"{theme}-mode"
