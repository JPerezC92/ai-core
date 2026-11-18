/**
 * End to end: an unsafe invocation is refused before anything is written.
 *
 * One behavioral concern — an assembled run is handed a declaration that would
 * take a managed path outside the destination tree, and the entry point refuses
 * it with exit 2 and its diagnostic instead of enrolling or delivering anything.
 * The refusal happens before any write, so the destination tree is byte-identical
 * before and after.
 *
 * The destination and source are disposable fixtures; the checkout is never a
 * target (T18).
 */

import { join } from "node:path";

import { describe, expect, test } from "vitest";

import {
	REVISION,
	createRepresentativeFixture,
	invokeWithRevision,
	type RepresentativeFixture,
} from "#support/aicore-cli.e2e-harness.ts";
import { snapshotTree } from "#support/tree-snapshot.ts";

/** The binder every destination carries. */
const BINDINGS_FILE = join(".aicore", "core.yaml");

/** A declared path that escapes the destination tree and must be refused. */
const ESCAPING_PATH = "../outside-the-project.md";

/** The unsafe `--bind` declaration, as an operator would mistype it. */
const UNSAFE_DECLARATION = `${ESCAPING_PATH}=${ESCAPING_PATH}`;

function enrollArguments(fixture: RepresentativeFixture): string[] {
	return [
		"init",
		"--source",
		fixture.source,
		"--destination",
		fixture.destination,
		"--bindings",
		join(fixture.destination, BINDINGS_FILE),
		"--source-revision",
		REVISION,
		"--editor",
		"opencode",
		"--bind-cleared",
		"--bind",
		UNSAFE_DECLARATION,
	];
}

describe("an unsafe invocation is refused without writing", () => {
	test("a declaration that escapes the destination is refused at exit 2 and the tree stays byte-identical", async () => {
		const fixture = await createRepresentativeFixture();
		try {
			const before = await snapshotTree(fixture.destination);

			const refused = await invokeWithRevision(enrollArguments(fixture), fixture);

			expect(refused.status, `stderr: ${refused.stderr}`).toBe(2);
			expect(refused.stderr).toMatch(/invalid init binding/);
			expect(refused.stderr).toMatch(/malformed or unsafe binding declaration/);
			// A reported failure, not an unhandled crash.
			expect(refused.stderr).not.toMatch(/at file:|Error \[|node:internal/);

			expect(await snapshotTree(fixture.destination)).toEqual(before);
		} finally {
			await fixture.dispose();
		}
	});
});
