"""Local stdio MCP server. Protocol messages use stdout; logs must use stderr."""
import sys
import json
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from mcp.server.fastmcp import FastMCP
from common.data import order_for

mcp = FastMCP('SupportDesk Orders')


@mcp.tool()
def order_lookup(customer_id: str, order_id: str) -> str:
    """Return an order only when it belongs to the supplied customer."""
    return json.dumps(order_for(customer_id, order_id))


if __name__ == '__main__':
    mcp.run(transport='stdio')
