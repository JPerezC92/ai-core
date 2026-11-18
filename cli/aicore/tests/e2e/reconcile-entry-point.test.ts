/**
 * End to end: the assembled entry point's `reconcile` command.
 *
 * One behavioral concern — the command the operator actually runs: `reconcile`
 * validates its own arguments, resolves `--target`, builds the read-only readers
 * over the real checkout, renders the proposal through the delivery edge, and
 * maps the proposal onto its exit status without touching the destination.
 *
 * This is the entry-point case the two reconciliation classification modules do
 * not provide: they exercise the composed operation below `main` against a
 * disposable synthetic source root, which the assembled command cannot be given
 * because it resolves the real checkout. The fixture here is a destination whose
 * binding names a source that genuinely exists in this checkout and is cleared in
 * its shipped registry, so the assembled command classifies it for real.
 */

import { copyFile, mkdir, readdir, readFile } from "node:fs/promises";
import { join } from "node:path";

import { afterEach, describe, expect, test } from "vitest";

import { BINDINGS_RELATIVE_PATH } from "#domain/constants.ts";
import type { StreamWriter } from "#delivery/stream-writer.ts";
import { YamlBindingsStore } from "#infrastructure/synchronization/bindings-store.ts";
import { CHECKOUT, createFixture, type Fixture } from "#support/aicore-cli.e2e-harness.ts";
import { makeBindingsDocument } from "#support/synchronization.factory.ts";

/** The module the CLI entry point is loaded from, the way the parity seam loads it. */
const ENTRY_POINT_MODULE = new URL("../../src/main.ts", import.meta.url);

/** The one cleared source this destination is bound to. */
const BOUND_SOURCE = "AGENTS.md";

/** A writer that records the bytes the entry point wrote. */
class RecordingWriter implements StreamWriter {
	#stdout = "";
	#stderr = "";

	get stdout(): string {
		return this.#stdout;
	}

	get stderr(): string {
		return this.#stderr;
	}

	writeStdout(lines: readonly string[]): void {
		for (const line of lines) {
			this.#stdout += `${line}\n`;
		}
	}

	writeStderr(lines: readonly string[]): void {
		for (const line of lines) {
			this.#stderr += `${line}\n`;
		}
	}
}

/** Invoke the assembled entry point in process, capturing its bytes. */
async function invokeEntryPoint(arguments_: readonly string[]): Promise<{
	status: number;
	stdout: string;
	stderr: string;
}> {
	const loaded = (await import(ENTRY_POINT_MODULE.href)) as {
		main?: (
			argv: readonly string[],
			environment: Readonly<Record<string, string | undefined>>,
			writer: StreamWriter,
		) => Promise<number>;
	};
	const entryPoint = loaded.main;
	if (typeof entryPoint !== "function") {
		throw new Error(`${ENTRY_POINT_MODULE.pathname} must export main()`);
	}
	const writer = new RecordingWriter();
	const status = await entryPoint(arguments_, {}, writer);
	return { status, stdout: writer.stdout, stderr: writer.stderr };
}

/** Every file under a root, with its bytes, so "unchanged" is a comparison. */
async function snapshotTree(target: string): Promise<ReadonlyMap<string, string>> {
	const collected = new Map<string, string>();
	const walk = async (directory: string, prefix: string): Promise<void> => {
		for (const entry of await readdir(directory, { withFileTypes: true })) {
			const path = prefix === "" ? entry.name : `${prefix}/${entry.name}`;
			if (entry.isDirectory()) {
				await walk(join(directory, entry.name), path);
				continue;
			}
			collected.set(path, (await readFile(join(directory, entry.name))).toString("hex"));
		}
	};
	await walk(target, "");
	return collected;
}

let fixture: Fixture | undefined;

afterEach(async () => {
	await fixture?.dispose();
	fixture = undefined;
});

describe("the reconcile command at the entry point", () => {
	test("refuses a missing --target, then proposes for the target and writes nothing", async () => {
		const created = await createFixture();
		fixture = created;
		const { destination } = created;

		// `reconcile` validates its own arguments: the target is named, never
		// remembered, and its absence is invalid input.
		const refused = await invokeEntryPoint(["reconcile"]);
		expect(refused.status).toBe(2);
		expect(refused.stdout).toBe("");
		expect(refused.stderr).toMatch(/requires --target/);

		// A destination bound to a source that exists in this checkout and is cleared
		// in its shipped registry: the current copy is managed and kept.
		await copyFile(join(CHECKOUT, BOUND_SOURCE), join(destination, BOUND_SOURCE));
		await mkdir(join(destination, ".aicore"), { recursive: true });
		await new YamlBindingsStore().save(
			join(destination, BINDINGS_RELATIVE_PATH),
			makeBindingsDocument({
				editor: "opencode",
				bindings: [{ source: BOUND_SOURCE, destinations: [BOUND_SOURCE], declaredMode: "region" }],
			}),
		);

		const before = await snapshotTree(destination);

		const result = await invokeEntryPoint(["reconcile", "--target", destination]);

		const entryLine = `reconcile: ${"kept".padEnd(10)} ${"managed".padEnd(17)} ${BOUND_SOURCE} — matches ${BOUND_SOURCE}`;

		expect(result.stderr).toBe("");
		expect(result.status).toBe(0);
		const lines = result.stdout.split("\n").filter((line) => line !== "");
		// The proposal names the target this run was given, and what it proposes.
		expect(lines[0]).toBe(`reconcile: proposal for ${destination} (read-only: nothing was written)`);
		expect(lines).toContain(entryLine);
		expect(lines).toContain("reconcile: managed 1, superseded 0, locally modified 0, destination-owned 0.");
		expect(lines).toContain("reconcile: nothing requires the destination owner's action.");

		// The read-only promise, asserted over the whole tree rather than repeated.
		expect(await snapshotTree(destination)).toEqual(before);
	});
});
