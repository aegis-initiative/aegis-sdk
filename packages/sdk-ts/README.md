# @aegis-initiative/sdk

TypeScript/JavaScript client SDK for the AEGIS Governance Platform.

## Installation

```bash
npm install @aegis-initiative/sdk
```

## Usage

```ts
import { AegisClient, Verdict } from "@aegis-initiative/sdk";

const client = new AegisClient({
  baseUrl: "https://demo.aegis-platform.net",
});

const decision = await client.propose({
  capability: "file:write",
  resource: "/etc/config",
  parameters: { content: "new config" },
});

if (decision.decision === Verdict.ALLOW) {
  // Proceed with the action
}
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

- `constructor(options: { baseUrl: string; apiKey?: string })` — Create a client
- `propose(proposal: ActionProposal): Promise<GovernanceDecision>` — Submit an action proposal

## Status

Stub — not yet connected to aegis-platform. See [aegis-platform](https://github.com/aegis-initiative/aegis-platform) for
API development progress.
