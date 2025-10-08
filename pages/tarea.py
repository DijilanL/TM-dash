import dash
from dash import html, dcc
import plotly.graph_objects as go
import numpy as np
import pandas as pd

#######################################################
# Modelo logístico con capacidad de carga

# Parámetros 
P0 = 50     # Población inicial 
r  = 0.03   # Tasa intrínseca de crecimiento
K  = 150    # Capacidad de carga

t = np.linspace(0, 200, 15)  
P = K / (1 + ((K - P0) / P0) * np.exp(-r * t))

# Punto de inflexión 
t_inf = (1 / r) * np.log((K - P0) / P0) 
P_inf = K / 2

# Trazas
trace_log = go.Scatter(
    x=t, y=P,
    mode='lines+markers',
    line=dict(
        dash='solid',
        color='blue',
        width=3
    ),
    marker=dict(
        color='green',
        symbol='circle',
        size=8
    ),
    name='Ecuación Logística',
    hovertemplate='t: %{x:.2f}<br>P(t): %{y:.2f}<extra></extra>'
)

trace_K = go.Scatter(
    x=t, y=[K]*len(t),
    mode='lines',
    line=dict(
        dash='dash',
        color='red',
        width=2
    ),
    name='Capacidad de carga (K)',
    hovertemplate='t: %{x:.2f}<br>K: %{y:.2f}<extra></extra>'
)


traces = [trace_log, trace_K]
if 0 <= t_inf <= t.max():
    trace_inf = go.Scatter(
        x=[t_inf], y=[P_inf],
        mode='markers',
        marker=dict(symbol='x', size=10, line=dict(width=2), color='black'),
        name='Inflexión (P=K/2)',
        hovertemplate='t*: %{x:.2f}<br>P(t*)=K/2=%{y:.2f}<extra></extra>'
    )
    traces.append(trace_inf)

fig = go.Figure(data=traces)

fig.update_layout(
    title=dict(
        text='<b>Modelo logístico con capacidad de carga</b>',
        font=dict(family='Playfair Display', size=20, color='purple'),
        x=0.5, y=0.995,                 
        xanchor='center', yanchor='top',
        pad=dict(t=6, b=0)
    ),
    xaxis_title='Tiempo (t)',
    yaxis_title='Población P(t)',
    margin=dict(l=60, r=40, t=110, b=90), 
    paper_bgcolor='lightblue',
    plot_bgcolor='grey',
    font=dict(family='Playfair Display, serif', size=15, color='black'),
    legend=dict(
        orientation='h',
        x=0.5, y=1.08,                   
        xanchor='center', yanchor='bottom',
        bgcolor='rgba(255,255,255,0.70)',  
        bordercolor='rgba(0,0,0,0.2)',
        borderwidth=1,
        itemsizing='constant',
        itemwidth=40
    ),
    uniformtext_minsize=12,
    uniformtext_mode='hide'
)

fig.update_xaxes(
    showgrid=True, gridwidth=1, gridcolor='lightpink',
    zeroline=True, zerolinewidth=2, zerolinecolor='blue',
    showline=True, linecolor='black', linewidth=2, mirror=True,
    automargin=True,
    title_standoff=10,                   
    ticklabelposition='outside'
)

fig.update_yaxes(
    showgrid=True, gridwidth=1, gridcolor='lightpink',
    zeroline=True, zerolinewidth=2, zerolinecolor='blue',
    showline=True, linecolor='black', linewidth=2, mirror=True,
    automargin=True,
    title_standoff=10,
    ticklabelposition='outside',
    rangemode='tozero'
)


#######################################################

dash.register_page(__name__, path='/pagina2', name='Pagina 2')

layout = html.Div(children=[
# Contenedor izquierdo
html.Div(children=[
    html.H2("Crecimiento logístico y capacidad de carga", className='title'),

    dcc.Markdown(r"""
Para incorporar la capacidad de carga en el crecimiento poblacional, se usa el modelo logístico. 
Sea $P(t)$ la población en el tiempo $t$, $r>0$ la tasa intrínseca de crecimiento y $K>0$ la 
capacidad de carga (población máxima sostenible por el ambiente). El modelo queda dado por la 
ecuación diferencial

$$
\frac{dP}{dt}=r\,P\!\left(1-\frac{P}{K}\right).
$$

Cuando $P$ es pequeña comparada con $K$, el término $\left(1-\frac{P}{K}\right)\approx 1$ y el crecimiento
es casi exponencial. Al acercarse $P$ a $K$, el factor $\left(1-\frac{P}{K}\right)$ reduce la tasa de 
cambio hasta hacerla nula en el equilibrio $P=K$. Así, $P=0$ y $P=K$ son puntos de equilibrio del sistema; 
si $r>0$, $P=0$ es inestable y $P=K$ es estable.
""", mathjax=True),

    dcc.Markdown(r"""
La solución explícita del modelo logístico con condición inicial $P(0)=P_0$ es

$$
P(t)=\frac{K}{\,1+\left(\frac{K-P_0}{P_0}\right)e^{-rt}}\;.
$$

En el ejemplo usaremos $P_0=50$, $r=0{,}03$ y $K=150$. Con estos valores la población crece de forma 
sigmoidal: la máxima tasa de crecimiento ocurre alrededor de $P=K/2$ (punto de inflexión) y, 
a largo plazo,
$$
\lim_{t\to\infty}P(t)=K.
$$
A la derecha se muestra la curva logística y la línea horizontal que representa la capacidad de carga $K$.
""", mathjax=True),
], className="content left"),

    # Contenedor derecho
    html.Div(children=[
        html.H2("Gráfica", className='title'),
        dcc.Graph(
            figure=fig,
            style={'height': '420px', 'width': '100%'},
        )
    ], className="content right")
], className="page-container")
