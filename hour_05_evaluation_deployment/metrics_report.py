"""Aggregate measured node latency, model token usage and optional estimated cost."""
import argparse
import json
from collections import defaultdict
from pathlib import Path

parser = argparse.ArgumentParser()
parser.add_argument('file', type=Path)
args = parser.parse_args()
totals = defaultdict(lambda: {'runs': 0, 'seconds': 0.0, 'input_tokens': 0, 'output_tokens': 0,
                              'model_calls': 0, 'estimated_cost_usd': None})
for line in args.file.read_text().splitlines():
    row = json.loads(line)
    aggregate = totals[row['agent']]
    aggregate['runs'] += 1
    for key in ('seconds', 'input_tokens', 'output_tokens', 'model_calls'):
        aggregate[key] += row[key]
    if row['estimated_cost_usd'] is not None:
        aggregate['estimated_cost_usd'] = (aggregate['estimated_cost_usd'] or 0) + row['estimated_cost_usd']
print(json.dumps(dict(sorted(totals.items(), key=lambda kv: -kv[1]['seconds'])), indent=2))
