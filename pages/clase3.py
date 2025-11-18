import dash
from dash import html, dcc, callback, Input, Output, State
import numpy as np
import plotly.graph_objects as go
from scipy.integrate import odeint

dash.register_page(__name__, path="/pagina7", name="Modelo SIR")

# =========================
#   LAYOUT
# =========================
layout = html.Div(
    children=[
  
        html.Div(
            children=[
                html.H2("Modelo SIR - Epidemiología", className="title"),

                html.P(
                    "Ajusta los parámetros del modelo SIR para explorar cómo evoluciona "
                    "una epidemia en una población cerrada.",
                    className="section-subtitle",
                ),

           
                html.Div(
                    children=[
                        html.Div(
                            [
                                html.Label("Población total (N)"),
                                html.Div(
                                    [
                                        dcc.Input(
                                            id="input-N",
                                            type="number",
                                            value=1000,
                                            className="input-field",
                                        ),
                                        html.Span(
                                            "personas",
                                            className="input-addon",
                                        ),
                                    ],
                                    className="input-wrapper",
                                ),
                            ],
                            className="input-group",
                        ),

                        html.Div(
                            [
                                html.Label("Tasa de transmisión (β)"),
                                html.Div(
                                    [
                                        dcc.Input(
                                            id="input-beta",
                                            type="number",
                                            value=0.30,
                                            step=0.01,
                                            className="input-field",
                                        ),
                                        html.Span(
                                            "por día",
                                            className="input-addon",
                                        ),
                                    ],
                                    className="input-wrapper",
                                ),
                                html.Small(
                                    "Controla qué tan rápido se contagia la enfermedad.",
                                    className="field-hint",
                                ),
                            ],
                            className="input-group",
                        ),

                        html.Div(
                            [
                                html.Label("Tasa de recuperación (γ)"),
                                html.Div(
                                    [
                                        dcc.Input(
                                            id="input-gamma",
                                            type="number",
                                            value=0.10,
                                            step=0.01,
                                            className="input-field",
                                        ),
                                        html.Span(
                                            "por día",
                                            className="input-addon",
                                        ),
                                    ],
                                    className="input-wrapper",
                                ),
                                html.Small(
                                    "Personas que dejan de ser infecciosas cada día.",
                                    className="field-hint",
                                ),
                            ],
                            className="input-group",
                        ),

                        html.Div(
                            [
                                html.Label("Infectados iniciales"),
                                html.Div(
                                    [
                                        dcc.Input(
                                            id="input-I0",
                                            type="number",
                                            value=1,
                                            className="input-field",
                                        ),
                                        html.Span(
                                            "personas",
                                            className="input-addon",
                                        ),
                                    ],
                                    className="input-wrapper",
                                ),
                            ],
                            className="input-group",
                        ),

                        html.Div(
                            [
                                html.Label("Tiempo de simulación"),
                                html.Div(
                                    [
                                        dcc.Input(
                                            id="input-tiempo",
                                            type="number",
                                            value=100,
                                            className="input-field",
                                        ),
                                        html.Span(
                                            "días",
                                            className="input-addon",
                                        ),
                                    ],
                                    className="input-wrapper",
                                ),
                            ],
                            className="input-group",
                        ),
                    ],
                    className="sir-form-grid",
                ),

              
                html.Div(
                    children=[
                        html.Button(
                            "Simular epidemia",
                            id="btn-simular",
                            className="btn-generar",
                        ),
                        html.Span(
                            "Tip: prueba β > γ para observar un brote marcado.",
                            className="panel-hint",
                        ),
                    ],
                    className="sir-actions-row",
                ),
            ],
            className="content left sir-panel",
        ),

        # COLUMNA DERECHA: gráfica
        html.Div(
            children=[
                html.H2("Evolución de epidemia", className="title"),
                dcc.Graph(
                    id="grafica-sir",
                    style={"height": "450px", "width": "100%"},
                ),
            ],
            className="content right",
        ),
    ],
    className="page-container",
)

# =========================
#   MODELO SIR
# =========================
def modelo_sir(y, t, beta, gamma, N):
    S, I, R = y
    dS_dt = -beta * S * I / N
    dI_dt = beta * S * I / N - gamma * I
    dR_dt = gamma * I
    return [dS_dt, dI_dt, dR_dt]


@callback(
    Output("grafica-sir", "figure"),
    Input("btn-simular", "n_clicks"),
    State("input-N", "value"),
    State("input-beta", "value"),
    State("input-gamma", "value"),
    State("input-I0", "value"),
    State("input-tiempo", "value"),
    prevent_initial_call=False,
)
def simular_sir(n_clicks, N, beta, gamma, I0, tiempo_max):
    N = float(N)
    beta = float(beta)
    gamma = float(gamma)
    I0 = float(I0)
    tiempo_max = float(tiempo_max)

    S0 = N - I0
    R0_inicial = 0.0
    y0 = [S0, I0, R0_inicial]

    t = np.linspace(0, tiempo_max, 200)

    try:
        solucion = odeint(modelo_sir, y0, t, args=(beta, gamma, N))
        S, I, R = solucion.T
    except Exception:
        S = np.full_like(t, 50.0)
        I = np.full_like(t, I0)
        R = np.full_like(t, R0_inicial)

    fig = go.Figure()

    fig.add_trace(
        go.Scatter(
            x=t,
            y=S,
            mode="lines",
            name="Susceptibles (S)",
            line=dict(color="blue", width=2),
            hovertemplate="Día: %{x:.0f}<br>Susceptibles: %{y:.0f}<extra></extra>",
        )
    )

    fig.add_trace(
        go.Scatter(
            x=t,
            y=I,
            mode="lines",
            name="Infectados (I)",
            line=dict(color="red", width=2),
            hovertemplate="Día: %{x:.0f}<br>Infectados: %{y:.0f}<extra></extra>",
        )
    )

    fig.add_trace(
        go.Scatter(
            x=t,
            y=R,
            mode="lines",
            name="Recuperados (R)",
            line=dict(color="green", width=2),
            hovertemplate="Día: %{x:.0f}<br>Recuperados: %{y:.0f}<extra></extra>",
        )
    )

    fig.update_layout(
        title=dict(
            text="<b>Evolución del Modelo SIR(t)</b>",
            x=0.5,
            font=dict(size=16, color="darkblue"),
        ),
        xaxis_title="Tiempo (días)",
        yaxis_title="Número de personas",
        paper_bgcolor="lightcyan",
        plot_bgcolor="white",
        font=dict(family="Outfit", size=12),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=0.5,
        ),
        margin=dict(l=80, r=40, t=60, b=60),
    )

    fig.update_xaxes(
        showgrid=True,
        gridwidth=1,
        gridcolor="lightpink",
        zeroline=True,
        zerolinewidth=2,
        zerolinecolor="black",
    )

    fig.update_yaxes(
        showgrid=True,
        gridwidth=1,
        gridcolor="lightpink",
        zeroline=True,
        zerolinewidth=2,
        zerolinecolor="black",
    )

    return fig
