from dash import dcc, html, Input, Output, State, callback, MATCH
import dash_bootstrap_components as dbc

def DropdownThemed(id, options=[], placeholder="Selecione...", **kwargs):
    """
    Wrapper para dcc.Dropdown com suporte a tema dinâmico
    - Aplica classe 'theme-dark' ou 'theme-light' no wrapper externo com base na store de tema
    - Permite repassar quaisquer outros kwargs para o Dropdown original
    """
    return html.Div(
        id={"type": "dropdown-themed-wrapper", "id": id},
        children=[
            dcc.Dropdown(
                id=id,
                options=options,
                placeholder=placeholder,
                className="dropdown-clientes",
                **kwargs
            )
        ],
        className="dropdown-wrapper"
    )
