from .server import app
from dash import html
from . import components
from . import callbacks

app.layout = html.Div(
    id='app-body',
    className='app-body dbc',
    children=[
        components.load_title(),
        components.load_search(),
        components.load_content()
    ]
)
