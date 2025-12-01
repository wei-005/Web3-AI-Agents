from google.adk.agents import LlmAgent
from google.adk.models.google_llm import Gemini

from agents import DEFAULT_MODEL, DEFAULT_RETRY
from tools.data_tools import synthesize_dataset_ref, fetch_binance_spot_klines, fetch_binance_agg_trades


def create_data_engineering_agent(model_name: str = DEFAULT_MODEL) -> LlmAgent:
    """
    Agent that designs simple data pipelines for a given idea.
    Outputs a pipeline spec plus a dataset_ref (placeholder for a real job).
    """
    model = Gemini(model=model_name, retry_options=DEFAULT_RETRY)
    return LlmAgent(
        model=model,
        name="DataEngineeringAgent",
        description="Designs lightweight data pipelines and emits dataset references.",
        instruction="""
        Given an idea (symbol + window), produce:
        - pipeline_spec: yaml-like text describing steps (source, filter, clean, save)
        - dataset_ref: JSON stub referencing the prepared dataset (use synthesize_dataset_ref tool)
        Prefer live Binance spot data tools when available (klines / aggTrades); otherwise local sample.
        Keep it concise. Assume data is local and small.
        """,
        tools=[fetch_binance_spot_klines, fetch_binance_agg_trades, synthesize_dataset_ref],
    )
