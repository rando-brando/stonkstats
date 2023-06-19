from dash import dcc, html
import dash_bootstrap_components as dbc
from stonkly.config import FMP_API_KEY
from stonkly.data.fmp import FMP
import json


def load_search():
    fmp = FMP(FMP_API_KEY)
    symbols = fmp.stock_screener({'exchange': 'NYSE,AMEX,NASDAQ'})
    symbols.sort_values(['symbol', 'companyName'], ignore_index=True, inplace=True)

    div = html.Div(
        id='search-container',
        className='search-container',
        children=[
            dcc.Store(
                id='search-options',
                storage_type='memory',
                data=json.dumps(symbols)
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
