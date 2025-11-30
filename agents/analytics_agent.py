from google.adk.agents import LlmAgent
from google.adk.models.google_llm import Gemini

from agents import DEFAULT_MODEL
from tools.analysis_tools import compute_basic_metrics, compute_trade_stats
from tools.data_tools import (
    load_prices,
    load_trades,
    fetch_binance_spot_klines,
    fetch_binance_agg_trades,
)


def create_analytics_agent(model_name: str = DEFAULT_MODEL) -> LlmAgent:
    """
    Analytics agent: run simple metrics and narrate findings.
    """
    model = Gemini(model=model_name)
    return LlmAgent(
        model=model,
        name="AnalyticsAgent",
        description="Computes basic performance metrics and writes an analysis report.",
        instruction="""
        Given a dataset_ref or symbol/address, use the tools to fetch data and compute metrics
        (returns, volatility, max drawdown, trade counts). Return JSON:
        {
          "symbol": ...,
          "metrics": {...},
          "trade_stats": {...},
          "summary": "short natural language overview"
        }
        If data is missing, state it clearly.
        """,
        tools=[
            fetch_binance_spot_klines,
            fetch_binance_agg_trades,
            load_prices,
            load_trades,
            compute_basic_metrics,
            compute_trade_stats,
        ],
    )
