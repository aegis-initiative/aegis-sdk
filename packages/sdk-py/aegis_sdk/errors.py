"""AEGIS SDK error hierarchy.

Every error carries a structured ``code`` (shared with the TypeScript SDK --
see ``../sdk-ts/src/errors.ts`` and ``docs/errors.md`` for the full taxonomy)
and a ``help_url`` pointing to the matching section of that taxonomy doc on
aegis-docs.com.
"""

from __future__ import annotations

_DOCS_BASE = "https://aegis-docs.com/sdk/errors"


class AegisError(Exception):
    """Base exception for all AEGIS SDK errors.

    Attributes:
        code:     Structured error code, shared with the TypeScript SDK.
        message:  Human-readable description of what went wrong.
        help_url: Link to the relevant section of the error taxonomy doc.
    """

    code: str = "AEGIS_SDK_GENERAL_001"
    help_url: str = f"{_DOCS_BASE}#aegis_sdk_general_001"

    def __init__(self, message: str, *, help_url: str | None = None) -> None:
        self.message = message
        if help_url is not None:
            self.help_url = help_url
        super().__init__(f"[{self.code}] {message}  (see {self.help_url})")


class AegisConnectionError(AegisError):
    """Raised when the SDK cannot reach the AEGIS API.

    Common causes: wrong endpoint URL, network issues, or the platform
    service is down.
    """

    code: str = "AEGIS_SDK_CONN_001"
    help_url: str = f"{_DOCS_BASE}#aegis_sdk_conn_001"

    def __init__(self, message: str, *, help_url: str | None = None) -> None:
        super().__init__(message, help_url=help_url or self.help_url)


class AegisAuthError(AegisError):
    """Raised when authentication fails (HTTP 401/403).

    Common causes: missing API key, expired key, or insufficient
    permissions.
    """

    code: str = "AEGIS_SDK_AUTH_001"
    help_url: str = f"{_DOCS_BASE}#aegis_sdk_auth_001"

    def __init__(self, message: str, *, help_url: str | None = None) -> None:
        super().__init__(message, help_url=help_url or self.help_url)


class AegisDeniedError(AegisError):
    """Raised when a governance proposal is denied.

    Attributes:
        reason:     Why the action was denied.
        policy_ids: List of policy IDs that caused the denial.

    Not currently raised by AegisClient.propose() -- a DENY verdict is a
    normal GovernanceDecision return value, not an exception (see
    client.py's module docstring). Kept for SDK consumers that want to
    convert a DENY decision into a raised error at their own call site.
    """

    code: str = "AEGIS_SDK_DENIED_001"
    help_url: str = f"{_DOCS_BASE}#aegis_sdk_denied_001"

    def __init__(
        self,
        reason: str,
        policy_ids: list[str],
        *,
        help_url: str | None = None,
    ) -> None:
        self.reason = reason
        self.policy_ids = policy_ids
        detail = f"Action denied: {reason} [policies: {', '.join(policy_ids)}]"
        super().__init__(detail, help_url=help_url or self.help_url)
