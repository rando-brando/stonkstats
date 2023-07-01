from dash import dcc, html
import dash_bootstrap_components as dbc
from stonkly.data.fmp import FMP
import pandas as pd
import os


class Search:
    def load(self):
        #FMP_API_KEY = os.getenv('FMP_API_KEY')
        #fmp = FMP(FMP_API_KEY)
        #symbols = fmp.stock_screener({'exchange': 'NYSE,AMEX,NASDAQ'})
        symbols = pd.read_json('stonkly/data/list.json')
        symbols = symbols[
            (symbols.exchangeShortName.isin(['NYSE', 'NASDAQ', 'AMEX'])) &
            (symbols.type.isin(['etf', 'stock'])) &
            (symbols.name != '') &
            (symbols.name.notna()) &
            (~symbols.symbol.str.contains('-'))
        ].sort_values('symbol').to_json(orient='records')

        div = html.Div(
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
        )

        return div
