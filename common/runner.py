"""Durable graph lifecycle shared by CLI, API and evaluation."""
import importlib
import json
import os
import sqlite3
from contextlib import contextmanager
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.checkpoint.sqlite import SqliteSaver
from langgraph.errors import GraphRecursionError
from langgraph.types import Command
from common.agents import Agents
from common.config import runtime_dir
from common.memory import ProfileMemory
from common.state import Ticket, Decision

FOLDERS = {1: 'hour_01_foundations', 2: 'hour_02_orchestration', 3: 'hour_03_memory_rag_mcp',
           4: 'hour_04_collaboration_reliability', 5: 'hour_05_evaluation_deployment'}


@contextmanager
def session(hour, mode=None, pattern=None, use_mcp=False, fault='none'):
    folder = runtime_dir(hour)
    mode = mode or os.getenv('APP_MODE', 'demo')
    if mode not in ('demo', 'live'):
        raise ValueError('APP_MODE must be demo or live')
    memory = ProfileMemory(folder / 'profiles.json') if hour >= 3 else None
    ctx = Agents(hour, mode, folder, memory, use_mcp, fault)
    connection = sqlite3.connect(folder / 'checkpoints.sqlite', check_same_thread=False) if hour >= 3 else None
    saver = SqliteSaver(connection) if connection else InMemorySaver()
    build = importlib.import_module(FOLDERS[hour] + '.graph').build
    graph = build(ctx, pattern or ('specialists' if hour == 1 else 'supervisor'),
                  saver, memory.store if memory else None)
    try:
        yield graph, ctx
    finally:
        if connection:
            connection.close()


def graph_config(customer, thread, recursion_limit=45):
    # Customer prefix prevents accidental thread collisions across identities.
    return {'configurable': {'thread_id': customer + ':' + thread}, 'recursion_limit': recursion_limit,
            'tags': ['supportdesk'], 'metadata': {'customer_id': customer, 'thread': thread}}


def public_result(values, hour, mode, thread):
    interrupts = values.get('__interrupt__', ())
    return {'hour': hour, 'mode': mode, 'thread_id': thread,
            'status': 'awaiting_approval' if interrupts else values.get('status', 'unknown'),
            'route': values.get('route', []), 'completed': values.get('completed', []),
            'refund_amount_inr': values.get('refund_amount', 0),
            'refund_status': values.get('refund_status', 'not_requested'),
            'response': values.get('response', ''), 'draft': values.get('draft', ''),
            'profile': values.get('profile', {}), 'plan': values.get('plan', []),
            'review': values.get('review', {}), 'events': values.get('events', []),
            'approval_request': [x.value for x in interrupts]}


def prepare(graph, config, ticket=None, decision=None):
    snapshot = graph.get_state(config)
    if decision is not None:
        if not snapshot.tasks or not any(task.interrupts for task in snapshot.tasks):
            raise ValueError('No pending approval for this customer and thread.')
        validated = Decision.model_validate(decision)
        maximum = snapshot.values.get('refund_amount', 0)
        if validated.action == 'edit' and (validated.amount_inr is None or validated.amount_inr > maximum):
            raise ValueError('Edited amount must be between 1 and the proposed amount.')
        return Command(resume=validated.model_dump())
    if snapshot.next:
        raise ValueError('This thread has unfinished work. Resume its approval or use a new thread ID.')
    if ticket is None:
        raise ValueError('A ticket is required for a new turn.')
    return Ticket.model_validate(ticket).model_dump()


def run(hour, ticket=None, *, customer='C001', thread='demo-1', mode=None, pattern=None,
        use_mcp=False, decision=None, fault='none', recursion_limit=45, on_event=None):
    with session(hour, mode, pattern, use_mcp, fault) as (graph, ctx):
        if ticket:
            customer = ticket['customer_id']
        config = graph_config(customer, thread, recursion_limit)
        payload = prepare(graph, config, ticket, decision)
        try:
            if on_event:
                for event in graph.stream(payload, config, stream_mode='updates'):
                    on_event(event)
                snapshot = graph.get_state(config)
                values = dict(snapshot.values)
                pauses = tuple(i for t in snapshot.tasks for i in t.interrupts)
                if pauses:
                    values['__interrupt__'] = pauses
            else:
                values = graph.invoke(payload, config)
        except (ConnectionError, TimeoutError, GraphRecursionError) as exc:
            # Fail closed after bounded retries/steps; do not execute a pending refund.
            snapshot = graph.get_state(config)
            values = dict(snapshot.values)
            values.update(status='escalated', response='Human support handoff required: ' + type(exc).__name__,
                          refund_status='not_executed', events=values.get('events', []) + ['runtime_fallback'])
            # The failed checkpoint remains inspectable; resume is not offered for this failure.
        result = public_result(values, hour, ctx.mode, thread)
        (ctx.folder / 'last_output.json').write_text(json.dumps(result, indent=2))
        return result
