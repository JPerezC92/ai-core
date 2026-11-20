import { spawnSync } from "node:child_process";
import { existsSync, mkdtempSync, readFileSync, readdirSync, rmSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { dirname, join, resolve } from "node:path";
import { fileURLToPath } from "node:url";
import { afterEach, describe, expect, it } from "vitest";

import { makeCreationInput, makeReviewInput, TITLE } from "#tests/support/publication-fixtures.ts";

const entry = resolve(dirname(fileURLToPath(import.meta.url)), "../../scripts/prepare_pr_review.ts");
const PROGRAM = "prepare_pr_review.ts";
const USAGE = `usage: ${PROGRAM} [-h] --input <publication.json> --output <body.md>`;
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

afterEach(() => {
	for (const path of roots.splice(0)) rmSync(path, { recursive: true, force: true });
});

describe("preparing one publication body", () => {
	it("creates the canonical body and its receipt from a creation input", () => {
		const directory = root();
		const input = write(join(directory, "publication.json"), makeCreationInput());
		const output = join(directory, "generated-body.md");

		const result = run(["--input", input, "--output", output]);

		expect(result.status).toBe(0);
		const receipt = `{"status":"prepared","title":"${TITLE}"}\n`;
		expect(result.stdout).toBe(receipt);
		expect(readFileSync(`${output}.receipt.json`, "utf8")).toBe(receipt);
		expect(readFileSync(output, "utf8")).toBe(
			[
				"## Summary",
				"",
				"- Adds the review preparation commands\\.",
				"",
				"## Test plan",
				"",
				"- [ ] Run the focused suite",
				"- [ ] Confirm the import map resolves",
				"",
				"## Findings / blockers",
				"",
				"No review findings yet.",
				"",
			].join("\n"),
		);
	});

	it("creates the review body with its evidence, findings and verdict", () => {
		const directory = root();
		const input = write(join(directory, "publication.json"), makeReviewInput());
		const output = join(directory, "review-body.md");

		const result = run(["--input", input, "--output", output]);

		expect(result.status).toBe(0);
		const body = readFileSync(output, "utf8");
		expect(body).toContain("- [x] Run the focused suite");
		expect(body).toContain("- [ ] Confirm the import map resolves");
		expect(body).toContain("## Findings / blockers\n\nNo findings.");
		expect(body).toContain("- Immutable head SHA: `abc1234def5678abc1234def5678abc1234def56`");
		expect(body).toContain(
			"| Run the focused suite | pnpm vitest run | All focused tests passed; exit 0\\. | Cipher |",
		);
		expect(body.endsWith("[PASS] — Zero open findings; every required check is verified\\.\n")).toBe(true);
	});

	it("refuses an invalid input with its code and message and creates no body", () => {
		const directory = root();
		const input = write(join(directory, "publication.json"), "not json");
		const output = join(directory, "generated-body.md");

		const result = run(["--input", input, "--output", output]);

		expect(result.status).toBe(1);
		expect(result.stdout).toBe('{"code": "INPUT_INVALID", "message": "valid JSON publication required"}\n');
		expect(existsSync(output)).toBe(false);
		expect(existsSync(`${output}.receipt.json`)).toBe(false);
	});
});

describe("command line contract", () => {
	it("rejects invalid invocations with the usage diagnostic and no artifact", () => {
		const directory = root();
		const invocations = [
			{ args: [], message: "the following arguments are required: --input" },
			{ args: ["--input", "publication.json"], message: "the following arguments are required: --output" },
			{ args: ["--input"], message: "argument --input: expected one argument" },
			{ args: ["--output", "body.md"], message: "the following arguments are required: --input" },
			{ args: ["extra"], message: "unrecognized arguments: extra" },
			{
				args: ["--input", "publication.json", "--output", "body.md", "--decisions", "decisions.json"],
				message: "unrecognized arguments: --decisions",
			},
			{
				args: ["--input", "publication.json", "--output", "body.md", "--baseline", "baseline.json"],
				message: "unrecognized arguments: --baseline",
			},
			{
				args: ["--input", "publication.json", "--output", "body.md", "--previous", "prior.json"],
				message: "unrecognized arguments: --previous",
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

	it("prints the usage line for a help invocation", () => {
		const result = run(["--help"]);

		expect(result.status).toBe(0);
		expect(result.stdout).toBe(`${USAGE}\n`);
	});
});

describe("boundary failure reporting", () => {
	it("reports an occupied body as exit 2 and leaves the artifact unchanged", () => {
		const directory = root();
		const input = write(join(directory, "publication.json"), makeCreationInput());
		const output = write(join(directory, "generated-body.md"), "existing body\n");

		const result = run(["--input", input, "--output", output]);

		expect(result.status).toBe(2);
		expect(result.stdout).toBe("");
		expect(result.stderr).toContain("input/output failure:");
		expect(readFileSync(output, "utf8")).toBe("existing body\n");
		expect(existsSync(`${output}.receipt.json`)).toBe(false);
	});

	it("reports an occupied receipt as exit 2 and creates no body", () => {
		const directory = root();
		const input = write(join(directory, "publication.json"), makeCreationInput());
		const output = join(directory, "generated-body.md");
		write(`${output}.receipt.json`, "previous receipt\n");

		const result = run(["--input", input, "--output", output]);

		expect(result.status).toBe(2);
		expect(result.stdout).toBe("");
		expect(result.stderr).toContain("input/output failure:");
		expect(readFileSync(`${output}.receipt.json`, "utf8")).toBe("previous receipt\n");
		expect(existsSync(output)).toBe(false);
	});

	it("reports a missing input as exit 2", () => {
		const directory = root();
		const output = join(directory, "generated-body.md");

		const result = run(["--input", join(directory, "absent.json"), "--output", output]);

		expect(result.status).toBe(2);
		expect(result.stdout).toBe("");
		expect(result.stderr).toContain("input/output failure:");
		expect(existsSync(output)).toBe(false);
	});
});
