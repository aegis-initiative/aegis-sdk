"""Type definitions for AEGIS governance outcomes.

All types mirror the canonical JSON schemas defined in `aegis`:
https://github.com/aegis-initiative/aegis/tree/main/schemas
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any


class Verdict(StrEnum):
    """Governance verdict — the four possible outcomes of a governance evaluation.

    Matches the canonical decision enum defined in `aegis`:
    https://aegis-initiative.com/schemas/common/decision.schema.json

    - ALLOW: Action is permitted under current policy
    - DENY: Action is forbidden under current policy
    - ESCALATE: Action requires review by a higher authority
    - REQUIRE_CONFIRMATION: Action is permitted only after explicit human confirmation
    """

    ALLOW = "ALLOW"
    DENY = "DENY"
    ESCALATE = "ESCALATE"
    REQUIRE_CONFIRMATION = "REQUIRE_CONFIRMATION"


@dataclass(frozen=True)
class ActionProposal:
    """An action proposal submitted to the governance engine for evaluation.

    Mirrors the canonical AGP ACTION_PROPOSE schema defined in `aegis`:
    https://aegis-initiative.com/schemas/agp/action_propose.schema.json
    """

    capability: str
    """The capability being invoked (e.g. 'file:write', 'network:request')."""

    resource: str
    """The target resource for the action."""

    parameters: dict[str, Any] = field(default_factory=dict)
    """Action-specific parameters."""

    trace_id: str | None = None
    """Optional trace ID for request correlation."""


@dataclass(frozen=True)
class GovernanceDecision:
    """A governance decision returned by the governance engine.

    Mirrors the canonical AGP DECISION_RESPONSE schema defined in `aegis`:
    https://aegis-initiative.com/schemas/agp/decision_response.schema.json
    """

    action_id: str
    """The unique ID of the evaluated action."""

    decision: Verdict
    """The governance verdict."""

    timestamp: str
    """ISO 8601 timestamp of the decision."""

    reason: str | None = None
    """Human-readable explanation of the decision."""

    policy_ids: list[str] = field(default_factory=list)
    """IDs of the policies that influenced this decision."""
