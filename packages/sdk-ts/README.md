# @aegis-initiative/sdk

TypeScript/JavaScript client SDK for the AEGIS Governance Platform.

## Installation

```bash
npm install @aegis-initiative/sdk
```

## Usage

```ts
import { ActionProposal, AegisClient, Verdict } from "@aegis-initiative/sdk";

const client = new AegisClient({
  baseUrl: "https://demo.aegis-platform.net",
  apiKey: "your-session-token",
});

const decision = await client.propose({
  actor: { id: "agent-soc-001", type: "ai-agent" },
  capability: "file.write",
  resource: "/etc/config",
  parameters: { content: "new config" },
});

if (decision.decision === Verdict.ALLOW) {
  // proceed with the action
} else if (decision.decision === Verdict.DENY) {
  console.log(`Denied: ${decision.reason}`); // a normal return value, not a thrown error
}
```

See [`examples/typescript/`](../../examples/typescript/) for five complete, runnable scripts covering every governance outcome, capability checking, and audit log querying.

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
- `listCapabilities(): Promise<Capability[]>` — List registered capabilities
- `getAuditEvents(options?: { agentId?: string; decision?: string; limit?: number }): Promise<AuditEvent[]>` — Query the audit log

### Errors

`AegisError`, `AegisConnectionError`, `AegisAuthError`, `AegisDeniedError` — see [`docs/errors.md`](../../docs/errors.md) for the full error code taxonomy (shared with the Python SDK).

## Status

Implemented and tested against the live AEGIS Platform API (`aegis-platform`). See that repo for the governance engine this client talks to.
