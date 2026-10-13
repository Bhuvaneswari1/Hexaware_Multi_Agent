"""A synchronous wrapper around a real stdio MCP tool for sync graph nodes."""
import asyncio
import json
import sys
from common.config import ROOT


async def remote_lookup(customer_id: str, order_id: str):
    from langchain_mcp_adapters.client import MultiServerMCPClient
    client = MultiServerMCPClient({'orders': {
        'transport': 'stdio', 'command': sys.executable,
        'args': [str(ROOT / 'hour_03_memory_rag_mcp' / 'mcp_server.py')],
    }})
    tools = await client.get_tools()
    lookup = next(t for t in tools if t.name == 'order_lookup')
    result = await lookup.ainvoke({'customer_id': customer_id, 'order_id': order_id})
    if isinstance(result, str):
        return json.loads(result)
    if isinstance(result, dict):
        return result
    for block in result:
        if isinstance(block, dict) and block.get('type') == 'text':
            return json.loads(block['text'])
    raise ValueError('MCP order_lookup did not return JSON text')


def lookup(customer_id: str, order_id: str):
    return asyncio.run(asyncio.wait_for(remote_lookup(customer_id, order_id), timeout=15))
