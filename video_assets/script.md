# Web3 AI Agents – 2-Min Script (≈230–260 words)

**Intro (5s)**  
Title: “Web3 AI Agents — Multi-Agent Trading Copilot”

**Problem (15–20s)**  
Voice: “Web3 trading is fragmented: prices, order books, sentiment, and alerts live in different tabs. It’s easy to miss exposure or security signals and make rushed trades.”

**Why Agents (15–20s)**  
Voice: “Instead of one model doing everything, I use a team: researcher, data engineer, analyst, CRO, and trader, coordinated by an orchestrator. Specialized roles plus shared context.”

**Architecture (25–30s)**  
Voice: “The orchestrator delegates to five agents: Search (market stats/sentiment), Data Engineering (fetch/normalize prices and trades), Analytics (returns, vol, drawdown, density), Risk (depth/bookTicker for liquidity/slippage, risk level), Trading (paper plans with human approval). Gemini powers reasoning; A2A connects agents; MCP shows standardized tools; memory keeps user profile; human-in-loop toggle controls risky actions.”

**Demo (35–40s)**  
On screen: terminal command `python -m agents.run_orchestrator --request "analyze ETH, SOL; risk=balanced"` (or a pre-recorded snippet).  
Voice: “One command runs the flow. Search/Data pull context, Analytics generates metrics, Risk flags issues, Trading proposes a plan. If a trade is risky, the flow can pause for approval. Output is a markdown report with ideas, metrics, risk level, trade plan, and cautions.”

**Build (25–30s)**  
Voice: “Stack: Python + google-adk, Gemini with unified retries, A2A-style agent calls, MCP sample server, optional Binance public data with `USE_BINANCE_LIVE`, JSON tools, session/memory with compaction, Evaluator Agent for safety/completeness checks, human-in-loop via `AUTO_APPROVE_TRADES`. Deployment plan: expose only the orchestrator to Agent Engine; keep sub-agents behind A2A.”

**Close (10–15s)**  
Voice: “Web3 AI Agents delivers faster insights and safer trades with modular agents. Next: richer data, broader evals, and an Agent Engine demo. Thanks for watching.”
