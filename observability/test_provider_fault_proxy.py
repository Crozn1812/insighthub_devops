"""Incident faults are explicit, bounded and do not fabricate model responses."""

from fastapi.testclient import TestClient
import provider_fault_proxy as proxy


def test_disabled_proxy_forwards_auth_and_real_response(monkeypatch):
    captured = {}

    class Client:
        def __init__(self, **kwargs):
            pass

        async def __aenter__(self):
            return self

        async def __aexit__(self, *args):
            pass

        async def request(self, method, url, **kwargs):
            captured.update(method=method, url=url, **kwargs)
            return proxy.httpx.Response(200, json={"id": "synthetic-test-response"})

    monkeypatch.setattr(proxy.httpx, "AsyncClient", Client)
    monkeypatch.setattr(proxy, "DELAY", 0)
    monkeypatch.setattr(proxy, "ERROR", False)
    response = TestClient(proxy.app).post('/v1/chat/completions',
        headers={'Authorization':'Bearer synthetic-unit-identity', 'X-Unrelated':'drop'},
        json={'model':'local-test'})
    assert response.status_code == 200
    assert response.json()['id'] == 'synthetic-test-response'
    assert captured['headers']['authorization'] == 'Bearer synthetic-unit-identity'
    assert 'x-unrelated' not in captured['headers']


def test_controlled_provider_error_does_not_generate(monkeypatch):
    monkeypatch.setattr(proxy, "ERROR", True)
    response = TestClient(proxy.app).post('/v1/chat/completions', json={})
    assert response.status_code == 503
    assert 'choices' not in response.json()


def test_transport_error_is_sanitized(monkeypatch):
    class Client:
        def __init__(self, **kwargs):
            raise proxy.httpx.ConnectError('synthetic-private-detail')
    monkeypatch.setattr(proxy.httpx, "AsyncClient", Client)
    monkeypatch.setattr(proxy, "ERROR", False)
    monkeypatch.setattr(proxy, "DELAY", 0)
    response = TestClient(proxy.app).post('/v1/chat/completions', json={})
    assert response.status_code == 502
    assert 'synthetic-private-detail' not in response.text
