/**
 * Example 3: Escalation flow.
 *
 * demo-agent is granted network.fetch for a short list of approved
 * domains, but a policy routes every network request to ESCALATE for
 * review rather than auto-allowing it -- even to an approved domain.
 * ESCALATE means "don't auto-allow, but don't auto-deny either": a human
 * or a higher-authority process needs to decide, and your application's
 * job is to route that decision somewhere (a queue, a notification, a
 * dashboard), not to retry or treat it as a failure.
 *
 * Run: npx tsx 03-escalation-flow.ts
 */
import { AegisClient, Verdict } from "@aegis-initiative/sdk";

async function main() {
  const client = new AegisClient({
    baseUrl: process.env.AEGIS_SDK_EXAMPLE_BASE_URL ?? "https://demo.aegis-platform.net",
    apiKey: "example-03",
  });

  const decision = await client.propose({
    actor: { id: "demo-agent", type: "ai-agent" },
    capability: "network.fetch",
    resource: "https://api.github.com/repos/aegis-initiative/aegis-core",
    parameters: {},
  });

  if (decision.decision === Verdict.ESCALATE) {
    console.log(`Needs review: ${decision.reason}`);
    console.log(`Audit ref to attach to the review ticket: ${decision.auditRef}`);
    // In a real integration, this is where you'd open a review item --
    // e.g. post decision.auditRef to a queue or ticketing system and wait
    // for a human verdict before the agent proceeds.
  } else {
    console.log(`Unexpected verdict: ${decision.decision}`);
  }

  if (decision.decision !== Verdict.ESCALATE) {
    throw new Error(
      "pol-escalate-network routes every network.fetch to ESCALATE " +
        "regardless of domain, so this should always ESCALATE",
    );
  }
}

main();
