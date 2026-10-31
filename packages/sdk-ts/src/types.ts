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
 * The actor submitting an action proposal.
 *
 * Mirrors the canonical AGP actor schema defined in aegis-governance:
 * https://aegis-initiative.com/schemas/common/actor.schema.json
 *
 * Note: the canonical schema constrains `type` to "agent" | "user" |
 * "service", but aegis-platform's deployed API accepts an open string
 * (e.g. "ai-agent", "ai-copilot", "automation", "human") and does not
 * enforce the narrower canonical enum, so this type does not either.
 */
export interface Actor {
  /**
   * Unique actor identifier. The canonical schema's own example uses a
   * colon ("agent:soc-001"), but aegis_core's actual validation
   * (AEGIS-VAL-004) only allows alphanumeric characters, hyphens,
   * underscores, and dots -- e.g. "agent-soc-001".
   */
  id: string;
  /** Actor type, e.g. "ai-agent", "ai-copilot", "automation", "human" */
  type: string;
}

/**
 * An action proposal submitted to the governance engine for evaluation.
 *
 * Mirrors the AGP ACTION_PROPOSE schema defined in aegis-governance:
 * https://aegis-initiative.com/schemas/agp/action_propose.schema.json
 */
export interface ActionProposal {
  /** The actor requesting the action */
  actor: Actor;
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
 * actionId/decision/reason/policyIds/timestamp mirror the AGP
 * DECISION_RESPONSE schema defined in aegis-governance:
 * https://aegis-initiative.com/schemas/agp/decision_response.schema.json
 *
 * riskScore and auditRef are aegis-platform extensions beyond the
 * canonical schema, included here because the platform always sends
 * them; policyIds is currently always empty since the runtime has no
 * per-decision policy-attribution field yet.
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
  /** Computed risk score (0.0-1.0) -- aegis-platform extension */
  riskScore?: number;
  /** Reference to the full audit trail entry -- aegis-platform extension */
  auditRef?: string;
  /** ISO 8601 timestamp of the decision */
  timestamp: string;
}
