/** Contract that separate per-agent profile files stay retired. */

import { existsSync, readdirSync } from "node:fs";
import { join } from "node:path";
import { describe, expect, it } from "vitest";
import { REPO_ROOT } from "#support/agent-spec-documents.ts";

describe("retired agent profiles", () => {
  it("carries no per-agent profile file", () => {
    const agentsDirectory = join(REPO_ROOT, "agents");
    const profiles = existsSync(agentsDirectory)
      ? readdirSync(agentsDirectory, { withFileTypes: true })
          .filter((entry) => entry.isDirectory())
          .map((entry) => join(agentsDirectory, entry.name, "profile.md"))
          .filter((candidate) => existsSync(candidate))
          .sort()
      : [];

    expect(profiles).toEqual([]);
  });
});
