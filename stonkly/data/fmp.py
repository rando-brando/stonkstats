import requests
from requests.exceptions import HTTPError, JSONDecodeError


class FMP:
    def __init__(self, api_key: str) -> None:
        class TimeFrames:
            minutes_1 = '1min'
            minutes_5 = '5min'
            minutes_15 = '15min'
            minutes_30 = '30min'
            hours_1 = '1hour'
            hours_4 = '4hour'
            daily = '1day'
            weekly = '1week',
            monthly = '1month'
            yearly = '1year'

        class ReportingPeriods:
            annual = 'annual'
            quarter = 'quarter'
            ttm = 'ttm'

        self.TIME_FRAMES = TimeFrames()
        self.REPORTING_PERIODS = ReportingPeriods()
        self._base_url = 'https://financialmodelingprep.com'
        self._api_key = api_key

    def _get_request(self, url: str, params={}):
        params['apikey'] = self._api_key
        response = requests.get(url, params=params)
        return response

    def _make_url_v3(self, endpoint: str) -> str:
        return f'{self._base_url}/api/v3/{endpoint}'

    def _make_url_v4(self, endpoint: str) -> str:
        return f'{self._base_url}/api/v4/{endpoint}'

    def _parse_response_content(self, response):
        try:
            content = response.json()
        except JSONDecodeError:
            raise JSONDecodeError('Invalid JSON response')

        if isinstance(content, dict) and 'Error Message' in content:
            raise PermissionError(content['Error Message'])

        try:
            response.raise_for_status()
        except HTTPError:
            raise HTTPError(f'{response.status_code} - {response.reason}')

        return content

    def tradeable_symbols(self) -> list:
        url = self._make_url_v3('available-traded/list')
        response = self._get_request(url)
        data = self._parse_response_content(response)
        return data

    def stock_screener(self, params={}) -> list:
        url = self._make_url_v3('stock-screener')
        params['isActivelyTrading'] = 'true'
        response = self._get_request(url, params=params)
        data = self._parse_response_content(response)
        return data

    def technical_chart(self, symbol: str, timeframe='1day', type='sma', period=50) -> list:
        url = self._make_url_v3(f'technical_indicator/{timeframe}/{symbol}')
        params = {'type': type, 'period': period}
        response = self._get_request(url, params=params)
        data = self._parse_response_content(response)
        return data

    def company_profile(self, symbol: str) -> list:
        url = self._make_url_v3(f'profile/{symbol}')
        response = self._get_request(url)
        data = self._parse_response_content(response)
        return data

    def key_metrics(self, symbol: str, period='ttm', limit=10) -> list:
        url = self._make_url_v3(f'key-metrics/{symbol}')
        params = {'period': period, 'limit': limit}
        response = self._get_request(url, params=params)
        data = self._parse_response_content(response)
        return data

    def income_statements(self, symbol: str, period='annual', limit=10) -> list:
        url = self._make_url_v3(f'income-statement/{symbol}')
        params = {'period': period, 'limit': limit}
        response = self._get_request(url, params=params)
        data = self._parse_response_content(response)
        return data

    def balance_sheet_statements(self, symbol: str, period='annual', limit=10) -> list:
        url = self._make_url_v3(f'balance-sheet-statement/{symbol}')
        params = {'period': period, 'limit': limit}
        response = self._get_request(url, params=params)
        data = self._parse_response_content(response)
        return data

    def cash_flow_statements(self, symbol: str, period='annual', limit=10) -> list:
        url = self._make_url_v3(f'cash-flow-statement/{symbol}')
        params = {'period': period, 'limit': limit}
        response = self._get_request(url, params=params)
        data = self._parse_response_content(response)
        return data

    def earnings_surprises(self, symbol: str) -> list:
        url = self._make_url_v3(f'earnings-surprises/{symbol}')
        response = self._get_request(url)
        data = self._parse_response_content(response)
        return data
