from typing import Dict

from google.adk.agents import LlmAgent
from google.adk.models.google_llm import Gemini

from agents import DEFAULT_MODEL, DEFAULT_RETRY


def create_evaluator_agent(model_name: str = DEFAULT_MODEL) -> LlmAgent:
    model = Gemini(model=model_name, retry_options=DEFAULT_RETRY)
    return LlmAgent(
        model=model,
        name="EvaluatorAgent",
        description="Scores final reports for completeness and risk coverage.",
        instruction="""
        You are an evaluator. Given user_request and final_report, produce JSON:
        {
          "completeness_score": 0-1,
          "risk_score": 0-1,
          "alignment_score": 0-1,
          "comments": ["...","..."]
        }
        Completeness: mentions ideas, metrics, risk, trade plan.
        Risk: flags high drawdown/volatility, low liquidity, or missing data.
        Alignment: respects user risk profile (conservative/balanced/aggressive).
        """,
    )


def evaluate_report(agent: LlmAgent, user_request: str, report: str) -> Dict:
    prompt = f"User request: {user_request}\nReport:\n{report}\nReturn JSON only."
    resp = agent.run(prompt)
    # Attempt to extract text parts
    if isinstance(resp, str):
        return {"raw": resp}
    text_parts = []
    for event in resp or []:
        if getattr(event, "content", None) and event.content.parts:
            for part in event.content.parts:
                if getattr(part, "text", None):
                    text_parts.append(part.text)
    return {"raw": "\n".join(text_parts)}
