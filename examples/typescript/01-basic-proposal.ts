/**
 * Example 1: Basic proposal submission.
 *
 * Submits an ACTION_PROPOSE for a file read that the demo-agent identity is
 * actually granted -- the governance engine evaluates it and returns ALLOW.
 *
 * Run: npx tsx 01-basic-proposal.ts
 */
import { AegisClient, Verdict } from "@aegis-initiative/sdk";

async function main() {
  // Any string works as the apiKey -- the public demo treats it as an
  // opaque per-visitor sandbox token, not a real credential, so this just
  // gets you your own isolated sandbox session.
  const client = new AegisClient({
    baseUrl: process.env.AEGIS_SDK_EXAMPLE_BASE_URL ?? "https://demo.aegis-platform.net",
    apiKey: "example-01",
  });

  const decision = await client.propose({
    actor: { id: "demo-agent", type: "ai-agent" },
    capability: "file.read",
    resource: "/home/documents/report.txt",
    parameters: {},
  });

  console.log(`Decision: ${decision.decision}`);
  console.log(`Reason:   ${decision.reason}`);
  console.log(`Risk score: ${decision.riskScore}`);
  console.log(`Audit ref:  ${decision.auditRef}`);

  if (decision.decision !== Verdict.ALLOW) {
    throw new Error(
      "demo-agent is granted cap-file-read-docs for /home/documents/*, " +
        "so this should always ALLOW against the current demo configuration",
    );
  }
}

main();
