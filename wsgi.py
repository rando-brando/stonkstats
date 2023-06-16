from dash import Dash, dcc, html, Output, Input, State, ClientsideFunction, ALL, Patch
import dash_bootstrap_components as dbc
import plotly.graph_objs as go
from stonkly.data.fmp import FMP
import stonkly.dashboard.layouts as sdl
import pandas as pd
import os
import json
import asyncio

FMP_API_KEY = os.getenv('FMP_API_KEY')
fmp = FMP(FMP_API_KEY)

#symbols = fmp.stock_screener({'exchange': 'NYSE,AMEX,NASDAQ'})
symbols = json.dumps([
    {"symbol": "AAPL", "companyName": "Apple", "exchangeShortName": "NASDAQ"},
    {"symbol": "MSFT", "companyName": "Microsoft", "exchangeShortName": "NASDAQ"},
    {"symbol": "AMZN", "companyName": "Amazon", "exchangeShortName": "NASDAQ"}
])

app = Dash(__name__, external_stylesheets=[dbc.themes.SLATE])

app.layout = html.Div(
    id='app-body',
    className='app-body dbc',
    children=[
        html.H1('Stonkly'),
        html.Div(
            id='search-container',
            className='search-container',
            children=[
                dcc.Store(
                    id='search-options',
                    storage_type='memory',
                    data=symbols
                ),
                dcc.Store(
                    id='selected-option',
                    storage_type='memory'
                ),
                dbc.Input(
                    id='search-input',
                    type='search',
                    placeholder='Search for a stock...',
                    maxlength=100,
                    autofocus=True
                ),
                dbc.Table(
                    id='search-table',
                    className='search-table',
                    color='light',
                    hover=True,
                    responsive=True,
                    children=html.Tbody(id='search-body')
                )
            ]
        ),
        html.Div(
            id='content-container',
            children=[
                dcc.Store(
                    id='chart-data',
                    storage_type='memory'
                ),
                dcc.Store(
                    id='stats-data',
                    storage_type='memory'
                ),
                dcc.Store(
                    id='screener-data',
                    storage_type='memory'
                ),
                dbc.Tabs(
                    id='content-tabs',
                    active_tab='chart-tab',
                    children=[
                        dbc.Tab(tab_id='chart-tab', label='Chart'),
                        dbc.Tab(tab_id='stats-tab', label='Stats'),
                        dbc.Tab(tab_id='screener-tab', label='Screener')
                    ],
                ),
                html.Div(id='tab-content')
            ]
        )
    ]
)

app.clientside_callback(
    ClientsideFunction(
        namespace='clientside',
        function_name='suggest_options'
    ),
    Output('search-body', 'children'),
    Input('search-input', 'value'),
    State('search-options', 'data')
)

app.clientside_callback(
    ClientsideFunction(
        namespace='clientside',
        function_name='select_option'
    ),
    Output('selected-option', 'data'),
    Output('search-input', 'value'),
    Input({'index': ALL, 'type': 'search-row'}, 'n_clicks'),
    State({'index': ALL, 'type': 'search-row'}, 'children')
)

@app.callback(
    Output('chart-data', 'data'),
    Output('stats-data', 'data'),
    Output('screener-data', 'data'),
    Input('selected-option', 'data')
)
def update_data(symbol):
    chart_data = fmp.technical_chart(symbol)
    stats_data = fmp.key_metrics(symbol)
    screener_data = fmp.company_profile(symbol)
    return [chart_data, stats_data, screener_data]

@app.callback(
    Output('tab-content', 'children'),
    Input('content-tabs', 'active_tab'),
    Input('chart-data', 'data'),
    Input('stats-data', 'data'),
    Input('screener-data', 'data')
)
def update_content(tab, chart, stats, screener):
    if (tab == 'chart-tab') and (chart is not None):
        df = pd.DataFrame(chart)
        component = dcc.Graph(
            figure=go.Figure(
                data=go.Scatter(x=df.close, y=df.date),
                layout=sdl.stock_chart_layout
            )
        )
    elif (tab == 'stats-tab') and (stats is not None):
        df = pd.DataFrame.(stats)
        component = dbc.Table.from_dataframe(df=df)
    elif (tab == 'screener-tab') and (screener is not None):
        df = pd.DataFrame(screener)
        component = dbc.Table.from_dataframe(df=df)
    else:
        component = dcc.Graph(
            figure=go.Figure(
                data=go.Bar(x=['a', 'b', 'c', 'd'], y=[1, 2, 3, 4]),
                layout=sdl.stock_chart_layout
            )
        )
    return component

if __name__ == '__main__':
    app.run_server(debug=True)
