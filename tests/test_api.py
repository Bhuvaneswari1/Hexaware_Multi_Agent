import pytest
from fastapi.testclient import TestClient
from hour_05_evaluation_deployment.api import app


@pytest.fixture
def client(tmp_path, monkeypatch):
    monkeypatch.setenv('DESK_RUNTIME_DIR', str(tmp_path))
    monkeypatch.setenv('APP_MODE', 'demo')
    monkeypatch.setenv('LANGSMITH_TRACING', 'false')
    monkeypatch.setenv('EMBEDDING_BACKEND', 'local_hash')
    monkeypatch.setenv('DESK_API_KEY', 'test-customer')
    monkeypatch.setenv('REVIEWER_API_KEY', 'test-reviewer')
    return TestClient(app)


def body():
    return {'thread_id': 'api-test', 'ticket': {'customer_id':'C001','order_id':'ORD1001',
            'message':'My headphones arrived damaged and I was charged twice.'}}


def test_api_pause_resume_auth(client):
    assert client.get('/health').json()['status'] == 'ok'
    assert client.post('/tickets', json=body()).status_code == 401
    result = client.post('/tickets', json=body(), headers={'X-API-Key':'test-customer'})
    assert result.status_code == 200 and result.json()['status'] == 'awaiting_approval'
    approval = {'thread_id':'api-test','customer_id':'C001','decision':{'action':'approve'}}
    assert client.post('/approvals',json=approval,headers={'X-API-Key':'test-customer'}).status_code == 401
    done = client.post('/approvals',json=approval,headers={'X-Reviewer-Key':'test-reviewer'})
    assert done.json()['refund_status'] == 'simulated'
    assert client.post('/approvals',json=approval,headers={'X-Reviewer-Key':'test-reviewer'}).status_code == 400


def test_stream_and_customer_isolation(client):
    result = client.post('/tickets/stream',json=body(),headers={'X-API-Key':'test-customer'})
    assert 'event: update' in result.text and 'event: result' in result.text
    assert 'awaiting_approval' in result.text
    bad = body()
    bad['ticket']['customer_id'] = 'C002'
    assert client.post('/tickets',json=bad,headers={'X-API-Key':'test-customer'}).status_code == 403
    assert client.get('/threads/no-such-thread',headers={'X-API-Key':'test-customer'}).status_code == 404
