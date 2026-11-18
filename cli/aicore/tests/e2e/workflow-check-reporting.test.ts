/**
 * End to end: the check reporting workflow.
 *
 * One behavioral concern — what a drift check reports to the operator and what
 * it leaves behind. The two user-facing outcomes are distinct: a destination
 * whose managed content matches its source is reported current at exit 0, and a
 * destination whose managed content differs is reported as drift at exit 1.
 * Neither outcome may write anything, so each case compares the destination
 * tree's exact bytes before and after the run.
 *
 * The fixtures bind raw files only, because raw drift is content drift the run
 * can satisfy without the destination-owned `pending` reconciliation cycle; the
 * source and destination are disposable (T18).
 */

import { mkdir, readFile, writeFile } from "node:fs/promises";
import { join } from "node:path";

import { describe, expect, test } from "vitest";

import {
	REVISION,
	createRepresentativeFixture,
	invokeWithRevision,
	type RepresentativeFixture,
} from "#support/aicore-cli.e2e-harness.ts";
import { snapshotTree } from "#support/tree-snapshot.ts";

/** The raw file a drift edit changes and the check must report. */
const DRIFTED_FILE = ".aicore/core/odd/tasks/_template.md";

/** The raw-cleared files the bindings declare, source and destination alike. */
const BOUND_FILES = [DRIFTED_FILE, ".aicore/core/odd/features/_template.md"] as const;

/** The binder every destination carries. */
const BINDINGS_FILE = join(".aicore", "core.yaml");

/** A literal line a drift edit appends to a destination file. */
const DRIFT_LINE = "A destination edit the check must notice.\n";

/** The bindings of a destination that manages one raw file per bound path. */
function rawBindings(): string {
	const lines = ["schema: 1", `core_revision: ${REVISION}`, "editor: opencode", "bindings:"];
	for (const path of BOUND_FILES) {
		lines.push(`  - source: ${path}`, "    destinations:", `      - ${path}`);
	}
	lines.push("pending: []", "");
	return lines.join("\n");
}

/** Seed the destination's own bindings document before the first run. */
async function seedBindings(fixture: RepresentativeFixture): Promise<void> {
	await mkdir(join(fixture.destination, ".aicore"), { recursive: true });
	await writeFile(join(fixture.destination, BINDINGS_FILE), rawBindings(), "utf8");
}

function argumentsFor(command: string, fixture: RepresentativeFixture): string[] {
	return [
		command,
		"--source",
		fixture.source,
		"--destination",
		fixture.destination,
		"--bindings",
		join(fixture.destination, BINDINGS_FILE),
		"--source-revision",
		REVISION,
	];
}

/** Enroll the raw-bound files in one run, so the destination is synchronized. */
async function enroll(fixture: RepresentativeFixture): Promise<void> {
	await seedBindings(fixture);
	const enrolled = await invokeWithRevision(argumentsFor("init", fixture), fixture);
	expect(enrolled.status, `init stderr: ${enrolled.stderr}`).toBe(0);
}

describe("a drift check reports the destination state and writes nothing", () => {
	test("a current destination reports current at exit 0 and leaves the tree untouched", async () => {
		const fixture = await createRepresentativeFixture();
		try {
			await enroll(fixture);
			const before = await snapshotTree(fixture.destination);

			const checked = await invokeWithRevision(argumentsFor("check", fixture), fixture);
			expect(checked.status, `check stderr: ${checked.stderr}`).toBe(0);
			// The reported outcome is the literal fact `current`.
			expect(checked.stdout.trim()).toBe("current");

			expect(await snapshotTree(fixture.destination)).toEqual(before);
		} finally {
			await fixture.dispose();
		}
	});

	test("a destination whose managed content differs reports drift at exit 1 and leaves the tree untouched", async () => {
		const fixture = await createRepresentativeFixture();
		try {
			await enroll(fixture);
			await writeFile(
				join(fixture.destination, DRIFTED_FILE),
				`${await readFile(join(fixture.destination, DRIFTED_FILE), "utf8")}${DRIFT_LINE}`,
				"utf8",
			);
			const before = await snapshotTree(fixture.destination);

			const checked = await invokeWithRevision(argumentsFor("check", fixture), fixture);
			expect(checked.status, `check stdout: ${checked.stdout}`).toBe(1);
			expect(checked.stderr).toMatch(/raw drift/);

			expect(await snapshotTree(fixture.destination)).toEqual(before);
		} finally {
			await fixture.dispose();
		}
	});
});
