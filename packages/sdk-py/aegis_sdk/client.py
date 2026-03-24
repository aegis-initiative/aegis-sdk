"""AEGIS Python SDK client.

Provides ``AegisClient``, the main entry-point for interacting with
the AEGIS governance platform API.  Uses only the Python standard
library (``urllib.request``) so there are zero external runtime
dependencies.
"""

from __future__ import annotations

import json
import urllib.error
import urllib.request
from typing import Any

from .errors import AegisAuthError, AegisConnectionError, AegisDeniedError, AegisError
from .types import GovernanceDecision, Verdict

_DEFAULT_TIMEOUT = 30  # seconds


class AegisClient:
    """Synchronous client for the AEGIS governance API.

    Args:
        endpoint: Base URL of the AEGIS platform
                  (e.g. ``"https://api.aegissystems.app"``).
        api_key:  Optional API key for authentication.  When provided it
                  is sent as an ``Authorization: Bearer <key>`` header on
                  every request.
        timeout:  HTTP request timeout in seconds (default 30).

    Example::

        client = AegisClient("https://api.aegissystems.app", api_key="ak_...")
        decision = client.propose("file.write", "/etc/hosts")
        print(decision.verdict)
    """

    def __init__(
        self,
        endpoint: str,
        api_key: str | None = None,
        *,
        timeout: int = _DEFAULT_TIMEOUT,
    ) -> None:
        # Strip trailing slash so callers don't have to worry about it.
        self._endpoint = endpoint.rstrip("/")
        self._api_key = api_key
        self._timeout = timeout

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def propose(
        self,
        capability: str,
        resource: str,
        parameters: dict | None = None,
    ) -> GovernanceDecision:
        """Submit an action proposal for governance evaluation.

        Args:
            capability: The capability being requested
                        (e.g. ``"file.write"``).
            resource:   The target resource
                        (e.g. ``"/etc/hosts"``).
            parameters: Optional extra parameters for the action.

        Returns:
            A :class:`GovernanceDecision` describing the platform's
            verdict.

        Raises:
            AegisDeniedError: If the action was denied.  The exception
                carries the denial *reason* and *policy_ids*.
            AegisAuthError: If the API returns 401 or 403.
            AegisConnectionError: If the API is unreachable.
            AegisError: For any other unexpected API error.
        """
        payload: dict[str, Any] = {
            "capability": capability,
            "resource": resource,
        }
        if parameters is not None:
            payload["parameters"] = parameters

        data = self._post("/api/v1/governance/propose", payload)

        decision = _parse_decision(data)

        if decision.verdict is Verdict.DENY:
            raise AegisDeniedError(
                reason=decision.reason,
                policy_ids=list(decision.policy_ids),
            )

        return decision

    def health(self) -> dict:
        """Check the health of the AEGIS platform.

        Returns:
            The JSON response from ``GET /api/v1/health`` as a dict.

        Raises:
            AegisConnectionError: If the API is unreachable.
            AegisError: For any other unexpected API error.
        """
        return self._get("/api/v1/health")

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _headers(self) -> dict[str, str]:
        headers: dict[str, str] = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "User-Agent": "aegis-sdk-py/0.1.0",
        }
        if self._api_key is not None:
            headers["Authorization"] = f"Bearer {self._api_key}"
        return headers

    def _get(self, path: str) -> dict:
        url = f"{self._endpoint}{path}"
        req = urllib.request.Request(url, headers=self._headers(), method="GET")
        return self._send(req)

    def _post(self, path: str, body: dict) -> dict:
        url = f"{self._endpoint}{path}"
        data = json.dumps(body).encode("utf-8")
        req = urllib.request.Request(
            url, data=data, headers=self._headers(), method="POST"
        )
        return self._send(req)

    def _send(self, req: urllib.request.Request) -> dict:
        try:
            with urllib.request.urlopen(req, timeout=self._timeout) as resp:
                raw = resp.read().decode("utf-8")
                return json.loads(raw)  # type: ignore[no-any-return]
        except urllib.error.HTTPError as exc:
            self._handle_http_error(exc)
        except urllib.error.URLError as exc:
            raise AegisConnectionError(
                f"Cannot reach AEGIS API at {req.full_url}: {exc.reason}"
            ) from exc
        except OSError as exc:
            raise AegisConnectionError(
                f"Network error contacting AEGIS API at {req.full_url}: {exc}"
            ) from exc

        # Unreachable, but keeps mypy happy.
        raise AegisError("Unexpected error during HTTP request")  # pragma: no cover

    @staticmethod
    def _handle_http_error(exc: urllib.error.HTTPError) -> None:
        """Translate HTTP errors into typed SDK exceptions."""
        body_text = ""
        try:
            body_text = exc.read().decode("utf-8", errors="replace")
        except Exception:  # noqa: BLE001
            pass

        if exc.code in (401, 403):
            raise AegisAuthError(
                f"Authentication failed (HTTP {exc.code}): {body_text}"
            ) from exc

        raise AegisError(
            f"AEGIS API error (HTTP {exc.code}): {body_text}"
        ) from exc


# ------------------------------------------------------------------
# Module-level helpers
# ------------------------------------------------------------------


def _parse_decision(data: dict) -> GovernanceDecision:
    """Deserialise a JSON dict into a ``GovernanceDecision``."""
    raw_verdict = data.get("verdict", "")
    try:
        verdict = Verdict(raw_verdict)
    except ValueError:
        raise AegisError(
            f"Unknown verdict '{raw_verdict}' returned by the API"
        ) from None

    return GovernanceDecision(
        verdict=verdict,
        reason=data.get("reason", ""),
        policy_ids=data.get("policy_ids", []),
        audit_id=data.get("audit_id", ""),
        timestamp=data.get("timestamp", ""),
    )
