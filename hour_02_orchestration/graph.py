"""Hour 2: sequential, conditional router, and Command-based supervisor handoffs."""
from langgraph.graph import StateGraph, START, END
from common.state import DeskState


def build(ctx, pattern='supervisor', checkpointer=None, store=None):
    graph = StateGraph(DeskState)
    for name, fn in [('intake', ctx.intake), ('triage', ctx.triage), ('billing', ctx.billing),
                     ('tech', ctx.tech), ('knowledge', ctx.knowledge_node),
                     ('escalation', ctx.escalation), ('draft', ctx.draft), ('finish', ctx.finish)]:
        graph.add_node(name, ctx.wrapped(name, fn))
    graph.add_edge(START, 'intake')
    graph.add_edge('intake', 'triage')
    if pattern == 'sequential':
        graph.add_conditional_edges('triage', lambda s: 'escalation' if s['route'] == ['escalation'] else 'billing',
                                    {'escalation': 'escalation', 'billing': 'billing'})
        graph.add_edge('billing', 'tech')
        graph.add_edge('tech', 'draft')
        graph.add_edge('knowledge', 'draft')
        graph.add_edge('escalation', 'draft')
    elif pattern == 'router':
        # A one-pass router picks ONE team. Compare its mixed-ticket limitation to supervisor.
        graph.add_conditional_edges('triage', lambda s: s['route'][0],
                                    {x: x for x in ['billing', 'tech', 'knowledge', 'escalation']})
        for name in ['billing', 'tech', 'knowledge', 'escalation']:
            graph.add_edge(name, 'draft')
    else:
        graph.add_node('supervisor', ctx.wrapped('supervisor', ctx.supervisor),
                       destinations=('billing', 'tech', 'knowledge', 'escalation', 'draft'))
        graph.add_edge('triage', 'supervisor')
        for name in ['billing', 'tech', 'knowledge']:
            graph.add_edge(name, 'supervisor')
        graph.add_edge('escalation', 'draft')
    graph.add_edge('draft', 'finish')
    graph.add_edge('finish', END)
    return graph.compile(checkpointer=checkpointer, store=store)
