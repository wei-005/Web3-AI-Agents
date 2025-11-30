import os
from datetime import datetime
from typing import Any, Dict, Optional

import pandas as pd
import requests

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
BINANCE_SPOT_BASE = "https://api.binance.com"


def _use_live() -> bool:
    """
    Toggle live Binance access with env USE_BINANCE_LIVE (default on).
    """
    return os.getenv("USE_BINANCE_LIVE", "1").lower() not in {"0", "false", "no"}


def load_prices(symbol: Optional[str] = None, start: Optional[str] = None, end: Optional[str] = None) -> pd.DataFrame:
    """
    Load OHLCV price data from the local sample CSV. Used as fallback when live data is off/unavailable.
    """
    path = os.path.join(DATA_DIR, "prices.csv")
    df = pd.read_csv(path, parse_dates=["timestamp"])
    if symbol:
        df = df[df["symbol"].str.lower() == symbol.lower()]
    if start:
        df = df[df["timestamp"] >= pd.to_datetime(start)]
    if end:
        df = df[df["timestamp"] <= pd.to_datetime(end)]
    return df.reset_index(drop=True)


def load_trades(address: Optional[str] = None, portfolio: Optional[list] = None) -> pd.DataFrame:
    """
    Load trade history from the local sample CSV. A real implementation would call an exchange or chain indexer.
    """
    path = os.path.join(DATA_DIR, "trades.csv")
    df = pd.read_csv(path, parse_dates=["timestamp"])
    if address:
        df = df[df["address"].str.lower() == address.lower()]
    if portfolio:
        lower = [addr.lower() for addr in portfolio]
        df = df[df["address"].str.lower().isin(lower)]
    return df.reset_index(drop=True)


def synthesize_dataset_ref(symbol: str, window_days: int = 7) -> dict:
    """
    Generate a lightweight dataset reference for downstream agents (placeholder for real pipelines).
    """
    return {
        "symbol": symbol,
        "window_days": window_days,
        "generated_at": datetime.utcnow().isoformat() + "Z",
        "source": "local-simulated",
    }


# -----------------------------
# Live Binance Spot (public, no key required)
# -----------------------------

def fetch_binance_spot_klines(symbol: str, interval: str = "1h", limit: int = 200) -> pd.DataFrame:
    """
    Fetch spot klines (public). Falls back to local prices on error or if live disabled.
    Columns align with load_prices: timestamp, symbol, open, high, low, close, volume.
    """
    if not _use_live():
        return load_prices(symbol)
    try:
        resp = requests.get(
            f"{BINANCE_SPOT_BASE}/api/v3/klines",
            params={"symbol": symbol.upper(), "interval": interval, "limit": limit},
            timeout=10,
        )
        resp.raise_for_status()
        rows = resp.json()
        data = []
        for r in rows:
            data.append(
                {
                    "timestamp": pd.to_datetime(r[0], unit="ms"),
                    "symbol": symbol.upper(),
                    "open": float(r[1]),
                    "high": float(r[2]),
                    "low": float(r[3]),
                    "close": float(r[4]),
                    "volume": float(r[5]),
                }
            )
        return pd.DataFrame(data)
    except Exception:
        return load_prices(symbol)


def fetch_binance_24h(symbol: Optional[str] = None) -> Any:
    """
    24h ticker stats (public). Returns dict or list from Binance; caller can parse.
    """
    if not _use_live():
        return {"status": "disabled", "reason": "USE_BINANCE_LIVE=0"}
    try:
        params = {"symbol": symbol.upper()} if symbol else {}
        resp = requests.get(f"{BINANCE_SPOT_BASE}/api/v3/ticker/24hr", params=params, timeout=10)
        resp.raise_for_status()
        return resp.json()
    except Exception as e:
        return {"status": "error", "error": str(e)}


def fetch_binance_book_ticker(symbol: Optional[str] = None) -> Any:
    """
    Best bid/ask snapshot (public).
    """
    if not _use_live():
        return {"status": "disabled", "reason": "USE_BINANCE_LIVE=0"}
    try:
        params = {"symbol": symbol.upper()} if symbol else {}
        resp = requests.get(f"{BINANCE_SPOT_BASE}/api/v3/ticker/bookTicker", params=params, timeout=10)
        resp.raise_for_status()
        return resp.json()
    except Exception as e:
        return {"status": "error", "error": str(e)}


def fetch_binance_depth(symbol: str, limit: int = 20) -> Any:
    """
    Order book depth (public). Keep limit small to reduce weight.
    """
    if not _use_live():
        return {"status": "disabled", "reason": "USE_BINANCE_LIVE=0"}
    try:
        resp = requests.get(
            f"{BINANCE_SPOT_BASE}/api/v3/depth",
            params={"symbol": symbol.upper(), "limit": limit},
            timeout=10,
        )
        resp.raise_for_status()
        return resp.json()
    except Exception as e:
        return {"status": "error", "error": str(e)}


def fetch_binance_agg_trades(symbol: str, limit: int = 200) -> Any:
    """
    Aggregated trades (public) for short-term flow/volume analysis.
    """
    if not _use_live():
        return {"status": "disabled", "reason": "USE_BINANCE_LIVE=0"}
    try:
        resp = requests.get(
            f"{BINANCE_SPOT_BASE}/api/v3/aggTrades",
            params={"symbol": symbol.upper(), "limit": limit},
            timeout=10,
        )
        resp.raise_for_status()
        return resp.json()
    except Exception as e:
        return {"status": "error", "error": str(e)}
