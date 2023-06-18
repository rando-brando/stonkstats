from dash import Dash, dcc, html, Output, Input, State
from dash import ClientsideFunction, ALL
import dash_bootstrap_components as dbc
import stonkly.data.prep as prep
import yahooquery as yq

fmp = prep.fmp()
symbols = prep.symbols()

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
                    id='price-data',
                    storage_type='memory'
                ),
                dcc.Store(
                    id='earnings-data',
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
                    active_tab='graph-tab',
                    children=[
                        dbc.Tab(tab_id='graph-tab', label='Graph'),
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
    Output('price-data', 'data'),
    Output('earnings-data', 'data'),
    Input('selected-option', 'data')
)
def update_data(symbol):
    price = fmp.technical_chart(symbol)
    earnings = fmp.earnings_surprises(symbol)
    return [price, earnings]


@app.callback(
    Output('tab-content', 'children'),
    Input('price-data', 'modified_timestamp'),
    State('price-data', 'data'),
    State('earnings-data', 'data')
)
def update_content(_, price_data, earnings_data):
    if price_data:
        fig = prep.stonk_graph(price_data, earnings_data)
        graph = dcc.Graph(
            className='stonk-graph',
            figure=fig,
            config={'displayModeBar': False}
        )
        return graph


if __name__ == '__main__':
    app.run_server(debug=True)
