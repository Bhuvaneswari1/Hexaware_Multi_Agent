"""Verify imports/configuration without printing keys or making paid API calls."""
import importlib
import importlib.metadata
import os
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from common.config import ROOT

if __name__ == '__main__':
    print('Python:', sys.version.split()[0], '(recommended: 3.12)')
    for package, module in [('langgraph','langgraph'), ('langchain','langchain'),
                            ('langsmith','langsmith'), ('chromadb','chromadb'),
                            ('mcp','mcp'), ('fastapi','fastapi')]:
        importlib.import_module(module)
        print(package, importlib.metadata.version(package), 'OK')
    print('Mode:', os.getenv('APP_MODE', 'demo'))
    print('OpenAI key configured:', bool(os.getenv('OPENAI_API_KEY')))
    print('LangSmith tracing:', os.getenv('LANGSMITH_TRACING', 'false'))
    print('LangSmith key configured:', bool(os.getenv('LANGSMITH_API_KEY')))
    print('CSV data:', len(list((ROOT / 'data').glob('*.csv'))), 'files')
