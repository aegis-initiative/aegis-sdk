/**
 * AEGIS governance client.
 *
 * Uses the native `fetch()` API available in Node 18+ — zero runtime
 * dependencies.
 *
 * @example
 * ```ts
 * import { AegisClient } from '@aegis-initiative/sdk';
 *
 * const client = new AegisClient({
 *   endpoint: 'https://api.aegissystems.live',
 *   apiKey: 'ak_live_...',
 * });
 *
 * const decision = await client.propose({
 *   actor: { id: 'agent-001', type: 'ai-agent' },
 *   action: { capability: 'database.query', parameters: { query: '...' } },
 * });
 * ```
 */

import type { ActionProposal, AegisClientOptions, GovernanceDecision } from './types.js';
import { Verdict } from './types.js';
import { AegisAuthError, AegisConnectionError, AegisDeniedError, AegisError } from './errors.js';

export class AegisClient {
  private readonly endpoint: string;
  private readonly apiKey?: string;

  /**
   * Create a new AEGIS client.
   *
   * @param options - Client configuration.
   * @param options.endpoint - Base URL of the AEGIS platform API.
   * @param options.apiKey - Optional API key for authenticated requests.
   */
  constructor(options: AegisClientOptions) {
    if (!options.endpoint) {
      throw new AegisError('endpoint is required');
    }
    // Strip trailing slash for consistent URL construction
    this.endpoint = options.endpoint.replace(/\/+$/, '');
    this.apiKey = options.apiKey;
  }

  /**
   * Submit an action proposal to the AEGIS governance engine.
   *
   * @param proposal - The action proposal to evaluate.
   * @returns The governance decision.
   * @throws {AegisConnectionError} If the API is unreachable.
   * @throws {AegisAuthError} If authentication fails.
   * @throws {AegisDeniedError} If the action is denied.
   * @throws {AegisError} For other API errors.
   */
  async propose(proposal: ActionProposal): Promise<GovernanceDecision> {
    const response = await this.request<GovernanceDecision>(
      '/api/v1/governance/propose',
      {
        method: 'POST',
        body: JSON.stringify(proposal),
      },
    );

    if (response.verdict === Verdict.DENY) {
      throw new AegisDeniedError(response.reason, response.policyIds);
    }

    return response;
  }

  /**
   * Check the health of the AEGIS platform API.
   *
   * @returns An object with a `status` field (e.g. `"ok"`).
   * @throws {AegisConnectionError} If the API is unreachable.
   */
  async health(): Promise<{ status: string }> {
    return this.request<{ status: string }>('/api/v1/health', {
      method: 'GET',
    });
  }

  // -----------------------------------------------------------
  // Internal helpers
  // -----------------------------------------------------------

  /** Build default headers, including auth when configured. */
  private buildHeaders(): Record<string, string> {
    const headers: Record<string, string> = {
      'Content-Type': 'application/json',
      Accept: 'application/json',
    };

    if (this.apiKey) {
      headers['Authorization'] = `Bearer ${this.apiKey}`;
    }

    return headers;
  }

  /**
   * Execute an HTTP request and return the parsed JSON body.
   *
   * Maps HTTP-level failures to the appropriate AEGIS error class.
   */
  private async request<T>(path: string, init: RequestInit): Promise<T> {
    const url = `${this.endpoint}${path}`;

    let response: Response;
    try {
      response = await fetch(url, {
        ...init,
        headers: {
          ...this.buildHeaders(),
          ...(init.headers as Record<string, string> | undefined),
        },
      });
    } catch (err: unknown) {
      const message =
        err instanceof Error ? err.message : 'Unknown network error';
      throw new AegisConnectionError(
        `Failed to connect to AEGIS API at ${url}: ${message}`,
      );
    }

    if (response.status === 401 || response.status === 403) {
      const body = await this.safeReadBody(response);
      throw new AegisAuthError(
        `Authentication failed (HTTP ${response.status}): ${body}`,
      );
    }

    if (!response.ok) {
      const body = await this.safeReadBody(response);
      throw new AegisError(
        `AEGIS API request failed (HTTP ${response.status}): ${body}`,
      );
    }

    return (await response.json()) as T;
  }

  /** Read the response body as text, returning a fallback on failure. */
  private async safeReadBody(response: Response): Promise<string> {
    try {
      return await response.text();
    } catch {
      return '<unable to read response body>';
    }
  }
}
