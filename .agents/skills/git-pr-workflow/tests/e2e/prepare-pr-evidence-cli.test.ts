/** End-to-end behavior of the evidence CLI as a spawned process. */

import { spawnSync } from "node:child_process";
import { existsSync, mkdtempSync, readFileSync, rmSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { dirname, join, resolve } from "node:path";
import { fileURLToPath } from "node:url";
import { afterEach, describe, expect, it } from "vitest";
import {
	createBinaryOnlyRepository,
	createBody,
	createCommittedRepository,
	createCreationPublicationDocument,
	createFixtureEnvironment,
	createLocalInventory,
	createLocalSnapshot,
	createMalformedTextRepository,
	createMetadata,
	createPaths,
	createPolicy,
	createPreparedReceipt,
	createPublicationHandoff,
	createPublicationTitle,
	createReviewPublicationDocument,
	createSnapshot,
	createReceiptWithUndeclaredField,
	createUndecodablePublicationText,
	createUnexactPathInventory,
	GIT_CHANGED_BINARY_PATH,
	GIT_CHANGED_CONTENT,
	GIT_SOURCE_PATH,
} from "#tests/support/review-fixtures.ts";

const skillRoot = resolve(dirname(fileURLToPath(import.meta.url)), "../..");
const entryPoint = join(skillRoot, "scripts", "prepare_pr_evidence.ts");

const temporaryDirectories: string[] = [];

interface CliRun {
	readonly status: number;
	readonly stdout: string;
	readonly stderr: string;
}

function makeDirectory(): string {
	const directory = mkdtempSync(join(tmpdir(), "git-pr-workflow-prepare-e2e-"));
	temporaryDirectories.push(directory);
	return directory;
}

/** Run the entry point as a spawned process and capture its status and streams. */
function runCli(args: readonly string[], cwd: string, env: NodeJS.ProcessEnv = process.env): CliRun {
	const completed = spawnSync(process.execPath, [entryPoint, ...args], {
		cwd,
		encoding: "utf8",
		env,
	});
	if (completed.error) throw completed.error;
	return {
		status: completed.status ?? -1,
		stdout: completed.stdout,
		stderr: completed.stderr,
	};
}

afterEach(() => {
	for (const directory of temporaryDirectories.splice(0)) {
		rmSync(directory, { recursive: true, force: true });
	}
});

describe("prepare_pr_evidence as a spawned process", () => {
	it("hands the generated creation and review artifacts through scanning and verified persistence", () => {
		const directory = makeDirectory();
		const contentEntry = resolve(skillRoot, "../git-pr/scripts/prepare_pr_review.ts");
		const scanEntry = join(skillRoot, "scripts", "scan_attribution.ts");
		const execute = (entry: string, args: string[]) =>
			spawnSync(process.execPath, [entry, ...args], { cwd: directory, encoding: "utf8" });
		const publication = join(directory, "publication.json");
		const inventory = join(directory, "inventory.json");
		const paths = join(directory, "paths.json");
		const policy = join(directory, "policy.json");
		const creation = createCreationPublicationDocument();
		writeFileSync(inventory, JSON.stringify(createLocalInventory()), "utf8");
		writeFileSync(paths, JSON.stringify(createPaths()), "utf8");
		writeFileSync(policy, JSON.stringify(createPolicy()), "utf8");
		let calls = 0;
		const publish = (body: string, receipt: string): { title: string; body: string } => {
			calls += 1;
			const prepared = JSON.parse(readFileSync(receipt, "utf8")) as { title: string };
			return { title: prepared.title, body };
		};
		const prepare = (stage: string, input: string) => {
			const body = join(directory, `${stage}.md`);
			const receipt = `${body}.receipt.json`;
			const snapshot = join(directory, `${stage}-snapshot.json`);
			writeFileSync(publication, input, "utf8");
			const generated = execute(contentEntry, ["--input", publication, "--output", body]);
			if (generated.status !== 0) return { generated, body, receipt: undefined, snapshot: undefined };
			const prepared = runCli(
				[
					"prepare-snapshot",
					"--receipt",
					receipt,
					"--body",
					body,
					"--inventory",
					inventory,
					"--paths",
					paths,
					"--output",
					snapshot,
				],
				directory,
			);
			expect(prepared.status).toBe(0);
			const scan = execute(scanEntry, ["--policy", policy, "--snapshot", snapshot]);
			expect(scan.status).toBe(0);
			expect(JSON.parse(scan.stdout)).toMatchObject({ matches: [] });
			return { generated, body, receipt, snapshot };
		};
		const created = prepare("initial", JSON.stringify(creation));
		expect(created.generated.status).toBe(0);
		expect(calls).toBe(0);
		const initialReceipt = JSON.parse(readFileSync(created.receipt!, "utf8")) as { title: string };
		expect(initialReceipt).toEqual(createPreparedReceipt(createPublicationTitle()));
		const published = publish(readFileSync(created.body, "utf8"), created.receipt!);
		expect(calls).toBe(1);
		const metadata = createMetadata({ body: published.body });
		metadata.title = published.title;
		const baseline = join(directory, "baseline.json");
		const current = join(directory, "current.json");
		writeFileSync(baseline, JSON.stringify(metadata), "utf8");
		writeFileSync(current, JSON.stringify(metadata), "utf8");
		const verified = runCli(
			["verify", "--baseline", baseline, "--current", current, "--body", created.body],
			directory,
		);
		expect(verified.status).toBe(0);
		expect(verified.stdout).toBe('{"status": "prepared", "command": "verify"}\n');

		const review = createReviewPublicationDocument(creation);
		const updated = prepare("review", JSON.stringify(review));
		expect(updated.generated.status).toBe(0);
		const publishedReview = publish(readFileSync(updated.body, "utf8"), updated.receipt!);
		expect(calls).toBe(2);
		const reviewMetadata = createMetadata({ body: publishedReview.body });
		reviewMetadata.title = publishedReview.title;
		writeFileSync(current, JSON.stringify(reviewMetadata), "utf8");
		const reviewVerified = runCli(
			["verify", "--baseline", baseline, "--current", current, "--body", updated.body],
			directory,
		);
		expect(reviewVerified.status).toBe(0);

		const invalid = prepare("invalid", createUndecodablePublicationText());
		expect(invalid.generated.status).not.toBe(0);
		expect(calls).toBe(2);
		expect(existsSync(invalid.body)).toBe(false);
	}, 30_000);

	it("prepares the local snapshot and reports the prepared status", () => {
		const directory = makeDirectory();
		const handoff = createPublicationHandoff();
		const receipt = join(directory, "receipt.json");
		const body = join(directory, "pr-working-body.md");
		const inventory = join(directory, "inventory.json");
		const paths = join(directory, "paths.json");
		const output = join(directory, "snapshot.json");
		writeFileSync(receipt, handoff.receipt, "utf8");
		writeFileSync(body, handoff.body, "utf8");
		writeFileSync(inventory, JSON.stringify(createLocalInventory()), "utf8");
		writeFileSync(paths, JSON.stringify(createPaths()), "utf8");

		const run = runCli(
			[
				"prepare-snapshot",
				"--receipt",
				receipt,
				"--body",
				body,
				"--inventory",
				inventory,
				"--paths",
				paths,
				"--output",
				output,
			],
			directory,
		);

		expect(run.status).toBe(0);
		expect(run.stdout).toBe('{"status": "prepared", "command": "prepare-snapshot"}\n');
		expect(run.stderr).toBe("");
		expect(readFileSync(output, "utf8")).toBe(`${JSON.stringify(createLocalSnapshot(), null, 2)}\n`);
		expect(JSON.parse(readFileSync(output, "utf8"))).toEqual(createLocalSnapshot());
	});

	it("prepares a real local inventory from one committed repository and reports the prepared status", () => {
		const directory = makeDirectory();
		const handoff = createPublicationHandoff();
		const repository = createCommittedRepository(join(directory, "repository"));
		const receipt = join(directory, "receipt.json");
		const body = join(directory, "pr-working-body.md");
		const output = join(directory, "snapshot.json");
		writeFileSync(receipt, handoff.receipt, "utf8");
		writeFileSync(body, handoff.body, "utf8");

		const run = runCli(
			[
				"prepare-local",
				"--pr",
				"80",
				"--base",
				repository.base,
				"--receipt",
				receipt,
				"--body",
				body,
				"--output",
				output,
			],
			repository.directory,
			createFixtureEnvironment(),
		);

		expect(run.status).toBe(0);
		expect(run.stdout).toBe('{"status": "prepared", "command": "prepare-local"}\n');
		expect(run.stderr).toBe("");
		const snapshot = JSON.parse(readFileSync(output, "utf8")) as {
			head_sha: string;
			base: string;
			changed_files: Array<{ path: string; content: string }>;
		};
		expect(snapshot.head_sha).toBe(repository.head);
		expect(snapshot.base).toBe(repository.base);
		expect(snapshot.changed_files.map((file) => file.path)).toEqual(repository.changedPaths);
		expect(snapshot.changed_files.find((file) => file.path === GIT_CHANGED_BINARY_PATH)?.content).toBe("");
		expect(snapshot.changed_files.find((file) => file.path === GIT_SOURCE_PATH)?.content).toBe(GIT_CHANGED_CONTENT);
	}, 30_000);

	it("prepares and scans a binary-only local inventory", () => {
		const directory = makeDirectory();
		const handoff = createPublicationHandoff();
		const repository = createBinaryOnlyRepository(join(directory, "repository"));
		const receipt = join(directory, "receipt.json");
		const body = join(directory, "pr-working-body.md");
		const output = join(directory, "snapshot.json");
		const policy = join(directory, "policy.json");
		writeFileSync(receipt, handoff.receipt, "utf8");
		writeFileSync(body, handoff.body, "utf8");
		writeFileSync(policy, JSON.stringify(createPolicy()), "utf8");

		const run = runCli(
			[
				"prepare-local",
				"--pr",
				"80",
				"--base",
				repository.base,
				"--receipt",
				receipt,
				"--body",
				body,
				"--output",
				output,
			],
			repository.directory,
			createFixtureEnvironment(),
		);

		expect(run.status).toBe(0);
		expect(run.stdout).toBe('{"status": "prepared", "command": "prepare-local"}\n');
		const snapshot = JSON.parse(readFileSync(output, "utf8")) as {
			changed_files: Array<{ path: string; content: string }>;
		};
		expect(snapshot.changed_files).toEqual([{ path: GIT_CHANGED_BINARY_PATH, content: "" }]);

		const scan = spawnSync(
			process.execPath,
			[join(skillRoot, "scripts", "scan_attribution.ts"), "--policy", policy, "--snapshot", output],
			{ cwd: directory, encoding: "utf8" },
		);
		expect(scan.status).toBe(0);
		expect(JSON.parse(scan.stdout)).toMatchObject({ matches: [] });
	}, 30_000);

	it("refuses a text change whose committed body is not valid UTF-8", () => {
		const directory = makeDirectory();
		const handoff = createPublicationHandoff();
		const repository = createMalformedTextRepository(join(directory, "repository"));
		const receipt = join(directory, "receipt.json");
		const body = join(directory, "pr-working-body.md");
		const output = join(directory, "snapshot.json");
		writeFileSync(receipt, handoff.receipt, "utf8");
		writeFileSync(body, handoff.body, "utf8");

		const run = runCli(
			[
				"prepare-local",
				"--pr",
				"80",
				"--base",
				repository.base,
				"--receipt",
				receipt,
				"--body",
				body,
				"--output",
				output,
			],
			repository.directory,
			createFixtureEnvironment(),
		);

		expect(run.status).toBe(2);
		expect(run.stdout).toBe("");
		expect(run.stderr).toBe("git read failure: git output was not valid UTF-8\n");
		expect(existsSync(output)).toBe(false);
	}, 30_000);

	it("rejects a path inventory that is not the exact diff inventory", () => {
		const directory = makeDirectory();
		const handoff = createPublicationHandoff();
		const receipt = join(directory, "receipt.json");
		const body = join(directory, "pr-working-body.md");
		const inventory = join(directory, "inventory.json");
		const paths = join(directory, "paths.json");
		const output = join(directory, "snapshot.json");
		writeFileSync(receipt, handoff.receipt, "utf8");
		writeFileSync(body, handoff.body, "utf8");
		writeFileSync(inventory, JSON.stringify(createLocalInventory()), "utf8");
		writeFileSync(paths, JSON.stringify(createUnexactPathInventory()), "utf8");

		const run = runCli(
			[
				"prepare-snapshot",
				"--receipt",
				receipt,
				"--body",
				body,
				"--inventory",
				inventory,
				"--paths",
				paths,
				"--output",
				output,
			],
			directory,
		);

		expect(run.status).toBe(1);
		expect(run.stdout).toBe(
			'{"code": "SNAPSHOT_PATHS_MISMATCH", "message": "snapshot paths must equal the exact diff inventory"}\n',
		);
		expect(run.stderr).toBe("");
		expect(existsSync(output)).toBe(false);
	});

	it("rejects a receipt that is not the prepared status and title pair", () => {
		const directory = makeDirectory();
		const handoff = createPublicationHandoff();
		const receipt = join(directory, "receipt.json");
		const body = join(directory, "pr-working-body.md");
		const inventory = join(directory, "inventory.json");
		const paths = join(directory, "paths.json");
		const output = join(directory, "snapshot.json");
		writeFileSync(receipt, createReceiptWithUndeclaredField(), "utf8");
		writeFileSync(body, handoff.body, "utf8");
		writeFileSync(inventory, JSON.stringify(createLocalInventory()), "utf8");
		writeFileSync(paths, JSON.stringify(createPaths()), "utf8");

		const run = runCli(
			[
				"prepare-snapshot",
				"--receipt",
				receipt,
				"--body",
				body,
				"--inventory",
				inventory,
				"--paths",
				paths,
				"--output",
				output,
			],
			directory,
		);

		expect(run.status).toBe(1);
		expect(run.stdout).toBe(
			'{"code": "PUBLICATION_DIVERGED", "message": "generated publication receipt must carry exactly a prepared status and a title"}\n',
		);
		expect(run.stderr).toBe("");
		expect(existsSync(output)).toBe(false);
	});

	it("assembles a scanner snapshot from a supplied complete snapshot", () => {
		const directory = makeDirectory();
		const collected = join(directory, "collected.json");
		const paths = join(directory, "paths.json");
		const output = join(directory, "snapshot.json");
		writeFileSync(collected, JSON.stringify(createSnapshot()), "utf8");
		writeFileSync(paths, JSON.stringify(createPaths()), "utf8");

		const run = runCli(["snapshot", "--input", collected, "--paths", paths, "--output", output], directory);

		expect(run.status).toBe(0);
		expect(run.stdout).toBe('{"status": "prepared", "command": "snapshot"}\n');
		expect(run.stderr).toBe("");
		expect(readFileSync(output, "utf8")).toBe(`${JSON.stringify(createSnapshot(), null, 2)}\n`);
	});

	it("verifies an unchanged persisted capture and rejects a diverged one", () => {
		const directory = makeDirectory();
		const baseline = join(directory, "baseline.json");
		const current = join(directory, "current.json");
		const body = join(directory, "pr-working-body.md");
		writeFileSync(baseline, JSON.stringify(createMetadata()), "utf8");
		writeFileSync(current, JSON.stringify(createMetadata()), "utf8");
		writeFileSync(body, createBody(), "utf8");
		const arguments_ = ["verify", "--baseline", baseline, "--current", current, "--body", body];

		const verified = runCli(arguments_, directory);

		expect(verified.status).toBe(0);
		expect(verified.stdout).toBe('{"status": "prepared", "command": "verify"}\n');
		expect(verified.stderr).toBe("");

		writeFileSync(current, JSON.stringify(createMetadata({ body: "Changed remotely" })), "utf8");
		const diverged = runCli(arguments_, directory);

		expect(diverged.status).toBe(1);
		expect(diverged.stdout).toBe(
			'{"code": "READBACK_DIVERGED", "message": "persisted body differs from the intended publication"}\n',
		);
		expect(diverged.stderr).toBe("");
	});

	it("reports every rejected command line with its usage line and diagnostic", () => {
		const directory = makeDirectory();
		const cases = [
			{
				name: "a command whose option value is not a positive integer",
				args: ["prepare-local", "--pr", "0"],
				stderr:
					"usage: prepare_pr_evidence.ts prepare-local --pr PR --base BASE --receipt RECEIPT --body BODY --output OUTPUT\n" +
					"prepare_pr_evidence.ts prepare-local: error: argument --pr: a positive integer is required: 0\n",
			},
			{
				name: "a command line that names no command",
				args: [],
				stderr:
					"usage: prepare_pr_evidence.ts <command> [options]\n" +
					"prepare_pr_evidence.ts: error: the following arguments are required: command\n",
			},
			{
				name: "a command name outside the four composed commands",
				args: ["publish"],
				stderr:
					"usage: prepare_pr_evidence.ts <command> [options]\n" +
					"prepare_pr_evidence.ts: error: argument command: invalid choice: 'publish' " +
					"(choose from 'snapshot', 'prepare-snapshot', 'prepare-local', 'verify')\n",
			},
			{
				name: "the retired publication-comparison command",
				args: ["verify-publication"],
				stderr:
					"usage: prepare_pr_evidence.ts <command> [options]\n" +
					"prepare_pr_evidence.ts: error: argument command: invalid choice: 'verify-publication' " +
					"(choose from 'snapshot', 'prepare-snapshot', 'prepare-local', 'verify')\n",
			},
		];

		for (const testCase of cases) {
			const run = runCli(testCase.args, directory);

			expect(run.status, testCase.name).toBe(2);
			expect(run.stdout, testCase.name).toBe("");
			expect(run.stderr, testCase.name).toBe(testCase.stderr);
		}
	});

	it("refuses the retired publication and digest arguments", () => {
		const directory = makeDirectory();
		const handoff = createPublicationHandoff();
		const receipt = join(directory, "receipt.json");
		const body = join(directory, "pr-working-body.md");
		const inventory = join(directory, "inventory.json");
		const paths = join(directory, "paths.json");
		const output = join(directory, "snapshot.json");
		writeFileSync(receipt, handoff.receipt, "utf8");
		writeFileSync(body, handoff.body, "utf8");
		writeFileSync(inventory, JSON.stringify(createLocalInventory()), "utf8");
		writeFileSync(paths, JSON.stringify(createPaths()), "utf8");
		const cases = [
			{
				name: "the retired publication input argument",
				extra: ["--publication", join(directory, "publication.json")],
			},
			{
				name: "the retired receipt digest argument",
				extra: ["--receipt-sha256", "f".repeat(64)],
			},
			{
				name: "the retired working body argument",
				extra: ["--working-body", body],
			},
		];

		for (const testCase of cases) {
			const run = runCli(
				[
					"prepare-snapshot",
					"--receipt",
					receipt,
					"--body",
					body,
					"--inventory",
					inventory,
					"--paths",
					paths,
					"--output",
					output,
					...testCase.extra,
				],
				directory,
			);

			expect(run.status, testCase.name).toBe(2);
			expect(run.stdout, testCase.name).toBe("");
			expect(run.stderr, testCase.name).toContain("unrecognized arguments: ");
			expect(existsSync(output), testCase.name).toBe(false);
		}
	});

	it("reports an unreadable input as an input/output failure", () => {
		const directory = makeDirectory();
		const input = join(directory, "absent-input.json");
		const paths = join(directory, "absent-paths.json");
		const output = join(directory, "snapshot.json");

		const run = runCli(["snapshot", "--input", input, "--paths", paths, "--output", output], directory);

		// The fixed contract is the `input/output failure: ` prefix and exit status 2;
		// the detail after the prefix is this runtime's own error wording.
		expect(run.status).toBe(2);
		expect(run.stdout).toBe("");
		expect(run.stderr).toBe(`input/output failure: ENOENT: no such file or directory, open '${input}'\n`);
		expect(existsSync(output)).toBe(false);
	});

	it("leaves an existing output untouched and reports an input/output failure", () => {
		const directory = makeDirectory();
		const handoff = createPublicationHandoff();
		const receipt = join(directory, "receipt.json");
		const body = join(directory, "pr-working-body.md");
		const inventory = join(directory, "inventory.json");
		const paths = join(directory, "paths.json");
		const output = join(directory, "snapshot.json");
		writeFileSync(receipt, handoff.receipt, "utf8");
		writeFileSync(body, handoff.body, "utf8");
		writeFileSync(inventory, JSON.stringify(createLocalInventory()), "utf8");
		writeFileSync(paths, JSON.stringify(createPaths()), "utf8");
		writeFileSync(output, "existing\n", "utf8");

		const run = runCli(
			[
				"prepare-snapshot",
				"--receipt",
				receipt,
				"--body",
				body,
				"--inventory",
				inventory,
				"--paths",
				paths,
				"--output",
				output,
			],
			directory,
		);

		// The fixed contract is the `input/output failure: ` prefix and exit status 2;
		// the detail after the prefix is this runtime's own error wording.
		expect(run.status).toBe(2);
		expect(run.stdout).toBe("");
		expect(run.stderr.startsWith("input/output failure: ")).toBe(true);
		expect(readFileSync(output, "utf8")).toBe("existing\n");
	});
});
