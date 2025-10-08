import dash
from dash import html, dcc

dash.register_page(__name__, path='/', name='Inicio')

layout = html.Div(children=[

    # Contenedor izquierdo
    html.Div(children=[
        html.H2("Sobre mí", className='title'),
        dcc.Markdown(r"""
Hola, soy Dylan Ricardo Lúcar Jaimes. Tengo 23 años y curso el 6.º ciclo de la carrera de 
Computación Científica en la Universidad Nacional Mayor de San Marcos. 
Soy titulado técnico del Instituto de Educación Superior Tecnológico Público Argentina en 
Computación e Informática.

Actualmente soy Director de Eventos del IEEE CIS UNMSM, donde impulsamos proyectos de 
inteligencia computacional y divulgación tecnológica dentro de la universidad.

Descubrí mis gustos por la computación desde niño: con una PC antigua y sin hermanos, 
pasaba horas explorando las funcionalidades del sistema operativo y buscando en internet cómo aprender más sobre las herramientas de Windows. 
Desde entonces me apasionan el modelamiento matemático, el desarrollo en Python 
(Dash/Django), la visualización de datos y el aprendizaje automático.

Fuera del teclado, soy amante de los videojuegos y del arte en general: me atraen el diseño, 
la música y las experiencias interactivas. También disfruto del básquet y la natación; 
me identifico con el trabajo en equipo y la disciplina que ambos deportes exigen.

**Objetivo personal:** Unir matemática, ciencia de datos y creatividad para construir soluciones 
con impacto positivo en mi comunidad universitaria y local.
""", mathjax=True),
    ], className="content left"),

    # Contenedor derecho
    html.Div(children=[
        html.H2("Mi apariencia", className='title'),
        html.Div([
            html.Img(
                src='/assets/images/yo.jpeg',
                alt='Foto de Dylan Ricardo Lúcar Jaimes',
                className='profile-photo'
                
            ),
            html.Div([
                html.H4("Dylan Ricardo Lúcar Jaimes"),
                html.P("'El arte es lo único que puede cambiar al ser humano'"),
            ], className='profile-caption')
        ], className='profile-card')
    ], className="content right"),

], className="page-container")
