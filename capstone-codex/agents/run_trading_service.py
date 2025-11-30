import uvicorn
from google.adk.a2a.utils.agent_to_a2a import to_a2a

from agents.trading_agent import create_trading_agent


def main():
    agent = create_trading_agent()
    app = to_a2a(agent)
    uvicorn.run(app, host="0.0.0.0", port=8015)


if __name__ == "__main__":
    main()
