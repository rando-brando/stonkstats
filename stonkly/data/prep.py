import plotly.graph_objs as go
import pandas as pd
from stonkly.data.fmp import FMP
import stonkly.dashboard.layouts as sdl
import json
import os


def fmp():
    FMP_API_KEY = os.getenv('FMP_API_KEY')
    fmp = FMP(FMP_API_KEY)
    return fmp


def symbols():
    # symbols = fmp.stock_screener({'exchange': 'NYSE,AMEX,NASDAQ'})
    symbols = json.dumps([
        {"symbol": "AAPL", "companyName": "Apple", "exchangeShortName": "NASDAQ"},
        {"symbol": "MSFT", "companyName": "Microsoft", "exchangeShortName": "NASDAQ"},
        {"symbol": "AMZN", "companyName": "Amazon", "exchangeShortName": "NASDAQ"},
        {"symbol": "PARA", "companyName": "Paramount", "exchangeShortName": "NYSE"}
    ])
    return symbols


def _price(price_data):
    df = pd.DataFrame(price_data)
    df['date'] = pd.to_datetime(df['date'])
    df['sma200'] = df['close'].rolling(200).mean().shift(-199)
    return df


def _earnings(earnings_data):
    # TODO: Fix 4p for stocks that report more or less
    df = pd.DataFrame(earnings_data)
    df['date'] = pd.to_datetime(df['date'])
    df['epsTTM'] = df['actualEarningResult'].rolling(4).sum().shift(-3)
    df['fairPE'] = 15 * df['epsTTM']
    return df


def _price_to_earnings(price_df, earnings_df):
    df = price_df.merge(earnings_df, how='left', on='date')
    df['lastEarningDate'] = df['date']
    df.loc[df['symbol'].isna(), 'lastEarningDate'] = pd.NA
    df['lastEarningDate'] = df['lastEarningDate'].bfill()
    df['epsTTM'] = df['epsTTM'].bfill()
    df['PE'] = df['close'] / df['epsTTM']
    mean_df = df.groupby(['lastEarningDate', 'epsTTM'], as_index=False, sort=False).agg({'PE': 'mean'})
    mean_df['normalPE'] = mean_df['PE'].rolling(20).mean().shift(-19) * mean_df['epsTTM']
    mean_df.rename(columns={'lastEarningDate': 'date'}, inplace=True)
    return mean_df


def stonk_graph(price_data, earnings_data):
    price_df = _price(price_data)
    earnings_df = _earnings(earnings_data)
    pe_df = _price_to_earnings(price_df, earnings_df)
    
    fig = go.Figure(
        layout=sdl.graph_layout,
        data=[
            go.Scatter(
                x=earnings_df.date,
                y=earnings_df.fairPE,
                mode='lines',
                name='Fair PE',
                fill='tozeroy',
                line_width=3
            ),
            go.Scatter(
                x=pe_df.date,
                y=pe_df.normalPE,
                mode='lines',
                name='Normal PE',
                line_width=3
            ),
            go.Scatter(
                x=price_df.date,
                y=price_df.close,
                mode='lines',
                name='Close'
            ),
            go.Scatter(
                x=price_df.date,
                y=price_df.sma200,
                mode='lines',
                name='200d MA',
                line_width=3
            ),
            go.Scatter(
                x=price_df.date,
                y=price_df.sma,
                mode='lines',
                name='50d MA',
                line_width=3
            )
        ]
    )
    return fig
