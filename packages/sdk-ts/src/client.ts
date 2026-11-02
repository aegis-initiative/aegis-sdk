import { AegisAuthError, AegisConnectionError, AegisError } from "./errors.js";
import {
  Verdict,
  type ActionProposal,
  type AuditEvent,
  type Capability,
  type GovernanceDecision,
} from "./types.js";

const PROPOSE_PATH = "/api/v1/governance/propose";
const CAPABILITIES_PATH = "/api/v1/capabilities";
const AUDIT_EVENTS_PATH = "/api/v1/audit/events";

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
    const data = await this.request("POST", PROPOSE_PATH, {
      actor: { id: proposal.actor.id, type: proposal.actor.type },
      capability: proposal.capability,
      resource: proposal.resource,
      parameters: proposal.parameters,
      ...(proposal.traceId !== undefined ? { trace_id: proposal.traceId } : {}),
    });

    try {
      if (
        typeof data.action_id !== "string" ||
        typeof data.decision !== "string" ||
        typeof data.timestamp !== "string"
      ) {
        throw new Error("missing required field(s) action_id/decision/timestamp");
      }
      if (!Object.values(Verdict).includes(data.decision as Verdict)) {
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

  /**
   * List all capabilities registered in the governance runtime.
   *
   * @returns Every capability visible to the caller's session (or the
   *   shared anonymous seed, if no API key is set)
   * @throws {AegisAuthError} Authentication failed (HTTP 401/403)
   * @throws {AegisConnectionError} The platform API could not be reached
   * @throws {AegisError} The API returned an error status or a malformed body
   */
  async listCapabilities(): Promise<Capability[]> {
    const data = await this.request("GET", CAPABILITIES_PATH);
    try {
      if (!Array.isArray(data.capabilities)) {
        throw new Error("missing required field capabilities");
      }
      return data.capabilities.map((c: Record<string, any>) => ({
        id: c.id,
        name: c.name,
        description: c.description,
        actionTypes: c.action_types,
        targetPatterns: c.target_patterns,
        platform: c.platform ?? "any",
      }));
    } catch (cause) {
      throw new AegisError(
        `malformed capabilities list in API response: ${(cause as Error).message}`,
      );
    }
  }

  /**
   * Query the unified audit log.
   *
   * Merges the governance-decision trail with the platform-layer CRUD
   * trail (Policy/Profile/Capability/EndpointPolicy changes);
   * `AuditEvent.source` discriminates which fields are populated. Records
   * are scoped to the caller's session.
   *
   * @param options.agentId - Filter to decisions made by this agent (governance entries only)
   * @param options.decision - Filter to this verdict, e.g. "DENY" (governance entries only)
   * @param options.limit - Maximum number of records to return (1-200, default 50)
   * @returns Matching audit events, most recent first
   * @throws {AegisAuthError} Authentication failed (HTTP 401/403)
   * @throws {AegisConnectionError} The platform API could not be reached
   * @throws {AegisError} The API returned an error status or a malformed body
   */
  async getAuditEvents(options: GetAuditEventsOptions = {}): Promise<AuditEvent[]> {
    const params = new URLSearchParams();
    params.set("limit", String(options.limit ?? 50));
    if (options.agentId !== undefined) params.set("agent_id", options.agentId);
    if (options.decision !== undefined) params.set("decision", options.decision);

    const data = await this.request("GET", `${AUDIT_EVENTS_PATH}?${params}`);
    try {
      if (!Array.isArray(data.events)) {
        throw new Error("missing required field events");
      }
      return data.events.map((e: Record<string, any>) => ({
        id: e.id,
        timestamp: e.timestamp,
        source: e.source ?? "governance",
        sessionId: e.session_id ?? "",
        requestId: e.request_id,
        agentId: e.agent_id,
        actionType: e.action_type,
        actionTarget: e.action_target,
        decision: e.decision,
        reason: e.reason,
        eventType: e.event_type,
        resourceId: e.resource_id,
        summary: e.summary,
      }));
    } catch (cause) {
      throw new AegisError(
        `malformed audit events list in API response: ${(cause as Error).message}`,
      );
    }
  }

  /**
   * Issue one HTTP request and return its parsed JSON body.
   *
   * Shared by every endpoint method -- the response SHAPE (which fields
   * mean what) is endpoint-specific and parsed by the caller; this only
   * handles the request/transport/error-status concerns common to all of
   * them.
   */
  private async request(
    method: "GET" | "POST",
    path: string,
    body?: Record<string, unknown>,
  ): Promise<Record<string, any>> {
    const url = `${this.baseUrl.replace(/\/$/, "")}${path}`;
    const headers: Record<string, string> = { Accept: "application/json" };
    if (this.apiKey) {
      headers.Authorization = `Bearer ${this.apiKey}`;
    }
    if (body !== undefined) {
      headers["Content-Type"] = "application/json";
    }

    let response: Response;
    try {
      response = await fetch(url, {
        method,
        headers,
        ...(body !== undefined ? { body: JSON.stringify(body) } : {}),
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

    const raw = await response.text();
    try {
      return JSON.parse(raw);
    } catch (cause) {
      throw new AegisError(`malformed JSON in API response: ${(cause as Error).message}`);
    }
  }
}

export interface AegisClientOptions {
  /** Base URL of the AEGIS Platform API */
  baseUrl: string;
  /** Optional API key for authentication */
  apiKey?: string;
}

export interface GetAuditEventsOptions {
  /** Filter to decisions made by this agent (governance entries only) */
  agentId?: string;
  /** Filter to this verdict, e.g. "DENY" (governance entries only) */
  decision?: string;
  /** Maximum number of records to return (1-200, default 50) */
  limit?: number;
}
