from typing import Annotated, Dict
from .blockbeats_utils import fetch_news_from_blockbeats
from .coindesk_utils import fetch_news_from_coindesk
from .coinstats_utils import *
from .reddit_utils import fetch_posts_from_reddit
from .googlenews_utils import *
from .binance_utils import *
from .alternativeme_utils import fetch_fear_and_greed_from_alternativeme
from .taapi_utils import *
from dateutil.relativedelta import relativedelta
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from .utils import ts_to_time
import json
import os
import pandas as pd
from tqdm import tqdm
from openai import OpenAI
from .config import get_config, set_config, DATA_DIR

from warnings import deprecated
from .yfin_utils import *
from .stockstats_utils import *
from .finnhub_utils import get_data_in_range
import yfinance as yf

def get_blockbeats_news(count: Annotated[int, "news' count, no more than 30"] = 10):
    """
    Retrieve the latest top Blockbeats news
    Args:
        count (int): number of news to retrieve, no more than 30
    Returns:
        str: A formatted string containing the latest news articles and meta information
    """
    if count > 30:
        raise ValueError("Count should not be more than 30")

    news = fetch_news_from_blockbeats(count)

    if len(news) == 0:
        return ""

    news_str = ""
    for entry in news:
        news_str += f"### {entry['title']} ({entry['create_time']})\n\n{entry['content']}\n\n"

    return f"## Blockbeats News:\n\n{news_str}"

def get_coindesk_news(
    tickers: Annotated[list[str], "List of ticker symbols to fetch news for"] = [],
    count: Annotated[int, "Number of news articles to fetch, default is 10"] = 10,
) -> str:
    """
    Retrieve the latest top Coindesk news for given tickers.
    
    Args:
        tickers (list): List of ticker symbols to fetch news for.
        count (int): Number of news articles to fetch, default is 10.
        
    Returns:
        str: A formatted string containing the latest news articles and meta information.
    """
    news = fetch_news_from_coindesk(tickers, count)

    if len(news) == 0:
        return ""

    news_str = ""
    for entry in news:
        news_str += f"### {entry['title']} ({', '.join(entry['categories'])})\n\n{entry['body']}\n\n"

    return f"## Coindesk News:\n\n{news_str}"

def get_fear_and_greed_index() -> str:
    fng = fetch_fear_and_greed_from_alternativeme()
    return f"""## Fear and Greed Index: {fng[0]}\n0 means \"Extreme Fear\", while 100 means \"Extreme Greed\"\nPrevious daily FnG: {','.join(fng[1:])}"""

def get_coinstats_btc_dominance() -> str:
    """
    Fetch the current Bitcoin dominance percentage from CoinStats API.

    Returns:
        str: A formatted string containing Bitcoin dominance for 24 hours and 1 week.
    """
    btc_dominance = fetch_btc_dominance_from_coinstats()
    return f"## Bitcoin Dominance:\n24h: {btc_dominance['24h']}%, 1week: {btc_dominance['1w']}%"

def get_taapi_single_indicator(
    symbol: Annotated[str, "ticker symbol of the asset"],
    indicator: Annotated[
        str,
        "Technical analysis indicator to fetch, e.g., 'sma', 'ema', 'rsi', 'macd', etc.",
    ],
    interval: Annotated[str, "time interval for the data, e.g., '1m', '5m', '1h'"] = "15m",
) -> str:
    """
    Fetch technical analysis indicators for a given symbol and interval.

    Args:
        symbol (str): The trading pair symbol (e.g., 'BTCUSDT').
        indicator (str): The technical analysis indicator to fetch (e.g., 'sma', 'ema', 'rsi', 'macd').
        interval (str): The time interval for the data (e.g., '1m', '5m', '1h').

    Returns:
        str: A formatted string containing the latest technical analysis indicators.
    """
    ta_data = fetch_ta_from_taapi(symbol, indicator, interval)
    return f"## {symbol} Technical Analysis ({indicator}) at {interval}: {ta_data}\n"

def get_taapi_bulk_indicators(
    symbol: Annotated[str, "ticker symbol of the asset"],
    interval: Annotated[str, "time interval for the data, e.g., '1m', '5m', '1h'"] = "15m",
    **kwargs: dict
) -> str:
    """
    Fetch bulk technical analysis indicators for a given symbol and interval.

    Args:
        symbol (str): The trading pair symbol (e.g., 'BTC/USDT').
        interval (str): The time interval for the data (e.g., '1m', '5m', '1h').
        **kwargs: Additional parameters for the indicators.
    Returns:
        str: A formatted string containing the latest technical analysis indicators.
    """
    bulk = TAAPIBulkUtils(symbol, bulk_interval=interval, **kwargs)
    trend_momentum = bulk.fetch_trend_momentum_indicators_from_taapi()
    volatility_structure = bulk.fetch_volatility_structure_indicators_from_taapi()
    return f"## {symbol} Trend and Momentum Indicators at {interval}:\n{trend_momentum}\n\n" + \
            f"## {symbol} Volatility and Pattern Indicators at {interval}:\n{volatility_structure}\n"

def get_coinstats_news() -> str:
    """
    Fetch the latest news from CoinStats API.

    Returns:
        str: A formatted string containing the latest news articles and meta information.
    """
    news = fetch_news_from_coinstats()
    if len(news) == 0:
        return ""
    news_str = ""
    for article in news:
        news_str += f"### {article['title']} (source: {article['source']})\n{article['description']}\n\n"
    return f"## CoinStats News:\n{news_str}"

def get_google_news(
    query: Annotated[str, "Query to search with"],
    curr_date: Annotated[str, "Curr date in yyyy-mm-dd format"],
    look_back_days: Annotated[int, "how many days to look back"],
) -> str:
    query = query.replace(" ", "+")

    start_date = datetime.strptime(curr_date, "%Y-%m-%d")
    before = start_date - relativedelta(days=look_back_days)
    before = before.strftime("%Y-%m-%d")

    news_results = getNewsData(query, before, curr_date)

    news_str = ""

    for news in news_results:
        news_str += (
            f"### {news['title']} (source: {news['source']}) \n\n{news['snippet']}\n\n"
        )

    if len(news_results) == 0:
        return ""

    return f"## {query} Google News, from {before} to {curr_date}:\n\n{news_str}"

def get_reddit_posts(
    symbol: Annotated[str, "ticker symbol of the asset"],
    subreddit_name: Annotated[str, "name of the subreddit to fetch posts from, e.g., 'CryptoCurrency', 'CryptoMarkets', 'all'"],
    sort: Annotated[str, "sorting method for posts ('hot', 'new', 'top', etc.)", "default is 'hot'"] = "hot",
    limit: Annotated[int, "maximum number of posts to fetch, default is 25"] = 25,
) -> str:
    """
    Fetch top posts from a specified subreddit.

    Args:
        symbol (str): The ticker symbol of the asset to filter posts.
        subreddit_name (str): The name of the subreddit to fetch posts from.
        sort (str): The sorting method for posts ('hot', 'new', 'top', etc.).
        limit (int): The maximum number of posts to fetch.

    Returns:
        str: A formatted string containing the top posts from the subreddit.
    """
    posts = fetch_posts_from_reddit(symbol, subreddit_name, sort, limit)
    if len(posts) == 0:
        return ""

    posts_str = ""
    for post in posts:
        posts_str += f"### {post['title']} (score: {post['score']}, created at: {datetime.utcfromtimestamp(post['created_utc']).strftime('%Y-%m-%d %H:%M:%S')})\n{post['content']}\n\n"

    return f"## Reddit Posts in r/{subreddit_name} for {symbol}:\n{posts_str}"

def get_binance_ohlcv(
    symbol: Annotated[str, "ticker symbol of the asset"],
    interval: Annotated[str, "time interval for the data, e.g., '1m', '5m', '1h'"],
) -> str:
    """
    Fetch the latest OHLCV (Open, High, Low, Close, Volume) data from Binance for a given symbol and interval.

    Args:
        symbol (str): The trading pair symbol (e.g., 'BTCUSDT').
        interval (str): The time interval for the OHLCV data (e.g., '1m', '5m', '1h').
    Returns:
        str: A formatted string containing the latest OHLCV data.
    """
    symbol = symbol.upper().strip()
    if not symbol.endswith("USDT"):
        symbol += "USDT"

    ohlcv = fetch_ohlcv_from_binance(symbol, interval)
    if ohlcv is dict:
        return (
            f"## {symbol} Futures **Latest OHLCV Data** in last {interval}:\n"
            f"Open: {ohlcv['open']}, High: {ohlcv['high']}, Low: {ohlcv['low']}, Close: {ohlcv['close']}, Volume: {ohlcv['volume']}\n"
        )

def get_binance_data(
    symbol: Annotated[str, "ticker symbol of the asset"],
    interval: Annotated[str, "time interval for the data, e.g., '1m', '5m', '1h'"],
    klines_limit: Annotated[int, "maximum number of klines to fetch, default is 75"] = 75,
    depth_limit: Annotated[int, "maximum number of bids and asks to fetch, default is 50"] = 50,
    longshort_limit: Annotated[int, "maximum number of long/short ratios to fetch, default is 50"] = 50,
) -> str:
    """
    Fetch historical futures data from Binance for a given symbol and interval.

    Args:
        symbol (str): The trading pair symbol (e.g., 'BTCUSDT').
        interval (str): The time interval for the klines (e.g., '1m', '5m', '1h').
        klines_limit (int): The maximum number of klines to fetch (default is 75).
        depth_limit (int): The maximum number of bids and asks to fetch (default is 50).
        longshort_limit (int): The maximum number of long/short ratios to fetch (default is 50).
        
    Returns:
        str: A formatted string containing the historical futures data.
    """
    symbol = symbol.upper().strip()
    if not symbol.endswith("USDT"):
        symbol += "USDT"  # Ensure the symbol ends with USDT for futures

    klines_str = ""
    klines = fetch_klines_from_binance(symbol, interval, klines_limit)
    if klines is not None and len(klines) != 0:
        klines = list(map(lambda x: { "t": x[0], "o": x[1], "h": x[2], "l": x[3], "c": x[4], "v": x[5] }, klines))
        klines_str = f"## {symbol} Futures **KLines Data** for {interval} interval:\n" + "\n".join(
            [f"{ts_to_time(int(entry["t"]) / 1000)}: Open: {entry["o"]}, High: {entry["h"]}, Low: {entry["l"]}, Close: {entry["c"]}, Volume: {entry["v"]}" for entry in klines]
        ) + "\n\n"
    
    depth_str = ""
    depth = fetch_depth_from_binance(symbol, depth_limit)
    if depth is not None and isinstance(depth, dict):
        bids = depth.get("bids", [-1, -1])
        asks = depth.get("asks", [-1, -1])
        depth = { "bids": { "price": bids[0], "volume": bids[1] }, "asks": { "price": asks[0], "volume": asks[1] } }
        depth_str = f"## {symbol} Futures **Current Depth Data**:\nBids: Price: {depth["bids"]["price"]}, Volume: {depth["bids"]["volume"]}\nAsks: Price: {depth["asks"]["price"]}, Volume: {depth["asks"]["volume"]}\n\n"

    ticker_24hr_str = ""
    ticker_24hr = fetch_24hr_pricechange_from_binance(symbol)
    if ticker_24hr is not None and isinstance(ticker_24hr, dict):
        ticker_24hr_str = f"## {symbol} Futures **24-Hour Price Change**:\nPrice Change: {ticker_24hr.get("priceChange", "N/A")}, Price Change Percent: {ticker_24hr.get("priceChangePercent", "N/A")}, Weighted Avg Price: {ticker_24hr.get("weightedAvgPrice", "N/A")}\n\n"

    top_longshort_position_ratio_str = ""
    top_longshort_position_ratio = fetch_toplongshort_position_ratio_from_binance(symbol, interval, longshort_limit)
    if top_longshort_position_ratio is not None and isinstance(top_longshort_position_ratio, list):
        top_longshort_position_ratio = [
            { "t": entry["timestamp"], "longShortRatio": entry["longShortRatio"] }
            for entry in top_longshort_position_ratio
        ]
        top_longshort_position_ratio_str = f"## {symbol} Futures **Top Long/Short Position Ratio**:\n" + "\n".join(
            [f"{ts_to_time(int(entry["t"]) / 1000)}: Long/Short Ratio: {entry["longShortRatio"]}" for entry in top_longshort_position_ratio]
        ) + "\n\n"

    top_longshort_account_ratio_str = ""
    top_longshort_account_ratio = fetch_toplongshort_account_ratio_from_binance(symbol, interval, longshort_limit)
    if top_longshort_account_ratio is not None and isinstance(top_longshort_account_ratio, list):
        top_longshort_account_ratio = [
            { "t": entry["timestamp"], "longShortRatio": entry["longShortRatio"] }
            for entry in top_longshort_account_ratio
        ]
        top_longshort_account_ratio_str = f"## {symbol} Futures **Top Long/Short Account Ratio**:\n" + "\n".join(
            [f"{ts_to_time(int(entry["t"]) / 1000)}: Long/Short Ratio: {entry["longShortRatio"]}" for entry in top_longshort_account_ratio]
        ) + "\n\n"

    global_longshort_account_ratio_str = ""
    global_longshort_account_ratio = fetch_global_longshort_account_ratio_from_binance(symbol, interval, longshort_limit)
    if global_longshort_account_ratio is not None and isinstance(global_longshort_account_ratio, list):
        global_longshort_account_ratio = [
            { "t": entry["timestamp"], "longShortRatio": entry["longShortRatio"] }
            for entry in global_longshort_account_ratio
        ]
        global_longshort_account_ratio_str = f"## {symbol} Futures **Global Long/Short Account Ratio**:\n" + "\n".join(
            [f"{ts_to_time(int(entry["t"]) / 1000)}: Long/Short Ratio: {entry["longShortRatio"]}" for entry in global_longshort_account_ratio]
        ) + "\n\n"

    taker_longshort_ratio_str = ""
    taker_longshort_ratio = fetch_taker_longshort_ratio_from_binance(symbol, interval, longshort_limit)
    if taker_longshort_ratio is not None and isinstance(taker_longshort_ratio, list):
        taker_longshort_ratio = [
            { "t": entry["timestamp"], "buySellRatio": entry["buySellRatio"], "buyVol": entry["buyVol"], "sellVol": entry["sellVol"] }
            for entry in taker_longshort_ratio
        ]
        taker_longshort_ratio_str = f"## {symbol} Futures **Taker Long/Short Ratio**:\n" + "\n".join(
            [f"{ts_to_time(int(entry["t"]) / 1000)}: Long/Short Ratio: {entry["buySellRatio"]}, Buy Volume: {entry["buyVol"]}, Sell Volume: {entry["sellVol"]}" for entry in taker_longshort_ratio]
        ) + "\n\n"

    return (
        f"## {symbol} Futures Data:\n\n"
        + klines_str
        + depth_str
        + ticker_24hr_str
        + top_longshort_position_ratio_str
        + top_longshort_account_ratio_str
        + global_longshort_account_ratio_str
        + taker_longshort_ratio_str
    )

def get_stock_news_openai(ticker, curr_date):
    config = get_config()
    client = OpenAI(
        base_url=config["backend_url"],
        api_key=os.getenv(config["api_key_env_name"])
    )

    response = client.responses.create(
        model=config["quick_think_llm"],
        input=[
            {
                "role": "system",
                "content": [
                    {
                        "type": "input_text",
                        "text": f"Can you search Social Media for {ticker} from 7 days before {curr_date} to {curr_date}? Make sure you only get the data posted during that period.",
                    }
                ],
            }
        ],
        text={"format": {"type": "text"}},
        reasoning={},
        tools=[
            {
                "type": "web_search_preview",
                "user_location": {"type": "approximate"},
                "search_context_size": "low",
            }
        ],
        temperature=1,
        max_output_tokens=4096,
        top_p=1,
        store=True,
    )

    return response.output[1].content[0].text

def get_global_news_openai(curr_date):
    config = get_config()
    client = OpenAI(
        base_url=config["backend_url"],
        api_key=os.getenv(config["api_key_env_name"])
    )

    response = client.responses.create(
        model=config["quick_think_llm"],
        input=[
            {
                "role": "system",
                "content": [
                    {
                        "type": "input_text",
                        "text": f"Can you search global or macroeconomics news from 7 days before {curr_date} to {curr_date} that would be informative for trading purposes? Make sure you only get the data posted during that period.",
                    }
                ],
            }
        ],
        text={"format": {"type": "text"}},
        reasoning={},
        tools=[
            {
                "type": "web_search_preview",
                "user_location": {"type": "approximate"},
                "search_context_size": "low",
            }
        ],
        temperature=1,
        max_output_tokens=4096,
        top_p=1,
        store=True,
    )

    return response.output[1].content[0].text

def get_fundamentals_openai(ticker, curr_date):
    config = get_config()
    client = OpenAI(
        base_url=config["backend_url"],
        api_key=os.getenv(config["api_key_env_name"])
    )

    response = client.responses.create(
        model=config["quick_think_llm"],
        input=[
            {
                "role": "system",
                "content": [
                    {
                        "type": "input_text",
                        "text": f"Can you search Fundamental for discussions on {ticker} during of the month before {curr_date} to the month of {curr_date}. Make sure you only get the data posted during that period. List as a table, with PE/PS/Cash flow/ etc",
                    }
                ],
            }
        ],
        text={"format": {"type": "text"}},
        reasoning={},
        tools=[
            {
                "type": "web_search_preview",
                "user_location": {"type": "approximate"},
                "search_context_size": "low",
            }
        ],
        temperature=1,
        max_output_tokens=4096,
        top_p=1,
        store=True,
    )

    return response.output[1].content[0].text

#region Deprecated Stock Utilities
@deprecated("Utilities only for stocks are deprecated.")
def get_finnhub_news(
    ticker: Annotated[
        str,
        "Search query of a asset's, e.g. 'AAPL, TSM, etc.",
    ],
    curr_date: Annotated[str, "Current date in yyyy-mm-dd format"],
    look_back_days: Annotated[int, "how many days to look back"],
):
    """
    Retrieve news about a asset within a time frame

    Args
        ticker (str): ticker for the asset you are interested in
        start_date (str): Start date in yyyy-mm-dd format
        end_date (str): End date in yyyy-mm-dd format
    Returns
        str: dataframe containing the news of the asset in the time frame

    """

    start_date = datetime.strptime(curr_date, "%Y-%m-%d")
    before = start_date - relativedelta(days=look_back_days)
    before = before.strftime("%Y-%m-%d")

    result = get_data_in_range(ticker, before, curr_date, "news_data", DATA_DIR)

    if len(result) == 0:
        return ""

    combined_result = ""
    for day, data in result.items():
        if len(data) == 0:
            continue
        for entry in data:
            current_news = (
                "### " + entry["headline"] + f" ({day})" + "\n" + entry["summary"]
            )
            combined_result += current_news + "\n\n"

    return f"## {ticker} News, from {before} to {curr_date}:\n" + str(combined_result)

@deprecated("Utilities only for stocks are deprecated.")
def get_finnhub_asset_insider_sentiment(
    ticker: Annotated[str, "ticker symbol for the asset"],
    curr_date: Annotated[
        str,
        "current date of you are trading at, yyyy-mm-dd",
    ],
    look_back_days: Annotated[int, "number of days to look back"],
):
    """
    Retrieve insider sentiment about a asset (retrieved from public SEC information) for the past 15 days
    Args:
        ticker (str): ticker symbol of the asset
        curr_date (str): current date you are trading on, yyyy-mm-dd
    Returns:
        str: a report of the sentiment in the past 15 days starting at curr_date
    """

    date_obj = datetime.strptime(curr_date, "%Y-%m-%d")
    before = date_obj - relativedelta(days=look_back_days)
    before = before.strftime("%Y-%m-%d")

    data = get_data_in_range(ticker, before, curr_date, "insider_senti", DATA_DIR)

    if len(data) == 0:
        return ""

    result_str = ""
    seen_dicts = []
    for date, senti_list in data.items():
        for entry in senti_list:
            if entry not in seen_dicts:
                result_str += f"### {entry['year']}-{entry['month']}:\nChange: {entry['change']}\nMonthly Share Purchase Ratio: {entry['mspr']}\n\n"
                seen_dicts.append(entry)

    return (
        f"## {ticker} Insider Sentiment Data for {before} to {curr_date}:\n"
        + result_str
        + "The change field refers to the net buying/selling from all insiders' transactions. The mspr field refers to monthly share purchase ratio."
    )

@deprecated("Utilities only for stocks are deprecated.")
def get_finnhub_asset_insider_transactions(
    ticker: Annotated[str, "ticker symbol"],
    curr_date: Annotated[
        str,
        "current date you are trading at, yyyy-mm-dd",
    ],
    look_back_days: Annotated[int, "how many days to look back"],
):
    """
    Retrieve insider transcaction information about a asset (retrieved from public SEC information) for the past 15 days
    Args:
        ticker (str): ticker symbol of the asset
        curr_date (str): current date you are trading at, yyyy-mm-dd
    Returns:
        str: a report of the asset's insider transaction/trading informtaion in the past 15 days
    """

    date_obj = datetime.strptime(curr_date, "%Y-%m-%d")
    before = date_obj - relativedelta(days=look_back_days)
    before = before.strftime("%Y-%m-%d")

    data = get_data_in_range(ticker, before, curr_date, "insider_trans", DATA_DIR)

    if len(data) == 0:
        return ""

    result_str = ""

    seen_dicts = []
    for date, senti_list in data.items():
        for entry in senti_list:
            if entry not in seen_dicts:
                result_str += f"### Filing Date: {entry['filingDate']}, {entry['name']}:\nChange:{entry['change']}\nShares: {entry['share']}\nTransaction Price: {entry['transactionPrice']}\nTransaction Code: {entry['transactionCode']}\n\n"
                seen_dicts.append(entry)

    return (
        f"## {ticker} insider transactions from {before} to {curr_date}:\n"
        + result_str
        + "The change field reflects the variation in share count—here a negative number indicates a reduction in holdings—while share specifies the total number of shares involved. The transactionPrice denotes the per-share price at which the trade was executed, and transactionDate marks when the transaction occurred. The name field identifies the insider making the trade, and transactionCode (e.g., S for sale) clarifies the nature of the transaction. FilingDate records when the transaction was officially reported, and the unique id links to the specific SEC filing, as indicated by the source. Additionally, the symbol ties the transaction to a particular asset, isDerivative flags whether the trade involves derivative securities, and currency notes the currency context of the transaction."
    )

@deprecated("Utilities only for stocks are deprecated.")
def get_simfin_balance_sheet(
    ticker: Annotated[str, "ticker symbol"],
    freq: Annotated[
        str,
        "reporting frequency of the asset's financial history: annual / quarterly",
    ],
    curr_date: Annotated[str, "current date you are trading at, yyyy-mm-dd"],
):
    data_path = os.path.join(
        DATA_DIR,
        "fundamental_data",
        "simfin_data_all",
        "balance_sheet",
        "companies",
        "us",
        f"us-balance-{freq}.csv",
    )
    df = pd.read_csv(data_path, sep=";")

    # Convert date strings to datetime objects and remove any time components
    df["Report Date"] = pd.to_datetime(df["Report Date"], utc=True).dt.normalize()
    df["Publish Date"] = pd.to_datetime(df["Publish Date"], utc=True).dt.normalize()

    # Convert the current date to datetime and normalize
    curr_date_dt = pd.to_datetime(curr_date, utc=True).normalize()

    # Filter the DataFrame for the given ticker and for reports that were published on or before the current date
    filtered_df = df[(df["Ticker"] == ticker) & (df["Publish Date"] <= curr_date_dt)]

    # Check if there are any available reports; if not, return a notification
    if filtered_df.empty:
        print("No balance sheet available before the given current date.")
        return ""

    # Get the most recent balance sheet by selecting the row with the latest Publish Date
    latest_balance_sheet = filtered_df.loc[filtered_df["Publish Date"].idxmax()]

    # drop the SimFinID column
    latest_balance_sheet = latest_balance_sheet.drop("SimFinId")

    return (
        f"## {freq} balance sheet for {ticker} released on {str(latest_balance_sheet['Publish Date'])[0:10]}: \n"
        + str(latest_balance_sheet)
        + "\n\nThis includes metadata like reporting dates and currency, share details, and a breakdown of assets, liabilities, and equity. Assets are grouped as current (liquid items like cash and receivables) and noncurrent (long-term investments and property). Liabilities are split between short-term obligations and long-term debts, while equity reflects shareholder funds such as paid-in capital and retained earnings. Together, these components ensure that total assets equal the sum of liabilities and equity."
    )

@deprecated("Utilities only for stocks are deprecated.")
def get_simfin_cashflow(
    ticker: Annotated[str, "ticker symbol"],
    freq: Annotated[
        str,
        "reporting frequency of the asset's financial history: annual / quarterly",
    ],
    curr_date: Annotated[str, "current date you are trading at, yyyy-mm-dd"],
):
    data_path = os.path.join(
        DATA_DIR,
        "fundamental_data",
        "simfin_data_all",
        "cash_flow",
        "companies",
        "us",
        f"us-cashflow-{freq}.csv",
    )
    df = pd.read_csv(data_path, sep=";")

    # Convert date strings to datetime objects and remove any time components
    df["Report Date"] = pd.to_datetime(df["Report Date"], utc=True).dt.normalize()
    df["Publish Date"] = pd.to_datetime(df["Publish Date"], utc=True).dt.normalize()

    # Convert the current date to datetime and normalize
    curr_date_dt = pd.to_datetime(curr_date, utc=True).normalize()

    # Filter the DataFrame for the given ticker and for reports that were published on or before the current date
    filtered_df = df[(df["Ticker"] == ticker) & (df["Publish Date"] <= curr_date_dt)]

    # Check if there are any available reports; if not, return a notification
    if filtered_df.empty:
        print("No cash flow statement available before the given current date.")
        return ""

    # Get the most recent cash flow statement by selecting the row with the latest Publish Date
    latest_cash_flow = filtered_df.loc[filtered_df["Publish Date"].idxmax()]

    # drop the SimFinID column
    latest_cash_flow = latest_cash_flow.drop("SimFinId")

    return (
        f"## {freq} cash flow statement for {ticker} released on {str(latest_cash_flow['Publish Date'])[0:10]}: \n"
        + str(latest_cash_flow)
        + "\n\nThis includes metadata like reporting dates and currency, share details, and a breakdown of cash movements. Operating activities show cash generated from core business operations, including net income adjustments for non-cash items and working capital changes. Investing activities cover asset acquisitions/disposals and investments. Financing activities include debt transactions, equity issuances/repurchases, and dividend payments. The net change in cash represents the overall increase or decrease in the asset's cash position during the reporting period."
    )

@deprecated("Utilities only for stocks are deprecated.")
def get_simfin_income_statements(
    ticker: Annotated[str, "ticker symbol"],
    freq: Annotated[
        str,
        "reporting frequency of the asset's financial history: annual / quarterly",
    ],
    curr_date: Annotated[str, "current date you are trading at, yyyy-mm-dd"],
):
    data_path = os.path.join(
        DATA_DIR,
        "fundamental_data",
        "simfin_data_all",
        "income_statements",
        "companies",
        "us",
        f"us-income-{freq}.csv",
    )
    df = pd.read_csv(data_path, sep=";")

    # Convert date strings to datetime objects and remove any time components
    df["Report Date"] = pd.to_datetime(df["Report Date"], utc=True).dt.normalize()
    df["Publish Date"] = pd.to_datetime(df["Publish Date"], utc=True).dt.normalize()

    # Convert the current date to datetime and normalize
    curr_date_dt = pd.to_datetime(curr_date, utc=True).normalize()

    # Filter the DataFrame for the given ticker and for reports that were published on or before the current date
    filtered_df = df[(df["Ticker"] == ticker) & (df["Publish Date"] <= curr_date_dt)]

    # Check if there are any available reports; if not, return a notification
    if filtered_df.empty:
        print("No income statement available before the given current date.")
        return ""

    # Get the most recent income statement by selecting the row with the latest Publish Date
    latest_income = filtered_df.loc[filtered_df["Publish Date"].idxmax()]

    # drop the SimFinID column
    latest_income = latest_income.drop("SimFinId")

    return (
        f"## {freq} income statement for {ticker} released on {str(latest_income['Publish Date'])[0:10]}: \n"
        + str(latest_income)
        + "\n\nThis includes metadata like reporting dates and currency, share details, and a comprehensive breakdown of the asset's financial performance. Starting with Revenue, it shows Cost of Revenue and resulting Gross Profit. Operating Expenses are detailed, including SG&A, R&D, and Depreciation. The statement then shows Operating Income, followed by non-operating items and Interest Expense, leading to Pretax Income. After accounting for Income Tax and any Extraordinary items, it concludes with Net Income, representing the asset's bottom-line profit or loss for the period."
    )

@deprecated("Utilities only for stocks are deprecated.")
def get_stock_stats_indicators_window(
    symbol: Annotated[str, "ticker symbol of the asset"],
    indicator: Annotated[str, "technical indicator to get the analysis and report of"],
    curr_date: Annotated[
        str, "The current trading date you are trading on, YYYY-mm-dd"
    ],
    look_back_days: Annotated[int, "how many days to look back"],
    online: Annotated[bool, "to fetch data online or offline"],
) -> str:

    best_ind_params = {
        # Moving Averages
        "close_50_sma": (
            "50 SMA: A medium-term trend indicator. "
            "Usage: Identify trend direction and serve as dynamic support/resistance. "
            "Tips: It lags price; combine with faster indicators for timely signals."
        ),
        "close_200_sma": (
            "200 SMA: A long-term trend benchmark. "
            "Usage: Confirm overall market trend and identify golden/death cross setups. "
            "Tips: It reacts slowly; best for strategic trend confirmation rather than frequent trading entries."
        ),
        "close_10_ema": (
            "10 EMA: A responsive short-term average. "
            "Usage: Capture quick shifts in momentum and potential entry points. "
            "Tips: Prone to noise in choppy markets; use alongside longer averages for filtering false signals."
        ),
        # MACD Related
        "macd": (
            "MACD: Computes momentum via differences of EMAs. "
            "Usage: Look for crossovers and divergence as signals of trend changes. "
            "Tips: Confirm with other indicators in low-volatility or sideways markets."
        ),
        "macds": (
            "MACD Signal: An EMA smoothing of the MACD line. "
            "Usage: Use crossovers with the MACD line to trigger trades. "
            "Tips: Should be part of a broader strategy to avoid false positives."
        ),
        "macdh": (
            "MACD Histogram: Shows the gap between the MACD line and its signal. "
            "Usage: Visualize momentum strength and spot divergence early. "
            "Tips: Can be volatile; complement with additional filters in fast-moving markets."
        ),
        # Momentum Indicators
        "rsi": (
            "RSI: Measures momentum to flag overbought/oversold conditions. "
            "Usage: Apply 70/30 thresholds and watch for divergence to signal reversals. "
            "Tips: In strong trends, RSI may remain extreme; always cross-check with trend analysis."
        ),
        # Volatility Indicators
        "boll": (
            "Bollinger Middle: A 20 SMA serving as the basis for Bollinger Bands. "
            "Usage: Acts as a dynamic benchmark for price movement. "
            "Tips: Combine with the upper and lower bands to effectively spot breakouts or reversals."
        ),
        "boll_ub": (
            "Bollinger Upper Band: Typically 2 standard deviations above the middle line. "
            "Usage: Signals potential overbought conditions and breakout zones. "
            "Tips: Confirm signals with other tools; prices may ride the band in strong trends."
        ),
        "boll_lb": (
            "Bollinger Lower Band: Typically 2 standard deviations below the middle line. "
            "Usage: Indicates potential oversold conditions. "
            "Tips: Use additional analysis to avoid false reversal signals."
        ),
        "atr": (
            "ATR: Averages true range to measure volatility. "
            "Usage: Set stop-loss levels and adjust position sizes based on current market volatility. "
            "Tips: It's a reactive measure, so use it as part of a broader risk management strategy."
        ),
        # Volume-Based Indicators
        "vwma": (
            "VWMA: A moving average weighted by volume. "
            "Usage: Confirm trends by integrating price action with volume data. "
            "Tips: Watch for skewed results from volume spikes; use in combination with other volume analyses."
        ),
        "mfi": (
            "MFI: The Money Flow Index is a momentum indicator that uses both price and volume to measure buying and selling pressure. "
            "Usage: Identify overbought (>80) or oversold (<20) conditions and confirm the strength of trends or reversals. "
            "Tips: Use alongside RSI or MACD to confirm signals; divergence between price and MFI can indicate potential reversals."
        ),
    }

    if indicator not in best_ind_params:
        raise ValueError(
            f"Indicator {indicator} is not supported. Please choose from: {list(best_ind_params.keys())}"
        )

    end_date = curr_date
    curr_date = datetime.strptime(curr_date, "%Y-%m-%d")
    before = curr_date - relativedelta(days=look_back_days)

    if not online:
        # read from YFin data
        data = pd.read_csv(
            os.path.join(
                DATA_DIR,
                f"market_data/price_data/{symbol}-YFin-data-2015-01-01-2025-03-25.csv",
            )
        )
        data["Date"] = pd.to_datetime(data["Date"], utc=True)
        dates_in_df = data["Date"].astype(str).str[:10]

        ind_string = ""
        while curr_date >= before:
            # only do the trading dates
            if curr_date.strftime("%Y-%m-%d") in dates_in_df.values:
                indicator_value = get_stockstats_indicator(
                    symbol, indicator, curr_date.strftime("%Y-%m-%d"), online
                )

                ind_string += f"{curr_date.strftime('%Y-%m-%d')}: {indicator_value}\n"

            curr_date = curr_date - relativedelta(days=1)
    else:
        # online gathering
        ind_string = ""
        while curr_date >= before:
            indicator_value = get_stockstats_indicator(
                symbol, indicator, curr_date.strftime("%Y-%m-%d"), online
            )

            ind_string += f"{curr_date.strftime('%Y-%m-%d')}: {indicator_value}\n"

            curr_date = curr_date - relativedelta(days=1)

    result_str = (
        f"## {indicator} values from {before.strftime('%Y-%m-%d')} to {end_date}:\n\n"
        + ind_string
        + "\n\n"
        + best_ind_params.get(indicator, "No description available.")
    )

    return result_str

@deprecated("Utilities only for stocks are deprecated.")
def get_stockstats_indicator(
    symbol: Annotated[str, "ticker symbol of the asset"],
    indicator: Annotated[str, "technical indicator to get the analysis and report of"],
    curr_date: Annotated[
        str, "The current trading date you are trading on, YYYY-mm-dd"
    ],
    online: Annotated[bool, "to fetch data online or offline"],
) -> str:

    curr_date = datetime.strptime(curr_date, "%Y-%m-%d")
    curr_date = curr_date.strftime("%Y-%m-%d")

    try:
        indicator_value = StockstatsUtils.get_stock_stats(
            symbol,
            indicator,
            curr_date,
            os.path.join(DATA_DIR, "market_data", "price_data"),
            online=online,
        )
    except Exception as e:
        print(
            f"Error getting stockstats indicator data for indicator {indicator} on {curr_date}: {e}"
        )
        return ""

    return str(indicator_value)

@deprecated("Utilities only for stocks are deprecated.")
def get_YFin_data_window(
    symbol: Annotated[str, "ticker symbol of the asset"],
    curr_date: Annotated[str, "Start date in yyyy-mm-dd format"],
    look_back_days: Annotated[int, "how many days to look back"],
) -> str:
    # calculate past days
    date_obj = datetime.strptime(curr_date, "%Y-%m-%d")
    before = date_obj - relativedelta(days=look_back_days)
    start_date = before.strftime("%Y-%m-%d")

    # read in data
    data = pd.read_csv(
        os.path.join(
            DATA_DIR,
            f"market_data/price_data/{symbol}-YFin-data-2015-01-01-2025-03-25.csv",
        )
    )

    # Extract just the date part for comparison
    data["DateOnly"] = data["Date"].str[:10]

    # Filter data between the start and end dates (inclusive)
    filtered_data = data[
        (data["DateOnly"] >= start_date) & (data["DateOnly"] <= curr_date)
    ]

    # Drop the temporary column we created
    filtered_data = filtered_data.drop("DateOnly", axis=1)

    # Set pandas display options to show the full DataFrame
    with pd.option_context(
        "display.max_rows", None, "display.max_columns", None, "display.width", None
    ):
        df_string = filtered_data.to_string()

    return (
        f"## Raw Market Data for {symbol} from {start_date} to {curr_date}:\n\n"
        + df_string
    )

@deprecated("Utilities only for stocks are deprecated.")
def get_YFin_data_online(
    symbol: Annotated[str, "ticker symbol of the asset"],
    start_date: Annotated[str, "Start date in yyyy-mm-dd format"],
    end_date: Annotated[str, "Start date in yyyy-mm-dd format"],
):

    datetime.strptime(start_date, "%Y-%m-%d")
    datetime.strptime(end_date, "%Y-%m-%d")

    # Create ticker object
    ticker = yf.Ticker(symbol.upper())

    # Fetch historical data for the specified date range
    data = ticker.history(start=start_date, end=end_date)

    # Check if data is empty
    if data.empty:
        return (
            f"No data found for symbol '{symbol}' between {start_date} and {end_date}"
        )

    # Remove timezone info from index for cleaner output
    if data.index.tz is not None:
        data.index = data.index.tz_localize(None)

    # Round numerical values to 2 decimal places for cleaner display
    numeric_columns = ["Open", "High", "Low", "Close", "Adj Close"]
    for col in numeric_columns:
        if col in data.columns:
            data[col] = data[col].round(2)

    # Convert DataFrame to CSV string
    csv_string = data.to_csv()

    # Add header information
    header = f"# Stock data for {symbol.upper()} from {start_date} to {end_date}\n"
    header += f"# Total records: {len(data)}\n"
    header += f"# Data retrieved on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"

    return header + csv_string

@deprecated("Utilities only for stocks are deprecated.")
def get_YFin_data(
    symbol: Annotated[str, "ticker symbol of the asset"],
    start_date: Annotated[str, "Start date in yyyy-mm-dd format"],
    end_date: Annotated[str, "Start date in yyyy-mm-dd format"],
) -> str:
    # read in data
    data = pd.read_csv(
        os.path.join(
            DATA_DIR,
            f"market_data/price_data/{symbol}-YFin-data-2015-01-01-2025-03-25.csv",
        )
    )

    if end_date > "2025-03-25":
        raise Exception(
            f"Get_YFin_Data: {end_date} is outside of the data range of 2015-01-01 to 2025-03-25"
        )

    # Extract just the date part for comparison
    data["DateOnly"] = data["Date"].str[:10]

    # Filter data between the start and end dates (inclusive)
    filtered_data = data[
        (data["DateOnly"] >= start_date) & (data["DateOnly"] <= end_date)
    ]

    # Drop the temporary column we created
    filtered_data = filtered_data.drop("DateOnly", axis=1)

    # remove the index from the dataframe
    filtered_data = filtered_data.reset_index(drop=True)

    return filtered_data
#endregion