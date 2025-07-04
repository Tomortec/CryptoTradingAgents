
import os
from datetime import datetime, timedelta
import requests
from .utils import Singleton

def fetch_ta_from_taapi(symbol: str, indicator: str, interval: str = "15m", **params):
    """
    Fetch technical analysis data from TAAPI.io for a given symbol and indicator.
    :note: For free plan, the rate limit is 1 request per 15 seconds.
    
    :param symbol: The trading pair symbol (e.g., 'BTC/USDT').
    :param indicator: The technical indicator to fetch (e.g., 'rsi', 'macd').
    :param interval: The time interval for the data (default is '15m').
    :return: Technical analysis data for the specified indicator. (Raw JSON text)
    """
    api_key = os.getenv("TAAPI_API_KEY")
    if not api_key:
        return ""
    params = {
        "secret": api_key,
        "exchange": "binance",
        "symbol": symbol,
        "interval": interval,
        **params
    }
    url = f"https://api.taapi.io/{indicator}"
    response = requests.get(url, params=params)
    return response.text if response.status_code == 200 else None

class TAAPIBulkUtils(metaclass=Singleton):
    """
    Singleton class for fetching bulk technical analysis data from TAAPI.io.\n
    :note: For free plan, the rate limit is 1 request per 15 seconds.
    """

    trend_momentum_indicators = [
        "ema", "ichimoku", "supertrend", "donchianchannels",
        "macd", "rsi", "stochrsi", "trix", "stc", "vwap"
    ]
    volatility_structure_indicators = [
        "atr", "bbands", "keltnerchannels", "chop", "engulfing",
        "hammer", "morningstar", "eveningstar", "3whitesoldiers", "3blackcrows"
    ]
    indicators = trend_momentum_indicators + volatility_structure_indicators

    def __init__(self, symbol, bulk_interval: str = "15m", **kwargs):
        """
        Initialize the TAAPIUtils with a trading pair symbol and interval.

        :param symbol: The trading pair symbol (e.g., 'BTC/USDT').
        :param bulk_interval: The time interval for the data (default is '15m'). Only for bulk data.
        :param kwargs: Additional parameters for the indicators.
        """
        self.api_key = os.getenv("TAAPI_API_KEY")
        self.bulk_data = None
        self.last_fetch_time = None

        symbol = symbol.upper()
        if not symbol.endswith("/USDT") and not symbol.endswith("/USDC"):
            symbol += "/USDT"
        self.symbol = symbol
        self.bulk_interval = bulk_interval
        self.indicator_params = [
            {
                "indicator": indicator,
                **({k.replace(f"{indicator}_", ""): v for k, v in kwargs.items() if k.startswith(f"{indicator}_")})
            } for indicator in self.indicators
        ]
        
    def __fetch_bulk_ta_from_taapi(self):
        if self.bulk_data is not None and self.last_fetch_time is not None and \
            datetime.now() - self.last_fetch_time < timedelta(seconds=15):
            return self.bulk_data
        
        if not self.api_key:
            return None

        url = "https://api.taapi.io/bulk"
        body = {
            "secret": self.api_key,
            "construct": {
                "exchange": "binance",
                "symbol": self.symbol,
                "interval": self.bulk_interval,
                "indicators": self.indicator_params
            }
        }
        self.last_fetch_time = datetime.now()
        response = requests.post(url, json=body)
        if response.status_code == 200:
            data = response.json()
            if "data" in data and isinstance(data["data"], list):
                format_floats_in_dict = lambda d: {k: (round(v, 4) if isinstance(v, float) else v) for k, v in d.items()}
                self.bulk_data = {
                    item["indicator"]: format_floats_in_dict(item["result"])
                    for item in data["data"]
                }
        else:
            print(f"Error fetching bulk data: {response.status_code} - {response.text}")
            self.bulk_data = None

    def fetch_trend_momentum_indicators_from_taapi(self):
        """
        Fetch trend and momentum indicators from TAAPI.io.
        :return: A dictionary containing the latest values for each trend and momentum indicator.
        """
        self.__fetch_bulk_ta_from_taapi()
        if self.bulk_data is None or not isinstance(self.bulk_data, dict):
            return None
        return {indicator: self.bulk_data.get(indicator, {}) for indicator in self.trend_momentum_indicators}
    
    def fetch_volatility_structure_indicators_from_taapi(self):
        """
        Fetch volatility and structure indicators from TAAPI.io.
        :return: A dictionary containing the latest values for each volatility and structure indicator.
        """
        self.__fetch_bulk_ta_from_taapi()
        if self.bulk_data is None or not isinstance(self.bulk_data, dict):
            return None
        return {indicator: self.bulk_data.get(indicator, {}) for indicator in self.volatility_structure_indicators}