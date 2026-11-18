import { mkdirSync, mkdtempSync, rmSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";
import { afterAll, describe, expect, it } from "vitest";
import { GitBoundaryError, GitReader } from "#scripts/pr_review/infrastructure/git_reader.ts";
import { limitRepositorySearch } from "#tests/support/review-fixtures.ts";

const temporaryDirectories: string[] = [];

function makeDirectory(): string {
	const directory = mkdtempSync(join(tmpdir(), "git-pr-workflow-git-"));
	temporaryDirectories.push(directory);
	return directory;
}

afterAll(() => {
	for (const directory of temporaryDirectories.splice(0)) {
		rmSync(directory, { recursive: true, force: true });
	}
});

describe("the Git reader outside a repository", () => {
	it("reports a directory that is not a Git repository", () => {
		const root = makeDirectory();
		limitRepositorySearch(root);
		const directory = join(root, "not-a-repository");
		mkdirSync(directory, { recursive: true });
		const reader = new GitReader({ cwd: directory });

		expect(reader.resolveCommit("HEAD")).toBeNull();
		expect(() => reader.readFile("HEAD", "any.txt")).toThrow(GitBoundaryError);
		expect(() => reader.readFile("HEAD", "any.txt")).toThrow(/^git exited with [0-9]+:/u);
	});
});
