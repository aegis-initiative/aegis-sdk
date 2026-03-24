/**
 * AEGIS SDK type definitions.
 *
 * These types mirror the aegis-platform governance API contracts
 * defined in the aegis repo's JSON Schema specifications.
 */

/** Governance verdict returned by the AEGIS platform. */
export enum Verdict {
  ALLOW = 'ALLOW',
  DENY = 'DENY',
  ESCALATE = 'ESCALATE',
  REQUIRE_CONFIRMATION = 'REQUIRE_CONFIRMATION',
}

/** Describes the actor initiating the action. */
export interface Actor {
  /** Unique identifier for the actor (e.g. "agent-001"). */
  id: string;
  /** The kind of actor (e.g. "ai-agent", "human", "service"). */
  type: string;
}

/** Describes the action being proposed for governance review. */
export interface Action {
  /** The capability being invoked (e.g. "database.query"). */
  capability: string;
  /** Arbitrary parameters for the action. */
  parameters?: Record<string, unknown>;
}

/** A proposal submitted to the governance engine for evaluation. */
export interface ActionProposal {
  /** The actor proposing the action. */
  actor: Actor;
  /** The action being proposed. */
  action: Action;
  /** Optional context passed to policy evaluation. */
  context?: Record<string, unknown>;
}

/** The governance decision returned by the AEGIS platform. */
export interface GovernanceDecision {
  /** The governance verdict. */
  verdict: Verdict;
  /** Human-readable explanation for the decision. */
  reason: string;
  /** IDs of the policies that influenced this decision. */
  policyIds: string[];
  /** Unique audit trail identifier for this decision. */
  auditId: string;
  /** ISO-8601 timestamp of the decision. */
  timestamp: string;
}

/** Configuration options for {@link AegisClient}. */
export interface AegisClientOptions {
  /** Base URL of the AEGIS platform API (e.g. "https://api.aegissystems.live"). */
  endpoint: string;
  /** Optional API key for authenticated requests. */
  apiKey?: string;
}
