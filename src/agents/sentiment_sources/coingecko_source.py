"""
CoinGecko Sentiment Source
==========================
Fetches crypto community metrics and developer activity.
"""

from pycoingecko import CoinGeckoAPI
from src.agents.sentiment_sources import BaseSentimentSource, SentimentSourceRegistry

class CoinGeckoSource(BaseSentimentSource):
    name = "CoinGecko Community"
    category = "community"
    
    def __init__(self):
        try:
            self.cg = CoinGeckoAPI()
        except Exception:
            self.cg = None
            
    def fetch_data(self, symbol: str, market_type: str = "indian") -> dict:
        # Only works for Crypto
        if market_type != "crypto" or not self.cg:
            return {"items": [], "count": 0}
            
        # Very basic mapping for major coins
        mapping = {
            "BTC/USDT": "bitcoin",
            "ETH/USDT": "ethereum",
            "SOL/USDT": "solana",
            "BNB/USDT": "binancecoin",
            "XRP/USDT": "ripple"
        }
        
        cg_id = mapping.get(symbol)
        if not cg_id:
            return {"items": [], "count": 0}
            
        try:
            data = self.cg.get_coin_by_id(id=cg_id, localization=False, tickers=False, market_data=False, sparkline=False)
            
            return {
                "community_score": data.get("community_score", 50.0),
                "liquidity_score": data.get("liquidity_score", 50.0),
                "upvotes_percentage": data.get("sentiment_votes_up_percentage", 50.0),
                "count": 1 # Representing 1 successful API pull
            }
        except Exception as e:
            print(f"CoinGecko API Error: {e}")
            return {"items": [], "count": 0}
            
    def analyze_sentiment(self, data: dict) -> float:
        if data.get("count", 0) == 0:
            return 50.0
            
        # Combine upvotes and community score
        upvotes = data.get("upvotes_percentage", 50.0)
        community = data.get("community_score", 50.0)
        
        # Weighted average: direct user votes matter slightly more
        score = (upvotes * 0.7) + ((community / 100 * 100) * 0.3)
        return score

SentimentSourceRegistry.register(CoinGeckoSource())
