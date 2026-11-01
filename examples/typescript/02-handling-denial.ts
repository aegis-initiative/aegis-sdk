/**
 * Example 2: Handling a denial response.
 *
 * demo-agent is granted the file.write capability -- but a separate policy
 * denies all file writes outright. This is the scenario the demo is built
 * to teach: having a capability is necessary but not sufficient, since a
 * policy can still override it. A DENY verdict is a normal
 * GovernanceDecision return value, not a thrown error -- it's an expected
 * outcome of evaluation, so there's no try/catch needed to "catch" it.
 *
 * Run: npx tsx 02-handling-denial.ts
 */
import { AegisClient, Verdict } from "@aegis-initiative/sdk";

async function main() {
  const client = new AegisClient({
    baseUrl: process.env.AEGIS_SDK_EXAMPLE_BASE_URL ?? "https://demo.aegis-platform.net",
    apiKey: "example-02",
  });

  const decision = await client.propose({
    actor: { id: "demo-agent", type: "ai-agent" },
    capability: "file.write",
    resource: "/home/documents/report.txt",
    parameters: {},
  });

  if (decision.decision === Verdict.DENY) {
    // This branch is where your application decides what to do next: log
    // it, surface it to a human, or just stop. Nothing exceptional
    // happened at the SDK layer -- the governance engine did its job.
    console.log(`Denied: ${decision.reason}`);
    console.log(`Audit ref for this denial: ${decision.auditRef}`);
  } else {
    console.log(`Unexpected verdict: ${decision.decision}`);
  }

  if (decision.decision !== Verdict.DENY) {
    throw new Error(
      "pol-deny-file-write blocks all file writes regardless of " +
        "capability grants, so this should always DENY",
    );
  }
}

main();
