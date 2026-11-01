# AEGIS SDK Error Taxonomy

Every error raised by either SDK client (Python, TypeScript) carries a structured `code` from
this shared namespace, plus a `help_url` (Python) / `helpUrl` (TypeScript) pointing back to the
matching section below. Both languages use identical codes for identical conditions, so a code
seen in a Python traceback and a code seen in a browser console mean the same thing.

| Code | Class | Thrown when |
|---|---|---|
| `AEGIS_SDK_GENERAL_001` | `AegisError` | Base class; also used directly for an API error status or a malformed response body that doesn't fit a more specific category below |
| `AEGIS_SDK_CONN_001` | `AegisConnectionError` | The SDK could not reach the AEGIS platform API — wrong endpoint URL, network failure, DNS failure, timeout, or the platform service is down |
| `AEGIS_SDK_AUTH_001` | `AegisAuthError` | Authentication failed (HTTP 401/403) — missing API key, expired key, or insufficient permissions |
| `AEGIS_SDK_DENIED_001` | `AegisDeniedError` | A governance proposal was denied. **Not currently thrown by `AegisClient.propose()`** — a DENY verdict is a normal `GovernanceDecision` return value in both SDKs, not an exception. This class exists for SDK consumers who want to convert a DENY decision into a thrown error at their own call site. |

## `AEGIS_SDK_GENERAL_001` {#aegis_sdk_general_001}

Raised for two distinct situations that don't warrant their own code yet:

- The governance API responded with a non-2xx, non-401/403 status (e.g. a 500, or a 400 from a
  malformed proposal). The error message includes the HTTP status and the first 500 characters
  of the response body.
- The response body couldn't be parsed into a `GovernanceDecision` — missing required fields
  (`action_id`/`decision`/`timestamp`), or an unrecognized `decision` value.

**Resolution**: check the included status code and response detail. A 400 almost always means
the proposal body is malformed (e.g. a missing `actor`, or `resource` with zero length) --
inspect the request against the `ActionProposal` type and the platform's `ProposeRequest` model.

## `AEGIS_SDK_CONN_001` {#aegis_sdk_conn_001}

Raised when the HTTP request itself fails before a response is received: DNS failure, refused
connection, or a timeout (either establishing the connection or mid-transfer).

**Resolution**: verify `base_url`/`baseUrl` is correct and reachable, and that the platform
service is running. If this fires intermittently under load, consider increasing the client's
timeout.

## `AEGIS_SDK_AUTH_001` {#aegis_sdk_auth_001}

Raised when the platform responds with HTTP 401 or 403.

**Resolution**: confirm `api_key`/`apiKey` is set and current. aegis-platform's public demo
treats this as a per-visitor sandbox token (see its own docs), not a long-lived credential -- an
expired or missing token is the most common cause here.

## `AEGIS_SDK_DENIED_001` {#aegis_sdk_denied_001}

Not thrown by the SDK itself today. Both `AegisClient.propose()` implementations return all four
governance verdicts (`ALLOW`, `DENY`, `ESCALATE`, `REQUIRE_CONFIRMATION`) as a normal
`GovernanceDecision`, matching the AGP contract's own design: a denial is an expected, valid
outcome of evaluation, not a failure of the call itself.

`AegisDeniedError` is exported from both SDKs for callers who prefer exceptions for control flow
-- e.g. `if decision.decision is Verdict.DENY: raise AegisDeniedError(decision.reason, decision.policy_ids)`
at the call site, rather than branching on the verdict inline.
