/**
 * Integration: the destination's declared opt-outs across the real bindings
 * boundary.
 *
 * One behavioral concern — the `exclude:` declaration is the bindings
 * document's own state, so it is written by the real adapter to a real file, read
 * back as the same list, and omitted entirely when the destination declares no
 * opt-out; an entry that is not a canonical safe relative path is rejected as
 * malformed rather than read as a declaration (contract T4).
 *
 * The application-level consequences of an opt-out — a binding dropped, a
 * destination listed in `pending`, a revoked entry restored — belong to the
 * enrollment operation's unit cases, which observe them as writes.
 */

import { readFile, writeFile } from "node:fs/promises";
import { join } from "node:path";
import { afterEach, beforeEach, describe, expect, it } from "vitest";

import { parseBindingsDocument } from "#domain/synchronization/bindings.ts";
import { YamlBindingsStore } from "#infrastructure/synchronization/bindings-store.ts";
import { readDocumentText } from "#infrastructure/synchronization/yaml-document.ts";
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
