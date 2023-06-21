from dash import Input, Output
from stonkly.server import app
from stonkly.data.fmp import FMP
import yahooquery as yq
import os


@app.callback(
    Output('symbol-data', 'data'),
    Input('selected-option', 'data')
)
def update_data(symbol):
    FMP_API_KEY = os.getenv('FMP_API_KEY')
    fmp = FMP(FMP_API_KEY)
    prices = fmp.technical_chart(symbol)
    earnings = fmp.earnings_surprises(symbol)
    estimates = yq.Ticker(symbol).earnings_trend[symbol]['trend']
    data = {
        'prices': prices,
        'earnings': earnings,
        'estimates': estimates
    }
    return data
