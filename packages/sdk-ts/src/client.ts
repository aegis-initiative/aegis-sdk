import type { ActionProposal, GovernanceDecision } from "./types";

/**
 * Client for the AEGIS Governance Platform API.
 *
 * Wraps the aegis-platform REST API to submit action proposals
 * and receive governance decisions.
 *
 * @example
 * ```ts
 * const client = new AegisClient({ baseUrl: "https://api.aegissystems.app" });
 * const decision = await client.propose({
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
   * REQUIRE_CONFIRMATION.
   *
   * @param proposal - The action proposal to evaluate
   * @returns A governance decision with verdict, reason, and policy IDs
   */
  async propose(proposal: ActionProposal): Promise<GovernanceDecision> {
    // TODO: Implement HTTP call to aegis-platform API
    // POST /v1/governance/propose
    throw new Error("Not yet implemented — awaiting aegis-platform API");
  }
}

export interface AegisClientOptions {
  /** Base URL of the AEGIS Platform API */
  baseUrl: string;
  /** Optional API key for authentication */
  apiKey?: string;
}
