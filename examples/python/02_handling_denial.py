"""Example 2: Handling a denial response.

demo-agent is granted the file.write capability -- but a separate policy
denies all file writes outright. This is the scenario the demo is built to
teach: having a capability is necessary but not sufficient, since a policy
can still override it. A DENY verdict is a normal GovernanceDecision return
value, not a thrown/raised error -- it's an expected outcome of evaluation,
so there's no try/except needed to "catch" it.

Run: python 02_handling_denial.py
"""

import asyncio
import os

from aegis_sdk import ActionProposal, AegisClient, Actor, Verdict


async def main() -> None:
    client = AegisClient(base_url=os.environ.get("AEGIS_SDK_EXAMPLE_BASE_URL", "https://demo.aegis-platform.net"), api_key="example-02")

    decision = await client.propose(
        ActionProposal(
            actor=Actor(id="demo-agent", type="ai-agent"),
            capability="file.write",
            resource="/home/documents/report.txt",
        )
    )

    if decision.decision is Verdict.DENY:
        # This branch is where your application decides what to do next:
        # log it, surface it to a human, or just stop. Nothing exceptional
        # happened at the SDK layer -- the governance engine did its job.
        print(f"Denied: {decision.reason}")
        print(f"Audit ref for this denial: {decision.audit_ref}")
    else:
        print(f"Unexpected verdict: {decision.decision.value}")

    assert decision.decision is Verdict.DENY, (
        "pol-deny-file-write blocks all file writes regardless of "
        "capability grants, so this should always DENY"
    )


if __name__ == "__main__":
    asyncio.run(main())
