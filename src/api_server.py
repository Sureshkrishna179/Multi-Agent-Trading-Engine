"""
FastAPI Backend API Server
==========================
Production REST & WebSocket API powering the custom React / HTML5 Dark Terminal.
Decouples the 8-Agent algorithmic trading engine from the user interface.
"""

import sys
import asyncio
from pathlib import Path
from typing import Optional, List
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel

root_dir = Path(__file__).resolve().parent.parent
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

from src import config
from src.pipeline import run_pipeline
from src.agents import risk_executor_agent
from src.connectors import indian_market, crypto_market
from src.connectors.live_ticker import check_volatility, get_recent_alerts

app = FastAPI(
    title="Multi-Agent Trading Engine API",
    description="Asynchronous institutional backend for 8-agent algorithmic trading",
    version="2.0.0"
)

# Enable CORS for local development and production frontends
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── WebSocket Connection Manager ──────────────────────────────────────────────
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)

    async def broadcast(self, message: dict):
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except Exception:
                pass

manager = ConnectionManager()


# ── REST API Endpoints ────────────────────────────────────────────────────────

@app.get("/api/health")
def health_check():
    return {
        "status": "ONLINE",
        "engine": "8-Agent Async DAG",
        "mode": config.EXECUTION_MODE,
        "active_clients": len(manager.active_connections)
    }


@app.get("/api/portfolio")
def get_portfolio(market: str = Query("indian")):
    """Returns available capital, PnL, open positions, and trade history."""
    clean_market = market.lower() if market in ("indian", "crypto") else "indian"
    status = risk_executor_agent.get_portfolio_status(clean_market)
    currency = "₹" if clean_market == "indian" else "$"
    return {
        "market": clean_market,
        "currency": currency,
        "available_capital": status["available_capital"],
        "daily_pnl": status["daily_pnl"],
        "open_positions": status["open_positions"],
        "total_trades": status["total_trades"],
        "positions": status.get("positions", [])
    }


@app.get("/api/watchlists")
def get_watchlists():
    """Returns the default Indian and Crypto watchlists."""
    return {
        "indian": config.INDIAN_WATCHLIST,
        "crypto": config.CRYPTO_WATCHLIST
    }


@app.get("/api/alerts")
def get_alerts():
    """Returns recent volatility and risk alerts."""
    return {"alerts": get_recent_alerts(max_age_hours=6)}


@app.get("/api/ohlcv")
def get_ohlcv(symbol: str, market: str = "indian"):
    """Returns OHLCV candlestick data formatted for Lightweight Charts."""
    try:
        clean_symbol = symbol.strip().upper()
        if market == "indian":
            df = indian_market.fetch_ohlcv(clean_symbol, period_days=60)
        else:
            df = crypto_market.fetch_ohlcv(clean_symbol, timeframe="1d", limit=60)

        candles = []
        for index, row in df.iterrows():
            time_str = index.strftime("%Y-%m-%d") if hasattr(index, "strftime") else str(index)[:10]
            candles.append({
                "time": time_str,
                "open": round(float(row["open"]), 2),
                "high": round(float(row["high"]), 2),
                "low": round(float(row["low"]), 2),
                "close": round(float(row["close"]), 2),
                "volume": round(float(row.get("volume", 0)), 2)
            })
        return {"symbol": clean_symbol, "market": market, "candles": candles}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


class ScanRequest(BaseModel):
    symbol: str
    market_type: str = "indian"  # "indian" or "crypto"


@app.post("/api/scan")
async def scan_symbol(req: ScanRequest):
    """
    Executes the full 8-agent pipeline for a single asset.
    Broadcasts real-time events over WebSocket to all connected terminals.
    """
    symbol = req.symbol.strip().upper()
    market = req.market_type.lower()

    if market not in ("indian", "crypto"):
        raise HTTPException(status_code=400, detail="market_type must be 'indian' or 'crypto'")

    # Broadcast scan initiation event
    await manager.broadcast({
        "type": "SCAN_STARTED",
        "symbol": symbol,
        "market": market
    })

    try:
        # Run pipeline asynchronously in a worker thread so the API remains non-blocking
        loop = asyncio.get_event_loop()
        res = await loop.run_in_executor(None, run_pipeline, symbol, market)

        consensus = res.get("consensus", {})
        tech = res.get("agent_1_technical", {})
        price = tech.get("latest_price", 0)

        # Check volatility
        vol_alert = check_volatility(symbol, price, market)

        output = {
            "symbol": symbol,
            "market": market,
            "price": price,
            "pipeline_time_seconds": res.get("pipeline_time_seconds", 0),
            "consensus": {
                "score": consensus.get("consensus_score", 0.0),
                "action": consensus.get("consensus_action", "HOLD"),
                "strength": consensus.get("strength", "WEAK"),
                "confidence": consensus.get("confidence", 0.0),
                "agent_votes": consensus.get("agent_votes", {})
            },
            "technical": tech,
            "sentiment": res.get("agent_2_sentiment", {}),
            "ml": res.get("agent_7_ml", {}),
            "ml_health": res.get("ml_health", {}),
            "debate": res.get("agent_6_debate", {}),
            "risk": res.get("agent_4_risk_execution", {}).get("risk_validation", {}),
            "volatility_alert": vol_alert
        }

        # Broadcast completion to all connected terminals
        await manager.broadcast({
            "type": "SCAN_COMPLETED",
            "data": output
        })

        return output

    except Exception as e:
        error_msg = str(e)
        await manager.broadcast({
            "type": "SCAN_FAILED",
            "symbol": symbol,
            "error": error_msg
        })
        raise HTTPException(status_code=500, detail=error_msg)


# ── WebSocket Real-Time Channel ───────────────────────────────────────────────

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        await websocket.send_json({
            "type": "CONNECTED",
            "message": "Connected to Multi-Agent Trading Engine WebSocket",
            "mode": config.EXECUTION_MODE
        })
        while True:
            # Keep connection alive & handle incoming client messages
            data = await websocket.receive_text()
            if data == "ping":
                await websocket.send_text("pong")
    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception:
        manager.disconnect(websocket)


# ── Static Web Dashboard Hosting ──────────────────────────────────────────────
# Serve the compiled modern frontend directly from public/ if it exists
frontend_dir = root_dir / "frontend" / "dist"
if not frontend_dir.exists():
    frontend_dir = root_dir / "frontend"

if frontend_dir.exists():
    app.mount("/static", StaticFiles(directory=str(frontend_dir)), name="static")

    @app.get("/")
    def serve_frontend():
        index_file = frontend_dir / "index.html"
        if index_file.exists():
            return FileResponse(index_file)
        return {"message": "API Server Running. Frontend available at /docs"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("src.api_server:app", host="0.0.0.0", port=8000, reload=True)

