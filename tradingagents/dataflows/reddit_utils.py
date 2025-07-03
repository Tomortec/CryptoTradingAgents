
import os
import praw

ticker_to_asset = {
    "BTC": "Bitcoin",
    "ETH": "Ethereum",
    "XRP": "XRP",
    "LTC": "Litecoin",
    "DOGE": "Dogecoin",
    "SOL": "Solana",
    "ADA": "Cardano",
    "DOT": "Polkadot",
    "AVAX": "Avalanche",
}

def fetch_posts_from_reddit(
    symbol: str, subreddit_name: str, 
    sort: str = "hot", limit: int = 25
):
    """
    Fetch top posts from a specified subreddit.

    Args:
        symbol (str): The ticker symbol of the asset to filter posts.
        subreddit (str): The name of the subreddit to fetch posts from.
        sort (str): The sorting method for posts ('hot', 'new', 'top', etc.).
        limit (int): The maximum number of posts to fetch.
    Returns:
        list: A list of dictionaries containing post data.
    """
    client_id = os.getenv("REDDIT_CLIENT_ID")
    client_secret = os.getenv("REDDIT_CLIENT_SECRET")
    username = os.getenv("REDDIT_USERNAME")
    password = os.getenv("REDDIT_PASSWORD")
    user_agent = os.getenv("REDDIT_USER_AGENT")

    if not all([client_id, client_secret, username, password, user_agent]):
        return None

    reddit = praw.Reddit(
        client_id=client_id,
        client_secret=client_secret,
        username=username,
        password=password,
        user_agent=user_agent
    )
    subreddit = reddit.subreddit(subreddit_name)
    query = symbol + " OR " + ticker_to_asset.get(symbol, symbol)
    submissions = subreddit.search(query, sort=sort, time_filter="day", limit=limit)
    return [
        {
            "title": submission.title,
            "content": submission.selftext,
            "score": submission.score,
            "created_utc": submission.created_utc,
        }
        for submission in submissions
    ]