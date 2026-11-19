/**
 * End to end: Workflow A — initial synchronization.
 *
 * One behavioral concern — a destination that holds none of the managed files
 * is enrolled by one assembled run, and that single operation creates the
 * managed files at their expected destination paths with their required
 * contents in all three binding modes, together with the managed directory
 * structure, the reconciliation report and the reconciliation blocker.
 *
 * Several files, paths and contents of that one workflow are asserted here on
 * purpose: they are one operation's observable result, not one case per rule.
 * The source is a disposable representative tree, never the checkout, and the
 * destination is a temporary directory the fixture owns (T18).
 */

import { readFile, stat } from "node:fs/promises";
import { basename, join } from "node:path";

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

/** A shared document the registry clears as a region. */
const SHARED_REGION_FILE = ".aicore/core/knowledge/agents.md";

/** The managed template the registry clears as a raw file, asserted literally. */
const RAW_TEMPLATE = ".aicore/core/odd/tasks/_template.md";

/** The managed templates the registry clears as raw files. */
const RAW_FILES = [RAW_TEMPLATE, ".aicore/core/odd/features/_template.md"] as const;

/** A skill directory root cleared as raw, delivered to its canonical path. */
const RAW_SKILL_FILE = ".agents/skills/git-commit/SKILL.md";

/** The project configuration the registry clears as a merge. */
const MERGE_FILE = ".opencode/opencode.jsonc";

/** The reconciliation report `init` writes beside the bindings file. */
const REPORT_FILE = join(".aicore", "reconciliation", "init.yaml");

/** The binder every enrolled destination carries. */
const BINDINGS_FILE = join(".aicore", "core.yaml");

/** The credential placeholder OpenCode enrollment creates. */
const SECRET_FILE = join(".secrets", "context7-api-key");

/** A literal line the shipped template must carry. */
const TEMPLATE_LINE = "## Specs";

/** The literal core-region markers every enrolled root file is written between. */
const CORE_BEGIN = "<!-- core:begin -->";
const CORE_END = "<!-- core:end -->";

/** The literal project-region markers a markerless destination's body is moved into. */
const PROJECT_BEGIN = "<!-- project:begin -->";
const PROJECT_END = "<!-- project:end -->";

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

/** Read one member of a parsed JSON value, or `undefined`. */
function member(value: unknown, key: string): unknown {
	return typeof value === "object" && value !== null ? (value as Record<string, unknown>)[key] : undefined;
}

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
	];
}

describe("initial synchronization creates the managed destination", () => {
	test("one enrollment delivers every managed file, its exact content, and the managed structure", async () => {
		const fixture = await createRepresentativeFixture();
		try {
			const enrolled = await invokeWithRevision(enrollArguments(fixture), fixture);
			expect(enrolled.status, `init stderr: ${enrolled.stderr}`).toBe(0);
			expect(enrolled.stdout).toMatch(/initialized/);

			// Raw mode: the delivered file is the source's bytes, exactly, and still
			// carries the content the source declares.
			for (const path of [...RAW_FILES, RAW_SKILL_FILE]) {
				expect(await readFile(join(fixture.destination, path), "utf8"), path).toBe(
					await readFile(join(fixture.source, path), "utf8"),
				);
			}
			expect(await readFile(join(fixture.destination, RAW_TEMPLATE), "utf8")).toContain(TEMPLATE_LINE);

			// Region mode: the delivered core region is the source core, byte for
			// byte, between the destination's own markers.
			for (const path of [ROOT_FILE, SHARED_REGION_FILE]) {
				const sourceText = await readFile(join(fixture.source, path), "utf8");
				const deliveredText = await readFile(join(fixture.destination, path), "utf8");
				const source = betweenMarkerLines(sourceText, CORE_BEGIN, CORE_END);
				const delivered = betweenMarkerLines(deliveredText, CORE_BEGIN, CORE_END);
				expect(delivered, path).toBe(source);
			}

			// The markerless destination's previous body was preserved into its
			// project region rather than discarded: the whole body, byte for byte.
			const deliveredRoot = await readFile(join(fixture.destination, ROOT_FILE), "utf8");
			expect(betweenMarkerLines(deliveredRoot, PROJECT_BEGIN, PROJECT_END)).toBe(fixture.body);

			// Merge mode: the created destination carries the source's top-level
			// values, and its QMD index is this destination folder's name.
			const deliveredConfig = parseJsoncObject(await readFile(join(fixture.destination, MERGE_FILE), "utf8"));
			const sourceConfig = parseJsoncObject(await readFile(join(fixture.source, MERGE_FILE), "utf8"));
			expect(deliveredConfig, "the delivered configuration must be a JSONC object").not.toBeNull();
			expect(member(deliveredConfig?.value, "$schema")).toBe(member(sourceConfig?.value, "$schema"));
			const qmdCommand = member(member(member(deliveredConfig?.value, "mcp"), "servers"), "qmd") as
				| Record<string, unknown>
				| undefined;
			expect(Array.isArray(member(qmdCommand, "command"))).toBe(true);
			expect(member(qmdCommand, "command") as readonly unknown[]).toContain("--index");
			expect(member(qmdCommand, "command") as readonly unknown[]).toContain(basename(fixture.destination));

			// The managed directory structure exists: the binder, the reconciliation
			// report location, and the credential placeholder the profile creates.
			expect((await stat(join(fixture.destination, ".aicore"))).isDirectory()).toBe(true);
			expect((await stat(join(fixture.destination, BINDINGS_FILE))).isFile()).toBe(true);
			expect((await stat(join(fixture.destination, REPORT_FILE))).isFile()).toBe(true);
			expect((await stat(join(fixture.destination, SECRET_FILE))).isFile()).toBe(true);

			const report = await readFile(join(fixture.destination, REPORT_FILE), "utf8");
			expect(report).toContain(REVISION);
			expect(report).toContain(ROOT_FILE);

			// The root runtime file carries the reconciliation blocker the report's
			// pending list corresponds to.
			const rootText = await readFile(join(fixture.destination, ROOT_FILE), "utf8");
			expect(rootText).toContain("<!-- core:reconcile:begin -->");
			expect(rootText).toContain("<!-- core:reconcile:end -->");
		} finally {
			await fixture.dispose();
		}
	});
});
