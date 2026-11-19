import { spawnSync } from "node:child_process";
import { existsSync, mkdtempSync, readdirSync, readFileSync, rmSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { dirname, join, resolve } from "node:path";
import { fileURLToPath } from "node:url";
import { afterEach, describe, expect, it } from "vitest";

import {
	makeCompletedBody,
	makeCreationBody,
	makeCreationDraft,
	makeExistingArtifact,
	makeMalformedDraft,
	makeMalformedMetadataJson,
	makeMetadata,
} from "#tests/support/review-content-fixtures.ts";

const entry = resolve(dirname(fileURLToPath(import.meta.url)), "../../scripts/prepare_pr_review.ts");
const PROGRAM = "prepare_pr_review.ts";
const USAGE = `usage: ${PROGRAM} [-h] {initialize,validate} ...`;
const roots: string[] = [];

function root(): string {
	const path = mkdtempSync(join(tmpdir(), "prepare-pr-review-test-"));
	roots.push(path);
	return path;
}

function write(path: string, content: string): string {
	writeFileSync(path, content);
	return path;
}

function run(args: string[]) {
	const result = spawnSync(process.execPath, [entry, ...args], { encoding: "utf8" });
	if (result.error) throw result.error;
	return result;
}

/** The documented usage diagnostic for one rejected invocation. */
function diagnostic(message: string): string {
	return `${USAGE}\n${PROGRAM}: error: ${message}\n`;
}

/** The documented business refusal payload for one refused command. */
function refusal(payload: { readonly code: string; readonly message: string }): string {
	return `{"code": ${JSON.stringify(payload.code)}, "message": ${JSON.stringify(payload.message)}}\n`;
}

afterEach(() => {
	for (const path of roots.splice(0)) rmSync(path, { recursive: true, force: true });
});

describe("initialize command", () => {
	it("creates the working body from a creation draft", () => {
		const directory = root();
		const draft = write(join(directory, "draft.md"), makeCreationDraft());
		const working = join(directory, "working-body.md");

		const result = run(["initialize", "--draft", draft, "--working-body", working]);

		expect(result.status).toBe(0);
		expect(result.stdout).toBe('{"status": "prepared", "command": "initialize"}\n');
		expect(readFileSync(working, "utf8")).toBe(makeCreationBody());
	});
});

describe("business refusal reporting", () => {
	it("reports a business refusal as exit 1 with its code and message", () => {
		const cases = [
			{
				name: "initialize with a malformed creation draft",
				arrange: (directory: string) => {
					const draft = write(join(directory, "draft.md"), makeMalformedDraft());
					const working = join(directory, "working-body.md");
					return {
						args: ["initialize", "--draft", draft, "--working-body", working],
						artifact: working,
						payload: {
							code: "DRAFT_INVALID",
							message: "creation draft title wrapper and Summary required",
						},
					};
				},
			},
			{
				name: "validate whose supplied metadata diverges from the accepted baseline",
				arrange: (directory: string) => {
					const baseline = write(join(directory, "baseline.json"), JSON.stringify(makeMetadata()));
					const current = write(
						join(directory, "current.json"),
						JSON.stringify(makeMetadata({ headRefOid: "def5678abc1234def5678abc1234def5678abc1" })),
					);
					const working = write(join(directory, "working-body.md"), makeCompletedBody());
					return {
						args: ["validate", "--baseline", baseline, "--current", current, "--working-body", working],
						artifact: null,
						payload: { code: "REMOTE_DIVERGED", message: "remote metadata differs from accepted baseline" },
					};
				},
			},
		];

		for (const testCase of cases) {
			const directory = root();
			const { args, artifact, payload } = testCase.arrange(directory);

			const result = run(args);

			expect(result.status, testCase.name).toBe(1);
			expect(result.stdout, testCase.name).toBe(refusal(payload));
			if (artifact !== null) expect(existsSync(artifact), testCase.name).toBe(false);
		}
	});
});

describe("boundary failure reporting", () => {
	it("reports a work failure as exit 2 with the documented diagnostic and unchanged artifacts", () => {
		const cases = [
			{
				name: "initialize over an existing working body",
				arrange: (directory: string) => {
					const draft = write(join(directory, "draft.md"), makeCreationDraft());
					const working = write(join(directory, "working-body.md"), makeExistingArtifact());
					return { args: ["initialize", "--draft", draft, "--working-body", working], working };
				},
			},
			{
				name: "validate over a baseline that is not valid JSON",
				arrange: (directory: string) => {
					const baseline = write(join(directory, "baseline.json"), makeMalformedMetadataJson());
					const current = write(join(directory, "current.json"), JSON.stringify(makeMetadata()));
					const working = write(join(directory, "working-body.md"), makeCompletedBody());
					return {
						args: ["validate", "--baseline", baseline, "--current", current, "--working-body", working],
						working,
					};
				},
			},
		];

		for (const testCase of cases) {
			const directory = root();
			const { args, working } = testCase.arrange(directory);
			const before = readFileSync(working, "utf8");

			const result = run(args);

			expect(result.status, testCase.name).toBe(2);
			expect(result.stdout, testCase.name).toBe("");
			expect(result.stderr, testCase.name).toContain("input/output failure:");
			expect(readFileSync(working, "utf8"), testCase.name).toBe(before);
		}
	});
});

describe("validate command", () => {
	it("accepts a fresh completed body", () => {
		const directory = root();
		const metadata = JSON.stringify(makeMetadata());
		const baseline = write(join(directory, "baseline.json"), metadata);
		const current = write(join(directory, "current.json"), metadata);
		const working = write(join(directory, "working-body.md"), makeCompletedBody());

		const result = run(["validate", "--baseline", baseline, "--current", current, "--working-body", working]);

		expect(result.status).toBe(0);
		expect(result.stdout).toBe('{"status": "prepared", "command": "validate"}\n');
	});
});

describe("command line contract", () => {
	it("rejects invalid invocations with the usage diagnostic and no artifact", () => {
		const directory = root();
		const invocations = [
			{ args: [], message: "the following arguments are required: command" },
			{
				args: ["publish"],
				message: "argument command: invalid choice: 'publish' (choose from 'initialize', 'validate')",
			},
			{
				args: ["initialize", "--draft", "d.md"],
				message: "the following arguments are required: --working-body",
			},
			{ args: ["initialize", "extra"], message: "unrecognized arguments: extra" },
			{ args: ["initialize", "--draft"], message: "argument --draft: expected one argument" },
			{
				args: ["initialize", "--draft", "d.md", "--working-body", "w.md", "--extra", "x"],
				message: "unrecognized arguments: --extra",
			},
		];

		for (const invocation of invocations) {
			const result = run(invocation.args);

			expect(result.status).toBe(2);
			expect(result.stdout).toBe("");
			expect(result.stderr).toBe(diagnostic(invocation.message));
			expect(readdirSync(directory)).toEqual([]);
		}
	});
});
