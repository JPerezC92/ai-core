/**
 * Integration: the clearance registry's strict reader across its real boundary.
 *
 * One behavioral concern — a registry that declares the same key twice is
 * rejected and names the repeated key, instead of the last declaration silently
 * winning. The store runs over a real temporary file, so the strict JSON reader,
 * its duplicate detection and the store's diagnostic mapping all execute as the
 * engine executes them (contract T4).
 */

import { writeFile } from "node:fs/promises";
import { join } from "node:path";
import { afterEach, beforeEach, describe, expect, test } from "vitest";

import { CLEARANCE_FILENAME, CLEARANCE_SCHEMA } from "#domain/synchronization/constants.ts";
import { JsonClearanceStore } from "#infrastructure/synchronization/clearance-store.ts";
import { createTemporaryRoot, disposeTemporaryRoot } from "#support/disposable-root.ts";

/** Prefix that identifies a root this suite owns. */
const ROOT_PREFIX = "aicore-cli-clearance-duplicate-keys-";

/** The cleared path the nested duplicate declares twice. */
const CLEARED_PATH = "docs/guide.md";

/** The top-level key the wrapper documents declare twice. */
const REPEATED_TOP_LEVEL_KEY = "schema";

/** The entry-level key the nested document declares twice. */
const REPEATED_NESTED_KEY = "mode";

let root: string;
let rootPrefix: string;
const store = new JsonClearanceStore();

beforeEach(async () => {
	const created = await createTemporaryRoot(ROOT_PREFIX);
	root = created.root;
	rootPrefix = created.prefix;
});

afterEach(async () => {
	await disposeTemporaryRoot(root, rootPrefix);
});

/** The diagnostic the store reports for a registry that repeats `key`. */
function duplicateReason(key: string): string {
	return `duplicate key in clearance document: ${key}`;
}

/** Write raw registry text into this case's temporary source root. */
async function writeRegistryText(text: string): Promise<void> {
	await writeFile(join(root, CLEARANCE_FILENAME), text, "utf8");
}

/** A registry whose wrapper declares its schema key twice at the top level. */
function makeTopLevelDuplicateText(): string {
	return [
		"{",
		`  "${REPEATED_TOP_LEVEL_KEY}": ${CLEARANCE_SCHEMA},`,
		`  "${REPEATED_TOP_LEVEL_KEY}": ${CLEARANCE_SCHEMA},`,
		'  "cleared": {}',
		"}",
	].join("\n");
}

/** A registry whose clearance entry declares its mode key twice. */
function makeNestedDuplicateText(): string {
	return [
		"{",
		`  "schema": ${CLEARANCE_SCHEMA},`,
		'  "cleared": {',
		`    "${CLEARED_PATH}": {`,
		`      "${REPEATED_NESTED_KEY}": "region",`,
		`      "${REPEATED_NESTED_KEY}": "region"`,
		"    }",
		"  }",
		"}",
	].join("\n");
}

/** A registry that repeats a top-level key and is also truncated mid-object. */
function makeMalformedWithDuplicateText(): string {
	return [
		"{",
		`  "${REPEATED_TOP_LEVEL_KEY}": ${CLEARANCE_SCHEMA},`,
		`  "${REPEATED_TOP_LEVEL_KEY}": ${CLEARANCE_SCHEMA},`,
		'  "cleared": {',
	].join("\n");
}

describe("duplicate keys", () => {
	test("a duplicate top-level key is rejected and names the repeated key", async () => {
		await writeRegistryText(makeTopLevelDuplicateText());

		const loaded = await store.load(root);

		expect(loaded.exists).toBe(true);
		expect(loaded.entries).toBeNull();
		expect(loaded.reason).toBe(duplicateReason(REPEATED_TOP_LEVEL_KEY));
	});

	test("a duplicate key nested inside a clearance entry is rejected", async () => {
		await writeRegistryText(makeNestedDuplicateText());

		const loaded = await store.load(root);

		expect(loaded.entries).toBeNull();
		expect(loaded.reason).toBe(duplicateReason(REPEATED_NESTED_KEY));
	});

	test("a document that is both malformed and duplicated reports the duplicate", async () => {
		await writeRegistryText(makeMalformedWithDuplicateText());

		const loaded = await store.load(root);

		expect(loaded.entries).toBeNull();
		expect(loaded.reason).toBe(duplicateReason(REPEATED_TOP_LEVEL_KEY));
	});
});
