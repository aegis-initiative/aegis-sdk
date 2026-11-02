"""Example 3: Escalation flow.

demo-agent is granted network.fetch for a short list of approved domains,
but a policy routes every network request to ESCALATE for review rather
than auto-allowing it -- even to an approved domain. ESCALATE means "don't
auto-allow, but don't auto-deny either": a human or a higher-authority
process needs to decide, and your application's job is to route that
decision somewhere (a queue, a notification, a dashboard), not to retry or
treat it as a failure.

Run: python 03_escalation_flow.py
"""

import asyncio
import os

from aegis_sdk import ActionProposal, AegisClient, Actor, Verdict


async def main() -> None:
    client = AegisClient(base_url=os.environ.get("AEGIS_SDK_EXAMPLE_BASE_URL", "https://demo.aegis-platform.net"), api_key="example-03")

    decision = await client.propose(
        ActionProposal(
            actor=Actor(id="demo-agent", type="ai-agent"),
            capability="network.fetch",
            resource="https://api.github.com/repos/aegis-initiative/aegis-core",
        )
    )

    if decision.decision is Verdict.ESCALATE:
        print(f"Needs review: {decision.reason}")
        print(f"Audit ref to attach to the review ticket: {decision.audit_ref}")
        # In a real integration, this is where you'd open a review item --
        # e.g. post decision.audit_ref to a queue or ticketing system and
        # wait for a human verdict before the agent proceeds.
    else:
        print(f"Unexpected verdict: {decision.decision.value}")

    assert decision.decision is Verdict.ESCALATE, (
        "pol-escalate-network routes every network.fetch to ESCALATE "
        "regardless of domain, so this should always ESCALATE"
    )


if __name__ == "__main__":
    asyncio.run(main())
