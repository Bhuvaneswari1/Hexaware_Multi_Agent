import argparse
import json
from common.config import ROOT
from common.runner import FOLDERS, run, session, graph_config


def main(hour):
    parser = argparse.ArgumentParser(description=f'SupportDesk Hour {hour}')
    parser.add_argument('--input', default=str(ROOT / FOLDERS[hour] / 'sample_input.json'))
    parser.add_argument('--mode', choices=['demo', 'live'])
    parser.add_argument('--thread', default='classroom-1')
    parser.add_argument('--customer', default='C001')
    parser.add_argument('--pattern', choices=['single', 'overloaded', 'specialists', 'sequential', 'router', 'supervisor'])
    parser.add_argument('--mcp', action='store_true')
    parser.add_argument('--decision', choices=['approve', 'reject', 'edit'])
    parser.add_argument('--amount', type=int)
    parser.add_argument('--inspect', action='store_true')
    parser.add_argument('--fault', choices=['none', 'once', 'always'], default='none')
    parser.add_argument('--recursion-limit', type=int, default=45)
    parser.add_argument('--stream', action='store_true')
    args = parser.parse_args()
    if args.inspect:
        with session(hour, args.mode) as (graph, _):
            state = graph.get_state(graph_config(args.customer, args.thread))
            print(json.dumps({'next': state.next, 'state': state.values}, indent=2, default=str))
        return
    if args.decision and hour < 4:
        parser.error('Human approval is introduced in Hour 4.')
    allowed = ['single', 'overloaded', 'specialists'] if hour == 1 else ['sequential', 'router', 'supervisor'] if hour == 2 else ['supervisor']
    if args.pattern and args.pattern not in allowed:
        parser.error(f'Hour {hour} supports patterns: {allowed}')
    ticket = None if args.decision else json.loads(open(args.input).read())
    decision = {'action': args.decision, 'amount_inr': args.amount} if args.decision else None
    try:
        result = run(hour, ticket, customer=args.customer, thread=args.thread, mode=args.mode,
                     pattern=args.pattern, use_mcp=args.mcp, decision=decision, fault=args.fault,
                     recursion_limit=args.recursion_limit,
                     on_event=(lambda e: print('EVENT ' + json.dumps(e, default=str))) if args.stream else None)
    except (ValueError, PermissionError) as exc:
        parser.exit(2, f'Input/action error: {exc}\n')
    print(json.dumps(result, indent=2))

