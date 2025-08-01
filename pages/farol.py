# pages/farol.py
import dash
import pandas as pd
import plotly.express as px
import dash_bootstrap_components as dbc
from dash import ctx, dcc, html, dash_table, callback, Output, Input, State, MATCH, ALL, ClientsideFunction, no_update
from utils.api import get_all_features_by_cliente, get_revisions
from utils.helpers import limpar_valor, normalize_value, normalizar_status, STATUS_CARDS_COLORS, get_card_class, DOMINIO_PARA_CLIENTE
from components.comentarios import _extrair_comentarios
from dash.exceptions import PreventUpdate
from cache_config import cache
import io
from openpyxl import Workbook
from openpyxl.styles import Alignment, Font, PatternFill
from openpyxl.utils.dataframe import dataframe_to_rows
from datetime import datetime
from utils.excel_export import gerar_excel_status_report

dash.register_page(__name__, path="/farol", name="Farol")

def interpretar_farol(status):
    status = limpar_valor(status, "").lower()
    if "sem problema" in status:
        return "Sem Problema"
    elif "com problema" in status:
        return "Com Problema"
    elif "problema crítico" in status:
        return "Problema Crítico"
    return "Indefinido"

def gerar_icone_farol(status):
    status = limpar_valor(status, "").lower()
    if "sem problema" in status:
        return "🟢"
    elif "com problema" in status:
        return "🟡"
    elif "problema crítico" in status:
        return "🔴"
    return "⚪"

def extrair_ultimo_comentario(item_id):
    revisions = get_revisions(item_id)
    comentarios = _extrair_comentarios(revisions)
    if not comentarios:
        return ""
    c = comentarios[0]
    return f"{c['data']}\n{c['conteudo']}\n{c['responsavel']}"

def extrair_nome_cliente(area_path, iteration_path):
    def buscar_nome(path):
        if not path:
            return None
        partes = path.split("\\")
        if partes:
            return partes[-1].strip().capitalize()
        return None

    cliente_area = buscar_nome(area_path)
    cliente_iter = buscar_nome(iteration_path)

    if cliente_area and cliente_area.lower() != "qualit":
        return cliente_area
    if cliente_iter and cliente_iter.lower() != "qualit":
        return cliente_iter
    return "Cliente"

def gerar_dados_features(usuario, force_refresh=False):
    cliente_email = usuario.lower().split("@")[1] if usuario else "publico"
    cache_key = f"farol_features_{cliente_email}"

    if not force_refresh:
        dados_cacheados = cache.get(cache_key)
        if dados_cacheados:
            return pd.DataFrame(dados_cacheados)

    dominio_para_cliente = DOMINIO_PARA_CLIENTE

    is_admin = usuario.endswith("@qualiit.com.br")
    dominio = usuario.split("@")[1].lower()
    cliente = None if is_admin else dominio_para_cliente.get(dominio)

    todas_features = get_all_features_by_cliente(
        cliente=cliente,
        force_admin=is_admin
    )

    features_filtradas = []

    for item in todas_features:
        fields = item.get("fields", {})
        status = normalizar_status(fields.get("System.State"))
        area_path = fields.get("System.AreaPath", "").lower()

        if not is_admin:
            if not cliente or cliente.lower() not in area_path:
                continue

        if status not in ["Closed", "Em Garantia"]:
            proposta = fields.get("Custom.NumeroProposta") or next((v for k, v in fields.items() if "proposta" in k.lower()), "")
            horas = fields.get("Custom.HorasVendidas")
            horas = int(horas) if isinstance(horas, (int, float)) else 0
            features_filtradas.append({
                "NumeroProposta": limpar_valor(proposta),
                "Horas": str(horas),
                "Projeto": limpar_valor(fields.get("System.Title"), ""),
                "%": limpar_valor(fields.get("Custom.PorcentagemEntrega"), ""),
                "FarolTexto": interpretar_farol(fields.get("Custom.StatusProjeto")),
                "FarolIcone": gerar_icone_farol(fields.get("Custom.StatusProjeto")),
                "Situação": extrair_ultimo_comentario(item["id"]),
                "Status": status,
                "Responsavel": limpar_valor(fields.get("Custom.ResponsavelCliente"), ""),
                "PMO": fields.get("System.AssignedTo", {}).get("displayName", "Não atribuído"),
                "DataInicio": normalize_value("Data de Início", fields.get("Microsoft.VSTS.Scheduling.StartDate")),
                "DataFimOriginal": normalize_value("Data Fim Original", fields.get("Custom.DataInicialEntregaProjeto")),
                "DataHomologacao": normalize_value("Data liberada homologação", fields.get("Custom.DataLiberadaHomologacao")),
                "DataFim": normalize_value("Data Fim", fields.get("Microsoft.VSTS.Scheduling.TargetDate")),
                "KeyUser": limpar_valor(fields.get("Custom.KeyUserCliente"), ""),
                "Aprovador": limpar_valor(fields.get("Custom.AprovadorProjetoCliente"), ""),
                "Cliente": extrair_nome_cliente(fields.get("System.AreaPath"), fields.get("System.IterationPath")),
                "ID": item.get("id")
            })

    df = pd.DataFrame(features_filtradas)
    cache.set(cache_key, df.to_dict("records"), timeout=600)
    return df

def gerar_cards(df, campo, cor_dict):
    cards = []
    valores = df[campo].value_counts()
    for valor, count in valores.items():
        cor = cor_dict.get(valor, "#ccc")
        cor_classe = valor.lower().replace(" ", "-")
        borda_classe = f"card-borda-{cor_classe}"

        estilo = {
            "minWidth": "120px",
            "backgroundColor": cor,
            "color": "#fff",
            "cursor": "pointer"
        }

        cards.append(
            html.Div([
                html.Div([
                    html.Small(valor, className="d-block fw-bold"),
                    html.H5(str(count), className="fw-bold mb-0")
                ],
                id={"type": "filtro-card", "campo": campo, "valor": valor},
                className=get_card_class(valor),
                style=estilo)
            ], className="m-1")
        )
    return html.Div(cards, className="d-flex justify-content-center flex-wrap mb-3")

@callback(
    Output("store-features-ativas", "data"),
    Output("dropdown-clientes", "options"),
    Output("store-cliente-selecionado", "data"),
    Output("store-refresh-farol", "data"),  # novo
    Input("store-user-session", "data"),
    State("store-refresh-farol", "data"),
    prevent_initial_call=True
)
def atualizar_dados(user, already_loaded):
    if not user:
        raise PreventUpdate
    email = user.get("email")
    force_refresh = not already_loaded
    df = gerar_dados_features(email, force_refresh=force_refresh)
    opcoes_clientes = sorted(df["Cliente"].dropna().unique())
    return df.to_dict("records"), [{"label": c, "value": c} for c in opcoes_clientes], None, True


@callback(
    Output("cards-status", "children"),
    Output("graph-responsavel", "figure"),
    Output("graph-pmo", "figure"),
    Input("store-features-ativas", "data"),
    Input("dropdown-clientes", "value"),
    Input("theme-store", "data")
)
def atualizar_cards(data, cliente, tema):
    if not data:
        raise PreventUpdate

    df = pd.DataFrame(data)
    if df.empty or "Status" not in df.columns:
        raise PreventUpdate

    if cliente:
        df = df[df["Cliente"] == cliente]

    status_cards = gerar_cards(df, "Status", STATUS_CARDS_COLORS)

    template_plotly = "plotly_dark" if tema == "dark" else "plotly"


    fig_responsavel = px.bar(
        df.groupby("Responsavel", as_index=False).size(),
        x="Responsavel",
        y="size",
        title="",
        labels={"size": ""},
        template=template_plotly
    )
    fig_responsavel.update_traces(hovertemplate="%{x} = %{y}<extra></extra>")

    fig_pmo = px.bar(
        df.groupby("PMO", as_index=False).size(),
        x="PMO",
        y="size",
        title="",
        labels={"size": ""},
        template=template_plotly
    )
    fig_pmo.update_traces(hovertemplate="%{x} = %{y}<extra></extra>")

    return status_cards, fig_responsavel, fig_pmo


@callback(
    Output("modal-tabela", "is_open"),
    Output("modal-tabela-conteudo", "children"),
    Input({"type": "filtro-card", "campo": ALL, "valor": ALL}, "n_clicks"),
    Input("graph-responsavel", "clickData"),
    Input("graph-pmo", "clickData"),
    State({"type": "filtro-card", "campo": ALL, "valor": ALL}, "id"),
    State("store-features-ativas", "data"),
    State("dropdown-clientes", "value"),
    prevent_initial_call=True
)
def abrir_modal_tabela(clicks, click_responsavel, click_pmo, ids, data, cliente):
    # Dicionário para nomes exibidos no título
    NOMES_TITULO = {
        "FarolTexto": "Farol"
        # Adicione mais substituições se quiser
    }

    trigger = ctx.triggered_id

    # Fechar modal se trigger inválido
    if not trigger:
        return False, dash.no_update

    is_card = isinstance(trigger, dict) and trigger.get("type") == "filtro-card"
    is_responsavel = trigger == "graph-responsavel"
    is_pmo = trigger == "graph-pmo"

    if is_card:
        try:
            idx = ids.index(trigger)
        except ValueError:
            return False, dash.no_update
        if not clicks or clicks[idx] is None or clicks[idx] == 0:
            return False, dash.no_update
    elif is_responsavel and not click_responsavel:
        return False, dash.no_update
    elif is_pmo and not click_pmo:
        return False, dash.no_update
    elif not (is_card or is_responsavel or is_pmo):
        return False, dash.no_update

    campo = valor = None
    if is_responsavel and click_responsavel:
        campo = "Responsavel"
        valor = click_responsavel["points"][0]["x"]
    elif is_pmo and click_pmo:
        campo = "PMO"
        valor = click_pmo["points"][0]["x"]
    elif is_card:
        campo = trigger.get("campo")
        valor = trigger.get("valor")

    if not campo or not valor:
        return False, dash.no_update

    # Troca nome do campo só para exibição do título
    nome_exibido = NOMES_TITULO.get(campo, campo)

    df = pd.DataFrame(data)
    if cliente:
        df = df[df["Cliente"] == cliente]

    df = df[df[campo] == valor]

    return True, html.Div([
        html.H4(f"Tabela {nome_exibido} - {valor}", className="fw-bold mb-3 text-center"),
        dcc.Location(id="redirect-feature", refresh=True),
        dash_table.DataTable(
            id="tabela-modal-detalhada",
            columns=[
                {"name": "Nº de Proposta", "id": "NumeroProposta", "hideable": True},
                {"name": "Horas", "id": "Horas", "hideable": True},
                {"name": "Projeto", "id": "Projeto", "hideable": True},
                {"name": "%", "id": "%", "hideable": True},
                {"name": "Farol", "id": "FarolIcone", "hideable": True, "presentation": "markdown"},
                {"name": "Situação", "id": "Situação", "hideable": True},
                {"name": "Status", "id": "Status", "hideable": True},
                {"name": "Responsável", "id": "Responsavel", "hideable": True},
                {"name": "PMO", "id": "PMO", "hideable": True},
                {"name": "Data de Início", "id": "DataInicio", "hideable": True},
                {"name": "Data Fim Original", "id": "DataFimOriginal", "hideable": True},
                {"name": "Data de Homologação", "id": "DataHomologacao", "hideable": True},
                {"name": "Data Estimada", "id": "DataFim", "hideable": True},
                {"name": "Key User", "id": "KeyUser", "hideable": True},
                {"name": "Aprovador", "id": "Aprovador", "hideable": True},
            ],
            style_cell_conditional=[
                {"if": {"column_id": "NumeroProposta"}, "minWidth": "90px", "maxWidth": "10px", "whiteSpace": "normal"},
                {"if": {"column_id": "%"}, "minWidth": "30px", "maxWidth": "40px", "whiteSpace": "normal"},
                {"if": {"column_id": "FarolTexto"}, "minWidth": "60px", "maxWidth": "60px", "whiteSpace": "normal"},
                {"if": {"column_id": "Situação"}, "minWidth": "200px", "maxWidth": "300px", "whiteSpace": "pre-line"},
                {"if": {"column_id": "DataHomologacao"}, "minWidth": "110px", "maxWidth": "120px", "whiteSpace": "normal"},
                {"if": {"column_id": "DataInicio"}, "minWidth": "100px", "maxWidth": "110px", "whiteSpace": "normal"},
                {"if": {"column_id": "DataFimOriginal"}, "minWidth": "100px", "maxWidth": "110px", "whiteSpace": "normal"},
                {"if": {"column_id": "DataFim"}, "minWidth": "100px", "maxWidth": "110px", "whiteSpace": "normal"},
                {"if": {"column_id": "Aprovador"}, "minWidth": "100px", "maxWidth": "110px", "whiteSpace": "normal"},
                {"if": {"column_id": "FarolIcone"}, "textAlign": "center", "verticalAlign": "middle", "fontSize": "45px", "padding": "0px", "minWidth": "60px", "maxWidth": "60px", "whiteSpace": "normal"},
            ],
            data=df.to_dict("records"),
            style_table={
                "overflowX": "auto",
                "overflowY": "auto",
                "maxHeight": "600px",
                "width": "100%"
            },
            fixed_rows={"headers": True},
            style_cell={
                "textAlign": "center",
                "whiteSpace": "pre-line",
                "fontSize": "11px",
                "padding": "6px",
                "minWidth": "70px",
                "maxWidth": "200px",
                "cursor": "pointer"
            },
            style_header={"backgroundColor": "#f8f9fa", "fontWeight": "bold", "whiteSpace": "normal", "textAlign": "center", "fontWeight": "bold" , "fontSize": "12px"},
            page_size=len(df),
            cell_selectable=True,
        )
    ])


@callback(
    Output("download-excel-farol", "data"),
    Input("btn-exportar-dados", "n_clicks"),
    State("store-features-ativas", "data"),
    State("dropdown-clientes", "value"),
    State("store-user-session", "data"),
    prevent_initial_call=True
)
def exportar_excel(n, data, cliente, user):
    df = pd.DataFrame(data)
    cliente_nome = cliente if cliente else "TODOS"
    email = user.get("email", "").lower()
    is_admin = email.endswith("@qualiit.com.br")
    if cliente:
        df = df[df["Cliente"] == cliente]
    output = gerar_excel_status_report(df, cliente_nome, is_admin)
    nome_arquivo = f"Status_Report_{cliente_nome.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d')}.xlsx"
    return dcc.send_bytes(output.read(), filename=nome_arquivo)

layout = dbc.Container([
    dcc.Store(id="store-user-session", storage_type="local"),
    dcc.Store(id="store-features-ativas", data=[]),
    dcc.Store(id="store-cliente-selecionado", storage_type="session"),
    dcc.Store(id="store-refresh-farol", storage_type="session"),
    html.Div(id="cards-status", className="mb-3 mt-4 d-flex justify-content-center flex-wrap"),
    html.Div(id="dummy-output", style={"display": "none"}),
    html.Div([
        html.Div([
            dbc.Label("Filtrar por Cliente:", className="fw-bold text-center mb-1"),
            dbc.InputGroup([
                dbc.Button("🔄 Atualizar Dados", id="btn-atualizar-dados", color="secondary"),
                dcc.Dropdown(
                    id="dropdown-clientes",
                    placeholder="Selecione o Cliente",
                    style={"minWidth": "240px"},
                    className="text-center"
                ),
                dbc.Button("📥 Exportar Farol", id="btn-exportar-dados", color="primary"),
                dcc.Download(id="download-excel-farol")
            ], className="gap-2 d-flex align-items-center justify-content-center")
        ], className="text-center")
    ], className="my-3"),
    dbc.Row([
        dbc.Col(dcc.Graph(id="graph-responsavel"), md=6),
        dbc.Col(dcc.Graph(id="graph-pmo"), md=6)
    ]),
    dbc.Modal([
        dbc.ModalHeader(dbc.ModalTitle("Tabela Filtrada")),
        dbc.ModalBody(id="modal-tabela-conteudo")
    ], id="modal-tabela", size="xl", is_open=False, scrollable=True, fullscreen=True, style={"padding": "20px"}),
    html.A(id="link-nova-aba", href="", target="_blank", style={"display": "none"})

], fluid=True)


@callback(
    Output("store-features-ativas", "data", allow_duplicate=True),
    Output("dropdown-clientes", "options", allow_duplicate=True),
    Output("store-cliente-selecionado", "data", allow_duplicate=True),
    Input("btn-atualizar-dados", "n_clicks"),
    State("store-user-session", "data"),
    prevent_initial_call=True
)
def forcar_atualizacao_farol(n_clicks, user):
    if not user:
        raise PreventUpdate
    email = user.get("email")
    # Aqui está a correção principal: forçar ignorar o cache
    df = gerar_dados_features(email, force_refresh=True)
    opcoes_clientes = sorted(df["Cliente"].dropna().unique())
    return df.to_dict("records"), [{"label": c, "value": c} for c in opcoes_clientes], None

@callback(
    Output("link-nova-aba", "href"),
    Input("tabela-modal-detalhada", "active_cell"),
    State("tabela-modal-detalhada", "data"),
    prevent_initial_call=True
)
def abrir_nova_aba(_, __):
    return dash.no_update

abrir_nova_aba._clientside_function = ClientsideFunction(
    namespace="clientside",
    function_name="abrirNovaAba"
)
