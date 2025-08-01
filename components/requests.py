# components/requests.py
from dash import html
from utils.helpers import (
    format_datetime, normalize_value, clean_html,
    RENOMEAR_CAMPOS, normalize_field_key,
    CAMPOS_EXCLUIDOS, CAMPOS_STATUS_REPORT, ORDEM_PRIORITARIA
)

def render_request(data):
    fields = data.get("fields", {})
    wi_id = data.get("id")
    titulo = fields.get("System.Title", "-")

    link = f"https://dev.azure.com/qualiit/Quali%20IT%20-%20Inova%C3%A7%C3%A3o%20e%20Tecnologia/_boards/board/t/Quali%20IT%20!%20Gestao%20de%20Proposta/Requests?workitem={wi_id}"

    created_date = format_datetime(fields.get('System.CreatedDate', '-'))
    changed_date = format_datetime(fields.get('System.ChangedDate', '-'))
    area = fields.get('System.AreaPath', '-')
    state = fields.get('System.State', '-')
    iteration = fields.get('System.IterationPath', '-')

    assigned = fields.get("System.AssignedTo")
    assigned_to = assigned.get("displayName", "-") if isinstance(assigned, dict) else "-"

    return html.Div([
        html.H4(f"🔹 ID: {wi_id} - {titulo}"),
        html.A("🔗 Abrir no Azure DevOps", href=link, target="_blank"),
        html.Br(),
        html.Div(f"📌 Estado: {state} | 🔹 Iteration: {iteration}"),
        html.Div(f"📍 Área: {area} | 🔍 Atualizado: {changed_date}"),
        html.Div(f"👤 Atribuído a: {assigned_to} | 📅 Criado: {created_date}"),

        html.Hr(),
        html.H5("📄 Informações da Request"),
        _render_custom_fields(fields)
    ])

def _render_custom_fields(fields):
    campos_unicos = {}

    for k, v in fields.items():
        if (k.startswith("Custom.") or k.startswith("Extension.")) and not any(sub in k.lower() for sub in CAMPOS_STATUS_REPORT):
            key_id = normalize_field_key(k.split('.')[-1])
            label = RENOMEAR_CAMPOS.get(key_id, k.split('.')[-1])
            if key_id in CAMPOS_EXCLUIDOS:
                continue
            valor = normalize_value(label, v)
            if label not in campos_unicos:
                campos_unicos[label] = valor

    prioritarios = [(k, campos_unicos[k]) for k in ORDEM_PRIORITARIA if k in campos_unicos]
    restantes = sorted([(k, v) for k, v in campos_unicos.items() if k not in ORDEM_PRIORITARIA], key=lambda x: x[0].lower())
    todos = prioritarios + restantes

    def render_campo(label, valor):
        linhas = str(valor).split("\n")
        return html.P([
            html.Span("\u2022 "),
            html.Strong(f"{label}: "),
            html.Span(linhas[0]),
            html.Br(),
            *[html.Span(linha, style={"display": "block"}) for linha in linhas[1:]]
        ], style={"whiteSpace": "pre-wrap", "marginBottom": "12px"})

    metade = len(todos) // 2 + len(todos) % 2
    col1 = html.Div([render_campo(k, v) for k, v in todos[:metade]])
    col2 = html.Div([render_campo(k, v) for k, v in todos[metade:]])

    return html.Div([
        html.Div([col1], style={"width": "48%", "display": "inline-block", "verticalAlign": "top"}),
        html.Div([col2], style={"width": "48%", "display": "inline-block", "marginLeft": "4%"})
    ])
