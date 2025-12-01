from google.adk.agents import LlmAgent
from google.adk.models.google_llm import Gemini

from agents import DEFAULT_MODEL, DEFAULT_RETRY
from tools.data_tools import fetch_binance_book_ticker, fetch_binance_depth


def create_risk_agent(model_name: str = DEFAULT_MODEL) -> LlmAgent:
    """
    Risk agent: review trade plan + analysis + user profile; return RiskAssessment.
    """
    model = Gemini(model=model_name, retry_options=DEFAULT_RETRY)
    return LlmAgent(
        model=model,
        name="RiskAgent",
        description="Assesses risk levels and suggests mitigations for trade plans.",
        instruction="""
        Inputs: trade_plan (JSON), analysis (metrics, summary), user_profile (risk tolerance).
        Tools for liquidity/slippage checks:
        - fetch_binance_book_ticker (best bid/ask)
        - fetch_binance_depth (order book snapshot)
        Produce RiskAssessment JSON with fields:
        - risk_level: one of [low, medium, high, reject]
        - reasons: list of concise bullets
        - adjustments: optional changes to sizing/entry/stop
        Be conservative for high drawdown or high volatility; reject if missing data or blatant risk.
        """,
        tools=[fetch_binance_book_ticker, fetch_binance_depth],
    )
