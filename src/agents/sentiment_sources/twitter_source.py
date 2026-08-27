"""
Twitter/X Sentiment Source (Free Scraper)
=========================================
Fetches recent tweets containing the symbol/cashtag using Nitter.
Requires no API keys and is 100% free.
"""

from ntscraper import Nitter
from src.agents.sentiment_sources import BaseSentimentSource, SentimentSourceRegistry

class TwitterSource(BaseSentimentSource):
    name = "Twitter/X Cashtags"
    category = "twitter"
    
    def __init__(self):
        try:
            # Initialize Nitter with auto-selected random instance
            self.scraper = Nitter(log_level=1, skip_instance_check=False)
        except Exception as e:
            print(f"Failed to initialize Nitter scraper: {e}")
            self.scraper = None

    def fetch_data(self, symbol: str, market_type: str = "indian") -> dict:
        if not self.scraper:
            return {"items": [], "count": 0}
            
        clean_symbol = symbol.replace(".NS", "").replace("/USDT", "")
        # Construct cashtag, e.g., $RELIANCE or $BTC
        query = f"${clean_symbol}"
        
        tweets = []
        try:
            # Fetch recent tweets using 'term' search mode
            # We fetch 15 tweets to get a decent sample
            result = self.scraper.get_tweets(query, mode='term', number=15)
            
            if result and 'tweets' in result:
                for tweet in result['tweets']:
                    # Extract the actual text content of the tweet
                    if 'text' in tweet:
                        tweets.append(tweet['text'])
                        
        except Exception as e:
            print(f"Twitter Scraper Error: {e}")
            
        return {"items": tweets, "count": len(tweets)}
        
    def analyze_sentiment(self, data: dict) -> float:
        tweets = data.get("items", [])
        if not tweets:
            return 50.0
            
        # Basic lexical scoring similar to NewsRSS
        # A production bot would pass these through an LLM for precise intent.
        from src.agents.sentiment_sources.news_rss import POSITIVE_WORDS, NEGATIVE_WORDS
        
        pos_score = 0
        neg_score = 0
        
        for text in tweets:
            words = set(text.lower().split())
            if words.intersection(POSITIVE_WORDS):
                pos_score += 1
            if words.intersection(NEGATIVE_WORDS):
                neg_score += 1
                
        total = pos_score + neg_score
        if total == 0:
            return 50.0
            
        return (pos_score / total) * 100.0

SentimentSourceRegistry.register(TwitterSource())
