"""
Agent 7: Machine Learning Brain (XGBoost — Hybrid Inference)
=============================================================
Production-grade ML agent with two operating modes:

  Mode A (Fast): Loads a pre-trained .joblib model and runs inference
                 in ~5ms per ticker. Zero training overhead.

  Mode B (Fallback): If no pre-trained model exists, trains XGBoost
                     on-the-fly from the supplied DataFrame (backward
                     compatible with v1 behavior).

Pre-train models offline via: python scripts/train_models.py
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

try:
    import joblib
    JOBLIB_AVAILABLE = True
except ImportError:
    JOBLIB_AVAILABLE = False

CACHE_DIR = ".cache/ml"
MODEL_DIR = ".models"
CACHE_TTL = 6 * 3600  # Cache prediction for 6 hours per symbol
CONFIDENCE_THRESHOLD = 0.70  # 70% minimum for BUY/SELL signal

# Feature columns used by the model (must match training)
FEATURE_COLS = [
    "rsi_14", "macd_val", "macd_sig", "macd_hist",
    "bb_high", "bb_low", "bb_pctb",
    "atr_val", "atr_ratio",
    "sma_20", "sma_50",
    "vol_delta", "vol_sma_ratio",
    "close_pct_1d", "close_pct_5d",
]


def _get_cache_file(symbol: str) -> str:
    clean_sym = symbol.replace(":", "_").replace("/", "_").replace(".", "_")
    return os.path.join(CACHE_DIR, f"{clean_sym}.json")


def _get_model_file(symbol: str) -> str:
    clean_sym = symbol.replace(":", "_").replace("/", "_").replace(".", "_")
    return os.path.join(MODEL_DIR, f"{clean_sym}.joblib")


def _get_universal_model_file() -> str:
    return os.path.join(MODEL_DIR, "universal_model.joblib")


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
    """
    Enhanced feature engineering with 15 features.
    Uses the 'ta' library for robust indicator calculation.
    """
    if df is None or len(df) < 50:
        return df

    df_feat = df.copy()

    try:
        # ── Core Indicators ──
        df_feat['rsi_14'] = ta.momentum.rsi(df_feat['close'], window=14)
        df_feat['macd_val'] = ta.trend.macd(df_feat['close'])
        df_feat['macd_sig'] = ta.trend.macd_signal(df_feat['close'])
        df_feat['macd_hist'] = ta.trend.macd_diff(df_feat['close'])

        # ── Bollinger Bands + %B ──
        df_feat['bb_high'] = ta.volatility.bollinger_hband(df_feat['close'])
        df_feat['bb_low'] = ta.volatility.bollinger_lband(df_feat['close'])
        bb_range = df_feat['bb_high'] - df_feat['bb_low']
        df_feat['bb_pctb'] = np.where(
            bb_range > 0,
            (df_feat['close'] - df_feat['bb_low']) / bb_range,
            0.5
        )

        # ── Volatility ──
        df_feat['atr_val'] = ta.volatility.average_true_range(
            df_feat['high'], df_feat['low'], df_feat['close']
        )
        atr_mean = df_feat['atr_val'].rolling(20).mean()
        df_feat['atr_ratio'] = np.where(
            atr_mean > 0, df_feat['atr_val'] / atr_mean, 1.0
        )

        # ── Trend ──
        df_feat['sma_20'] = ta.trend.sma_indicator(df_feat['close'], window=20)
        df_feat['sma_50'] = ta.trend.sma_indicator(df_feat['close'], window=50)

        # ── Volume Features ──
        vol_sma = df_feat['volume'].rolling(20).mean()
        df_feat['vol_delta'] = df_feat['volume'].diff()
        df_feat['vol_sma_ratio'] = np.where(
            vol_sma > 0, df_feat['volume'] / vol_sma, 1.0
        )

        # ── Price Momentum ──
        df_feat['close_pct_1d'] = df_feat['close'].pct_change(1) * 100
        df_feat['close_pct_5d'] = df_feat['close'].pct_change(5) * 100

    except Exception as e:
        print(f"   ⚠️ Feature calculation warning: {e}")

    # Target Variable: 1 if next candle's close is higher than current close, else 0
    df_feat['target'] = (df_feat['close'].shift(-1) > df_feat['close']).astype(int)

    # Drop rows with NaN
    df_feat.dropna(inplace=True)
    return df_feat


def _load_pretrained_model(symbol: str):
    """
    Attempts to load a pre-trained model in this priority:
    1. Symbol-specific model (.models/RELIANCE_NS.joblib)
    2. Universal fallback model (.models/universal_model.joblib)
    Returns (model, model_name) or (None, None) if not found.
    """
    if not JOBLIB_AVAILABLE:
        return None, None

    # Try symbol-specific model first
    sym_model_path = _get_model_file(symbol)
    if os.path.exists(sym_model_path):
        try:
            model = joblib.load(sym_model_path)
            return model, f"Pre-trained ({symbol})"
        except Exception:
            pass

    # Try universal fallback
    uni_model_path = _get_universal_model_file()
    if os.path.exists(uni_model_path):
        try:
            model = joblib.load(uni_model_path)
            return model, "Pre-trained (Universal)"
        except Exception:
            pass

    return None, None


def analyze(df: pd.DataFrame, symbol: str, force_retrain: bool = False) -> dict:
    """
    Hybrid ML prediction engine.

    Priority:
    1. Return cached prediction if fresh (< 6 hours old)
    2. Load pre-trained model and run instant inference
    3. Fall back to on-the-fly training if no model exists
    """
    print(f"\n🧠 Agent 7: Running Machine Learning (XGBoost) for {symbol}...")

    if not ML_AVAILABLE:
        print("   ⚠️ ML libraries (xgboost, scikit-learn, ta) not installed. Skipping.")
        return {"action": "HOLD", "confidence": 0.0, "error": "Libraries not installed"}

    # ── Step 1: Check Cache ──
    if not force_retrain:
        cached = _load_cache(symbol)
        if cached:
            print(f"   ⚡ Using Cached ML Prediction for {symbol} (0% CPU).")
            return cached

    # ── Step 2: Extract Features ──
    df_ml = extract_features(df)
    if df_ml is None or len(df_ml) < 20:
        print("   ⚠️ Not enough data points for ML analysis.")
        return {"action": "HOLD", "confidence": 0.0, "error": "Insufficient data"}

    # Ensure all feature columns exist
    available_features = [f for f in FEATURE_COLS if f in df_ml.columns]
    if len(available_features) < 5:
        print("   ⚠️ Not enough features computed.")
        return {"action": "HOLD", "confidence": 0.0, "error": "Insufficient features"}

    last_row = df_ml.iloc[-1:]
    X_latest = last_row[available_features]

    # ── Step 3: Try Pre-trained Model (Instant Inference) ──
    model, model_name = _load_pretrained_model(symbol)

    if model is not None:
        try:
            prob = model.predict_proba(X_latest)[0]
            prob_bear, prob_bull = prob[0], prob[1]
            inference_mode = f"⚡ INSTANT ({model_name})"
        except Exception as e:
            print(f"   ⚠️ Pre-trained model inference failed: {e}")
            model = None

    # ── Step 4: Fallback — Train On-The-Fly ──
    if model is None:
        print(f"   🔧 No pre-trained model found. Training on-the-fly...")
        X = df_ml[available_features]
        y = df_ml['target']

        model = xgb.XGBClassifier(
            n_estimators=50,
            max_depth=3,
            learning_rate=0.1,
            eval_metric='logloss',
            random_state=42,
        )

        try:
            model.fit(X, y)
            prob = model.predict_proba(X_latest)[0]
            prob_bear, prob_bull = prob[0], prob[1]
            inference_mode = "🔧 On-The-Fly Training"
        except Exception as e:
            print(f"   ❌ ML Training Error: {e}")
            return {"action": "HOLD", "confidence": 0.0, "error": str(e)}

    # ── Step 5: Decision with 70% Confidence Threshold ──
    action = "HOLD"
    confidence = 0.0

    if prob_bull >= CONFIDENCE_THRESHOLD:
        action = "BUY"
        confidence = prob_bull
    elif prob_bear >= CONFIDENCE_THRESHOLD:
        action = "SELL"
        confidence = prob_bear

    print(f"   ✅ ML Prediction: {action} (Bull: {prob_bull:.1%}, Bear: {prob_bear:.1%}) [{inference_mode}]")

    # Feature importance (only for tree-based models)
    top_features = []
    try:
        importance = model.feature_importances_
        feature_imp = pd.Series(importance, index=available_features).sort_values(ascending=False)
        top_features = feature_imp.head(3).index.tolist()
    except Exception:
        pass

    result = {
        "action": action,
        "confidence": float(confidence),
        "prob_bull": float(prob_bull),
        "prob_bear": float(prob_bear),
        "top_features": top_features,
        "model": "XGBoost Classifier",
        "inference_mode": inference_mode,
        "threshold": CONFIDENCE_THRESHOLD,
    }

    _save_cache(symbol, result)
    return result
