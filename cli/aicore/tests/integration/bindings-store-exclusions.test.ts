/**
 * Integration: the bindings document across the real adapter boundary.
 *
 * The persisted document is the destination's own state, so it is written by the
 * real adapter to a real file and read back through the real reader. One group
 * covers the destination's declared opt-outs: written, read back as the same
 * list, and omitted entirely when the destination declares none, with an entry
 * that is not a canonical safe relative path rejected as malformed. The other
 * group covers the document's schema: the fields a saved document carries, the
 * malformed shapes the schema rule refuses, the persisted path rule, and a
 * persisted `raw` declaration that fails closed when the source record is not
 * raw (contract T4).
 *
 * The application-level consequences of an opt-out — a binding dropped, a
 * destination listed in `pending`, a revoked entry restored — belong to the
 * enrollment operation's unit cases, which observe them as writes.
 */

import { readFile, writeFile } from "node:fs/promises";
import { join } from "node:path";
import { afterEach, beforeEach, describe, expect, it } from "vitest";

import { bindingModeConflict, parseBindingsDocument } from "#domain/synchronization/bindings.ts";
import { type BindingMode, MODE_RAW, MODE_REGION } from "#domain/synchronization/constants.ts";
import { YamlBindingsStore } from "#infrastructure/synchronization/bindings-store.ts";
import { readDocumentText } from "#infrastructure/synchronization/yaml-document.ts";
import { REVISION } from "#support/aicore-cli.factory.ts";
import { createTemporaryRoot, disposeTemporaryRoot } from "#support/disposable-root.ts";
import { makeBindingsDocument } from "#support/synchronization.factory.ts";

/** Prefix that identifies a root this suite owns. */
const ROOT_PREFIX = "aicore-cli-bindings-exclusions-";

/** An optional skill directory root, as a clearance expansion names its files. */
const SKILL_ROOT = ".agents/skills/op-model/";

/** One agent document, cleared by the `.opencode/agents/` directory root. */
const AGENT_SOURCE = ".opencode/agents/forge.md";

let root: string;
let rootPrefix: string;
let bindingsPath: string;

beforeEach(async () => {
	const created = await createTemporaryRoot(ROOT_PREFIX);
	root = created.root;
	rootPrefix = created.prefix;
	bindingsPath = join(root, "core.yaml");
});

afterEach(async () => {
	await disposeTemporaryRoot(root, rootPrefix);
});

/** A document declaring the given opt-outs. */
function documentWithExclusions(exclude: readonly string[]) {
	return makeBindingsDocument({
		exclude,
		bindings: [{ source: AGENT_SOURCE, destinations: [AGENT_SOURCE], declaredMode: "region" }],
	});
}

describe("the exclusion declaration", () => {
	it("is written, read back as the same list, and omitted when the destination declares none", async () => {
		await new YamlBindingsStore().save(bindingsPath, documentWithExclusions([AGENT_SOURCE, SKILL_ROOT]));

		const text = await readFile(bindingsPath, "utf8");
		expect(text).toMatch(/^exclude:$/m);
		expect(text).toMatch(/^- \.agents\/skills\/op-model\/$/m);

		const read = await new YamlBindingsStore().load(bindingsPath);
		expect(read?.exclude).toEqual([AGENT_SOURCE, SKILL_ROOT]);

		await new YamlBindingsStore().save(bindingsPath, documentWithExclusions([]));
		expect(await readFile(bindingsPath, "utf8")).not.toMatch(/exclude/u);
	});

	it("rejects an unsafe entry as malformed, and reads an absent key as no opt-outs", async () => {
		for (const entry of ["../escape", "/absolute/path", ".agents\\skills\\op-model\\"]) {
			const text = [
				"schema: 1",
				"core_revision: null",
				"exclude:",
				`- ${entry}`,
				"bindings: []",
				"pending: []",
				"",
			].join("\n");
			expect(parseBindingsDocument(readDocumentText(text)), entry).toBeNull();
			await writeFile(bindingsPath, text, "utf8");
			expect(await new YamlBindingsStore().load(bindingsPath), entry).toBeNull();
		}

		// A document that declares no `exclude` key has declared no opt-outs, and an
		// unknown key elsewhere is still ignored rather than read as one.
		const absent = [
			"schema: 1",
			"core_revision: null",
			"unknown_key: ignored",
			"bindings: []",
			"pending: []",
			"",
		].join("\n");
		await writeFile(bindingsPath, absent, "utf8");
		const loaded = await new YamlBindingsStore().load(bindingsPath);
		expect(loaded?.exclude).toEqual([]);
	});
});

/**
 * A persisted document's text, with the fields a case varies.
 *
 * The spelling of every other field is fixed here so a case states only the
 * value under test.
 */
function bindingsText(
	overrides: {
		readonly schema?: string;
		readonly coreRevision?: string;
		readonly source?: string;
		readonly destination?: string;
		readonly mode?: string;
		readonly pending?: string;
	} = {},
): string {
	const lines = [
		`schema: ${overrides.schema ?? "1"}`,
		`core_revision: ${overrides.coreRevision ?? `"${REVISION}"`}`,
		"editor: opencode",
		"bindings:",
		`- source: ${overrides.source ?? AGENT_SOURCE}`,
		"  destinations:",
		`  - ${overrides.destination ?? AGENT_SOURCE}`,
		...(overrides.mode === undefined ? [] : [`  mode: ${overrides.mode}`]),
		`pending: ${overrides.pending ?? "[]"}`,
		"",
	];
	return lines.join("\n");
}

describe("the persisted document's schema", () => {
	it("is written with the schema label, the pinned revision, the mapping and an empty pending list", async () => {
		await new YamlBindingsStore().save(
			bindingsPath,
			makeBindingsDocument({
				bindings: [{ source: AGENT_SOURCE, destinations: [AGENT_SOURCE], declaredMode: "region" }],
			}),
		);

		const text = await readFile(bindingsPath, "utf8");
		expect(text).toMatch(/^schema: 1$/m);
		expect(text).toContain(`core_revision: "${REVISION}"`);
		expect(text).toMatch(/^- source: \.opencode\/agents\/forge\.md$/m);
		expect(text).toMatch(/^  - \.opencode\/agents\/forge\.md$/m);
		expect(text).toMatch(/^pending: \[\]$/m);

		// Reading the file back yields the document it was written from.
		expect(await new YamlBindingsStore().load(bindingsPath)).toEqual({
			coreRevision: REVISION,
			root: null,
			editor: "opencode",
			exclude: [],
			bindings: [{ source: AGENT_SOURCE, destinations: [AGENT_SOURCE], declaredMode: "region" }],
			pending: [],
		});
	});

	it("refuses a document whose schema label, revision or pending shape is malformed", async () => {
		const malformed = [
			bindingsText({ schema: "2" }),
			bindingsText({ coreRevision: "deadbeef" }),
			bindingsText({ pending: "5" }),
		];
		for (const text of malformed) {
			await writeFile(bindingsPath, text, "utf8");
			expect(await new YamlBindingsStore().load(bindingsPath), text).toBeNull();
		}
	});

	it("refuses a persisted path that is not a canonical safe relative POSIX path", async () => {
		const unsafe = [
			bindingsText({ source: "../escape.md" }),
			bindingsText({ source: "C:/absolute.md" }),
			bindingsText({ destination: "/absolute.md" }),
			bindingsText({ source: ".opencode\\agents\\forge.md" }),
		];
		for (const text of unsafe) {
			await writeFile(bindingsPath, text, "utf8");
			expect(await new YamlBindingsStore().load(bindingsPath), text).toBeNull();
		}
	});

	it("fails closed when a persisted raw declaration's source record is not raw", async () => {
		await writeFile(bindingsPath, bindingsText({ mode: "raw" }), "utf8");

		const loaded = await new YamlBindingsStore().load(bindingsPath);
		const entry = loaded?.bindings[0];
		expect(entry?.declaredMode).toBe("raw");
		if (entry === undefined) {
			throw new Error("the persisted raw declaration did not read back");
		}

		// The clearance registry owns the mode: a leftover `raw` hint against a
		// region record is refused rather than silently ignored.
		expect(bindingModeConflict(entry, new Map<string, BindingMode>([[AGENT_SOURCE, MODE_REGION]]))).toEqual({
			code: "invalid",
			message: `binding mode 'raw' conflicts with source clearance mode 'region' for ${AGENT_SOURCE}`,
		});
		// Against a raw record the same entry is not a conflict.
		expect(bindingModeConflict(entry, new Map<string, BindingMode>([[AGENT_SOURCE, MODE_RAW]]))).toBeNull();
	});
});
