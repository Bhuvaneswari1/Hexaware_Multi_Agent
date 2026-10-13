"""Hour 4: planner, executor team, review subgraph, human interrupt, bounded retries."""
from langgraph.graph import StateGraph, START, END
from langgraph.types import RetryPolicy
from common.state import DeskState


def build(ctx, pattern='supervisor', checkpointer=None, store=None):
    review = StateGraph(DeskState)
    review.add_node('draft', ctx.wrapped('draft', ctx.draft))
    review.add_node('critic', ctx.wrapped('critic', ctx.critic))
    review.add_node('revise', ctx.wrapped('revise', ctx.revise))
    review.add_edge(START, 'draft')
    review.add_edge('draft', 'critic')
    review.add_conditional_edges('critic', lambda s: END if s['review']['passed'] or s['revisions'] >= 2 else 'revise',
                                 {END: END, 'revise': 'revise'})
    review.add_edge('revise', 'critic')

    graph = StateGraph(DeskState)
    nodes = [('intake', ctx.intake), ('triage', ctx.triage), ('planner', ctx.planner),
             ('billing', ctx.billing), ('tech', ctx.tech), ('knowledge', ctx.knowledge_node),
             ('escalation', ctx.escalation), ('approval', ctx.approval),
             ('billing_refund', ctx.execute_refund), ('finish', ctx.finish)]
    for name, fn in nodes:
        # Only read-only specialist nodes are retried. Do not blindly retry side effects.
        retry = RetryPolicy(max_attempts=3, initial_interval=0.1, backoff_factor=2,
                            jitter=False, retry_on=(ConnectionError, TimeoutError)) if name in ('billing', 'tech', 'knowledge') else None
        graph.add_node(name, ctx.wrapped(name, fn), retry_policy=retry)
    graph.add_node('supervisor', ctx.wrapped('supervisor', ctx.supervisor),
                   destinations=('billing', 'tech', 'knowledge', 'escalation', 'draft'))
    graph.add_node('draft', review.compile())
    graph.add_edge(START, 'intake')
    graph.add_edge('intake', 'triage')
    graph.add_edge('triage', 'planner')
    graph.add_edge('planner', 'supervisor')
    for name in ['billing', 'tech', 'knowledge']:
        graph.add_edge(name, 'supervisor')
    graph.add_edge('escalation', 'draft')
    graph.add_conditional_edges('draft', lambda s: 'approval' if s['review']['passed'] else 'finish_rejected_review',
                                {'approval': 'approval', 'finish_rejected_review': 'finish_rejected_review'})

    def failed_review(state):
        return {'status': 'escalated', 'draft': 'Human support handoff required: review failed after two passes.',
                'events': state['events'] + ['review_fallback']}
    graph.add_node('finish_rejected_review', failed_review)
    graph.add_edge('finish_rejected_review', 'finish')
    graph.add_edge('approval', 'billing_refund')
    graph.add_edge('billing_refund', 'finish')
    graph.add_edge('finish', END)
    return graph.compile(checkpointer=checkpointer, store=store)
