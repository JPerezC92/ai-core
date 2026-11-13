/**
 * The clearance-registry integrity concern: a duplicate key in the registry.
 *
 * `distribution-clearance.json` is a JSON object whose cleared keys must be
 * unique. A duplicate key is not a redundant spelling of one record: it is two
 * conflicting declarations of one path, and the registry is malformed. A
 * general-purpose JSON parser collapses the pair before any domain rule can see
 * it, so this case separates an engine that validates the document it was given
 * from one that validates a lossy parse of it.
 */

import { REVISION } from "../fixtures.ts";
import type { ParityCase, TreeEntry } from "../types.ts";

const ROOT_PATH = "AGENTS.md";
const ROOT_TEXT = "# Integrity fixture\n\nA disposable destination for the clearance cases.\n";

const NOTES_PATH = "notes.md";

const NOTES_TEXT = [
  "---",
  "name: notes",
  "description: Synthetic clearance-integrity fixture",
  "version: 1.0.0",
  "---",
  "",
  "Note core line one.",
  "",
].join("\n");

const DEST_NOTES_MARKED_TEXT = [
  "---",
  "name: notes",
  "description: Destination description",
  "version: 1.0.0",
  "---",
  "<!-- core:begin -->",
  "Old shared body.",
  "<!-- core:end -->",
  "",
  "<!-- project:begin -->",
  "Destination project content.",
  "<!-- project:end -->",
  "",
].join("\n");

/** Two conflicting declarations of one cleared path. */
const DUPLICATE_KEY_CLEARANCE_TEXT = [
  "{",
  '  "schema": 1,',
  '  "cleared": {',
  '    "notes.md": {',
  '      "mode": "region"',
  "    },",
  '    "notes.md": {',
  '      "mode": "raw"',
  "    }",
  "  }",
  "}",
  "",
].join("\n");

const BINDINGS_TEXT = [
  "schema: 1",
  `core_revision: ${REVISION}`,
  "bindings:",
  `- source: ${NOTES_PATH}`,
  "  destinations:",
  `  - ${NOTES_PATH}`,
  "pending: []",
  "",
].join("\n");

const AICORE_DIRECTORY: TreeEntry = { kind: "directory", path: ".aicore" };

export const CLEARANCE_INTEGRITY_CASES: readonly ParityCase[] = [
  {
    id: "clearance-duplicate-key-rejected",
    concern: "clearance-integrity",
    title: "a clearance registry that declares one cleared path twice is malformed, not resolved by the last value",
    provenance: {
      contract: [
        "distribution-clearance.definition.md / Validity: a document is valid when `parse_clearance` accepts it — schema exactly `1`; keys unique and repo-relative",
        "SKILL.md / Exit contract: exit 2 — `distribution-clearance.json` present but malformed",
        "SKILL.md / Exit contract: the clearance gate runs before any bound-source payload read or destination mutation",
      ],
      reference: [
        "The parser hook that rejects a repeated key at any nesting level is the reference's mechanism, not contract text.",
        "The pinned diagnostic is the form BOTH engines produce — `invalid clearance file: <path>` — because one corpus judges both. `parse_clearance` builds `duplicate key in clearance document: …`, but `load_clearance` collapses any parse failure to its malformed flag and the application renders `invalid clearance file: <path>` with no detail, so that reason never reaches the reference's stderr (its own suite asserts exactly that). An engine may keep its own detail after that prefix; the corpus never requires it, since the detail is not contract text and only the exit class (2) and the keys-unique classification are.",
      ],
    },
    fixture: {
      sourceFiles: [{ path: NOTES_PATH, content: NOTES_TEXT }],
      clearance: DUPLICATE_KEY_CLEARANCE_TEXT,
      destinationFiles: [
        { path: ROOT_PATH, content: ROOT_TEXT },
        { path: NOTES_PATH, content: DEST_NOTES_MARKED_TEXT },
      ],
      bindings: BINDINGS_TEXT,
    },
    steps: [{ command: "check" }],
    expectations: [
      {
        exitCode: 2,
        stdout: "",
        stderr: { kind: "contains", value: ["invalid clearance file"] },
      },
    ],
    destinationTree: [
      { kind: "file", path: ROOT_PATH, content: ROOT_TEXT },
      { kind: "file", path: NOTES_PATH, content: DEST_NOTES_MARKED_TEXT },
      AICORE_DIRECTORY,
      { kind: "file", path: ".aicore/core.yaml", content: BINDINGS_TEXT },
    ],
  },
];
