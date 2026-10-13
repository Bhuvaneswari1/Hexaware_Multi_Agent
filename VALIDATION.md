# Validation report

Environment: Python **3.12.14**, macOS ARM64. Library versions are pinned in `requirements.txt`; the full resolved environment is recorded in `requirements-lock.txt`.

## Executed checks

| Check | Result |
|---|---|
| `python -m pytest -q` | **19 tests passed**, including parametrized cases. |
| `python scripts/preflight.py` | Core imports and installed versions verified; no provider/LangSmith keys configured. |
| `python scripts/smoke_test.py` | **All five hours passed**. Hours 1–3 produced proposals; Hours 4–5 paused and then recorded simulated refunds after approval. |
| `evaluate.py --mode demo` | **15/15** fixtures met route, completed-team and outcome expectations. |
| Real MCP stdio tool | Subprocess launched, tools discovered, authorized order returned. Also exercised in the captured Hour-3 example. |
| Chroma retrieval | Local hashed embeddings and policy source IDs exercised by workflows and tests. |
| Durable memory | SQLite history survives independent graph sessions; profile survives restart and is retrieved on a new thread. |
| Human review | Approval, rejection, valid edited amount, excessive edit rejection, repeated resume rejection and idempotent ledger behavior tested. |
| Reliability | One failed Billing read recovered; permanent injected outage escalated; deliberate graph loop failed at its bound and corrected loop terminated after four handoffs. |
| API | Health, authorization, customer isolation, SSE events/results, pause and approval tested with FastAPI's test client. |
| Live-code contract | Real LangChain `create_agent` executed a tool call and final answer using an offline scripted test model. This is not a provider test. |
| Browser | Local console opened; graph events and a completed rejected-refund result were inspected in the rendered browser. Layout and result text were visually checked. |
| Example outputs | Captured by running each default hourly graph in clean temporary runtime storage. |

The evaluation result is **deterministic fixture coverage**, not a general model-accuracy score. The demo router is based on declared keyword rules. A high score on this tiny dataset does not establish production reliability.

## Not executed in this environment

- Real provider LLM calls or paid semantic embeddings: no API key was supplied/configured.
- Cloud LangSmith trace delivery, dataset upload or experiment execution: no LangSmith credentials were supplied/configured.
- Live model-as-judge evaluation and the optional CrewAI comparison: require a provider key; the optional CrewAI environment was not executed.
- Docker image build or container runtime: the authoring environment could not access the Docker daemon socket. Dockerfile, Compose configuration and verification commands are supplied, but a successful container build is not claimed.
- Cloud publication: no target cloud account or provider was supplied; deployment guidance is included.
- Windows/Linux execution: commands are provided; local execution was verified on macOS Python 3.12.

Rehearse live calls and Docker on the trainer's machine before class. These limitations do not affect the tested local demo and API paths.
