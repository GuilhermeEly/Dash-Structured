import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output

from app import app
from apps import app1, app2, app3


app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    html.Div(id='page-content')
])

index_page = html.Div([
    dcc.Link('Ir para app 1', href='/apps/app1'),
    html.Br(),
    dcc.Link('Ir para app 2', href='/apps/app2'),
    html.Br(),
    dcc.Link('Ir para app 3', href='/apps/app3'),
])


@app.callback(Output('page-content', 'children'),
              [Input('url', 'pathname')])
def display_page(pathname):
    if pathname == '/apps/app1':
        return app1.layout
    elif pathname == '/apps/app2':
        return app2.layout
    elif pathname == '/apps/app3':
        return app3.layout
    else:
        return index_page

if __name__ == '__main__':
    app.run_server(debug=True)
