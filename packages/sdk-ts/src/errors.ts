/**
 * AEGIS SDK error hierarchy.
 *
 * Every error carries a structured `code` (shared with the Python SDK --
 * see `../sdk-py/aegis_sdk/errors.py` and `docs/errors.md` for the full
 * taxonomy) and a `helpUrl` pointing to the matching section of that
 * taxonomy doc on aegis-docs.com.
 */

const DOCS_BASE = 'https://aegis-docs.com/sdk/errors';

/**
 * Base error for all AEGIS SDK errors.
 *
 * Extends the native `Error` with a structured `code` and `helpUrl`.
 */
export class AegisError extends Error {
  /** Structured error code, shared with the Python SDK. */
  public readonly code: string;
  /** Link to the relevant section of the error taxonomy doc. */
  public readonly helpUrl: string;

  constructor(message: string, code = 'AEGIS_SDK_GENERAL_001', helpUrl?: string) {
    super(`[${code}] ${message}`);
    this.name = 'AegisError';
    this.code = code;
    this.helpUrl = helpUrl ?? `${DOCS_BASE}#${code.toLowerCase()}`;
    // Restore prototype chain — required when extending built-ins in TS
    Object.setPrototypeOf(this, new.target.prototype);
  }
}

/**
 * Thrown when the SDK cannot reach the AEGIS platform API.
 *
 * Common causes: network issues, incorrect endpoint, DNS failure.
 */
export class AegisConnectionError extends AegisError {
  constructor(message: string) {
    super(message, 'AEGIS_SDK_CONN_001');
    this.name = 'AegisConnectionError';
  }
}

/**
 * Thrown when an action proposal is denied by the governance engine.
 *
 * Includes the denial reason and the policies that caused it. Not
 * currently thrown by `AegisClient.propose()` -- a DENY verdict is a
 * normal `GovernanceDecision` return value, not a thrown error (see
 * client.ts's propose() docstring). Kept for SDK consumers that want to
 * convert a DENY decision into a thrown error at their own call site.
 */
export class AegisDeniedError extends AegisError {
  /** Human-readable reason the action was denied. */
  public readonly reason: string;
  /** IDs of the policies that triggered the denial. */
  public readonly policyIds: string[];

  constructor(reason: string, policyIds: string[]) {
    super(`Action denied: ${reason}`, 'AEGIS_SDK_DENIED_001');
    this.name = 'AegisDeniedError';
    this.reason = reason;
    this.policyIds = policyIds;
  }
}

/**
 * Thrown when authentication fails (401 / 403).
 *
 * Common causes: missing API key, expired key, insufficient permissions.
 */
export class AegisAuthError extends AegisError {
  constructor(message: string) {
    super(message, 'AEGIS_SDK_AUTH_001');
    this.name = 'AegisAuthError';
  }
}
