"""Tests for AegisClient against a loopback governance endpoint.

The fake server implements the three real endpoints (propose, list
capabilities, query audit events) with just enough logic to exercise each
of AegisClient's methods -- including a rule-based verdict for propose so
each of the four outcomes, plus auth and connection failures, is exercised
over the real urllib code path.
"""

from __future__ import annotations

import asyncio
import json
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlparse

import pytest

from aegis_sdk import ActionProposal, Actor, AegisClient, Verdict
from aegis_sdk import client as _client_module
from aegis_sdk.errors import AegisAuthError, AegisConnectionError, AegisError

_CAPABILITIES = [
    {
        "id": "cap-1",
        "name": "file.read",
        "description": "Read files",
        "action_types": ["file_read"],
        "target_patterns": ["/home/*"],
        "platform": "linux",
    },
    {
        "id": "cap-2",
        "name": "file.write",
        "description": "Write files",
        "action_types": ["file_write"],
        "target_patterns": ["*"],
        "platform": "any",
    },
]

_AUDIT_EVENTS = [
    {
        "id": "evt-1",
        "timestamp": "2026-06-16T00:00:00Z",
        "source": "governance",
        "session_id": "sess-1",
        "agent_id": "agent-test",
        "action_type": "file_read",
        "action_target": "/home/x",
        "decision": "ALLOW",
        "reason": "matched policy POL-1",
    },
    {
        "id": "evt-2",
        "timestamp": "2026-06-16T00:01:00Z",
        "source": "platform",
        "session_id": "sess-1",
        "event_type": "capability.create",
        "resource_id": "cap-2",
        "summary": "Created capability 'file.write'",
    },
]

# Map a requested capability to the verdict the fake engine returns.
_VERDICT_BY_CAPABILITY = {
    "file:read": Verdict.ALLOW,
    "file:write": Verdict.DENY,
    "network:request": Verdict.ESCALATE,
    "secret:rotate": Verdict.REQUIRE_CONFIRMATION,
}


class _Handler(BaseHTTPRequestHandler):
    def log_message(self, *_args):  # silence test output
        pass

    def _send_json(self, payload: dict) -> None:
        body = json.dumps(payload).encode()
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        if self.headers.get("Authorization") != "Bearer test-key":
            self.send_error(401, "missing or invalid api key")
            return

        parsed = urlparse(self.path)
        if parsed.path == "/api/v1/capabilities":
            self._send_json(
                {"capabilities": _CAPABILITIES, "count": len(_CAPABILITIES)}
            )
            return
        if parsed.path == "/api/v1/audit/events":
            query = parse_qs(parsed.query)
            events = _AUDIT_EVENTS
            if "agent_id" in query:
                events = [
                    e for e in events if e.get("agent_id") == query["agent_id"][0]
                ]
            if "decision" in query:
                events = [
                    e for e in events if e.get("decision") == query["decision"][0]
                ]
            self._send_json({"events": events, "count": len(events)})
            return
        self.send_error(404, "not found")

    def do_POST(self):
        if self.path != "/api/v1/governance/propose":
            self.send_error(404, "not found")
            return
        # Require a bearer token; mirrors the platform's auth behaviour.
        if self.headers.get("Authorization") != "Bearer test-key":
            self.send_error(401, "missing or invalid api key")
            return
        body = json.loads(self.rfile.read(int(self.headers["Content-Length"])))
        assert body["actor"] == {"id": "agent-test", "type": "ai-agent"}
        verdict = _VERDICT_BY_CAPABILITY.get(body["capability"], Verdict.DENY)
        payload = json.dumps(
            {
                "action_id": "act-123",
                "decision": verdict.value,
                "timestamp": "2026-06-16T00:00:00Z",
                "reason": f"policy decision for {body['capability']}",
                "policy_ids": ["POL-1", "POL-2"],
                "risk_score": 0.0,
                "audit_ref": "audit-456",
            }
        ).encode()
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(payload)))
        self.end_headers()
        self.wfile.write(payload)


@pytest.fixture
def server():
    httpd = ThreadingHTTPServer(("127.0.0.1", 0), _Handler)
    thread = threading.Thread(target=httpd.serve_forever, daemon=True)
    thread.start()
    yield f"http://127.0.0.1:{httpd.server_address[1]}"
    httpd.shutdown()


def _propose(base_url, capability, *, api_key="test-key"):
    client = AegisClient(base_url=base_url, api_key=api_key)
    return asyncio.run(
        client.propose(
            ActionProposal(
                actor=Actor(id="agent-test", type="ai-agent"),
                capability=capability,
                resource="/x",
            )
        )
    )


@pytest.mark.parametrize(
    "capability,expected",
    [
        ("file:read", Verdict.ALLOW),
        ("file:write", Verdict.DENY),
        ("network:request", Verdict.ESCALATE),
        ("secret:rotate", Verdict.REQUIRE_CONFIRMATION),
    ],
)
def test_all_four_verdicts(server, capability, expected):
    decision = _propose(server, capability)
    assert decision.decision is expected
    assert decision.action_id == "act-123"
    assert decision.policy_ids == ["POL-1", "POL-2"]
    assert decision.reason and capability in decision.reason


def test_deny_is_returned_not_raised(server):
    # A DENY verdict is a normal return value, not an exception.
    decision = _propose(server, "file:write")
    assert decision.decision is Verdict.DENY


def test_auth_error_on_missing_key(server):
    with pytest.raises(AegisAuthError):
        _propose(server, "file:read", api_key=None)


def test_connection_error_on_dead_endpoint():
    # Port 1 is reserved and never listening → connection refused.
    with pytest.raises(AegisConnectionError):
        _propose("http://127.0.0.1:1", "file:read")


def test_timeout_during_response_body_raises_connection_error(monkeypatch):
    # Distinct from test_connection_error_on_dead_endpoint: that case never
    # connects at all, which urllib surfaces as urllib.error.URLError. This
    # case connects fine and starts the response, then stalls mid-body — a
    # timeout at that point comes back from response.read() as a bare
    # TimeoutError, a sibling of URLError under OSError rather than a
    # subclass of it, so it needs its own except clause in the client.
    class _StallingHandler(BaseHTTPRequestHandler):
        def log_message(self, *_args):
            pass

        def do_POST(self):
            self.rfile.read(int(self.headers["Content-Length"]))
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", "1000")  # promise more than we send
            self.end_headers()
            self.wfile.write(b"{")  # partial body, then stall past the client timeout
            self.wfile.flush()
            threading.Event().wait(1)

    httpd = ThreadingHTTPServer(("127.0.0.1", 0), _StallingHandler)
    threading.Thread(target=httpd.serve_forever, daemon=True).start()
    monkeypatch.setattr(_client_module, "_DEFAULT_TIMEOUT", 0.2)
    try:
        with pytest.raises(AegisConnectionError):
            _propose(f"http://127.0.0.1:{httpd.server_address[1]}", "file:read")
    finally:
        httpd.shutdown()


def test_list_capabilities(server):
    client = AegisClient(base_url=server, api_key="test-key")
    caps = asyncio.run(client.list_capabilities())
    assert [c.id for c in caps] == ["cap-1", "cap-2"]
    assert caps[0].platform == "linux"
    assert caps[1].platform == "any"
    assert caps[0].action_types == ["file_read"]


def test_get_audit_events_unfiltered(server):
    client = AegisClient(base_url=server, api_key="test-key")
    events = asyncio.run(client.get_audit_events())
    assert [e.id for e in events] == ["evt-1", "evt-2"]
    assert events[0].source == "governance"
    assert events[0].decision == "ALLOW"
    assert events[1].source == "platform"
    assert events[1].summary == "Created capability 'file.write'"


def test_get_audit_events_filtered_by_agent_id(server):
    client = AegisClient(base_url=server, api_key="test-key")
    events = asyncio.run(client.get_audit_events(agent_id="agent-test"))
    assert [e.id for e in events] == ["evt-1"]


def test_get_audit_events_filtered_by_decision(server):
    client = AegisClient(base_url=server, api_key="test-key")
    events = asyncio.run(client.get_audit_events(decision="ALLOW"))
    assert [e.id for e in events] == ["evt-1"]


def test_list_capabilities_auth_error_on_missing_key(server):
    client = AegisClient(base_url=server, api_key=None)
    with pytest.raises(AegisAuthError):
        asyncio.run(client.list_capabilities())


def test_malformed_response_raises_aegis_error():
    class _BadHandler(_Handler):
        def do_POST(self):
            if self.headers.get("Authorization") != "Bearer test-key":
                self.send_error(401)
                return
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(b'{"not":"a decision"}')

    httpd = ThreadingHTTPServer(("127.0.0.1", 0), _BadHandler)
    threading.Thread(target=httpd.serve_forever, daemon=True).start()
    try:
        with pytest.raises(AegisError):
            _propose(f"http://127.0.0.1:{httpd.server_address[1]}", "file:read")
    finally:
        httpd.shutdown()
