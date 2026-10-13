"""Create a handoff loop, observe recursion failure, then add a bounded exit."""
from typing_extensions import TypedDict
from langgraph.graph import StateGraph, START, END
from langgraph.errors import GraphRecursionError


class State(TypedDict):
    handoffs: int


def graph(fixed=False):
    builder = StateGraph(State)
    builder.add_node('billing', lambda s: {'handoffs': s['handoffs'] + 1})
    builder.add_node('tech', lambda s: {'handoffs': s['handoffs'] + 1})
    builder.add_node('escalation', lambda s: s)
    builder.add_edge(START, 'billing')
    builder.add_edge('billing', 'tech')
    if fixed:
        builder.add_conditional_edges('tech', lambda s: 'escalation' if s['handoffs'] >= 4 else 'billing')
    else:
        builder.add_edge('tech', 'billing')
    builder.add_edge('escalation', END)
    return builder.compile()


if __name__ == '__main__':
    try:
        graph().invoke({'handoffs': 0}, {'recursion_limit': 6})
    except GraphRecursionError:
        print('BEFORE: GraphRecursionError caught after the configured step budget.')
    result = graph(True).invoke({'handoffs': 0}, {'recursion_limit': 8})
    print(f"AFTER: Escalated after {result['handoffs']} handoffs; the graph terminated.")
