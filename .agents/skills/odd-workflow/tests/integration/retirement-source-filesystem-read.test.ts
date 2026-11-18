import { mkdtempSync, rmSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";
import { afterEach, describe, expect, it } from "vitest";
import { FilesystemRetirementSource } from "#scripts/retirement_check/infrastructure/filesystem.ts";
import { makeTaskRecord } from "#tests/support/retirement-fixtures.ts";

const temporaryDirectories: string[] = [];

function makeDirectory(): string {
	const directory = mkdtempSync(join(tmpdir(), "odd-workflow-retirement-source-"));
	temporaryDirectories.push(directory);
	return directory;
}

afterEach(() => {
	for (const directory of temporaryDirectories.splice(0)) {
		rmSync(directory, { recursive: true, force: true });
	}
});

describe("FilesystemRetirementSource.read", () => {
	it("returns the record's exact UTF-8 text", () => {
		const directory = makeDirectory();
		const file = join(directory, "a.md");
		writeFileSync(file, makeTaskRecord(), "utf8");

		expect(new FilesystemRetirementSource().read(file)).toBe(makeTaskRecord());
	});

	it("keeps the byte-order mark in the decoded text", () => {
		const directory = makeDirectory();
		const file = join(directory, "a.md");
		writeFileSync(file, Buffer.concat([Buffer.from([0xef, 0xbb, 0xbf]), Buffer.from(makeTaskRecord(), "utf8")]));

		expect(new FilesystemRetirementSource().read(file)).toBe(`${String.fromCodePoint(0xfeff)}${makeTaskRecord()}`);
	});

	it("rejects invalid UTF-8 with the runtime's own error", () => {
		const directory = makeDirectory();
		const file = join(directory, "a.md");
		writeFileSync(file, Buffer.from([0xff]));

		expect(() => new FilesystemRetirementSource().read(file)).toThrow(TypeError);
	});

	it("propagates the runtime's error for a missing file", () => {
		const directory = makeDirectory();
		const missing = join(directory, "absent.md");

		expect(() => new FilesystemRetirementSource().read(missing)).toThrow(/ENOENT/u);
	});
});
