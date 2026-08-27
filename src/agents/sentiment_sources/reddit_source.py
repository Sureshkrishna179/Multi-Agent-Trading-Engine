"""
Reddit Sentiment Source
=======================
Fetches posts and comments from financial subreddits.
"""

import praw
from src.agents.sentiment_sources import BaseSentimentSource, SentimentSourceRegistry
from src import config

class RedditSource(BaseSentimentSource):
    name = "Reddit Communities"
    category = "reddit"
    
    def __init__(self):
        self.reddit = None
        if config.REDDIT_CLIENT_ID and config.REDDIT_CLIENT_SECRET:
            try:
                self.reddit = praw.Reddit(
                    client_id=config.REDDIT_CLIENT_ID,
                    client_secret=config.REDDIT_CLIENT_SECRET,
                    user_agent=config.REDDIT_USER_AGENT
                )
            except Exception:
                pass

    def fetch_data(self, symbol: str, market_type: str = "indian") -> dict:
        if not self.reddit:
            return {"items": [], "count": 0}
            
        clean_symbol = symbol.replace(".NS", "").replace("/USDT", "")
        
        subs = "IndianStreetBets+IndiaInvestments" if market_type == "indian" else "CryptoCurrency+SatoshiStreetBets"
        
        posts = []
        try:
            # Search for the symbol in the past 24 hours
            for submission in self.reddit.subreddit(subs).search(clean_symbol, time_filter="day", limit=10):
                posts.append({
                    "title": submission.title,
                    "score": submission.score, # Upvotes
                    "upvote_ratio": submission.upvote_ratio
                })
        except Exception as e:
            print(f"Reddit API Error: {e}")
            
        return {"items": posts, "count": len(posts)}
        
    def analyze_sentiment(self, data: dict) -> float:
        posts = data.get("items", [])
        if not posts:
            return 50.0
            
        # Basic scoring: weight by upvote ratio.
        # High upvote ratio = community agrees with the sentiment.
        # Here we just look at engagement for simplicity. A highly engaged post implies momentum.
        avg_ratio = sum(p["upvote_ratio"] for p in posts) / len(posts)
        
        # If community heavily upvotes symbol mentions, it's generally bullish interest.
        # If avg ratio is > 0.8, very bullish (80+). If < 0.5, bearish (< 40).
        score = avg_ratio * 100.0
        return score

SentimentSourceRegistry.register(RedditSource())
