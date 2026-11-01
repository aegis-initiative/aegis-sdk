"""Example 5: Audit log querying.

Submits a couple of proposals (so there's something to query), then reads
the unified audit log back -- both unfiltered and filtered by agent_id /
decision. Every propose() call is automatically recorded; this is how you
retrieve that history rather than keeping your own copy.

Run: python 05_audit_log_querying.py
"""

import asyncio
import os

from aegis_sdk import ActionProposal, AegisClient, Actor


async def main() -> None:
    client = AegisClient(base_url=os.environ.get("AEGIS_SDK_EXAMPLE_BASE_URL", "https://demo.aegis-platform.net"), api_key="example-05")

    # Generate a couple of audit entries to query back.
    await client.propose(
        ActionProposal(
            actor=Actor(id="demo-agent", type="ai-agent"),
            capability="file.read",
            resource="/home/documents/report.txt",
        )
    )
    await client.propose(
        ActionProposal(
            actor=Actor(id="demo-agent", type="ai-agent"),
            capability="file.write",
            resource="/home/documents/report.txt",
        )
    )

    print("-- All recent events --")
    for event in await client.get_audit_events(limit=10):
        if event.source == "governance":
            print(f"  [{event.timestamp}] {event.agent_id}: {event.action_type} -> {event.decision}")
        else:
            print(f"  [{event.timestamp}] (platform) {event.event_type}: {event.summary}")

    print("\n-- Filtered to demo-agent only --")
    for event in await client.get_audit_events(agent_id="demo-agent", limit=10):
        print(f"  [{event.timestamp}] {event.action_type} -> {event.decision}")

    print("\n-- Filtered to DENY only --")
    for event in await client.get_audit_events(decision="DENY", limit=10):
        print(f"  [{event.timestamp}] {event.agent_id}: {event.action_type} -> {event.reason}")


if __name__ == "__main__":
    asyncio.run(main())
