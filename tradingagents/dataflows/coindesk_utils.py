
import os
import requests

def fetch_news_from_coindesk(tickers=[], count=10) -> list[dict[str, str]]:
    """
    Fetches the latest news from Coindesk for a given ticker.
    
    Args:
        tickers (list): The ticker symbols for which to fetch news.
        count (int): The number of news articles to fetch. Default is 10.
        
    Returns:
        list: A list of news articles, each represented as a dictionary.
    """
    api_key = os.getenv('COINDESK_API_KEY')
    if not api_key:
        return None

    url = f"https://data-api.coindesk.com/news/v1/article/list?lang=EN&limit={count}&categories={','.join(tickers)}&api_key={api_key}"
    response = requests.get(url)
    
    if response.status_code == 200:
        data = response.json()
        if "Data" in data and isinstance(data["Data"], list):
            return list(map(lambda item: {
                "title": item.get("TITLE", ""),
                "categories": item.get("KEYWORDS", []),
                "body": item.get("BODY", ""),
            }, data["Data"]))
        return []
    else:
        print(f"Error: {response.status_code} - {response.text}")
        return []