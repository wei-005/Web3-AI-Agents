from dataclasses import dataclass
from typing import Dict, Optional

import pandas as pd


@dataclass
class AnalysisResult:
    metrics: Dict[str, float]
    notes: str


def compute_basic_metrics(prices: pd.DataFrame) -> AnalysisResult:
    """
    Compute simple performance metrics on OHLCV data.
    """
    # Accept either DataFrame or dict with rows
    if isinstance(prices, dict):
        prices = pd.DataFrame(prices.get("rows", []))
    if prices.empty:
        return {"metrics": {}, "notes": "No price data available."}

    prices = prices.sort_values("timestamp")
    first_close = float(prices.iloc[0]["close"])
    last_close = float(prices.iloc[-1]["close"])
    ret = (last_close - first_close) / first_close if first_close else 0.0

    daily_returns = prices["close"].pct_change().dropna()
    vol = float(daily_returns.std()) if not daily_returns.empty else 0.0
    max_drawdown = _max_drawdown(prices["close"])

    metrics = {
        "return_pct": round(ret * 100, 2),
        "volatility_pct": round(vol * 100, 2),
        "max_drawdown_pct": round(max_drawdown * 100, 2),
    }
    return {"metrics": metrics, "notes": "Computed on local sample OHLCV data."}


def compute_trade_stats(trades: pd.DataFrame) -> AnalysisResult:
    """
    Compute simple trade stats for a given address or portfolio.
    """
    if isinstance(trades, dict):
        trades = pd.DataFrame(trades.get("rows", []))
    if trades.empty:
        return {"metrics": {}, "notes": "No trades found for selection."}

    buys = trades[trades["side"].str.lower() == "buy"]
    sells = trades[trades["side"].str.lower() == "sell"]

    metrics = {
        "num_trades": len(trades),
        "num_buys": len(buys),
        "num_sells": len(sells),
        "symbols_traded": trades["symbol"].nunique(),
    }
    return {"metrics": metrics, "notes": "Basic trade stats; no PnL since we use mock data."}


def _max_drawdown(series: pd.Series) -> float:
    """
    Compute max drawdown for a price series.
    """
    roll_max = series.cummax()
    drawdown = (series - roll_max) / roll_max
    return float(drawdown.min()) if not drawdown.empty else 0.0
