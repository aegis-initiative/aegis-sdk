"""Core data types returned by the AEGIS governance API."""

from __future__ import annotations

import enum
from dataclasses import dataclass, field
from datetime import datetime


class Verdict(enum.Enum):
    """Possible outcomes of a governance evaluation."""

    ALLOW = "ALLOW"
    DENY = "DENY"
    ESCALATE = "ESCALATE"
    REQUIRE_CONFIRMATION = "REQUIRE_CONFIRMATION"


@dataclass(frozen=True)
class ActionProposal:
    """A proposed action submitted for governance review.

    Attributes:
        capability: The capability being requested (e.g. ``"file.write"``).
        resource:   The target resource (e.g. ``"/etc/hosts"``).
        parameters: Optional additional parameters for the action.
    """

    capability: str
    resource: str
    parameters: dict | None = None


@dataclass(frozen=True)
class GovernanceDecision:
    """The platform's response to a governance proposal.

    Attributes:
        verdict:    The governance outcome.
        reason:     Human-readable explanation of the decision.
        policy_ids: IDs of the policies that contributed to this decision.
        audit_id:   Unique identifier for the audit trail entry.
        timestamp:  When the decision was made (ISO-8601).
    """

    verdict: Verdict
    reason: str
    policy_ids: list[str] = field(default_factory=list)
    audit_id: str = ""
    timestamp: str = ""
