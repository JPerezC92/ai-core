/**
 * Integration: a read of a genuinely absent path across the real filesystem.
 *
 * One behavioral concern — the local source adapter reports genuine absence as
 * `null` through both read methods instead of throwing or guessing, which is the
 * read contract `local-files.ts` owns and the engine relies on to tell "not
 * there" from a read failure. Exercised over a real disposable root (contract
 * T4, T18).
 */

import { join } from "node:path";
import { afterEach, beforeEach, describe, expect, test } from "vitest";

import { LocalSourceFiles } from "#infrastructure/synchronization/local-source-files.ts";
import { createTemporaryRoot, disposeTemporaryRoot } from "#support/disposable-root.ts";

/** Prefix that identifies a root this suite owns. */
const ROOT_PREFIX = "aicore-cli-file-absence-";

let root: string;
let rootPrefix: string;
const source = new LocalSourceFiles();

beforeEach(async () => {
	const created = await createTemporaryRoot(ROOT_PREFIX);
	root = created.root;
	rootPrefix = created.prefix;
});

afterEach(async () => {
	await disposeTemporaryRoot(root, rootPrefix);
});

describe("absent file reads", () => {
	test("a missing path reads as null through both read methods", async () => {
		const missing = join(root, "absent", "document.md");

		expect(await source.readText(missing)).toBeNull();
		expect(await source.readBytes(missing)).toBeNull();
	});
});
