import { mkdtempSync, rmSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";
import { afterEach, describe, expect, it } from "vitest";
import { FilesystemFeatureSource } from "#scripts/feature_validation/infrastructure/filesystem.ts";
import { makeFeature } from "#tests/support/feature-fixtures.ts";

const temporaryDirectories: string[] = [];

function makeDirectory(): string {
	const directory = mkdtempSync(join(tmpdir(), "odd-workflow-feature-source-"));
	temporaryDirectories.push(directory);
	return directory;
}

afterEach(() => {
	for (const directory of temporaryDirectories.splice(0)) {
		rmSync(directory, { recursive: true, force: true });
	}
});

describe("FilesystemFeatureSource.read", () => {
	it("returns the file's exact UTF-8 text", () => {
		const directory = makeDirectory();
		const file = join(directory, "a.md");
		writeFileSync(file, makeFeature(), "utf8");

		expect(new FilesystemFeatureSource().read(file)).toBe(makeFeature());
	});

	it("keeps the byte-order mark in the decoded text", () => {
		const directory = makeDirectory();
		const file = join(directory, "a.md");
		writeFileSync(file, Buffer.concat([Buffer.from([0xef, 0xbb, 0xbf]), Buffer.from(makeFeature(), "utf8")]));

		expect(new FilesystemFeatureSource().read(file)).toBe(`${String.fromCodePoint(0xfeff)}${makeFeature()}`);
	});

	it("rejects invalid UTF-8 with the runtime's own error", () => {
		const directory = makeDirectory();
		const file = join(directory, "a.md");
		writeFileSync(file, Buffer.from([0xff]));

		expect(() => new FilesystemFeatureSource().read(file)).toThrow(TypeError);
	});

	it("propagates the runtime's error for a missing file", () => {
		const directory = makeDirectory();
		const missing = join(directory, "absent.md");

		expect(() => new FilesystemFeatureSource().read(missing)).toThrow(/ENOENT/u);
	});
});
