"""
TradingOrchestratorAgent: coordinates the five sub-agents through A2A-style calls.
This implementation runs agents in-process for simplicity; you can swap to HTTP A2A
endpoints by replacing the call_* helpers with real A2A clients.
"""
import os
import asyncio
import json
from typing import Any, Dict, List, Optional

from google.genai import types
from google.adk.models.google_llm import Gemini
from google.adk.agents import LlmAgent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService

from agents import DEFAULT_MODEL
from agents.analytics_agent import create_analytics_agent
from agents.data_engineering_agent import create_data_engineering_agent
from agents.risk_agent import create_risk_agent
from agents.search_agent import create_search_agent
from agents.trading_agent import create_trading_agent
from agents.memory import get_user_profile, upsert_user_profile
from tools.reporting import save_report
from tools.context import compact_messages


async def _invoke(agent: LlmAgent, user_text: str) -> str:
    """
    Attempt to invoke an ADK LlmAgent. ADK supports async iteration over events,
    so we gather text parts; fallback to sync call if needed.
    """
    # Prefer async streaming if available
    if hasattr(agent, "run_async"):
        chunks = []
        async for event in agent.run_async(user_text):
            if getattr(event, "content", None) and event.content.parts:
                for part in event.content.parts:
                    if getattr(part, "text", None):
                        chunks.append(part.text)
        return "\n".join(chunks).strip()

    # Fallback: try sync run
    if hasattr(agent, "run"):
        events = agent.run(user_text)
        if isinstance(events, str):
            return events
        text_parts = []
        for event in events or []:
            if getattr(event, "content", None) and event.content.parts:
                for part in event.content.parts:
                    if getattr(part, "text", None):
                        text_parts.append(part.text)
        return "\n".join(text_parts).strip()

            raise RuntimeError("Agent invocation not supported for this agent type.")


def _safe_json(text: str) -> Any:
    try:
        return json.loads(text)
    except Exception:
        return {"raw": text}


class TradingOrchestrator:
    """
    High-level coordinator:
      1) find ideas
      2) build pipelines
      3) analyze data
      4) assess risk
      5) propose trades
      6) assemble a human-friendly report
    """

    def __init__(self, model_name: str = DEFAULT_MODEL):
        # Orchestrator uses Gemini mainly to summarize final output.
        self.model = Gemini(model=model_name, retry_options=DEFAULT_RETRY)
        self.search_agent = create_search_agent(model_name)
        self.de_agent = create_data_engineering_agent(model_name)
        self.analytics_agent = create_analytics_agent(model_name)
        self.risk_agent = create_risk_agent(model_name)
        self.trading_agent = create_trading_agent(model_name)

    async def _invoke_with_approval(self, agent: LlmAgent, user_text: str, auto_approve: bool = True) -> str:
        """
        Run an agent that may pause for human approval (adk_request_confirmation).
        If pause detected, auto-approve unless overridden via AUTO_APPROVE_TRADES=0 env.
        """
        session_service = InMemorySessionService()
        runner = Runner(agent=agent, session_service=session_service)
        events = []
        async for event in runner.run_async(user_id="trade-user", session_id="trade-session", new_message=types.Content(role="user", parts=[types.Part(text=user_text)])):
            events.append(event)

        approval_event = None
        for e in events:
            if getattr(e, "content", None) and e.content.parts:
                for part in e.content.parts:
                    if getattr(part, "function_call", None) and part.function_call.name == "adk_request_confirmation":
                        approval_event = {
                            "approval_id": part.function_call.id,
                            "invocation_id": e.invocation_id,
                        }
                        break
        if approval_event:
            approve_flag = auto_approve
            # Build FunctionResponse back to agent
            confirmation_response = types.FunctionResponse(
                id=approval_event["approval_id"],
                name="adk_request_confirmation",
                response={"confirmed": approve_flag},
            )
            approval_message = types.Content(role="user", parts=[types.Part(function_response=confirmation_response)])
            async for event in runner.run_async(
                user_id="trade-user",
                session_id="trade-session",
                new_message=approval_message,
                invocation_id=approval_event["invocation_id"],
            ):
                events.append(event)

        # Gather text parts
        chunks = []
        for event in events:
            if getattr(event, "content", None) and event.content.parts:
                for part in event.content.parts:
                    if getattr(part, "text", None):
                        chunks.append(part.text)
        return "\n".join(chunks).strip()

    async def run_workflow(
        self,
        request: str,
        user_profile: Optional[Dict[str, Any]] = None,
        app_name: str = "web3-trading-copilot",
        user_id: str = "demo-user",
        session_id: str = "default-session",
    ) -> Dict[str, Any]:
        profile = user_profile or {"risk": "balanced", "notes": ""}
        # Persist profile in session memory
        await upsert_user_profile(app_name, user_id, session_id, profile)
        profile = await get_user_profile(app_name, user_id, session_id)

        # Step 1: Search for opportunities
        ideas_raw = await _invoke(self.search_agent, f"User request: {request}. Return ideas JSON.")
        ideas_resp = _safe_json(ideas_raw)
        ideas: List[Dict[str, Any]] = ideas_resp.get("ideas", []) if isinstance(ideas_resp, dict) else []

        results = []
        for idea in ideas:
            idea_text = json.dumps(idea)

            # Step 2: Data engineering
            pipeline_raw = await _invoke(
                self.de_agent,
                f"Design pipeline for idea: {idea_text}. Emit pipeline_spec and dataset_ref JSON.",
            )
            pipeline = _safe_json(pipeline_raw)

            # Step 3: Analytics
            analysis_raw = await _invoke(
                self.analytics_agent,
                f"Analyze dataset_ref={json.dumps(pipeline)} for idea {idea_text}. Return JSON report.",
            )
            analysis = _safe_json(analysis_raw)

            # Step 4: Risk
            risk_raw = await _invoke(
                self.risk_agent,
                f"trade_plan will come later. For now, assess risk using analysis={json.dumps(analysis)}, user_profile={json.dumps(profile)}.",
            )
            risk = _safe_json(risk_raw)

            # Step 5: Trading plan
            auto_approve = os.getenv("AUTO_APPROVE_TRADES", "1").lower() not in {"0", "false", "no"}
            trade_raw = await self._invoke_with_approval(
                self.trading_agent,
                f"Idea: {idea_text}. RiskAssessment: {json.dumps(risk)}. User profile: {json.dumps(profile)}. Output TradePlan JSON; call propose_trade_execution to gate execution.",
                auto_approve=auto_approve,
            )
            trade_plan = _safe_json(trade_raw)

            results.append(
                {
                    "idea": idea,
                    "pipeline": pipeline,
                    "analysis": analysis,
                    "risk": risk,
                    "trade_plan": trade_plan,
                }
            )

        # Step 6: Final summary via Gemini
        summary_agent = LlmAgent(
            model=self.model,
            name="SummaryAgent",
            description="Summarize orchestrator results",
            instruction="""
            Create a concise markdown report from orchestrator outputs.
            Include: ideas considered, key metrics, risk levels, trade plan highlights, cautions.
            """,
        )
        summary_raw = await _invoke(summary_agent, json.dumps(results))
        report_path = save_report(summary_raw, prefix="workflow")
        return {"results": results, "report_path": report_path, "summary": summary_raw}


async def main():
    orchestrator = TradingOrchestrator()
    resp = await orchestrator.run_workflow(
        request="Analyze ETHUSD and SOLUSD for the next week; risk=balanced", user_profile={"risk": "balanced"}
    )
    print("Report:", resp["report_path"])
    print(resp["summary"][:800])


if __name__ == "__main__":
    asyncio.run(main())
