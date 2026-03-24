"""AEGIS Governance Platform client."""

from __future__ import annotations

from aegis_sdk.types import ActionProposal, GovernanceDecision


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
        REQUIRE_CONFIRMATION.

        Args:
            proposal: The action proposal to evaluate.

        Returns:
            A governance decision with verdict, reason, and policy IDs.

        Raises:
            NotImplementedError: Until the aegis-platform API is available.
        """
        # TODO: Implement HTTP call to aegis-platform API
        # POST /v1/governance/propose
        raise NotImplementedError("Not yet implemented — awaiting aegis-platform API")