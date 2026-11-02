"""AEGIS SDK — Python client for the AEGIS Governance Platform."""

__version__ = "0.1.1"

from aegis_sdk.client import AegisClient
from aegis_sdk.types import (
    ActionProposal,
    Actor,
    AuditEvent,
    Capability,
    GovernanceDecision,
    Verdict,
)

__all__ = [
    "AegisClient",
    "Actor",
    "ActionProposal",
    "AuditEvent",
    "Capability",
    "GovernanceDecision",
    "Verdict",
]
