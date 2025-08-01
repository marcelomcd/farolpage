# callback_login.py (corrigido)
from dash import html, dcc, register_page, callback, Output, Input
import requests
import urllib.parse
import jwt  # pyjwt

register_page(__name__, path="/callback_login")

layout = html.Div([
    dcc.Location(id="url", refresh=True),
    html.H4("🔄 Verificando login...", style={"color": "#0078d4"}),
])

@callback(
    Output("url", "href"),
    Output("store-user-session", "data"),
    Input("url", "search"),
    prevent_initial_call=False
)
def processar_callback(query_string):
    if not query_string:
        return "/", None

    parsed = urllib.parse.parse_qs(query_string.lstrip("?"))
    code = parsed.get("code", [None])[0]
    if not code:
        return "/", None

    token_url = "https://login.microsoftonline.com/6eb6a2fd-839d-460d-9bb0-7ed15211a782/oauth2/v2.0/token"
    client_id = "87e8d9fc-60fa-4d01-894f-f3753e11004b"
    redirect_uri = "https://d2k6golik0z21l.cloudfront.net/callback_login"

    payload = {
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": redirect_uri,
        "client_id": client_id,
        "scope": "openid profile email",
    }

    try:
        response = requests.post(token_url, data=payload)
        token_data = response.json()
        print("🪪 TOKEN DATA:", token_data)

        id_token = token_data.get("id_token")
        if id_token:
            decoded = jwt.decode(id_token, options={"verify_signature": False})
            email = decoded.get("preferred_username")
            nome = decoded.get("name")
            return "/farol", {"email": email, "nome": nome}

    except Exception as e:
        print("Erro ao trocar o código:", e)

    return "/", None
