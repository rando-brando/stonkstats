from dash import dcc, html
import dash_bootstrap_components as dbc


class Content:
    def load(self):
        div = html.Div(
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
                    id='estimates-data',
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
        return div
