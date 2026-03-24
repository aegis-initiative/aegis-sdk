"""AEGIS SDK error hierarchy.

All errors include a ``help_url`` attribute pointing to relevant
documentation on aegis-docs.com.
"""

from __future__ import annotations

_DOCS_BASE = "https://aegis-docs.com/sdk/python/errors"


class AegisError(Exception):
    """Base exception for all AEGIS SDK errors.

    Attributes:
        message:  Human-readable description of what went wrong.
        help_url: Link to the relevant troubleshooting page.
    """

    help_url: str = f"{_DOCS_BASE}#aegis-error"

    def __init__(self, message: str, *, help_url: str | None = None) -> None:
        self.message = message
        if help_url is not None:
            self.help_url = help_url
        super().__init__(f"{message}  (see {self.help_url})")


class AegisConnectionError(AegisError):
    """Raised when the SDK cannot reach the AEGIS API.

    Common causes: wrong endpoint URL, network issues, or the platform
    service is down.
    """

    help_url: str = f"{_DOCS_BASE}#connection-error"

    def __init__(self, message: str, *, help_url: str | None = None) -> None:
        super().__init__(message, help_url=help_url or self.help_url)


class AegisAuthError(AegisError):
    """Raised when authentication fails (HTTP 401/403).

    Common causes: missing API key, expired key, or insufficient
    permissions.
    """

    help_url: str = f"{_DOCS_BASE}#auth-error"

    def __init__(self, message: str, *, help_url: str | None = None) -> None:
        super().__init__(message, help_url=help_url or self.help_url)


class AegisDeniedError(AegisError):
    """Raised when a governance proposal is denied.

    Attributes:
        reason:     Why the action was denied.
        policy_ids: List of policy IDs that caused the denial.
    """

    help_url: str = f"{_DOCS_BASE}#denied-error"

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
