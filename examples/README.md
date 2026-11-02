# AEGIS SDK Examples

Five runnable, self-contained flows, in both languages, against the live public demo at
`https://demo.aegis-platform.net`:

| # | Flow | Python | TypeScript |
|---|------|--------|------------|
| 1 | Basic proposal submission (ALLOW) | [`python/01_basic_proposal.py`](python/01_basic_proposal.py) | [`typescript/01-basic-proposal.ts`](typescript/01-basic-proposal.ts) |
| 2 | Handling a denial response (DENY) | [`python/02_handling_denial.py`](python/02_handling_denial.py) | [`typescript/02-handling-denial.ts`](typescript/02-handling-denial.ts) |
| 3 | Escalation flow (ESCALATE) | [`python/03_escalation_flow.py`](python/03_escalation_flow.py) | [`typescript/03-escalation-flow.ts`](typescript/03-escalation-flow.ts) |
| 4 | Capability checking | [`python/04_capability_checking.py`](python/04_capability_checking.py) | [`typescript/04-capability-checking.ts`](typescript/04-capability-checking.ts) |
| 5 | Audit log querying | [`python/05_audit_log_querying.py`](python/05_audit_log_querying.py) | [`typescript/05-audit-log-querying.ts`](typescript/05-audit-log-querying.ts) |

All five use the demo's built-in `demo-agent` identity, which the public sandbox pre-configures
with exactly the capabilities and policies needed to produce each of these outcomes for real --
see `services/platform-api/main.py`'s `_build_runtime()` in `aegis-platform` for the scenario
these examples walk through. No account or API key is required: the `Authorization: Bearer
<token>` header is just an opaque per-visitor sandbox identifier, not a credential, so any
string works to get your own isolated sandbox session.

## Neither SDK is published yet

`@aegis-initiative/sdk` and `aegis-sdk` (this repo's Python package) are not yet published to
npm or PyPI (confirmed: the PyPI name `aegis-sdk` already belongs to an unrelated package --
this repo's Python package will need a different distribution name before it can publish, e.g.
`aegis-initiative-sdk`). Until then, these examples run against the local package source via a
relative path, not a real install. Once published, drop the relative-path step below and `pip
install`/`npm install` the real package instead.

## Running the Python examples

```bash
cd examples/python
pip install -r requirements.txt   # editable-installs the local packages/sdk-py
python 01_basic_proposal.py
python 02_handling_denial.py
python 03_escalation_flow.py
python 04_capability_checking.py
python 05_audit_log_querying.py
```

## Running the TypeScript examples

```bash
cd ../../packages/sdk-ts && npm install && npm run build   # the local package must be built first
cd ../../examples/typescript
npm install
npm run 01   # or: npx tsx 01-basic-proposal.ts
npm run 02
npm run 03
npm run 04
npm run 05
```
