import dash
from dash import html, dcc, callback, Input, Output, State
import plotly.graph_objects as go
import requests
from datetime import datetime
import numpy as np


def formatear_numero(numero):
    """
    Convierte un número (ej: 1234567) en "1,234,567".
    """
    if numero is None:
        return "N/A"
    try:
        return f"{int(numero):,}"
    except (ValueError, TypeError):
        return str(numero)


# Registrar la página
dash.register_page(__name__, path="/pagina9", name="Covid-19")

# =========================
#   LAYOUT
# =========================
layout = html.Div(
    children=[
        # COLUMNA IZQUIERDA
        html.Div(
            children=[
                html.H2("Dashboard Covid-19", className="title"),

                html.Div(
                    [
                        html.Label("Seleccione el país:"),
                        dcc.Dropdown(
                            id="dropdown-pais",
                            options=[
                                {"label": "Perú", "value": "Peru"},
                                {"label": "México", "value": "Mexico"},
                                {"label": "Estados Unidos", "value": "USA"},
                                {"label": "Canadá", "value": "Canada"},
                            ],
                            value="Peru",
                            className="input-field",
                            style={"width": "100%"},
                        ),
                    ],
                    className="input-group",
                ),

                html.Div(
                    [
                        html.Label("Días histórico:"),
                        dcc.Dropdown(
                            id="dropdown-dias-covid",
                            options=[
                                {"label": "30 días", "value": 30},
                                {"label": "60 días", "value": 60},
                                {"label": "90 días", "value": 90},
                                {"label": "120 días", "value": 120},
                                {"label": "Todo el histórico", "value": "all"},
                            ],
                            value=30,
                            className="input-field",
                            style={"width": "100%"},
                        ),
                    ],
                    className="input-group",
                ),

                html.Button(
                    "Actualizar datos",
                    id="btn-actualizar-covid",
                    className="btn-generar",
                ),

                html.Div(id="info-actualizado-covid", style={"marginTop": "8px"}),
            ],
            className="content left",
        ),

        # COLUMNA DERECHA
        html.Div(
            children=[
                html.H2("Estadísticas en tiempo real", className="title"),

                # Primera fila de tarjetas
                html.Div(
                    [
                        html.Div(
                            [
                                html.H4("Total casos", style={"color": "#1976d2"}),
                                html.H3(
                                    id="total-casos",
                                    style={"color": "#0b3661", "margin": 0},
                                ),
                            ],
                            style={
                                "backgroundColor": "#e3f2fd",
                                "padding": "10px",
                                "borderRadius": "10px",
                                "textAlign": "center",
                                "flex": "1",
                            },
                        ),
                        html.Div(
                            [
                                html.H4("Casos nuevos", style={"color": "#e65100"}),
                                html.H3(
                                    id="casos-nuevos",
                                    style={"color": "#bf360c", "margin": 0},
                                ),
                            ],
                            style={
                                "backgroundColor": "#fff3e0",
                                "padding": "10px",
                                "borderRadius": "10px",
                                "textAlign": "center",
                                "flex": "1",
                            },
                        ),
                    ],
                    style={"display": "flex", "gap": "10px", "marginBottom": "10px"},
                ),

                # Segunda fila de tarjetas
                html.Div(
                    [
                        html.Div(
                            [
                                html.H4("Total muertes", style={"color": "#4d4545"}),
                                html.H3(
                                    id="total-muertes",
                                    style={"color": "#212121", "margin": 0},
                                ),
                            ],
                            style={
                                "backgroundColor": "#f5f5f5",
                                "padding": "10px",
                                "borderRadius": "10px",
                                "textAlign": "center",
                                "flex": "1",
                            },
                        ),
                        html.Div(
                            [
                                html.H4("Recuperados", style={"color": "#2e7d32"}),
                                html.H3(
                                    id="total-recuperados",
                                    style={"color": "#1b5e20", "margin": 0},
                                ),
                            ],
                            style={
                                "backgroundColor": "#e8f5e9",
                                "padding": "10px",
                                "borderRadius": "10px",
                                "textAlign": "center",
                                "flex": "1",
                            },
                        ),
                    ],
                    style={"display": "flex", "gap": "10px", "marginBottom": "14px"},
                ),

                dcc.Graph(
                    id="grafica-covid",
                    style={"height": "520px", "width": "100%"},
                ),
            ],
            className="content right",
        ),
    ],
    className="page-container",
)

# =========================
#   FUNCIONES API
# =========================
def obtener_datos_pais(pais: str):
    try:
        url = f"https://disease.sh/v3/covid-19/countries/{pais}"
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        print(f"Error al obtener datos del país: {e}")
        return None


def obtener_historico_pais(pais: str, dias):
    try:
        url = f"https://disease.sh/v3/covid-19/historical/{pais}"
        params = {"lastdays": dias}
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        print(f"Error al obtener histórico del país ({pais}): {e}")
        return None


# =========================
#   CALLBACK
# =========================
@callback(
    Output("total-casos", "children"),
    Output("casos-nuevos", "children"),
    Output("total-muertes", "children"),
    Output("total-recuperados", "children"),
    Output("grafica-covid", "figure"),
    Output("info-actualizado-covid", "children"),
    Input("btn-actualizar-covid", "n_clicks"),
    State("dropdown-pais", "value"),
    State("dropdown-dias-covid", "value"),
    prevent_initial_call=False,
)
def actualizar_dashboard_covid(n_clicks, pais, dias):
    # Llamadas a la API
    datos_actuales = obtener_datos_pais(pais)
    historico = obtener_historico_pais(pais, dias)

    # Si falla la API
    if not datos_actuales or not historico:
        fig = go.Figure()
        fig.add_annotation(
            text="Error al obtener datos",
            xref="paper",
            yref="paper",
            x=0.5,
            y=0.5,
            showarrow=False,
            font=dict(size=15, color="red"),
        )
        fig.update_layout(paper_bgcolor="lightcyan", plot_bgcolor="white")

        return "N/A", "N/A", "N/A", "N/A", fig, "No se pudieron actualizar los datos."

    # Datos actuales
    total_casos = datos_actuales.get("cases", 0)
    casos_hoy = datos_actuales.get("todayCases", 0)
    total_muertes = datos_actuales.get("deaths", 0)
    total_recuperados = datos_actuales.get("recovered", 0)

    total_casos_texto = formatear_numero(total_casos)
    casos_hoy_texto = formatear_numero(casos_hoy)
    total_muertes_texto = formatear_numero(total_muertes)
    total_recuperados_texto = formatear_numero(total_recuperados)

    # Histórico
    timeline = historico.get("timeline", {})
    casos_historicos = timeline.get("cases", {})
    muertes_historicas = timeline.get("deaths", {})

    fechas = list(casos_historicos.keys())
    valores_casos_acum = list(casos_historicos.values())
    valores_muertes_acum = list(muertes_historicas.values())

    if not fechas:
        fig = go.Figure()
        fig.add_annotation(
            text=f"No hay datos históricos para {pais}.",
            xref="paper",
            yref="paper",
            x=0.5,
            y=0.5,
            showarrow=False,
        )
        return (
            total_casos_texto,
            casos_hoy_texto,
            total_muertes_texto,
            total_recuperados_texto,
            fig,
            "Datos actuales cargados (sin histórico).",
        )

    # Convertir fechas a datetime
    fechas_dt = [datetime.strptime(fecha, "%m/%d/%y") for fecha in fechas]

    # Arrays acumulados
    valores_casos_acum = np.array(valores_casos_acum, dtype=float)
    valores_muertes_acum = np.array(valores_muertes_acum, dtype=float)

    # Si hay al menos 2 días, usamos diferencias (nuevos casos diarios)
    if len(fechas_dt) >= 2:
        nuevos_casos = np.diff(valores_casos_acum, prepend=valores_casos_acum[0])
        nuevas_muertes = np.diff(
            valores_muertes_acum, prepend=valores_muertes_acum[0]
        )

        # descartamos el primer día para evitar el salto artificial
        fechas_plot = fechas_dt[1:]
        nuevos_casos = nuevos_casos[1:]
        nuevas_muertes = nuevas_muertes[1:]
    else:
        # fallback raro: usamos acumulados directamente
        fechas_plot = fechas_dt
        nuevos_casos = valores_casos_acum
        nuevas_muertes = valores_muertes_acum

    # Rango del eje-Y adaptado y ticks razonables
    max_val = float(max(max(nuevos_casos), max(nuevas_muertes)))
    if max_val <= 0:
        max_val = 1.0
    top_y = ((max_val // 50_000) + 1) * 50_000  # múltiplos de 50k
    paso_y = max(10_000, top_y // 8)  # ~8 ticks

    # FIGURA
    fig = go.Figure()

    fig.add_trace(
        go.Scatter(
            x=fechas_plot,
            y=nuevos_casos,
            mode="lines",
            name="Nuevos casos diarios",
            line=dict(color="orange", width=2),
            fill="tozeroy",
            hovertemplate=(
                "Fecha: %{x|%d %b %Y}"
                "<br>Nuevos casos: %{y:,.0f}<extra></extra>"
            ),
        )
    )

    fig.add_trace(
        go.Scatter(
            x=fechas_plot,
            y=nuevas_muertes,
            mode="lines",
            name="Nuevas muertes diarias",
            line=dict(color="red", width=2),
            hovertemplate=(
                "Fecha: %{x|%d %b %Y}"
                "<br>Nuevas muertes: %{y:,.0f}<extra></extra>"
            ),
        )
    )

    fig.update_layout(
        title=f"Evolución diaria de casos y muertes en {pais}",
        xaxis_title="Fecha",
        yaxis_title="Número de personas",
        plot_bgcolor="white",
        paper_bgcolor="white",
        margin=dict(l=60, r=30, t=70, b=60),
        legend=dict(
            x=0.01,
            y=0.99,
            bgcolor="rgba(255,255,255,0.6)",
            bordercolor="rgba(0,0,0,0.1)",
            borderwidth=1,
        ),
        yaxis=dict(
            range=[0, top_y],
            dtick=paso_y,
            tickformat=",",
        ),
        xaxis=dict(
            tickformat="%b %d\n%Y",
            tickangle=0,
        ),
    )

    mensaje_actualizacion = f"Datos actualizados para {pais}."

    return (
        total_casos_texto,
        casos_hoy_texto,
        total_muertes_texto,
        total_recuperados_texto,
        fig,
        mensaje_actualizacion,
    )
