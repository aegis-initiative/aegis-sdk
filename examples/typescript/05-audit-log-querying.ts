/**
 * Example 5: Audit log querying.
 *
 * Submits a couple of proposals (so there's something to query), then
 * reads the unified audit log back -- both unfiltered and filtered by
 * agentId / decision. Every propose() call is automatically recorded;
 * this is how you retrieve that history rather than keeping your own
 * copy.
 *
 * Run: npx tsx 05-audit-log-querying.ts
 */
import { AegisClient } from "@aegis-initiative/sdk";

async function main() {
  const client = new AegisClient({
    baseUrl: process.env.AEGIS_SDK_EXAMPLE_BASE_URL ?? "https://demo.aegis-platform.net",
    apiKey: "example-05",
  });

  // Generate a couple of audit entries to query back.
  await client.propose({
    actor: { id: "demo-agent", type: "ai-agent" },
    capability: "file.read",
    resource: "/home/documents/report.txt",
    parameters: {},
  });
  await client.propose({
    actor: { id: "demo-agent", type: "ai-agent" },
    capability: "file.write",
    resource: "/home/documents/report.txt",
    parameters: {},
  });

  console.log("-- All recent events --");
  for (const event of await client.getAuditEvents({ limit: 10 })) {
    if (event.source === "governance") {
      console.log(`  [${event.timestamp}] ${event.agentId}: ${event.actionType} -> ${event.decision}`);
    } else {
      console.log(`  [${event.timestamp}] (platform) ${event.eventType}: ${event.summary}`);
    }
  }

  console.log("\n-- Filtered to demo-agent only --");
  for (const event of await client.getAuditEvents({ agentId: "demo-agent", limit: 10 })) {
    console.log(`  [${event.timestamp}] ${event.actionType} -> ${event.decision}`);
  }

  console.log("\n-- Filtered to DENY only --");
  for (const event of await client.getAuditEvents({ decision: "DENY", limit: 10 })) {
    console.log(`  [${event.timestamp}] ${event.agentId}: ${event.actionType} -> ${event.reason}`);
  }
}

main();
