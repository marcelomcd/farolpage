# pages/projetosConcluidos.py
from dash import html, dcc, dash_table, callback, Output, Input, State
import dash_bootstrap_components as dbc
import dash
import re
from dash.exceptions import PreventUpdate
from utils.api import get_all_features_by_cliente
from utils.helpers import limpar_valor
from cache_config import cache

dash.register_page(__name__, path="/projetos-concluidos", name="Projetos Concluídos")

def extrair_nome_cliente(area_path, iteration_path):
    import re

    def limpar_nome(nome):
        nome = re.sub(r"\bcliente\b", "", nome, flags=re.IGNORECASE)
        nome = re.sub(r"[^a-zA-Z0-9 ]+", "", nome).strip()
        if not nome:
            return ""
        if "qualiit" in nome.replace(" ", "").lower():
            return "Quali IT"
        return nome.title()

    def processar_caminho(caminho, prioridade_cliente=False):
        if not caminho:
            return ""
        segmentos = re.split(r"[\\/]+", caminho.strip())

        if prioridade_cliente:
            for i, segmento in enumerate(segmentos):
                if "cliente" in segmento.lower():
                    partes = re.split(r"\bcliente\b", segmento, flags=re.IGNORECASE)
                    if len(partes) > 1:
                        nome = " ".join(partes[1:]).strip()
                        nome_limpo = limpar_nome(nome)
                        if nome_limpo:
                            return nome_limpo
                    if i + 1 < len(segmentos):
                        nome_limpo = limpar_nome(segmentos[i + 1])
                        if nome_limpo:
                            return nome_limpo
            return ""

        return limpar_nome(segmentos[-1]) if segmentos else ""

    nome = processar_caminho(area_path, prioridade_cliente=True)
    if nome:
        return nome

    if iteration_path and "quali it" in iteration_path.lower():
        nome = processar_caminho(iteration_path)
        if nome:
            return nome

    return "Sem Cliente"

layout = dbc.Container([
    dcc.Location(id="redirect-concluidas", refresh=True),
    dcc.Store(id="store-user-session", storage_type="local"),

    html.H2("✅ Projetos Concluídos", className="my-4 text-center"),

    dbc.Row([
        dbc.Col(
            dcc.Input(
                id="input-busca-concluidos",
                type="text",
                placeholder="🔍 Pesquisar projeto por Cliente, Número, Título, Responsável ou PMO...",
                debounce=True,
                className="form-control mb-3",
            ), width=12
        )
    ]),

    dbc.Card([
        dbc.CardHeader("Projetos Concluídos"),
        dbc.CardBody([
            dash_table.DataTable(
                id="tabela-projetos-concluidos",
                columns=[
                    {"name": "Cliente", "id": "Cliente"},
                    {"name": "Número de Proposta", "id": "Número de Proposta"},
                    {"name": "ID", "id": "ID"},
                    {"name": "Título", "id": "Título"},
                    {"name": "Responsável", "id": "Responsável"},
                    {"name": "PMO", "id": "PMO"},
                ],
                data=[],
                style_table={"maxHeight": "700px", "overflowY": "auto"},
                style_cell={"textAlign": "center", "verticalAlign": "middle", "padding": "8px", "cursor": "pointer", "fontSize": "12px"},
                style_header={"backgroundColor": "#f8f9fa", "fontWeight": "bold", "textAlign": "center"},
                sort_action="none"
            )
        ])
    ], className="shadow")
], fluid=True)

@callback(
    Output("tabela-projetos-concluidos", "data"),
    Input("store-user-session", "data"),
    Input("input-busca-concluidos", "value")
)
def carregar_e_filtrar_concluidos(user, termo):
    if not user or "email" not in user:
        raise PreventUpdate

    email = user["email"].lower()
    cliente_email = email.split("@")[1].split(".")[0] if not email.endswith("@qualiit.com.br") else None

    cache_key = f"projetos_concluidos_{cliente_email or 'all'}"
    cached_data = cache.get(cache_key)

    if cached_data:
        features_concluidas = cached_data
    else:
        features_concluidas = []
        features = get_all_features_by_cliente(cliente_email)
        for item in features:
            fields = item.get("fields", {})
            status = limpar_valor(fields.get("System.State"), "")
            area_path = fields.get("System.AreaPath", "")
            iteration_path = fields.get("System.IterationPath", "")

            if cliente_email and cliente_email not in area_path:
                continue

            if status in ["Closed", "Em Garantia"]:
                registro = {
                    "Cliente": extrair_nome_cliente(area_path, iteration_path),
                    "Número de Proposta": limpar_valor(fields.get("Custom.NumeroProposta"), "Sem Definição de Número de Proposta"),
                    "ID": item["id"],
                    "Título": limpar_valor(fields.get("System.Title"), "Sem Título"),
                    "Responsável": limpar_valor(fields.get("Custom.ResponsavelCliente"), "Sem Responsável"),
                    "PMO": fields.get("System.AssignedTo", {}).get("displayName", "Não atribuído")
                }
                features_concluidas.append(registro)

        features_concluidas = sorted(features_concluidas, key=lambda x: x["Cliente"])
        cache.set(cache_key, features_concluidas, timeout=600)

    if termo:
        termo = termo.lower()
        features_concluidas = [
            item for item in features_concluidas
            if termo in str(item["Cliente"]).lower()
            or termo in str(item["Número de Proposta"]).lower()
            or termo in str(item["ID"]).lower()
            or termo in str(item["Título"]).lower()
            or termo in str(item["Responsável"]).lower()
            or termo in str(item["PMO"]).lower()
        ]

    return features_concluidas

@callback(
    Output("redirect-concluidas", "href"),
    Input("tabela-projetos-concluidos", "active_cell"),
    State("tabela-projetos-concluidos", "data"),
    prevent_initial_call=True
)
def abrir_feature_concluida(active_cell, data_table):
    if not active_cell or not data_table:
        return dash.no_update

    row = active_cell["row"]
    feature_id = data_table[row]["ID"]
    return f"/feature?id={feature_id}"
