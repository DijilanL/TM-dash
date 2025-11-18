import dash
from dash import html, dcc, callback, Input, Output, State
import numpy as np
import plotly.graph_objects as go


dash.register_page(__name__, path="/pagina6", name="Campo Vectorial")

# =========================
#   LAYOUT
# =========================
layout = html.Div(
    children=[
     
        html.Div(
            children=[
                html.H2("Campo Vectorial 2D", className="title"),

                html.P(
                    "Define las componentes del campo y el dominio en cada eje "
                    "para visualizar el comportamiento de las trayectorias.",
                    className="section-subtitle",
                ),

               
                html.Div(
                    children=[
                        html.Div(
                            [
                                html.Label("Ecuación dx/dt = f(X,Y)"),
                                html.Div(
                                    [
                                        dcc.Input(
                                            id="input-fx",
                                            type="text",
                                            value="Y/(X**2+Y**2+1)",
                                            className="input-field",
                                        ),
                                    ],
                                    className="input-wrapper",
                                ),
                                html.Small(
                                    "Usa funciones de numpy: np.sin, np.cos, np.exp, etc.",
                                    className="field-hint",
                                ),
                            ],
                            className="input-group",
                        ),

                        html.Div(
                            [
                                html.Label("Ecuación dy/dt = g(X,Y)"),
                                html.Div(
                                    [
                                        dcc.Input(
                                            id="input-fy",
                                            type="text",
                                            value="-X/(X**2+Y**2+1)",
                                            className="input-field",
                                        ),
                                    ],
                                    className="input-wrapper",
                                ),
                                html.Small(
                                    "Ambas ecuaciones se evalúan sobre la malla (X,Y).",
                                    className="field-hint",
                                ),
                            ],
                            className="input-group",
                        ),

                        html.Div(
                            [
                                html.Label("Rango del eje X"),
                                html.Div(
                                    [
                                        dcc.Input(
                                            id="input-xmax",
                                            type="number",
                                            value=5,
                                            className="input-field",
                                        ),
                                        html.Span(
                                            "[-Xmax, Xmax]",
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
                                html.Label("Rango del eje Y"),
                                html.Div(
                                    [
                                        dcc.Input(
                                            id="input-ymax",
                                            type="number",
                                            value=5,
                                            className="input-field",
                                        ),
                                        html.Span(
                                            "[-Ymax, Ymax]",
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
                                html.Label("Mallado (n puntos por eje)"),
                                html.Div(
                                    [
                                        dcc.Input(
                                            id="input-n",
                                            type="number",
                                            value=15,
                                            className="input-field",
                                        ),
                                        html.Span(
                                            "resolución",
                                            className="input-addon",
                                        ),
                                    ],
                                    className="input-wrapper",
                                ),
                                html.Small(
                                    "Valores mayores dan más vectores pero tardan más en dibujar.",
                                    className="field-hint",
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
                            "Generar campo",
                            id="btn-generar",
                            className="btn-generar",
                        ),
                        html.Span(
                            "Tip: prueba un campo rotacional o uno que apunte hacia el origen.",
                            className="panel-hint",
                        ),
                    ],
                    className="sir-actions-row",
                ),

              
                html.Div(
                    children=[
                        html.H3("Ejemplos para probar", className="examples-title"),
                        html.Ul(
                            children=[
                                html.Li("dx/dt = X,      dy/dt = Y"),
                                html.Li("dx/dt = -Y,     dy/dt = X"),
                                html.Li("dx/dt = X+Y,    dy/dt = np.cos(Y)"),
                                html.Li("dx/dt = Y/(X**2+Y**2+1), dy/dt = -X/(X**2+Y**2+1)"),
                            ]
                        ),
                    ],
                    className="examples-box",
                ),
            ],
            className="content left sir-panel",
        ),

    
        html.Div(
            children=[
                html.H2(
                    "Visualización del Campo Vectorial",
                    className="title",
                ),
                dcc.Graph(
                    id="grafica-campo",
                    style={"height": "450px", "width": "100%"},
                ),
                html.Div(id="info-campo"),
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
    [
        Output("grafica-campo", "figure"),
        Output("info-campo", "children"),
    ],
    Input("btn-generar", "n_clicks"),
    State("input-fx", "value"),
    State("input-fy", "value"),
    State("input-xmax", "value"),
    State("input-ymax", "value"),
    State("input-n", "value"),
    prevent_initial_call=False,
)
def actualizar_grafica(n_clicks, fx_str, fy_str, xmax, ymax, n):
    
    x = np.linspace(-xmax, xmax, n)
    y = np.linspace(-ymax, ymax, n)
    X, Y = np.meshgrid(x, y)

    info_mensaje = ""

    try:
       
        diccionario = {
            "X": X,
            "Y": Y,
            "np": np,
            "sin": np.sin,
            "cos": np.cos,
            "tan": np.tan,
            "exp": np.exp,
            "sqrt": np.sqrt,
            "pi": np.pi,
            "e": np.e,
        }

        fx = eval(fx_str, diccionario)
        fy = eval(fy_str, diccionario)

   
        mag = np.sqrt(fx**2 + fy**2)
        mag_max = float(np.max(mag))
        mag_min = float(np.min(mag))
        info_mensaje = f"Magnitud: min = {mag_min:.2f}, max = {mag_max:.2f}"

    except Exception as error:
        fx = np.zeros_like(X)
        fy = np.zeros_like(Y)
        info_mensaje = f"Error en las ecuaciones: {error}"

 
    fig = go.Figure()

    for i in range(n):
        for j in range(n):
            x0, y0 = X[i, j], Y[i, j]
            x1, y1 = x0 + fx[i, j], y0 + fy[i, j]

            fig.add_trace(
                go.Scatter(
                    x=[x0, x1],
                    y=[y0, y1],
                    mode="lines+markers",
                    line=dict(color="blue", width=2),
                    marker=dict(size=[3, 5], color=["blue", "red"]),
                    showlegend=False,
                    hovertemplate=(
                        f"Punto: ({x0:.1f}, {y0:.1f})"
                        f"<br>Vector: ({fx[i,j]:.2f}, {fy[i,j]:.2f})"
                        "<extra></extra>"
                    ),
                )
            )

    fig.update_layout(
        title=dict(
            text=f"<b>Campo Vectorial: dx/dt = {fx_str}, dy/dt = {fy_str}</b>",
            x=0.5,
            font=dict(size=16, color="green"),
        ),
        xaxis_title="Eje X",
        yaxis_title="Eje Y",
        paper_bgcolor="lightyellow",
        plot_bgcolor="white",
        font=dict(family="Outfit", size=12),
        margin=dict(l=40, r=40, t=60, b=40),
    )

    fig.update_xaxes(
        showgrid=True,
        gridwidth=1,
        gridcolor="Lightpink",
        zeroline=True,
        zerolinewidth=2,
        zerolinecolor="red",
        range=[-xmax * 1.1, xmax * 1.1],
    )

    fig.update_yaxes(
        showgrid=True,
        gridwidth=1,
        gridcolor="Lightpink",
        zeroline=True,
        zerolinewidth=2,
        zerolinecolor="red",
        range=[-ymax * 1.1, ymax * 1.1],
        scaleanchor="x",
        scaleratio=1,
    )

    return fig, info_mensaje
