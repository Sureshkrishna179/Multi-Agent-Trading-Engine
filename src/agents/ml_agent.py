"""
Agent 7: Machine Learning Brain (XGBoost)
=========================================
Trains an XGBoost gradient boosting model on raw features to 
mathematically predict the direction of the next candle.
"""

import pandas as pd
import numpy as np
try:
    import pandas_ta as ta
    import xgboost as xgb
    from sklearn.model_selection import train_test_split
    ML_AVAILABLE = True
except ImportError:
    ML_AVAILABLE = False

def extract_features(df: pd.DataFrame) -> pd.DataFrame:
    """Uses pandas-ta to extract 50+ technical features from OHLCV."""
    if df is None or len(df) < 50:
        return df
        
    df_features = df.copy()
    
    # Core technicals
    df_features.ta.rsi(length=14, append=True)
    df_features.ta.macd(append=True)
    df_features.ta.bbands(append=True)
    df_features.ta.atr(append=True)
    df_features.ta.stoch(append=True)
    df_features.ta.obv(append=True)
    df_features.ta.adx(append=True)
    
    # Target Variable: 1 if next candle's close is higher than current close, else 0
    df_features['Target'] = (df_features['Close'].shift(-1) > df_features['Close']).astype(int)
    
    # Drop rows with NaN (due to indicators like 14-period RSI taking time to calculate)
    df_features.dropna(inplace=True)
    return df_features

def analyze(df: pd.DataFrame, symbol: str) -> dict:
    """
    Trains XGBoost on the fly and predicts the next move.
    """
    print(f"\n🧠 Agent 7: Running Machine Learning (XGBoost) for {symbol}...")
    
    if not ML_AVAILABLE:
        print("   ⚠️ ML libraries (xgboost, scikit-learn, pandas-ta) not installed. Skipping.")
        return {"action": "HOLD", "confidence": 0.0, "error": "Libraries not installed"}
        
    df_ml = extract_features(df)
    
    if len(df_ml) < 20:
        print("   ⚠️ Not enough data points for ML training.")
        return {"action": "HOLD", "confidence": 0.0, "error": "Insufficient data"}
        
    # We want to predict the absolute LAST candle's future, so it's our test case
    # Target for the last row is NaN because we shifted it, but dropna dropped it.
    # We must predict on the unshifted last row.
    
    # Re-extract just for the current state (no shift)
    current_features = df.copy()
    current_features.ta.rsi(length=14, append=True)
    current_features.ta.macd(append=True)
    current_features.ta.bbands(append=True)
    current_features.ta.atr(append=True)
    current_features.ta.stoch(append=True)
    current_features.ta.obv(append=True)
    current_features.ta.adx(append=True)
    
    last_row = current_features.iloc[-1:]
    last_row = last_row.dropna(axis=1) # Drop the empty target or any fully NaN columns
    
    # Prepare training data
    features = [col for col in df_ml.columns if col not in ['Target', 'Open', 'High', 'Low', 'Close', 'Volume']]
    
    X = df_ml[features]
    y = df_ml['Target']
    
    # Train/Test split is mostly to prevent overfitting, but we'll train on the whole recent dataset
    # since it's just a 60-day window and we want the most recent context.
    model = xgb.XGBClassifier(
        n_estimators=50,
        max_depth=3,
        learning_rate=0.1,
        eval_metric='logloss',
        random_state=42
    )
    
    try:
        model.fit(X, y)
        
        # Predict the latest state
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
        
        # Get top 3 most important features
        importance = model.feature_importances_
        feature_imp = pd.Series(importance, index=features).sort_values(ascending=False)
        top_features = feature_imp.head(3).index.tolist()
        
        return {
            "action": action,
            "confidence": float(confidence),
            "prob_bull": float(prob_bull),
            "prob_bear": float(prob_bear),
            "top_features": top_features,
            "model": "XGBoost Classifier"
        }
    except Exception as e:
        print(f"   ❌ ML Training Error: {e}")
        return {"action": "HOLD", "confidence": 0.0, "error": str(e)}
