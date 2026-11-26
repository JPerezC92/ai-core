import { existsSync, mkdtempSync, rmSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";
import { afterAll, beforeAll, describe, expect, it } from "vitest";
import { GitBoundaryError, GitReader } from "#scripts/pr_review/infrastructure/git_reader.ts";
import {
	createBinaryRenameRepository,
	createCommittedRepository,
	createMalformedTextRepository,
	createModeOnlyBinaryRepository,
	GIT_BINARY_PATH,
	GIT_CHANGED_BINARY_PATH,
	GIT_MALFORMED_TEXT_PATH,
	GIT_METACHARACTER_PATH,
	GIT_REMOVED_PATH,
	GIT_RENAMED_BINARY_PATH,
	GIT_RENAMED_FROM_PATH,
	GIT_RENAMED_TO_PATH,
	GIT_SIDE_EFFECT_NAME,
	GIT_SOURCE_PATH,
	limitRepositorySearch,
} from "#tests/support/review-fixtures.ts";
import type { GitRangeFixture, GitRepositoryFixture } from "#tests/support/review-fixtures.ts";

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

	describe("commit and path inventories", () => {
		it("maps commit and path inventories, including rename destinations and disjoint history", () => {
			const reader = new GitReader({ cwd: repository.directory });

			expect(reader.resolveCommit("HEAD")).toBe(repository.head);
			expect(reader.mergeBase(repository.base, repository.head)).toBe(repository.base);
			expect(reader.listCommits(repository.base, repository.head)).toEqual([repository.head]);
			expect(reader.readMessage(repository.head)).toBe(repository.message);
			expect(reader.listChangedPaths(repository.base, repository.head)).toEqual(repository.changedPaths);
			expect(reader.listDeletedPaths(repository.base, repository.head)).toEqual(repository.deletedPaths);
			expect(reader.listBinaryPaths(repository.base, repository.head)).toEqual(repository.binaryPaths);

			expect(reader.listChangedPaths(repository.base, repository.head)).not.toContain(GIT_RENAMED_FROM_PATH);
			expect(reader.listChangedPaths(repository.base, repository.head)).toContain(GIT_RENAMED_TO_PATH);
			expect(reader.listDeletedPaths(repository.base, repository.head)).not.toContain(GIT_RENAMED_TO_PATH);

			expect(reader.resolveCommit("refs/heads/unresolved")).toBeNull();
			expect(reader.mergeBase(repository.base, repository.orphanHead)).toBeNull();
			expect(() => reader.listCommits(repository.base, "refs/heads/unresolved")).toThrow(GitBoundaryError);
		});

		it("maps an unchanged range to empty path, commit and deletion inventories", () => {
			const reader = new GitReader({ cwd: repository.directory });

			expect(reader.listCommits(repository.base, repository.base)).toEqual([]);
			expect(reader.listChangedPaths(repository.base, repository.base)).toEqual([]);
			expect(reader.listDeletedPaths(repository.base, repository.base)).toEqual([]);
			expect(reader.listBinaryPaths(repository.base, repository.base)).toEqual([]);
		});
	});

	describe("committed file reads", () => {
		it("reads committed and renamed file bodies without interpreting path metacharacters", () => {
			const reader = new GitReader({ cwd: repository.directory });

			expect(reader.readFile(repository.head, GIT_SOURCE_PATH)).toBe(repository.bodies[GIT_SOURCE_PATH]);
			expect(reader.readFile(repository.head, GIT_RENAMED_TO_PATH)).toBe(repository.bodies[GIT_RENAMED_TO_PATH]);
			expect(reader.readFile(repository.head, GIT_METACHARACTER_PATH)).toBe(
				repository.bodies[GIT_METACHARACTER_PATH],
			);
			expect(existsSync(join(repository.directory, GIT_SIDE_EFFECT_NAME))).toBe(false);
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
			expect(() => reader.readFile(repository.head, GIT_CHANGED_BINARY_PATH)).toThrow(
				"git output was not valid UTF-8",
			);
		});
	});

	describe("binary classification", () => {
		let malformed: GitRangeFixture;

		beforeAll(() => {
			const root = makeDirectory();
			limitRepositorySearch(root);
			malformed = createMalformedTextRepository(join(root, "malformed"));
		}, 30_000);

		it("classifies a binary change as binary and leaves a non-UTF-8 text change unclassified", () => {
			const reader = new GitReader({ cwd: malformed.directory });

			expect(reader.listBinaryPaths(malformed.base, malformed.head)).toEqual(malformed.binaryPaths);
			expect(reader.listChangedPaths(malformed.base, malformed.head)).toEqual(malformed.changedPaths);
		});

		it("keeps strict UTF-8 validation for a text path whose body is malformed", () => {
			const reader = new GitReader({ cwd: malformed.directory });

			expect(() => reader.readFile(malformed.head, GIT_MALFORMED_TEXT_PATH)).toThrow(
				"git output was not valid UTF-8",
			);
		});
	});

	describe("a mode-only binary change", () => {
		let modeOnly: GitRangeFixture;

		beforeAll(() => {
			const root = makeDirectory();
			limitRepositorySearch(root);
			modeOnly = createModeOnlyBinaryRepository(join(root, "mode-only"));
		}, 30_000);

		it("still classifies the changed binary path as binary", () => {
			const reader = new GitReader({ cwd: modeOnly.directory });

			expect(reader.listChangedPaths(modeOnly.base, modeOnly.head)).toEqual(modeOnly.changedPaths);
			expect(reader.listBinaryPaths(modeOnly.base, modeOnly.head)).toEqual(modeOnly.binaryPaths);
		});
	});

	describe("a binary rename", () => {
		let renamed: GitRangeFixture;

		beforeAll(() => {
			const root = makeDirectory();
			limitRepositorySearch(root);
			renamed = createBinaryRenameRepository(join(root, "renamed-binary"));
		}, 30_000);

		it("classifies the rename destination as binary without listing the source path", () => {
			const reader = new GitReader({ cwd: renamed.directory });

			expect(reader.listChangedPaths(renamed.base, renamed.head)).toEqual(renamed.changedPaths);
			// Rename detection is off, so the deleted source is compared as an all-binary
			// removal too; it is already carried with an empty body as a deleted path.
			expect(reader.listBinaryPaths(renamed.base, renamed.head)).toEqual(renamed.binaryPaths);
			expect(reader.listBinaryPaths(renamed.base, renamed.head)).toContain(GIT_RENAMED_BINARY_PATH);
		});
	});
}, 30_000);
