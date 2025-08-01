# pages/login.py (refinado)
from dash import html, register_page
import dash_bootstrap_components as dbc
from dash import clientside_callback, Output, Input

register_page(__name__, path="/")

layout = html.Div([
    html.Div(
        "Farol Operacional - Quali IT",
        style={
            "position": "absolute",
            "top": "20px",
            "left": "30px",
            "color": "#bbb",
            "fontSize": "14px",
            "letterSpacing": "0.5px"
        }
    ),

    html.Div([
        html.Img(src="/assets/QualiIT_Logo.png", style={"height": "80px", "marginBottom": "30px"}),
        html.H1("🚦 Farol Operacional", style={"fontSize": "3em", "marginBottom": "10px"}),
        html.P("Soluções práticas para quem precisa de resultado", style={"fontSize": "1.2em", "marginBottom": "40px"}),

        html.A(
            html.Button(
                [
                    html.Img(
                        src="https://img.icons8.com/color/28/000000/microsoft.png",
                        className="ms-icon"
                    ),
                    html.Span("Entrar com Microsoft")
                ],
                className="login-button"
            ),
            href="https://login.microsoftonline.com/6eb6a2fd-839d-460d-9bb0-7ed15211a782/oauth2/v2.0/authorize?client_id=87e8d9fc-60fa-4d01-894f-f3753e11004b&response_type=code&redirect_uri=https%3A%2F%2Fd2k6golik0z21l.cloudfront.net%2Fcallback_login&response_mode=query&scope=openid%20email%20profile&state=12345",
            id="login-button"
        ),


        html.Small("Você será redirecionado para autenticação segura da Microsoft.", style={"marginTop": "15px", "opacity": 0.6})
    ],
        style={
            "display": "flex",
            "flexDirection": "column",
            "alignItems": "center",
            "textAlign": "center",
            "animation": "fadeIn 0.8s ease-in-out"
        },
        className="fade-in"
    )
],
    style={
        "height": "100vh",
        "display": "flex",
        "justifyContent": "center",
        "alignItems": "center",
        "background": "linear-gradient(135deg, #0f2027, #203a43, #2c5364)",
        "color": "white",
        "fontFamily": "Segoe UI, sans-serif",
        "overflow": "hidden"
    }
)

clientside_callback(
    """
    function(n_clicks) {
        if (n_clicks > 0) {
            var audio = document.getElementById('login-sound');
            if (audio) {
                audio.play();
            }
        }
        return null;
    }
    """,
    Output("play-sound", "data"),
    Input("login-button", "n_clicks"),
    prevent_initial_call=True
)