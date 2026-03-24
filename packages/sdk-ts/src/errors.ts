/**
 * AEGIS SDK error hierarchy.
 *
 * Every error includes a `helpUrl` pointing to the relevant
 * troubleshooting page on aegis-docs.com.
 */

const DOCS_BASE = 'https://aegis-docs.com/sdk/errors';

/**
 * Base error for all AEGIS SDK errors.
 *
 * Extends the native `Error` with a `helpUrl` for documentation.
 */
export class AegisError extends Error {
  /** Link to documentation about this error. */
  public readonly helpUrl: string;

  constructor(message: string, helpUrl?: string) {
    super(message);
    this.name = 'AegisError';
    this.helpUrl = helpUrl ?? `${DOCS_BASE}/general`;
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
    super(message, `${DOCS_BASE}/connection`);
    this.name = 'AegisConnectionError';
  }
}

/**
 * Thrown when an action proposal is denied by the governance engine.
 *
 * Includes the denial reason and the policies that caused it.
 */
export class AegisDeniedError extends AegisError {
  /** Human-readable reason the action was denied. */
  public readonly reason: string;
  /** IDs of the policies that triggered the denial. */
  public readonly policyIds: string[];

  constructor(reason: string, policyIds: string[]) {
    super(`Action denied: ${reason}`, `${DOCS_BASE}/denied`);
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
    super(message, `${DOCS_BASE}/auth`);
    this.name = 'AegisAuthError';
  }
}
