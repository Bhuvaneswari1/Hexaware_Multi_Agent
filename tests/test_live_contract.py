"""Exercise real LangChain tool-loop code with an offline test model, not an API provider."""
from typing import Any
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import AIMessage, ToolMessage
from langchain_core.outputs import ChatGeneration, ChatResult
from common.agents import Agents


class ScriptedToolModel(BaseChatModel):
    @property
    def _llm_type(self):
        return 'offline-contract-test'

    def bind_tools(self, tools, **kwargs):
        return self

    def _generate(self, messages, stop=None, run_manager=None, **kwargs):
        if any(isinstance(m, ToolMessage) for m in messages):
            message = AIMessage(content='Verified order using the tool; no payment action executed.')
        else:
            message = AIMessage(content='', tool_calls=[{'name':'order_lookup','args':{},'id':'test-1','type':'tool_call'}])
        return ChatResult(generations=[ChatGeneration(message=message)])


def test_real_create_agent_tool_loop(tmp_path, monkeypatch):
    import common.agents
    monkeypatch.setattr(common.agents, 'model', lambda: ScriptedToolModel())
    ctx = Agents(2, 'live', tmp_path)
    result = ctx.specialist_text({'customer_id':'C001','order_id':'ORD1001','message':'Check my payment.'},
                                'billing', {'summary':'Test evidence'})
    assert result == 'Verified order using the tool; no payment action executed.'
