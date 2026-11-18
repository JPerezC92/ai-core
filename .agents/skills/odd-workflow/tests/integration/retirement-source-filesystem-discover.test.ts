import { mkdirSync, mkdtempSync, rmSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { join, sep } from "node:path";
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

describe("FilesystemRetirementSource.discover", () => {
	it("discovers only the Markdown task records in a directory", () => {
		const directory = makeDirectory();
		writeFileSync(join(directory, "a.md"), makeTaskRecord(), "utf8");
		writeFileSync(join(directory, "b.md"), makeTaskRecord(), "utf8");
		writeFileSync(join(directory, "notes.txt"), "not a task record", "utf8");
		writeFileSync(join(directory, "notes.md.bak"), "not a task record", "utf8");

		const discovered = new FilesystemRetirementSource().discover(directory);

		expect([...discovered].sort()).toEqual([join(directory, "a.md"), join(directory, "b.md")]);
	});

	it("does not descend into subdirectories", () => {
		const directory = makeDirectory();
		writeFileSync(join(directory, "a.md"), makeTaskRecord(), "utf8");
		const nested = join(directory, "nested");
		mkdirSync(nested);
		writeFileSync(join(nested, "inner.md"), makeTaskRecord(), "utf8");

		const discovered = new FilesystemRetirementSource().discover(directory);

		expect([...discovered]).toEqual([join(directory, "a.md")]);
	});

	it("discovers the template alongside the task records", () => {
		const directory = makeDirectory();
		writeFileSync(join(directory, "a.md"), makeTaskRecord(), "utf8");
		writeFileSync(join(directory, "_template.md"), makeTaskRecord(), "utf8");

		const discovered = new FilesystemRetirementSource().discover(directory);

		expect([...discovered].sort()).toEqual([join(directory, "_template.md"), join(directory, "a.md")]);
	});

	it("treats a non-directory target as a single reference", () => {
		const directory = makeDirectory();
		const file = join(directory, "a.md");
		writeFileSync(file, makeTaskRecord(), "utf8");

		expect(new FilesystemRetirementSource().discover(file)).toEqual([file]);
	});

	it("treats a missing target as a single reference", () => {
		const directory = makeDirectory();
		const missing = join(directory, "absent.md");

		expect(new FilesystemRetirementSource().discover(missing)).toEqual([missing]);
	});

	it("normalizes the discovered references", () => {
		const directory = makeDirectory();
		const file = join(directory, "a.md");
		writeFileSync(file, makeTaskRecord(), "utf8");

		expect(new FilesystemRetirementSource().discover(`${directory}${sep}${sep}a.md`)).toEqual([file]);
	});
});
