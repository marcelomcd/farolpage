# pages/requestsConcluidas.py
from dash import html, dcc, dash_table, callback, Output, Input, State
import dash_bootstrap_components as dbc
import dash
from dash.exceptions import PreventUpdate
from utils.api import get_all_requests
from utils.helpers import limpar_valor

dash.register_page(__name__, path="/requests-concluidas", name="Requests Concluídas")

layout = dbc.Container([
    dcc.Location(id="redirect-request-concluida", refresh=True),
    dcc.Store(id="store-user-session", storage_type="local"),

    html.H2("✅ Requests Concluídas", className="my-4 text-center"),

    dbc.Row([
        dbc.Col(
            dcc.Input(
                id="input-busca-requests-concluidas",
                type="text",
                placeholder="🔍 Pesquisar por Número, Título, Cliente ou PMO...",
                debounce=True,
                className="form-control mb-3",
            ), width=12
        )
    ]),

    dbc.Card([
        dbc.CardHeader("Requests Concluídas"),
        dbc.CardBody([
            dash_table.DataTable(
                id="tabela-requests-concluidas",
                columns=[
                    {"name": "Número de Proposta", "id": "Número de Proposta"},
                    {"name": "ID", "id": "ID"},
                    {"name": "Título", "id": "Título"},
                    {"name": "Cliente", "id": "Cliente"},
                    {"name": "PMO", "id": "PMO"},
                ],
                data=[],
                style_table={"maxHeight": "700px", "overflowY": "auto"},
                style_cell={"textAlign": "center", "verticalAlign": "middle", "padding": "8px", "fontSize": "12px"},
                style_header={"backgroundColor": "#f8f9fa", "fontWeight": "bold"},
                sort_action="none"
            )
        ])
    ], className="shadow")
], fluid=True)

@callback(
    Output("tabela-requests-concluidas", "data"),
    Input("store-user-session", "data"),
    Input("input-busca-requests-concluidas", "value")
)
def carregar_requests_concluidas(user, termo):
    if not user or "email" not in user:
        raise PreventUpdate

    email = user["email"].lower()
    resultado = []

    for wi in get_all_requests():
        fields = wi.get("fields", {})
        estado = limpar_valor(fields.get("System.State"), "")
        if estado not in ["Closed", "Em Garantia"]:
            continue

        cliente = limpar_valor(fields.get("Custom.RequestClienteNome"), "Sem Cliente")

        resultado.append({
            "Número de Proposta": limpar_valor(fields.get("Custom.NumeroProposta"), "Sem Número"),
            "ID": wi["id"],
            "Título": limpar_valor(fields.get("System.Title"), "Sem Título"),
            "Cliente": cliente,
            "PMO": fields.get("System.AssignedTo", {}).get("displayName", "Não atribuído")
        })

    if termo:
        termo = termo.lower()
        resultado = [
            r for r in resultado if
            termo in str(r["Número de Proposta"]).lower()
            or termo in str(r["ID"]).lower()
            or termo in str(r["Título"]).lower()
            or termo in str(r["Cliente"]).lower()
            or termo in str(r["PMO"]).lower()
        ]

    return resultado

@callback(
    Output("redirect-request-concluida", "href"),
    Input("tabela-requests-concluidas", "active_cell"),
    State("tabela-requests-concluidas", "data"),
    prevent_initial_call=True
)
def abrir_request_concluida(active_cell, data_table):
    if not active_cell or not data_table:
        return dash.no_update

    row_index = active_cell.get("row")
    if row_index is None or row_index >= len(data_table):
        return dash.no_update

    request_id = data_table[row_index]["ID"]
    return f"/request?id={request_id}"
