import argparse
import asyncio
import os

from agents.orchestrator import TradingOrchestrator


async def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--request", type=str, required=True, help="User request, e.g., 'analyze ETH, SOL; risk=balanced'")
    parser.add_argument("--risk", type=str, default="balanced", help="User risk profile")
    parser.add_argument("--auto-approve", action="store_true", help="Auto-approve risky trades (default true unless AUTO_APPROVE_TRADES=0)")
    args = parser.parse_args()

    if args.auto_approve:
        os.environ["AUTO_APPROVE_TRADES"] = "1"

    orchestrator = TradingOrchestrator()
    resp = await orchestrator.run_workflow(args.request, user_profile={"risk": args.risk})
    print("Summary:\n", resp["summary"])
    print("Report saved to:", resp["report_path"])


if __name__ == "__main__":
    asyncio.run(main())
