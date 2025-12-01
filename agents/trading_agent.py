from google.adk.agents import LlmAgent
from google.adk.models.google_llm import Gemini
from google.adk.tools.function_tool import FunctionTool

from agents import DEFAULT_MODEL
from tools.trading_tools import propose_trade_execution


def create_trading_agent(model_name: str = DEFAULT_MODEL) -> LlmAgent:
    """
    Trading agent: generates a trade plan (paper only) based on idea + risk assessment.
    """
    model = Gemini(model=model_name)
    return LlmAgent(
        model=model,
        name="TradingAgent",
        description="Proposes paper trade plans (no live execution).",
        instruction="""
        Given an idea and risk assessment, output a TradePlan JSON:
        {
          "symbol": ...,
          "side": "buy"|"sell",
          "size_pct": number (0-100 of portfolio),
          "entry": target price or range,
          "stop_loss": level or percent,
          "take_profit": level or percent,
          "time_horizon_days": int,
          "notes": "short text"
        }
        Then call propose_trade_execution to gate execution:
          - if status is pending, inform user we await approval
          - if approved/auto-approved/rejected, summarize outcome
        Respect user risk: reduce size for conservative profiles, tighten stops for high risk.
        Do NOT claim to execute trades; this is paper planning only.
        """,
        tools=[FunctionTool(func=propose_trade_execution)],
    )
