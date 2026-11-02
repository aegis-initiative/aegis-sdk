"""AEGIS Governance Platform client."""

from __future__ import annotations

import asyncio
import json
import urllib.error
import urllib.parse
import urllib.request
from typing import Any

from aegis_sdk.errors import AegisAuthError, AegisConnectionError, AegisError
from aegis_sdk.types import (
    ActionProposal,
    AuditEvent,
    Capability,
    GovernanceDecision,
    Verdict,
)

_PROPOSE_PATH = "/api/v1/governance/propose"
_CAPABILITIES_PATH = "/api/v1/capabilities"
_AUDIT_EVENTS_PATH = "/api/v1/audit/events"
_DEFAULT_TIMEOUT = 30.0  # seconds


class AegisClient:
    """Client for the AEGIS Governance Platform API.

    Wraps the aegis-platform REST API to submit action proposals
    and receive governance decisions.

    Example::

        client = AegisClient(base_url="https://demo.aegis-platform.net")
        decision = await client.propose(
            ActionProposal(
                actor=Actor(id="agent-soc-001", type="ai-agent"),
                capability="file:write",
                resource="/etc/config",
                parameters={"content": "..."},
            )
        )
    """

    def __init__(self, *, base_url: str, api_key: str | None = None) -> None:
        self.base_url = base_url
        self.api_key = api_key

    async def propose(self, proposal: ActionProposal) -> GovernanceDecision:
        """Submit an action proposal to the AEGIS governance engine.

        The governance engine evaluates the proposal against active policies
        and returns one of four verdicts: ALLOW, DENY, ESCALATE, or
        REQUIRE_CONFIRMATION. All four are returned as a ``GovernanceDecision``;
        a DENY verdict is a normal return, not an exception.

        Args:
            proposal: The action proposal to evaluate.

        Returns:
            A governance decision with verdict, reason, and policy IDs.

        Raises:
            AegisAuthError: Authentication failed (HTTP 401/403).
            AegisConnectionError: The platform API could not be reached.
            AegisError: The API returned an error status or a malformed body.
        """
        # The SDK has no runtime dependencies, so the HTTP call uses the stdlib
        # (urllib, which is blocking). Run it in a worker thread to preserve the
        # async signature shared with the TypeScript SDK without blocking the
        # caller's event loop.
        return await asyncio.to_thread(self._propose_sync, proposal)

    def _propose_sync(self, proposal: ActionProposal) -> GovernanceDecision:
        payload: dict[str, object] = {
            "actor": {"id": proposal.actor.id, "type": proposal.actor.type},
            "capability": proposal.capability,
            "resource": proposal.resource,
            "parameters": proposal.parameters,
        }
        if proposal.trace_id is not None:
            payload["trace_id"] = proposal.trace_id

        data = self._request_sync("POST", _PROPOSE_PATH, json_body=payload)
        try:
            return GovernanceDecision(
                action_id=data["action_id"],
                decision=Verdict(data["decision"]),
                timestamp=data["timestamp"],
                reason=data.get("reason"),
                policy_ids=data.get("policy_ids", []),
                risk_score=data.get("risk_score"),
                audit_ref=data.get("audit_ref"),
            )
        except (KeyError, ValueError, TypeError) as exc:
            raise AegisError(
                f"malformed governance decision in API response: {exc}"
            ) from exc

    async def list_capabilities(self) -> list[Capability]:
        """List all capabilities registered in the governance runtime.

        Returns:
            Every capability visible to the caller's session (or the
            shared anonymous seed, if no API key is set).

        Raises:
            AegisAuthError: Authentication failed (HTTP 401/403).
            AegisConnectionError: The platform API could not be reached.
            AegisError: The API returned an error status or a malformed body.
        """
        return await asyncio.to_thread(self._list_capabilities_sync)

    def _list_capabilities_sync(self) -> list[Capability]:
        data = self._request_sync("GET", _CAPABILITIES_PATH)
        try:
            return [
                Capability(
                    id=c["id"],
                    name=c["name"],
                    description=c["description"],
                    action_types=c["action_types"],
                    target_patterns=c["target_patterns"],
                    platform=c.get("platform", "any"),
                )
                for c in data["capabilities"]
            ]
        except (KeyError, TypeError) as exc:
            raise AegisError(
                f"malformed capabilities list in API response: {exc}"
            ) from exc

    async def get_audit_events(
        self,
        *,
        agent_id: str | None = None,
        decision: str | None = None,
        limit: int = 50,
    ) -> list[AuditEvent]:
        """Query the unified audit log.

        Merges the governance-decision trail with the platform-layer CRUD
        trail (Policy/Profile/Capability/EndpointPolicy changes);
        ``AuditEvent.source`` discriminates which fields are populated.
        Records are scoped to the caller's session.

        Args:
            agent_id: Filter to decisions made by this agent (governance
                entries only).
            decision: Filter to this verdict, e.g. "DENY" (governance
                entries only).
            limit: Maximum number of records to return (1-200).

        Returns:
            Matching audit events, most recent first.

        Raises:
            AegisAuthError: Authentication failed (HTTP 401/403).
            AegisConnectionError: The platform API could not be reached.
            AegisError: The API returned an error status or a malformed body.
        """
        return await asyncio.to_thread(
            self._get_audit_events_sync, agent_id, decision, limit
        )

    def _get_audit_events_sync(
        self, agent_id: str | None, decision: str | None, limit: int
    ) -> list[AuditEvent]:
        params: dict[str, str] = {"limit": str(limit)}
        if agent_id is not None:
            params["agent_id"] = agent_id
        if decision is not None:
            params["decision"] = decision

        data = self._request_sync("GET", _AUDIT_EVENTS_PATH, params=params)
        try:
            return [
                AuditEvent(
                    id=e["id"],
                    timestamp=e["timestamp"],
                    source=e.get("source", "governance"),
                    session_id=e.get("session_id", ""),
                    request_id=e.get("request_id"),
                    agent_id=e.get("agent_id"),
                    action_type=e.get("action_type"),
                    action_target=e.get("action_target"),
                    decision=e.get("decision"),
                    reason=e.get("reason"),
                    event_type=e.get("event_type"),
                    resource_id=e.get("resource_id"),
                    summary=e.get("summary"),
                )
                for e in data["events"]
            ]
        except (KeyError, TypeError) as exc:
            raise AegisError(
                f"malformed audit events list in API response: {exc}"
            ) from exc

    def _request_sync(
        self,
        method: str,
        path: str,
        *,
        json_body: dict[str, object] | None = None,
        params: dict[str, str] | None = None,
    ) -> dict[str, Any]:
        """Issue one HTTP request and return its parsed JSON body.

        Shared by every endpoint method -- the response SHAPE (which
        fields mean what) is endpoint-specific and parsed by the caller;
        this only handles the request/transport/error-status concerns
        common to all of them.
        """
        url = f"{self.base_url.rstrip('/')}{path}"
        if params:
            url = f"{url}?{urllib.parse.urlencode(params)}"

        headers = {"Accept": "application/json"}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        data = None
        if json_body is not None:
            headers["Content-Type"] = "application/json"
            data = json.dumps(json_body).encode("utf-8")

        request = urllib.request.Request(url, data=data, headers=headers, method=method)
        try:
            with urllib.request.urlopen(request, timeout=_DEFAULT_TIMEOUT) as response:
                raw = response.read()
        except urllib.error.HTTPError as exc:
            if exc.code in (401, 403):
                raise AegisAuthError(
                    f"authentication failed (HTTP {exc.code})"
                ) from exc
            detail = exc.read().decode("utf-8", "replace")[:500] if exc.fp else ""
            message = f"governance API returned HTTP {exc.code}: {exc.reason}. {detail}"
            raise AegisError(message.strip()) from exc
        except (urllib.error.URLError, TimeoutError) as exc:
            # A timeout that occurs establishing the connection surfaces as
            # urllib.error.URLError (reason=socket.timeout), but a timeout
            # that occurs mid-transfer while reading the response body
            # surfaces as a bare TimeoutError — a sibling of URLError under
            # OSError, not a subclass of it, so it needs its own branch here
            # rather than falling through uncaught.
            reason = exc.reason if isinstance(exc, urllib.error.URLError) else exc
            raise AegisConnectionError(
                f"could not reach AEGIS platform at {self.base_url}: {reason}"
            ) from exc

        try:
            parsed: dict[str, Any] = json.loads(raw)
        except json.JSONDecodeError as exc:
            raise AegisError(f"malformed JSON in API response: {exc}") from exc
        return parsed
