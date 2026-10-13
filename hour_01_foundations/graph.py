"""Hour 1: one tool agent, tool overload, then two scoped specialist agents."""
import json
from langchain.agents import create_agent
from langgraph.graph import StateGraph, START, END
from common.config import model
from common.state import DeskState
from common.agents import TEAM_PROMPT


def build(ctx, pattern='specialists', checkpointer=None, store=None):
    graph = StateGraph(DeskState)
    graph.add_node('intake', ctx.wrapped('intake', ctx.intake))
    graph.add_edge(START, 'intake')
    if pattern in ('single', 'overloaded'):
        def single(state):
            tools = ctx.tools(state, pattern)
            if ctx.mode == 'live':
                agent = create_agent(model(), tools=tools, system_prompt=TEAM_PROMPT)
                result = agent.invoke({'messages': [{'role': 'user', 'content': state['message']}]},
                                      config={'callbacks': [ctx.usage], 'recursion_limit': 14})
                text = str(result['messages'][-1].content)
                calls = [call['name'] for m in result['messages'] for call in getattr(m, 'tool_calls', [])]
            else:
                # Explicit scripted replay; NOT an LLM and not evidence of model failure.
                calls = ['order_lookup', 'faq_search']
                observations = [tools[0].invoke({}), tools[1].invoke({'query': state['message']})]
                text = 'Scripted tool replay: ' + json.dumps(observations)
            log = {'mode': ctx.mode, 'pattern': pattern, 'available_tools': [t.name for t in tools],
                   'actual_tool_calls': calls, 'response': text,
                   'trainer_note': 'Inspect for missing payment evidence; do not assume overload always fails.'}
            (ctx.folder / 'tool_trace.json').write_text(json.dumps(log, indent=2))
            return {'draft': text, 'events': state['events'] + calls}
        graph.add_node('single_agent', ctx.wrapped('single_agent', single))
        graph.add_edge('intake', 'single_agent')
        graph.add_edge('single_agent', 'finish')
    else:
        # Deliberately fixed two-agent sequence; dynamic routing is introduced in Hour 2.
        graph.add_node('billing', ctx.wrapped('billing', ctx.billing))
        graph.add_node('tech', ctx.wrapped('tech', ctx.tech))
        graph.add_node('draft', ctx.wrapped('draft', ctx.draft))
        graph.add_edge('intake', 'billing')
        graph.add_edge('billing', 'tech')
        graph.add_edge('tech', 'draft')
        graph.add_edge('draft', 'finish')
    graph.add_node('finish', ctx.wrapped('finish', ctx.finish))
    graph.add_edge('finish', END)
    return graph.compile(checkpointer=checkpointer, store=store)
