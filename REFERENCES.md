# Official references and API choices

Reviewed for this kit on 2026-10-07. These links document libraries; business rules and classroom fixtures are invented for the exercise.

- [LangChain agents](https://docs.langchain.com/oss/python/langchain/agents): `create_agent` supplies the live model/tool loop. The older TOC mentions `langgraph.prebuilt` ReAct; this kit uses the current LangChain entry point built on LangGraph.
- [LangGraph persistence](https://docs.langchain.com/oss/python/langgraph/persistence): thread checkpoints and cross-thread Stores are distinct. This kit uses `SqliteSaver` and a snapshot-backed `InMemoryStore` for local teaching.
- [LangGraph interrupt reference](https://reference.langchain.com/python/langgraph/types/interrupt): human review pauses a checkpointed graph; resume re-enters the node, so action execution is kept afterward.
- [LangGraph subgraphs](https://docs.langchain.com/oss/python/langgraph/use-subgraphs): Hour 4 compiles draft/review/revision into a child graph.
- [MCP Python SDK](https://github.com/modelcontextprotocol/python-sdk): the order server uses `FastMCP` and stdio transport.
- [LangChain MCP adapter client reference](https://reference.langchain.com/python/langchain-mcp-adapters/client): the kit uses the separately packaged `MultiServerMCPClient` to match the TOC.
- [Current LangChain MCP overview](https://docs.langchain.com/oss/python/langchain/mcp): newer versions also offer `MCPAdapter`; changing interfaces is a follow-on migration exercise, not required here.
- [LangSmith tracing](https://docs.langchain.com/langsmith/observability-quickstart): configure tracing via environment variables and inspect nested runs.
- [LangSmith evaluation](https://docs.langchain.com/langsmith/evaluate-llm-application): the optional cloud experiment uploads synthetic examples and applies a task-success evaluator.
- [CrewAI quickstart](https://docs.crewai.com/en/quickstart): optional six-minute sequential triage/Billing comparison in a separate environment.
- [GPT-4.1 mini model](https://developers.openai.com/api/docs/models/gpt-4.1-mini): configurable example model for the live provider integration. No token price is hardcoded.
- [A2A specification](https://a2a-protocol.org/latest/specification/): independent-agent interoperability, discovery, tasks, messages and results; covered as theory in Hour 5.

The source workbook is `Multi_Agent_System_Engineering_5hr_TOC.xlsx`, sheets `Hourly TOC` and `Summary`. Its activities determine the hourly mapping in `TOC_COVERAGE.md`; no instructions embedded in reference material are executed as user commands.
