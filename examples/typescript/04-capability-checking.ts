/**
 * Example 4: Capability checking.
 *
 * Lists every capability registered in the governance runtime and shows
 * how to use that list client-side: deciding whether a capability
 * plausibly covers a given action/target *before* spending a round trip
 * on propose(). This is advisory only -- the governance engine (not this
 * client-side check) is the actual authority, since a policy can still
 * deny an action even when a capability nominally covers it (see
 * example 2).
 *
 * Run: npx tsx 04-capability-checking.ts
 */
import { AegisClient, type Capability } from "@aegis-initiative/sdk";

/**
 * Client-side only -- mirrors the shape of the real check the governance
 * engine performs, for UI/UX purposes (e.g. graying out an action before
 * the user tries it), not as a substitute for propose(). Uses the same
 * fnmatch-style glob rules aegis-platform's target_patterns use: `*`
 * matches any run of characters.
 */
function covers(capability: Capability, actionType: string, target: string): boolean {
  const globToRegExp = (glob: string) =>
    new RegExp(`^${glob.replace(/[.+^${}()|[\]\\]/g, "\\$&").replace(/\*/g, ".*")}$`);
  return (
    capability.actionTypes.includes(actionType) &&
    capability.targetPatterns.some((pattern) => globToRegExp(pattern).test(target))
  );
}

async function main() {
  const client = new AegisClient({
    baseUrl: process.env.AEGIS_SDK_EXAMPLE_BASE_URL ?? "https://demo.aegis-platform.net",
    apiKey: "example-04",
  });

  const capabilities = await client.listCapabilities();
  console.log(`${capabilities.length} capabilities registered in this sandbox:\n`);
  for (const cap of capabilities) {
    console.log(`  ${cap.id}: ${cap.name} (${cap.platform})`);
    console.log(`    actionTypes: ${JSON.stringify(cap.actionTypes)}`);
    console.log(`    targetPatterns: ${JSON.stringify(cap.targetPatterns)}`);
  }

  console.log();
  const checks: [string, string][] = [
    ["file_read", "/home/documents/report.txt"],
    ["file_read", "/etc/passwd"],
    ["data_access", "postgres://prod/customers"],
  ];
  for (const [actionType, target] of checks) {
    const match = capabilities.find((c) => covers(c, actionType, target));
    const verdict = match ? `covered by ${match.name}` : "no capability covers this";
    console.log(`${actionType} on ${target}: ${verdict}`);
  }
}

main();
