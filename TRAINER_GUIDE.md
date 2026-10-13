# Trainer rehearsal and delivery script

## Before participants arrive

1. Extract the full kit and install it using the root README. Use Python 3.12.
2. Run `python scripts/preflight.py`, `python scripts/smoke_test.py`, and `python -m pytest -q`.
3. Run `python hour_03_memory_rag_mcp/mcp_demo.py`. Two JSON lines should identify Billing and Tech with the same authorized order.
4. If teaching live agents, configure `.env`, run one live Hour-2 ticket, open its LangSmith trace, then rehearse the Hour-4 approval. The included captured outputs are demo outputs, not proof that your provider configuration works.
5. Preinstall the optional CrewAI environment using Hour 4's instructions. Keep the main environment intact.
6. Rehearse the browser demonstration. Open the console and a second tab for LangSmith; enlarge the terminal font and editor font.
7. Reset each hour you intend to show fresh: `python scripts/reset_demo.py --hour 1` through `--hour 5`. Stop any API before resetting.
8. Keep the hourly captured outputs open as a fallback if the classroom network fails. Explain that they are previously captured deterministic runs.

## The storyline to repeat

“Ananya has one message but two problems. We need different expertise for payment evidence and damaged-device policy. The supervisor coordinates specialists, shared state carries evidence, retrieval supplies policy, and the approval gate controls the action. We can inspect every handoff and measure the outcome.”

Ask participants which part requires a model and which part should remain ordinary code. Payment arithmetic, ownership checks, authorization, amount limits and idempotency are deterministic. Intent interpretation and specialist explanations may benefit from LLMs.

## Teaching sequence and visible proof

| Hour | Show in the editor | Run and show | Ask participants |
|---|---|---|---|
| 1 | `common/agents.py: tools`, Hour-1 `graph.py` | Single replay/live loop, nine-tool variant, two-specialist result | Which evidence is missing if the agent cannot inspect payments? |
| 2 | `common/state.py`, Hour-2 graph conditional edges, `Agents.supervisor` | Router handles one team; supervisor completes Billing and Tech | Why does a one-pass router miss the second issue? |
| 3 | `memory.py`, `knowledge.py`, MCP server | Same-thread history, new-thread preference, retrieved source IDs, two MCP consumers | What belongs in a checkpoint versus a customer Store? |
| 4 | Review subgraph, `approval`, `simulate_refund` | Pause; restart CLI; approve/edit/reject; retry once; permanent failure | Why must side effects occur after an interrupt and be idempotent? |
| 5 | Evaluation CSV, trace, API endpoints | 15-case report, permission failure, streamed UI, approved result | How do we know a plausible reply is also a correct and authorized action? |

Use each hourly README's minute-by-minute table to stay within the original TOC. This is a guided build using supplied code and focused edits; it is not a from-empty-directory implementation of every feature in five hours.

## Final demonstration script, approximately 8 minutes

1. **0:00–1:00:** Open the browser console; identify customer/order IDs and the two issues in the message.
2. **1:00–2:00:** Submit; narrate triage → planner → supervisor → Billing → Tech. Expand source evidence in events.
3. **2:00–3:00:** Show `awaiting_approval` and explain the INR 1,000 threshold. Ask whether an LLM statement could authorize payment. Answer: authorization is application-controlled.
4. **3:00–4:00:** Approve. Show the final result and `simulated` status. Repeat with a new thread to demonstrate the unique refund ledger returning `already_simulated` after approval.
5. **4:00–5:00:** Show the LangSmith trace if configured. Otherwise show `metrics.jsonl` and explicitly explain why demo token counts are zero.
6. **5:00–6:00:** Open the 15-case evaluation report. Show a mixed ticket, cross-customer request and prompt-injection example.
7. **6:00–7:00:** Show `/docs`, API headers, and the SSE output; explain how another application consumes the service.
8. **7:00–8:00:** Show the Dockerfile/Compose health check or a prebuilt running container. Ask a participant to identify the checkpoint, Store, vector index and action ledger.

## Participant completion checklist

- Can explain the single-agent/tool-loop boundary and specialist tool scopes.
- Can predict which graph nodes execute for a mixed ticket.
- Can inspect thread history and retrieve a preference on a new thread.
- Can show a policy source ID and describe demo versus semantic embeddings.
- Can demonstrate a real MCP call from two specialists.
- Can pause and resume an approval without creating a duplicate simulated refund.
- Can explain routing accuracy, handoff correctness, task success, latency and token costs separately.
- Can run the API, see events in the console, and verify the final JSON result.

## What to say about limitations

“Demo mode proves the wiring and business rules on our synthetic fixtures. Live mode introduces model uncertainty; evaluate it separately. Keyword injection checks catch examples, not every attack. The API is a single-worker teaching deployment, and the refund action is simulated. A real service needs authenticated customer identity and durable shared infrastructure.”
