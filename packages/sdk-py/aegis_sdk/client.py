"""AEGIS Governance Platform client."""

from __future__ import annotations

import asyncio
import json
import urllib.error
import urllib.request

from aegis_sdk.errors import AegisAuthError, AegisConnectionError, AegisError
from aegis_sdk.types import ActionProposal, GovernanceDecision, Verdict

_PROPOSE_PATH = "/v1/governance/propose"
_DEFAULT_TIMEOUT = 30.0  # seconds


class AegisClient:
    """Client for the AEGIS Governance Platform API.

    Wraps the aegis-platform REST API to submit action proposals
    and receive governance decisions.

    Example::

        client = AegisClient(base_url="https://api.aegis-platform.net")
        decision = await client.propose(
            ActionProposal(
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
        url = f"{self.base_url.rstrip('/')}{_PROPOSE_PATH}"
        payload: dict[str, object] = {
            "capability": proposal.capability,
            "resource": proposal.resource,
            "parameters": proposal.parameters,
        }
        if proposal.trace_id is not None:
            payload["traceId"] = proposal.trace_id

        headers = {"Content-Type": "application/json", "Accept": "application/json"}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"

        request = urllib.request.Request(
            url,
            data=json.dumps(payload).encode("utf-8"),
            headers=headers,
            method="POST",
        )
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

        return self._parse_decision(raw)

    @staticmethod
    def _parse_decision(raw: bytes) -> GovernanceDecision:
        try:
            data = json.loads(raw)
            return GovernanceDecision(
                action_id=data["actionId"],
                decision=Verdict(data["decision"]),
                timestamp=data["timestamp"],
                reason=data.get("reason"),
                policy_ids=data.get("policyIds", []),
            )
        except (json.JSONDecodeError, KeyError, ValueError, TypeError) as exc:
            raise AegisError(
                f"malformed governance decision in API response: {exc}"
            ) from exc
