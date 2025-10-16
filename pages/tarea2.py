import dash
from dash import html, dcc, Input, Output, callback
import plotly.graph_objects as go
import numpy as np
import pandas as pd


def simulate_logistic_harvest(P0, r, K, H, t_max=120.0, dt=0.2):
    """
    Integra con RK4 y corta cuando P cae ~0 para evitar una meseta pegada al eje.
    Retorna arrays (t, P).
    """
    def f(_, P):
        return r*P*(1 - P/K) - H

    n = int(t_max/dt) + 1
    t = np.zeros(n)
    P = np.zeros(n)
    t[0] = 0.0
    P[0] = max(float(P0), 0.0)

    eps = 1e-6
    for i in range(n - 1):
        Pi = max(P[i], 0.0)

        k1 = f(t[i], Pi)
        k2 = f(t[i] + dt/2, Pi + dt*k1/2)
        k3 = f(t[i] + dt/2, Pi + dt*k2/2)
        k4 = f(t[i] + dt,   Pi + dt*k3)

        P_next = Pi + (dt/6)*(k1 + 2*k2 + 2*k3 + k4)
        t[i+1] = t[i] + dt
        P[i+1] = max(P_next, 0.0)

        if P[i+1] <= eps:
            P[i+1] = 0.0
            t = t[:i+2]
            P = P[:i+2]
            break

    return t, P


def build_figure(P0, r, K, H, t_max):
    dt = max(0.05, float(t_max) / 400.0)
    t, P = simulate_logistic_harvest(P0, r, K, H, t_max=float(t_max), dt=dt)

    # Línea continua P(t)
    tr_line = go.Scatter(
        x=t, y=P,
        mode='lines',
        line=dict(color='blue', width=3),
        name='P(t)',
        hovertemplate='t: %{x:.2f}<br>P(t): %{y:.2f}<extra></extra>'
    )
    step = max(1, len(t)//30)
    tr_mark = go.Scatter(
        x=t[::step], y=P[::step],
        mode='markers',
        marker=dict(color='green', symbol='circle', size=8),
        name='Muestras',
        hovertemplate='t: %{x:.2f}<br>P(t): %{y:.2f}<extra></extra>'
    )

    tr_K = go.Scatter(
        x=t, y=[K]*len(t),
        mode='lines',
        line=dict(dash='dash', color='red', width=2),
        name='Capacidad de carga K',
        hovertemplate='t: %{x:.2f}<br>K: %{y:.2f}<extra></extra>'
    )

    traces = [tr_line, tr_mark, tr_K]

    H_star = (r*K)/4.0 if (r > 0 and K > 0) else None
    if r > 0 and K > 0:
        disc = 1.0 - 4.0*H/(r*K)
        if disc >= 0:
            s = np.sqrt(disc)
            P_unstable = 0.5*K*(1 - s)
            P_stable   = 0.5*K*(1 + s)

            traces.append(go.Scatter(
                x=t, y=[P_stable]*len(t),
                mode='lines',
                line=dict(dash='dot', color='green', width=2),
                name='Equilibrio estable',
                hovertemplate='P*: %{y:.2f}<extra></extra>'
            ))
            traces.append(go.Scatter(
                x=t, y=[P_unstable]*len(t),
                mode='lines',
                line=dict(dash='dot', color='black', width=2),
                name='Equilibrio inestable',
                hovertemplate='P**: %{y:.2f}<extra></extra>'
            ))

    fig = go.Figure(data=traces)

    extinct = (len(P) >= 2 and P[-1] == 0.0 and H_star is not None and H > H_star)
    if extinct:
        t_ext = t[-1]
        fig.add_vline(
            x=t_ext, line_width=2, line_dash='dash', line_color='purple',
            annotation_text='Extinción', annotation_position='top'
        )
    ymax = max(K, P.max()) * 1.10 if len(P) else K*1.10
    fig.update_layout(
        title=dict(
            text='Logístico con cosecha',
            font=dict(family='Playfair Display', size=20, color='purple'),
            x=0.5, y=0.995, xanchor='center', yanchor='top', pad=dict(t=6, b=0)
        ),
        xaxis_title='Tiempo (t)',
        yaxis_title='Tamaño poblacional / biomasa P(t)',
        margin=dict(l=60, r=40, t=110, b=90),
        paper_bgcolor='lightblue',
        plot_bgcolor='grey',
        font=dict(family='Playfair Display, serif', size=15, color='black'),
        legend=dict(
            orientation='h',
            x=0.5, y=1.08, xanchor='center', yanchor='bottom',
            bgcolor='rgba(255,255,255,0.70)', bordercolor='rgba(0,0,0,0.2)', borderwidth=1,
            itemsizing='constant', itemwidth=60
        ),
        uniformtext_minsize=12, uniformtext_mode='hide'
    )
    fig.update_xaxes(
        range=[0, float(t_max)],  
        showgrid=True, gridwidth=1, gridcolor='lightpink',
        zeroline=True, zerolinewidth=2, zerolinecolor='blue',
        showline=True, linecolor='black', linewidth=2, mirror=True,
        automargin=True, title_standoff=10, ticklabelposition='outside'
    )
    fig.update_yaxes(
        range=[0, ymax],
        showgrid=True, gridwidth=1, gridcolor='lightpink',
        zeroline=True, zerolinewidth=2, zerolinecolor='blue',
        showline=True, linecolor='black', linewidth=2, mirror=True,
        automargin=True, title_standoff=10, ticklabelposition='outside'
    )

    return fig, H_star

#######################################################

dash.register_page(__name__, path='/pagina3', name='Pagina 3')

layout = html.Div(children=[
    html.Div(children=[
        html.H2("Crecimiento logístico con cosecha", className='title'),
        dcc.Markdown(r"""
Se considera el modelo logístico con capacidad de carga $K$ y una extracción constante $H\ge 0$:
$$
\frac{dP}{dt}=r\,P\left(1-\frac{P}{K}\right)-H,
$$
donde $P(t)$ denota el tamaño poblacional (o biomasa), $r>0$ la tasa intrínseca de crecimiento y $K>0$ la capacidad de carga.

Los puntos de equilibrio positivos satisfacen $rP\!\left(1-\frac{P}{K}\right)-H=0$, de donde
$$
P^*=\frac{K}{2}\left(1\pm\sqrt{1-\frac{4H}{rK}}\right),
$$
que existen si y solo si $H\le H^*=\frac{rK}{4}$. Si $H<H^*$, el equilibrio mayor es estable y el menor es inestable; si $H=H^*$, hay un único equilibrio en $P=K/2$; si $H>H^*$, no existe equilibrio positivo y la población colapsa.
""", mathjax=True),
    ], className="content left"),

    html.Div(children=[
        html.H2("Parámetros y gráfica dinámica", className='title'),

        html.Div([
            html.Label("r (tasa intrínseca)"),
            dcc.Slider(id='p3-r', min=0.005, max=0.2, step=0.005, value=0.06,
                       marks={0.005:'0.005', 0.05:'0.05', 0.1:'0.10', 0.15:'0.15', 0.2:'0.20'}),

            html.Label("K (capacidad de carga)"),
            dcc.Slider(id='p3-K', min=50, max=500, step=10, value=150,
                       marks={50:'50', 150:'150', 300:'300', 500:'500'}),

            html.Label("H (cosecha constante)"),
            dcc.Slider(id='p3-H', min=0.0, max=50.0, step=0.5, value=5.0,
                       marks={0:'0', 10:'10', 20:'20', 30:'30', 40:'40', 50:'50'}),

            html.Label("P₀ (población inicial)"),
            dcc.Slider(id='p3-P0', min=0, max=300, step=1, value=80,
                       marks={0:'0', 50:'50', 100:'100', 150:'150', 200:'200', 300:'300'}),

            html.Label("Horizonte temporal (t máx)"),
            dcc.Slider(
                id='p3-T',
                min=1, max=40, step=1, value=20,
                marks={1:'1', 5:'5', 10:'10', 15:'15', 20:'20', 25:'25', 30:'30', 35:'35', 40:'40'}
            ),
        ], style={'padding':'6px 0', 'display':'grid', 'gap':'8px'}),

        html.Div(id='p3-msy', style={'margin':'6px 0 10px 0'}),
        dcc.Graph(id='p3-fig', style={'height':'420px', 'width':'100%'})
    ], className="content right")
], className="page-container")

@callback(
    Output('p3-fig', 'figure'),
    Output('p3-msy', 'children'),
    Input('p3-r', 'value'),
    Input('p3-K', 'value'),
    Input('p3-H', 'value'),
    Input('p3-P0', 'value'),
    Input('p3-T', 'value'),
)
def update_pagina3(r, K, H, P0, T):
    r = float(r); K = float(K); H = float(H); P0 = float(P0); T = float(T)
    fig, H_star = build_figure(P0, r, K, H, T)
    if r > 0 and K > 0:
        regime = "sostenible (H < H*)" if H < (r*K)/4 else ("crítico (H ≈ H*)" if abs(H - (r*K)/4) < 1e-9 else "colapso (H > H*)")
        txt = f"H* = rK/4 = {H_star:.4f}. Régimen: {regime}"
    else:
        txt = "Parámetros inválidos: r y K deben ser positivos."
    return fig, txt
