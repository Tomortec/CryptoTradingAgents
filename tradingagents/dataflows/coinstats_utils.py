
import os
import requests

def fetch_btc_dominance_from_coinstats():
    """
    Fetches the current Bitcoin dominance percentage from CoinStats API.
    
    Returns:
        dict: A dictionary containing Bitcoin dominance for 24 hours and 1 week. {"24h": value, "1w": value}
    """
    url_24h = "https://openapiv1.coinstats.app/insights/btc-dominance?type=24h"
    url_1w = "https://openapiv1.coinstats.app/insights/btc-dominance?type=1w"
    
    headers = {
        "accept": "application/json",
        "X-API-KEY": os.getenv("COINSTATS_API_KEY")
    }

    response_24h = requests.get(url_24h, headers=headers)
    response_1w = requests.get(url_1w, headers=headers)

    if response_24h.status_code == 200 and response_1w.status_code == 200:
        data_24h = response_24h.json()
        data_1w = response_1w.json()
        
        if "data" in data_24h and "data" in data_1w and \
            isinstance(data_24h["data"], list) and isinstance(data_1w["data"], list):
            btc_dominance_24h = data_24h["data"][-1][1]
            btc_dominance_1w = data_1w["data"][-1][1]
            return {"24h": btc_dominance_24h, "1w": btc_dominance_1w}
            
def fetch_news_from_coinstats():
    """
    Fetches the latest news from CoinStats API.
    
    Returns:
        list: A list of dictionaries containing news articles with keys: "title", "source", "description"
    """
    url = "https://openapiv1.coinstats.app/news/type/latest?page=1&limit=20"
    headers = {
        "accept": "application/json",
        "X-API-KEY": os.getenv("COINSTATS_API_KEY")
    }
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        data = response.json()
        if isinstance(data, list):
            return [
                {
                    "title": article.get("title", ""),
                    "description": article.get("description", ""),
                    "source": article.get("source", "")
                } for article in data
            ]