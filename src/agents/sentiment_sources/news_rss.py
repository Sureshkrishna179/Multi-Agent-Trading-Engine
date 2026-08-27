"""
News RSS Sentiment Source
=========================
Fetches headlines from standard RSS feeds.
"""

import feedparser
from bs4 import BeautifulSoup
from src.agents.sentiment_sources import BaseSentimentSource, SentimentSourceRegistry
from src import config

# Note: In a real system, you'd use a local LLM or FinBERT here.
# For simplicity, we use a dictionary approach or rely on Agent 2 to combine scores.
# Here we'll implement a fast lexical baseline.
POSITIVE_WORDS = {"surge", "jump", "rally", "buy", "growth", "profit", "bull", "high", "upgrade", "outperform"}
NEGATIVE_WORDS = {"crash", "plunge", "sell", "loss", "bear", "low", "downgrade", "underperform", "scam", "hack"}

class NewsRSSSource(BaseSentimentSource):
    name = "News RSS"
    category = "news"
    
    def fetch_data(self, symbol: str, market_type: str = "indian") -> dict:
        clean_symbol = symbol.replace(".NS", "").replace("/USDT", "")
        headlines = []
        
        feeds = config.NEWS_RSS_FEEDS.values()
        
        for url in feeds:
            try:
                feed = feedparser.parse(url)
                for entry in feed.entries[:10]: # Check last 10 entries per feed
                    # Clean title
                    title = BeautifulSoup(entry.title, "html.parser").get_text().lower()
                    if clean_symbol.lower() in title:
                        headlines.append(title)
            except Exception:
                pass
                
        return {"items": headlines, "count": len(headlines)}
        
    def analyze_sentiment(self, data: dict) -> float:
        headlines = data.get("items", [])
        if not headlines:
            return 50.0
            
        pos_score = 0
        neg_score = 0
        
        for hl in headlines:
            words = set(hl.split())
            if words.intersection(POSITIVE_WORDS):
                pos_score += 1
            if words.intersection(NEGATIVE_WORDS):
                neg_score += 1
                
        total = pos_score + neg_score
        if total == 0:
            return 50.0
            
        # Convert to 0-100 scale
        ratio = pos_score / total
        return ratio * 100.0

SentimentSourceRegistry.register(NewsRSSSource())
