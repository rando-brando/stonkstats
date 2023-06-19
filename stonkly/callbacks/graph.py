from dash import Input, Output, State
from stonkly.server import app
from stonkly.components.graph import StonkGraph


@app.callback(
    Output('tab-content', 'children'),
    Input('price-data', 'modified_timestamp'),
    State('price-data', 'data'),
    State('earnings-data', 'data'),
    State('estimates-data', 'data')
)
def update_content(_, price, earnings, estimates):
    if price:
        graph = StonkGraph(price, earnings, estimates)
        return graph.load_graph()
