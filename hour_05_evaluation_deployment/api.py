"""Single-worker teaching service with customer/reviewer keys and event streaming."""
import json
import os
import queue
import secrets
import threading
from pathlib import Path
from fastapi import FastAPI, Header, HTTPException, Depends
from fastapi.responses import HTMLResponse, StreamingResponse
from pydantic import BaseModel, Field
from common.config import ROOT
from common.runner import run, session, graph_config, public_result
from common.state import Ticket, Decision

app = FastAPI(title='SupportDesk training API', version='1.0')
# JSON profile snapshots and a local SQLite checkpoint are a single-worker teaching setup.
RUN_LOCK = threading.Lock()


def customer_identity(x_api_key: str = Header(default='')):
    expected = os.getenv('DESK_API_KEY', 'classroom-customer-key')
    if not expected or not secrets.compare_digest(x_api_key, expected):
        raise HTTPException(401, 'Invalid customer API key')
    return os.getenv('DESK_CUSTOMER_ID', 'C001')


def reviewer_identity(x_reviewer_key: str = Header(default='')):
    expected = os.getenv('REVIEWER_API_KEY', 'classroom-reviewer-key')
    if not expected or not secrets.compare_digest(x_reviewer_key, expected):
        raise HTTPException(401, 'Invalid reviewer API key')
    return 'reviewer'


class Request(BaseModel):
    thread_id: str = Field(pattern=r'^[A-Za-z0-9_-]{1,80}$')
    ticket: Ticket
    use_mcp: bool = False


class Approval(BaseModel):
    thread_id: str = Field(pattern=r'^[A-Za-z0-9_-]{1,80}$')
    customer_id: str = Field(pattern=r'^C\d{3}$')
    decision: Decision


@app.get('/health')
def health():
    return {'status': 'ok', 'mode': os.getenv('APP_MODE', 'demo'), 'hour': 5}


@app.get('/', response_class=HTMLResponse)
def home():
    return (Path(__file__).parent / 'demo.html').read_text()


def authorize(body, customer):
    if body.ticket.customer_id != customer:
        raise HTTPException(403, 'Ticket customer does not match the API key identity')


@app.post('/tickets')
def submit(body: Request, customer=Depends(customer_identity)):
    authorize(body, customer)
    try:
        with RUN_LOCK:
            return run(5, body.ticket.model_dump(), thread=body.thread_id, use_mcp=body.use_mcp)
    except (ValueError, PermissionError) as exc:
        raise HTTPException(400, str(exc)) from exc


@app.post('/tickets/stream')
def stream(body: Request, customer=Depends(customer_identity)):
    authorize(body, customer)
    events = queue.Queue()

    def worker():
        try:
            with RUN_LOCK:
                result = run(5, body.ticket.model_dump(), thread=body.thread_id, use_mcp=body.use_mcp,
                             on_event=lambda e: events.put(('update', e)))
            events.put(('result', result))
        except Exception as exc:
            events.put(('error', {'type': type(exc).__name__, 'message': str(exc)}))
        finally:
            events.put(None)

    def generate():
        threading.Thread(target=worker, daemon=True).start()
        while True:
            try:
                item = events.get(timeout=10)
            except queue.Empty:
                yield ': heartbeat\n\n'
                continue
            if item is None:
                break
            event, data = item
            yield f'event: {event}\ndata: {json.dumps(data, default=str)}\n\n'

    return StreamingResponse(generate(), media_type='text/event-stream',
                             headers={'Cache-Control': 'no-cache', 'X-Accel-Buffering': 'no'})


@app.post('/approvals')
def approve(body: Approval, reviewer=Depends(reviewer_identity)):
    try:
        with RUN_LOCK:
            return run(5, customer=body.customer_id, thread=body.thread_id,
                       decision=body.decision.model_dump())
    except (ValueError, PermissionError) as exc:
        raise HTTPException(400, str(exc)) from exc


@app.get('/threads/{thread_id}')
def inspect(thread_id: str, customer=Depends(customer_identity)):
    with RUN_LOCK, session(5) as (graph, ctx):
        snapshot = graph.get_state(graph_config(customer, thread_id))
        if not snapshot.values:
            raise HTTPException(404, 'Thread not found for this customer')
        values = dict(snapshot.values)
        pauses = tuple(i for task in snapshot.tasks for i in task.interrupts)
        if pauses:
            values['__interrupt__'] = pauses
        return public_result(values, 5, ctx.mode, thread_id)
