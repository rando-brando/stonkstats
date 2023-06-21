from dash import Input, Output, State
from stonkly.server import app
from stonkly.components.graph import StonkGraph


@app.callback(
    Output('tab-content', 'children'),
    Input('symbol-data', 'data')
)
def update_content(data):
    if data:
        graph = StonkGraph(data)
        return graph.load()
