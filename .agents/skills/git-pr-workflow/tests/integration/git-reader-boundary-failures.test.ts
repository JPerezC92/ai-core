import { spawnSync } from "node:child_process";
import { describe, expect, it, vi } from "vitest";
import { GitBoundaryError, GitReader } from "#scripts/pr_review/infrastructure/git_reader.ts";
import { createTruncatedNumstatPayload, createTruncatedStatusPayload } from "#tests/support/review-fixtures.ts";

vi.mock("node:child_process", () => ({ spawnSync: vi.fn() }));

describe("the Git reader boundary failures", () => {
	it("rejects a truncated name-status payload instead of returning a partial path", () => {
		vi.mocked(spawnSync).mockReturnValueOnce({
			pid: 1,
			output: [null, Buffer.from(createTruncatedStatusPayload()), Buffer.alloc(0)],
			stdout: Buffer.from(createTruncatedStatusPayload()),
			stderr: Buffer.alloc(0),
			status: 0,
			signal: null,
		});

		expect(() => new GitReader().listDeletedPaths("base", "head")).toThrow(GitBoundaryError);
	});

	it("rejects a truncated numstat payload instead of classifying a partial path", () => {
		vi.mocked(spawnSync).mockReturnValue({
			pid: 1,
			output: [null, Buffer.from(createTruncatedNumstatPayload()), Buffer.alloc(0)],
			stdout: Buffer.from(createTruncatedNumstatPayload()),
			stderr: Buffer.alloc(0),
			status: 0,
			signal: null,
		});

		expect(() => new GitReader().listBinaryPaths("base", "head")).toThrow(GitBoundaryError);
		expect(() => new GitReader().listBinaryPaths("base", "head")).toThrow("git numstat output was malformed");
	});
});
