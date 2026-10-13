import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from common.data import simulate_refund
from common.config import runtime_dir

if __name__ == '__main__':
    for role, approved in [('tech', True), ('billing', False)]:
        try:
            simulate_refund(runtime_dir(5) / 'refunds.sqlite', role=role,
                            customer_id='C001', order_id='ORD1001', amount=2499, approved=approved)
        except PermissionError as exc:
            print(f'BLOCKED ({role}, approved={approved}): {exc}')
