# tests/login_simulado.py
import dash
from dash import html, dcc, callback, Output, Input, State, register_page

register_page(__name__, path="/login_simulado")

layout = html.Div([
    html.H3("Simulador de Login", className="mb-4"),
    
    dcc.Input(id="input-nome", type="text", placeholder="Nome completo", style={"marginRight": "10px"}),
    dcc.Input(id="input-email", type="email", placeholder="Email (ex: teste@cliente.com)", style={"marginRight": "10px"}),

    html.Button("Simular Login", id="btn-simular", n_clicks=0, className="btn btn-primary mt-2"),
    
    html.Div(id="simulador-status", className="mt-3", style={"fontWeight": "bold", "color": "green"}),

    dcc.Store(id="store-user-session", storage_type="local")
])

@callback(
    Output("store-user-session", "data", allow_duplicate=True),
    Output("simulador-status", "children"),
    Input("btn-simular", "n_clicks"),
    State("input-nome", "value"),
    State("input-email", "value"),
    prevent_initial_call=True
)
def simular_login(n, nome, email):
    if not nome or not email:
        return dash.no_update, "Preencha todos os campos."

    user_data = {
        "nome": nome,
        "email": email
    }
    return user_data, f"Login simulado como: {nome} ({email})"

