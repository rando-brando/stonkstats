import plotly.graph_objs as go
import stonkly.dashboard.layouts as sdl
import pandas as pd


def _price(price):
    df = pd.DataFrame(price).sort_values('date')
    df['date'] = pd.to_datetime(df['date'])
    df['sma200'] = df['close'].rolling(200).mean()
    return df


def _earnings(earnings):
    # TODO: Fix 4p for stocks that report more or less
    df = pd.DataFrame(earnings).sort_values('date')
    df['date'] = pd.to_datetime(df['date'])
    df['epsTTM'] = df['actualEarningResult'].rolling(4).sum()
    return df


def _estimates(estimates):
    thisY = pd.to_datetime(estimates[2]['endDate'])
    nextY = pd.to_datetime(estimates[3]['endDate'])
    gr1Y = estimates[3]['growth']
    gr5Y = estimates[4]['growth']
    offD = pd.DateOffset(days=1)
    offY = pd.DateOffset(years=1)
    dates, growth, avgs, highs, lows = [], [], [], [], []
    if thisY:
        dates.append(thisY)
        growth.append(estimates[2]['growth'])
        avgs.append(estimates[2]['earningsEstimate']['avg'])
        lows.append(estimates[2]['earningsEstimate']['low'])
        highs.append(estimates[2]['earningsEstimate']['high'])
    if nextY:
        dates.append(nextY)
        growth.append(estimates[3]['growth'])
        avgs.append(estimates[3]['earningsEstimate']['avg'])
        lows.append(estimates[3]['earningsEstimate']['low'])
        highs.append(estimates[3]['earningsEstimate']['high'])
    if gr5Y:
        if gr1Y:
            gr4Y = pow(pow(1 + gr5Y, 5) / (1 + gr1Y), 0.25)
            grs = [gr4Y] * 4
        else:
            grs = [1 + gr5Y] * 5
        for gr in grs:
            dates.append(dates[-1] + offD + offY - offD)
            growth.append(gr - 1)
            avgs.append(avgs[-1] * gr)
            lows.append(lows[-1] * gr)
            highs.append(highs[-1] * gr)
    data = {
        'date': dates,
        'growth': growth,
        'avgEstimate': avgs,
        'lowEstimate': lows,
        'highEstimate': highs
    }
    return pd.DataFrame(data)


def _price_to_earnings(price, earnings, estimates):
    # join price and earnings
    earnings['earningDate'] = earnings['date']
    pe = pd.merge_asof(price, earnings, on='date')
    pe['peTTM'] = pe['close'] / pe['epsTTM']
    cols = ['earningDate', 'epsTTM']
    aggs = {'peTTM': 'mean'}
    pe = pe.groupby(cols, as_index=False, sort=False).agg(aggs)
    pe.rename(columns={'earningDate': 'date'}, inplace=True)
    # calculate growth rates
    offY = earnings['date'].iloc[-1] + pd.DateOffset(years=1)
    growth = estimates[estimates['date'] > offY]['growth'].iloc[0]
    fairPEG = min(max(100 * growth, 15), 30) if growth else 15
    normalPEG = pe['peTTM'].iloc[-20:].mean()
    # calculte ratios
    pe['fairPE'] = pe['epsTTM'] * fairPEG
    pe['normalPE'] = pe['epsTTM'] * pe['peTTM'].rolling(20).mean()
    estimates['fairFwdPE'] = estimates['avgEstimate'] * fairPEG
    estimates['lowFwdPE'] = estimates['lowEstimate'] * fairPEG
    estimates['highFwdPE'] = estimates['highEstimate'] * fairPEG
    estimates['normalFwdPE'] = estimates['avgEstimate'] * normalPEG
    fpe = pe.tail(1).rename(columns={'fairPE': 'fairFwdPE', 'normalPE': 'normalFwdPE'})
    fpe['lowFwdPE'] = fpe['fairFwdPE']
    fpe['highFwdPE'] = fpe['fairFwdPE']
    fpe = pd.concat([fpe, estimates], ignore_index=True)
    return pe, fpe


def _graph_layout(price, fpe):
    graph_layout = sdl.graph_layout
    xmax = max(
        pd.Timestamp.now(),
        fpe['date'].max()
    )
    xmin = max(
        price['date'].max() - pd.Timedelta(days=365.25 * 20),
        price['date'].min()
    )
    ymax = max(
        price['close'].max(),
        fpe['normalFwdPE'].max(),
        fpe['highFwdPE'].max()
    )
    ymin = 0
    i = xmax.year - xmin.year
    date_selector = [
        {
            'count': i,
            'label': f'{i}Y',
            'step': 'year',
            'stepmode': 'backward'
        }
        for i in range(i, 0, -1)
    ]
    date_selector.append({'label': 'ALL', 'step': 'all'})
    graph_layout['xaxis']['range'] = [xmin, xmax]
    graph_layout['yaxis']['range'] = [ymin, ymax]
    graph_layout['xaxis']['rangeselector'] = None
    graph_layout['xaxis']['rangeselector'] = {'buttons': date_selector}
    return graph_layout


def stonk_graph(price, earnings, estimates):
    price = _price(price)
    earnings = _earnings(earnings)
    estimates = _estimates(estimates)
    pe, fpe = _price_to_earnings(price, earnings, estimates)
    fig = go.Figure(
        layout=_graph_layout(price, fpe),
        data=[
            go.Scatter(
                x=pe.date,
                y=pe.fairPE,
                name='Fair PE',
                fill='tozeroy',
                line_width=3
            ),
            go.Scatter(
                x=fpe.date,
                y=fpe.fairFwdPE,
                name='Fair Fwd PE',
                fill='tozeroy',
                line_width=3,
                line_dash='dot'
            ),
            go.Scatter(
                x=fpe.date,
                y=fpe.highFwdPE,
                name='High Fwd PE',
                line_width=3,
                line_dash='dash'
            ),
            go.Scatter(
                x=fpe.date,
                y=fpe.lowFwdPE,
                name='Low Fwd PE',
                line_width=3,
                line_dash='dash'
            ),
            go.Scatter(
                x=pe.date,
                y=pe.normalPE,
                name='Normal PE',
                line_width=3
            ),
            go.Scatter(
                x=fpe.date,
                y=fpe.normalFwdPE,
                name='Normal Fwd PE',
                line_width=3,
                line_dash='dot'
            ),
            go.Scatter(
                x=price.date,
                y=price.close,
                name='Close',
                line_color='white'
            )
        ]
    )
    return fig

"""
go.Scatter(
    x=price.date,
    y=price.sma200,
    name='200d MA',
    line_width=1,
),
go.Scatter(
    x=price.date,
    y=price.sma,
    name='50d MA',
    line_width=1
)
"""