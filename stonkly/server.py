from flask import Flask
from dash import Dash
import dash_bootstrap_components as dbc

server = Flask('stonkly')
app = Dash(
    server=server,
    prevent_initial_callbacks=True,
    suppress_callback_exceptions=False,
    external_stylesheets=[dbc.themes.SLATE]
)
