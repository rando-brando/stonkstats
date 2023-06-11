
import dash_bootstrap_components as dbc
from dash import html

search_bar = dbc.Input(
    id='search-input',
    type='search',
    placeholder='Search for a stock...',
    autofocus=True
)

search_body = html.Tbody(
    id='search-body'
)

search_table = dbc.Table(
    id='search-table',
    color='primary',
    hover=True,
    responsive=True,
    children=search_body
)
