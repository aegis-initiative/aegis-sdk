/**
 * @aegis-initiative/sdk — TypeScript client for the AEGIS governance platform.
 *
 * @packageDocumentation
 */

export { AegisClient } from './client.js';

export {
  Verdict,
  type Actor,
  type Action,
  type ActionProposal,
  type GovernanceDecision,
  type AegisClientOptions,
} from './types.js';

export {
  AegisError,
  AegisConnectionError,
  AegisDeniedError,
  AegisAuthError,
} from './errors.js';
