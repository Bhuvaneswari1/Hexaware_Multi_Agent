# Mapping to the supplied five-hour TOC

Source: `Multi_Agent_System_Engineering_5hr_TOC.xlsx`, `Hourly TOC` rows 5–28. The workbook's five-hour allocation is preserved. Theory-only topics are marked explicitly rather than implied to be implemented.

| Hour / minutes | Source activity | Implementation or teaching reference | Observable proof |
|---|---|---|---|
| 1 / 12 | Agents, single vs multi-agent, roles/goals/messages, framework landscape | Hour-1 README concepts; `common/agents.py` | Explain model/tool/state boundaries and framework choices |
| 1 / 8 | Environment, keys, smoke LLM call | Root install steps, `scripts/preflight.py`, Hour-1 `smoke_llm.py` | Imports work; live smoke call prints reply/usage with credentials |
| 1 / 18 | Single ReAct/tool-using agent | Hour-1 graph `single`; `create_agent` | Model/tool loop in live mode; declared scripted replay in demo |
| 1 / 10 | Nine-tool overload and observations | `overloaded` pattern; `tool_trace.json`; `failure_log_template.csv` | Compare available/called tools and missing evidence; record success or failure honestly |
| 1 / 12 | Split Billing and Tech | Hour-1 `specialists`; role tool lists | Two specialist findings, proposed INR 2,499 refund |
| 2 / 12 | Graph patterns, handoffs, shared/private context | Hour-2 theory; `workflow.mmd` | Compare sequential, router, supervisor, hierarchical and network concepts |
| 2 / 12 | Typed state and sequential pipeline | `common/state.py`; `--pattern sequential` | Triage → Billing → Tech → writer |
| 2 / 14 | Conditional router | `--pattern router` | Single selected specialist; mixed-ticket limitation is visible |
| 2 / 22 | Supervisor reviews and delegates with handoffs | `Agents.supervisor`, `Command`; `--pattern supervisor` | Remaining-work queue, two completed teams, bounded reassignment for missing findings |
| 3 / 12 | Memory, persistence, RAG and MCP design | Hour-3 concepts | Distinguish checkpoints, Store, vector index and shared tools |
| 3 / 12 | Thread checkpointing | `SqliteSaver`; `--thread`, `--inspect` | Separate CLI processes retain four-message conversation history |
| 3 / 10 | Cross-session Store | `ProfileMemory`, `InMemoryStore` plus JSON snapshot | New thread recalls preference and prior issues for same customer |
| 3 / 14 | Shared Knowledge agent and RAG | `KnowledgeBase`; `ask_knowledge_agent`; `knowledge_demo.py` | Chroma source IDs; nested live Knowledge agent is restricted to retrieval |
| 3 / 12 | MCP order lookup shared by two agents | `mcp_server.py`, `mcp_demo.py`, `--mcp` | Real subprocess/tool round trips from Billing and Tech |
| 4 / 12 | Planner/executor, critic/debate, HITL and failure modes | Hour-4 concepts | Debate is discussed; planner/critic/HITL are implemented |
| 4 / 16 | Planner, executor team and critic subgraph | Hour-4 graph review subgraph | Plan, draft, review, one bounded revision and failure fallback |
| 4 / 14 | Approve, edit or reject and resume | `interrupt`, `Command(resume=...)`, decision validation | Durable pause, approved/reduced/rejected simulated refund |
| 4 / 12 | Loops, retries, timeout and fallback | `reliability_demo.py`; `--fault once/always`; per-call timeouts | Loop caught; fixed graph terminates; retry recovers or escalates |
| 4 / 6 | CrewAI comparison | `crewai_comparison.py` and separate requirements | Optional real-model triage/Billing task sequence; compare code and control |
| 5 / 12 | Evaluation, tracing, security, deployment and A2A | Hour-5 concepts | A2A is an overview; HTTP/SSE deployment is implemented |
| 5 / 10 | Tracing and per-agent cost/latency | LangSmith env configuration; `metrics_report.py` | Node durations, model usage where available, optional configured-price estimate |
| 5 / 14 | Fifteen tickets, task/routing quality evaluation | `test_tickets.csv`, `evaluate.py`, pytest; `--judge`, `--langsmith` | Local CSV/summary, optional subjective judge and cloud experiment |
| 5 / 10 | Prompt injection and tool permission scope | `injection_input.json`, `permission_demo.py`, API auth tests | Escalation on sample attack; role/approval/ownership rejection |
| 5 / 14 | Streaming API, container and end-to-end demo | `api.py`, `demo.html`, root Dockerfile/Compose/DEPLOYMENT | Browser graph events, pause/resume, HTTP output and deployment verification steps |

## Deliberate modernization and scope

- The TOC's older prebuilt ReAct name is implemented with the current `langchain.agents.create_agent` API. The teaching concept remains model → tool → observation → next decision.
- `SqliteSaver` provides actual cross-process checkpoint persistence. `InMemoryStore` alone is not durable, so the classroom adapter snapshots profiles; production Store infrastructure is a follow-on.
- The writer is ordinary deterministic code. Calling every function an LLM agent would obscure which components require reasoning and which should enforce a contract.
- Live specialists can call a shared Knowledge agent. Demo mode executes deterministic retrieval and business nodes with real infrastructure.
- `langchain-mcp-adapters` is retained to match the source TOC and is version-pinned. Newer MCP interfaces are linked in REFERENCES.md.
- Tracing uses LangSmith, one of the TOC's alternatives. Evaluation uses pytest plus optional LangSmith and a structured model judge; Langfuse and DeepEval are not installed redundantly.
- AutoGen, OpenAI Agents SDK, network/debate patterns and A2A are discussion topics, as distinct from the implemented graph workflows and the optional CrewAI code.
- CSVs replace enterprise backends for reproducibility. No real payment, replacement shipment or customer notification is issued.
