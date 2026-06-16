"""Tests for AegisClient.propose against a loopback governance endpoint.

The fake server implements POST /v1/governance/propose with a rule-based
verdict so each of the four outcomes — plus auth and connection failures —
is exercised over the real urllib code path.
"""

from __future__ import annotations

import asyncio
import json
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

import pytest

from aegis_sdk import ActionProposal, AegisClient, Verdict
from aegis_sdk.errors import AegisAuthError, AegisConnectionError, AegisError

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

    def do_POST(self):
        if self.path != "/v1/governance/propose":
            self.send_error(404, "not found")
            return
        # Require a bearer token; mirrors the platform's auth behaviour.
        if self.headers.get("Authorization") != "Bearer test-key":
            self.send_error(401, "missing or invalid api key")
            return
        body = json.loads(self.rfile.read(int(self.headers["Content-Length"])))
        verdict = _VERDICT_BY_CAPABILITY.get(body["capability"], Verdict.DENY)
        payload = json.dumps(
            {
                "actionId": "act-123",
                "decision": verdict.value,
                "timestamp": "2026-06-16T00:00:00Z",
                "reason": f"policy decision for {body['capability']}",
                "policyIds": ["POL-1", "POL-2"],
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
        client.propose(ActionProposal(capability=capability, resource="/x"))
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
