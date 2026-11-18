import { mkdirSync, mkdtempSync, rmSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { join, sep } from "node:path";
import { afterEach, describe, expect, it } from "vitest";
import { ValidateFeatureFiles } from "#scripts/feature_file_validation/application/validate_feature_files.ts";
import type { FeatureFileSource } from "#scripts/feature_file_validation/domain/ports.ts";
import { ValidFeatureFile } from "#scripts/feature_file_validation/domain/records.ts";
import type { PathComparisonPolicy } from "#scripts/feature_file_validation/domain/rules.ts";
import { FilesystemFeatureFileSource } from "#scripts/feature_file_validation/infrastructure/filesystem.ts";
import { makeFeatureFile } from "#tests/support/feature-file-fixtures.ts";

const temporaryDirectories: string[] = [];

function makeDirectory(): string {
	const directory = mkdtempSync(join(tmpdir(), "odd-workflow-feature-file-source-"));
	temporaryDirectories.push(directory);
	return directory;
}

/** The host path-comparison policy: Windows paths compare case-insensitively. */
const hostPathComparisonPolicy: PathComparisonPolicy = {
	caseSensitive: process.platform !== "win32",
};

afterEach(() => {
	for (const directory of temporaryDirectories.splice(0)) {
		rmSync(directory, { recursive: true, force: true });
	}
});

describe("FilesystemFeatureFileSource.discover", () => {
	it("discovers only the Markdown files in a directory", () => {
		const directory = makeDirectory();
		writeFileSync(join(directory, "a.md"), makeFeatureFile(), "utf8");
		writeFileSync(join(directory, "b.md"), makeFeatureFile(), "utf8");
		writeFileSync(join(directory, "notes.txt"), "not a feature document", "utf8");
		writeFileSync(join(directory, "notes.md.bak"), "not a feature document", "utf8");

		const discovered = new FilesystemFeatureFileSource().discover(directory);

		expect([...discovered].sort()).toEqual([join(directory, "a.md"), join(directory, "b.md")]);
	});

	it("does not descend into subdirectories", () => {
		const directory = makeDirectory();
		writeFileSync(join(directory, "a.md"), makeFeatureFile(), "utf8");
		const nested = join(directory, "nested");
		mkdirSync(nested);
		writeFileSync(join(nested, "inner.md"), makeFeatureFile(), "utf8");

		const discovered = new FilesystemFeatureFileSource().discover(directory);

		expect([...discovered]).toEqual([join(directory, "a.md")]);
	});

	it("treats a non-directory target as a single reference", () => {
		const directory = makeDirectory();
		const file = join(directory, "a.md");
		writeFileSync(file, makeFeatureFile(), "utf8");

		expect(new FilesystemFeatureFileSource().discover(file)).toEqual([file]);
	});

	it("treats a missing target as a single reference", () => {
		const directory = makeDirectory();
		const missing = join(directory, "absent.md");

		expect(new FilesystemFeatureFileSource().discover(missing)).toEqual([missing]);
	});

	it("normalizes the discovered references", () => {
		const directory = makeDirectory();
		const file = join(directory, "a.md");
		writeFileSync(file, makeFeatureFile(), "utf8");

		expect(new FilesystemFeatureFileSource().discover(`${file}${sep}`)).toEqual([file]);
		expect(new FilesystemFeatureFileSource().discover(`${directory}${sep}${sep}a.md`)).toEqual([file]);
	});
});

describe("FilesystemFeatureFileSource.read", () => {
	it("returns the file's exact UTF-8 text", () => {
		const directory = makeDirectory();
		const file = join(directory, "a.md");
		writeFileSync(file, makeFeatureFile(), "utf8");

		expect(new FilesystemFeatureFileSource().read(file)).toBe(makeFeatureFile());
	});

	it("keeps the byte-order mark in the decoded text", () => {
		const directory = makeDirectory();
		const file = join(directory, "a.md");
		writeFileSync(file, Buffer.concat([Buffer.from([0xef, 0xbb, 0xbf]), Buffer.from(makeFeatureFile(), "utf8")]));

		expect(new FilesystemFeatureFileSource().read(file)).toBe(
			`${String.fromCodePoint(0xfeff)}${makeFeatureFile()}`,
		);
	});

	it("rejects invalid UTF-8 with the runtime's own error", () => {
		const directory = makeDirectory();
		const file = join(directory, "a.md");
		writeFileSync(file, Buffer.from([0xff]));

		expect(() => new FilesystemFeatureFileSource().read(file)).toThrow(TypeError);
	});

	it("propagates the runtime's error for a missing file", () => {
		const directory = makeDirectory();
		const missing = join(directory, "absent.md");

		expect(() => new FilesystemFeatureFileSource().read(missing)).toThrow(/ENOENT/u);
	});
});

// This adapter is separately implemented from the feature source adapter, so it
// carries its own boundary coverage above. What is distinct here is the
// FeatureFileSource port it declares, and the feature-file application that
// consumes it through that port.
describe("FilesystemFeatureFileSource as the feature-file source port", () => {
	it("satisfies the FeatureFileSource port the feature-file application composes", () => {
		const source: FeatureFileSource = new FilesystemFeatureFileSource();
		expect(typeof source.discover).toBe("function");
		expect(typeof source.read).toBe("function");

		const directory = makeDirectory();
		const file = join(directory, "feature.md");
		writeFileSync(file, makeFeatureFile(), "utf8");

		const operation = new ValidateFeatureFiles(source, hostPathComparisonPolicy);
		const results = [...operation.execute(directory)];

		expect(results).toHaveLength(1);
		expect(results[0]).toBeInstanceOf(ValidFeatureFile);
		expect(results[0]).toMatchObject({ path: file, status: "partial" });
	});
});
