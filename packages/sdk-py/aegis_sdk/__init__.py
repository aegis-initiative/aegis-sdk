"""AEGIS Python SDK — client library for the AEGIS governance platform."""

from .client import AegisClient
from .errors import AegisAuthError, AegisConnectionError, AegisDeniedError, AegisError
from .types import ActionProposal, GovernanceDecision, Verdict

__all__ = [
    "AegisClient",
    "AegisError",
    "AegisConnectionError",
    "AegisDeniedError",
    "AegisAuthError",
    "ActionProposal",
    "GovernanceDecision",
    "Verdict",
]

__version__ = "0.1.0"
