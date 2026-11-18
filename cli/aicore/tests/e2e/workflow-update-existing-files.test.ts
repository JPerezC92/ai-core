/**
 * End to end: Workflow B — updating existing files.
 *
 * One behavioral concern — a destination that already carries managed files is
 * updated by one assembled run after the source changes meaningfully: the
 * managed files reach their new expected contents in all three binding modes,
 * while destination-owned content (the project region, a project-owned record,
 * an unmanaged file, and merge destination-only keys and comments) is preserved
 * byte for byte.
 *
 * Preservation is asserted by comparing exact bytes, never by absence. The
 * source is a disposable representative tree, never the checkout, and the
 * destination is a temporary directory the fixture owns (T18).
 */

import { mkdir, readFile, writeFile } from "node:fs/promises";
import { join } from "node:path";

import { describe, expect, test } from "vitest";

import { parseJsoncObject } from "#domain/synchronization/jsonc.ts";
import {
	REVISION,
	createRepresentativeFixture,
	invokeWithRevision,
	type RepresentativeFixture,
} from "#support/aicore-cli.e2e-harness.ts";

/** The destination root runtime file, delivered as a region. */
const ROOT_FILE = "AGENTS.md";

/** The managed template the registry clears as a raw file. */
const RAW_FILE = ".aicore/core/odd/tasks/_template.md";

/** The project configuration the registry clears as a merge. */
const MERGE_FILE = ".opencode/opencode.jsonc";

/** The binder every enrolled destination carries. */
const BINDINGS_FILE = join(".aicore", "core.yaml");

/** A destination-owned record under a project-owned root. */
const PROJECT_OWNED_FILE = "odd/tasks/2026-01-01-destination-change.md";

/** A destination-owned file no binding names. */
const UNMANAGED_FILE = "NOTES.md";

/** The destination-owned project content planted before enrollment. */
const PROJECT_OWNED_CONTENT = ["# Destination change", "", "> **Status:** active", ""].join("\n");

/** The unmanaged destination file's content. */
const UNMANAGED_CONTENT = "# Notes\n\nA destination-owned file synchronization never binds.\n";

/** A comment the destination owns; a merge write must keep it. */
const DESTINATION_COMMENT = "// destination-owned comment";

/** A literal line the core update adds to the source region. */
const CORE_UPDATE_LINE = "A line the core update added.";

/** The merge key the source change adds. */
const SOURCE_MERGE_KEY = "workflowMarker";

/** The value the changed source carries for that key. */
const SOURCE_MERGE_VALUE = "after-source-change";

/** The destination-only merge key a merge write must keep. */
const DESTINATION_MERGE_KEY = "destinationOnly";

/** The literal core-region markers the root runtime file is written between. */
const CORE_BEGIN = "<!-- core:begin -->";
const CORE_END = "<!-- core:end -->";

/**
 * The offset where the line that is exactly `marker` starts, or `-1`.
 *
 * The marker is matched as a whole line, so `from` must be a line boundary: an
 * inline mention inside prose is never taken for the marker.
 */
function markerLineStart(text: string, marker: string, from = 0): number {
	if (text.startsWith(`${marker}\n`, from)) {
		return from;
	}
	const prefixed = text.indexOf(`\n${marker}\n`, from);
	return prefixed < 0 ? -1 : prefixed + 1;
}

/** The slice between two literal marker lines, excluding both marker lines. */
function betweenMarkerLines(text: string, begin: string, end: string): string {
	const beginStart = markerLineStart(text, begin);
	const endStart = beginStart < 0 ? -1 : markerLineStart(text, end, beginStart + 1);
	if (beginStart < 0 || endStart < 0) {
		throw new Error(`the document does not carry the literal marker lines ${begin} and ${end}`);
	}
	return text.slice(beginStart + begin.length + 1, endStart);
}

/** The slice after a literal marker line, that line's terminator included. */
function afterMarkerLine(text: string, marker: string): string {
	const start = markerLineStart(text, marker);
	if (start < 0) {
		throw new Error(`the document does not carry the literal marker line ${marker}`);
	}
	return text.slice(start + marker.length);
}

/** Read one member of a parsed JSON value, or `undefined`. */
function member(value: unknown, key: string): unknown {
	return typeof value === "object" && value !== null ? (value as Record<string, unknown>)[key] : undefined;
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
		"--editor",
		"opencode",
	];
}

/** Plant the destination-owned files the update must not disturb. */
async function plantDestinations(fixture: RepresentativeFixture): Promise<void> {
	await mkdir(join(fixture.destination, "odd", "tasks"), { recursive: true });
	await writeFile(join(fixture.destination, PROJECT_OWNED_FILE), PROJECT_OWNED_CONTENT, "utf8");
	await writeFile(join(fixture.destination, UNMANAGED_FILE), UNMANAGED_CONTENT, "utf8");
	await mkdir(join(fixture.destination, ".opencode"), { recursive: true });
	await writeFile(
		join(fixture.destination, MERGE_FILE),
		["{", `  ${DESTINATION_COMMENT}`, `  "${DESTINATION_MERGE_KEY}": { "kept": true }`, "}", ""].join("\n"),
		"utf8",
	);
}

/**
 * Change the source meaningfully, once: a region line, a raw file line, and a
 * new merge key the destination does not hold.
 */
async function changeSource(fixture: RepresentativeFixture): Promise<void> {
	const agentsPath = join(fixture.source, ROOT_FILE);
	const agents = await readFile(agentsPath, "utf8");
	expect(agents).toContain("<!-- core:end -->");
	await writeFile(agentsPath, agents.replace("<!-- core:end -->", `${CORE_UPDATE_LINE}\n<!-- core:end -->`), "utf8");

	const rawPath = join(fixture.source, RAW_FILE);
	await writeFile(rawPath, `${await readFile(rawPath, "utf8")}Raw update marker.\n`, "utf8");

	const configPath = join(fixture.source, MERGE_FILE);
	const config = await readFile(configPath, "utf8");
	const anchor = `"$schema": "https://opencode.ai/config.json",`;
	expect(config).toContain(anchor);
	await writeFile(
		configPath,
		config.replace(anchor, `${anchor}\n  "${SOURCE_MERGE_KEY}": "${SOURCE_MERGE_VALUE}",`),
		"utf8",
	);
}

describe("updating an enrolled destination rewrites managed content and preserves the rest", () => {
	test("one apply delivers the changed source and leaves every destination-owned byte untouched", async () => {
		const fixture = await createRepresentativeFixture({ editor: "opencode" });
		try {
			await plantDestinations(fixture);

			const enrolled = await invokeWithRevision([...argumentsFor("init", fixture), "--bind-cleared"], fixture);
			expect(enrolled.status, `init stderr: ${enrolled.stderr}`).toBe(0);

			// The destination already carries managed files; capture the project
			// region the update must preserve before the source changes.
			const installedRoot = await readFile(join(fixture.destination, ROOT_FILE), "utf8");
			const installedProjectRegion = afterMarkerLine(installedRoot, CORE_END);

			await changeSource(fixture);

			const applied = await invokeWithRevision(argumentsFor("apply", fixture), fixture);
			expect(applied.status, `apply stderr: ${applied.stderr}`).toBe(0);
			expect(applied.stdout).toMatch(/applied/);

			// Region mode is updated to the new source core, byte for byte.
			const source = betweenMarkerLines(
				await readFile(join(fixture.source, ROOT_FILE), "utf8"),
				CORE_BEGIN,
				CORE_END,
			);
			const deliveredRoot = await readFile(join(fixture.destination, ROOT_FILE), "utf8");
			const deliveredCore = betweenMarkerLines(deliveredRoot, CORE_BEGIN, CORE_END);
			expect(deliveredCore).toBe(source);
			expect(deliveredCore).toContain(CORE_UPDATE_LINE);

			// The destination's project region is preserved byte for byte.
			const deliveredProjectRegion = afterMarkerLine(deliveredRoot, CORE_END);
			expect(deliveredProjectRegion).toBe(installedProjectRegion);
			expect(deliveredProjectRegion).toContain("# Fixture project");

			// Raw mode is updated to the new source bytes, exactly.
			expect(await readFile(join(fixture.destination, RAW_FILE), "utf8")).toBe(
				await readFile(join(fixture.source, RAW_FILE), "utf8"),
			);

			// Merge mode takes the new source key while the destination's own key
			// and comment survive.
			const mergedText = await readFile(join(fixture.destination, MERGE_FILE), "utf8");
			const merged = parseJsoncObject(mergedText);
			expect(merged, "the merged configuration must be a JSONC object").not.toBeNull();
			expect(member(merged?.value, SOURCE_MERGE_KEY)).toBe(SOURCE_MERGE_VALUE);
			expect(member(member(merged?.value, DESTINATION_MERGE_KEY), "kept")).toBe(true);
			expect(mergedText).toContain(DESTINATION_COMMENT);

			// A project-owned record and an unmanaged file are untouched, by bytes.
			expect(await readFile(join(fixture.destination, PROJECT_OWNED_FILE), "utf8")).toBe(PROJECT_OWNED_CONTENT);
			expect(await readFile(join(fixture.destination, UNMANAGED_FILE), "utf8")).toBe(UNMANAGED_CONTENT);
		} finally {
			await fixture.dispose();
		}
	});
});
