# CLAUDE.md — aegis-sdk

## Project

AEGIS client SDK — dual-language monorepo providing TypeScript/JavaScript and Python client libraries for the AEGIS
Governance Platform.

## Org Context

- GitHub Org: github.com/aegis-initiative
- IP Owner: Finnoybu IP LLC
- Parent Ecosystem: Finnoybu Holdings LLC
- Domain: aegis-platform.net

## This Repo's Role

aegis-sdk is the primary integration surface for developers building on top of AEGIS. It provides TypeScript/JavaScript
and Python client libraries that wrap the aegis-platform REST API. Published to npm as @aegis-initiative/sdk and to PyPI
as aegis-sdk. Documentation auto-published to aegis-docs.

## Repo Structure (Dual-Package Monorepo)

- /packages/sdk-ts — TypeScript/JavaScript SDK (@aegis-initiative/sdk on npm)
  - /src/client.ts — AegisClient class wrapping the platform REST API
  - /src/types.ts — Verdict enum, GovernanceDecision, ActionProposal types
  - /src/index.ts — Package entry point and re-exports
- /packages/sdk-py — Python SDK (aegis-sdk on PyPI)
  - /aegis_sdk/client.py — AegisClient class wrapping the platform REST API
  - /aegis_sdk/types.py — Verdict enum, GovernanceDecision, ActionProposal dataclasses
- /docs — SDK documentation plan and guides

## API Surface

Both SDKs expose an identical API surface wrapping the aegis-platform REST API:

- **AegisClient(baseUrl, apiKey?)** — Create a client pointing at an AEGIS Platform instance
- **client.propose(proposal) → GovernanceDecision** — Submit an ActionProposal and receive a governance decision

### The Four Governance Outcomes (Verdict)

Every governance evaluation returns exactly one of these verdicts, matching the decision schema in aegis-governance:

1. **ALLOW** — Action is permitted under current policy
2. **DENY** — Action is forbidden under current policy
3. **ESCALATE** — Action requires review by a higher authority
4. **REQUIRE_CONFIRMATION** — Action is permitted only after explicit human confirmation

### Core Types

- **ActionProposal** — Mirrors AGP ACTION_PROPOSE schema (capability, resource, parameters, traceId)
- **GovernanceDecision** — Mirrors AGP DECISION_RESPONSE schema (actionId, decision, reason, policyIds, timestamp)

## Related Repos

- aegis-platform — The REST API that this SDK wraps (POST /v1/governance/propose)
- aegis-core — The governance enforcement engine that evaluates proposals behind the platform API
- aegis-governance — Source of truth for AGP protocol schemas and type definitions
- aegis-docs — SDK reference docs published here
- aegis-ops — Publish pipeline for npm and PyPI releases

## Stack

- TypeScript SDK: TypeScript 5.7+, Node 20+, ESM, no runtime dependencies
- Python SDK: Python 3.11+, hatchling build system, no runtime dependencies

## Key Conventions

- Both SDKs maintain identical API surfaces and are versioned in sync
- All public methods must have JSDoc (TS) / docstrings (Python) + type signatures
- Types mirror the JSON schemas defined in aegis-governance
- Branch: main is protected; all changes via PR with 1 required review
- Commit style: conventional commits (feat:, docs:, chore:, fix:)

## Current Focus

Initial scaffold complete — TypeScript and Python package structure with stub implementations. Next: implement HTTP
client when aegis-platform API is available.
