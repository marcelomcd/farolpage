# pages/projetosAtivos.py
from dash import html, dcc, dash_table, callback, Output, Input, State
import dash_bootstrap_components as dbc
import dash
from dash.exceptions import PreventUpdate
from flask import request
import re
from utils.api import get_all_features_by_cliente
from utils.helpers import limpar_valor
from cache_config import cache

dash.register_page(__name__, path="/projetos-ativos", name="Projetos Ativos")

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

def carregar_dados_cacheados(cliente_email, force_refresh=False):
    cache_key = f"projetos_ativos_{cliente_email or 'all'}"
    if not force_refresh:
        dados_em_cache = cache.get(cache_key)
        if dados_em_cache:
            return dados_em_cache

        print("🔄 Requisição direta: ignorando cache")
    else:
        dados_em_cache = cache.get(cache_key)
        if dados_em_cache:
            return dados_em_cache

    features = get_all_features_by_cliente(cliente_email)
    features_ativas = []

    for item in features:
        fields = item.get("fields", {})
        status = limpar_valor(fields.get("System.State"), "")
        area_path = fields.get("System.AreaPath", "")
        iteration_path = fields.get("System.IterationPath", "")
        cliente_nome = extrair_nome_cliente(area_path, iteration_path)

        if cliente_email and cliente_email.upper() not in area_path.upper():
            continue


        if status not in ["Closed", "Em Garantia"]:
            registro = {
                "Cliente": cliente_nome,
                "Número de Proposta": limpar_valor(fields.get("Custom.NumeroProposta"), "Sem Definição de Número de Proposta"),
                "ID": item["id"],
                "Título": limpar_valor(fields.get("System.Title"), "Sem Definição de Título"),
                "Responsável": limpar_valor(fields.get("Custom.ResponsavelCliente"), "Sem Definição de Responsável"),
                "PMO": fields.get("System.AssignedTo", {}).get("displayName", "Não atribuído")
            }
            features_ativas.append(registro)

    features_ativas = sorted(features_ativas, key=lambda x: x["Cliente"])
    cache.set(cache_key, features_ativas, timeout=600)
    return features_ativas

layout = dbc.Container([
    dcc.Location(id="redirect", refresh=True),
    dcc.Store(id="store-user-session", storage_type="local"),
    dcc.Store(id="store-refresh-session", storage_type="session"),


    html.H2("📈 Painel Operacional - Projetos Ativos", className="my-4 text-center"),

    dbc.Row([
        dbc.Col(
            dcc.Input(
                id="input-busca-ativos",
                type="text",
                placeholder="🔍 Pesquisar projeto por Cliente, Número, Título, Responsável ou PMO...",
                debounce=True,
                className="form-control mb-3",
            ), width=12
        )
    ]),

    dbc.Card([
        dbc.CardHeader("Projetos Ativos"),
        dbc.CardBody([
            dash_table.DataTable(
                id="tabela-consigaz-filtrada",
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
    Output("tabela-consigaz-filtrada", "data"),
    Output("store-refresh-session", "data"),
    Input("store-user-session", "data"),
    Input("input-busca-ativos", "value"),
    State("store-refresh-session", "data")
)
def carregar_e_filtrar_dados(user, termo, already_loaded):
    if not user or "email" not in user:
        raise PreventUpdate

    email = user["email"].lower()
    cliente_email = email.split("@")[1].split(".")[0] if not email.endswith("@qualiit.com.br") else None
    force_refresh = not already_loaded
    features_ativas = carregar_dados_cacheados(cliente_email, force_refresh=force_refresh)

    if termo:
        termo = termo.lower()
        features_ativas = [
            item for item in features_ativas
            if termo in str(item["Cliente"]).lower()
            or termo in str(item["Número de Proposta"]).lower()
            or termo in str(item["ID"]).lower()
            or termo in str(item["Título"]).lower()
            or termo in str(item["Responsável"]).lower()
            or termo in str(item["PMO"]).lower()
        ]

    return features_ativas, True

@callback(
    Output("redirect", "href"),
    Input("tabela-consigaz-filtrada", "active_cell"),
    State("tabela-consigaz-filtrada", "data"),
    prevent_initial_call=True
)
def abrir_feature_ativa(active_cell, data_table):
    if not active_cell or not data_table:
        return dash.no_update

    row_index = active_cell.get("row")
    if row_index is None or row_index >= len(data_table):
        return dash.no_update

    feature_id = data_table[row_index]["ID"]
    return f"/feature?id={feature_id}"
