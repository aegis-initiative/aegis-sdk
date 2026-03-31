# aegis-sdk (Python)

Python client SDK for the AEGIS Governance Platform.

## Installation

```bash
pip install aegis-sdk
```

## Usage

```python
from aegis_sdk import AegisClient, ActionProposal, Verdict

client = AegisClient(base_url="https://demo.aegis-platform.net")

decision = await client.propose(
    ActionProposal(
        capability="file:write",
        resource="/etc/config",
        parameters={"content": "new config"},
    )
)

if decision.decision == Verdict.ALLOW:
    # Proceed with the action
    ...
```

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

- `AegisClient(base_url: str, api_key: str | None = None)` — Create a client
- `await client.propose(proposal: ActionProposal) -> GovernanceDecision` — Submit an action proposal

## Status

Stub — not yet connected to aegis-platform. See [aegis-platform](https://github.com/aegis-initiative/aegis-platform) for
API development progress.
