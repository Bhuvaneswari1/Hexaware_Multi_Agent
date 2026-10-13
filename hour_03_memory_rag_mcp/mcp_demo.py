"""Two independently scoped specialists consume the same MCP server tool."""
import sys
import json
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from common.mcp_tools import lookup

if __name__ == '__main__':
    for specialist in ['billing', 'tech']:
        print(json.dumps({'agent': specialist, 'transport': 'MCP stdio',
                          'order': lookup('C001', 'ORD1001')}))
