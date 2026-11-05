"""
Sentiment Source Base Class & Registry
======================================
Modular system for registering different sentiment data sources.
"""

from typing import Dict, Any, List
from abc import ABC, abstractmethod


class BaseSentimentSource(ABC):
    """
    Abstract base class for all sentiment sources.
    """
    
    name: str = "BaseSource"
    category: str = "unknown"  # e.g., "news", "reddit", "twitter"
    
    @abstractmethod
    def fetch_data(self, symbol: str, market_type: str = "indian") -> Dict[str, Any]:
        """
        Fetch data for a specific symbol.
        Returns a dictionary containing raw data or parsed insights.
        """
        pass
    
    @abstractmethod
    def analyze_sentiment(self, data: Dict[str, Any]) -> float:
        """
        Analyze the fetched data and return a sentiment score from 0-100.
        0 = Extreme Fear/Bearish, 100 = Extreme Greed/Bullish, 50 = Neutral.
        """
        pass
        
    def evaluate(self, symbol: str, market_type: str = "indian") -> Dict[str, Any]:
        """
        Main pipeline: fetches data and computes the score.
        Returns score=None when the source has no live data, so the aggregator
        can exclude it rather than inject a phantom 50.0 neutral into the final score.
        """
        try:
            data = self.fetch_data(symbol, market_type)
            # If no data found, mark as unavailable — do NOT default to 50
            if not data or data.get("count", 0) == 0:
                return {
                    "score": None,  # Explicitly None → aggregator will skip this source
                    "source": self.name,
                    "category": self.category,
                    "data_points": 0,
                    "status": "NO_DATA"
                }
                
            score = self.analyze_sentiment(data)
            
            return {
                "score": score,
                "source": self.name,
                "category": self.category,
                "data_points": data.get("count", len(data.get("items", []))),
                "status": "OK"
            }
        except Exception as e:
            print(f"Error in {self.name} evaluating {symbol}: {e}")
            return {
                "score": None,  # Also None on error — don't fake a neutral score
                "source": self.name,
                "category": self.category,
                "data_points": 0,
                "status": f"ERROR: {e}"
            }


class SentimentSourceRegistry:
    """
    Singleton registry to manage all sentiment sources.
    """
    _sources: List[BaseSentimentSource] = []

    @classmethod
    def register(cls, source: BaseSentimentSource):
        cls._sources.append(source)

    @classmethod
    def get_all(cls) -> List[BaseSentimentSource]:
        return cls._sources
    
    @classmethod
    def get_by_category(cls, category: str) -> List[BaseSentimentSource]:
        return [s for s in cls._sources if s.category == category]
