/**
 * The `--bind` / `--bind-raw` declaration concern.
 *
 * A declaration is a second way to name a mapping, next to the persisted
 * bindings document: `init --bind SOURCE=DESTINATION` appends a region-mode
 * binding and `init --bind-raw` a raw one, before preflight, repeatably and
 * idempotently. The concern owns the three things a declaration can do —
 * succeed, be malformed, and conflict with what the bindings file already
 * says — plus the raw form's own consequence.
 *
 * The cases are self-contained: their own synthetic source text, destination
 * text and clearance registry, so they measure the declaration behaviour and
 * nothing else in the corpus.
 */

import { CONTRACT_BLOCK_FACTS, BLOCK_BEGIN, BLOCK_END } from "../blocker.ts";
import { REVISION } from "../fixtures.ts";
import type { ParityCase, TreeEntry } from "../types.ts";

const ROOT_PATH = "AGENTS.md";
const ROOT_TEXT = "# Declaration fixture\n\nA disposable destination for the declaration cases.\n";

const NOTES_PATH = "notes.md";
const OTHER_PATH = "other.md";
const RAW_PATH = "raw-note.md";

const NOTES_TEXT = [
  "---",
  "name: notes",
  "description: Synthetic declaration fixture",
  "version: 1.0.0",
  "---",
  "",
  "Note core line one.",
  "Note core line two.",
  "",
].join("\n");

const OTHER_TEXT = [
  "---",
  "name: other",
  "description: Synthetic second declaration fixture",
  "version: 1.0.0",
  "---",
  "",
  "Other core line one.",
  "",
].join("\n");

/** The bytes `init` creates for an absent region target bound to `notes.md`. */
const NOTES_CREATED_TEXT = [
  "---",
  "name: notes",
  "description: Synthetic declaration fixture",
  "version: 1.0.0",
  "---",
  "<!-- core:begin -->",
  "",
  "Note core line one.",
  "Note core line two.",
  "<!-- core:end -->",
  "",
  "<!-- project:begin -->",
  "<!-- project:end -->",
  "",
].join("\n");

const RAW_TEXT = "raw declaration payload line one\nraw declaration payload line two";

const DEST_NOTES_MARKERLESS_TEXT = "Destination notes body before enrollment.\n";

const EMPTY_BINDINGS_TEXT = [
  "schema: 1",
  `core_revision: ${REVISION}`,
  "bindings: []",
  "pending: []",
  "",
].join("\n");

/** A bindings document that already maps `notes.md` to `notes.md`. */
const NOTES_BOUND_BINDINGS_TEXT = [
  "schema: 1",
  `core_revision: ${REVISION}`,
  "bindings:",
  "- source: notes.md",
  "  destinations:",
  "  - notes.md",
  "pending: []",
  "",
].join("\n");

const NOTES_CLEARANCE_TEXT = [
  "{",
  '  "schema": 1,',
  '  "cleared": {',
  '    "notes.md": {',
  '      "mode": "region"',
  "    }",
  "  }",
  "}",
  "",
].join("\n");

const BOTH_CLEARANCE_TEXT = [
  "{",
  '  "schema": 1,',
  '  "cleared": {',
  '    "notes.md": {',
  '      "mode": "region"',
  "    },",
  '    "other.md": {',
  '      "mode": "region"',
  "    }",
  "  }",
  "}",
  "",
].join("\n");

const RAW_CLEARANCE_TEXT = [
  "{",
  '  "schema": 1,',
  '  "cleared": {',
  '    "raw-note.md": {',
  '      "mode": "raw"',
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

/** The root runtime file with the reconciliation blocker appended to it. */
function blockerAfter(rootText: string): TreeEntry {
  return {
    kind: "blocker",
    path: ROOT_PATH,
    prefix: `${rootText.endsWith("\n") ? rootText : `${rootText}\n`}\n${BLOCK_BEGIN}\n`,
    suffix: `\n${BLOCK_END}\n`,
    bodyContains: CONTRACT_BLOCK_FACTS,
  };
}

export const BINDING_DECLARATION_CASES: readonly ParityCase[] = [
  {
    id: "bind-region-declaration-enrolls-target",
    concern: "binding-declarations",
    title: "init --bind appends a region-mode binding before preflight and enrolls the absent target it names",
    provenance: {
      contract: [
        "SKILL.md / Commands: `init --bind SOURCE=DESTINATION` — append a region-mode binding to the loaded bindings file before preflight",
        "SKILL.md / Commands: `apply` and `init` create any region or raw target a binding declares, creating missing parent directories",
        "SKILL.md / Exit contract: exit 0 for `init` — every markerless destination enrolled, absent region … target created …; prints `initialized`",
        "SKILL.md / Reconciliation blocker: while region-mode paths remain in `pending`, `init` ensures the destination root runtime file carries the blocker block",
      ],
      reference: [
        "The created file's byte layout (source frontmatter, core region, empty project region) and the two YAML documents' serialization are reference behaviour.",
      ],
    },
    fixture: {
      sourceFiles: [{ path: NOTES_PATH, content: NOTES_TEXT }],
      clearance: NOTES_CLEARANCE_TEXT,
      destinationFiles: [{ path: ROOT_PATH, content: ROOT_TEXT }],
      bindings: EMPTY_BINDINGS_TEXT,
    },
    steps: [{ command: "init", bind: [`${NOTES_PATH}=${NOTES_PATH}`] }],
    expectations: [{ exitCode: 0, stdout: "initialized\n", stderr: { kind: "empty" } }],
    destinationTree: [
      blockerAfter(ROOT_TEXT),
      { kind: "file", path: NOTES_PATH, content: NOTES_CREATED_TEXT },
      AICORE_DIRECTORY,
      RECONCILIATION_DIRECTORY,
      {
        kind: "bindings",
        path: ".aicore/core.yaml",
        document: {
          schema: 1,
          coreRevision: REVISION,
          root: null,
          bindings: [{ source: NOTES_PATH, destinations: [NOTES_PATH] }],
          pending: [NOTES_PATH],
        },
      },
      {
        kind: "report",
        path: ".aicore/reconciliation/init.yaml",
        document: {
          schema: 1,
          coreRevision: REVISION,
          entries: [{ destination: NOTES_PATH, source: NOTES_PATH, action: "initialized" }],
        },
      },
    ],
  },
  {
    id: "bind-malformed-declaration-rejected",
    concern: "binding-declarations",
    title: "a declaration that is not exactly one safe SOURCE=DEST pair is rejected before any write",
    provenance: {
      contract: [
        "SKILL.md / Bindings schema: source and destination paths must be canonical safe relative POSIX paths",
        "SKILL.md / Exit contract: exit 2 — malformed bindings",
        "SKILL.md / Commands: the flags update binding metadata and synchronized content together; a refused declaration writes neither",
      ],
      reference: [
        "The diagnostic words `invalid init binding` and `malformed or unsafe binding declaration` are reference behaviour.",
      ],
    },
    fixture: {
      sourceFiles: [{ path: NOTES_PATH, content: NOTES_TEXT }],
      clearance: NOTES_CLEARANCE_TEXT,
      destinationFiles: [{ path: ROOT_PATH, content: ROOT_TEXT }],
      bindings: EMPTY_BINDINGS_TEXT,
    },
    steps: [{ command: "init", bind: [NOTES_PATH] }],
    expectations: [
      {
        exitCode: 2,
        stdout: "",
        stderr: {
          kind: "contains",
          value: ["invalid init binding", "malformed or unsafe binding declaration"],
        },
      },
    ],
    destinationTree: [
      { kind: "file", path: ROOT_PATH, content: ROOT_TEXT },
      AICORE_DIRECTORY,
      { kind: "file", path: ".aicore/core.yaml", content: EMPTY_BINDINGS_TEXT },
    ],
  },
  {
    id: "bind-conflicts-with-existing-binding",
    concern: "binding-declarations",
    title: "a declaration whose destination the bindings file already maps to another source fails closed",
    provenance: {
      contract: [
        "SKILL.md / Bindings schema: destination paths must be unique",
        "SKILL.md / Commands: a destination already mapped to a different source fails closed",
        "SKILL.md / Exit contract: exit 2 — malformed bindings",
      ],
      reference: [
        "The diagnostic words `invalid init binding` and `destination mapping conflicts` are reference behaviour.",
      ],
    },
    fixture: {
      sourceFiles: [
        { path: NOTES_PATH, content: NOTES_TEXT },
        { path: OTHER_PATH, content: OTHER_TEXT },
      ],
      clearance: BOTH_CLEARANCE_TEXT,
      destinationFiles: [
        { path: ROOT_PATH, content: ROOT_TEXT },
        { path: NOTES_PATH, content: DEST_NOTES_MARKERLESS_TEXT },
      ],
      bindings: NOTES_BOUND_BINDINGS_TEXT,
    },
    steps: [{ command: "init", bind: [`${OTHER_PATH}=${NOTES_PATH}`] }],
    expectations: [
      {
        exitCode: 2,
        stdout: "",
        stderr: {
          kind: "contains",
          value: ["invalid init binding", "destination mapping conflicts"],
        },
      },
    ],
    destinationTree: [
      { kind: "file", path: ROOT_PATH, content: ROOT_TEXT },
      { kind: "file", path: NOTES_PATH, content: DEST_NOTES_MARKERLESS_TEXT },
      AICORE_DIRECTORY,
      { kind: "file", path: ".aicore/core.yaml", content: NOTES_BOUND_BINDINGS_TEXT },
    ],
  },
  {
    id: "bind-raw-declaration-copies-source",
    concern: "binding-declarations",
    title: "init --bind-raw appends a raw binding, copies the source byte-for-byte and takes no part in reconciliation",
    provenance: {
      contract: [
        "SKILL.md / Commands: `init --bind-raw SOURCE=DESTINATION` — append a raw binding",
        "SKILL.md / Binding modes: raw — `init` and `apply` write the source file to the destination byte-for-byte; a raw destination carries no `project` region, creates no reconciliation report, and never creates a `pending` entry",
        "SKILL.md / Exit contract: exit 0 for `init` — raw file copied; prints `initialized`",
      ],
      reference: ["The two YAML documents' serialization is reference behaviour."],
    },
    fixture: {
      sourceFiles: [{ path: RAW_PATH, content: RAW_TEXT }],
      clearance: RAW_CLEARANCE_TEXT,
      destinationFiles: [{ path: ROOT_PATH, content: ROOT_TEXT }],
      bindings: EMPTY_BINDINGS_TEXT,
    },
    steps: [{ command: "init", bindRaw: [`${RAW_PATH}=${RAW_PATH}`] }],
    expectations: [{ exitCode: 0, stdout: "initialized\n", stderr: { kind: "empty" } }],
    destinationTree: [
      { kind: "file", path: ROOT_PATH, content: ROOT_TEXT },
      { kind: "file", path: RAW_PATH, content: RAW_TEXT },
      AICORE_DIRECTORY,
      {
        kind: "bindings",
        path: ".aicore/core.yaml",
        document: {
          schema: 1,
          coreRevision: REVISION,
          root: null,
          bindings: [{ source: RAW_PATH, destinations: [RAW_PATH] }],
          pending: [],
        },
      },
    ],
  },
];
