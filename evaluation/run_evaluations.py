"""
Run a couple of canned scenarios end-to-end and score them with EvaluatorAgent.
"""
import asyncio
from pathlib import Path

from agents.orchestrator import TradingOrchestrator
from evaluation.evaluator_agent import create_evaluator_agent, evaluate_report


async def run_scenario(request: str):
    orchestrator = TradingOrchestrator()
    result = await orchestrator.run_workflow(request, user_profile={"risk": "balanced"})
    evaluator = create_evaluator_agent()
    score = evaluate_report(evaluator, request, result["summary"])
    return {"request": request, "score": score, "report_path": result["report_path"]}


async def main():
    scenarios = [
        "Analyze ETHUSD for conservative user; flag risks and propose small-size trades.",
        "Analyze SOLUSD and DOGEUSD with aggressive risk; highlight volatility and sizing.",
    ]
    outputs = []
    for s in scenarios:
        out = await run_scenario(s)
        outputs.append(out)
        print(f"Scenario: {s}")
        print("Score:", out["score"])
        print("Report:", out["report_path"])
        print("-" * 40)

    # Save summary artifact
    summary_path = Path("evaluation") / "eval_results.txt"
    lines = [f"{o['request']} -> {o['score']}" for o in outputs]
    summary_path.write_text("\n".join(lines))
    print("Saved eval summary to", summary_path)


if __name__ == "__main__":
    asyncio.run(main())
