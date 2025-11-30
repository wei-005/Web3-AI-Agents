import uvicorn
from google.adk.a2a.utils.agent_to_a2a import to_a2a

from agents.analytics_agent import create_analytics_agent


def main():
    agent = create_analytics_agent()
    app = to_a2a(agent)
    uvicorn.run(app, host="0.0.0.0", port=8013)


if __name__ == "__main__":
    main()
