import { createServer, type Server } from "node:http";
import { afterEach, describe, expect, it } from "vitest";

import { AegisAuthError, AegisClient, AegisConnectionError, AegisError, Verdict } from "../src/index.js";

// Mirrors the Python SDK's loopback test fixture (packages/sdk-py/tests/test_client.py)
// so both language clients are exercised against the same four-verdict contract.
const VERDICT_BY_CAPABILITY: Record<string, Verdict> = {
  "file:read": Verdict.ALLOW,
  "file:write": Verdict.DENY,
  "network:request": Verdict.ESCALATE,
  "secret:rotate": Verdict.REQUIRE_CONFIRMATION,
};

function startServer(
  handler: (req: import("node:http").IncomingMessage, res: import("node:http").ServerResponse) => void,
): Promise<{ server: Server; baseUrl: string }> {
  return new Promise((resolve) => {
    const server = createServer(handler);
    server.listen(0, "127.0.0.1", () => {
      const { port } = server.address() as { port: number };
      resolve({ server, baseUrl: `http://127.0.0.1:${port}` });
    });
  });
}

const ACTOR = { id: "agent-test", type: "ai-agent" };

function defaultHandler(
  req: import("node:http").IncomingMessage,
  res: import("node:http").ServerResponse,
) {
  if (req.url !== "/api/v1/governance/propose") {
    res.writeHead(404).end("not found");
    return;
  }
  if (req.headers.authorization !== "Bearer test-key") {
    res.writeHead(401).end("missing or invalid api key");
    return;
  }
  let body = "";
  req.on("data", (chunk) => (body += chunk));
  req.on("end", () => {
    const parsed = JSON.parse(body);
    if (JSON.stringify(parsed.actor) !== JSON.stringify(ACTOR)) {
      res.writeHead(400).end("missing or malformed actor");
      return;
    }
    const verdict = VERDICT_BY_CAPABILITY[parsed.capability] ?? Verdict.DENY;
    const payload = JSON.stringify({
      action_id: "act-123",
      decision: verdict,
      timestamp: "2026-06-16T00:00:00Z",
      reason: `policy decision for ${parsed.capability}`,
      policy_ids: ["POL-1", "POL-2"],
      risk_score: 0.0,
      audit_ref: "audit-456",
    });
    res.writeHead(200, { "Content-Type": "application/json" }).end(payload);
  });
}

describe("AegisClient.propose", () => {
  let server: Server | undefined;

  afterEach(() => {
    server?.close();
    server = undefined;
  });

  it.each(Object.entries(VERDICT_BY_CAPABILITY))(
    "returns %s as a normal decision for capability %s",
    async (capability, expected) => {
      const started = await startServer(defaultHandler);
      server = started.server;
      const client = new AegisClient({ baseUrl: started.baseUrl, apiKey: "test-key" });

      const decision = await client.propose({ actor: ACTOR, capability, resource: "/x", parameters: {} });

      expect(decision.decision).toBe(expected);
      expect(decision.actionId).toBe("act-123");
      expect(decision.policyIds).toEqual(["POL-1", "POL-2"]);
      expect(decision.auditRef).toBe("audit-456");
    },
  );

  it("returns DENY as a normal value, not a thrown error", async () => {
    const started = await startServer(defaultHandler);
    server = started.server;
    const client = new AegisClient({ baseUrl: started.baseUrl, apiKey: "test-key" });

    const decision = await client.propose({ actor: ACTOR, capability: "file:write", resource: "/x", parameters: {} });

    expect(decision.decision).toBe(Verdict.DENY);
  });

  it("throws AegisAuthError when no API key is supplied", async () => {
    const started = await startServer(defaultHandler);
    server = started.server;
    const client = new AegisClient({ baseUrl: started.baseUrl });

    await expect(
      client.propose({ actor: ACTOR, capability: "file:read", resource: "/x", parameters: {} }),
    ).rejects.toThrow(AegisAuthError);
  });

  it("throws AegisConnectionError when the endpoint is unreachable", async () => {
    // Port 1 is reserved and never listening -> connection refused.
    const client = new AegisClient({ baseUrl: "http://127.0.0.1:1", apiKey: "test-key" });

    await expect(
      client.propose({ actor: ACTOR, capability: "file:read", resource: "/x", parameters: {} }),
    ).rejects.toThrow(AegisConnectionError);
  });

  it("throws AegisError on a malformed response body", async () => {
    const started = await startServer((req, res) => {
      if (req.headers.authorization !== "Bearer test-key") {
        res.writeHead(401).end();
        return;
      }
      res.writeHead(200, { "Content-Type": "application/json" }).end(JSON.stringify({ not: "a decision" }));
    });
    server = started.server;
    const client = new AegisClient({ baseUrl: started.baseUrl, apiKey: "test-key" });

    await expect(
      client.propose({ actor: ACTOR, capability: "file:read", resource: "/x", parameters: {} }),
    ).rejects.toThrow(AegisError);
  });
});
