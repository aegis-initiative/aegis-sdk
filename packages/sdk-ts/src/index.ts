export { AegisClient, type AegisClientOptions, type GetAuditEventsOptions } from "./client.js";
export {
  Verdict,
  type GovernanceDecision,
  type ActionProposal,
  type Actor,
  type Capability,
  type AuditEvent,
} from "./types.js";
export {
  AegisError,
  AegisConnectionError,
  AegisAuthError,
  AegisDeniedError,
} from "./errors.js";
