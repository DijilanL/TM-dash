import dash
from dash import html, dcc
import plotly.graph_objects as go
import numpy as np
import pandas as pd

#######################################################

P0=100 #Poblacion inicial
r=0.03  #Tasa de crecimiento
t= np.linspace(0,100,10) #Tiempo
P= P0* np.exp(r*t) # Funcion de crecimiento exponencial

# Creamos un scatter plot
trace =go.Scatter(
    x=t,
    y=P,
    mode='lines+markers',
    line=dict(
        dash='dot',
        color='green',
        width=2
    ),
    marker=dict(
        color='orange',
        symbol='square',
        size=8 
    ),
    name='P(t) = P0 * e^(rt)',  
    hovertemplate='t: %{x:.3f}<br>P(t): %{y:.3f}<extra></extra>'
)

#Creamos la figura
fig=go.Figure(data=trace)

fig.update_layout(
    title=dict(
        text='<b>Crecimiento de población</b>',
        font=dict(
            family='Playfair Display',
            size=20,
            color='purple'
        ),
        x=0.5,
        y=0.93
    ),
    xaxis_title='Tiempo (t)',
    yaxis_title='Población P(t)',
    margin=dict(l=40, r=40, t=50, b=40),
    paper_bgcolor='lightblue',
    plot_bgcolor='grey',
    font=dict(
        family='Playfair Display',
        size=15,
        color='black'
    )   

)

fig.update_xaxes(
    showgrid=True, gridwidth=1, gridcolor='lightpink',
    zeroline=True, zerolinewidth=2, zerolinecolor='blue',
    showline=True, linecolor='black', linewidth=2, mirror=True,
)

fig.update_yaxes(
    showgrid=True, gridwidth=1, gridcolor='lightpink',
    zeroline=True, zerolinewidth=2, zerolinecolor='blue',
    showline=True, linecolor='black', linewidth=2, mirror=True,
)

#######################################################

dash.register_page(__name__, path='/pagina1', name='Pagina 1')

#layout = html.Div([
#        html.H1("Bienvenido a la página 1"),
#])

layout = html.Div(children=[
        #Contenedor izquierdo
        html.Div(children=[
            html.H2("Crecimiento de la población y capacidad de carga", className='title'),
            dcc.Markdown("""
        Para modelar el crecimiento de la población mediante una ecuación diferencial, primero 
        tenemos que introducir algunas variables y términos relevantes. La variable $t$.
        representará el tiempo. Las unidades de tiempo pueden ser horas, días, semanas, 
        meses o incluso años. Cualquier problema dado debe especificar las unidades utilizadas 
        en ese problema en particular. La variable $P$
        representará a la población. Como la población varía con el tiempo, se entiende que es 
        una función del tiempo. Por lo tanto, utilizamos la notación $P(t)$
        para la población en función del tiempo. Si $P(t)$
        es una función diferenciable, entonces la primera derivada $\\dfrac{dP}{dt}$
        representa la tasa instantánea de cambio de la población en función del tiempo.
        """, mathjax=True),
        dcc.Markdown("""
        Un ejemplo de función de crecimiento exponencial es  $P(t)=P_0e^{rt}$.
        En esta función,  $P(t)$
        representa la población en el momento  $t$, $P_0$
        representa la población inicial (población en el tiempo  $t=0$),
        y la constante  $r>0$
        se denomina tasa de crecimiento. Aquí  $P_0=100$ y  $r=0,03$.
    """, mathjax=True),
        ], className="content left"),

        
        #Contenedor derecho
        html.Div(children=[
            html.H2("Gráfica", className='title'),
            
            dcc.Graph(
                figure=fig, 
                style={'height': '350px', 'width': '100%'},
            )

        ], className="content right")
], className="page-container")