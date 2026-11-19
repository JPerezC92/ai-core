/**
 * Integration: the shared local-file content contract across the real filesystem.
 *
 * One behavioral concern — the content contract both adapters delegate to in
 * `local-files.ts`: a text write is normalised to LF terminators, a raw byte
 * payload is never transformed, and a text read preserves the file's own line
 * endings. `LocalSourceFiles` and `LocalDestinationFiles` both appear here
 * because the contract is genuinely shared through `local-files.ts`, not because
 * two separate behaviours are collected in one module; each case names the
 * adapter whose delegation it proves and asserts that one shared rule. A real
 * disposable root per case (contract T4, T18).
 */

import { readFile, writeFile } from "node:fs/promises";
import { join } from "node:path";
import { afterEach, beforeEach, describe, expect, test } from "vitest";

import { LocalDestinationFiles } from "#infrastructure/synchronization/local-destination-files.ts";
import { LocalSourceFiles } from "#infrastructure/synchronization/local-source-files.ts";
import { createTemporaryRoot, disposeTemporaryRoot } from "#support/disposable-root.ts";

/** Prefix that identifies a root this suite owns. */
const ROOT_PREFIX = "aicore-cli-file-fidelity-";

/** The CRLF terminator a text input may carry. */
const CRLF = "\r\n";

/** The LF terminator every text write must store. */
const LF = "\n";

/** The byte value of a carriage return, which a text write must never emit. */
const CARRIAGE_RETURN = 0x0d;

let root: string;
let rootPrefix: string;
const source = new LocalSourceFiles();
const destination = new LocalDestinationFiles();

beforeEach(async () => {
	const created = await createTemporaryRoot(ROOT_PREFIX);
	root = created.root;
	rootPrefix = created.prefix;
});

afterEach(async () => {
	await disposeTemporaryRoot(root, rootPrefix);
});

/** A multi-line document whose lines are separated by `terminator`. */
function makeTextDocument(terminator: string): string {
	return ["first line", "second line", "third line"].join(terminator) + terminator;
}

/** The same document with LF terminators, which is what a text write must store. */
function makeLfTextDocument(): string {
	return makeTextDocument(LF);
}

/** A raw payload carrying CRLF bytes and a non-ASCII UTF-8 sequence. */
function makeRawPayload(): Uint8Array {
	return new TextEncoder().encode("raw line\r\nsecond ñ→ line\r\n");
}

describe("local file content fidelity", () => {
	test("a text write replaces CRLF with LF terminators", async () => {
		const path = join(root, "text", "document.md");
		await destination.writeText(path, makeTextDocument(CRLF));

		const raw = await readFile(path);

		expect(raw.includes(CARRIAGE_RETURN)).toBe(false);
		expect(raw.toString("utf8")).toBe(makeLfTextDocument());
	});

	test("a raw byte payload round-trips byte-identically through both readers", async () => {
		const path = join(root, "bytes", "payload.bin");
		const payload = makeRawPayload();
		await destination.writeBytes(path, payload);

		const fromDestination = await destination.readBytes(path);
		const fromSource = await source.readBytes(path);

		expect(Array.from(fromDestination ?? [])).toEqual(Array.from(payload));
		expect(Array.from(fromSource ?? [])).toEqual(Array.from(payload));
	});

	test("reading a source's text preserves the file's own line endings", async () => {
		const path = join(root, "source-document.md");
		const text = makeTextDocument(CRLF);
		await writeFile(path, text, "utf8");

		expect(await source.readText(path)).toBe(text);
	});
});
