import { mkdtempSync, readFileSync, rmSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";
import { afterEach, describe, expect, it } from "vitest";
import { createText, InputOutputFailure, readText } from "#scripts/pr_review/infrastructure/filesystem.ts";

const temporaryDirectories: string[] = [];

function makeDirectory(): string {
	const directory = mkdtempSync(join(tmpdir(), "git-pr-workflow-filesystem-"));
	temporaryDirectories.push(directory);
	return directory;
}

afterEach(() => {
	for (const directory of temporaryDirectories.splice(0)) {
		rmSync(directory, { recursive: true, force: true });
	}
});

describe("the filesystem adapter", () => {
	it("reads UTF-8 bytes without newline translation", () => {
		const directory = makeDirectory();
		const file = join(directory, "body.md");
		writeFileSync(file, "first\r\nsecond\r\n", "utf8");

		expect(readText(file)).toBe("first\r\nsecond\r\n");
	});

	it("rejects content that is not valid UTF-8", () => {
		const directory = makeDirectory();
		const file = join(directory, "binary.bin");
		writeFileSync(file, Buffer.from([0xff, 0xfe, 0x00]));

		expect(() => readText(file)).toThrow(InputOutputFailure);
	});

	it("reports its own fixed message for content that is not valid UTF-8", () => {
		const directory = makeDirectory();
		const file = join(directory, "binary.bin");
		writeFileSync(file, Buffer.from([0xff, 0xfe, 0x00]));

		expect(() => readText(file)).toThrow("the encoded data was not valid for encoding utf-8");
	});

	it("keeps the byte-order mark in the decoded text", () => {
		const directory = makeDirectory();
		const file = join(directory, "body.md");
		writeFileSync(
			file,
			Buffer.concat([Buffer.from([0xef, 0xbb, 0xbf]), Buffer.from("first\r\nsecond\r\n", "utf8")]),
		);

		expect(readText(file)).toBe(`${String.fromCodePoint(0xfeff)}first\r\nsecond\r\n`);
	});

	it("returns an empty string for an empty file", () => {
		const directory = makeDirectory();
		const file = join(directory, "empty.md");
		writeFileSync(file, "", "utf8");

		expect(readText(file)).toBe("");
	});

	it("reports a missing file as an input/output failure", () => {
		const directory = makeDirectory();

		expect(() => readText(join(directory, "absent.md"))).toThrow(InputOutputFailure);
	});

	it("passes the runtime's own message through for a missing file", () => {
		const directory = makeDirectory();
		const missing = join(directory, "absent.md");

		expect(() => readText(missing)).toThrow(InputOutputFailure);
		expect(() => readText(missing)).toThrow(/^ENOENT: no such file or directory/u);
	});

	it("creates an artifact exclusively and leaves an existing file untouched", () => {
		const directory = makeDirectory();
		const file = join(directory, "snapshot.json");

		createText(file, "{}\n");

		expect(readFileSync(file, "utf8")).toBe("{}\n");
		expect(() => createText(file, "replaced\n")).toThrow(InputOutputFailure);
		expect(readFileSync(file, "utf8")).toBe("{}\n");
	});

	it("reports a missing parent directory as an input/output failure", () => {
		const directory = makeDirectory();

		expect(() => createText(join(directory, "absent", "snapshot.json"), "{}\n")).toThrow(InputOutputFailure);
	});

	it("reports a directory as an input/output failure", () => {
		const directory = makeDirectory();

		expect(() => readText(directory)).toThrow(InputOutputFailure);
	});

	it("reports an input/output failure when the artifact path is a directory", () => {
		const directory = makeDirectory();

		expect(() => createText(directory, "{}\n")).toThrow(InputOutputFailure);
	});
});
