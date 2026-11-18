/**
 * Integration: a source document's core markers across the real source reader.
 *
 * One behavioral concern — `LocalSourceFiles.readCore` decides what a source's
 * core is, so the marker rule is exercised over a real disposable filesystem
 * (contract T4). A document that carries project markers without a core pair, or
 * a reversed core pair, is malformed rather than read as a markerless body; a
 * document whose marker literals sit inside a fenced code block is markerless,
 * and its whole body is the core. A genuine pair outside any fence still yields
 * its region, so the malformed refusals above are the marker rule and not a
 * reader that refuses everything.
 */

import { writeFile } from "node:fs/promises";
import { join } from "node:path";
import { afterEach, beforeEach, describe, expect, test } from "vitest";

import { LocalSourceFiles } from "#infrastructure/synchronization/local-source-files.ts";
import { createTemporaryRoot, disposeTemporaryRoot } from "#support/disposable-root.ts";

/** Prefix that identifies a root this suite owns. */
const ROOT_PREFIX = "aicore-cli-source-core-";

/** The one line block a case writes as a candidate source. */
const CORE_BEGIN = "<!-- core:begin -->";
const CORE_END = "<!-- core:end -->";
const PROJECT_BEGIN = "<!-- project:begin -->";
const PROJECT_END = "<!-- project:end -->";

const FENCE = "```md";

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

/** Read one candidate source document's core through the real adapter. */
async function readCoreOf(lines: readonly string[]) {
	const path = join(root, "source.md");
	await writeFile(path, lines.join("\n"), "utf8");
	return source.readCore(path);
}

describe("source core markers", () => {
	test("project markers without a core pair, or a reversed core pair, are malformed", async () => {
		// The project region is never re-read as the core.
		expect(await readCoreOf([PROJECT_BEGIN, "project body", PROJECT_END, ""])).toStrictEqual({
			kind: "malformed",
		});
		// A reversed pair is not a region either.
		expect(await readCoreOf([CORE_END, "old core", CORE_BEGIN, ""])).toStrictEqual({ kind: "malformed" });
	});

	test("marker literals inside a fence leave the source markerless, and a real pair still yields its region", async () => {
		const fenced = ["# Document", "", FENCE, CORE_BEGIN, "not a marker", CORE_END, "```", ""];

		expect(await readCoreOf(fenced)).toStrictEqual({ kind: "core", core: fenced.join("\n") });

		// The same literals outside a fence are a region.
		expect(await readCoreOf(["before", CORE_BEGIN, "inner", CORE_END, "after", ""])).toStrictEqual({
			kind: "core",
			core: "inner\n",
		});
	});
});
