from langchain_core.messages import BaseMessage, HumanMessage, ToolMessage, AIMessage
from typing import List
from typing import Annotated
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import RemoveMessage
from langchain_core.tools import tool
from datetime import date, timedelta, datetime
import functools
import pandas as pd
import os
from dateutil.relativedelta import relativedelta
from langchain_openai import ChatOpenAI
import tradingagents.dataflows.interface as interface
from tradingagents.default_config import DEFAULT_CONFIG
from langchain_core.messages import HumanMessage


def create_msg_delete():
    def delete_messages(state):
        """Clear messages and add placeholder for Anthropic compatibility"""
        messages = state["messages"]
        
        # Remove all messages
        removal_operations = [RemoveMessage(id=m.id) for m in messages]
        
        # Add a minimal placeholder message
        placeholder = HumanMessage(content="Continue")
        
        return {"messages": removal_operations + [placeholder]}
    
    return delete_messages


class Toolkit:
    _config = DEFAULT_CONFIG.copy()

    @classmethod
    def update_config(cls, config):
        """Update the class-level configuration."""
        cls._config.update(config)

    @property
    def config(self):
        """Access the configuration."""
        return self._config

    def __init__(self, config=None):
        if config:
            self.update_config(config)

    @staticmethod
    @tool
    def get_blockbeats_news(
        count: Annotated[int, "Number of news articles to retrieve, no more than 30"] = 10,
    ) -> str:
        """
        Retrieve the latest news from BlockBeats, especially useful for Cryptos.
        Args:
            count (int): Number of news articles to retrieve, no more than 30
        Returns:
            str: A formatted string containing the latest news from BlockBeats.
        """
        blockbeats_news_result = interface.get_blockbeats_news(count)
        return blockbeats_news_result
    
    @staticmethod
    @tool
    def get_coindesk_news(
        tickers: Annotated[
            List[str],
            "List of tickers to get news for, e.g. ['BTC', 'ETH']",
        ] = [],
        count: Annotated[int, "Number of news articles to retrieve, default is 10"] = 10,
    ) -> str:
        """
        Retrieve the latest news from Coindesk for a given list of tickers.
        Args:
            tickers (List[str]): List of tickers to get news for, e.g. ['BTC', 'ETH']
            count (int): Number of news articles to retrieve, default is 10
        Returns:
            str: A formatted string containing the latest news from Coindesk for the specified tickers.
        """
        coindesk_news_result = interface.get_coindesk_news(tickers, count)
        return coindesk_news_result
    
    @staticmethod
    @tool
    def get_coinstats_news() -> str:
        """
        Retrieve the latest news from CoinStats.
        Returns:
            str: A formatted string containing the latest news from CoinStats.
        """
        coinstats_news_result = interface.get_coinstats_news()
        return coinstats_news_result
    
    @staticmethod
    @tool
    def get_binance_ohlcv(
        symbol: Annotated[str, "ticker symbol of the asset"],
        interval: Annotated[
            str,
            "Interval for the data, e.g. '1m', '5m', '1h', '1d'",
        ] = "15m",
    ) -> str:
        """
        Retrieve the latest OHLCV data from Binance for a given symbol and interval.
        Args:
            symbol (str): Ticker symbol of the asset, e.g. 'BTCUSDT'
            interval (str): Interval for the data, e.g. '1m', '5m', '1h', '1d'
        Returns:
            str: A formatted string containing the latest OHLCV data from Binance for the specified symbol and interval.
        """
        binance_ohlcv_result = interface.get_binance_ohlcv(symbol, interval)
        return binance_ohlcv_result
    
    @staticmethod
    @tool
    def get_coinstats_btc_dominance() -> str:
        """
        Retrieve the current Bitcoin dominance percentage from CoinStats.
        Returns:
            str: A formatted string containing the last daily and weekly Bitcoin dominance percentage.
        """
        btc_dominance_result = interface.get_coinstats_btc_dominance()
        return btc_dominance_result
    
    @staticmethod
    @tool
    def get_binance_data(
        symbol: Annotated[str, "ticker symbol of the asset"],
        interval: Annotated[
            str,
            "Interval for the data, e.g. '1m', '5m', '1h', '1d'",
        ] = "15m",
    ) -> str:
        """
        Retrieve the latest market data from Binance for a given symbol and interval.
        Args:
            symbol (str): Ticker symbol of the asset, e.g. 'BTCUSDT'
            interval (str): Interval for the data, e.g. '1m', '5m', '1h', '1d'
        Returns:
            str: A formatted string containing the latest market data from Binance for the specified symbol and interval.
        """
        binance_data_result = interface.get_binance_data(symbol, interval)
        return binance_data_result
    
    @staticmethod
    @tool
    def get_fear_and_greed_index() -> str:
        """
        Get current crypto market Fear and Greed Index. 0 means "Extreme Fear", while 100 means "Extreme Greed"
        Returns:
            str: A formatted string containing the current crypto market Fear and Greed Index.
        """
        return interface.get_fear_and_greed_index()
    
    @staticmethod
    @tool
    def get_taapi_bulk_indicators(
        symbol: Annotated[str, "Ticker symbol of the asset, e.g. 'BTC'"],
        interval: Annotated[
            str,
            "Interval for the data, e.g. '1m', '5m', '1h', '1d'",
        ] = "15m",
        ema_period: Annotated[int, "EMA period, default is 30"] = 30,
        ichimoku_conversionPeriod: Annotated[int, "Ichimoku conversion line period, default is 9"] = 9,
        ichimoku_basePeriod: Annotated[int, "Ichimoku base line period, default is 26"] = 26,
        ichimoku_spanPeriod: Annotated[int, "Ichimoku span period, default is 52"] = 52,
        ichimoku_displacement: Annotated[int, "Ichimoku displacement, default is 26"] = 26,
        supertrend_period: Annotated[int, "Supertrend period, default is 7"] = 7,
        supertrend_multiplier: Annotated[float, "Supertrend multiplier, default is 3.0"] = 3.0,
        psar_start: Annotated[float, "Parabolic SAR start, default is 0.02"] = 0.02,
        psar_increment: Annotated[float, "Parabolic SAR increment, default is 0.02"] = 0.02,
        psar_maximum: Annotated[float, "Parabolic SAR maximum, default is 0.2"] = 0.2,
        donchianchannels_period: Annotated[int, "Donchian Channels period, default is 20"] = 20,
        macd_optInFastPeriod: Annotated[int, "MACD fast period, default is 12"] = 12,
        macd_optInSlowPeriod: Annotated[int, "MACD slow period, default is 26"] = 26,
        macd_optInSignalPeriod: Annotated[int, "MACD signal period, default is 9"] = 9,
        rsi_period: Annotated[int, "RSI period, default is 14"] = 14,
        stochrsi_rsiPeriod: Annotated[int, "Stochastic RSI RSI period, default is 14"] = 14,
        stochrsi_kPeriod: Annotated[int, "Stochastic RSI %K period, default is 5"] = 5,
        stochrsi_dPeriod: Annotated[int, "Stochastic RSI %D period, default is 3"] = 3,
        stochrsi_stochasticPeriod: Annotated[int, "Stochastic RSI stochastic period, default is 14"] = 14,
        trix_period: Annotated[int, "TRIX period, default is 30"] = 30,
        stc_fastLength: Annotated[int, "STC fast length, default is 23"] = 23,
        stc_slowLength: Annotated[int, "STC slow length, default is 50"] = 50,
        stc_cycleLength: Annotated[int, "STC cycle length, default is 10"] = 10,
        atr_period: Annotated[int, "ATR period, default is 14"] = 14,
        bbands_period: Annotated[int, "Bollinger Bands period, default is 20"] = 20,
        bbands_stddev: Annotated[float, "Bollinger Bands standard deviation, default is 2.0"] = 2.0,
        keltnerchannels_period: Annotated[int, "Keltner Channels period, default is 20"] = 20,
        keltnerchannels_multiplier: Annotated[float, "Keltner Channels multiplier, default is 2"] = 2,
        keltnerchannels_atrLength: Annotated[int, "Keltner Channels ATR length, default is 10"] = 10,
        chop_period: Annotated[int, "Chop period, default is 14"] = 14,
    ) -> str:
        """
        Retrieve bulk technical indicators from TAAPI.io for a given symbol and interval.
        Args:
            symbol (str): Ticker symbol of the asset, e.g. 'BTC'
            interval (str): Interval for the data, e.g. '1m', '5m', '1h', '1d'
        Returns:
            str: A formatted string containing the bulk technical indicators from TAAPI.io for the specified symbol and interval.
        """
        taapi_bulk_indicators_result = interface.get_taapi_bulk_indicators("BTC", "15m")
        return taapi_bulk_indicators_result

    @staticmethod
    @tool
    def get_reddit_posts(
        symbol: Annotated[str, "Ticker symbol of the asset, e.g. 'BTC'"],
        subreddit: Annotated[str, "Subreddit to search in, e.g. 'CryptoCurrency', 'CryptoMarkets', 'all'"] = "CryptoCurrency",
        sort: Annotated[str, "Sorting method for posts ('hot', 'new', 'top', etc.)"] = "hot",
        limit: Annotated[int, "Maximum number of posts to fetch"] = 25,
    ) -> str:
        """
        Fetch top posts from a specified subreddit related to a given ticker symbol.
        Args:
            symbol (str): Ticker symbol of the asset, e.g. 'BTC'
            subreddit (str): Subreddit to search in, e.g. 'CryptoCurrency', 'CryptoMarkets', 'all'
            sort (str): Sorting method for posts ('hot', 'new', 'top', etc.)
            limit (int): Maximum number of posts to fetch
        Returns:
            str: A formatted string containing the top posts from the specified subreddit related to the ticker symbol.
        """
        reddit_posts_result = interface.get_reddit_posts(symbol, subreddit, sort, limit)
        return reddit_posts_result

    @staticmethod
    @tool
    def get_google_news(
        query: Annotated[str, "Query to search with"],
        curr_date: Annotated[str, "Curr date in yyyy-mm-dd format"],
    ):
        """
        Retrieve the latest news from Google News based on a query and date range.
        Args:
            query (str): Query to search with
            curr_date (str): Current date in yyyy-mm-dd format
            look_back_days (int): How many days to look back
        Returns:
            str: A formatted string containing the latest news from Google News based on the query and date range.
        """

        google_news_results = interface.get_google_news(query, curr_date, 7)

        return google_news_results

    @staticmethod
    @tool
    def get_asset_news_llm(
        ticker: Annotated[str, "the asset's ticker"],
        curr_date: Annotated[str, "Current date in yyyy-mm-dd format"],
    ):
        """
        Retrieve the latest news about a given asset by using OpenAI's news API.
        Args:
            ticker (str): Ticker of a asset. e.g. BTC, ETH
            curr_date (str): Current date in yyyy-mm-dd format
        Returns:
            str: A formatted string containing the latest news about the asset on the given date.
        """

        openai_news_results = interface.get_asset_news_llm(ticker, curr_date)
        return openai_news_results

    @staticmethod
    @tool
    def get_global_news_llm(
        curr_date: Annotated[str, "Current date in yyyy-mm-dd format"],
    ):
        """
        Retrieve the latest macroeconomics news on a given date using OpenAI's macroeconomics news API.
        Args:
            curr_date (str): Current date in yyyy-mm-dd format
        Returns:
            str: A formatted string containing the latest macroeconomic news on the given date.
        """

        openai_news_results = interface.get_global_news_llm(curr_date)
        return openai_news_results

    @staticmethod
    @tool
    def get_fundamentals_llm(
        ticker: Annotated[str, "the asset's ticker"],
        curr_date: Annotated[str, "Current date in yyyy-mm-dd format"],
    ):
        """
        Retrieve the latest fundamental information about a given asset on a given date by using OpenAI's news API.
        Args:
            ticker (str): Ticker of a asset. e.g. BTC, ETH
            curr_date (str): Current date in yyyy-mm-dd format
        Returns:
            str: A formatted string containing the latest fundamental information about the asset on the given date.
        """

        openai_fundamentals_results = interface.get_fundamentals_llm(ticker, curr_date)
        return openai_fundamentals_results
