"""
Indian Market Trading Bot — CLI Backend
=======================================
Isolated execution environment for Indian Equities.
"""

from src import config
from src.pipeline import run_pipeline

if __name__ == "__main__":
    print("\n" + "="*60)
    print("📈 INDIAN MARKET TRADING BOT 📈")
    print("="*60)
    
    for symbol in config.INDIAN_WATCHLIST:
        try:
            print(f"\nEvaluating {symbol}...")
            res = run_pipeline(symbol, "indian")
            action = res["agent_4_risk_execution"]["risk_validation"]["action"]
            status = "APPROVED" if res["agent_4_risk_execution"]["risk_validation"]["approved"] else "VETOED"
            print(f"[{symbol}] Action: {action} | Status: {status}")
        except Exception as e:
            print(f"Error processing {symbol}: {e}")
            
    print("\n✅ Indian Market Scan Complete.")
