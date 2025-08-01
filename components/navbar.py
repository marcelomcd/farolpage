import dash_bootstrap_components as dbc
from dash import html, dcc, Output, Input, State, callback, clientside_callback

def get_navbar_color(status: str) -> str:
    if not status:
        return "#009999"
    status = status.lower()
    if "sem problema" in status:
        return "#198754"
    elif "com problema" in status:
        return "#ffc107"
    elif "problema crítico" in status:
        return "#dc3545"
    return "#009999"

def build_navbar(status_projeto=None, user_data=None):
    status_cor = get_navbar_color(status_projeto)

    login_button = html.A(
        dbc.Button("Entrar com Microsoft", color="primary", size="sm"),
        href=(
            "https://login.microsoftonline.com/6eb6a2fd-839d-460d-9bb0-7ed15211a782/"
            "oauth2/v2.0/authorize?client_id=87e8d9fc-60fa-4d01-894f-f3753e11004b"
            "&response_type=code&redirect_uri=http://localhost:8050/callback_login"
            "&response_mode=query&scope=openid%20email%20profile&state=12345"
        ),
        style={"marginLeft": "10px"}
    )

    nav_links = [
        dbc.NavLink("Farol", href="/farol", active="exact"),
    ]

    if user_data and user_data.get("email", "").endswith("@qualiit.com.br"):
        nav_links.extend([
            dbc.NavLink("Projetos Concluídos", href="/projetos-concluidos", active="exact"),
            dbc.NavLink("Requests Ativas", href="/requests-ativas", active="exact"),
            dbc.NavLink("Requests Concluídas", href="/requests-concluidas", active="exact")
        ])

    return html.Div([
        dcc.Store(id="theme-store", data="light"),
        dcc.Store(id="theme-persistence", storage_type="local"),
        html.Link(id="theme-link", rel="stylesheet", href="/assets/light.css"),

        dbc.Navbar(
            dbc.Container([
                html.A(
                    dbc.Row([
                        dbc.Col(html.Img(src="/assets/QualiIT_Logo.png", height="40px")),
                        dbc.Col(dbc.NavbarBrand("Farol Operacional", className="ms-2")),
                    ], align="center", className="g-0"),
                    href="/farol",
                    style={"textDecoration": "none"}
                ),
                dbc.Nav(nav_links, pills=True),
                dbc.Row([
                    dbc.Col([
                        html.Div(id="theme-status", className="me-2", style={
                            "color": "white", "fontSize": "13px", "fontWeight": "bold"
                        }),
                        html.Div([
                            html.Span("Dark", className="me-2 text-white"),
                            dbc.Checklist(
                                options=[{"label": "", "value": 1}],
                                id="theme-toggle",
                                switch=True,
                                className="light-switch"
                            ),
                            html.Span("Light", className="ms-2 text-white")
                        ], className="d-flex align-items-center gap-2")
                    ]),
                    dbc.Col([
                        html.Span(user_data.get("nome", ""), style={
                            "color": "white", "fontSize": "14px", "marginLeft": "10px"
                        }) if user_data else html.Span("")
                    ]),

                ], align="center", justify="end")
            ], fluid=True),
            color=status_cor,
            dark=True,
            className="px-3"
        )
    ])

clientside_callback(
    """
    function(toggleVal, currentTheme) {
        const trigger = dash_clientside.callback_context.triggered_id;
        if (trigger === 'theme-toggle') {
            const newTheme = toggleVal?.includes(1) ? 'light' : 'dark';
            localStorage.setItem('theme', newTheme);
            return [newTheme, toggleVal, newTheme];
        }
        if (trigger === 'theme-persistence') {
            const savedTheme = localStorage.getItem('theme') || 'light';
            const toggleState = savedTheme === 'light' ? [1] : [];
            return [savedTheme, toggleState, savedTheme];
        }
        return dash_clientside.no_update;
    }
    """,
    Output("theme-store", "data"),
    Output("theme-toggle", "value"),
    Output("theme-persistence", "data"),
    Input("theme-toggle", "value"),
    Input("theme-persistence", "data"),
    State("theme-store", "data"),
)

@callback(
    Output("theme-link", "href"),
    Output("body-wrapper", "className"),
    Input("theme-store", "data")
)
def update_css_and_body_class(theme):
    return f"/assets/{theme}.css", f"{theme}-mode"

@callback(
    Output("theme-status", "children"),
    Input("theme-store", "data")
)
def update_theme_label(theme):
    return "💡 Luz Acesa" if theme == "light" else "🌃 Luz Apagada"

navbar_padrao = build_navbar()
