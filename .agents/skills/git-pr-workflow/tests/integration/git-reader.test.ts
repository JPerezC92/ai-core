import { existsSync, mkdtempSync, rmSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";
import { afterEach, describe, expect, it } from "vitest";
import {
  GitBoundaryError,
  GitReader,
  parseStatusEntries,
} from "../../scripts/pr_review/infrastructure/git_reader.ts";
import {
  createCommittedRepository,
  createOrphanRepository,
  createTruncatedStatusPayload,
  GIT_METACHARACTER_PATH,
  GIT_RENAMED_FROM_PATH,
  GIT_RENAMED_TO_PATH,
  GIT_SIDE_EFFECT_NAME,
  GIT_SOURCE_PATH,
} from "../support/review-fixtures.ts";

const temporaryDirectories: string[] = [];

function makeDirectory(): string {
  const directory = mkdtempSync(join(tmpdir(), "git-pr-workflow-git-"));
  temporaryDirectories.push(directory);
  return directory;
}

afterEach(() => {
  for (const directory of temporaryDirectories.splice(0)) {
    rmSync(directory, { recursive: true, force: true });
  }
});

describe("the Git reader against a real repository", () => {
  it("maps commits, messages and a deleted path", () => {
    const repository = createCommittedRepository(join(makeDirectory(), "repository"));
    const reader = new GitReader({ cwd: repository.directory });

    expect(reader.resolveCommit("HEAD")).toBe(repository.head);
    expect(reader.mergeBase(repository.base, repository.head)).toBe(repository.base);
    expect(reader.listCommits(repository.base, repository.head)).toEqual([repository.head]);
    expect(reader.readMessage(repository.head)).toBe(repository.message);
    expect(reader.listChangedPaths(repository.base, repository.head)).toEqual(
      repository.changedPaths,
    );
    expect(reader.listDeletedPaths(repository.base, repository.head)).toEqual(
      repository.deletedPaths,
    );
    expect(reader.readFile(repository.head, GIT_SOURCE_PATH)).toBe(
      repository.bodies[GIT_SOURCE_PATH],
    );
  });

  it("maps a rename to its destination path", () => {
    const repository = createCommittedRepository(join(makeDirectory(), "repository"));
    const reader = new GitReader({ cwd: repository.directory });

    expect(reader.listChangedPaths(repository.base, repository.head)).not.toContain(
      GIT_RENAMED_FROM_PATH,
    );
    expect(reader.listChangedPaths(repository.base, repository.head)).toContain(GIT_RENAMED_TO_PATH);
    expect(reader.listDeletedPaths(repository.base, repository.head)).not.toContain(
      GIT_RENAMED_TO_PATH,
    );
    expect(reader.readFile(repository.head, GIT_RENAMED_TO_PATH)).toBe(
      repository.bodies[GIT_RENAMED_TO_PATH],
    );
  });

  it("reports an unresolvable revision as absence", () => {
    const repository = createCommittedRepository(join(makeDirectory(), "repository"));
    const reader = new GitReader({ cwd: repository.directory });

    expect(reader.resolveCommit("refs/heads/unresolved")).toBeNull();
  });

  it("reports a disjoint history as no common ancestor", () => {
    const orphan = createOrphanRepository(join(makeDirectory(), "orphan-repository"));
    const reader = new GitReader({ cwd: orphan.directory });

    expect(reader.resolveCommit(orphan.orphanHead)).toBe(orphan.orphanHead);
    expect(reader.mergeBase(orphan.base, orphan.orphanHead)).toBeNull();
  });

  it("reads a metacharacter path without a side effect", () => {
    const repository = createCommittedRepository(join(makeDirectory(), "repository"));
    const reader = new GitReader({ cwd: repository.directory });

    const body = reader.readFile(repository.head, GIT_METACHARACTER_PATH);

    expect(body).toBe(repository.bodies[GIT_METACHARACTER_PATH]);
    expect(existsSync(join(repository.directory, GIT_SIDE_EFFECT_NAME))).toBe(false);
  });
});

describe("the Git reader boundary failures", () => {
  it("rejects a truncated name-status payload instead of returning a partial path", () => {
    expect(() => parseStatusEntries(createTruncatedStatusPayload())).toThrow(GitBoundaryError);
  });

  it("reports a missing git executable as a boundary failure", () => {
    const reader = new GitReader({ executable: null });

    expect(() => reader.resolveCommit("HEAD")).toThrow(GitBoundaryError);
    expect(() => reader.resolveCommit("HEAD")).toThrow("git executable was not found on PATH");
  });

  it("reports a failing read as a boundary failure", () => {
    const repository = createCommittedRepository(join(makeDirectory(), "repository"));
    const reader = new GitReader({ cwd: repository.directory });

    expect(() => reader.listCommits(repository.base, "refs/heads/unresolved")).toThrow(
      GitBoundaryError,
    );
  });
});
