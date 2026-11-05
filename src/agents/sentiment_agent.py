"""
Agent 2: Multi-Source Sentiment Aggregator
==========================================
Pulls sentiment from News, Reddit, Twitter, and Crypto sources.
Combines scores using weighted averages defined in config.
"""

from typing import Dict, Any
from src.agents.sentiment_sources import SentimentSourceRegistry
from src import config

# Import all sources to trigger registration
import src.agents.sentiment_sources.news_rss
import src.agents.sentiment_sources.reddit_source
import src.agents.sentiment_sources.twitter_source
import src.agents.sentiment_sources.coingecko_source

def analyze(symbol: str, market_type: str = "indian") -> Dict[str, Any]:
    """
    Main entry point for Agent 2.
    Queries all registered sources and computes a weighted final score.
    """
    print(f"   → Agent 2: Gathering sentiment from multi-source network...")
    
    sources = SentimentSourceRegistry.get_all()
    results = []
    
    # Store aggregated scores by category to apply weights
    category_scores = {}
    category_counts = {}
    
    for source in sources:
        # Skip crypto-only sources for Indian stocks
        if source.category == "community" and market_type != "crypto":
            continue
            
        print(f"      - Polling {source.name}...")
        res = source.evaluate(symbol, market_type)
        results.append(res)
        
        # Skip sources that returned no live data (score=None)
        # This prevents phantom 50.0 neutrals from diluting the consensus.
        if res.get("score") is None:
            print(f"        ⚠️ {source.name}: No live data — excluded from scoring.")
            continue
        
        cat = res["category"]
        if cat not in category_scores:
            category_scores[cat] = 0.0
            category_counts[cat] = 0
            
        category_scores[cat] += res["score"]
        category_counts[cat] += 1

    # Average scores within each category
    final_category_scores = {}
    for cat in category_scores:
        if category_counts[cat] > 0:
            final_category_scores[cat] = category_scores[cat] / category_counts[cat]
            
    # Apply global weights
    total_weight = 0.0
    final_score = 0.0
    
    for cat, score in final_category_scores.items():
        weight = config.SENTIMENT_WEIGHTS.get(cat, 0.1) # Default 10% if unknown
        final_score += score * weight
        total_weight += weight
        
    if total_weight > 0:
        final_score = final_score / total_weight
    else:
        final_score = 50.0 # Neutral fallback
        
    # Check for extreme shock
    sentiment_label = "NEUTRAL"
    if final_score < 20:
        sentiment_label = "EXTREME_PANIC"
    elif final_score < 40:
        sentiment_label = "BEARISH"
    elif final_score > 80:
        sentiment_label = "EXTREME_GREED"
    elif final_score > 60:
        sentiment_label = "BULLISH"
        
    live_sources = [r for r in results if r.get("score") is not None]
    dead_sources = [r["source"] for r in results if r.get("score") is None]

    return {
        "sentiment_score": round(final_score, 2),
        "sentiment_label": sentiment_label,
        "category_breakdown": final_category_scores,
        "sources_polled": len(results),
        "live_sources": len(live_sources),
        "blocked_sources": dead_sources,  # Transparent: show which scrapers had no data
        "headlines_analyzed": sum(r.get("data_points", 0) for r in results),
        "narrative_summary": (
            f"Live data from {len(live_sources)}/{len(results)} sources. "
            f"Score: {final_score:.1f}/100. Label: {sentiment_label}. "
            + (f"Blocked/Empty: {', '.join(dead_sources)}." if dead_sources else "All sources live.")
        )
    }
