/**
 * End to end: the assembled `sync` command's report for a run that raises.
 *
 * One behavioral concern — a write that fails on the filesystem is rendered the
 * way a failed write has always been rendered: the I/O diagnostic, then the
 * sentence that nothing is claimed current, at the drift exit status. The failure
 * is provoked through the real CLI with a condition the engine's own predicate
 * classifies, not simulated: after a destination is enrolled, its `.gitignore`
 * is replaced by a directory, so the next run's ignore-rule write raises `EISDIR`
 * on every platform that refuses to open a directory for writing.
 *
 * This protects the boundary the delivery edge owns: the exception stays an
 * exception (contract C5) and the operator's lines do not depend on which module
 * caught it.
 */

import { mkdir, readFile, rm, stat, writeFile } from "node:fs/promises";
import { join, resolve } from "node:path";

import { afterEach, describe, expect, test } from "vitest";

import { REVISION, createFixture, invoke, type Fixture } from "#support/aicore-cli.e2e-harness.ts";

let fixture: Fixture | undefined;

afterEach(async () => {
	await fixture?.dispose();
	fixture = undefined;
});

describe("a sync run whose write raises on the filesystem", () => {
	test("reports the I/O diagnostic and the nothing-is-current sentence at the drift status", async () => {
		const created = await createFixture();
		fixture = created;
		const { destination } = created;

		// Enroll from the checkout the way the operator does, so the destination
		// holds a bound payload, its OpenCode configuration and the ignore rule.
		const enrollment = await invoke(["sync", "--target", destination, "--editor", "opencode"], {
			fixture: created,
			revision: REVISION,
		});
		expect(enrollment.status, `enrollment stderr: ${enrollment.stderr}`).toBe(1);
		expect((await stat(join(destination, ".gitignore"))).isFile()).toBe(true);
		expect((await stat(join(destination, ".opencode", "opencode.jsonc"))).isFile()).toBe(true);

		// A directory where the ignore rule's file must be written: the next run's
		// write is refused by the filesystem, which is the classified condition.
		await rm(join(destination, ".gitignore"), { force: true });
		await mkdir(join(destination, ".gitignore"));
		await writeFile(join(destination, ".gitignore", "not-a-rule"), "occupied\n", "utf8");

		const result = await invoke(["sync", "--target", destination], { fixture: created, revision: REVISION });

		const lines = result.stderr.split("\n").filter((line) => line !== "");
		expect(result.stdout).toBe("");
		expect(result.status, `stderr: ${result.stderr}`).toBe(1);
		expect(lines).toHaveLength(2);
		expect(lines[0]).toMatch(/^core-sync I\/O error: /u);
		expect(lines[0]).toContain(".gitignore");
		expect(lines[1]).toBe(
			`sync: synchronization of ${resolve(destination)} failed with status 1; nothing is claimed current.`,
		);

		// The destination is left exactly as the failure found it: no partial claim.
		expect(await readFile(join(destination, ".gitignore", "not-a-rule"), "utf8")).toBe("occupied\n");
	});
});
