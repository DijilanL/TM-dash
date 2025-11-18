import dash
from dash import html, dcc, Input, Output, State, callback
import numpy as np
import plotly.graph_objects as go

# Registrar página en Dash
dash.register_page(__name__, path="/pagina3", name="Pagina 3")

#######################################################
# LAYOUT
#######################################################

layout = html.Div(children=[
    # Contenedor izquierdo: SOLO parámetros
    html.Div(children=[
        html.H2(
            "Crecimiento de la población y capacidad de carga",
            className='title'
        ),

        html.Div(children=[
            # P0
            html.Div([
                html.Label("Población inicial  P₀", style={"fontWeight": 500}),
                dcc.Input(
                    id="input-p0",
                    type="number",
                    value=200,
                    className="input-field",
                ),
            ], className="input-group"),

            # r
            html.Div([
                html.Label("Tasa de crecimiento  r", style={"fontWeight": 500}),
                dcc.Input(
                    id="input-r",
                    type="number",
                    value=0.04,
                    step=0.005,
                    className="input-field",
                ),
            ], className="input-group"),

            # K
            html.Div([
                html.Label("Capacidad de carga  K", style={"fontWeight": 500}),
                dcc.Input(
                    id="input-k",
                    type="number",
                    value=750,
                    className="input-field",
                ),
            ], className="input-group"),

            # t_max
            html.Div([
                html.Label("Horizonte temporal  tₘₐₓ", style={"fontWeight": 500}),
                dcc.Input(
                    id="input-t",
                    type="number",
                    value=100,
                    className="input-field",
                ),
            ], className="input-group"),
        ], className="sir-form-grid"),

        html.Div([
            html.Button(
                "Generar gráfica",
                id="btn-generar",
                className="btn-generar",
            ),
        ], className="sir-actions-row"),

    ], className="content left"),

    # Contenedor derecho: gráfica
    html.Div(children=[
        html.H2("Gráfica", className="title"),
        dcc.Graph(
            id="graph-output",
            style={"height": "380px", "width": "100%"},
        ),
    ], className="content right"),

], className="page-container")

#######################################################
# CALLBACK
#######################################################

@callback(
    Output("graph-output", "figure"),
    Input("btn-generar", "n_clicks"),
    State("input-p0", "value"),
    State("input-r", "value"),
    State("input-k", "value"),
    State("input-t", "value"),
    prevent_initial_call=False,
)
def actualizar_grafico(n_clicks, P0, r, K, t_max):
    # Asegurar tipos numéricos
    P0 = float(P0)
    r = float(r)
    K = float(K)
    t_max = float(t_max)

    # Mallado temporal
    t = np.linspace(0, t_max, 200)

    # Ecuación logística
    P = (P0 * K * np.exp(r * t)) / ((K - P0) + P0 * np.exp(r * t))

    # Curva de población
    trace_poblacion = go.Scatter(
        x=t,
        y=P,
        mode="lines+markers",
        name="P(t)",
        line=dict(
            dash="dot",
            color="green",
            width=2,
        ),
        marker=dict(
            color="orange",
            symbol="square",
            size=8,
        ),
        hovertemplate="t: %{x:.2f}<br>P(t): %{y:.2f}<extra></extra>",
    )

    # Línea de capacidad de carga
    trace_capacidad = go.Scatter(
        x=[0, t_max],
        y=[K, K],
        mode="lines",
        name="Capacidad de carga K",
        line=dict(
            color="red",
            width=2,
            dash="dash",
        ),
        hovertemplate="K: %{y:.2f}<extra></extra>",
    )

    fig = go.Figure(data=[trace_poblacion, trace_capacidad])

    # Layout general
    fig.update_layout(
        title=dict(
            text="<b>Crecimiento de población con capacidad de carga</b>",
            font=dict(
                family="Playfair Display",
                size=20,
                color="purple",
            ),
            x=0.5,
            y=0.93,
        ),
        xaxis_title="Tiempo (t)",
        yaxis_title="Población P(t)",
        margin=dict(l=80, r=40, t=60, b=120),  # más espacio abajo e izquierda
        paper_bgcolor="lightblue",
        plot_bgcolor="grey",
        font=dict(
            family="Playfair Display",
            size=15,
            color="black",
        ),
        legend=dict(
            orientation="h",
            yanchor="top",
            y=-0.30,             # leyenda más abajo
            xanchor="center",
            x=0.5,
            bgcolor="rgba(255,255,255,0.9)",
            bordercolor="rgba(0,0,0,0.1)",
            borderwidth=1,
        ),
    )

    # Eje X
    fig.update_xaxes(
        showgrid=True,
        gridwidth=1,
        gridcolor="lightpink",
        zeroline=True,
        zerolinewidth=2,
        zerolinecolor="blue",
        showline=True,
        linecolor="black",
        linewidth=2,
        mirror=True,
        title_standoff=25,          # separa el título del eje
        ticklabelposition="outside",
        automargin=True,
    )

    # Eje Y
    fig.update_yaxes(
        showgrid=True,
        gridwidth=1,
        gridcolor="lightpink",
        zeroline=True,
        zerolinewidth=2,
        zerolinecolor="blue",
        showline=True,
        linecolor="black",
        linewidth=2,
        mirror=True,
        title_standoff=25,
        ticklabelposition="outside",
        automargin=True,
    )

    return fig
