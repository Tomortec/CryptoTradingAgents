
import requests

def fetch_news_from_blockbeats(count = 10):
    url = f"https://api.theblockbeats.news/v1/open-api/open-flash?page=1&size={count}&type=push&lang=cn"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        if "data" in data and "data" in data["data"] and isinstance(data["data"]["data"], list):
            return data["data"]["data"]
        else:
            print("No 'data' key found in the response.")
            return []
    else:
        print(f"Error: {response.status_code} - {response.text}")
        return []
