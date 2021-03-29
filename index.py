import dash
external_scripts = ['https://cdn.plot.ly/plotly-locale-pt-br-latest.js']

app = dash.Dash(__name__)
app.scripts.config.serve_locally = False
server = app.server

import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State

from apps.controllers.product_fpy.general_fpy import get_fpy_geral
from apps.controllers.product_fpy.group_by_date import get_timeseries_by_PA
from apps.controllers.product_fpy.causes import get_causes_by_PA
from apps.controllers.product_fpy.fpy_by_product import get_fpy_by_Date

import plotly.express as px
import pandas as pd

#from app import app
#from apps import FPY_DASHBOARD

#import dash

#app = dash.Dash(__name__)
#app.scripts.config.serve_locally = False
#server = app.server

app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    html.Div(id='page-content')
])

index_page = html.Div([
    dcc.Link('Ir para app FPY DASHBOARD', href='/apps/FPY_DASHBOARD.py')
])


@app.callback(Output('page-content', 'children'),
              [Input('url', 'pathname')])
def display_page(pathname):
    if pathname == '/apps/FPY_DASHBOARD.py':
        return FPY_DASHBOARD.layout
    else:
        return index_page

if __name__ == '__main__':
    #Para rodar em Desenvolvimento
    #app.run_server(debug=True)

    #Para rodar em LAN
    app.run_server(debug=False, processes=10, port=8082, host='0.0.0.0')
from apps import FPY_DASHBOARD

@app.callback(
    Output('crossfilter-indicator-scatter-fpy', 'figure'),
    [Input('submit-button-state', 'n_clicks')],
    [State('crossfilter-yaxis-type-fpy', 'value'),
     State('date-picker-range', 'start_date'),
     State('date-picker-range', 'end_date'),
     State('PA-Selection', 'value'),
     State('fpy-filter-low', 'value'),
     State('fpy-filter-high', 'value')])
def update_table(n_clicks,Filter,start_date,end_date,PA_selection,limit_Low,limit_High):

    if float(limit_High)<float(limit_Low):
        limit_High = 100
        limit_Low = 0

    if limit_High==None or str(limit_High).isdigit()==False:
        limit_High = 100
    if limit_Low==None or str(limit_Low).isdigit()==False:
        limit_Low = 0

    if Filter!= 'not selected' and start_date!=None and end_date!=None:

        data = get_fpy_by_Date(start_date, end_date, Filter, PA_selection, limit_High, limit_Low)

        fig = px.bar(data, x="PA", y="fpy", title='First Pass Yield',hover_name="NOME", hover_data=["Aprovadas", "Reprovadas", "Produzido"])
        fig.update_xaxes(type='category')
        fig.update_layout(
            hovermode="x",
            clickmode='event+select',
            font=dict(
                family="Arial",
                size=20
            ),
            margin={'l': 0, 'b': 0, 't': 50, 'r': 0},
            hoverlabel=dict(
                bgcolor="white",
                font_size=20,
                font_family="Rockwell"
            )
        )
        fig.update_layout(
            hovermode="closest"
        )
        return fig

    else:
        return dash.no_update

@app.callback(
    Output('fpy-causes', 'figure'),
    [Input('crossfilter-indicator-scatter-fpy', 'clickData')],
    [State('date-picker-range', 'start_date'),
     State('date-picker-range', 'end_date')])
def update_causes(clickData, start_date, end_date):

    if clickData is not None:
        PA_Selected = clickData['points'][0]['x']
        Total_Rep = clickData['points'][0]['customdata']
    else:
        PA_Selected = "not selected"

    if PA_Selected != "not selected":

        df_causes= get_causes_by_PA(start_date, end_date, PA_Selected)

        Total = df_causes['Reprovações'].sum()

        if (Total_Rep[1]-Total) > 0:
            df_causes.loc[-1] = ['Não iniciou teste', 'R', Total_Rep[1]-Total]

            df_causes = df_causes.sort_values(by=['Reprovações'], ascending=False)


        title = '<b>{} - Causas</b>'.format(PA_Selected)

        fig = px.bar(df_causes, x="STEP", y="Reprovações", title=title,hover_name="STEP")
        fig.update_xaxes(type='category')

        fig.update_layout(
            font=dict(
                family="Arial",
                size=20
            ),
            margin={'t': 50},
            hoverlabel=dict(
                bgcolor="white",
                font_size=20,
                font_family="Rockwell"
            )
        )

        return fig
    else:
        return dash.no_update

@app.callback(
    Output('time-series-fpy', 'figure'),
    [Input('crossfilter-indicator-scatter-fpy', 'clickData')],
    [State('date-picker-range', 'start_date'),
     State('date-picker-range', 'end_date'),
     State('crossfilter-yaxis-type-fpy', 'value')])
def update_x_timeseries(clickData, start_date, end_date, Filter):

    if clickData is not None:
        PA_Selected = clickData['points'][0]['x']
    else:
        PA_Selected = "not selected"

    if PA_Selected != "not selected":

        df_timeseries= get_timeseries_by_PA(start_date, end_date, PA_Selected, Filter)

        title = '<b>{} - {}</b>'.format(PA_Selected, Filter)
        if Filter == 'Diario':
            print(len(df_timeseries.index))
            if(len(df_timeseries.index)>3):
                dt_all = pd.date_range(start=df_timeseries['DateTime'].iloc[0],end=df_timeseries['DateTime'].iloc[-1])
                dt_obs = [d.strftime("%Y-%m-%d") for d in df_timeseries['DateTime']]
                dt_breaks = [d for d in dt_all.strftime("%Y-%m-%d").tolist() if not d in dt_obs]
                fig = px.bar(df_timeseries, x="DateTime", y="fpy", title=title, hover_name="fpy", hover_data=["Aprovadas", "Reprovadas", "Produzido"])
                fig.update_xaxes(
                    rangebreaks=[dict(values=dt_breaks)] # hide dates with no values
                )
                # df_timeseries['Width'] = 0.1
                #fig.update_traces(width = df_timeseries['Width'].to_list())
                # print(df_timeseries['Width'].to_numpy())
                # print(df_timeseries)
                # print(dt_breaks)
                # print(df_timeseries['Width'].to_list())
            else:
                fig = px.bar(df_timeseries, x="DateTime", y="fpy", title=title, hover_name="fpy", hover_data=["Aprovadas", "Reprovadas", "Produzido"])

        else:
            fig = px.bar(df_timeseries, x="DateTime", y="fpy", title=title, hover_name="fpy", hover_data=["Aprovadas", "Reprovadas", "Produzido"])
            fig.update_layout(xaxis_type='category')

        fig.update_layout(
            font=dict(
                family="Arial",
                size=20
            ),
            margin={'t': 50},
            hoverlabel=dict(
                bgcolor="white",
                font_size=20,
                font_family="Rockwell"
            )
        )

        return fig

    else:
        return dash.no_update

@app.callback(
    Output('output-fpy-button', 'children'),
    [Input('submit-button-state', 'n_clicks')],
    [State('date-picker-range', 'start_date'),
     State('date-picker-range', 'end_date'),
     State('PA-Selection', 'value'),
     State('fpy-filter-low', 'value'),
     State('fpy-filter-high', 'value')])
def update_total_fpy(n_clicks,start_date,end_date,PA_selection,limit_Low,limit_High):

    if float(limit_High)<float(limit_Low):
        limit_High = 100
        limit_Low = 0

    if limit_High==None or str(limit_High).isdigit()==False:
        limit_High = 100

    if limit_Low==None or str(limit_Low).isdigit()==False:
        limit_Low = 0

    if start_date!=None and end_date!=None:

        data = get_fpy_geral(start_date, end_date, PA_selection, limit_High, limit_Low)

        return '{}%'.format(data)
    else:
        return ''
