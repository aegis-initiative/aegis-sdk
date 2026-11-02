# aegis-sdk (Python)

Python client SDK for the AEGIS Governance Platform.

## Installation

```bash
pip install aegis-initiative-sdk
```

```python
from aegis_sdk import (
    AegisClient,
)  # the import name is aegis_sdk, not the PyPI package name
```

## Usage

```python
import asyncio

from aegis_sdk import ActionProposal, AegisClient, Actor, Verdict


async def main():
    client = AegisClient(
        base_url="https://demo.aegis-platform.net", api_key="your-session-token"
    )

    decision = await client.propose(
        ActionProposal(
            actor=Actor(id="agent-soc-001", type="ai-agent"),
            capability="file.write",
            resource="/etc/config",
            parameters={"content": "new config"},
        )
    )

    if decision.decision is Verdict.ALLOW:
        ...  # proceed with the action
    elif decision.decision is Verdict.DENY:
        print(
            f"Denied: {decision.reason}"
        )  # a normal return value, not a raised exception


asyncio.run(main())
```

See [`examples/python/`](../../examples/python/) for five complete, runnable scripts covering every governance outcome, capability checking, and audit log querying.

## Governance Outcomes

Every proposal returns one of four verdicts:

| Verdict | Meaning |
| --- | --- |
| `ALLOW` | Action is permitted under current policy |
| `DENY` | Action is forbidden under current policy |
| `ESCALATE` | Action requires review by a higher authority |
| `REQUIRE_CONFIRMATION` | Action is permitted only after explicit human confirmation |

## API

### `AegisClient`

- `AegisClient(*, base_url: str, api_key: str | None = None)` — Create a client
- `await client.propose(proposal: ActionProposal) -> GovernanceDecision` — Submit an action proposal
- `await client.list_capabilities() -> list[Capability]` — List registered capabilities
- `await client.get_audit_events(*, agent_id=None, decision=None, limit=50) -> list[AuditEvent]` — Query the audit log

### Errors

`AegisError`, `AegisConnectionError`, `AegisAuthError`, `AegisDeniedError` — see [`docs/errors.md`](../../docs/errors.md) for the full error code taxonomy (shared with the TypeScript SDK).

## Status

Implemented and tested against the live AEGIS Platform API (`aegis-platform`). See that repo for the governance engine this client talks to.
