from .server import app, server
from dash import html
from . import components
from . import callbacks

app.layout = html.Div(
    id='app-body',
    className='app-body dbc',
    children=[
        components.title.load(),
        components.search.load(),
        components.content.load()
    ]
)
