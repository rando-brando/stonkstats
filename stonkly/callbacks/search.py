from dash import Input, Output, State, ALL
from dash import ClientsideFunction
from stonkly.server import app

app.clientside_callback(
    ClientsideFunction(
        namespace='clientside',
        function_name='suggest_options'
    ),
    Output('search-body', 'children'),
    Input('search-input', 'value'),
    State('search-options', 'data')
)


app.clientside_callback(
    ClientsideFunction(
        namespace='clientside',
        function_name='select_option'
    ),
    Output('selected-option', 'data'),
    Output('search-input', 'value'),
    Input({'index': ALL, 'type': 'search-row'}, 'n_clicks'),
    State({'index': ALL, 'type': 'search-row'}, 'children')
)
