# Run, deploy and verify the output

All commands below run from the extracted `SupportDesk_Trainer_Kit` root with its virtual environment active. First copy `.env.example` to `.env`. Default mode is a deterministic classroom demo.

## A. Local service — recommended classroom path

1. Run `python scripts/preflight.py` and `python scripts/smoke_test.py`.
2. For a fresh demonstration, stop any running API, then run `python scripts/reset_demo.py --hour 5`.
3. Start the server:

```bash
python -m uvicorn hour_05_evaluation_deployment.api:app --host 127.0.0.1 --port 8000 --workers 1
```

4. Open `http://127.0.0.1:8000/health`. Expected: `{"status":"ok","mode":"demo","hour":5}`.
5. Open `http://127.0.0.1:8000`. Keep the prefilled message and click **Run and stream workflow**.
6. Show the events: intake → triage → planner → supervisor → billing → supervisor → tech → review → interrupt.
7. Show `status: awaiting_approval`, `refund_amount_inr: 2499`, and the `approval_request` payload. No ledger write has happened yet.
8. Keep the reviewer key, choose Approve, and click **Resume with decision**. Expected: `status: completed`, `refund_status: simulated`, and both issue findings in the response.
9. Open `http://127.0.0.1:8000/docs` and explain schemas and headers. `/tickets` and `/threads/{thread_id}` need `X-API-Key`; `/approvals` needs `X-Reviewer-Key`.
10. Stop with Ctrl+C. Do not start another process on the same port.

The browser displays real graph-update streaming, not token-by-token generation. The request uses HTTP POST with Server-Sent Events framing. It consumes events using `fetch()` because the browser's basic EventSource API cannot POST the ticket body. Heartbeats keep an idle stream active; a disconnected browser does not cancel an already-running ticket in this classroom implementation.

## B. Verify with curl

macOS/Linux shell examples; Windows users can send the same JSON with Swagger or use `curl.exe` and a JSON file to avoid quoting differences.

```bash
curl http://127.0.0.1:8000/health
curl -N http://127.0.0.1:8000/tickets/stream \
  -H 'Content-Type: application/json' \
  -H 'X-API-Key: classroom-customer-key' \
  -d '{"thread_id":"curl-1","ticket":{"customer_id":"C001","order_id":"ORD1001","message":"My headphones arrived damaged and I was charged twice."}}'
```

Observe `event: update` lines followed by `event: result` with `awaiting_approval`. Then:

```bash
curl http://127.0.0.1:8000/approvals \
  -H 'Content-Type: application/json' \
  -H 'X-Reviewer-Key: classroom-reviewer-key' \
  -d '{"thread_id":"curl-1","customer_id":"C001","decision":{"action":"approve"}}'
curl http://127.0.0.1:8000/threads/curl-1 \
  -H 'X-API-Key: classroom-customer-key'
```

For rejection replace the decision with `{"action":"reject"}`. For a reduced amount use `{"action":"edit","amount_inr":2000}` on a fresh unrefunded demo state. Values above the verified duplicate are rejected. Reusing an already-resumed approval returns HTTP 400, since it is no longer pending.

## C. Docker deployment

Docker Desktop/Engine must be installed and running. No image is published by these commands.

```bash
docker compose config
docker compose up --build -d
docker compose ps
docker compose logs --tail 100 supportdesk
curl http://127.0.0.1:8000/health
```

Open the same browser console and repeat steps A5–A8. The service binds the host port to loopback only. `.env` is passed at runtime and excluded from the image. A named volume stores checkpoints, Chroma, profiles and the simulated ledger.

To demonstrate checkpoint persistence:

1. Submit a new ticket and leave it awaiting approval.
2. Copy its thread ID from the UI.
3. Run `docker compose restart supportdesk` and wait for health to return.
4. In the console restore that same thread ID and customer, then submit the reviewer decision without resubmitting the ticket.
5. The persisted interrupt resumes. Inspect `/threads/{thread_id}` to confirm the result.

Stop with `docker compose down`; the named volume remains. `docker compose down -v` deletes the **container's synthetic runtime data** and gives a clean future demo. Host CLI runtime and container runtime are separate; `scripts/reset_demo.py` affects only the host folder.

The Docker image and deployment files are supplied. The delivery's validation report states whether the container build was actually exercised on the authoring host; do not interpret a supplied Dockerfile as a successful deployment.

## D. Hosting beyond the classroom

Use the Dockerfile on a container platform with a writable persistent volume and the service's listening port set to 8000. Keep **one worker/replica** for this exact implementation. Supply environment variables as platform secrets, replace the classroom keys, configure a trusted identity layer and TLS at ingress, and use `/health` as the health probe. A platform that mandates a `$PORT` variable should override the start command accordingly.

Horizontal scaling requires implementation changes: replace SQLite checkpoints with a shared durable checkpointer, replace the JSON snapshot adapter with a proper shared Store, move the refund ledger to a transactional shared database, and use per-thread concurrency control. The global lock in `api.py` intentionally serializes this one-worker teaching application. Proxies must support SSE and avoid buffering; allow enough request time for model calls plus retries. The local MCP child process is suitable here; a separately hosted MCP service needs explicit authentication and service connectivity.

No cloud account or hosting provider was supplied, so these are deployment instructions, not a claim that a public service has been published.

## Troubleshooting

| Symptom | Check or action |
|---|---|
| `ModuleNotFoundError` | Activate the kit's Python-3.12 environment and install root `requirements.txt`. Keep `common/` beside the hourly folders. |
| No API key configured | Use `--mode demo`, or edit root `.env` for live calls. Never paste private keys into tickets or slides. |
| Live call gets 401/429/model-not-found | Check provider key, model access, quota and billing. Test one live ticket before running the full evaluation. |
| No LangSmith trace | Check tracing flag, key, project and workspace endpoint; restart the API after edits and refresh the project after a run. |
| Demo shows zero tokens | Correct: no LLM was called. Switch to live for model token metrics. |
| Cost is `null` | Set current input/output token prices in `.env`; the application does not assume a price. |
| Thread has unfinished work | Resume a pending approval using the same thread/customer. After a failed read operation use a fresh thread; failed checkpoints remain inspectable. |
| `already_simulated` instead of `simulated` | The order was refunded earlier. Explain idempotency, or reset that hour's runtime before rerunning. |
| Edited refund conflicts with existing refund | Reset the synthetic demo or use a different unrefunded order; do not overwrite the ledger. |
| Preferences persist on a new thread | Expected cross-session memory. Reset the hour to clear profiles. |
| Changed/deleted knowledge still appears | Stop the service and reset that hour, then rebuild retrieval by running it again. |
| MCP hangs or returns malformed output | Use the same Python environment; do not print non-protocol text to the server's stdout. Client timeout is 15 seconds. |
| Docker cannot connect to daemon | Start Docker Desktop/Engine and ensure your account can access it. |
| Port 8000 is occupied | Stop the earlier server or select another local port and update URLs. |
| API refuses another customer's ticket | Classroom customer key maps to C001. Use the CLI for other fixtures or explicitly configure a different demo identity. |
