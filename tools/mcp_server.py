"""
Minimal MCP server exposing mock web3 data access.
This is a placeholder to demonstrate MCP integration; in practice, plug real data sources.
"""
import asyncio
from typing import Any, Dict

from google.adk.mcp import mcp_server

from tools.data_tools import load_prices, load_trades


async def get_historical_prices(params: Dict[str, Any]) -> Dict[str, Any]:
    symbol = params.get("symbol")
    window = params.get("window_days", 7)
    df = load_prices(symbol=symbol)
    # Return limited rows for brevity
    rows = df.tail(window).to_dict(orient="records")
    return {"rows": rows}


async def get_trades_for_address(params: Dict[str, Any]) -> Dict[str, Any]:
    address = params.get("address")
    df = load_trades(address=address)
    rows = df.to_dict(orient="records")
    return {"rows": rows}


def main():
    server = mcp_server.Server("web3-data-mcp")
    server.register_tool("get_historical_prices", get_historical_prices)
    server.register_tool("get_trades_for_address", get_trades_for_address)
    loop = asyncio.get_event_loop()
    loop.run_until_complete(server.run())


if __name__ == "__main__":
    main()
