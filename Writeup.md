# Web3 Trading Copilot: Enterprise-Grade Multi-Agent System  
**Track:** Enterprise Agents

## 1. Problem: Fragmented Intelligence in Web3 Trading
- **Data silos:** Market data, on-chain signals, and news live on different platforms.
- **Cognitive overload:** Combining price action, risk metrics, and sentiment in real time is hard.
- **Risk blind spots:** Easy to execute without checking exposure or recent security alerts.

I needed a **team**, not one model: a CRO, a quant, a researcher, and a trader working in sync.

## 2. Solution: Gemini-Powered Multi-Agent Collaboration
A multi-agent orchestration (not just a chatbot), with A2A-style calls between specialized roles:

- **Orchestrator (Manager):** User-facing, delegates work.
- **Search Agent (Researcher):** Grabs latest market stats/sentiment (can use Binance public endpoints).
- **Data Engineering Agent (Data):** Fetches/normalizes prices & trades (local samples or live spot API).
- **Analytics Agent (Analyst):** Computes returns, vol, max drawdown, trade density.
- **Risk Agent (CRO):** Checks liquidity/slippage via depth/bookTicker, aligns with user risk profile.
- **Trading Agent (Executor):** Generates paper trade plans with a human-in-loop toggle; pauses for approval when needed.

**Value:**  
- **Speed:** Seconds to synthesize insights.  
- **Safety:** Risk Agent + human approval as guardrails.  
- **Extensibility:** A2A makes it easy to plug in new specialists.

## 3. Architecture & Implementation
- **Models:** Gemini (default `gemini-2.5-flash-lite`, env-overridable) with unified retry options.
- **Multi-agent orchestration:** Hub-and-spoke; Orchestrator manages delegation.
- **A2A + MCP:** Agents expose/consume A2A; MCP server for standardized tool access.
- **Memory & context:** `InMemorySessionService` for user profile/session; lightweight compaction to keep prompts lean.
- **Tools & data:** Local CSVs; optional Binance spot public endpoints (klines/24h/depth/bookTicker/aggTrades) gated by `USE_BINANCE_LIVE`. All tool outputs are JSON-serializable.
- **Human-in-loop:** `AUTO_APPROVE_TRADES=0` enables pause → approve/reject → resume for trading plans.
- **Evaluation:** Evaluator Agent (Gemini) scores fixed scenarios on safety/completeness/alignment.
- **Deployment:** Expose only the Orchestrator to Agent Engine; keep sub-agents behind A2A (deployment steps in `deployment/README.md`).

### Workflow (simplified)
1) User request (e.g., “analyze ETH, SOL; risk=balanced”).  
2) Orchestrator calls Search/Data for market context.  
3) Analytics produces metrics and a short analysis.  
4) Risk assigns risk level/adjustments.  
5) Trading generates a plan; if risky, requests human approval; Orchestrator assembles the final markdown report.

## 4. Project Journey
- **Early (roles):** Defined agent “job descriptions”; let A2A handle sub-agent complexity instead of Orchestrator micromanaging.
- **Mid (integration/memory):** Added session/memory so Risk/Trading share user profile; added compaction for long reports.
- **Late (robustness):** Human-in-loop toggle, unified retries to handle 429/5xx, Evaluator Agent to tune risk sensitivity; JSON tool outputs to avoid serialization issues.

## Conclusion
Web3 Trading Copilot shows that Gemini + multi-agent architecture can deliver practical trading intelligence: it delegates, checks, waits for approval, and produces actionable plans. Next steps: deeper real-data integration, broader eval scenarios, and an Agent Engine deployment demo.
