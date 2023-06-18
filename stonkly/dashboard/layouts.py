date_selector = [
    {
        'count': i,
        'label': f'{i}Y',
        'step': 'year',
        'stepmode': 'backward'
    }
    for i in range(20, 0, -1)
]
date_selector.append({'label': 'ALL', 'step': 'all'})

graph_layout = {
    'height': 1000,
    'template': 'plotly_dark',
    'font_color': 'gray',
    'paper_bgcolor': 'rgba(0,0,0,0)',
    'plot_bgcolor': 'rgba(0,0,0,0)',
    'margin': {
        'b': 20,
        't': 20,
        'l': 20,
        'r': 20
    },
    'hovermode': 'x unified',
    'hoverdistance': 20,
    'xaxis': {
        'showspikes': True,
        'spikemode': 'across',
        'spikesnap': 'cursor',
        'spikecolor': 'gray',
        'spikedash': 'dash',
        'spikethickness': -2,
        #'rangeslider': {
        #    'visible': True
        #},
        'rangeselector': {
            'buttons': date_selector
        }
    },
    'yaxis': {
        'side': 'right',
        'showspikes': True,
        'spikemode': 'across',
        'spikesnap': 'cursor',
        'spikecolor': 'gray',
        'spikedash': 'dash',
        'spikethickness': -2
    },
    'legend': {
            "x": 0,
            "y": 1
    }
}