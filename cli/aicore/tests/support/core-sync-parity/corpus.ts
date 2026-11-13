/**
 * The behavioral-parity corpus for the TypeScript synchronization engine.
 *
 * Every case here states its fixture, its command, and the outcome the
 * *contract* requires. No case computes an expectation by running an engine:
 * the expected bytes are written down, so the same table judges a different
 * engine without a single line of it changing.
 *
 * Provenance rules this table follows:
 *
 * - A contract citation (`provenance.contract`) marks an expectation the
 *   documented contract fixes: the exit code, the command's success word, the
 *   region, raw and merge payload bytes, the pending list, the report's
 *   content, the blocker block's shape.
 * - A reference citation (`provenance.reference`) marks behaviour the contract
 *   does not spell out and that was read from the Python reference engine: the
 *   diagnostic wording, the exact serialization of the two YAML documents, and
 *   the shipped text of the blocker block. Those are flagged for the
 *   coordinator, and a TypeScript engine that differs must change the corpus
 *   by an explicit decision, never silently.
 */

import {
  OTHER_REVISION,
  REVISION,
} from "./fixtures.ts";
import {
  CONTRACT_BLOCK_FACTS,
  BLOCK_BEGIN,
  BLOCK_END,
  rootWithBlocker,
} from "./blocker.ts";
import { BINDING_DECLARATION_CASES } from "./cases/binding-declarations.ts";
import { CLEARANCE_INTEGRITY_CASES } from "./cases/clearance-integrity.ts";
import { ROOT_ROLE_CASES } from "./cases/root-role.ts";
import type { ParityCase, TreeEntry } from "./types.ts";

/* ------------------------------------------------------------------ *
 * Synthetic source and destination material
 * ------------------------------------------------------------------ */

const SOURCE_REGION_PATH = "shared.md";
const SOURCE_RAW_PATH = "raw.md";
const SOURCE_MERGE_PATH = "config.jsonc";
const SOURCE_MERGE_SIMPLE_PATH = "theme.jsonc";

const SOURCE_REGION_TEXT = [
  "---",
  "name: shared",
  "description: Shared source description",
  "version: 2.0.0",
  "---",
  "",
  "Shared core line one.",
  "Shared core line two.",
  "",
].join("\n");

const SOURCE_RAW_TEXT = "raw payload line one\nraw payload line two";

const SOURCE_MERGE_TEXT = [
  "{",
  '  "theme": "dark",',
  '  "mcp": {',
  '    "servers": {',
  '      "qmd": {',
  '        "command": ["npx", "-y", "@tobilu/qmd@2.8.3", "--index", "ai-core", "mcp"]',
  "      }",
  "    }",
  "  }",
  "}",
  "",
].join("\n");

const SOURCE_MERGE_SIMPLE_TEXT = ['{', '  "theme": "dark"', "}", ""].join("\n");

const ROOT_RUNTIME_TEXT = "# Project under test\n\nA disposable destination for the parity corpus.\n";

const DEST_REGION_MARKED_TEXT = [
  "---",
  "name: shared",
  "description: Destination description",
  "version: 1.0.0",
  "local-version: 1.0.0",
  "---",
  "",
  "<!-- core:begin -->",
  "Old shared body.",
  "<!-- core:end -->",
  "",
  "<!-- project:begin -->",
  "Destination project content.",
  "<!-- project:end -->",
  "",
].join("\n");

const DEST_REGION_MARKERLESS_TEXT = "Destination body before sync.\n";

const DEST_MERGE_TEXT = [
  "{",
  '  "theme": "light",',
  '  "own": true',
  "}",
  "",
].join("\n");

const DEST_MERGE_COMMENT_TEXT = [
  "{",
  "  // The destination keeps its own comment.",
  '  "theme": "light",',
  '  "own": true',
  "}",
  "",
].join("\n");

const DEST_MERGE_MCP_TEXT = [
  "{",
  "  // The destination keeps its own comment.",
  '  "mcp": {',
  '    "servers": {',
  '      "qmd": {',
  '        "command": ["npx", "-y", "@tobilu/qmd@2.8.3", "--index", "ai-core", "mcp"]',
  "      },",
  '      "local": {',
  '        "command": ["node", "local-server.js"]',
  "      }",
  "    }",
  "  }",
  "}",
  "",
].join("\n");

const EXPECT_REGION_SPLICED_TEXT = [
  "---",
  "name: shared",
  "description: Shared source description",
  "version: 2.0.0",
  "local-version: 1.0.0",
  "---",
  "",
  "<!-- core:begin -->",
  "",
  "Shared core line one.",
  "Shared core line two.",
  "<!-- core:end -->",
  "",
  "<!-- project:begin -->",
  "Destination project content.",
  "<!-- project:end -->",
  "",
].join("\n");

const EXPECT_REGION_ENROLLED_TEXT = [
  "---",
  "name: shared",
  "description: Shared source description",
  "version: 2.0.0",
  "---",
  "<!-- core:begin -->",
  "",
  "Shared core line one.",
  "Shared core line two.",
  "<!-- core:end -->",
  "",
  "<!-- project:begin -->",
  "Destination body before sync.",
  "<!-- project:end -->",
  "",
].join("\n");

const EXPECT_REGION_CREATED_TEXT = [
  "---",
  "name: shared",
  "description: Shared source description",
  "version: 2.0.0",
  "---",
  "<!-- core:begin -->",
  "",
  "Shared core line one.",
  "Shared core line two.",
  "<!-- core:end -->",
  "",
  "<!-- project:begin -->",
  "<!-- project:end -->",
  "",
].join("\n");

const EXPECT_MERGE_TOP_LEVEL_TEXT = [
  "{",
  "  // The destination keeps its own comment.",
  '  "theme": "dark",',
  '  "own": true',
  "}",
  "",
].join("\n");

const EXPECT_MERGE_MCP_TEXT = [
  "{",
  "  // The destination keeps its own comment.",
  '  "mcp": {',
  '    "servers": {',
  '      "qmd": {',
  '        "command": ["npx", "-y", "@tobilu/qmd@2.8.3", "--index", "project-under-test", "mcp"]',
  "      },",
  '      "local": {',
  '        "command": ["node", "local-server.js"]',
  "      }",
  "    }",
  "  },",
  '  "theme": "dark"',
  "}",
  "",
].join("\n");

/* ------------------------------------------------------------------ *
 * Fixture builders
 * ------------------------------------------------------------------ */

type BindingMapping = {
  readonly source: string;
  readonly destinations: readonly string[];
  readonly mode?: string;
};

function bindingsYaml(params: {
  readonly revision?: string;
  readonly root?: string;
  readonly entries?: readonly BindingMapping[];
  readonly pending?: readonly string[];
}): string {
  const lines: string[] = ["schema: 1", `core_revision: ${params.revision ?? REVISION}`];
  if (params.root !== undefined) {
    lines.push(`root: ${params.root}`);
  }
  lines.push("bindings:");
  for (const entry of params.entries ?? []) {
    lines.push(`- source: ${entry.source}`);
    lines.push("  destinations:");
    for (const destination of entry.destinations) {
      lines.push(`  - ${destination}`);
    }
    if (entry.mode !== undefined) {
      lines.push(`  mode: ${entry.mode}`);
    }
  }
  const pending = params.pending ?? [];
  if (pending.length === 0) {
    lines.push("pending: []");
  } else {
    lines.push("pending:");
    for (const path of pending) {
      lines.push(`- ${path}`);
    }
  }
  return `${lines.join("\n")}\n`;
}

function clearanceJson(records: Readonly<Record<string, { readonly mode: string; readonly role?: string }>>): string {
  const cleared: Record<string, unknown> = {};
  for (const [path, record] of Object.entries(records)) {
    cleared[path] =
      record.role === undefined ? { mode: record.mode } : { mode: record.mode, role: record.role };
  }
  return `${JSON.stringify({ schema: 1, cleared }, null, 2)}\n`;
}

const REGION_CLEARANCE = clearanceJson({ [SOURCE_REGION_PATH]: { mode: "region" } });
const RAW_CLEARANCE = clearanceJson({ [SOURCE_RAW_PATH]: { mode: "raw" } });
const MERGE_CLEARANCE = clearanceJson({
  [SOURCE_MERGE_PATH]: { mode: "merge" },
  [SOURCE_MERGE_SIMPLE_PATH]: { mode: "merge" },
});

/* ------------------------------------------------------------------ *
 * Expected tree builders
 * ------------------------------------------------------------------ */

const AICTORE_DIRECTORY: TreeEntry = { kind: "directory", path: ".aicore" };
const RECONCILIATION_DIRECTORY: TreeEntry = {
  kind: "directory",
  path: ".aicore/reconciliation",
};

function bindingsEntry(params: {
  readonly path?: string;
  readonly revision?: string;
  readonly root?: string | null;
  readonly entries?: readonly { readonly source: string; readonly destinations: readonly string[] }[];
  readonly pending?: readonly string[];
}): TreeEntry {
  return {
    kind: "bindings",
    path: params.path ?? ".aicore/core.yaml",
    document: {
      schema: 1,
      coreRevision: params.revision ?? REVISION,
      root: params.root ?? null,
      bindings: params.entries ?? [],
      pending: params.pending ?? [],
    },
  };
}

function reportEntry(params: {
  readonly revision?: string;
  readonly entries?: readonly {
    readonly destination: string;
    readonly source: string;
    readonly action: string;
  }[];
}): TreeEntry {
  return {
    kind: "report",
    path: ".aicore/reconciliation/init.yaml",
    document: {
      schema: 1,
      coreRevision: params.revision ?? REVISION,
      entries: params.entries ?? [],
    },
  };
}

function blockerEntry(rootText: string): TreeEntry {
  return {
    kind: "blocker",
    path: "AGENTS.md",
    prefix: `${rootText.endsWith("\n") ? rootText : `${rootText}\n`}\n${BLOCK_BEGIN}\n`,
    suffix: `\n${BLOCK_END}\n`,
    bodyContains: CONTRACT_BLOCK_FACTS,
  };
}

function rootFile(content: string): TreeEntry {
  return { kind: "file", path: "AGENTS.md", content };
}

/* ------------------------------------------------------------------ *
 * The corpus
 * ------------------------------------------------------------------ */

export const CORPUS: readonly ParityCase[] = [
  /* ---------------- region mode ---------------- */
  {
    id: "region-apply-splices-core",
    concern: "region-mode",
    title: "apply replaces the core region and keeps the project region and the destination-only frontmatter key",
    provenance: {
      contract: [
        "SKILL.md / Binding modes: region — `apply` splices only the content strictly between the destination's core markers",
        "SKILL.md / What I do: the destination's own project region is preserved by content",
        "SKILL.md / What I do: a destination-only frontmatter key keeps its exact bytes",
      ],
      reference: [
        "The refreshed frontmatter keeps the destination's key order and keeps `local-version` after the source-defined keys.",
      ],
    },
    fixture: {
      sourceFiles: [{ path: SOURCE_REGION_PATH, content: SOURCE_REGION_TEXT }],
      clearance: REGION_CLEARANCE,
      destinationFiles: [
        { path: "AGENTS.md", content: ROOT_RUNTIME_TEXT },
        { path: SOURCE_REGION_PATH, content: DEST_REGION_MARKED_TEXT },
      ],
      bindings: bindingsYaml({
        entries: [{ source: SOURCE_REGION_PATH, destinations: [SOURCE_REGION_PATH] }],
      }),
    },
    steps: [{ command: "apply" }],
    expectations: [{ exitCode: 0, stdout: "applied\n", stderr: { kind: "empty" } }],
    destinationTree: [
      rootFile(ROOT_RUNTIME_TEXT),
      { kind: "file", path: SOURCE_REGION_PATH, content: EXPECT_REGION_SPLICED_TEXT },
      AICTORE_DIRECTORY,
      bindingsEntry({ entries: [{ source: SOURCE_REGION_PATH, destinations: [SOURCE_REGION_PATH] }] }),
    ],
    sourceTree: [
      { kind: "file", path: SOURCE_REGION_PATH, content: SOURCE_REGION_TEXT },
      { kind: "file", path: "distribution-clearance.json", content: REGION_CLEARANCE },
    ],
  },
  {
    id: "region-init-enrolls-markerless",
    concern: "region-mode",
    title: "init turns a markerless destination into a core region plus a project region and records the reconciliation",
    provenance: {
      contract: [
        "SKILL.md / Commands: `init` rebuilds a markerless destination as frontmatter + a core region holding the source core + a project region holding the destination's previous body, then records that region path in `pending`",
        "SKILL.md / Reconciliation blocker: while region-mode paths remain in `pending`, `check`, `apply`, and `init` ensure the destination root runtime file carries a marker-delimited blocker block",
      ],
      reference: [
        "The exact byte layout of the enrolled file, the report's YAML serialization and the blocker block's words are reference behaviour.",
      ],
    },
    fixture: {
      sourceFiles: [{ path: SOURCE_REGION_PATH, content: SOURCE_REGION_TEXT }],
      clearance: REGION_CLEARANCE,
      destinationFiles: [
        { path: "AGENTS.md", content: ROOT_RUNTIME_TEXT },
        { path: SOURCE_REGION_PATH, content: DEST_REGION_MARKERLESS_TEXT },
      ],
      bindings: bindingsYaml({
        entries: [{ source: SOURCE_REGION_PATH, destinations: [SOURCE_REGION_PATH] }],
      }),
    },
    steps: [{ command: "init" }],
    expectations: [{ exitCode: 0, stdout: "initialized\n", stderr: { kind: "empty" } }],
    destinationTree: [
      blockerEntry(ROOT_RUNTIME_TEXT),
      { kind: "file", path: SOURCE_REGION_PATH, content: EXPECT_REGION_ENROLLED_TEXT },
      AICTORE_DIRECTORY,
      RECONCILIATION_DIRECTORY,
      bindingsEntry({
        entries: [{ source: SOURCE_REGION_PATH, destinations: [SOURCE_REGION_PATH] }],
        pending: [SOURCE_REGION_PATH],
      }),
      reportEntry({
        entries: [{ destination: SOURCE_REGION_PATH, source: SOURCE_REGION_PATH, action: "initialized" }],
      }),
    ],
  },
  {
    id: "region-init-refreshes-marked",
    concern: "region-mode",
    title: "init refreshes an already-marked destination and records it as refreshed",
    provenance: {
      contract: [
        "SKILL.md / Commands: `init` enrolls markerless destinations, raw-copies whole-file bindings, merge top-level keys, and refreshes existing bindings",
        "SKILL.md / Examples: already marked region destinations refresh their core and their source-defined frontmatter while preserving the rest of their outside content",
      ],
      reference: ["The report entry's action word `refreshed` is reference behaviour."],
    },
    fixture: {
      sourceFiles: [{ path: SOURCE_REGION_PATH, content: SOURCE_REGION_TEXT }],
      clearance: REGION_CLEARANCE,
      destinationFiles: [
        { path: "AGENTS.md", content: ROOT_RUNTIME_TEXT },
        { path: SOURCE_REGION_PATH, content: DEST_REGION_MARKED_TEXT },
      ],
      bindings: bindingsYaml({
        entries: [{ source: SOURCE_REGION_PATH, destinations: [SOURCE_REGION_PATH] }],
      }),
    },
    steps: [{ command: "init" }],
    expectations: [{ exitCode: 0, stdout: "initialized\n", stderr: { kind: "empty" } }],
    destinationTree: [
      blockerEntry(ROOT_RUNTIME_TEXT),
      { kind: "file", path: SOURCE_REGION_PATH, content: EXPECT_REGION_SPLICED_TEXT },
      AICTORE_DIRECTORY,
      RECONCILIATION_DIRECTORY,
      bindingsEntry({
        entries: [{ source: SOURCE_REGION_PATH, destinations: [SOURCE_REGION_PATH] }],
        pending: [SOURCE_REGION_PATH],
      }),
      reportEntry({
        entries: [{ destination: SOURCE_REGION_PATH, source: SOURCE_REGION_PATH, action: "refreshed" }],
      }),
    ],
  },
  {
    id: "region-init-creates-absent-target",
    concern: "region-mode",
    title: "init creates an absent declared region target as frontmatter, source core and an empty project region",
    provenance: {
      contract: [
        "SKILL.md / Examples: a declared region target may be absent; `apply` and `init` recreate it as a fresh creation (source frontmatter, source core, empty project region)",
      ],
      reference: ["The exact byte layout of the created file is reference behaviour."],
    },
    fixture: {
      sourceFiles: [{ path: SOURCE_REGION_PATH, content: SOURCE_REGION_TEXT }],
      clearance: REGION_CLEARANCE,
      destinationFiles: [{ path: "AGENTS.md", content: ROOT_RUNTIME_TEXT }],
      bindings: bindingsYaml({
        entries: [{ source: SOURCE_REGION_PATH, destinations: [SOURCE_REGION_PATH] }],
      }),
    },
    steps: [{ command: "init" }],
    expectations: [{ exitCode: 0, stdout: "initialized\n", stderr: { kind: "empty" } }],
    destinationTree: [
      blockerEntry(ROOT_RUNTIME_TEXT),
      { kind: "file", path: SOURCE_REGION_PATH, content: EXPECT_REGION_CREATED_TEXT },
      AICTORE_DIRECTORY,
      RECONCILIATION_DIRECTORY,
      bindingsEntry({
        entries: [{ source: SOURCE_REGION_PATH, destinations: [SOURCE_REGION_PATH] }],
        pending: [SOURCE_REGION_PATH],
      }),
      reportEntry({
        entries: [{ destination: SOURCE_REGION_PATH, source: SOURCE_REGION_PATH, action: "initialized" }],
      }),
    ],
  },
  {
    id: "region-apply-creates-absent-target",
    concern: "region-mode",
    title: "apply recreates an absent declared region target and names it in its success message",
    provenance: {
      contract: [
        "SKILL.md / Exit contract: `apply` prints `applied`, or `applied; created: <path>[, <path>]` when it recreated absent targets",
        "SKILL.md / Exit contract: `apply` and `init` repair a declared region or raw target by creating it",
      ],
      reference: ["`apply` records no pending entry and writes no reconciliation report for the recreated target; that is reference behaviour."],
    },
    fixture: {
      sourceFiles: [{ path: SOURCE_REGION_PATH, content: SOURCE_REGION_TEXT }],
      clearance: REGION_CLEARANCE,
      destinationFiles: [{ path: "AGENTS.md", content: ROOT_RUNTIME_TEXT }],
      bindings: bindingsYaml({
        entries: [{ source: SOURCE_REGION_PATH, destinations: [SOURCE_REGION_PATH] }],
      }),
    },
    steps: [{ command: "apply" }],
    expectations: [
      { exitCode: 0, stdout: `applied; created: ${SOURCE_REGION_PATH}\n`, stderr: { kind: "empty" } },
    ],
    destinationTree: [
      rootFile(ROOT_RUNTIME_TEXT),
      { kind: "file", path: SOURCE_REGION_PATH, content: EXPECT_REGION_CREATED_TEXT },
      AICTORE_DIRECTORY,
      bindingsEntry({ entries: [{ source: SOURCE_REGION_PATH, destinations: [SOURCE_REGION_PATH] }] }),
    ],
  },
  {
    id: "region-check-current",
    concern: "region-mode",
    title: "check reports a current region destination and writes nothing",
    provenance: {
      contract: [
        "SKILL.md / Exit contract: exit 0 — every core region matches the pinned revision … prints `current`",
      ],
      reference: [],
    },
    fixture: {
      sourceFiles: [{ path: SOURCE_REGION_PATH, content: SOURCE_REGION_TEXT }],
      clearance: REGION_CLEARANCE,
      destinationFiles: [
        { path: "AGENTS.md", content: ROOT_RUNTIME_TEXT },
        { path: SOURCE_REGION_PATH, content: EXPECT_REGION_SPLICED_TEXT },
      ],
      bindings: bindingsYaml({
        entries: [{ source: SOURCE_REGION_PATH, destinations: [SOURCE_REGION_PATH] }],
      }),
    },
    steps: [{ command: "check" }],
    expectations: [{ exitCode: 0, stdout: "current\n", stderr: { kind: "empty" } }],
    destinationTree: [
      rootFile(ROOT_RUNTIME_TEXT),
      { kind: "file", path: SOURCE_REGION_PATH, content: EXPECT_REGION_SPLICED_TEXT },
      AICTORE_DIRECTORY,
      bindingsEntry({ entries: [{ source: SOURCE_REGION_PATH, destinations: [SOURCE_REGION_PATH] }] }),
    ],
  },
  {
    id: "region-check-region-drift",
    concern: "region-mode",
    title: "check reports a destination whose core region no longer matches the source",
    provenance: {
      contract: [
        "SKILL.md / Exit contract: exit 1 — drift … raw/region/merge mismatch",
      ],
      reference: ["The diagnostic word `region drift` is reference behaviour."],
    },
    fixture: {
      sourceFiles: [{ path: SOURCE_REGION_PATH, content: SOURCE_REGION_TEXT }],
      clearance: REGION_CLEARANCE,
      destinationFiles: [
        { path: "AGENTS.md", content: ROOT_RUNTIME_TEXT },
        { path: SOURCE_REGION_PATH, content: DEST_REGION_MARKED_TEXT },
      ],
      bindings: bindingsYaml({
        entries: [{ source: SOURCE_REGION_PATH, destinations: [SOURCE_REGION_PATH] }],
      }),
    },
    steps: [{ command: "check" }],
    expectations: [
      { exitCode: 1, stdout: "", stderr: { kind: "contains", value: ["region drift"] } },
    ],
    destinationTree: [
      rootFile(ROOT_RUNTIME_TEXT),
      { kind: "file", path: SOURCE_REGION_PATH, content: DEST_REGION_MARKED_TEXT },
      AICTORE_DIRECTORY,
      bindingsEntry({ entries: [{ source: SOURCE_REGION_PATH, destinations: [SOURCE_REGION_PATH] }] }),
    ],
  },
  {
    id: "region-check-frontmatter-drift",
    concern: "region-mode",
    title: "check reports a region destination whose frontmatter a write would change",
    provenance: {
      contract: [
        "SKILL.md / Exit contract: exit 1 — drift … `frontmatter drift` (a region destination frontmatter a write would change)",
        "SKILL.md / Exit contract: `check` reports neither a skipped nor an unmappable frontmatter as drift — only a frontmatter a refresh would change",
      ],
      reference: ["The diagnostic word `frontmatter drift` is reference behaviour."],
    },
    fixture: {
      sourceFiles: [{ path: SOURCE_REGION_PATH, content: SOURCE_REGION_TEXT }],
      clearance: REGION_CLEARANCE,
      destinationFiles: [
        { path: "AGENTS.md", content: ROOT_RUNTIME_TEXT },
        {
          path: SOURCE_REGION_PATH,
          content: EXPECT_REGION_SPLICED_TEXT.replace(
            "description: Shared source description",
            "description: A stale description",
          ),
        },
      ],
      bindings: bindingsYaml({
        entries: [{ source: SOURCE_REGION_PATH, destinations: [SOURCE_REGION_PATH] }],
      }),
    },
    steps: [{ command: "check" }],
    expectations: [
      { exitCode: 1, stdout: "", stderr: { kind: "contains", value: ["frontmatter drift"] } },
    ],
    destinationTree: [
      rootFile(ROOT_RUNTIME_TEXT),
      {
        kind: "file",
        path: SOURCE_REGION_PATH,
        content: EXPECT_REGION_SPLICED_TEXT.replace(
          "description: Shared source description",
          "description: A stale description",
        ),
      },
      AICTORE_DIRECTORY,
      bindingsEntry({ entries: [{ source: SOURCE_REGION_PATH, destinations: [SOURCE_REGION_PATH] }] }),
    ],
  },

  /* ---------------- raw mode ---------------- */
  {
    id: "raw-apply-copies-bytes",
    concern: "raw-mode",
    title: "apply copies a raw source byte-for-byte, without a trailing newline",
    provenance: {
      contract: [
        "SKILL.md / Binding modes: raw — `init` and `apply` write the source file to the destination byte-for-byte, and `check` verifies byte equality",
        "SKILL.md / What I do: raw sources are read as bytes without decoding or newline normalization",
      ],
      reference: [],
    },
    fixture: {
      sourceFiles: [{ path: SOURCE_RAW_PATH, content: SOURCE_RAW_TEXT }],
      clearance: RAW_CLEARANCE,
      destinationFiles: [
        { path: "AGENTS.md", content: ROOT_RUNTIME_TEXT },
        { path: SOURCE_RAW_PATH, content: "stale raw payload\n" },
      ],
      bindings: bindingsYaml({
        entries: [{ source: SOURCE_RAW_PATH, destinations: [SOURCE_RAW_PATH] }],
      }),
    },
    steps: [{ command: "apply" }],
    expectations: [{ exitCode: 0, stdout: "applied\n", stderr: { kind: "empty" } }],
    destinationTree: [
      rootFile(ROOT_RUNTIME_TEXT),
      { kind: "file", path: SOURCE_RAW_PATH, content: SOURCE_RAW_TEXT },
      AICTORE_DIRECTORY,
      bindingsEntry({ entries: [{ source: SOURCE_RAW_PATH, destinations: [SOURCE_RAW_PATH] }] }),
    ],
  },
  {
    id: "raw-check-current",
    concern: "raw-mode",
    title: "check reports a byte-identical raw destination as current",
    provenance: {
      contract: ["SKILL.md / Exit contract: exit 0 — every raw destination byte-matches its source"],
      reference: [],
    },
    fixture: {
      sourceFiles: [{ path: SOURCE_RAW_PATH, content: SOURCE_RAW_TEXT }],
      clearance: RAW_CLEARANCE,
      destinationFiles: [
        { path: "AGENTS.md", content: ROOT_RUNTIME_TEXT },
        { path: SOURCE_RAW_PATH, content: SOURCE_RAW_TEXT },
      ],
      bindings: bindingsYaml({
        entries: [{ source: SOURCE_RAW_PATH, destinations: [SOURCE_RAW_PATH] }],
      }),
    },
    steps: [{ command: "check" }],
    expectations: [{ exitCode: 0, stdout: "current\n", stderr: { kind: "empty" } }],
    destinationTree: [
      rootFile(ROOT_RUNTIME_TEXT),
      { kind: "file", path: SOURCE_RAW_PATH, content: SOURCE_RAW_TEXT },
      AICTORE_DIRECTORY,
      bindingsEntry({ entries: [{ source: SOURCE_RAW_PATH, destinations: [SOURCE_RAW_PATH] }] }),
    ],
  },
  {
    id: "raw-check-drift",
    concern: "raw-mode",
    title: "check reports a raw destination whose bytes differ from the source",
    provenance: {
      contract: ["SKILL.md / Exit contract: exit 1 — drift … raw/region/merge mismatch"],
      reference: ["The diagnostic word `raw drift` is reference behaviour."],
    },
    fixture: {
      sourceFiles: [{ path: SOURCE_RAW_PATH, content: SOURCE_RAW_TEXT }],
      clearance: RAW_CLEARANCE,
      destinationFiles: [
        { path: "AGENTS.md", content: ROOT_RUNTIME_TEXT },
        { path: SOURCE_RAW_PATH, content: "a different raw payload\n" },
      ],
      bindings: bindingsYaml({
        entries: [{ source: SOURCE_RAW_PATH, destinations: [SOURCE_RAW_PATH] }],
      }),
    },
    steps: [{ command: "check" }],
    expectations: [{ exitCode: 1, stdout: "", stderr: { kind: "contains", value: ["raw drift"] } }],
    destinationTree: [
      rootFile(ROOT_RUNTIME_TEXT),
      { kind: "file", path: SOURCE_RAW_PATH, content: "a different raw payload\n" },
      AICTORE_DIRECTORY,
      bindingsEntry({ entries: [{ source: SOURCE_RAW_PATH, destinations: [SOURCE_RAW_PATH] }] }),
    ],
  },
  {
    id: "raw-carries-no-region-artifacts",
    concern: "raw-mode",
    title: "a raw destination carries no project region, no reconciliation report and no pending entry",
    provenance: {
      contract: [
        "SKILL.md / Binding modes: raw — a raw destination carries no `project` region, creates no reconciliation report, and never creates a `pending` entry",
      ],
      reference: [],
    },
    fixture: {
      sourceFiles: [{ path: SOURCE_RAW_PATH, content: SOURCE_RAW_TEXT }],
      clearance: RAW_CLEARANCE,
      destinationFiles: [
        { path: "AGENTS.md", content: ROOT_RUNTIME_TEXT },
        { path: SOURCE_RAW_PATH, content: "stale raw payload\n" },
      ],
      bindings: bindingsYaml({
        entries: [{ source: SOURCE_RAW_PATH, destinations: [SOURCE_RAW_PATH] }],
      }),
    },
    steps: [{ command: "apply" }],
    expectations: [{ exitCode: 0, stdout: "applied\n", stderr: { kind: "empty" } }],
    destinationTree: [
      rootFile(ROOT_RUNTIME_TEXT),
      { kind: "file", path: SOURCE_RAW_PATH, content: SOURCE_RAW_TEXT },
      AICTORE_DIRECTORY,
      bindingsEntry({ entries: [{ source: SOURCE_RAW_PATH, destinations: [SOURCE_RAW_PATH] }] }),
    ],
  },
  {
    id: "raw-apply-creates-absent-target",
    concern: "raw-mode",
    title: "apply creates an absent declared raw target with the source bytes",
    provenance: {
      contract: [
        "SKILL.md / Exit contract: `apply` and `init` repair a declared region or raw target by creating it",
        "SKILL.md / Commands: `apply` and `init` create any region or raw target a binding declares",
      ],
      reference: [],
    },
    fixture: {
      sourceFiles: [{ path: SOURCE_RAW_PATH, content: SOURCE_RAW_TEXT }],
      clearance: RAW_CLEARANCE,
      destinationFiles: [{ path: "AGENTS.md", content: ROOT_RUNTIME_TEXT }],
      bindings: bindingsYaml({
        entries: [{ source: SOURCE_RAW_PATH, destinations: [SOURCE_RAW_PATH] }],
      }),
    },
    steps: [{ command: "apply" }],
    expectations: [
      { exitCode: 0, stdout: `applied; created: ${SOURCE_RAW_PATH}\n`, stderr: { kind: "empty" } },
    ],
    destinationTree: [
      rootFile(ROOT_RUNTIME_TEXT),
      { kind: "file", path: SOURCE_RAW_PATH, content: SOURCE_RAW_TEXT },
      AICTORE_DIRECTORY,
      bindingsEntry({ entries: [{ source: SOURCE_RAW_PATH, destinations: [SOURCE_RAW_PATH] }] }),
    ],
  },

  /* ---------------- merge mode ---------------- */
  {
    id: "merge-apply-merges-top-level-keys",
    concern: "merge-mode",
    title: "apply replaces a source top-level key and keeps the destination's own keys, comment and formatting",
    provenance: {
      contract: [
        "SKILL.md / Binding modes: merge — every source top-level key carries the source value and every destination-only key, comment, and formatting outside replaced or inserted keys is preserved by content",
      ],
      reference: [
        "The contract fixes the merged result by content, not by bytes — it says the destination's content is preserved 'by content, not byte-for-byte' — so the corpus compares the merged payload with its layout whitespace removed. The placement of an inserted key is therefore not over-constrained.",
      ],
    },
    fixture: {
      sourceFiles: [{ path: SOURCE_MERGE_SIMPLE_PATH, content: SOURCE_MERGE_SIMPLE_TEXT }],
      clearance: MERGE_CLEARANCE,
      destinationFiles: [
        { path: "AGENTS.md", content: ROOT_RUNTIME_TEXT },
        { path: SOURCE_MERGE_SIMPLE_PATH, content: DEST_MERGE_COMMENT_TEXT },
      ],
      bindings: bindingsYaml({
        entries: [{ source: SOURCE_MERGE_SIMPLE_PATH, destinations: [SOURCE_MERGE_SIMPLE_PATH] }],
      }),
    },
    steps: [{ command: "apply" }],
    expectations: [{ exitCode: 0, stdout: "applied\n", stderr: { kind: "empty" } }],
    destinationTree: [
      rootFile(ROOT_RUNTIME_TEXT),
      {
        kind: "jsonc",
        path: SOURCE_MERGE_SIMPLE_PATH,
        content: EXPECT_MERGE_TOP_LEVEL_TEXT,
        mustContain: ["// The destination keeps its own comment.", '"own": true'],
      },
      AICTORE_DIRECTORY,
      bindingsEntry({
        entries: [{ source: SOURCE_MERGE_SIMPLE_PATH, destinations: [SOURCE_MERGE_SIMPLE_PATH] }],
      }),
    ],
  },
  {
    id: "merge-apply-merges-mcp-by-server-name",
    concern: "merge-mode",
    title: "apply merges the mcp key by server name, keeping the destination's own server",
    provenance: {
      contract: [
        "SKILL.md / Binding modes: merge — except `mcp`, whose servers merge by name when both sides hold `mcp.servers` as an object: a same-named server entry is core-wins, every destination-only server survives, a source-only server is inserted",
      ],
      reference: [
        "The merged payload is compared by content, not by bytes, for the reason the first merge case records.",
      ],
    },
    fixture: {
      sourceFiles: [{ path: SOURCE_MERGE_PATH, content: SOURCE_MERGE_TEXT }],
      clearance: MERGE_CLEARANCE,
      destinationFiles: [
        { path: "AGENTS.md", content: ROOT_RUNTIME_TEXT },
        { path: SOURCE_MERGE_PATH, content: DEST_MERGE_MCP_TEXT },
      ],
      bindings: bindingsYaml({
        entries: [{ source: SOURCE_MERGE_PATH, destinations: [SOURCE_MERGE_PATH] }],
      }),
    },
    steps: [{ command: "apply" }],
    expectations: [{ exitCode: 0, stdout: "applied\n", stderr: { kind: "empty" } }],
    destinationTree: [
      rootFile(ROOT_RUNTIME_TEXT),
      {
        kind: "jsonc",
        path: SOURCE_MERGE_PATH,
        content: EXPECT_MERGE_MCP_TEXT,
        mustContain: [
          "// The destination keeps its own comment.",
          '"command": ["node", "local-server.js"]',
        ],
      },
      AICTORE_DIRECTORY,
      bindingsEntry({ entries: [{ source: SOURCE_MERGE_PATH, destinations: [SOURCE_MERGE_PATH] }] }),
    ],
  },
  {
    id: "merge-apply-retargets-qmd-index",
    concern: "merge-mode",
    title: "apply retargets the qmd server's --index argument to the destination folder's name",
    provenance: {
      contract: [
        "SKILL.md / Binding modes: merge — the `qmd` server's `--index` argument is the destination folder's name, on every mcp write path and in the comparison",
      ],
      reference: [
        "The merged payload is compared by content, not by bytes, for the reason the first merge case records.",
      ],
    },
    fixture: {
      sourceFiles: [{ path: SOURCE_MERGE_PATH, content: SOURCE_MERGE_TEXT }],
      clearance: MERGE_CLEARANCE,
      destinationFiles: [
        { path: "AGENTS.md", content: ROOT_RUNTIME_TEXT },
        {
          path: SOURCE_MERGE_PATH,
          content: DEST_MERGE_MCP_TEXT.replace('"--index", "ai-core"', '"--index", "stale-index"'),
        },
      ],
      bindings: bindingsYaml({
        entries: [{ source: SOURCE_MERGE_PATH, destinations: [SOURCE_MERGE_PATH] }],
      }),
    },
    steps: [{ command: "apply" }],
    expectations: [{ exitCode: 0, stdout: "applied\n", stderr: { kind: "empty" } }],
    destinationTree: [
      rootFile(ROOT_RUNTIME_TEXT),
      {
        kind: "jsonc",
        path: SOURCE_MERGE_PATH,
        content: EXPECT_MERGE_MCP_TEXT,
        mustContain: ['"--index", "project-under-test"'],
      },
      AICTORE_DIRECTORY,
      bindingsEntry({ entries: [{ source: SOURCE_MERGE_PATH, destinations: [SOURCE_MERGE_PATH] }] }),
    ],
  },
  {
    id: "merge-check-current",
    concern: "merge-mode",
    title: "check reports a merged destination that carries every source key as current",
    provenance: {
      contract: [
        "SKILL.md / Exit contract: exit 0 — every merge destination carries each source top-level key with the source value (extra destination-only keys and, for an object mcp.servers on both sides, extra destination-only servers allowed)",
      ],
      reference: [],
    },
    fixture: {
      sourceFiles: [{ path: SOURCE_MERGE_PATH, content: SOURCE_MERGE_TEXT }],
      clearance: MERGE_CLEARANCE,
      destinationFiles: [
        { path: "AGENTS.md", content: ROOT_RUNTIME_TEXT },
        { path: SOURCE_MERGE_PATH, content: EXPECT_MERGE_MCP_TEXT },
      ],
      bindings: bindingsYaml({
        entries: [{ source: SOURCE_MERGE_PATH, destinations: [SOURCE_MERGE_PATH] }],
      }),
    },
    steps: [{ command: "check" }],
    expectations: [{ exitCode: 0, stdout: "current\n", stderr: { kind: "empty" } }],
    destinationTree: [
      rootFile(ROOT_RUNTIME_TEXT),
      { kind: "file", path: SOURCE_MERGE_PATH, content: EXPECT_MERGE_MCP_TEXT },
      AICTORE_DIRECTORY,
      bindingsEntry({ entries: [{ source: SOURCE_MERGE_PATH, destinations: [SOURCE_MERGE_PATH] }] }),
    ],
  },
  {
    id: "merge-check-drift",
    concern: "merge-mode",
    title: "check reports a merge destination that does not carry a source key",
    provenance: {
      contract: ["SKILL.md / Exit contract: exit 1 — drift … raw/region/merge mismatch"],
      reference: ["The diagnostic word `merge drift` is reference behaviour."],
    },
    fixture: {
      sourceFiles: [{ path: SOURCE_MERGE_PATH, content: SOURCE_MERGE_TEXT }],
      clearance: MERGE_CLEARANCE,
      destinationFiles: [
        { path: "AGENTS.md", content: ROOT_RUNTIME_TEXT },
        { path: SOURCE_MERGE_PATH, content: DEST_MERGE_TEXT },
      ],
      bindings: bindingsYaml({
        entries: [{ source: SOURCE_MERGE_PATH, destinations: [SOURCE_MERGE_PATH] }],
      }),
    },
    steps: [{ command: "check" }],
    expectations: [{ exitCode: 1, stdout: "", stderr: { kind: "contains", value: ["merge drift"] } }],
    destinationTree: [
      rootFile(ROOT_RUNTIME_TEXT),
      { kind: "file", path: SOURCE_MERGE_PATH, content: DEST_MERGE_TEXT },
      AICTORE_DIRECTORY,
      bindingsEntry({ entries: [{ source: SOURCE_MERGE_PATH, destinations: [SOURCE_MERGE_PATH] }] }),
    ],
  },
  {
    id: "merge-missing-destination-is-drift",
    concern: "merge-mode",
    title: "apply reports a missing merge destination as drift and creates nothing",
    provenance: {
      contract: [
        "SKILL.md / Binding modes: merge — a missing merge destination is drift (exit 1); only a first `init --bind-cleared` creates a merge target",
        "SKILL.md / Exit contract: `check` reports an absent bound destination as drift and creates nothing",
      ],
      reference: ["The diagnostic word `missing destination` is reference behaviour."],
    },
    fixture: {
      sourceFiles: [{ path: SOURCE_MERGE_PATH, content: SOURCE_MERGE_TEXT }],
      clearance: MERGE_CLEARANCE,
      destinationFiles: [{ path: "AGENTS.md", content: ROOT_RUNTIME_TEXT }],
      bindings: bindingsYaml({
        entries: [{ source: SOURCE_MERGE_PATH, destinations: [SOURCE_MERGE_PATH] }],
      }),
    },
    steps: [{ command: "apply" }],
    expectations: [
      { exitCode: 1, stdout: "", stderr: { kind: "contains", value: ["missing destination"] } },
    ],
    destinationTree: [
      rootFile(ROOT_RUNTIME_TEXT),
      AICTORE_DIRECTORY,
      bindingsEntry({ entries: [{ source: SOURCE_MERGE_PATH, destinations: [SOURCE_MERGE_PATH] }] }),
    ],
  },

  /* ---------------- marker contract ---------------- */
  {
    id: "marker-markerless-source-body-is-core",
    concern: "marker-contract",
    title: "a markerless source's whole post-frontmatter body is its core",
    provenance: {
      contract: [
        "SKILL.md / Marker contract: a source with neither core nor project markers outside fenced code is markerless and its whole post-frontmatter body is the core",
      ],
      reference: [],
    },
    fixture: {
      sourceFiles: [{ path: SOURCE_REGION_PATH, content: SOURCE_REGION_TEXT }],
      clearance: REGION_CLEARANCE,
      destinationFiles: [
        { path: "AGENTS.md", content: ROOT_RUNTIME_TEXT },
        { path: SOURCE_REGION_PATH, content: DEST_REGION_MARKED_TEXT },
      ],
      bindings: bindingsYaml({
        entries: [{ source: SOURCE_REGION_PATH, destinations: [SOURCE_REGION_PATH] }],
      }),
    },
    steps: [{ command: "apply" }],
    expectations: [{ exitCode: 0, stdout: "applied\n", stderr: { kind: "empty" } }],
    destinationTree: [
      rootFile(ROOT_RUNTIME_TEXT),
      { kind: "file", path: SOURCE_REGION_PATH, content: EXPECT_REGION_SPLICED_TEXT },
      AICTORE_DIRECTORY,
      bindingsEntry({ entries: [{ source: SOURCE_REGION_PATH, destinations: [SOURCE_REGION_PATH] }] }),
    ],
  },
  {
    id: "marker-source-project-markers-without-core-pair",
    concern: "marker-contract",
    title: "a source carrying project markers without a core pair is malformed and fails closed",
    provenance: {
      contract: [
        "SKILL.md / Marker contract: a source carrying exact project marker lines without exactly one ordered core pair is malformed and fails with exit 2, so its project content is never read as core",
      ],
      reference: ["The diagnostic word `invalid source markers` is reference behaviour."],
    },
    fixture: {
      sourceFiles: [
        {
          path: SOURCE_REGION_PATH,
          content: [
            "---",
            "name: shared",
            "---",
            "",
            "<!-- project:begin -->",
            "Source project content.",
            "<!-- project:end -->",
            "",
          ].join("\n"),
        },
      ],
      clearance: REGION_CLEARANCE,
      destinationFiles: [
        { path: "AGENTS.md", content: ROOT_RUNTIME_TEXT },
        { path: SOURCE_REGION_PATH, content: DEST_REGION_MARKED_TEXT },
      ],
      bindings: bindingsYaml({
        entries: [{ source: SOURCE_REGION_PATH, destinations: [SOURCE_REGION_PATH] }],
      }),
    },
    steps: [{ command: "apply" }],
    expectations: [
      { exitCode: 2, stdout: "", stderr: { kind: "contains", value: ["invalid source markers"] } },
    ],
    destinationTree: [
      rootFile(ROOT_RUNTIME_TEXT),
      { kind: "file", path: SOURCE_REGION_PATH, content: DEST_REGION_MARKED_TEXT },
      AICTORE_DIRECTORY,
      bindingsEntry({ entries: [{ source: SOURCE_REGION_PATH, destinations: [SOURCE_REGION_PATH] }] }),
    ],
  },
  {
    id: "marker-source-reversed-core-pair",
    concern: "marker-contract",
    title: "a source whose core pair is reversed is malformed and fails closed",
    provenance: {
      contract: [
        "SKILL.md / Marker contract: if any exact source core marker line exists, the source must have exactly one ordered pair or the command fails with exit 2 rather than treating malformed markers as a markerless file",
      ],
      reference: ["The diagnostic word `invalid source markers` is reference behaviour."],
    },
    fixture: {
      sourceFiles: [
        {
          path: SOURCE_REGION_PATH,
          content: [
            "---",
            "name: shared",
            "---",
            "",
            "<!-- core:end -->",
            "Shared core line one.",
            "<!-- core:begin -->",
            "",
          ].join("\n"),
        },
      ],
      clearance: REGION_CLEARANCE,
      destinationFiles: [
        { path: "AGENTS.md", content: ROOT_RUNTIME_TEXT },
        { path: SOURCE_REGION_PATH, content: DEST_REGION_MARKED_TEXT },
      ],
      bindings: bindingsYaml({
        entries: [{ source: SOURCE_REGION_PATH, destinations: [SOURCE_REGION_PATH] }],
      }),
    },
    steps: [{ command: "apply" }],
    expectations: [
      { exitCode: 2, stdout: "", stderr: { kind: "contains", value: ["invalid source markers"] } },
    ],
    destinationTree: [
      rootFile(ROOT_RUNTIME_TEXT),
      { kind: "file", path: SOURCE_REGION_PATH, content: DEST_REGION_MARKED_TEXT },
      AICTORE_DIRECTORY,
      bindingsEntry({ entries: [{ source: SOURCE_REGION_PATH, destinations: [SOURCE_REGION_PATH] }] }),
    ],
  },
  {
    id: "marker-fenced-marker-literals-are-not-markers",
    concern: "marker-contract",
    title: "marker literals inside a fenced code block are ordinary text, so the source stays markerless",
    provenance: {
      contract: [
        "SKILL.md / Marker contract: a marker counts only as an exact line (ignoring surrounding whitespace) outside a fenced code block",
        "SKILL.md / Binding modes: fenced template/example marker literals remain ordinary source bytes",
        "SKILL.md / What I do: a destination-only frontmatter key keeps its exact bytes",
      ],
      reference: [
        "The source of this case defines only the `name` key, so the destination's own `description` and `version` keys keep their bytes; that is the reference's refresh rule applied to the contract's destination-only-key rule.",
      ],
    },
    fixture: {
      sourceFiles: [
        {
          path: SOURCE_REGION_PATH,
          content: [
            "---",
            "name: shared",
            "---",
            "",
            "```markdown",
            "<!-- core:begin -->",
            "<!-- core:end -->",
            "```",
            "",
            "Shared core line one.",
            "Shared core line two.",
            "",
          ].join("\n"),
        },
      ],
      clearance: REGION_CLEARANCE,
      destinationFiles: [
        { path: "AGENTS.md", content: ROOT_RUNTIME_TEXT },
        { path: SOURCE_REGION_PATH, content: DEST_REGION_MARKED_TEXT },
      ],
      bindings: bindingsYaml({
        entries: [{ source: SOURCE_REGION_PATH, destinations: [SOURCE_REGION_PATH] }],
      }),
    },
    steps: [{ command: "apply" }],
    expectations: [{ exitCode: 0, stdout: "applied\n", stderr: { kind: "empty" } }],
    destinationTree: [
      rootFile(ROOT_RUNTIME_TEXT),
      {
        kind: "file",
        path: SOURCE_REGION_PATH,
        content: [
          "---",
          "name: shared",
          "description: Destination description",
          "version: 1.0.0",
          "local-version: 1.0.0",
          "---",
          "",
          "<!-- core:begin -->",
          "",
          "```markdown",
          "<!-- core:begin -->",
          "<!-- core:end -->",
          "```",
          "",
          "Shared core line one.",
          "Shared core line two.",
          "<!-- core:end -->",
          "",
          "<!-- project:begin -->",
          "Destination project content.",
          "<!-- project:end -->",
          "",
        ].join("\n"),
      },
      AICTORE_DIRECTORY,
      bindingsEntry({ entries: [{ source: SOURCE_REGION_PATH, destinations: [SOURCE_REGION_PATH] }] }),
    ],
  },
  {
    id: "marker-check-ignores-project-region",
    concern: "marker-contract",
    title: "check ignores the project region's content and still reports the destination as current",
    provenance: {
      contract: [
        "SKILL.md / Marker contract: the project region is the destination-owned region; the tool never reads or writes it",
        "SKILL.md / Exit contract: exit 0 — every core region matches the pinned revision",
      ],
      reference: [],
    },
    fixture: {
      sourceFiles: [{ path: SOURCE_REGION_PATH, content: SOURCE_REGION_TEXT }],
      clearance: REGION_CLEARANCE,
      destinationFiles: [
        { path: "AGENTS.md", content: ROOT_RUNTIME_TEXT },
        {
          path: SOURCE_REGION_PATH,
          content: EXPECT_REGION_SPLICED_TEXT.replace(
            "Destination project content.",
            "Arbitrary local records the destination owns.",
          ),
        },
      ],
      bindings: bindingsYaml({
        entries: [{ source: SOURCE_REGION_PATH, destinations: [SOURCE_REGION_PATH] }],
      }),
    },
    steps: [{ command: "check" }],
    expectations: [{ exitCode: 0, stdout: "current\n", stderr: { kind: "empty" } }],
    destinationTree: [
      rootFile(ROOT_RUNTIME_TEXT),
      {
        kind: "file",
        path: SOURCE_REGION_PATH,
        content: EXPECT_REGION_SPLICED_TEXT.replace(
          "Destination project content.",
          "Arbitrary local records the destination owns.",
        ),
      },
      AICTORE_DIRECTORY,
      bindingsEntry({ entries: [{ source: SOURCE_REGION_PATH, destinations: [SOURCE_REGION_PATH] }] }),
    ],
  },

  {
    id: "marker-blocker-written",
    concern: "marker-contract",
    title: "the reconciliation blocker block is written into the root runtime file after one blank line",
    provenance: {
      contract: [
        "SKILL.md / Reconciliation blocker: while region-mode paths remain in `pending`, `check`, `apply`, and `init` ensure the destination root runtime file carries a marker-delimited blocker block",
        "SKILL.md / Reconciliation blocker: the block is appended after one blank line when absent and replaced in place on later runs",
      ],
      reference: [
        "The shipped words of the block are reference behaviour, not contract text; the corpus pins them so the artifact a destination receives is identical.",
      ],
    },
    fixture: {
      sourceFiles: [{ path: SOURCE_REGION_PATH, content: SOURCE_REGION_TEXT }],
      clearance: REGION_CLEARANCE,
      destinationFiles: [
        { path: "AGENTS.md", content: ROOT_RUNTIME_TEXT },
        { path: SOURCE_REGION_PATH, content: DEST_REGION_MARKED_TEXT },
      ],
      bindings: bindingsYaml({
        entries: [{ source: SOURCE_REGION_PATH, destinations: [SOURCE_REGION_PATH] }],
      }),
    },
    steps: [{ command: "init" }],
    expectations: [{ exitCode: 0, stdout: "initialized\n", stderr: { kind: "empty" } }],
    destinationTree: [
      rootFile(rootWithBlocker(ROOT_RUNTIME_TEXT)),
      { kind: "file", path: SOURCE_REGION_PATH, content: EXPECT_REGION_SPLICED_TEXT },
      AICTORE_DIRECTORY,
      RECONCILIATION_DIRECTORY,
      bindingsEntry({
        entries: [{ source: SOURCE_REGION_PATH, destinations: [SOURCE_REGION_PATH] }],
        pending: [SOURCE_REGION_PATH],
      }),
      reportEntry({
        entries: [{ destination: SOURCE_REGION_PATH, source: SOURCE_REGION_PATH, action: "refreshed" }],
      }),
    ],
  },
  {
    id: "marker-blocker-replaced-in-place",
    concern: "marker-contract",
    title: "an existing blocker block is replaced in place and the rest of the root file is preserved",
    provenance: {
      contract: [
        "SKILL.md / Reconciliation blocker: the block is appended after one blank line when absent and replaced in place on later runs; all other root content is preserved",
      ],
      reference: ["The shipped words of the block are reference behaviour, not contract text."],
    },
    fixture: {
      sourceFiles: [{ path: SOURCE_REGION_PATH, content: SOURCE_REGION_TEXT }],
      clearance: REGION_CLEARANCE,
      destinationFiles: [
        {
          path: "AGENTS.md",
          content: `${ROOT_RUNTIME_TEXT}\n${BLOCK_BEGIN}\nan outdated blocker body\n${BLOCK_END}\n`,
        },
        { path: SOURCE_REGION_PATH, content: EXPECT_REGION_SPLICED_TEXT },
      ],
      bindings: bindingsYaml({
        entries: [{ source: SOURCE_REGION_PATH, destinations: [SOURCE_REGION_PATH] }],
        pending: [SOURCE_REGION_PATH],
      }),
    },
    steps: [{ command: "apply" }],
    expectations: [{ exitCode: 0, stdout: "applied\n", stderr: { kind: "empty" } }],
    destinationTree: [
      rootFile(rootWithBlocker(ROOT_RUNTIME_TEXT)),
      { kind: "file", path: SOURCE_REGION_PATH, content: EXPECT_REGION_SPLICED_TEXT },
      AICTORE_DIRECTORY,
      bindingsEntry({
        entries: [{ source: SOURCE_REGION_PATH, destinations: [SOURCE_REGION_PATH] }],
        pending: [SOURCE_REGION_PATH],
      }),
    ],
  },
  {
    id: "marker-blocker-removed",
    concern: "marker-contract",
    title: "the blocker block and its blank separator are removed once pending is empty",
    provenance: {
      contract: [
        "SKILL.md / Reconciliation blocker: when `pending:` is empty, delete the entire blocker block (markers included); once `pending` is empty, `check` removes it",
      ],
      reference: ["The removal of the one-line blank separator alongside the block is reference behaviour."],
    },
    fixture: {
      sourceFiles: [{ path: SOURCE_REGION_PATH, content: SOURCE_REGION_TEXT }],
      clearance: REGION_CLEARANCE,
      destinationFiles: [
        { path: "AGENTS.md", content: rootWithBlocker(ROOT_RUNTIME_TEXT) },
        { path: SOURCE_REGION_PATH, content: EXPECT_REGION_SPLICED_TEXT },
      ],
      bindings: bindingsYaml({
        entries: [{ source: SOURCE_REGION_PATH, destinations: [SOURCE_REGION_PATH] }],
      }),
    },
    steps: [{ command: "check" }],
    expectations: [{ exitCode: 0, stdout: "current\n", stderr: { kind: "empty" } }],
    destinationTree: [
      rootFile(ROOT_RUNTIME_TEXT),
      { kind: "file", path: SOURCE_REGION_PATH, content: EXPECT_REGION_SPLICED_TEXT },
      AICTORE_DIRECTORY,
      bindingsEntry({ entries: [{ source: SOURCE_REGION_PATH, destinations: [SOURCE_REGION_PATH] }] }),
    ],
  },

  /* ---------------- bindings schema ---------------- */
  {
    id: "bindings-serialization-after-apply",
    concern: "bindings-schema",
    title: "apply writes the bindings document with the schema, the pinned revision, the mapping and an empty pending list",
    provenance: {
      contract: [
        "SKILL.md / Bindings schema: `schema: 1`; `core_revision` is the pinned 40-hex source revision or `null`; each `bindings` entry maps one `source` to one or more `destinations`; `pending` lists outstanding paths",
        "SKILL.md / Exit contract: `apply` … the revision pinned",
      ],
      reference: [
        "The YAML serialization of the document is not fixed by the contract, so the corpus compares the parsed document, not its bytes.",
      ],
    },
    fixture: {
      sourceFiles: [{ path: SOURCE_REGION_PATH, content: SOURCE_REGION_TEXT }],
      clearance: REGION_CLEARANCE,
      destinationFiles: [
        { path: "AGENTS.md", content: ROOT_RUNTIME_TEXT },
        { path: SOURCE_REGION_PATH, content: DEST_REGION_MARKED_TEXT },
      ],
      bindings: bindingsYaml({
        entries: [{ source: SOURCE_REGION_PATH, destinations: [SOURCE_REGION_PATH] }],
      }),
    },
    steps: [{ command: "apply" }],
    expectations: [{ exitCode: 0, stdout: "applied\n", stderr: { kind: "empty" } }],
    destinationTree: [
      rootFile(ROOT_RUNTIME_TEXT),
      { kind: "file", path: SOURCE_REGION_PATH, content: EXPECT_REGION_SPLICED_TEXT },
      AICTORE_DIRECTORY,
      bindingsEntry({ entries: [{ source: SOURCE_REGION_PATH, destinations: [SOURCE_REGION_PATH] }] }),
    ],
  },
  {
    id: "bindings-malformed-document",
    concern: "bindings-schema",
    title: "a malformed bindings document is rejected before any filesystem operation uses it",
    provenance: {
      contract: [
        "SKILL.md / Bindings schema: invalid persisted paths are rejected as malformed bindings (exit 2) before filesystem operations use them",
        "SKILL.md / Exit contract: exit 2 — malformed bindings",
      ],
      reference: ["The diagnostic word `invalid bindings` is reference behaviour."],
    },
    fixture: {
      sourceFiles: [{ path: SOURCE_REGION_PATH, content: SOURCE_REGION_TEXT }],
      clearance: REGION_CLEARANCE,
      destinationFiles: [
        { path: "AGENTS.md", content: ROOT_RUNTIME_TEXT },
        { path: SOURCE_REGION_PATH, content: DEST_REGION_MARKED_TEXT },
      ],
      bindings: "schema: 2\ncore_revision: null\nbindings: not-a-list\npending: []\n",
    },
    steps: [{ command: "check" }],
    expectations: [
      { exitCode: 2, stdout: "", stderr: { kind: "contains", value: ["invalid bindings"] } },
    ],
    destinationTree: [
      rootFile(ROOT_RUNTIME_TEXT),
      { kind: "file", path: SOURCE_REGION_PATH, content: DEST_REGION_MARKED_TEXT },
      AICTORE_DIRECTORY,
      { kind: "file", path: ".aicore/core.yaml", content: "schema: 2\ncore_revision: null\nbindings: not-a-list\npending: []\n" },
    ],
  },
  {
    id: "bindings-unsafe-persisted-path",
    concern: "bindings-schema",
    title: "a persisted path that is not a canonical safe relative POSIX path is rejected as malformed",
    provenance: {
      contract: [
        "SKILL.md / Bindings schema: source and destination paths must be canonical safe relative POSIX paths and must not contain NUL characters (no absolute paths, empty/`.`/`..` components, backslashes, or Windows drive/root prefixes)",
      ],
      reference: ["The diagnostic word `invalid bindings` is reference behaviour."],
    },
    fixture: {
      sourceFiles: [{ path: SOURCE_REGION_PATH, content: SOURCE_REGION_TEXT }],
      clearance: REGION_CLEARANCE,
      destinationFiles: [
        { path: "AGENTS.md", content: ROOT_RUNTIME_TEXT },
        { path: SOURCE_REGION_PATH, content: DEST_REGION_MARKED_TEXT },
      ],
      bindings: bindingsYaml({
        entries: [{ source: SOURCE_REGION_PATH, destinations: ["../escape.md"] }],
      }),
    },
    steps: [{ command: "check" }],
    expectations: [
      { exitCode: 2, stdout: "", stderr: { kind: "contains", value: ["invalid bindings"] } },
    ],
    destinationTree: [
      rootFile(ROOT_RUNTIME_TEXT),
      { kind: "file", path: SOURCE_REGION_PATH, content: DEST_REGION_MARKED_TEXT },
      AICTORE_DIRECTORY,
      {
        kind: "file",
        path: ".aicore/core.yaml",
        content: bindingsYaml({
          entries: [{ source: SOURCE_REGION_PATH, destinations: ["../escape.md"] }],
        }),
      },
    ],
  },
  {
    id: "bindings-persisted-mode-conflict",
    concern: "bindings-schema",
    title: "a persisted raw declaration whose source record is not raw fails closed",
    provenance: {
      contract: [
        "SKILL.md / Bindings schema: a persisted `mode` key is read as a declaration; a persisted `raw` declaration whose source record is not `raw` fails closed (exit 2), and the key is dropped on the next save",
      ],
      reference: [
        "The diagnostic wording is reference behaviour; the contract also notes that a conflicting hint cannot be removed by a synchronization that already fails preflight, so the document is left untouched.",
      ],
    },
    fixture: {
      sourceFiles: [{ path: SOURCE_REGION_PATH, content: SOURCE_REGION_TEXT }],
      clearance: REGION_CLEARANCE,
      destinationFiles: [
        { path: "AGENTS.md", content: ROOT_RUNTIME_TEXT },
        { path: SOURCE_REGION_PATH, content: DEST_REGION_MARKED_TEXT },
      ],
      bindings: bindingsYaml({
        entries: [{ source: SOURCE_REGION_PATH, destinations: [SOURCE_REGION_PATH], mode: "raw" }],
      }),
    },
    steps: [{ command: "apply" }],
    expectations: [
      {
        exitCode: 2,
        stdout: "",
        stderr: { kind: "contains", value: ["conflicts with source clearance mode"] },
      },
    ],
    destinationTree: [
      rootFile(ROOT_RUNTIME_TEXT),
      { kind: "file", path: SOURCE_REGION_PATH, content: DEST_REGION_MARKED_TEXT },
      AICTORE_DIRECTORY,
      {
        kind: "file",
        path: ".aicore/core.yaml",
        content: bindingsYaml({
          entries: [{ source: SOURCE_REGION_PATH, destinations: [SOURCE_REGION_PATH], mode: "raw" }],
        }),
      },
    ],
  },
  {
    id: "bindings-stale-non-region-pending-on-check",
    concern: "bindings-schema",
    title: "check reports a pending path whose binding is no longer region-bound and leaves the bindings unchanged",
    provenance: {
      contract: [
        "SKILL.md / Binding modes: raw — if a path remains in `pending` from a prior region binding after switching it to raw, `check` reports that stale state (exit 1) without treating it as destination reconciliation",
        "SKILL.md / Exit contract: `check` excludes it from the blocker, returns drift with an instruction to run `apply` or `init`, and leaves bindings unchanged",
      ],
      reference: ["The diagnostic wording is reference behaviour."],
    },
    fixture: {
      sourceFiles: [{ path: SOURCE_RAW_PATH, content: SOURCE_RAW_TEXT }],
      clearance: RAW_CLEARANCE,
      destinationFiles: [
        { path: "AGENTS.md", content: ROOT_RUNTIME_TEXT },
        { path: SOURCE_RAW_PATH, content: "stale raw payload\n" },
      ],
      bindings: bindingsYaml({
        entries: [{ source: SOURCE_RAW_PATH, destinations: [SOURCE_RAW_PATH] }],
        pending: [SOURCE_RAW_PATH],
      }),
    },
    steps: [{ command: "check" }],
    expectations: [
      {
        exitCode: 1,
        stdout: "",
        stderr: { kind: "contains", value: ["stale raw-bound pending paths"] },
      },
    ],
    destinationTree: [
      rootFile(ROOT_RUNTIME_TEXT),
      { kind: "file", path: SOURCE_RAW_PATH, content: "stale raw payload\n" },
      AICTORE_DIRECTORY,
      bindingsEntry({
        entries: [{ source: SOURCE_RAW_PATH, destinations: [SOURCE_RAW_PATH] }],
        pending: [SOURCE_RAW_PATH],
      }),
    ],
  },
  {
    id: "bindings-stale-non-region-pending-cleared-by-apply",
    concern: "bindings-schema",
    title: "apply clears the stale pending entry of a path whose binding is no longer region-bound",
    provenance: {
      contract: [
        "SKILL.md / Exit contract: if a path changes from region to a non-region mode (raw or merge) while listed in `pending`, `apply`/`init` remove that stale entry",
      ],
      reference: [],
    },
    fixture: {
      sourceFiles: [{ path: SOURCE_RAW_PATH, content: SOURCE_RAW_TEXT }],
      clearance: RAW_CLEARANCE,
      destinationFiles: [
        { path: "AGENTS.md", content: ROOT_RUNTIME_TEXT },
        { path: SOURCE_RAW_PATH, content: "stale raw payload\n" },
      ],
      bindings: bindingsYaml({
        entries: [{ source: SOURCE_RAW_PATH, destinations: [SOURCE_RAW_PATH] }],
        pending: [SOURCE_RAW_PATH],
      }),
    },
    steps: [{ command: "apply" }],
    expectations: [{ exitCode: 0, stdout: "applied\n", stderr: { kind: "empty" } }],
    destinationTree: [
      rootFile(ROOT_RUNTIME_TEXT),
      { kind: "file", path: SOURCE_RAW_PATH, content: SOURCE_RAW_TEXT },
      AICTORE_DIRECTORY,
      bindingsEntry({ entries: [{ source: SOURCE_RAW_PATH, destinations: [SOURCE_RAW_PATH] }] }),
    ],
  },

  /* ---------------- exit contract ---------------- */
  {
    id: "exit-zero-current",
    concern: "exit-contract",
    title: "a current destination exits 0 and prints `current`",
    provenance: {
      contract: ["SKILL.md / Exit contract: exit 0 for `check` … prints `current`"],
      reference: [],
    },
    fixture: {
      sourceFiles: [{ path: SOURCE_REGION_PATH, content: SOURCE_REGION_TEXT }],
      clearance: REGION_CLEARANCE,
      destinationFiles: [
        { path: "AGENTS.md", content: ROOT_RUNTIME_TEXT },
        { path: SOURCE_REGION_PATH, content: EXPECT_REGION_SPLICED_TEXT },
      ],
      bindings: bindingsYaml({
        entries: [{ source: SOURCE_REGION_PATH, destinations: [SOURCE_REGION_PATH] }],
      }),
    },
    steps: [{ command: "check" }],
    expectations: [{ exitCode: 0, stdout: "current\n", stderr: { kind: "empty" } }],
    destinationTree: [
      rootFile(ROOT_RUNTIME_TEXT),
      { kind: "file", path: SOURCE_REGION_PATH, content: EXPECT_REGION_SPLICED_TEXT },
      AICTORE_DIRECTORY,
      bindingsEntry({ entries: [{ source: SOURCE_REGION_PATH, destinations: [SOURCE_REGION_PATH] }] }),
    ],
  },
  {
    id: "exit-one-drift",
    concern: "exit-contract",
    title: "a stale pinned revision exits 1 and writes nothing",
    provenance: {
      contract: [
        "SKILL.md / Exit contract: exit 1 for `check` — drift: stale `core_revision`",
      ],
      reference: ["The diagnostic word `revision drift` is reference behaviour."],
    },
    fixture: {
      sourceFiles: [{ path: SOURCE_REGION_PATH, content: SOURCE_REGION_TEXT }],
      clearance: REGION_CLEARANCE,
      destinationFiles: [
        { path: "AGENTS.md", content: ROOT_RUNTIME_TEXT },
        { path: SOURCE_REGION_PATH, content: EXPECT_REGION_SPLICED_TEXT },
      ],
      bindings: bindingsYaml({
        revision: OTHER_REVISION,
        entries: [{ source: SOURCE_REGION_PATH, destinations: [SOURCE_REGION_PATH] }],
      }),
    },
    steps: [{ command: "check" }],
    expectations: [
      { exitCode: 1, stdout: "", stderr: { kind: "contains", value: ["revision drift"] } },
    ],
    destinationTree: [
      rootFile(ROOT_RUNTIME_TEXT),
      { kind: "file", path: SOURCE_REGION_PATH, content: EXPECT_REGION_SPLICED_TEXT },
      AICTORE_DIRECTORY,
      bindingsEntry({
        revision: OTHER_REVISION,
        entries: [{ source: SOURCE_REGION_PATH, destinations: [SOURCE_REGION_PATH] }],
      }),
    ],
  },
  {
    id: "exit-two-malformed-input",
    concern: "exit-contract",
    title: "a malformed input exits 2 and writes nothing",
    provenance: {
      contract: ["SKILL.md / Exit contract: exit 2 — malformed bindings/source markers"],
      reference: ["The diagnostic word `invalid bindings` is reference behaviour."],
    },
    fixture: {
      sourceFiles: [{ path: SOURCE_REGION_PATH, content: SOURCE_REGION_TEXT }],
      clearance: REGION_CLEARANCE,
      destinationFiles: [
        { path: "AGENTS.md", content: ROOT_RUNTIME_TEXT },
        { path: SOURCE_REGION_PATH, content: DEST_REGION_MARKED_TEXT },
      ],
      bindings: "schema: 1\nbindings:\n- source: shared.md\n  destinations: []\n",
    },
    steps: [{ command: "check" }],
    expectations: [
      { exitCode: 2, stdout: "", stderr: { kind: "contains", value: ["invalid bindings"] } },
    ],
    destinationTree: [
      rootFile(ROOT_RUNTIME_TEXT),
      { kind: "file", path: SOURCE_REGION_PATH, content: DEST_REGION_MARKED_TEXT },
      AICTORE_DIRECTORY,
      {
        kind: "file",
        path: ".aicore/core.yaml",
        content: "schema: 1\nbindings:\n- source: shared.md\n  destinations: []\n",
      },
    ],
  },
  {
    id: "exit-two-invalid-revision-argument",
    concern: "exit-contract",
    title: "an invalid --source-revision syntax exits 2 before the command starts",
    provenance: {
      contract: [
        "SKILL.md / Exit contract: argument-parser/CLI validation errors (including invalid `--source-revision` syntax) exit 2 before a command starts",
      ],
      reference: ["The diagnostic wording is reference behaviour."],
    },
    fixture: {
      sourceFiles: [{ path: SOURCE_REGION_PATH, content: SOURCE_REGION_TEXT }],
      clearance: REGION_CLEARANCE,
      destinationFiles: [
        { path: "AGENTS.md", content: ROOT_RUNTIME_TEXT },
        { path: SOURCE_REGION_PATH, content: EXPECT_REGION_SPLICED_TEXT },
      ],
      bindings: bindingsYaml({
        entries: [{ source: SOURCE_REGION_PATH, destinations: [SOURCE_REGION_PATH] }],
      }),
    },
    steps: [{ command: "check", revisionOverride: "not-a-revision" }],
    expectations: [
      {
        exitCode: 2,
        stdout: "",
        stderr: { kind: "contains", value: ["40-character lowercase hex"] },
      },
    ],
    destinationTree: [
      rootFile(ROOT_RUNTIME_TEXT),
      { kind: "file", path: SOURCE_REGION_PATH, content: EXPECT_REGION_SPLICED_TEXT },
      AICTORE_DIRECTORY,
      bindingsEntry({ entries: [{ source: SOURCE_REGION_PATH, destinations: [SOURCE_REGION_PATH] }] }),
    ],
  },
  {
    id: "exit-zero-applied-names-created-target",
    concern: "exit-contract",
    title: "an update that recreates a target exits 0 and names the created path",
    provenance: {
      contract: [
        "SKILL.md / Exit contract: exit 0 for `apply` … prints `applied`, or `applied; created: <path>[, <path>]` when it recreated absent targets",
      ],
      reference: [],
    },
    fixture: {
      sourceFiles: [{ path: SOURCE_RAW_PATH, content: SOURCE_RAW_TEXT }],
      clearance: RAW_CLEARANCE,
      destinationFiles: [{ path: "AGENTS.md", content: ROOT_RUNTIME_TEXT }],
      bindings: bindingsYaml({
        entries: [{ source: SOURCE_RAW_PATH, destinations: [SOURCE_RAW_PATH] }],
      }),
    },
    steps: [{ command: "apply" }],
    expectations: [
      { exitCode: 0, stdout: `applied; created: ${SOURCE_RAW_PATH}\n`, stderr: { kind: "empty" } },
    ],
    destinationTree: [
      rootFile(ROOT_RUNTIME_TEXT),
      { kind: "file", path: SOURCE_RAW_PATH, content: SOURCE_RAW_TEXT },
      AICTORE_DIRECTORY,
      bindingsEntry({ entries: [{ source: SOURCE_RAW_PATH, destinations: [SOURCE_RAW_PATH] }] }),
    ],
  },

  /* ---------------- safety refusals ---------------- */
  {
    id: "safety-symlinked-write-target",
    concern: "safety-refusals",
    title: "a symlinked write target is rejected before any read or write",
    provenance: {
      contract: [
        "SKILL.md / What I do: before mutation, write targets must be regular files: a symlinked bindings or payload/root/report target is rejected before any read or write",
        "SKILL.md / Exit contract: all commands validate bindings and preflight resolved write targets (including symlinks) before mutation",
      ],
      reference: ["The diagnostic wording is reference behaviour."],
    },
    fixture: {
      sourceFiles: [{ path: SOURCE_REGION_PATH, content: SOURCE_REGION_TEXT }],
      clearance: REGION_CLEARANCE,
      destinationFiles: [
        { path: "AGENTS.md", content: ROOT_RUNTIME_TEXT },
        { path: "elsewhere.md", content: "an unrelated file\n" },
      ],
      destinationLinks: [{ path: SOURCE_REGION_PATH, target: "elsewhere.md" }],
      bindings: bindingsYaml({
        entries: [{ source: SOURCE_REGION_PATH, destinations: [SOURCE_REGION_PATH] }],
      }),
    },
    steps: [{ command: "apply" }],
    expectations: [
      {
        exitCode: 2,
        stdout: "",
        stderr: { kind: "contains", value: ["invalid write target", "symbolic link"] },
      },
    ],
    destinationTree: [
      rootFile(ROOT_RUNTIME_TEXT),
      { kind: "file", path: "elsewhere.md", content: "an unrelated file\n" },
      { kind: "symlink", path: SOURCE_REGION_PATH, target: "elsewhere.md" },
      AICTORE_DIRECTORY,
      bindingsEntry({ entries: [{ source: SOURCE_REGION_PATH, destinations: [SOURCE_REGION_PATH] }] }),
    ],
  },
  {
    id: "safety-non-regular-write-target",
    concern: "safety-refusals",
    title: "a non-regular write target is rejected before any mutation",
    provenance: {
      contract: [
        "SKILL.md / What I do: an existing non-regular target is rejected",
        "SKILL.md / Exit contract: exit 2 — unsafe write targets",
      ],
      reference: ["The diagnostic wording is reference behaviour."],
    },
    fixture: {
      sourceFiles: [{ path: SOURCE_REGION_PATH, content: SOURCE_REGION_TEXT }],
      clearance: REGION_CLEARANCE,
      destinationFiles: [{ path: "AGENTS.md", content: ROOT_RUNTIME_TEXT }],
      destinationDirectories: [SOURCE_REGION_PATH],
      bindings: bindingsYaml({
        entries: [{ source: SOURCE_REGION_PATH, destinations: [SOURCE_REGION_PATH] }],
      }),
    },
    steps: [{ command: "apply" }],
    expectations: [
      {
        exitCode: 2,
        stdout: "",
        stderr: { kind: "contains", value: ["invalid write target", "not a regular file"] },
      },
    ],
    destinationTree: [
      rootFile(ROOT_RUNTIME_TEXT),
      { kind: "directory", path: SOURCE_REGION_PATH },
      AICTORE_DIRECTORY,
      bindingsEntry({ entries: [{ source: SOURCE_REGION_PATH, destinations: [SOURCE_REGION_PATH] }] }),
    ],
  },
  {
    id: "safety-overlapping-roots",
    concern: "safety-refusals",
    title: "overlapping source and destination roots are rejected",
    provenance: {
      contract: ["SKILL.md / Exit contract: exit 2 — overlapping roots"],
      reference: ["The diagnostic wording is reference behaviour."],
    },
    fixture: {
      sourceFiles: [{ path: SOURCE_REGION_PATH, content: SOURCE_REGION_TEXT }],
      clearance: REGION_CLEARANCE,
      destinationFiles: [
        { path: "AGENTS.md", content: ROOT_RUNTIME_TEXT },
        { path: SOURCE_REGION_PATH, content: DEST_REGION_MARKED_TEXT },
      ],
      nestedSourceInsideDestination: true,
      bindings: bindingsYaml({
        entries: [{ source: SOURCE_REGION_PATH, destinations: [SOURCE_REGION_PATH] }],
      }),
    },
    steps: [{ command: "apply" }],
    expectations: [
      {
        exitCode: 2,
        stdout: "",
        stderr: { kind: "contains", value: ["invalid write target", "overlap"] },
      },
    ],
    destinationTree: [
      rootFile(ROOT_RUNTIME_TEXT),
      { kind: "file", path: SOURCE_REGION_PATH, content: DEST_REGION_MARKED_TEXT },
      { kind: "directory", path: "source" },
      { kind: "file", path: "source/shared.md", content: SOURCE_REGION_TEXT },
      { kind: "file", path: "source/distribution-clearance.json", content: REGION_CLEARANCE },
      AICTORE_DIRECTORY,
      bindingsEntry({ entries: [{ source: SOURCE_REGION_PATH, destinations: [SOURCE_REGION_PATH] }] }),
    ],
  },
  {
    id: "safety-write-target-inside-source-tree",
    concern: "safety-refusals",
    title: "a write target that resolves inside the source tree is rejected",
    provenance: {
      contract: [
        "SKILL.md / Exit contract: exit 2 — unsafe write targets (including source-inode aliases)",
        "SKILL.md / Troubleshooting: a write target resolves inside the source … the command fails before writing",
      ],
      reference: ["The diagnostic wording is reference behaviour."],
    },
    fixture: {
      sourceFiles: [{ path: SOURCE_REGION_PATH, content: SOURCE_REGION_TEXT }],
      clearance: REGION_CLEARANCE,
      destinationFiles: [{ path: "AGENTS.md", content: ROOT_RUNTIME_TEXT }],
      destinationLinks: [{ path: "into-source", target: "../source" }],
      bindings: bindingsYaml({
        entries: [{ source: SOURCE_REGION_PATH, destinations: ["into-source/shared.md"] }],
      }),
    },
    steps: [{ command: "apply" }],
    expectations: [
      {
        exitCode: 2,
        stdout: "",
        stderr: { kind: "contains", value: ["invalid write target", "resolves inside source tree"] },
      },
    ],
    destinationTree: [
      rootFile(ROOT_RUNTIME_TEXT),
      { kind: "symlink", path: "into-source", target: "../source" },
      AICTORE_DIRECTORY,
      bindingsEntry({
        entries: [{ source: SOURCE_REGION_PATH, destinations: ["into-source/shared.md"] }],
      }),
    ],
  },
  {
    id: "safety-write-target-shares-source-inode",
    concern: "safety-refusals",
    title: "a write target that shares an inode with a source file is rejected",
    provenance: {
      contract: [
        "SKILL.md / What I do: existing output-file device/inode identities are checked against regular files under the source tree, so hard links cannot mutate source files",
        "SKILL.md / Troubleshooting: a write target shares an inode with a source-tree file (including a hard link) … the command fails before writing",
      ],
      reference: ["The diagnostic wording is reference behaviour."],
    },
    fixture: {
      sourceFiles: [{ path: SOURCE_REGION_PATH, content: SOURCE_REGION_TEXT }],
      clearance: REGION_CLEARANCE,
      destinationFiles: [{ path: "AGENTS.md", content: ROOT_RUNTIME_TEXT }],
      destinationHardLinks: [{ path: SOURCE_REGION_PATH, target: "../source/shared.md" }],
      bindings: bindingsYaml({
        entries: [{ source: SOURCE_REGION_PATH, destinations: [SOURCE_REGION_PATH] }],
      }),
    },
    steps: [{ command: "apply" }],
    expectations: [
      {
        exitCode: 2,
        stdout: "",
        stderr: { kind: "contains", value: ["invalid write target", "source-tree file inode"] },
      },
    ],
    destinationTree: [
      rootFile(ROOT_RUNTIME_TEXT),
      { kind: "file", path: SOURCE_REGION_PATH, content: SOURCE_REGION_TEXT },
      AICTORE_DIRECTORY,
      bindingsEntry({ entries: [{ source: SOURCE_REGION_PATH, destinations: [SOURCE_REGION_PATH] }] }),
    ],
    sourceTree: [
      { kind: "file", path: SOURCE_REGION_PATH, content: SOURCE_REGION_TEXT },
      { kind: "file", path: "distribution-clearance.json", content: REGION_CLEARANCE },
    ],
  },
  {
    id: "safety-two-write-targets-share-an-inode",
    concern: "safety-refusals",
    title: "two distinct write targets that share an inode are rejected",
    provenance: {
      contract: [
        "SKILL.md / What I do: distinct output paths that resolve to the same target are rejected",
        "SKILL.md / Troubleshooting: distinct output paths resolve to one target … the command fails before writing",
      ],
      reference: ["The diagnostic wording is reference behaviour."],
    },
    fixture: {
      sourceFiles: [{ path: SOURCE_REGION_PATH, content: SOURCE_REGION_TEXT }],
      clearance: REGION_CLEARANCE,
      destinationFiles: [
        { path: "AGENTS.md", content: ROOT_RUNTIME_TEXT },
        { path: "first.md", content: "one target\n" },
      ],
      destinationHardLinks: [{ path: "second.md", target: "first.md" }],
      bindings: bindingsYaml({
        entries: [
          { source: SOURCE_REGION_PATH, destinations: ["first.md"] },
          { source: SOURCE_REGION_PATH, destinations: ["second.md"] },
        ],
      }),
    },
    steps: [{ command: "apply" }],
    expectations: [
      {
        exitCode: 2,
        stdout: "",
        stderr: { kind: "contains", value: ["invalid write target", "share a filesystem inode"] },
      },
    ],
    destinationTree: [
      rootFile(ROOT_RUNTIME_TEXT),
      { kind: "file", path: "first.md", content: "one target\n" },
      { kind: "file", path: "second.md", content: "one target\n" },
      AICTORE_DIRECTORY,
      bindingsEntry({
        entries: [
          { source: SOURCE_REGION_PATH, destinations: ["first.md"] },
          { source: SOURCE_REGION_PATH, destinations: ["second.md"] },
        ],
      }),
    ],
  },
  {
    id: "safety-write-target-escapes-destination-root",
    concern: "safety-refusals",
    title: "a write target that resolves outside the destination root is rejected",
    provenance: {
      contract: [
        "SKILL.md / Exit contract: exit 2 — unsafe write targets",
        "SKILL.md / Troubleshooting: a root or payload target escapes the destination … the command fails before writing",
      ],
      reference: ["The diagnostic wording is reference behaviour."],
    },
    fixture: {
      sourceFiles: [{ path: SOURCE_REGION_PATH, content: SOURCE_REGION_TEXT }],
      clearance: REGION_CLEARANCE,
      destinationFiles: [{ path: "AGENTS.md", content: ROOT_RUNTIME_TEXT }],
      destinationLinks: [{ path: "outside", target: ".." }],
      bindings: bindingsYaml({
        entries: [{ source: SOURCE_REGION_PATH, destinations: ["outside/escape.md"] }],
      }),
    },
    steps: [{ command: "apply" }],
    expectations: [
      {
        exitCode: 2,
        stdout: "",
        stderr: { kind: "contains", value: ["invalid write target", "escapes destination root"] },
      },
    ],
    destinationTree: [
      rootFile(ROOT_RUNTIME_TEXT),
      { kind: "symlink", path: "outside", target: ".." },
      AICTORE_DIRECTORY,
      bindingsEntry({
        entries: [{ source: SOURCE_REGION_PATH, destinations: ["outside/escape.md"] }],
      }),
    ],
  },
  {
    id: "safety-malformed-destination-markers",
    concern: "safety-refusals",
    title: "a destination with a duplicated core marker pair is malformed input and is rejected",
    provenance: {
      contract: [
        "SKILL.md / Marker contract: each region-mode destination must carry exactly one `core` marker pair, BEGIN before END; a missing, duplicated, or reversed destination pair is malformed input",
        "SKILL.md / Exit contract: exit 2 — invalid or unreadable region-destination markers",
      ],
      reference: ["The diagnostic wording is reference behaviour."],
    },
    fixture: {
      sourceFiles: [{ path: SOURCE_REGION_PATH, content: SOURCE_REGION_TEXT }],
      clearance: REGION_CLEARANCE,
      destinationFiles: [
        { path: "AGENTS.md", content: ROOT_RUNTIME_TEXT },
        {
          path: SOURCE_REGION_PATH,
          content: [
            "<!-- core:begin -->",
            "Old shared body.",
            "<!-- core:end -->",
            "<!-- core:begin -->",
            "A second core region.",
            "<!-- core:end -->",
            "",
          ].join("\n"),
        },
      ],
      bindings: bindingsYaml({
        entries: [{ source: SOURCE_REGION_PATH, destinations: [SOURCE_REGION_PATH] }],
      }),
    },
    steps: [{ command: "apply" }],
    expectations: [
      {
        exitCode: 2,
        stdout: "",
        stderr: { kind: "contains", value: ["invalid destination markers"] },
      },
    ],
    destinationTree: [
      rootFile(ROOT_RUNTIME_TEXT),
      {
        kind: "file",
        path: SOURCE_REGION_PATH,
        content: [
          "<!-- core:begin -->",
          "Old shared body.",
          "<!-- core:end -->",
          "<!-- core:begin -->",
          "A second core region.",
          "<!-- core:end -->",
          "",
        ].join("\n"),
      },
      AICTORE_DIRECTORY,
      bindingsEntry({ entries: [{ source: SOURCE_REGION_PATH, destinations: [SOURCE_REGION_PATH] }] }),
    ],
  },
  {
    id: "safety-malformed-clearance",
    concern: "safety-refusals",
    title: "a malformed clearance registry is rejected and produces no payload, report, bindings or blocker write",
    provenance: {
      contract: [
        "SKILL.md / Exit contract: exit 2 — `distribution-clearance.json` present but malformed",
        "SKILL.md / Exit contract: the clearance gate runs before any bound-source payload read or destination mutation; an uncleared source never produces a payload, report, bindings, or blocker write",
      ],
      reference: ["The diagnostic wording is reference behaviour."],
    },
    fixture: {
      sourceFiles: [{ path: SOURCE_REGION_PATH, content: SOURCE_REGION_TEXT }],
      clearance: "{ this is not json",
      destinationFiles: [
        { path: "AGENTS.md", content: ROOT_RUNTIME_TEXT },
        { path: SOURCE_REGION_PATH, content: DEST_REGION_MARKED_TEXT },
      ],
      bindings: bindingsYaml({
        entries: [{ source: SOURCE_REGION_PATH, destinations: [SOURCE_REGION_PATH] }],
      }),
    },
    steps: [{ command: "apply" }],
    expectations: [
      {
        exitCode: 2,
        stdout: "",
        stderr: { kind: "contains", value: ["invalid clearance file"] },
      },
    ],
    destinationTree: [
      rootFile(ROOT_RUNTIME_TEXT),
      { kind: "file", path: SOURCE_REGION_PATH, content: DEST_REGION_MARKED_TEXT },
      AICTORE_DIRECTORY,
      bindingsEntry({ entries: [{ source: SOURCE_REGION_PATH, destinations: [SOURCE_REGION_PATH] }] }),
    ],
  },
  {
    id: "safety-revision-mismatch",
    concern: "safety-refusals",
    title: "a bindings revision that does not match the requested source revision is drift",
    provenance: {
      contract: ["SKILL.md / Exit contract: exit 1 for `check` — drift: stale `core_revision`"],
      reference: ["The diagnostic wording is reference behaviour."],
    },
    fixture: {
      sourceFiles: [{ path: SOURCE_REGION_PATH, content: SOURCE_REGION_TEXT }],
      clearance: REGION_CLEARANCE,
      destinationFiles: [
        { path: "AGENTS.md", content: ROOT_RUNTIME_TEXT },
        { path: SOURCE_REGION_PATH, content: EXPECT_REGION_SPLICED_TEXT },
      ],
      bindings: bindingsYaml({
        revision: OTHER_REVISION,
        entries: [{ source: SOURCE_REGION_PATH, destinations: [SOURCE_REGION_PATH] }],
      }),
    },
    steps: [{ command: "check" }],
    expectations: [
      { exitCode: 1, stdout: "", stderr: { kind: "contains", value: ["revision drift"] } },
    ],
    destinationTree: [
      rootFile(ROOT_RUNTIME_TEXT),
      { kind: "file", path: SOURCE_REGION_PATH, content: EXPECT_REGION_SPLICED_TEXT },
      AICTORE_DIRECTORY,
      bindingsEntry({
        revision: OTHER_REVISION,
        entries: [{ source: SOURCE_REGION_PATH, destinations: [SOURCE_REGION_PATH] }],
      }),
    ],
  },
  {
    id: "safety-missing-source",
    concern: "safety-refusals",
    title: "a bound source that is absent from the source tree is drift",
    provenance: {
      contract: ["SKILL.md / Exit contract: exit 1 — drift: missing/unreadable source"],
      reference: ["The diagnostic word `missing source` is reference behaviour."],
    },
    fixture: {
      clearance: REGION_CLEARANCE,
      destinationFiles: [
        { path: "AGENTS.md", content: ROOT_RUNTIME_TEXT },
        { path: SOURCE_REGION_PATH, content: EXPECT_REGION_SPLICED_TEXT },
      ],
      bindings: bindingsYaml({
        entries: [{ source: SOURCE_REGION_PATH, destinations: [SOURCE_REGION_PATH] }],
      }),
    },
    steps: [{ command: "apply" }],
    expectations: [
      { exitCode: 1, stdout: "", stderr: { kind: "contains", value: ["missing source"] } },
    ],
    destinationTree: [
      rootFile(ROOT_RUNTIME_TEXT),
      { kind: "file", path: SOURCE_REGION_PATH, content: EXPECT_REGION_SPLICED_TEXT },
      AICTORE_DIRECTORY,
      bindingsEntry({ entries: [{ source: SOURCE_REGION_PATH, destinations: [SOURCE_REGION_PATH] }] }),
    ],
    sourceTree: [{ kind: "file", path: "distribution-clearance.json", content: REGION_CLEARANCE }],
  },
  {
    id: "safety-missing-destination",
    concern: "safety-refusals",
    title: "check reports an absent bound destination as drift and creates nothing",
    provenance: {
      contract: [
        "SKILL.md / Exit contract: `check` reports an absent bound destination as drift and creates nothing",
        "SKILL.md / Exit contract: exit 1 for `check` — drift: missing destination",
      ],
      reference: ["The diagnostic word `missing destination` is reference behaviour."],
    },
    fixture: {
      sourceFiles: [{ path: SOURCE_REGION_PATH, content: SOURCE_REGION_TEXT }],
      clearance: REGION_CLEARANCE,
      destinationFiles: [{ path: "AGENTS.md", content: ROOT_RUNTIME_TEXT }],
      bindings: bindingsYaml({
        entries: [{ source: SOURCE_REGION_PATH, destinations: [SOURCE_REGION_PATH] }],
      }),
    },
    steps: [{ command: "check" }],
    expectations: [
      { exitCode: 1, stdout: "", stderr: { kind: "contains", value: ["missing destination"] } },
    ],
    destinationTree: [
      rootFile(ROOT_RUNTIME_TEXT),
      AICTORE_DIRECTORY,
      bindingsEntry({ entries: [{ source: SOURCE_REGION_PATH, destinations: [SOURCE_REGION_PATH] }] }),
    ],
  },

  /* ---------------- idempotence ---------------- */
  {
    id: "idempotence-apply-twice",
    concern: "idempotence",
    title: "applying twice leaves the destination exactly as the first application left it",
    provenance: {
      contract: [
        "SKILL.md / Exit contract: `apply` … every region spliced or created / raw file copied / merge document written and the revision pinned",
        "SKILL.md / What I do: the source is read-only; the only writes are the destination files, a reconciliation report, the bindings file, and the destination root runtime file's reconciliation blocker",
      ],
      reference: [],
    },
    fixture: {
      sourceFiles: [
        { path: SOURCE_REGION_PATH, content: SOURCE_REGION_TEXT },
        { path: SOURCE_RAW_PATH, content: SOURCE_RAW_TEXT },
      ],
      clearance: clearanceJson({
        [SOURCE_REGION_PATH]: { mode: "region" },
        [SOURCE_RAW_PATH]: { mode: "raw" },
      }),
      destinationFiles: [
        { path: "AGENTS.md", content: ROOT_RUNTIME_TEXT },
        { path: SOURCE_REGION_PATH, content: DEST_REGION_MARKED_TEXT },
        { path: SOURCE_RAW_PATH, content: "stale raw payload\n" },
      ],
      bindings: bindingsYaml({
        entries: [
          { source: SOURCE_REGION_PATH, destinations: [SOURCE_REGION_PATH] },
          { source: SOURCE_RAW_PATH, destinations: [SOURCE_RAW_PATH] },
        ],
      }),
    },
    steps: [{ command: "apply" }, { command: "apply" }],
    expectations: [
      { exitCode: 0, stdout: "applied\n", stderr: { kind: "empty" } },
      { exitCode: 0, stdout: "applied\n", stderr: { kind: "empty" } },
    ],
    destinationTree: [
      rootFile(ROOT_RUNTIME_TEXT),
      { kind: "file", path: SOURCE_REGION_PATH, content: EXPECT_REGION_SPLICED_TEXT },
      { kind: "file", path: SOURCE_RAW_PATH, content: SOURCE_RAW_TEXT },
      AICTORE_DIRECTORY,
      bindingsEntry({
        entries: [
          { source: SOURCE_REGION_PATH, destinations: [SOURCE_REGION_PATH] },
          { source: SOURCE_RAW_PATH, destinations: [SOURCE_RAW_PATH] },
        ],
      }),
    ],
  },
  {
    id: "idempotence-init-enroll-twice",
    concern: "idempotence",
    title: "enrolling twice leaves the destination exactly as the first enrollment left it",
    provenance: {
      contract: [
        "SKILL.md / Commands: `init --bind SOURCE=DESTINATION` is repeatable and idempotent for an identical mapping",
        "SKILL.md / Commands: with `--bind-cleared`, an absent bindings file is initialized from an empty routing document",
      ],
      reference: [],
    },
    fixture: {
      sourceFiles: [{ path: SOURCE_REGION_PATH, content: SOURCE_REGION_TEXT }],
      clearance: REGION_CLEARANCE,
      destinationFiles: [{ path: "AGENTS.md", content: ROOT_RUNTIME_TEXT }],
      bindings: null,
    },
    steps: [{ command: "init", bindCleared: true }, { command: "init", bindCleared: true }],
    expectations: [
      { exitCode: 0, stdout: "initialized\n", stderr: { kind: "empty" } },
      { exitCode: 0, stdout: "initialized\n", stderr: { kind: "empty" } },
    ],
    destinationTree: [
      blockerEntry(ROOT_RUNTIME_TEXT),
      { kind: "file", path: SOURCE_REGION_PATH, content: EXPECT_REGION_CREATED_TEXT },
      AICTORE_DIRECTORY,
      RECONCILIATION_DIRECTORY,
      bindingsEntry({
        entries: [{ source: SOURCE_REGION_PATH, destinations: [SOURCE_REGION_PATH] }],
        pending: [SOURCE_REGION_PATH],
      }),
      reportEntry({
        entries: [{ destination: SOURCE_REGION_PATH, source: SOURCE_REGION_PATH, action: "initialized" }],
      }),
    ],
  },

  /* ---------------- binding declarations, root role, clearance integrity ---------------- */
  ...BINDING_DECLARATION_CASES,
  ...ROOT_ROLE_CASES,
  ...CLEARANCE_INTEGRITY_CASES,
];

/** Return the cases of one behavioural concern, in corpus order. */
export function casesFor(concern: ParityCase["concern"]): readonly ParityCase[] {
  return CORPUS.filter((entry) => entry.concern === concern);
}
