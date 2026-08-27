"""
Agent 4: Risk Guardian & Order Executor
=========================================
The uncompromising gatekeeper. Enforces the 2% maximum risk rule,
calculates position sizing, validates trade proposals, and dispatches
orders to Paper Trading logger or live broker APIs.

Position Size Formula:
    Position Size (units) = (Total Capital × 0.02) / (Entry Price − Stop-Loss Price)

Hard Veto Rules:
  - Rejects any trade proposal WITHOUT a stop-loss.
  - Rejects any trade where risk exceeds 2% of account equity.
  - Rejects any trade where Risk-to-Reward ratio is below 1:2.
  - Halts all trading if daily drawdown exceeds 6%.
"""

import json
from datetime import datetime, timezone, timedelta
from src import config


# ── Paper Trading Ledger (in-memory for simulation) ────────────
_paper_portfolio = {
    "indian": {
        "capital": config.DEFAULT_CAPITAL_INR,
        "currency": "INR",
        "open_positions": [],
        "trade_history": [],
        "daily_pnl": 0.0,
    },
    "crypto": {
        "capital": config.DEFAULT_CAPITAL_USD,
        "currency": "USD",
        "open_positions": [],
        "trade_history": [],
        "daily_pnl": 0.0,
    }
}


def calculate_position_size(
    total_capital: float,
    entry_price: float,
    stop_loss: float,
    max_risk_fraction: float = None,
) -> dict:
    """
    Calculate the exact position size using the 2% Risk Rule.

    Position Size = (Capital × Max Risk %) / |Entry − Stop-Loss|

    Args:
        total_capital: Total account equity.
        entry_price: Proposed entry price.
        stop_loss: Proposed stop-loss price.
        max_risk_fraction: Max risk per trade (default from config: 0.02).

    Returns:
        Dict with position_size, risk_amount, and risk_percent.
    """
    if max_risk_fraction is None:
        max_risk_fraction = config.MAX_RISK_PER_TRADE

    risk_per_unit = abs(entry_price - stop_loss)

    if risk_per_unit <= 0:
        return {
            "position_size": 0,
            "risk_amount": 0,
            "risk_percent": 0,
            "error": "Invalid stop-loss: identical to entry price.",
        }

    max_risk_amount = total_capital * max_risk_fraction
    position_size = max_risk_amount / risk_per_unit

    # For Indian equities, round down to whole shares
    position_size_int = int(position_size)

    actual_risk = position_size_int * risk_per_unit
    actual_risk_percent = (actual_risk / total_capital) * 100 if total_capital > 0 else 0

    return {
        "position_size": position_size_int,
        "risk_amount": round(actual_risk, 2),
        "risk_percent": round(actual_risk_percent, 2),
    }


def validate_trade_proposal(trade_proposal: dict, market_type: str = "indian") -> dict:
    """
    Validate a trade proposal against all risk governance rules.

    Args:
        trade_proposal: Output from Agent 3 (strategy_agent.analyze).
        market_type: "indian" or "crypto" (determines capital pool).

    Returns:
        Dict with approved (bool), veto_reasons (list), and position_sizing details.
    """
    action = trade_proposal.get("action", "HOLD")
    entry = trade_proposal.get("entry_price")
    stop_loss = trade_proposal.get("stop_loss")
    take_profit = trade_proposal.get("take_profit")
    rr_ratio = trade_proposal.get("risk_reward_ratio")

    veto_reasons = []

    # ── Rule 0: HOLD proposals are automatically skipped ────────
    if action == "HOLD":
        return {
            "approved": False,
            "action": "HOLD",
            "veto_reasons": ["Strategy chose HOLD — no trade to validate."],
            "position_size": 0,
        }

    # ── Rule 1: Must have a stop-loss ───────────────────────────
    if stop_loss is None or entry is None:
        veto_reasons.append("VETO: Trade proposal is missing a mandatory stop-loss or entry price.")

    # ── Rule 2: Risk-to-Reward must be ≥ 1:2 ───────────────────
    if rr_ratio is not None and rr_ratio < config.MIN_RISK_REWARD:
        veto_reasons.append(
            f"VETO: Risk-to-Reward ratio is {rr_ratio}:1 "
            f"(minimum required: {config.MIN_RISK_REWARD}:1)."
        )

    # ── Rule 3: Daily drawdown check ────────────────────────────
    portfolio = _paper_portfolio[market_type]
    capital = portfolio["capital"]
    daily_pnl = portfolio["daily_pnl"]

    if capital > 0 and abs(daily_pnl) / capital > config.MAX_DAILY_DRAWDOWN:
        veto_reasons.append(
            f"VETO: Daily drawdown limit reached ({config.MAX_DAILY_DRAWDOWN * 100}%). "
            f"All {market_type.upper()} trading halted for today."
        )

    # ── If any veto, reject ─────────────────────────────────────
    if veto_reasons:
        return {
            "approved": False,
            "action": action,
            "veto_reasons": veto_reasons,
            "position_size": 0,
        }

    # ── Rule 4: Calculate position size with 2% max risk ────────
    sizing = calculate_position_size(capital, entry, stop_loss)

    if sizing.get("error"):
        return {
            "approved": False,
            "action": action,
            "veto_reasons": [f"VETO: {sizing['error']}"],
            "position_size": 0,
        }

    if sizing["position_size"] <= 0:
        return {
            "approved": False,
            "action": action,
            "veto_reasons": ["VETO: Calculated position size is 0 (insufficient capital for this setup)."],
            "position_size": 0,
        }

    return {
        "approved": True,
        "action": action,
        "veto_reasons": [],
        "position_size": sizing["position_size"],
        "risk_amount": sizing["risk_amount"],
        "risk_percent": sizing["risk_percent"],
        "entry_price": entry,
        "stop_loss": stop_loss,
        "take_profit": take_profit,
        "risk_reward_ratio": rr_ratio,
    }


def execute_paper_trade(validated_trade: dict, symbol: str, market_type: str = "indian") -> dict:
    """
    Execute a validated trade in Paper Trading mode (virtual simulation).

    Args:
        validated_trade: Output from validate_trade_proposal() with approved=True.
        symbol: Ticker symbol.
        market_type: "indian" or "crypto".

    Returns:
        Trade execution receipt.
    """
    if not validated_trade.get("approved"):
        return {
            "executed": False,
            "reason": "Trade not approved by Risk Guardian.",
            "veto_reasons": validated_trade.get("veto_reasons", []),
        }

    ist_offset = timedelta(hours=5, minutes=30)
    timestamp = datetime.now(timezone.utc) + ist_offset

    trade_record = {
        "trade_id": f"PAPER-{timestamp.strftime('%Y%m%d%H%M%S')}-{symbol.replace('/', '-')}",
        "timestamp": timestamp.isoformat(),
        "symbol": symbol,
        "market_type": market_type,
        "action": validated_trade["action"],
        "entry_price": validated_trade["entry_price"],
        "stop_loss": validated_trade["stop_loss"],
        "take_profit": validated_trade["take_profit"],
        "position_size": validated_trade["position_size"],
        "risk_amount": validated_trade["risk_amount"],
        "risk_percent": validated_trade["risk_percent"],
        "risk_reward_ratio": validated_trade["risk_reward_ratio"],
        "status": "OPEN",
        "mode": "PAPER_TRADING",
    }

    # Add to portfolio
    _paper_portfolio[market_type]["open_positions"].append(trade_record)
    _paper_portfolio[market_type]["trade_history"].append(trade_record)

    return {
        "executed": True,
        "mode": "PAPER_TRADING",
        "trade_record": trade_record,
    }


def get_portfolio_status(market_type: str = "indian") -> dict:
    """
    Get current paper trading portfolio status.

    Returns:
        Dict with capital, open positions count, and trade history count.
    """
    portfolio = _paper_portfolio[market_type]

    return {
        "mode": config.EXECUTION_MODE,
        "available_capital": portfolio["capital"],
        "currency": portfolio["currency"],
        "open_positions": len(portfolio["open_positions"]),
        "total_trades": len(portfolio["trade_history"]),
        "daily_pnl": portfolio["daily_pnl"],
    }


def analyze(trade_proposal: dict, symbol: str, market_type: str = "indian") -> dict:
    """
    Full risk validation & execution pipeline for Agent 4.

    Args:
        trade_proposal: Output from Agent 3 (strategy_agent.analyze).
        symbol: Ticker symbol.
        market_type: "indian" or "crypto".

    Returns:
        Complete risk assessment and execution result payload.
    """
    # Step 1: Validate against all risk rules
    validation = validate_trade_proposal(trade_proposal, market_type)

    # Step 2: Execute if approved (Paper Trading mode)
    execution = {"executed": False, "reason": "Not approved."}
    if validation["approved"] and config.EXECUTION_MODE == "PAPER":
        execution = execute_paper_trade(validation, symbol, market_type)

    # Step 3: Get portfolio snapshot
    portfolio = get_portfolio_status(market_type)

    # Step 4: Build the output payload
    payload = {
        "agent": "Risk Guardian & Executor (Agent 4)",
        "symbol": symbol,
        "market_type": market_type,
        "risk_validation": validation,
        "execution": execution,
        "portfolio_status": portfolio,
    }

    return payload
