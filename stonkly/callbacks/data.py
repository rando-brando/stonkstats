from dash import Input, Output
from stonkly.server import app
from stonkly.config import FMP_API_KEY
from stonkly.data.fmp import FMP
import yahooquery as yq


@app.callback(
    Output('price-data', 'data'),
    Output('earnings-data', 'data'),
    Output('estimates-data', 'data'),
    Input('selected-option', 'data')
)
def update_data(symbol):
    fmp = FMP(FMP_API_KEY)
    price = fmp.technical_chart(symbol)
    earnings = fmp.earnings_surprises(symbol)
    estimates = yq.Ticker(symbol).earnings_trend[symbol]['trend']
    return [price, earnings, estimates]
