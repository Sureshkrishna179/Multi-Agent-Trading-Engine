"""
Agent 5: Fundamental Analyst
============================
Checks P/E, EPS, Revenue, and Market Cap to establish a baseline valuation.
Prevents buying overvalued garbage, and encourages buying undervalued assets.
"""

import yfinance as yf
from src import config

def analyze(symbol: str, market_type: str = "indian") -> dict:
    """
    Fetches fundamental data and scores valuation from -1.0 (overvalued) to 1.0 (undervalued).
    """
    print(f"\n📊 Agent 5: Analyzing Fundamentals for {symbol}...")
    
    # If Crypto, fundamentals are mostly network metrics (TVL, active addresses).
    # Since we are using yfinance for now, we'll return a neutral fundamental score for crypto.
    if market_type == "crypto":
        return {
            "score": 0.0,
            "label": "NEUTRAL",
            "reasoning": "Crypto fundamentals require on-chain data. Neutral default applied.",
            "metrics": {}
        }
        
    try:
        ticker = yf.Ticker(symbol)
        info = ticker.info
        
        pe_ratio = info.get("trailingPE") or info.get("forwardPE")
        revenue_growth = info.get("revenueGrowth")
        debt_to_equity = info.get("debtToEquity")
        eps = info.get("trailingEps")
        
        score = 0.0
        reasons = []
        
        # Evaluate P/E
        if pe_ratio:
            if pe_ratio < 15:
                score += 0.4
                reasons.append(f"Undervalued P/E ({pe_ratio:.1f})")
            elif pe_ratio > config.FUNDAMENTAL_PE_MAX:
                score -= 0.5
                reasons.append(f"Overvalued P/E ({pe_ratio:.1f} > {config.FUNDAMENTAL_PE_MAX})")
        else:
            reasons.append("P/E missing (loss making?)")
            score -= 0.2
            
        # Evaluate Revenue Growth
        if revenue_growth:
            if revenue_growth > 0.20:
                score += 0.3
                reasons.append(f"High growth (+{revenue_growth:.1%})")
            elif revenue_growth < 0:
                score -= 0.4
                reasons.append(f"Shrinking revenue ({revenue_growth:.1%})")
                
        # Evaluate Debt
        if debt_to_equity:
            # yfinance reports debt/equity as a percentage sometimes (e.g. 150 = 1.5)
            de_ratio = debt_to_equity / 100 if debt_to_equity > 10 else debt_to_equity
            if de_ratio > config.FUNDAMENTAL_DEBT_EQUITY_MAX:
                score -= 0.3
                reasons.append(f"High Debt/Equity ({de_ratio:.1f})")
                
        # Bound score between -1 and +1
        score = max(-1.0, min(1.0, score))
        
        label = "FAIRLY_VALUED"
        if score > 0.4:
            label = "UNDERVALUED"
        elif score < -0.4:
            label = "OVERVALUED"
            
        return {
            "score": score,
            "label": label,
            "reasoning": "; ".join(reasons) if reasons else "No clear fundamental signals",
            "metrics": {
                "pe_ratio": pe_ratio,
                "revenue_growth": revenue_growth,
                "debt_to_equity": debt_to_equity,
                "eps": eps
            }
        }
        
    except Exception as e:
        print(f"Error fetching fundamentals: {e}")
        return {
            "score": 0.0,
            "label": "UNKNOWN",
            "reasoning": f"Fundamental API error: {e}",
            "metrics": {}
        }
