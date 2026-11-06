"""
Agent 6: Bull vs Bear Debate
============================
Simulates two analysts arguing for and against a trade based on all compiled data.
A Judge then weighs the arguments to finalize the trade decision.
"""

from google import genai
from google.genai import types
from src import config

def _format_context(tech_data, sent_data, strat_data, fund_data):
    """Formats all agent data into a readable string for the LLM."""
    return f"""
    --- Technicals (Agent 1) ---
    Trend: {tech_data.get('trend')}
    RSI: {tech_data.get('indicators', {}).get('rsi_14')}
    MACD Hist: {tech_data.get('indicators', {}).get('macd_histogram')}
    
    --- Fundamentals (Agent 5) ---
    Label: {fund_data.get('label')}
    Score: {fund_data.get('score')}
    Reasoning: {fund_data.get('reasoning')}
    
    --- Sentiment (Agent 2) ---
    Label: {sent_data.get('sentiment_label')}
    Score: {sent_data.get('sentiment_score')}/100
    Summary: {sent_data.get('narrative_summary')}
    
    --- Strategy Confluence (Agent 3) ---
    Action Proposed: {strat_data.get('action')} (Confidence: {strat_data.get('confidence', 0):.0%})
    Confluence: BUY={strat_data.get('confluence_buy')} | SELL={strat_data.get('confluence_sell')}
    Reasoning: {strat_data.get('reasoning')}
    """

def debate(symbol: str, tech_data: dict, sent_data: dict, strat_data: dict, fund_data: dict) -> dict:
    """
    Runs the Bull vs Bear debate.
    """
    print(f"\n⚖️ Agent 6: Commencing Bull vs Bear Debate for {symbol}...")
    
    if not config.GEMINI_API_KEY:
        print("   ⚠️ Gemini API key not found. Skipping debate.")
        return {
            "bull_case": "N/A",
            "bear_case": "N/A",
            "judge_decision": strat_data.get("action", "HOLD"),
            "judge_reasoning": "Debate skipped due to missing API key.",
            "final_action": strat_data.get("action", "HOLD"),
            "final_confidence": strat_data.get("confidence", 0)
        }
        
    client = genai.Client(api_key=config.GEMINI_API_KEY)
    context = _format_context(tech_data, sent_data, strat_data, fund_data)
    
    prompt = f"""
    You are an elite, gritty Wall Street trading desk evaluating a potential trade for {symbol}. 
    Forget the robotic corporate speak — talk like real, battle-tested traders who have skin in the game.
    Use trading floor slang (e.g., "catching a falling knife", "bull trap", "fading the retail crowd", "smart money", "liquidity grab", "bagholder").
    
    Data context for {symbol}:
    {context}
    
    Generate your response EXACTLY in this format:
    
    BULL CASE:
    (Write 2-3 sentences from the perspective of an aggressive, hyper-bullish trader arguing WHY we must buy this immediately. Sound incredibly convicted and use slang.)
    
    BEAR CASE:
    (Write 2-3 sentences from the perspective of a cynical, heavily-short bear arguing WHY this is a terrible idea and will crash. Sound ruthless and skeptical.)
    
    JUDGE:
    (Write 2-3 sentences as the veteran Desk Manager breaking up the argument. Weigh the risks, cut the BS, and make a final call to BUY, SELL, or HOLD based purely on the data. Sound authoritative, experienced, and decisive.)
    
    FINAL_ACTION: (BUY, SELL, or HOLD)
    FINAL_CONFIDENCE: (0.0 to 1.0)
    """
    
    try:
        response = None
        for model_name in ['gemini-2.5-flash', 'gemini-2.0-flash', 'gemini-1.5-flash']:
            try:
                response = client.models.generate_content(
                    model=model_name,
                    contents=prompt,
                )
                if response and response.text:
                    break
            except Exception:
                continue

        if not response or not response.text:
            raise RuntimeError("Gemini API call returned empty response across available flash models.")

        text = response.text
        
        # Parse the structured response
        bull = text.split("BULL CASE:")[1].split("BEAR CASE:")[0].strip() if "BULL CASE:" in text else "N/A"
        bear = text.split("BEAR CASE:")[1].split("JUDGE:")[0].strip() if "BEAR CASE:" in text else "N/A"
        judge = text.split("JUDGE:")[1].split("FINAL_ACTION:")[0].strip() if "JUDGE:" in text else "N/A"
        
        action_line = [line for line in text.split('\n') if "FINAL_ACTION:" in line]
        conf_line = [line for line in text.split('\n') if "FINAL_CONFIDENCE:" in line]
        
        final_action = action_line[0].split(":")[1].strip() if action_line else strat_data.get("action", "HOLD")
        
        try:
            final_conf = float(conf_line[0].split(":")[1].strip()) if conf_line else strat_data.get("confidence", 0)
        except:
            final_conf = strat_data.get("confidence", 0)
            
        print(f"   🐂 Bull: {bull[:80]}...")
        print(f"   🐻 Bear: {bear[:80]}...")
        print(f"   🏛️ Judge: {judge[:80]}...")
        print(f"   ✅ Final Action: {final_action} (Conf: {final_conf})")
        
        return {
            "bull_case": bull,
            "bear_case": bear,
            "judge_decision": judge,
            "judge_reasoning": judge,
            "final_action": final_action,
            "final_confidence": final_conf
        }
        
    except Exception as e:
        print(f"   ❌ Debate Error: {e}")
        return {
            "bull_case": "Error",
            "bear_case": "Error",
            "judge_decision": "Error",
            "judge_reasoning": str(e),
            "final_action": strat_data.get("action", "HOLD"),
            "final_confidence": strat_data.get("confidence", 0)
        }
