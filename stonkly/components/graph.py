from dash import dcc


def load_graph(fig):
    graph = dcc.Graph(
        className='stonk-graph',
        figure=fig,
        config={
                'displayModeBar': False,
                'showAxisDragHandles': False
            }
        )
    return graph
