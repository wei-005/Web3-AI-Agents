from typing import List

from google.adk.agents import LlmAgent
from google.adk.models.google_llm import Gemini

from agents import DEFAULT_MODEL
from tools.data_tools import load_prices, fetch_binance_spot_klines, fetch_binance_24h


def create_search_agent(model_name: str = DEFAULT_MODEL) -> LlmAgent:
    """
    Search/Opportunity discovery agent.
    Uses local price data + Gemini reasoning to surface candidate symbols or ideas.
    """
    model = Gemini(model=model_name)
    return LlmAgent(
        model=model,
        name="SearchAgent",
        description="Find candidate trading opportunities from local price stats.",
        instruction="""
        You surface 3-5 candidate trading ideas based on simple heuristics
        (recent returns, volatility, volume). Prefer live Binance spot data when available:
        - fetch_binance_spot_klines for OHLCV
        - fetch_binance_24h for 24h change/volume
        If live is disabled, fall back to load_prices sample data.

        Suggest symbols with a short rationale and a 'idea_id'.

        Output JSON with: ideas=[{idea_id, symbol, rationale, suggested_window_days}]
        """,
        tools=[fetch_binance_spot_klines, fetch_binance_24h, load_prices],
    )
