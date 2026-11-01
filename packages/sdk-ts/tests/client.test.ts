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

const CAPABILITIES = [
  {
    id: "cap-1",
    name: "file.read",
    description: "Read files",
    action_types: ["file_read"],
    target_patterns: ["/home/*"],
    platform: "linux",
  },
  {
    id: "cap-2",
    name: "file.write",
    description: "Write files",
    action_types: ["file_write"],
    target_patterns: ["*"],
    platform: "any",
  },
];

const AUDIT_EVENTS = [
  {
    id: "evt-1",
    timestamp: "2026-06-16T00:00:00Z",
    source: "governance",
    session_id: "sess-1",
    agent_id: "agent-test",
    action_type: "file_read",
    action_target: "/home/x",
    decision: "ALLOW",
    reason: "matched policy POL-1",
  },
  {
    id: "evt-2",
    timestamp: "2026-06-16T00:01:00Z",
    source: "platform",
    session_id: "sess-1",
    event_type: "capability.create",
    resource_id: "cap-2",
    summary: "Created capability 'file.write'",
  },
];

function defaultHandler(
  req: import("node:http").IncomingMessage,
  res: import("node:http").ServerResponse,
) {
  const url = new URL(req.url ?? "", "http://localhost");

  if (req.headers.authorization !== "Bearer test-key") {
    res.writeHead(401).end("missing or invalid api key");
    return;
  }

  if (req.method === "GET" && url.pathname === "/api/v1/capabilities") {
    res.writeHead(200, { "Content-Type": "application/json" }).end(
      JSON.stringify({ capabilities: CAPABILITIES, count: CAPABILITIES.length }),
    );
    return;
  }

  if (req.method === "GET" && url.pathname === "/api/v1/audit/events") {
    let events = AUDIT_EVENTS;
    const agentId = url.searchParams.get("agent_id");
    const decision = url.searchParams.get("decision");
    if (agentId) events = events.filter((e) => e.agent_id === agentId);
    if (decision) events = events.filter((e) => e.decision === decision);
    res.writeHead(200, { "Content-Type": "application/json" }).end(
      JSON.stringify({ events, count: events.length }),
    );
    return;
  }

  if (req.method === "POST" && url.pathname === "/api/v1/governance/propose") {
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
    return;
  }

  res.writeHead(404).end("not found");
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

describe("AegisClient.listCapabilities", () => {
  let server: Server | undefined;

  afterEach(() => {
    server?.close();
    server = undefined;
  });

  it("lists capabilities with their platform field", async () => {
    const started = await startServer(defaultHandler);
    server = started.server;
    const client = new AegisClient({ baseUrl: started.baseUrl, apiKey: "test-key" });

    const caps = await client.listCapabilities();

    expect(caps.map((c) => c.id)).toEqual(["cap-1", "cap-2"]);
    expect(caps[0].platform).toBe("linux");
    expect(caps[1].platform).toBe("any");
    expect(caps[0].actionTypes).toEqual(["file_read"]);
  });

  it("throws AegisAuthError when no API key is supplied", async () => {
    const started = await startServer(defaultHandler);
    server = started.server;
    const client = new AegisClient({ baseUrl: started.baseUrl });

    await expect(client.listCapabilities()).rejects.toThrow(AegisAuthError);
  });
});

describe("AegisClient.getAuditEvents", () => {
  let server: Server | undefined;

  afterEach(() => {
    server?.close();
    server = undefined;
  });

  it("returns both governance and platform entries unfiltered", async () => {
    const started = await startServer(defaultHandler);
    server = started.server;
    const client = new AegisClient({ baseUrl: started.baseUrl, apiKey: "test-key" });

    const events = await client.getAuditEvents();

    expect(events.map((e) => e.id)).toEqual(["evt-1", "evt-2"]);
    expect(events[0].source).toBe("governance");
    expect(events[0].decision).toBe("ALLOW");
    expect(events[1].source).toBe("platform");
    expect(events[1].summary).toBe("Created capability 'file.write'");
  });

  it("filters by agentId", async () => {
    const started = await startServer(defaultHandler);
    server = started.server;
    const client = new AegisClient({ baseUrl: started.baseUrl, apiKey: "test-key" });

    const events = await client.getAuditEvents({ agentId: "agent-test" });

    expect(events.map((e) => e.id)).toEqual(["evt-1"]);
  });

  it("filters by decision", async () => {
    const started = await startServer(defaultHandler);
    server = started.server;
    const client = new AegisClient({ baseUrl: started.baseUrl, apiKey: "test-key" });

    const events = await client.getAuditEvents({ decision: "ALLOW" });

    expect(events.map((e) => e.id)).toEqual(["evt-1"]);
  });
});
