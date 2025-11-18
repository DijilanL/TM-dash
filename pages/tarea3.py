import dash
from dash import html, dcc, callback, Input, Output, State
import numpy as np
import plotly.graph_objects as go
from scipy.integrate import odeint


dash.register_page(__name__, path="/pagina8", name="Modelo SEIR")


def modelo_seir(y, t, beta, sigma, gamma, N):
    """
    Modelo SEIR clásico:
      S': -beta*S*I/N
      E':  beta*S*I/N - sigma*E
      I':  sigma*E - gamma*I
      R':  gamma*I
    """
    S, E, I, R = y

    dS_dt = -beta * S * I / N
    dE_dt = beta * S * I / N - sigma * E
    dI_dt = sigma * E - gamma * I
    dR_dt = gamma * I

    return [dS_dt, dE_dt, dI_dt, dR_dt]


# =========================
#   LAYOUT
# =========================
layout = html.Div(
    children=[
       
        html.Div(
            children=[
                html.H2(
                    "Modelo SEIR - Con periodo de latencia",
                    className="title",
                ),

                html.P(
                    "Explora la dinámica de una epidemia con individuos susceptibles (S), "
                    "expuestos pero aún no infecciosos (E), infectados (I) y recuperados (R).",
                    className="section-subtitle",
                ),

                html.Div(
                    children=[
                        # N
                        html.Div(
                            [
                                html.Label("Población total (N)"),
                                html.Div(
                                    [
                                        dcc.Input(
                                            id="seir-N",
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

                        # beta
                        html.Div(
                            [
                                html.Label("Tasa de transmisión (β)"),
                                html.Div(
                                    [
                                        dcc.Input(
                                            id="seir-beta",
                                            type="number",
                                            value=0.35,
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
                                    "Cuanto mayor es β, más rápido se contagia la enfermedad.",
                                    className="field-hint",
                                ),
                            ],
                            className="input-group",
                        ),

                        # sigma
                        html.Div(
                            [
                                html.Label("Tasa de paso de E a I (σ)"),
                                html.Div(
                                    [
                                        dcc.Input(
                                            id="seir-sigma",
                                            type="number",
                                            value=0.20,
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
                                    "Aproximadamente σ = 1 / (período de incubación).",
                                    className="field-hint",
                                ),
                            ],
                            className="input-group",
                        ),

                        # gamma
                        html.Div(
                            [
                                html.Label("Tasa de recuperación (γ)"),
                                html.Div(
                                    [
                                        dcc.Input(
                                            id="seir-gamma",
                                            type="number",
                                            value=0.15,
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
                                    "Aproximadamente γ = 1 / (duración infecciosa).",
                                    className="field-hint",
                                ),
                            ],
                            className="input-group",
                        ),

                        # E0
                        html.Div(
                            [
                                html.Label("Expuestos iniciales (E₀)"),
                                html.Div(
                                    [
                                        dcc.Input(
                                            id="seir-E0",
                                            type="number",
                                            value=5,
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

                        # I0
                        html.Div(
                            [
                                html.Label("Infectados iniciales (I₀)"),
                                html.Div(
                                    [
                                        dcc.Input(
                                            id="seir-I0",
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

                        # T
                        html.Div(
                            [
                                html.Label("Tiempo de simulación"),
                                html.Div(
                                    [
                                        dcc.Input(
                                            id="seir-T",
                                            type="number",
                                            value=160,
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
                            "Simular dinámica SEIR",
                            id="seir-btn-simular",
                            className="btn-generar",
                        ),
                        html.Span(
                            "Tip: prueba un período de incubación más largo (σ pequeño) "
                            "y observa cómo se retrasa el pico de infectados.",
                            className="panel-hint",
                        ),
                    ],
                    className="sir-actions-row",
                ),
            ],
            className="content left sir-panel",
        ),

       
        html.Div(
            children=[
                html.H2("Evolución temporal SEIR", className="title"),

                dcc.Graph(
                    id="seir-fig",
                    style={"height": "430px", "width": "100%"},
                ),

                html.Div(id="seir-info", className="examples-box"),
            ],
            className="content right",
        ),
    ],
    className="page-container",
)


# =========================
#   CALLBACK
# =========================
@callback(
    [Output("seir-fig", "figure"), Output("seir-info", "children")],
    Input("seir-btn-simular", "n_clicks"),
    State("seir-N", "value"),
    State("seir-beta", "value"),
    State("seir-sigma", "value"),
    State("seir-gamma", "value"),
    State("seir-E0", "value"),
    State("seir-I0", "value"),
    State("seir-T", "value"),
    prevent_initial_call=False,
)
def simular_seir(n_clicks, N, beta, sigma, gamma, E0, I0, T_max):

    N = float(N)
    beta = float(beta)
    sigma = float(sigma)
    gamma = float(gamma)
    E0 = float(E0)
    I0 = float(I0)
    T_max = float(T_max)

   
    S0 = N - E0 - I0
    R0_inicial = 0.0
    y0 = [S0, E0, I0, R0_inicial]

   
    t = np.linspace(0, T_max, 300)

    try:
        sol = odeint(modelo_seir, y0, t, args=(beta, sigma, gamma, N))
        S, E, I, R = sol.T
    except Exception:
      
        S = np.full_like(t, S0)
        E = np.full_like(t, E0)
        I = np.full_like(t, I0)
        R = np.full_like(t, R0_inicial)

  
    fig = go.Figure()

    fig.add_trace(
        go.Scatter(
            x=t,
            y=S,
            mode="lines",
            name="Susceptibles (S)",
            line=dict(color="#2563eb", width=2),
            hovertemplate="t = %{x:.1f}<br>S = %{y:.0f}<extra></extra>",
        )
    )
    fig.add_trace(
        go.Scatter(
            x=t,
            y=E,
            mode="lines",
            name="Expuestos (E)",
            line=dict(color="#eab308", width=2),
            hovertemplate="t = %{x:.1f}<br>E = %{y:.0f}<extra></extra>",
        )
    )
    fig.add_trace(
        go.Scatter(
            x=t,
            y=I,
            mode="lines",
            name="Infectados (I)",
            line=dict(color="#dc2626", width=2),
            hovertemplate="t = %{x:.1f}<br>I = %{y:.0f}<extra></extra>",
        )
    )
    fig.add_trace(
        go.Scatter(
            x=t,
            y=R,
            mode="lines",
            name="Recuperados (R)",
            line=dict(color="#16a34a", width=2),
            hovertemplate="t = %{x:.1f}<br>R = %{y:.0f}<extra></extra>",
        )
    )

    fig.update_layout(
    title=dict(
        text="<b>Modelo SEIR</b>",
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
        yanchor="top",
        y=-0.18,        
        xanchor="center",
        x=0.5,
        bgcolor="rgba(255,255,255,0.9)",
        bordercolor="rgba(0,0,0,0.1)",
        borderwidth=1,
    ),
    margin=dict(l=70, r=40, t=70, b=90),  
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

  
    R0 = beta / gamma if gamma > 0 else np.nan
 
    periodo_incub = 1.0 / sigma if sigma > 0 else np.nan
    periodo_infec = 1.0 / gamma if gamma > 0 else np.nan

    idx_peak = int(np.argmax(I))
    t_peak = float(t[idx_peak])
    I_peak = float(I[idx_peak])

    resumen = html.Div(
        children=[
            html.H4("Resumen de la simulación", style={"marginTop": 0}),
            html.P(
                f"R₀ ≈ {R0:.2f} "
                f"(β / γ). Si R₀ > 1, la epidemia tiende a crecer inicialmente.",
            ),
            html.P(
                f"Período medio de incubación ≈ {periodo_incub:.1f} días "
                f"(1/σ), período infeccioso ≈ {periodo_infec:.1f} días (1/γ).",
            ),
            html.P(
                f"Máximo de infectados: Iₘₐₓ ≈ {I_peak:.0f} personas "
                f"alrededor del día t ≈ {t_peak:.1f}.",
            ),
        ]
    )

    return fig, resumen
