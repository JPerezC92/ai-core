import { mkdtempSync, rmSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";
import { describe, expect, it } from "vitest";
import { GitBoundaryError, GitReader } from "#scripts/pr_review/infrastructure/git_reader.ts";

describe("the Git reader with an unavailable executable", () => {
	it("reports a missing executable as a boundary failure", () => {
		const directory = mkdtempSync(join(tmpdir(), "git-pr-workflow-missing-git-"));
		try {
			const reader = new GitReader({ executable: join(directory, "missing-git") });

			try {
				reader.resolveCommit("HEAD");
				expect.unreachable("expected a missing executable error");
			} catch (error) {
				expect(error).toBeInstanceOf(GitBoundaryError);
				expect(error).toHaveProperty("message", "git executable was not found on PATH");
			}
		} finally {
			rmSync(directory, { recursive: true, force: true });
		}
	});
});
