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
    def __init__(self, price=None, earnings=None, estimates=None):
        super().__init__()
        self.price = price
        self.earnings = earnings
        self.estimates = estimates
        self.fairPEG = 15
        self.normalPEG = 15
        self.maxPEG = 30
        self.pe = None
        self.fpe = None
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
            'dtick': 'M12'
        }
        self.layout['yaxis'] = {
            'showspikes': True,
            'spikemode': 'across',
            'spikesnap': 'cursor',
            'spikecolor': 'gray',
            'spikedash': 'dash',
            'spikethickness': -2,
            'rangemode': "tozero",
            'side': 'right',
            'griddash': 'dash',
            'gridcolor': 'rgba(128,128,128,0.5)'
        }
        self._price()
        self._earnings()
        self._estimates()
        self._price_earnings()
        self._xrange()
        self._yrange()

    def _price(self):
        df = pd.DataFrame(self.price).sort_values('date')
        df['date'] = pd.to_datetime(df['date'])
        df['sma200'] = df['close'].rolling(200).mean()
        return df

    def _earnings(self):
        # TODO: Fix 4p for stocks that report more or less
        df = pd.DataFrame(self.earnings).sort_values('date')
        df['date'] = pd.to_datetime(df['date'])
        df['epsTTM'] = df['actualEarningResult'].rolling(4).sum()
        return df

    def _estimates(self):
        estimates = self.estimates
        thisY = pd.to_datetime(estimates[2]['endDate'])
        nextY = pd.to_datetime(estimates[3]['endDate'])
        gr1Y = estimates[3]['growth']
        gr5Y = estimates[4]['growth']
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
                offD = pd.DateOffset(days=1)
                offY = pd.DateOffset(years=1)
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
        df = pd.DataFrame(data)
        return df

    def _price_earnings(self):
        # join price and earnings
        self.earnings['earningDate'] = self.earnings['date']
        self.pe = pd.merge_asof(self.price, self.earnings, on='date')
        self.pe['peTTM'] = self.pe['close'] / self.pe['epsTTM']
        cols = ['earningDate', 'epsTTM']
        aggs = {'peTTM': 'mean'}
        self.pe = self.pe.groupby(cols, as_index=False, sort=False).agg(aggs)
        self.pe.rename(columns={'earningDate': 'date'}, inplace=True)
        # calculate growth rates
        offY = self.earnings['date'].iloc[-1] + pd.DateOffset(years=1)
        growth = self.estimates[self.estimates['date'] > offY]['growth'].iloc[0]
        self.fairPEG = min(max(100 * growth, self.fairPEG), self.maxPEG)
        self.normalPEG = min(max(self.pe['peTTM'].iloc[-20:].mean(), self.normalPEG), self.maxPEG)
        # calculte ratios
        self.pe['fairPE'] = self.pe['epsTTM'] * self.fairPEG
        self.pe['normalPE'] = self.pe['epsTTM'] * self.pe['peTTM'].rolling(20).mean()
        self.estimates['fairFwdPE'] = self.estimates['avgEstimate'] * self.fairPEG
        self.estimates['lowFwdPE'] = self.estimates['lowEstimate'] * self.fairPEG
        self.estimates['highFwdPE'] = self.estimates['highEstimate'] * self.fairPEG
        self.estimates['normalFwdPE'] = self.estimates['avgEstimate'] * self.normalPEG
        self.fpe = self.pe.tail(1).rename(columns={'fairPE': 'fairFwdPE', 'normalPE': 'normalFwdPE'})
        self.fpe['lowFwdPE'] = self.fpe['fairFwdPE']
        self.fpe['highFwdPE'] = self.fpe['fairFwdPE']
        self.fpe = pd.concat([self.fpe, self.estimates], ignore_index=True)

    def _xrange(self):
        offY20 = pd.DateOffset(days=365.25 * 20)
        xmax = max(
            self.price['date'].max(skipna=True),
            self.fpe['date'].max(skipna=True)
        )
        xmin = max(
            self.price['date'].max(skipna=True) - offY20,
            self.price['date'].min(skipna=True)
        )
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
        self.layout['xaxis']['range'] = [xmin, xmax]
        self.layout['xaxis']['rangeselector'] = {'buttons': date_selector}

    def _yrange(self):
        ymax = max(
            self.price['close'].max(skipna=True),
            self.pe['fairPE'].max(skipna=True),
            self.pe['normalPE'].max(skipna=True),
            self.fpe['highFwdPE'].max(skipna=True),
            self.fpe['normalFwdPE'].max(skipna=True)
        )
        ymin = 0
        self.layout['yaxis']['range'] = [ymin, ymax]

    def load_graph(self):
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
                        line_width=3
                    ),
                    go.Scatter(
                        x=self.fpe.date,
                        y=self.fpe.fairFwdPE,
                        name='Fair Fwd PE',
                        fill='tozeroy',
                        line_width=3,
                    ),
                    go.Scatter(
                        x=self.fpe.date,
                        y=self.fpe.highFwdPE,
                        name='High Fwd PE',
                        line_width=3,
                        line_dash='dash'
                    ),
                    go.Scatter(
                        x=self.fpe.date,
                        y=self.fpe.lowFwdPE,
                        name='Low Fwd PE',
                        line_width=3,
                        line_dash='dash'
                    ),
                    go.Scatter(
                        x=self.pe.date,
                        y=self.pe.normalPE,
                        name='Normal PE',
                        line_width=3
                    ),
                    go.Scatter(
                        x=self.fpe.date,
                        y=self.fpe.normalFwdPE,
                        name='Normal Fwd PE',
                        line_width=3,
                        line_dash='dot'
                    ),
                    go.Scatter(
                        x=self.price.date,
                        y=self.price.close,
                        name='Close',
                        line_color='white'
                    )
                ]
            )
         )
        return graph
