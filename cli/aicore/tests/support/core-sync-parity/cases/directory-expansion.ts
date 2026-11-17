/**
 * The directory-expansion concern: what a cleared directory root puts in a
 * distribution set.
 *
 * A cleared directory root expands at every sync into the files that ship from
 * it. Dependency installation directories, the version-control directory and
 * every entry that is not a regular file — symbolic links and directory
 * junctions included — never join that set, while a skill's own scripts,
 * references and tests still do.
 *
 * The first and third cases hold no link and run everywhere; the second needs a
 * directory link and follows the corpus's platform skip convention where the
 * platform refuses to create one.
 */

import { REVISION } from "#support/core-sync-parity/fixtures.ts";
import type { ParityCase, TreeEntry } from "#support/core-sync-parity/types.ts";

const SKILL_ROOT = ".agents/skills/demo/";
const SKILL_FILE = `${SKILL_ROOT}SKILL.md`;
const SCRIPT_FILE = `${SKILL_ROOT}scripts/run.ts`;
const REFERENCE_FILE = `${SKILL_ROOT}references/guide.md`;
const TEST_FILE = `${SKILL_ROOT}tests/demo.spec.ts`;

const SKILL_TEXT = [
	"---",
	"name: demo",
	"description: Synthetic skill fixture",
	"version: 1.0.0",
	"---",
	"",
	"Skill core line one.",
	"",
].join("\n");

const SCRIPT_TEXT = 'export const run = (): string => "ok";\n';
const REFERENCE_TEXT = "# Reference\n\nA synthetic reference file.\n";
const TEST_TEXT = 'import { expect, test } from "vitest";\n\ntest("demo", () => {\n  expect(1).toBe(1);\n});\n';

/** The clearance registry that clears one skill directory root. */
function skillClearance(): string {
	return `${JSON.stringify({ schema: 1, cleared: { [SKILL_ROOT]: { mode: "raw" } } }, null, 2)}\n`;
}

const AICORE_DIRECTORY: TreeEntry = { kind: "directory", path: ".aicore" };
const SKILL_DIRECTORY: TreeEntry = { kind: "directory", path: ".agents/skills/demo" };
const SCRIPTS_DIRECTORY: TreeEntry = { kind: "directory", path: `${SKILL_ROOT}scripts` };
const REFERENCES_DIRECTORY: TreeEntry = { kind: "directory", path: `${SKILL_ROOT}references` };
const TESTS_DIRECTORY: TreeEntry = { kind: "directory", path: `${SKILL_ROOT}tests` };

/** The directory entries every one of these cases creates at the destination. */
const SKILL_TREE_DIRECTORIES: readonly TreeEntry[] = [
	{ kind: "directory", path: ".agents" },
	{ kind: "directory", path: ".agents/skills" },
	SKILL_DIRECTORY,
	AICORE_DIRECTORY,
];

/** The bindings document enrollment writes for the enumerated skill files. */
function enrollmentBindings(sources: readonly string[]): TreeEntry {
	return {
		kind: "bindings",
		path: ".aicore/core.yaml",
		document: {
			schema: 1,
			coreRevision: REVISION,
			root: null,
			bindings: sources.map((source) => ({ source, destinations: [source] })),
			pending: [],
		},
	};
}

export const DIRECTORY_EXPANSION_CASES: readonly ParityCase[] = [
	{
		id: "directory-expansion-skips-dependency-installation",
		concern: "directory-expansion",
		title: "a cleared directory root never distributes its dependency installation directory",
		provenance: {
			contract: [
				"SKILL.md / Bindings schema: the sync tool expands directory roots at every sync, and dependency installation directories (`node_modules`), `.git`, interpreter caches (`__pycache__`, `*.pyc`) and any entry that is not a regular file never join",
				"distribution-clearance.definition.md / Directory-root records / Expansion: every file under the root joins the set, except dependency installation directories, `.git`, interpreter caches, and any entry that is not a regular file",
				"SKILL.md / Commands: `init --bind-cleared` binds every cleared source this editor receives",
			],
			reference: [
				"The YAML serialization of the bindings document is not fixed by the contract, so the corpus compares the parsed document, not its bytes.",
			],
		},
		fixture: {
			sourceFiles: [
				{ path: SKILL_FILE, content: SKILL_TEXT },
				{ path: SCRIPT_FILE, content: SCRIPT_TEXT },
				{ path: REFERENCE_FILE, content: REFERENCE_TEXT },
				{ path: TEST_FILE, content: TEST_TEXT },
				{ path: `${SKILL_ROOT}node_modules/.bin/demo`, content: "#!/bin/sh\nexit 0\n" },
				{ path: `${SKILL_ROOT}node_modules/demo/index.js`, content: "module.exports = {};\n" },
				{ path: `${SKILL_ROOT}.git/config`, content: "[core]\n\trepositoryformatversion = 0\n" },
				{ path: `${SKILL_ROOT}__pycache__/demo.cpython-312.pyc`, content: "cache bytes\n" },
				{ path: `${SKILL_ROOT}scripts/legacy.pyc`, content: "cache bytes\n" },
			],
			clearance: skillClearance(),
			destinationFiles: [],
			bindings: null,
		},
		steps: [{ command: "init", bindCleared: true }],
		expectations: [{ exitCode: 0, stdout: "initialized\n", stderr: { kind: "empty" } }],
		destinationTree: [
			...SKILL_TREE_DIRECTORIES,
			{ kind: "file", path: SKILL_FILE, content: SKILL_TEXT },
			REFERENCES_DIRECTORY,
			{ kind: "file", path: REFERENCE_FILE, content: REFERENCE_TEXT },
			SCRIPTS_DIRECTORY,
			{ kind: "file", path: SCRIPT_FILE, content: SCRIPT_TEXT },
			TESTS_DIRECTORY,
			{ kind: "file", path: TEST_FILE, content: TEST_TEXT },
			enrollmentBindings([SKILL_FILE, REFERENCE_FILE, SCRIPT_FILE, TEST_FILE]),
		],
	},
	{
		id: "directory-expansion-skips-directory-link",
		concern: "directory-expansion",
		title: "a directory link under a cleared root is skipped and the command still succeeds",
		provenance: {
			contract: [
				"SKILL.md / Bindings schema: every entry that is not a regular file — symbolic links and junctions included — never joins a distribution set",
				"distribution-clearance.definition.md / Directory-root records / Expansion: any entry that is not a regular file never joins, so a link is neither followed nor delivered",
				"SKILL.md / Exit contract: exit 0 for `init` … prints `initialized`",
			],
			reference: [
				"An engine that collects the link as a file cannot read it as bytes, so it reports `missing source` drift instead of succeeding; that diagnostic is reference behaviour.",
			],
		},
		fixture: {
			sourceFiles: [
				{ path: SKILL_FILE, content: SKILL_TEXT },
				{ path: REFERENCE_FILE, content: REFERENCE_TEXT },
			],
			sourceDirectoryLinks: [{ path: `${SKILL_ROOT}linked`, target: "references" }],
			clearance: skillClearance(),
			destinationFiles: [],
			bindings: null,
		},
		steps: [{ command: "init", bindCleared: true }],
		expectations: [{ exitCode: 0, stdout: "initialized\n", stderr: { kind: "empty" } }],
		destinationTree: [
			{ kind: "directory", path: ".agents" },
			{ kind: "directory", path: ".agents/skills" },
			SKILL_DIRECTORY,
			{ kind: "file", path: SKILL_FILE, content: SKILL_TEXT },
			REFERENCES_DIRECTORY,
			{ kind: "file", path: REFERENCE_FILE, content: REFERENCE_TEXT },
			AICORE_DIRECTORY,
			enrollmentBindings([SKILL_FILE, REFERENCE_FILE]),
		],
	},
	{
		id: "directory-expansion-keeps-scripts-references-and-tests",
		concern: "directory-expansion",
		title: "a cleared directory root still distributes its scripts, references and tests",
		provenance: {
			contract: [
				"SKILL.md / Bindings schema: the sync tool expands directory roots at every sync, and every file that is not a dependency installation, `.git` or a non-regular entry joins the set",
				"distribution-clearance.definition.md / Directory-root records / Expansion: files added under a root later join automatically; the root's default mode delivers every one of them",
			],
			reference: [],
		},
		fixture: {
			sourceFiles: [
				{ path: SKILL_FILE, content: SKILL_TEXT },
				{ path: SCRIPT_FILE, content: SCRIPT_TEXT },
				{ path: REFERENCE_FILE, content: REFERENCE_TEXT },
				{ path: TEST_FILE, content: TEST_TEXT },
			],
			clearance: skillClearance(),
			destinationFiles: [],
			bindings: null,
		},
		steps: [{ command: "init", bindCleared: true }],
		expectations: [{ exitCode: 0, stdout: "initialized\n", stderr: { kind: "empty" } }],
		destinationTree: [
			...SKILL_TREE_DIRECTORIES,
			{ kind: "file", path: SKILL_FILE, content: SKILL_TEXT },
			REFERENCES_DIRECTORY,
			{ kind: "file", path: REFERENCE_FILE, content: REFERENCE_TEXT },
			SCRIPTS_DIRECTORY,
			{ kind: "file", path: SCRIPT_FILE, content: SCRIPT_TEXT },
			TESTS_DIRECTORY,
			{ kind: "file", path: TEST_FILE, content: TEST_TEXT },
			enrollmentBindings([SKILL_FILE, REFERENCE_FILE, SCRIPT_FILE, TEST_FILE]),
		],
	},
];
