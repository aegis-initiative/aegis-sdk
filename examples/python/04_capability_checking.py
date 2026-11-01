"""Example 4: Capability checking.

Lists every capability registered in the governance runtime and shows how
to use that list client-side: deciding whether a capability plausibly
covers a given action/target *before* spending a round trip on propose().
This is advisory only -- the governance engine (not this client-side
check) is the actual authority, since a policy can still deny an action
even when a capability nominally covers it (see example 2).

Run: python 04_capability_checking.py
"""

import asyncio
import fnmatch
import os

from aegis_sdk import AegisClient


def covers(capability, action_type: str, target: str) -> bool:
    """Client-side only -- mirrors the shape of the real check the
    governance engine performs, for UI/UX purposes (e.g. graying out an
    action before the user tries it), not as a substitute for propose().
    """
    return action_type in capability.action_types and any(
        fnmatch.fnmatch(target, pattern) for pattern in capability.target_patterns
    )


async def main() -> None:
    client = AegisClient(base_url=os.environ.get("AEGIS_SDK_EXAMPLE_BASE_URL", "https://demo.aegis-platform.net"), api_key="example-04")

    capabilities = await client.list_capabilities()
    print(f"{len(capabilities)} capabilities registered in this sandbox:\n")
    for cap in capabilities:
        print(f"  {cap.id}: {cap.name} ({cap.platform})")
        print(f"    action_types: {cap.action_types}")
        print(f"    target_patterns: {cap.target_patterns}")

    print()
    checks = [
        ("file_read", "/home/documents/report.txt"),
        ("file_read", "/etc/passwd"),
        ("data_access", "postgres://prod/customers"),
    ]
    for action_type, target in checks:
        matches = [c for c in capabilities if covers(c, action_type, target)]
        verdict = f"covered by {matches[0].name}" if matches else "no capability covers this"
        print(f"{action_type} on {target}: {verdict}")


if __name__ == "__main__":
    asyncio.run(main())
