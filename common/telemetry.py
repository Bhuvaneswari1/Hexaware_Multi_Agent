"""Local per-agent measurements; LangSmith automatically traces LangChain calls."""
import json
import os
from langchain_core.callbacks import BaseCallbackHandler


class UsageCollector(BaseCallbackHandler):
    def __init__(self):
        self.input_tokens = 0
        self.output_tokens = 0
        self.calls = 0

    def on_llm_end(self, response, **kwargs):
        self.calls += 1
        for generations in response.generations:
            for generation in generations:
                usage = getattr(getattr(generation, 'message', None), 'usage_metadata', None) or {}
                self.input_tokens += usage.get('input_tokens', 0)
                self.output_tokens += usage.get('output_tokens', 0)


def record(path, role, elapsed, usage, mode, ok):
    incoming, outgoing = os.getenv('INPUT_USD_PER_MILLION'), os.getenv('OUTPUT_USD_PER_MILLION')
    cost = ((usage.input_tokens * float(incoming) + usage.output_tokens * float(outgoing)) / 1e6
            if incoming and outgoing else None)
    row = {'agent': role, 'mode': mode, 'seconds': round(elapsed, 4),
           'model_calls': usage.calls, 'input_tokens': usage.input_tokens,
           'output_tokens': usage.output_tokens, 'estimated_cost_usd': cost, 'ok': ok}
    with path.open('a') as f:
        f.write(json.dumps(row) + '\n')
