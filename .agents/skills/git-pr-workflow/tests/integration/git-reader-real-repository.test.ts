import { existsSync, mkdtempSync, rmSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";
import { afterAll, beforeAll, describe, expect, it } from "vitest";
import { GitBoundaryError, GitReader } from "#scripts/pr_review/infrastructure/git_reader.ts";
import {
	createCommittedRepository,
	GIT_BINARY_PATH,
	GIT_METACHARACTER_PATH,
	GIT_REMOVED_PATH,
	GIT_RENAMED_FROM_PATH,
	GIT_RENAMED_TO_PATH,
	GIT_SIDE_EFFECT_NAME,
	GIT_SOURCE_PATH,
	limitRepositorySearch,
} from "#tests/support/review-fixtures.ts";
import type { GitRepositoryFixture } from "#tests/support/review-fixtures.ts";

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

describe("the Git reader against a real repository", () => {
	let repository: GitRepositoryFixture;

	beforeAll(() => {
		const root = makeDirectory();
		limitRepositorySearch(root);
		repository = createCommittedRepository(join(root, "repository"));
	}, 30_000);

	it("maps commits, rename destination, metacharacter path, unresolved revision and a failing read", () => {
		const reader = new GitReader({ cwd: repository.directory });

		expect(reader.resolveCommit("HEAD")).toBe(repository.head);
		expect(reader.mergeBase(repository.base, repository.head)).toBe(repository.base);
		expect(reader.listCommits(repository.base, repository.head)).toEqual([repository.head]);
		expect(reader.readMessage(repository.head)).toBe(repository.message);
		expect(reader.listChangedPaths(repository.base, repository.head)).toEqual(repository.changedPaths);
		expect(reader.listDeletedPaths(repository.base, repository.head)).toEqual(repository.deletedPaths);
		expect(reader.readFile(repository.head, GIT_SOURCE_PATH)).toBe(repository.bodies[GIT_SOURCE_PATH]);

		expect(reader.listChangedPaths(repository.base, repository.head)).not.toContain(GIT_RENAMED_FROM_PATH);
		expect(reader.listChangedPaths(repository.base, repository.head)).toContain(GIT_RENAMED_TO_PATH);
		expect(reader.listDeletedPaths(repository.base, repository.head)).not.toContain(GIT_RENAMED_TO_PATH);
		expect(reader.readFile(repository.head, GIT_RENAMED_TO_PATH)).toBe(repository.bodies[GIT_RENAMED_TO_PATH]);

		expect(reader.readFile(repository.head, GIT_METACHARACTER_PATH)).toBe(
			repository.bodies[GIT_METACHARACTER_PATH],
		);
		expect(existsSync(join(repository.directory, GIT_SIDE_EFFECT_NAME))).toBe(false);

		expect(reader.resolveCommit("refs/heads/unresolved")).toBeNull();
		expect(reader.mergeBase(repository.base, repository.orphanHead)).toBeNull();
		expect(() => reader.listCommits(repository.base, "refs/heads/unresolved")).toThrow(GitBoundaryError);
	});

	it("maps an unchanged range to empty path, commit and deletion inventories", () => {
		const reader = new GitReader({ cwd: repository.directory });

		expect(reader.listCommits(repository.base, repository.base)).toEqual([]);
		expect(reader.listChangedPaths(repository.base, repository.base)).toEqual([]);
		expect(reader.listDeletedPaths(repository.base, repository.base)).toEqual([]);
	});

	it("reports a path that is absent at the read commit", () => {
		const reader = new GitReader({ cwd: repository.directory });

		expect(() => reader.readFile(repository.head, GIT_REMOVED_PATH)).toThrow(GitBoundaryError);
		expect(() => reader.readFile(repository.head, GIT_REMOVED_PATH)).toThrow(/^git exited with [0-9]+:/u);
	});

	it("reports a committed body that is not valid UTF-8", () => {
		const reader = new GitReader({ cwd: repository.directory });

		expect(() => reader.readFile(repository.head, GIT_BINARY_PATH)).toThrow(GitBoundaryError);
		expect(() => reader.readFile(repository.head, GIT_BINARY_PATH)).toThrow("git output was not valid UTF-8");
	});
}, 30_000);
