"""
Agent 7: Machine Learning Brain (XGBoost with Caching)
=====================================================
Trains an XGBoost gradient boosting model on raw features to 
mathematically predict the direction of the next candle.
Caches predictions so CPU usage stays near 0% on repeat runs.
"""

import os
import json
import time
import pandas as pd
import numpy as np

try:
    import ta
    import xgboost as xgb
    from sklearn.model_selection import train_test_split
    ML_AVAILABLE = True
except ImportError:
    ML_AVAILABLE = False

CACHE_DIR = ".cache/ml"
CACHE_TTL = 6 * 3600  # Cache prediction for 6 hours per symbol

def _get_cache_file(symbol: str) -> str:
    clean_sym = symbol.replace(":", "_").replace("/", "_").replace(".", "_")
    return os.path.join(CACHE_DIR, f"{clean_sym}.json")

def _load_cache(symbol: str) -> dict | None:
    filepath = _get_cache_file(symbol)
    if os.path.exists(filepath):
        try:
            with open(filepath, "r") as f:
                data = json.load(f)
            if time.time() - data.get("timestamp", 0) < CACHE_TTL:
                return data.get("result")
        except Exception:
            pass
    return None

def _save_cache(symbol: str, result: dict):
    os.makedirs(CACHE_DIR, exist_ok=True)
    filepath = _get_cache_file(symbol)
    try:
        with open(filepath, "w") as f:
            json.dump({"timestamp": time.time(), "result": result}, f, indent=2)
    except Exception as e:
        print(f"   ⚠️ Could not save ML cache for {symbol}: {e}")

def extract_features(df: pd.DataFrame) -> pd.DataFrame:
    """Uses ta library to extract technical features from OHLCV."""
    if df is None or len(df) < 50:
        return df
        
    df_features = df.copy()
    
    # Technical Indicators via standard 'ta' library (lowercase columns)
    try:
        df_features['rsi_14'] = ta.momentum.rsi(df_features['close'], window=14)
        df_features['macd_val'] = ta.trend.macd(df_features['close'])
        df_features['macd_sig'] = ta.trend.macd_signal(df_features['close'])
        df_features['bb_high'] = ta.volatility.bollinger_hband(df_features['close'])
        df_features['bb_low'] = ta.volatility.bollinger_lband(df_features['close'])
        df_features['atr_val'] = ta.volatility.average_true_range(df_features['high'], df_features['low'], df_features['close'])
        df_features['sma_20'] = ta.trend.sma_indicator(df_features['close'], window=20)
        df_features['sma_50'] = ta.trend.sma_indicator(df_features['close'], window=50)
    except Exception as e:
        print(f"   ⚠️ Feature calculation warning: {e}")
    
    # Target Variable: 1 if next candle's close is higher than current close, else 0
    df_features['target'] = (df_features['close'].shift(-1) > df_features['close']).astype(int)
    
    # Drop rows with NaN
    df_features.dropna(inplace=True)
    return df_features

def analyze(df: pd.DataFrame, symbol: str, force_retrain: bool = False) -> dict:
    """
    Trains XGBoost on the fly and predicts the next move.
    Uses disk caching to prevent CPU overheating on repeat scans.
    """
    print(f"\n🧠 Agent 7: Running Machine Learning (XGBoost) for {symbol}...")
    
    if not ML_AVAILABLE:
        print("   ⚠️ ML libraries (xgboost, scikit-learn, ta) not installed. Skipping.")
        return {"action": "HOLD", "confidence": 0.0, "error": "Libraries not installed"}
        
    # Check Cache First
    if not force_retrain:
        cached = _load_cache(symbol)
        if cached:
            print(f"   ⚡ Using Cached ML Prediction for {symbol} (0% CPU).")
            return cached

    df_ml = extract_features(df)
    
    if df_ml is None or len(df_ml) < 20:
        print("   ⚠️ Not enough data points for ML training.")
        return {"action": "HOLD", "confidence": 0.0, "error": "Insufficient data"}
        
    current_features = extract_features(df)
    last_row = current_features.iloc[-1:]
    
    features = [col for col in df_ml.columns if col not in ['target', 'open', 'high', 'low', 'close', 'volume']]
    
    X = df_ml[features]
    y = df_ml['target']
    
    model = xgb.XGBClassifier(
        n_estimators=50,
        max_depth=3,
        learning_rate=0.1,
        eval_metric='logloss',
        random_state=42
    )
    
    try:
        model.fit(X, y)
        
        X_latest = last_row[features]
        prob = model.predict_proba(X_latest)[0]
        
        prob_bear = prob[0]
        prob_bull = prob[1]
        
        action = "HOLD"
        confidence = 0.0
        
        if prob_bull > 0.60:
            action = "BUY"
            confidence = prob_bull
        elif prob_bear > 0.60:
            action = "SELL"
            confidence = prob_bear
            
        print(f"   ✅ ML Prediction: {action} (Bull: {prob_bull:.1%}, Bear: {prob_bear:.1%})")
        
        importance = model.feature_importances_
        feature_imp = pd.Series(importance, index=features).sort_values(ascending=False)
        top_features = feature_imp.head(3).index.tolist()
        
        result = {
            "action": action,
            "confidence": float(confidence),
            "prob_bull": float(prob_bull),
            "prob_bear": float(prob_bear),
            "top_features": top_features,
            "model": "XGBoost Classifier"
        }
        
        _save_cache(symbol, result)
        return result
    except Exception as e:
        print(f"   ❌ ML Training Error: {e}")
        return {"action": "HOLD", "confidence": 0.0, "error": str(e)}
