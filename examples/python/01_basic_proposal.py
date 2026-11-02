"""Example 1: Basic proposal submission.

Submits an ACTION_PROPOSE for a file read that the demo-agent identity is
actually granted -- the governance engine evaluates it and returns ALLOW.

Run: python 01_basic_proposal.py
"""

import asyncio
import os

from aegis_sdk import ActionProposal, AegisClient, Actor


async def main() -> None:
    # Any string works as the api_key -- the public demo treats it as an
    # opaque per-visitor sandbox token, not a real credential, so this
    # just gets you your own isolated sandbox session.
    client = AegisClient(base_url=os.environ.get("AEGIS_SDK_EXAMPLE_BASE_URL", "https://demo.aegis-platform.net"), api_key="example-01")

    decision = await client.propose(
        ActionProposal(
            actor=Actor(id="demo-agent", type="ai-agent"),
            capability="file.read",
            resource="/home/documents/report.txt",
        )
    )

    print(f"Decision: {decision.decision.value}")
    print(f"Reason:   {decision.reason}")
    print(f"Risk score: {decision.risk_score}")
    print(f"Audit ref:  {decision.audit_ref}")
    assert decision.decision.value == "ALLOW", (
        "demo-agent is granted cap-file-read-docs for /home/documents/*, "
        "so this should always ALLOW against the current demo configuration"
    )


if __name__ == "__main__":
    asyncio.run(main())
