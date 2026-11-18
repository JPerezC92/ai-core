import { mkdirSync, mkdtempSync, rmSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { join, sep } from "node:path";
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

describe("FilesystemFeatureSource.discover", () => {
	it("discovers only the Markdown files in a directory", () => {
		const directory = makeDirectory();
		writeFileSync(join(directory, "a.md"), makeFeature(), "utf8");
		writeFileSync(join(directory, "b.md"), makeFeature(), "utf8");
		writeFileSync(join(directory, "notes.txt"), "not a feature document", "utf8");
		writeFileSync(join(directory, "notes.md.bak"), "not a feature document", "utf8");

		const discovered = new FilesystemFeatureSource().discover(directory);

		expect([...discovered].sort()).toEqual([join(directory, "a.md"), join(directory, "b.md")]);
	});

	it("does not descend into subdirectories", () => {
		const directory = makeDirectory();
		writeFileSync(join(directory, "a.md"), makeFeature(), "utf8");
		const nested = join(directory, "nested");
		mkdirSync(nested);
		writeFileSync(join(nested, "inner.md"), makeFeature(), "utf8");

		const discovered = new FilesystemFeatureSource().discover(directory);

		expect([...discovered]).toEqual([join(directory, "a.md")]);
	});

	it("treats a non-directory target as a single reference", () => {
		const directory = makeDirectory();
		const file = join(directory, "a.md");
		writeFileSync(file, makeFeature(), "utf8");

		expect(new FilesystemFeatureSource().discover(file)).toEqual([file]);
	});

	it("treats a missing target as a single reference", () => {
		const directory = makeDirectory();
		const missing = join(directory, "absent.md");

		expect(new FilesystemFeatureSource().discover(missing)).toEqual([missing]);
	});

	it("normalizes the discovered references", () => {
		const directory = makeDirectory();
		const file = join(directory, "a.md");
		writeFileSync(file, makeFeature(), "utf8");

		expect(new FilesystemFeatureSource().discover(`${file}${sep}`)).toEqual([file]);
		expect(new FilesystemFeatureSource().discover(`${directory}${sep}${sep}a.md`)).toEqual([file]);
	});
});
