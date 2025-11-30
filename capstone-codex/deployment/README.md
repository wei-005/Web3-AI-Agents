# Deployment guide (Vertex Agent Engine outline)

This project is designed so only the **Orchestrator** is exposed publicly; all sub-agents can run as A2A services behind it.

## 1) Prereqs
- `gcloud` configured with project/region.
- ADK CLI installed: `pip install google-adk`.
- Env vars: `GOOGLE_API_KEY`, `PROJECT_ID`, `REGION` (e.g., `us-central1`).

## 2) Define A2A schema (Orchestrator)
- Service name: `TradingCopilot`.
- Method: `run_workflow(request: str, risk: str="balanced") -> {summary, report_path, results}`.
- In code we keep orchestrator callable via CLI; for Agent Engine expose the same method via ADK CLI:
```
adk a2a export --agent-module agents.orchestrator --agent-class TradingOrchestrator --output orchestrator_a2a.yaml
```

## 3) Deploy Orchestrator to Agent Engine
```
adk deploy agent \
  --config orchestrator_a2a.yaml \
  --project $PROJECT_ID \
  --location $REGION \
  --display-name "web3-trading-copilot"
```

## 4) Call deployed agent (Python SDK sketch)
```python
from google.cloud import agentengine_v1

client = agentengine_v1.AgentServiceClient()
resp = client.generate_content(
    agent="projects/PROJECT_ID/locations/REGION/agents/AGENT_ID",
    contents=[agentengine_v1.Content(
        role="user",
        parts=[agentengine_v1.Part(text="Analyze ETH, SOL; risk=balanced")]
    )]
)
print(resp)
```

## 5) Running sub-agents
- Option A (recommended for demo): run sub-agents as local A2A services:
```
python agents/run_search_service.py
python agents/run_data_engineering_service.py
python agents/run_analytics_service.py
python agents/run_risk_service.py
python agents/run_trading_service.py
```
- Option B: keep them in-process (default orchestrator implementation); for cloud deployment you can bundle them into the same container for simplicity.

## 6) Environment/config knobs
- `GEMINI_MODEL` env var to override model name.
- Future: add real exchange/RPC URLs and credentials via env or Secret Manager; current version uses only local simulated data.

## 7) Cleanup
- Delete deployed agent when done to avoid charges:
```
gcloud agent-engine agents delete AGENT_ID --project $PROJECT_ID --location $REGION
```
