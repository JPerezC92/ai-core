import { describe, expect, it } from "vitest";
import { GitBoundaryError, GitReader, parseStatusEntries } from "#scripts/pr_review/infrastructure/git_reader.ts";
import { createTruncatedStatusPayload } from "#tests/support/review-fixtures.ts";

describe("the Git reader boundary failures", () => {
	it("rejects a truncated name-status payload instead of returning a partial path", () => {
		expect(() => parseStatusEntries(createTruncatedStatusPayload())).toThrow(GitBoundaryError);
	});

	it("reports a missing git executable as a boundary failure", () => {
		const reader = new GitReader({ executable: null });

		expect(() => reader.resolveCommit("HEAD")).toThrow(GitBoundaryError);
		expect(() => reader.resolveCommit("HEAD")).toThrow("git executable was not found on PATH");
	});
});
