# test/debug.py
from dash import html, dcc, callback, Input, Output, State
import dash
import dash_bootstrap_components as dbc
from utils.api import get_work_item, get_all_requests
from utils.helpers import limpar_valor, clean_html
from pprint import pformat
from components.comentarios import _extrair_comentarios
from utils.api import get_revisions

app = dash.get_app()
dash.register_page(__name__, path="/debug-feature", name="Debug Feature")

layout = dbc.Container([
    html.H2("🧪 Debug de Work Item (Feature ou Request)", className="my-4 text-center"),

    dbc.Row([
        dbc.Col([
            dcc.Dropdown(
                id="tipo-item",
                options=[{"label": "Feature", "value": "feature"}, {"label": "Request", "value": "request"}],
                value="feature",
                clearable=False,
                className="mb-2"
            ),
            dbc.Input(id="input-id-item", placeholder="Digite o número do item", type="number"),
            dbc.Button("Buscar", id="btn-buscar-item", color="primary", className="mt-2")
        ], width=4)
    ]),

    html.Hr(),

    dbc.Row([
        dbc.Col([
            html.H5("🧾 Texto Bruto (original da API)", className="mb-2"),
            dcc.Textarea(id="output-texto-bruto", style={"width": "100%", "height": "300px", "whiteSpace": "pre-wrap"})
        ], width=6),

        dbc.Col([
            html.H5("✅ Texto Limpo com limpar_valor + clean_html", className="mb-2"),
            dcc.Textarea(id="output-texto-processado", style={"width": "100%", "height": "300px", "whiteSpace": "pre-wrap"})
        ], width=6)
    ])
], fluid=True)

@callback(
    Output("output-texto-bruto", "value"),
    Output("output-texto-processado", "value"),
    Input("btn-buscar-item", "n_clicks"),
    State("tipo-item", "value"),
    State("input-id-item", "value"),
    prevent_initial_call=True
)
def debug_work_item(_, tipo, item_id):
    if not item_id:
        return "", ""

    if tipo == "feature":
        wi = get_work_item(item_id)
    elif tipo == "request":
        wi = next((req for req in get_all_requests() if req.get("id") == item_id), None)
    else:
        wi = None

    if not wi or "fields" not in wi:
        return "Item não encontrado.", ""

    revisions = get_revisions(item_id)
    if not revisions:
        return "Sem revisions encontradas.", ""

    brutos = []
    limpos = []
    for rev in revisions:
        hist = rev.get("fields", {}).get("System.History")
        if not hist:
            continue
        brutos.append(hist)
        limpos.append(clean_html(hist).strip())

    parsed = _extrair_comentarios(revisions)
    saida = []
    for i, c in enumerate(parsed, 1):
        saida.append(f"{i:02d}) {c['data_formatada']} - {c['responsavel']}\n{c['conteudo']}\n" + "-"*40)

    texto_bruto = "\n\n=== HISTÓRICO ORIGINAL ===\n" + "\n\n".join(brutos)
    texto_processado = "\n\n=== HISTÓRICO FORMATADO ===\n" + "\n\n".join(saida)

    return texto_bruto, texto_processado