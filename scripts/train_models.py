"""
Offline Model Trainer — Pre-train XGBoost Models
==================================================
Run this script ONCE (or periodically) to build pre-trained models.
The live bot loads these for instant 5ms inference instead of
training on every scan.

Usage:
    python scripts/train_models.py                    # Train all
    python scripts/train_models.py --market indian     # Train Indian only
    python scripts/train_models.py --market crypto     # Train Crypto only

Output:
    .models/<SYMBOL>.joblib          — Per-ticker model
    .models/universal_model.joblib   — Fallback universal model
    .models/training_report.json     — Accuracy & metrics report
"""

import sys
import os
import json
import time
import argparse
from pathlib import Path
from datetime import datetime, timezone

import pandas as pd
import numpy as np

root_dir = Path(__file__).resolve().parent.parent
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

try:
    import ta
    import xgboost as xgb
    import joblib
    from sklearn.model_selection import train_test_split
    from sklearn.metrics import accuracy_score
except ImportError as e:
    print(f"❌ Missing required library: {e}")
    print("   Install: pip install xgboost scikit-learn joblib ta")
    sys.exit(1)

from src import config

MODEL_DIR = ".models"
REPORT_FILE = os.path.join(MODEL_DIR, "training_report.json")

# Must match FEATURE_COLS in src/agents/ml_agent.py
FEATURE_COLS = [
    "rsi_14", "macd_val", "macd_sig", "macd_hist",
    "bb_high", "bb_low", "bb_pctb",
    "atr_val", "atr_ratio",
    "sma_20", "sma_50",
    "vol_delta", "vol_sma_ratio",
    "close_pct_1d", "close_pct_5d",
]


def fetch_training_data_indian(symbol: str, period_days: int = 365) -> pd.DataFrame:
    """Fetch 1 year of daily data for an Indian stock."""
    import yfinance as yf
    ticker = yf.Ticker(symbol)
    df = ticker.history(period=f"{period_days}d", interval="1d")
    if df.empty:
        return None
    df.columns = [col.lower() for col in df.columns]
    essential = [c for c in ["open", "high", "low", "close", "volume"] if c in df.columns]
    df = df[essential].dropna()
    return df if len(df) >= 60 else None


def fetch_training_data_crypto(symbol: str, limit: int = 365) -> pd.DataFrame:
    """Fetch 1 year of daily data for a crypto pair."""
    from src.connectors import crypto_market
    try:
        df = crypto_market.fetch_ohlcv(symbol, timeframe="1d", limit=limit)
        return df if len(df) >= 60 else None
    except Exception:
        return None


def engineer_features(df: pd.DataFrame) -> pd.DataFrame:
    """Engineer all 15 features + target label. Must match ml_agent.py exactly."""
    df_feat = df.copy()

    try:
        df_feat['rsi_14'] = ta.momentum.rsi(df_feat['close'], window=14)
        df_feat['macd_val'] = ta.trend.macd(df_feat['close'])
        df_feat['macd_sig'] = ta.trend.macd_signal(df_feat['close'])
        df_feat['macd_hist'] = ta.trend.macd_diff(df_feat['close'])

        df_feat['bb_high'] = ta.volatility.bollinger_hband(df_feat['close'])
        df_feat['bb_low'] = ta.volatility.bollinger_lband(df_feat['close'])
        bb_range = df_feat['bb_high'] - df_feat['bb_low']
        df_feat['bb_pctb'] = np.where(
            bb_range > 0,
            (df_feat['close'] - df_feat['bb_low']) / bb_range,
            0.5
        )

        df_feat['atr_val'] = ta.volatility.average_true_range(
            df_feat['high'], df_feat['low'], df_feat['close']
        )
        atr_mean = df_feat['atr_val'].rolling(20).mean()
        df_feat['atr_ratio'] = np.where(
            atr_mean > 0, df_feat['atr_val'] / atr_mean, 1.0
        )

        df_feat['sma_20'] = ta.trend.sma_indicator(df_feat['close'], window=20)
        df_feat['sma_50'] = ta.trend.sma_indicator(df_feat['close'], window=50)

        vol_sma = df_feat['volume'].rolling(20).mean()
        df_feat['vol_delta'] = df_feat['volume'].diff()
        df_feat['vol_sma_ratio'] = np.where(
            vol_sma > 0, df_feat['volume'] / vol_sma, 1.0
        )

        df_feat['close_pct_1d'] = df_feat['close'].pct_change(1) * 100
        df_feat['close_pct_5d'] = df_feat['close'].pct_change(5) * 100

    except Exception as e:
        print(f"      ⚠️ Feature engineering warning: {e}")
        return None

    df_feat['target'] = (df_feat['close'].shift(-1) > df_feat['close']).astype(int)
    df_feat.dropna(inplace=True)

    return df_feat


def train_single_model(symbol: str, df_features: pd.DataFrame) -> dict:
    """Train an XGBoost classifier for a single ticker. Returns metrics dict."""
    available = [f for f in FEATURE_COLS if f in df_features.columns]
    if len(available) < 5 or len(df_features) < 40:
        return {"symbol": symbol, "status": "SKIPPED", "reason": "Insufficient data/features"}

    X = df_features[available]
    y = df_features['target']

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, shuffle=False  # Time-series: chronological split
    )

    model = xgb.XGBClassifier(
        n_estimators=100,
        max_depth=4,
        learning_rate=0.08,
        subsample=0.8,
        colsample_bytree=0.8,
        eval_metric='logloss',
        random_state=42,
    )

    model.fit(X_train, y_train)

    # Evaluate
    y_pred = model.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)

    # Save model
    clean_sym = symbol.replace(":", "_").replace("/", "_").replace(".", "_")
    model_path = os.path.join(MODEL_DIR, f"{clean_sym}.joblib")
    joblib.dump(model, model_path)
    model_size_kb = os.path.getsize(model_path) / 1024

    return {
        "symbol": symbol,
        "status": "TRAINED",
        "accuracy": round(accuracy * 100, 1),
        "train_samples": len(X_train),
        "test_samples": len(X_test),
        "model_size_kb": round(model_size_kb, 1),
        "features_used": len(available),
        "model_path": model_path,
    }


def train_universal_model(all_features: list[pd.DataFrame]) -> dict:
    """Train a universal fallback model from combined data of all tickers."""
    if not all_features:
        return {"status": "SKIPPED", "reason": "No data"}

    combined = pd.concat(all_features, ignore_index=True)
    available = [f for f in FEATURE_COLS if f in combined.columns]

    if len(combined) < 100:
        return {"status": "SKIPPED", "reason": "Not enough combined data"}

    X = combined[available]
    y = combined['target']

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, shuffle=True, random_state=42
    )

    model = xgb.XGBClassifier(
        n_estimators=150,
        max_depth=5,
        learning_rate=0.05,
        subsample=0.8,
        colsample_bytree=0.8,
        eval_metric='logloss',
        random_state=42,
    )

    model.fit(X_train, y_train)

    y_pred = model.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)

    model_path = os.path.join(MODEL_DIR, "universal_model.joblib")
    joblib.dump(model, model_path)
    model_size_kb = os.path.getsize(model_path) / 1024

    print(f"\n   🌍 Universal Model: Accuracy={accuracy:.1%}, "
          f"Samples={len(combined)}, Size={model_size_kb:.0f} KB")

    return {
        "status": "TRAINED",
        "accuracy": round(accuracy * 100, 1),
        "total_samples": len(combined),
        "train_samples": len(X_train),
        "test_samples": len(X_test),
        "model_size_kb": round(model_size_kb, 1),
        "model_path": model_path,
    }


def main():
    parser = argparse.ArgumentParser(description="Offline XGBoost Model Trainer")
    parser.add_argument("--market", choices=["indian", "crypto", "all"], default="all",
                        help="Which market to train models for (default: all)")
    parser.add_argument("--days", type=int, default=365,
                        help="Days of historical data to use (default: 365)")
    args = parser.parse_args()

    os.makedirs(MODEL_DIR, exist_ok=True)

    print("\n" + "=" * 70)
    print("🧠 OFFLINE MODEL TRAINER — XGBoost Pre-Training")
    print("=" * 70)
    print(f"   Market: {args.market.upper()}")
    print(f"   History: {args.days} days")
    print(f"   Output: {MODEL_DIR}/")
    print()

    all_reports = []
    all_feature_dfs = []

    # ── Train Indian Models ──
    if args.market in ("indian", "all"):
        print(f"🇮🇳 Training {len(config.INDIAN_WATCHLIST)} Indian stock models...")
        for i, sym in enumerate(config.INDIAN_WATCHLIST, 1):
            print(f"   [{i}/{len(config.INDIAN_WATCHLIST)}] {sym}...", end=" ")
            try:
                df = fetch_training_data_indian(sym, args.days)
                if df is None:
                    print("❌ No data")
                    all_reports.append({"symbol": sym, "status": "NO_DATA"})
                    continue
                df_feat = engineer_features(df)
                if df_feat is None or len(df_feat) < 40:
                    print("❌ Insufficient features")
                    all_reports.append({"symbol": sym, "status": "INSUFFICIENT_FEATURES"})
                    continue
                report = train_single_model(sym, df_feat)
                all_reports.append(report)
                all_feature_dfs.append(df_feat)
                print(f"✅ Accuracy: {report.get('accuracy', 0):.1f}%")
            except Exception as e:
                print(f"❌ Error: {e}")
                all_reports.append({"symbol": sym, "status": "ERROR", "error": str(e)})

    # ── Train Crypto Models ──
    if args.market in ("crypto", "all"):
        print(f"\n₿ Training {len(config.CRYPTO_WATCHLIST)} crypto models...")
        for i, sym in enumerate(config.CRYPTO_WATCHLIST, 1):
            print(f"   [{i}/{len(config.CRYPTO_WATCHLIST)}] {sym}...", end=" ")
            try:
                df = fetch_training_data_crypto(sym, args.days)
                if df is None:
                    print("❌ No data")
                    all_reports.append({"symbol": sym, "status": "NO_DATA"})
                    continue
                df_feat = engineer_features(df)
                if df_feat is None or len(df_feat) < 40:
                    print("❌ Insufficient features")
                    all_reports.append({"symbol": sym, "status": "INSUFFICIENT_FEATURES"})
                    continue
                report = train_single_model(sym, df_feat)
                all_reports.append(report)
                all_feature_dfs.append(df_feat)
                print(f"✅ Accuracy: {report.get('accuracy', 0):.1f}%")
            except Exception as e:
                print(f"❌ Error: {e}")
                all_reports.append({"symbol": sym, "status": "ERROR", "error": str(e)})

    # ── Train Universal Fallback Model ──
    print("\n🌍 Training universal fallback model from all data...")
    universal_report = train_universal_model(all_feature_dfs)

    # ── Save Training Report ──
    trained = [r for r in all_reports if r.get("status") == "TRAINED"]
    avg_accuracy = np.mean([r["accuracy"] for r in trained]) if trained else 0

    final_report = {
        "trained_at": datetime.now(timezone.utc).isoformat(),
        "total_tickers": len(all_reports),
        "successfully_trained": len(trained),
        "average_accuracy": round(avg_accuracy, 1),
        "universal_model": universal_report,
        "per_ticker": all_reports,
    }

    with open(REPORT_FILE, "w") as f:
        json.dump(final_report, f, indent=2)

    # ── Summary ──
    print("\n" + "=" * 70)
    print("📊 TRAINING COMPLETE")
    print("=" * 70)
    print(f"   ✅ Models Trained: {len(trained)}/{len(all_reports)}")
    print(f"   📈 Average Accuracy: {avg_accuracy:.1f}%")
    print(f"   🌍 Universal Model: {universal_report.get('accuracy', 'N/A')}%")
    print(f"   💾 Report: {REPORT_FILE}")
    print(f"   📁 Models: {MODEL_DIR}/")
    print("=" * 70)


if __name__ == "__main__":
    main()
