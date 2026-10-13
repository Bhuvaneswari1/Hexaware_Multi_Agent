"""Run five hours in temporary storage, without API keys or changing demo history."""
import json
import os
import sys
import tempfile
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from common.runner import run

ticket = {'customer_id':'C001','order_id':'ORD1001',
          'message':'My headphones arrived damaged and I was charged twice.'}
if __name__ == '__main__':
    os.environ['EMBEDDING_BACKEND'] = 'local_hash'
    os.environ['LANGSMITH_TRACING'] = 'false'
    with tempfile.TemporaryDirectory() as temp:
        os.environ['DESK_RUNTIME_DIR'] = temp
        for hour in range(1, 6):
            result = run(hour, ticket, mode='demo', thread='smoke')
            expected = 'awaiting_approval' if hour >= 4 else 'completed'
            assert result['status'] == expected, result
            if hour >= 4:
                result = run(hour, decision={'action':'approve'}, mode='demo', thread='smoke')
                assert result['refund_status'] == 'simulated'
            print(json.dumps({'hour':hour,'status':'PASS','refund_status':result['refund_status']}))
