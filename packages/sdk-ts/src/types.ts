/**
 * Governance verdict — the four possible outcomes of a governance evaluation.
 *
 * Matches the decision enum defined in aegis-governance:
 * https://aegis-initiative.com/schemas/common/decision.schema.json
 *
 * - ALLOW: Action is permitted under current policy
 * - DENY: Action is forbidden under current policy
 * - ESCALATE: Action requires review by a higher authority
 * - REQUIRE_CONFIRMATION: Action is permitted only after explicit human confirmation
 */
export enum Verdict {
  ALLOW = "ALLOW",
  DENY = "DENY",
  ESCALATE = "ESCALATE",
  REQUIRE_CONFIRMATION = "REQUIRE_CONFIRMATION",
}

/**
 * An action proposal submitted to the governance engine for evaluation.
 *
 * Mirrors the AGP ACTION_PROPOSE schema defined in aegis-governance:
 * https://aegis-initiative.com/schemas/agp/action_propose.schema.json
 */
export interface ActionProposal {
  /** The capability being invoked (e.g. "file:write", "network:request") */
  capability: string;
  /** The target resource for the action */
  resource: string;
  /** Action-specific parameters */
  parameters: Record<string, unknown>;
  /** Optional trace ID for request correlation */
  traceId?: string;
}

/**
 * A governance decision returned by the governance engine.
 *
 * Mirrors the AGP DECISION_RESPONSE schema defined in aegis-governance:
 * https://aegis-initiative.com/schemas/agp/decision_response.schema.json
 */
export interface GovernanceDecision {
  /** The unique ID of the evaluated action */
  actionId: string;
  /** The governance verdict */
  decision: Verdict;
  /** Human-readable explanation of the decision */
  reason?: string;
  /** IDs of the policies that influenced this decision */
  policyIds?: string[];
  /** ISO 8601 timestamp of the decision */
  timestamp: string;
}
