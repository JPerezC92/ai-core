/**
 * The destination-root concern: the `root:` role and the `--root` override.
 *
 * A source registry entry may carry `role: root`, which makes it the
 * destination's instruction root rather than a file mirroring its own path. The
 * destination root is then detected from the destination's instruction files, or
 * named explicitly with `--root` when the destination holds none.
 *
 * The fixture's source is `AGENTS.md` while the destination's root is
 * `CLAUDE.md`, so the two mappings are distinguishable: an engine that mirrors
 * the source path instead of mapping it to the detected root writes the wrong
 * file, and one that ignores `--root` refuses a destination it could enroll.
 */

import { CONTRACT_BLOCK_FACTS, BLOCK_BEGIN, BLOCK_END } from "../blocker.ts";
import { REVISION } from "../fixtures.ts";
import type { ParityCase, TreeEntry } from "../types.ts";

const ROOT_SOURCE_PATH = "AGENTS.md";
const DETECTED_ROOT_PATH = "CLAUDE.md";
const OVERRIDDEN_ROOT_PATH = "CLAUDE.md";
const README_PATH = "README.md";

const ROOT_SOURCE_TEXT = [
  "---",
  "name: agents",
  "description: Synthetic destination-root fixture",
  "version: 1.0.0",
  "---",
  "",
  "Agents core line one.",
  "Agents core line two.",
  "",
].join("\n");

/** The bytes `init` creates for an absent destination root. */
const ROOT_CREATED_TEXT = [
  "---",
  "name: agents",
  "description: Synthetic destination-root fixture",
  "version: 1.0.0",
  "---",
  "<!-- core:begin -->",
  "",
  "Agents core line one.",
  "Agents core line two.",
  "<!-- core:end -->",
  "",
  "<!-- project:begin -->",
  "<!-- project:end -->",
  "",
].join("\n");

const DESTINATION_ROOT_MARKERLESS_TEXT = "Destination runtime notes before enrollment.\n";

/** The bytes `init` produces for a markerless destination root. */
const ROOT_ENROLLED_TEXT = [
  "---",
  "name: agents",
  "description: Synthetic destination-root fixture",
  "version: 1.0.0",
  "---",
  "<!-- core:begin -->",
  "",
  "Agents core line one.",
  "Agents core line two.",
  "<!-- core:end -->",
  "",
  "<!-- project:begin -->",
  "Destination runtime notes before enrollment.",
  "<!-- project:end -->",
  "",
].join("\n");

const README_TEXT = "# Project readme\n\nThis destination holds no instruction root today.\n";

const ROOT_CLEARANCE_TEXT = [
  "{",
  '  "schema": 1,',
  '  "cleared": {',
  '    "AGENTS.md": {',
  '      "mode": "region",',
  '      "role": "root"',
  "    }",
  "  }",
  "}",
  "",
].join("\n");

const AICORE_DIRECTORY: TreeEntry = { kind: "directory", path: ".aicore" };
const RECONCILIATION_DIRECTORY: TreeEntry = {
  kind: "directory",
  path: ".aicore/reconciliation",
};

/**
 * The destination root runtime file after the blocker was appended to it.
 *
 * The root role makes the source the destination root, so the root file is the
 * payload itself: its created bytes, one blank separator line, then the block.
 */
function rootWithBlocker(content: string): TreeEntry {
  return {
    kind: "blocker",
    path: DETECTED_ROOT_PATH,
    prefix: `${content.endsWith("\n") ? content : `${content}\n`}\n${BLOCK_BEGIN}\n`,
    suffix: `\n${BLOCK_END}\n`,
    bodyContains: CONTRACT_BLOCK_FACTS,
  };
}

/** The destination root file a completed enrollment leaves behind. */
function rootDestinationTree(params: {
  readonly rootPath: string;
  readonly rootEntry: TreeEntry;
}): readonly TreeEntry[] {
  return [
    { kind: "file", path: README_PATH, content: README_TEXT },
    params.rootEntry,
    AICORE_DIRECTORY,
    RECONCILIATION_DIRECTORY,
    {
      kind: "bindings",
      path: ".aicore/core.yaml",
      document: {
        schema: 1,
        coreRevision: REVISION,
        root: params.rootPath,
        bindings: [{ source: ROOT_SOURCE_PATH, destinations: [params.rootPath] }],
        pending: [params.rootPath],
      },
    },
    {
      kind: "report",
      path: ".aicore/reconciliation/init.yaml",
      document: {
        schema: 1,
        coreRevision: REVISION,
        entries: [
          { destination: params.rootPath, source: ROOT_SOURCE_PATH, action: "initialized" },
        ],
      },
    },
  ];
}

export const ROOT_ROLE_CASES: readonly ParityCase[] = [
  {
    id: "root-role-requires-detectable-root",
    concern: "root-role",
    title: "a root-role source with no detectable destination instruction root fails rather than guessing a path",
    provenance: {
      contract: [
        "SKILL.md / Bindings schema: `root` is detected from the destination instruction files in priority order … `init --root PATH` sets the destination path for the root-role source when detection must be overridden",
        "SKILL.md / Commands: `--root` (optional) overrides the detected destination instruction file",
        "SKILL.md / Exit contract: exit 1 — drift … missing destination",
      ],
      reference: [
        "The diagnostic words `destination instruction root not found; pass --root` are reference behaviour; the contract fixes the refusal class and the remedy, not the wording.",
      ],
    },
    fixture: {
      sourceFiles: [{ path: ROOT_SOURCE_PATH, content: ROOT_SOURCE_TEXT }],
      clearance: ROOT_CLEARANCE_TEXT,
      destinationFiles: [{ path: README_PATH, content: README_TEXT }],
      bindings: null,
    },
    steps: [{ command: "init", bindCleared: true }],
    expectations: [
      {
        exitCode: 1,
        stdout: "",
        stderr: { kind: "contains", value: ["destination instruction root not found"] },
      },
    ],
    destinationTree: [{ kind: "file", path: README_PATH, content: README_TEXT }],
  },
  {
    id: "root-override-names-absent-root",
    concern: "root-role",
    title: "init --root enrolls the root-role source at the named path when the destination holds no instruction root",
    provenance: {
      contract: [
        "SKILL.md / Commands: `init --root PATH` — set the destination path for the root-role source when it is not already mapped and detection must be overridden",
        "SKILL.md / Commands: `init --bind-cleared` — the `role: root` source maps to the destination instruction root",
        "SKILL.md / Exit contract: exit 0 for `init` … prints `initialized`",
        "SKILL.md / Bindings schema: `root` (optional) is the destination root runtime file, relative to the destination directory; a malformed value is rejected before filesystem operations",
      ],
      reference: [
        "The created file's byte layout, the blocker's placement one blank line after the payload, and the two YAML documents' serialization are reference behaviour.",
      ],
    },
    fixture: {
      sourceFiles: [{ path: ROOT_SOURCE_PATH, content: ROOT_SOURCE_TEXT }],
      clearance: ROOT_CLEARANCE_TEXT,
      destinationFiles: [{ path: README_PATH, content: README_TEXT }],
      bindings: null,
    },
    steps: [{ command: "init", bindCleared: true, root: OVERRIDDEN_ROOT_PATH }],
    expectations: [{ exitCode: 0, stdout: "initialized\n", stderr: { kind: "empty" } }],
    destinationTree: rootDestinationTree({
      rootPath: OVERRIDDEN_ROOT_PATH,
      rootEntry: rootWithBlocker(ROOT_CREATED_TEXT),
    }),
  },
  {
    id: "root-role-maps-to-detected-root",
    concern: "root-role",
    title: "a root-role source maps to the destination's detected instruction root instead of its own path",
    provenance: {
      contract: [
        "SKILL.md / Commands: `init --bind-cleared` — the `role: root` source maps to the destination instruction root",
        "SKILL.md / Bindings schema: `root` is detected from the destination instruction files in priority order: `AGENTS.md`/`agents.md`, then `CLAUDE.md`/`claude.md`, then `instructions.md`",
        "SKILL.md / Bindings schema: `root` (optional) is the destination root runtime file, relative to the destination directory",
      ],
      reference: [
        "The enrolled file's byte layout, the blocker's placement one blank line after the payload, and the two YAML documents' serialization are reference behaviour.",
      ],
    },
    fixture: {
      sourceFiles: [{ path: ROOT_SOURCE_PATH, content: ROOT_SOURCE_TEXT }],
      clearance: ROOT_CLEARANCE_TEXT,
      destinationFiles: [
        { path: README_PATH, content: README_TEXT },
        { path: DETECTED_ROOT_PATH, content: DESTINATION_ROOT_MARKERLESS_TEXT },
      ],
      bindings: null,
    },
    steps: [{ command: "init", bindCleared: true }],
    expectations: [{ exitCode: 0, stdout: "initialized\n", stderr: { kind: "empty" } }],
    destinationTree: rootDestinationTree({
      rootPath: DETECTED_ROOT_PATH,
      rootEntry: rootWithBlocker(ROOT_ENROLLED_TEXT),
    }),
  },
];
