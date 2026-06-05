# CLAUDE.md — aegis-sdk

## Identity

You maintain **aegis-sdk** — the AEGIS client SDK, a dual-language monorepo providing TypeScript/JavaScript
and Python client libraries for the AEGIS Governance Platform. This repo is the primary integration surface
for developers building on top of AEGIS: it provides client libraries that wrap the aegis-platform REST API,
published to npm as `@aegis-initiative/sdk` and to PyPI as `aegis-sdk`. SDK reference documentation is
auto-published to aegis-docs.

## Repository catalog

- `packages/sdk-ts/` — TypeScript/JavaScript SDK (`@aegis-initiative/sdk` on npm)
  - `src/client.ts` — `AegisClient` class wrapping the platform REST API
  - `src/types.ts` — `Verdict` enum, `GovernanceDecision`, `ActionProposal` types
  - `src/errors.ts` — SDK error types
  - `src/index.ts` — package entry point and re-exports
- `packages/sdk-py/` — Python SDK (`aegis-sdk` on PyPI)
  - `aegis_sdk/client.py` — `AegisClient` class wrapping the platform REST API
  - `aegis_sdk/types.py` — `Verdict` enum, `GovernanceDecision`, `ActionProposal` dataclasses
  - `aegis_sdk/errors.py` — SDK error types
  - `aegis_sdk/py.typed` — PEP 561 typing marker
  - `tests/` — Python test suite
- `docs/` — SDK documentation plan and guides

### API surface

Both SDKs expose an identical API surface wrapping the aegis-platform REST API:

- **`AegisClient(baseUrl, apiKey?)`** — create a client pointing at an AEGIS Platform instance
- **`client.propose(proposal) → GovernanceDecision`** — submit an `ActionProposal` and receive a governance
  decision

#### The four governance outcomes (Verdict)

Every governance evaluation returns exactly one of these verdicts, matching the canonical decision schema in
`aegis`:

1. **ALLOW** — action is permitted under current policy
2. **DENY** — action is forbidden under current policy
3. **ESCALATE** — action requires review by a higher authority
4. **REQUIRE_CONFIRMATION** — action is permitted only after explicit human confirmation

#### Core types

- **`ActionProposal`** — mirrors AGP `ACTION_PROPOSE` schema (capability, resource, parameters, traceId)
- **`GovernanceDecision`** — mirrors AGP `DECISION_RESPONSE` schema (actionId, decision, reason, policyIds,
  timestamp)

## Data registry

- **Shared AGP schemas (canonical source)**: `aegis` — SDK types mirror these JSON schemas
- **Governance decision schema**: the four-verdict `Verdict` enum and core types are kept in sync with `aegis`

## Publication registry

- **npm (TypeScript)**: [`@aegis-initiative/sdk`](https://www.npmjs.com/package/@aegis-initiative/sdk)
- **PyPI (Python)**: [`aegis-sdk`](https://pypi.org/project/aegis-sdk/)
- **Publish pipeline**: managed in `aegis-ops` (npm + PyPI releases)
- **Reference docs**: auto-published to aegis-docs

## People & contacts

- **Primary maintainer**: Ken (sole maintainer during pre-ratification)
- **Reviewer routing**: `.github/CODEOWNERS`

## Identifier registry

- **GitHub Org**: [github.com/aegis-initiative](https://github.com/aegis-initiative)
- **Operating Entity**: AEGIS Initiative
- **Trademark Owner**: AEGIS Initiative (public attribution rule — internal IP-holder context lives in the
  workspace CLAUDE.md, never in public repo content)
- **Platform Domain**: aegis-platform.net (the REST API this SDK wraps)
- **npm package**: `@aegis-initiative/sdk`
- **PyPI package**: `aegis-sdk`
- **Package versions**: TS + Python released in sync (current v0.0.1)
- **License**: Apache-2.0 (full dual-license matrix in the workspace CLAUDE.md)

## Cross-repo pointers

- **aegis-platform** — the REST API this SDK wraps (`POST /v1/governance/propose`)
- **aegis-core** — the governance enforcement engine that evaluates proposals behind the platform API
- **aegis** — canonical source of shared AGP schemas and type definitions
- **aegis-docs** — SDK reference docs published here
- **aegis-ops** — publish pipeline for npm and PyPI releases

Ecosystem-wide structure and the full specialist-role matrix live in the workspace-level CLAUDE.md
(`d:/dev/AEGIS Initiative/CLAUDE.md`), inherited automatically — not duplicated here.

## Responsibilities

- Maintain identical API surfaces across the TypeScript and Python SDKs, versioned in sync
- Keep SDK types mirrored to the canonical JSON schemas defined in `aegis`
- Ensure all public methods carry JSDoc (TS) / docstrings (Python) plus type signatures
- Coordinate npm + PyPI releases through the `aegis-ops` publish pipeline

## Conventions specific to this repo

- **Stack**:
  - TypeScript SDK: TypeScript 5.7+, Node 20+, ESM, no runtime dependencies
  - Python SDK: Python 3.11+, hatchling build system, no runtime dependencies
- Both SDKs maintain identical API surfaces and are versioned in sync
- All public methods must have JSDoc (TS) / docstrings (Python) plus type signatures
- Types mirror the canonical JSON schemas defined in `aegis`
- Branch: `main` protected, all changes via PR with 1 required review; conventional commits
  (`feat:`, `docs:`, `chore:`, `fix:`)

## Live state pointers

- **Active issues**: `gh issue list --repo aegis-initiative/aegis-sdk`
- **Recent activity**: `git log --since='14 days ago'`
- **Current state**: initial scaffold complete — TypeScript and Python package structure with stub
  implementations. Next: implement the HTTP client when the aegis-platform API is available.

## Addendum files

None yet. Create under `.claude/` when needed (e.g. `GOTCHAS.md`, `CONTACTS.md`).
