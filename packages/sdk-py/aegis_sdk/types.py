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
class Actor:
    """The actor submitting an action proposal.

    Mirrors the canonical AGP actor schema defined in `aegis`:
    https://aegis-initiative.com/schemas/common/actor.schema.json

    Note: the canonical schema constrains ``type`` to "agent" | "user" |
    "service", but aegis-platform's deployed API accepts an open string
    (e.g. "ai-agent", "ai-copilot", "automation", "human") and does not
    enforce the narrower canonical enum, so this type does not either.
    """

    id: str
    """Unique actor identifier. The canonical schema's own example uses a
    colon ('agent:soc-001'), but aegis_core's actual validation
    (AEGIS-VAL-004) only allows alphanumeric characters, hyphens,
    underscores, and dots -- e.g. 'agent-soc-001'."""

    type: str
    """Actor type, e.g. 'ai-agent', 'ai-copilot', 'automation', 'human'."""


@dataclass(frozen=True)
class ActionProposal:
    """An action proposal submitted to the governance engine for evaluation.

    Mirrors the canonical AGP ACTION_PROPOSE schema defined in `aegis`:
    https://aegis-initiative.com/schemas/agp/action_propose.schema.json
    """

    actor: Actor
    """The actor requesting the action."""

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

    action_id/decision/reason/policy_ids/timestamp mirror the canonical AGP
    DECISION_RESPONSE schema defined in `aegis`:
    https://aegis-initiative.com/schemas/agp/decision_response.schema.json

    risk_score and audit_ref are aegis-platform extensions beyond the
    canonical schema, included here because the platform always sends
    them; policy_ids is currently always empty since the runtime has no
    per-decision policy-attribution field yet.
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

    risk_score: float | None = None
    """Computed risk score (0.0-1.0) -- aegis-platform extension."""

    audit_ref: str | None = None
    """Reference to the full audit trail entry -- aegis-platform extension."""
