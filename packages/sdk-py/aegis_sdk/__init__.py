"""AEGIS SDK — Python client for the AEGIS Governance Platform."""

__version__ = "0.0.1"

from aegis_sdk.client import AegisClient
from aegis_sdk.types import ActionProposal, GovernanceDecision, Verdict

__all__ = [
    "AegisClient",
    "ActionProposal",
    "GovernanceDecision",
    "Verdict",
]
