import dash
from dash import html, dcc, Input, Output, callback

app = dash.Dash(__name__, use_pages=True, suppress_callback_exceptions=True)

app.layout = html.Div([
    html.H1("Técnicas de modelamiento matemático", className='app-header'),

    # Necesario para conocer la ruta actual y resaltar el link activo
    dcc.Location(id='url'),

    html.Div([
        # Aquí inyectaremos los links vía callback para poder marcar el activo
        html.Div(id='nav-links', className='nav-links')
    ], className='navigation'),

    dash.page_container
], className='app-container')


@callback(Output('nav-links', 'children'),
          Input('url', 'pathname'))
def render_nav(pathname):
    # Ordena las páginas por ruta para que la barra sea estable
    pages = sorted(dash.page_registry.values(), key=lambda p: p['relative_path'])
    items = []
    for page in pages:
        is_active = (page['relative_path'] == pathname)
        cls = 'nav-link' + (' active' if is_active else '')
        items.append(
            html.Div(
                dcc.Link(page['name'], href=page['relative_path'], className=cls)
            )
        )
    return items


if __name__ == '__main__':
    app.run(debug=True)
