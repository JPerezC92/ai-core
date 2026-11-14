/**
 * Integration contract for region-delimited agent source surfaces.
 *
 * Rule coverage mirrors the former Python suite module for module; each
 * assertion group is its own case so a failure names the rule it broke.
 */

import { readFileSync, readdirSync } from "node:fs";
import { join } from "node:path";
import { describe, expect, it } from "vitest";
import {
  AGENT_SPECS_DIR,
  CORE_BEGIN,
  CORE_END,
  PROJECT_BEGIN,
  PROJECT_END,
  exactMarkerLineIndices,
  extractSourceCore,
  findCoreMarkers,
  projectText,
  splitFrontmatter,
  splitLines,
  unfencedLines,
} from "#support/agent-spec-documents.ts";
import {
  effectivePermission,
  readHarnessConfig,
} from "#support/harness-permissions.ts";

const SPEC_H3 = [
  "Your Role",
  "Roster Context",
  "Rulebook",
  "Workflow",
  "Tools and References",
  "Output Format",
  "Stop and Report",
  "Hard Rules",
] as const;

const CORE_ANCHORS: Readonly<Record<string, string>> = {
  "atrium.md": "typescript/react.md",
  "forge.md": "Static Data Service Pattern",
  "ledger.md": "Close out now",
  "sentinel.md": "node_modules/",
  "vault.md": "Harness Parent Directories",
  "warden.md": "pnpm audit",
};

const LOCAL_ONLY: Readonly<Record<string, readonly string[]>> = {
  "crucible.md": [
    "The AICore project's narrow read-only discovery allowance includes " +
      "`rg`, `ls`, and `wc`. These commands are not test execution or a " +
      "package install. No Git command is authorized: the core no-Git " +
      "boundary applies to read-only Git as well as mutations, regardless " +
      "of any conflicting harness allow.",
  ],
  "warden.md": [
    "AICore's root carries no Python project: `pyproject.toml`, `uv.lock` and the pytest suite were removed once the repository contract suite was ported to TypeScript and passed.",
    "The two MCP tooling projects under `.opencode/tooling/` each own a locked Python environment and are provisioned per `docs/tooling.md`; the Python branch applies to those manifests, not to the repository root.",
    "The project's reviewed whole-suite command is `pnpm --dir tests test`.",
  ],
  "herald.md": [
    "This project's protected upstream base ref is `origin/main` — remote " +
      "`origin`, branch `main`.",
  ],
};

const CORE_DELIMITERS = new Set([CORE_BEGIN, CORE_END]);

function specNames(): string[] {
  return readdirSync(AGENT_SPECS_DIR)
    .filter((name) => name.endsWith(".md"))
    .sort();
}

function specContent(name: string): string {
  return readFileSync(join(AGENT_SPECS_DIR, name), "utf8");
}

describe("agent source regions", () => {
  it("places the core markers after the frontmatter", () => {
    const names = specNames();
    expect(names).toHaveLength(14);

    for (const name of names) {
      const content = specContent(name);
      const { frontmatter, body, frontmatterLineCount } = splitFrontmatter(content);
      const coreMarkers = findCoreMarkers(content);

      expect(frontmatter, name).not.toBe("");
      const frontmatterLines = splitLines(frontmatter);
      expect(frontmatterLines[0]?.trim(), name).toBe("---");
      expect(frontmatterLines.at(-1)?.trim(), name).toBe("---");
      expect(coreMarkers, name).not.toBeNull();
      expect(body.startsWith(`${CORE_BEGIN}\n`), name).toBe(true);
      expect(coreMarkers?.begin, name).toBe(frontmatterLineCount);

      const core = extractSourceCore(content);
      expect(core.trim(), name).not.toBe("");
      expect(
        unfencedLines(core).filter((line) => CORE_DELIMITERS.has(line.trim())),
        name,
      ).toEqual([]);
    }
  });

  it("keeps the eight core headings in order", () => {
    const expected = SPEC_H3.map((heading) => `### ${heading}`);

    for (const name of specNames()) {
      const core = extractSourceCore(specContent(name));
      const headings = unfencedLines(core)
        .map((line) => line.trim())
        .filter((line) => expected.includes(line as (typeof expected)[number]))
        .map((line) => line.slice(4));

      expect(headings, name).toEqual([...SPEC_H3]);
    }
  });

  it("keeps each core region's positive anchor", () => {
    for (const name of specNames()) {
      const anchor = CORE_ANCHORS[name];
      if (anchor === undefined) continue;

      expect(extractSourceCore(specContent(name)), name).toContain(anchor);
    }
  });

  it("keeps project-local facts out of the core region", () => {
    for (const [name, facts] of Object.entries(LOCAL_ONLY)) {
      const content = specContent(name);
      const core = extractSourceCore(content);
      const project = projectText(content);

      for (const fact of facts) {
        expect(core, `${name} core`).not.toContain(fact);
        expect(project, `${name} project`).toContain(fact);
      }
    }
  });

  it("keeps the optional project region shape", () => {
    for (const name of specNames()) {
      const lines = splitLines(specContent(name));
      const begins = exactMarkerLineIndices(lines, PROJECT_BEGIN);
      const ends = exactMarkerLineIndices(lines, PROJECT_END);

      expect(begins.length, name).toBe(ends.length);
      expect(begins.length, name).toBeLessThanOrEqual(1);

      if (begins.length > 0) {
        const begin = begins[0]!;
        expect(begin > 0, name).toBe(true);
        expect(lines[begin - 1]?.trim(), name).toBe("");
        expect(lines.at(-1)?.trim(), name).toBe(PROJECT_END);
      } else {
        expect(lines.at(-1)?.trim(), name).toBe(CORE_END);
      }
    }
  });
});

describe("effective harness permissions", () => {
  function mandatoryCheckCommands(): string[] {
    for (const line of projectText(specContent("warden.md")).split("\n")) {
      if (!line.startsWith("**Mandatory check commands:**")) continue;
      return [...line.matchAll(/`([^`]+)`/gu)].map((match) => match[1]!);
    }
    return [];
  }

  it("makes every mandatory warden check executable", () => {
    const commands = mandatoryCheckCommands();
    expect(commands.length, "warden.md declares no mandatory check commands").toBeGreaterThan(0);

    const config = readHarnessConfig();
    for (const command of commands) {
      expect(effectivePermission(config, "warden", command), command).toBe("allow");
    }
  });

  it("enforces the dependency permission boundaries", () => {
    const config = readHarnessConfig();

    const allowedForForge = [
      "pnpm install --lockfile-only --ignore-scripts",
      "pnpm --dir cli/aicore test",
      "pnpm --dir cli/aicore test:e2e",
      "pnpm --dir cli/aicore typecheck",
      "pnpm --dir .opencode/plugins/odd-adviser exec vitest run",
      "pnpm --dir .opencode/plugins/odd-adviser typecheck",
      "pnpm --dir mcp-servers/system-one exec vitest run",
      "pnpm --dir mcp-servers/system-one typecheck",
      "pnpm --dir .agents/skills/odd-workflow exec vitest run",
      "pnpm --dir .agents/skills/odd-workflow typecheck",
    ];
    for (const command of allowedForForge) {
      expect(effectivePermission(config, "forge", command), command).toBe("allow");
    }

    const deniedForForge = [
      "pnpm install",
      "pnpm install --ignore-scripts",
      "pnpm install --lockfile-only",
      "pnpm --dir cli/aicore install",
      "pnpm i",
      "pnpm add yaml",
      "pnpm remove yaml",
      "pnpm update",
      "pnpm audit --fix",
    ];
    for (const command of deniedForForge) {
      expect(effectivePermission(config, "forge", command), command).toBe("deny");
    }

    const deniedForWarden = [
      "pnpm install",
      "pnpm --dir cli/aicore install",
      "uv sync",
      "uv add pyyaml",
      "npm install yaml",
    ];
    for (const command of deniedForWarden) {
      expect(effectivePermission(config, "warden", command), command).toBe("deny");
    }

    for (const command of ["pnpm audit --json", "pnpm outdated --json"]) {
      expect(effectivePermission(config, "warden", command), command).toBe("allow");
    }

    expect(effectivePermission(config, "crucible", "pnpm install")).toBe("allow");
  });
});
