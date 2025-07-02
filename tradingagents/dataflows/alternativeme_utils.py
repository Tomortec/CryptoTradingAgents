
import requests

def fetch_fear_and_greed_from_alternativeme():
    """
    Fetch the Fear and Greed Index from Alternative.me API.
    Returns:
        list[str]: A list of fear and greed index values. Sorted by date in descending order.
    """
    url = "https://api.alternative.me/fng/?limit=10"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        if "data" in data and len(data["data"]) > 0:
            return [value["value"] for value in data["data"] if "value" in value]