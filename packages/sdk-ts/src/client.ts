import { AegisAuthError, AegisConnectionError, AegisError } from "./errors.js";
import { Verdict, type ActionProposal, type GovernanceDecision } from "./types.js";

const PROPOSE_PATH = "/api/v1/governance/propose";

/**
 * Client for the AEGIS Governance Platform API.
 *
 * Wraps the aegis-platform REST API to submit action proposals
 * and receive governance decisions.
 *
 * @example
 * ```ts
 * const client = new AegisClient({ baseUrl: "https://demo.aegis-platform.net" });
 * const decision = await client.propose({
 *   actor: { id: "agent-soc-001", type: "ai-agent" },
 *   capability: "file:write",
 *   resource: "/etc/config",
 *   parameters: { content: "..." },
 * });
 * ```
 */
export class AegisClient {
  private readonly baseUrl: string;
  private readonly apiKey?: string;

  constructor(options: AegisClientOptions) {
    this.baseUrl = options.baseUrl;
    this.apiKey = options.apiKey;
  }

  /**
   * Submit an action proposal to the AEGIS governance engine.
   *
   * The governance engine evaluates the proposal against active policies
   * and returns one of four verdicts: ALLOW, DENY, ESCALATE, or
   * REQUIRE_CONFIRMATION. All four come back as a `GovernanceDecision`; a
   * DENY verdict is a normal return, not a thrown error (mirrors the
   * Python SDK's contract).
   *
   * @param proposal - The action proposal to evaluate
   * @returns A governance decision with verdict, reason, and policy IDs
   * @throws {AegisAuthError} Authentication failed (HTTP 401/403)
   * @throws {AegisConnectionError} The platform API could not be reached
   * @throws {AegisError} The API returned an error status or a malformed body
   */
  async propose(proposal: ActionProposal): Promise<GovernanceDecision> {
    const url = `${this.baseUrl.replace(/\/$/, "")}${PROPOSE_PATH}`;
    const headers: Record<string, string> = {
      "Content-Type": "application/json",
      Accept: "application/json",
    };
    if (this.apiKey) {
      headers.Authorization = `Bearer ${this.apiKey}`;
    }

    let response: Response;
    try {
      response = await fetch(url, {
        method: "POST",
        headers,
        body: JSON.stringify({
          actor: { id: proposal.actor.id, type: proposal.actor.type },
          capability: proposal.capability,
          resource: proposal.resource,
          parameters: proposal.parameters,
          ...(proposal.traceId !== undefined ? { trace_id: proposal.traceId } : {}),
        }),
      });
    } catch (cause) {
      throw new AegisConnectionError(
        `could not reach AEGIS platform at ${this.baseUrl}: ${(cause as Error).message}`,
      );
    }

    if (response.status === 401 || response.status === 403) {
      throw new AegisAuthError(`authentication failed (HTTP ${response.status})`);
    }
    if (!response.ok) {
      const detail = (await response.text().catch(() => "")).slice(0, 500);
      throw new AegisError(
        `governance API returned HTTP ${response.status}: ${response.statusText}. ${detail}`.trim(),
      );
    }

    return this.parseDecision(await response.text());
  }

  private parseDecision(raw: string): GovernanceDecision {
    try {
      const data = JSON.parse(raw);
      if (
        typeof data.action_id !== "string" ||
        typeof data.decision !== "string" ||
        typeof data.timestamp !== "string"
      ) {
        throw new Error("missing required field(s) action_id/decision/timestamp");
      }
      if (!Object.values(Verdict).includes(data.decision)) {
        throw new Error(`unknown decision verdict: ${data.decision}`);
      }
      return {
        actionId: data.action_id,
        decision: data.decision as Verdict,
        timestamp: data.timestamp,
        reason: data.reason,
        policyIds: data.policy_ids ?? [],
        riskScore: data.risk_score,
        auditRef: data.audit_ref,
      };
    } catch (cause) {
      throw new AegisError(
        `malformed governance decision in API response: ${(cause as Error).message}`,
      );
    }
  }
}

export interface AegisClientOptions {
  /** Base URL of the AEGIS Platform API */
  baseUrl: string;
  /** Optional API key for authentication */
  apiKey?: string;
}