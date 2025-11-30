# Web3 Trading Copilot (Capstone)

Multi-agent, Gemini-powered web3 trading assistant built for the Kaggle 5-Day Agents capstone. The system demonstrates **multi-agent orchestration, MCP tools, memory/context engineering, evaluation, Agent2Agent (A2A) interop, and deployment**. All data is local/simulated (no live exchange calls), but the architecture leaves hooks to swap in real APIs.

## Highlights (what reviewers should notice)
- **Six agents**: Orchestrator + Search + DataEngineering + Analytics + Risk + Trading; all exposed via **A2A** schemas.  
- **Gemini everywhere**: Gemini models for planning, analysis narration, and evaluator. `GOOGLE_API_KEY` read from env (never committed).  
- **Tools + MCP**: local CSV loaders/writers, pandas analysis, mock web3 data via a simple MCP server.  
- **Memory & context**: session service to keep user profile (risk, preferred assets); lightweight compaction to summarize long chats.  
- **Evaluation**: evaluator agent checks completeness/risk coverage on predefined scenarios.  
- **Deployment**: Orchestrator is the public entry; sub-agents stay behind A2A. Deployment guide for Vertex Agent Engine plus local A2A servers.
- **Live spot data (optional)**: public Binance spot endpoints (klines/24h/depth/bookTicker/aggTrades) with `USE_BINANCE_LIVE` toggle; falls back to local CSV for offline/demo.

## Repo layout
```
capstone-codex/
  agents/                 # orchestrator + sub-agents
  tools/                  # data tools, MCP server, compaction helpers
  data/                   # sample CSVs (simulated)
  evaluation/             # evaluator agent + scenarios
  deployment/             # A2A schemas + deployment instructions
  logs/                   # runtime logs (gitignored)
```

## Prereqs
- Python 3.10+
- `pip install -r requirements.txt` (file will be added alongside code)
- Env vars: `GOOGLE_API_KEY` (required to run with Gemini). Optionally set dataset paths.  
- `USE_BINANCE_LIVE=1` (default) to use public spot APIs; set `0` to stay fully offline.

## Run locally (outline)
1) Start sub-agent A2A services (or run in-process):  
```bash
python agents/run_search_service.py
python agents/run_data_engineering_service.py
python agents/run_analytics_service.py
python agents/run_risk_service.py
python agents/run_trading_service.py
```
2) Run orchestrator CLI demo (in-process A2A also supported):  
```bash
python agents/run_orchestrator.py --request "analyze my portfolio: ETH, SOL; risk=balanced"
```
3) Evaluate sample scenarios:  
```bash
python evaluation/run_evaluations.py
```

## Deployment (Vertex Agent Engine outline)
- Deploy only the **Orchestrator** with its A2A schema; sub-agents remain callable A2A endpoints (or bundled as internal services).  
- See `deployment/README.md` for ADK CLI commands, config, and a Python client snippet.

## Kaggle writeup pointers
- Track: **Enterprise Agents** (web3 trading analytics).  
- Call out: multi-agent workflow, MCP tool, memory/compaction, evaluation, A2A, deployment, Gemini usage.  
- Provide screenshots of reports/logs if possible.
