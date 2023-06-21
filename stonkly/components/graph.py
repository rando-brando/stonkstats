from dash import dcc
import plotly.graph_objs as go
import pandas as pd


class Graph:
    def __init__(self):
        self.layout = {}
        self.layout['template'] = 'plotly_dark'
        self.layout['paper_bgcolor'] = 'rgba(0,0,0,0)'
        self.layout['plot_bgcolor'] = 'rgba(0,0,0,0)'
        self.layout['font_color'] = 'gray'
        self.layout['margin'] = {'b': 20, 't': 20, 'l': 20, 'r': 20}
        self.layout['clickmode'] = 'select'
        self.layout['dragmode'] = 'zoom'
        self.layout['hovermode'] = 'x unified'
        self.layout['hoverdistance'] = 20


class StonkGraph(Graph):
    def __init__(self, data=None):
        super().__init__()
        # default attributes
        self.prices = data['prices']
        self.earnings = data['earnings']
        self.estimates = data['estimates']
        self.pe = None
        self.fpe = None
        peg = {
            'fair': 15,
            'normal': 15,
            'max': 30
        }
        dates = {
            'thisY': pd.to_datetime(self.estimates[2]['endDate']),
            'nextY': pd.to_datetime(self.estimates[3]['endDate'])
        }
        growth = {
            '0Y': self.estimates[2]['growth'],
            '1Y': self.estimates[3]['growth'],
            '5Y': self.estimates[4]['growth']
        }
        offsets = {
            '1D': pd.DateOffset(days=1),
            '1Y': pd.DateOffset(years=1),
            '20Y': pd.DateOffset(years=20)
        }

        # prices dataframe
        self.prices = pd.DataFrame(self.prices).sort_values('date')
        self.prices['date'] = pd.to_datetime(self.prices['date'])

        # earnings dataframe
        # TODO: Fix 4p for stocks that report more or less?
        self.earnings = pd.DataFrame(self.earnings).sort_values('date')
        self.earnings['date'] = pd.to_datetime(self.earnings['date'])
        self.earnings['epsTTM'] = self.earnings['actualEarningResult'].rolling(4).sum()
        self.earnings['estNTM'] = self.earnings['estimatedEarning'].rolling(4).sum().shift(-4)
        self.earnings['estimatedGrowth'] = self.earnings['estNTM'] / self.earnings['epsTTM'] - 1
        self.earnings['epsNTM'] = self.earnings['epsTTM'].shift(-4)
        self.earnings['actualGrowth'] = self.earnings['epsNTM'] / self.earnings['epsTTM'] - 1

        # estimates dataframe
        data = []
        if dates['thisY']:
            data.append({
                'date': dates['thisY'],
                'growth': self.estimates[2]['growth'],
                'avgEstimate': self.estimates[2]['earningsEstimate']['avg'],
                'lowEstimate': self.estimates[2]['earningsEstimate']['low'],
                'highEstimate': self.estimates[2]['earningsEstimate']['high']
            })
        if dates['nextY']:
            data.append({
                'date': dates['nextY'],
                'growth': self.estimates[3]['growth'],
                'avgEstimate': self.estimates[3]['earningsEstimate']['avg'],
                'lowEstimate': self.estimates[3]['earningsEstimate']['low'],
                'highEstimate': self.estimates[3]['earningsEstimate']['high']
            })
        if growth['5Y']:
            if growth['1Y']:
                growth['4Y'] = pow(pow(1 + growth['5Y'], 5) / (1 + growth['1Y']), 0.25) - 1
                rates = [growth['4Y']] * 4
            else:
                rates = [growth['5Y']] * 5
            for rate in rates:
                data.append({
                    'date': data[-1]['date'] + offsets['1D'] + offsets['1Y'] - offsets['1D'],
                    'growth': rate,
                    'avgEstimate': data[-1]['avgEstimate'] * (1 + rate),
                    'lowEstimate': data[-1]['lowEstimate'] * (1 + rate),
                    'highEstimate': data[-1]['highEstimate'] * (1 + rate)
                })
        self.estimates = pd.DataFrame(data)

        # prices to earnings dataframe
        df = self.earnings
        df['earningDate'] = df['date']
        self.pe = pd.merge_asof(self.prices, df, on='date')
        self.pe['peTTM'] = self.pe['close'] / self.pe['epsTTM']
        self.pe = self.pe.groupby(
            ['earningDate', 'epsTTM'],
            as_index=False,
            sort=False
        ).agg({'peTTM': 'mean'})
        self.pe.rename(columns={'earningDate': 'date'}, inplace=True)
        rate = growth['5Y'] if growth['5Y'] else growth['1Y'] if growth['1Y'] else growth['0Y']
        peg['fair'] = min(max(100 * rate, peg['fair']), peg['max'])
        peg['normal'] = min(max(self.pe['peTTM'].iloc[-20:].mean(), peg['normal']), peg['max'])
        self.pe['fairPE'] = self.pe['epsTTM'] * peg['fair']
        self.pe['normalPE'] = self.pe['epsTTM'] * self.pe['peTTM'].rolling(20).mean()
        self.estimates['fairFwdPE'] = self.estimates['avgEstimate'] * peg['fair']
        self.estimates['lowFwdPE'] = self.estimates['lowEstimate'] * peg['fair']
        self.estimates['highFwdPE'] = self.estimates['highEstimate'] * peg['fair']
        self.estimates['normalFwdPE'] = self.estimates['avgEstimate'] * peg['normal']
        self.fpe = self.pe.tail(1).rename(columns={'fairPE': 'fairFwdPE', 'normalPE': 'normalFwdPE'})
        self.fpe['lowFwdPE'] = self.fpe['fairFwdPE']
        self.fpe['highFwdPE'] = self.fpe['fairFwdPE']
        self.fpe = pd.concat([self.fpe, self.estimates], ignore_index=True)

        # layout
        ymin = 0
        ymax = max(
            self.prices['close'].max(skipna=True),
            self.pe['fairPE'].max(skipna=True),
            self.pe['normalPE'].max(skipna=True),
            self.fpe['highFwdPE'].max(skipna=True),
            self.fpe['normalFwdPE'].max(skipna=True))
        xmin = max(
            self.prices['date'].min(skipna=True),
            self.prices['date'].max(skipna=True) - offsets['20Y'])
        xmax = max(
            self.fpe['date'].max(skipna=True),
            self.prices['date'].max(skipna=True))
        date_selector = []
        for i in range(xmax.year - xmin.year, 0, -1):
            date_selector.append({
                'count': i,
                'label': f'{i}Y',
                'step': 'year',
                'stepmode': 'backward'
            })
        self.layout['height'] = 1000
        self.layout['legend'] = {'x': 0, 'y': 1}
        self.layout['xaxis'] = {
            'showspikes': True,
            'spikemode': 'across',
            'spikesnap': 'cursor',
            'spikecolor': 'gray',
            'spikedash': 'dash',
            'spikethickness': -2,
            'griddash': 'dash',
            'gridcolor': 'rgba(128,128,128,0.5)',
            'dtick': 'M12',
            'rangeselector': {'buttons': date_selector},
            'range': [xmin, xmax]
        }
        self.layout['yaxis'] = {
            'showspikes': True,
            'spikemode': 'across',
            'spikesnap': 'cursor',
            'spikecolor': 'gray',
            'spikedash': 'dash',
            'spikethickness': -2,
            'side': 'right',
            'griddash': 'dash',
            'gridcolor': 'rgba(128,128,128,0.5)',
            'rangemode': "tozero",
            'range': [ymin, ymax]
        }

    def load(self):
        graph = dcc.Graph(
            className='stonk-graph',
            config={
                'displayModeBar': False,
                'showAxisDragHandles': False
            },
            figure=go.Figure(
                layout=self.layout,
                data=[
                    go.Scatter(
                        x=self.pe.date,
                        y=self.pe.fairPE,
                        name='Fair PE',
                        fill='tozeroy',
                        line={'width': 3}
                    ),
                    go.Scatter(
                        x=self.fpe.date,
                        y=self.fpe.fairFwdPE,
                        name='Fair Fwd PE',
                        fill='tozeroy',
                        line={'width': 3}
                    ),
                    go.Scatter(
                        x=self.fpe.date,
                        y=self.fpe.highFwdPE,
                        name='High Fwd PE',
                        line={'width': 3, 'dash': 'dash'}
                    ),
                    go.Scatter(
                        x=self.fpe.date,
                        y=self.fpe.lowFwdPE,
                        name='Low Fwd PE',
                        line={'width': 3, 'dash': 'dash'}
                    ),
                    go.Scatter(
                        x=self.pe.date,
                        y=self.pe.normalPE,
                        name='5Y Avg PE',
                        line={'width': 3}
                    ),
                    go.Scatter(
                        x=self.fpe.date,
                        y=self.fpe.normalFwdPE,
                        name='5Y Avg Fwd PE',
                        line={'width': 3, 'dash': 'dot'}
                    ),
                    go.Scatter(
                        x=self.prices.date,
                        y=self.prices.close,
                        name='Close',
                        line={'color': 'white'}
                    )
                ]
            )
         )
        return graph
