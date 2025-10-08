import dash
from dash import html,dcc

app=dash.Dash(__name__, use_pages=True)

app.layout= html.Div([
    html.H1("Técnicas de modelamiento matemático", className='app-header'),
    html.Div([
        html.Div([
        html.Div(
            dcc.Link(f"{page['name']}",href=page['relative_path'], className='nav-link'),
        ) for page in dash.page_registry.values()
    ],className='nav-links')
    ], className='navigation'),
    dash.page_container

], className='app-container')

if __name__ == '__main__':
    app.run(debug=True) 