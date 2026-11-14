/** Source-version contract for the agent runtime specifications. */

import { existsSync, readFileSync, readdirSync } from "node:fs";
import { join } from "node:path";
import { describe, expect, it } from "vitest";
import { AGENT_SPECS_DIR, splitFrontmatter } from "#support/agent-spec-documents.ts";

const EXPECTED_SPEC_FILES = [
  "atrium.md",
  "bastion.md",
  "crucible.md",
  "forge.md",
  "herald.md",
  "inquisitor.md",
  "investigator.md",
  "ledger.md",
  "lumen.md",
  "quill.md",
  "scribe.md",
  "sentinel.md",
  "vault.md",
  "warden.md",
] as const;

const EXPECTED_SPEC_VERSIONS: Readonly<Record<string, string>> = {
  "atrium.md": "1.14.1",
  "bastion.md": "1.18.1",
  "crucible.md": "1.18.1",
  "forge.md": "3.4.0",
  "herald.md": "1.14.1",
  "inquisitor.md": "1.16.2",
  "investigator.md": "1.5.0",
  "ledger.md": "2.3.0",
  "lumen.md": "1.4.1",
  "quill.md": "1.6.0",
  "scribe.md": "1.4.0",
  "sentinel.md": "1.21.1",
  "vault.md": "1.8.0",
  "warden.md": "1.11.0",
};

const SEMVER_RE = /^\d+\.\d+\.\d+$/u;

function declaredVersion(frontmatter: string, specName: string): string {
  const versions = frontmatter
    .split("\n")
    .filter((line) => line.startsWith("version:"))
    .map((line) => (line.split(":", 2)[1] ?? "").trim());

  expect(versions, `${specName}: expected exactly one version line`).toHaveLength(1);
  return versions[0]!;
}

function specContent(specName: string): string {
  return readFileSync(join(AGENT_SPECS_DIR, specName), "utf8");
}

describe("agent specification versions", () => {
  it("declares a valid version on every specification", () => {
    expect(existsSync(AGENT_SPECS_DIR), AGENT_SPECS_DIR).toBe(true);
    expect(readdirSync(AGENT_SPECS_DIR).filter((name) => name.endsWith(".md")).sort()).toEqual([
      ...EXPECTED_SPEC_FILES,
    ]);

    for (const specName of EXPECTED_SPEC_FILES) {
      const { frontmatter } = splitFrontmatter(specContent(specName));
      expect(frontmatter, `${specName}: no frontmatter block`).not.toBe("");
      expect(declaredVersion(frontmatter, specName), specName).toMatch(SEMVER_RE);
    }
  });

  it("declares the pinned version on every specification", () => {
    for (const [specName, expected] of Object.entries(EXPECTED_SPEC_VERSIONS)) {
      const { frontmatter } = splitFrontmatter(specContent(specName));
      expect(frontmatter, `${specName}: no frontmatter block`).not.toBe("");
      expect(declaredVersion(frontmatter, specName), specName).toBe(expected);
    }
  });
});
