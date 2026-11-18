/**
 * End-to-end: synchronization never disturbs project-owned artifacts.
 *
 * One behavioral concern (S8) — with a real enrollment, real `apply` and real
 * `check` over disposable fixtures, a destination's own ODD records and
 * diagnostic registers keep byte-identical contents across synchronization
 * while AICore-managed payloads still arrive. The source is a representative
 * tree, never the checkout, and the destination is a temporary directory the
 * harness owns.
 *
 * The repository-artifact facts are asserted here as delivered effects of the
 * assembled run: the cleared managed templates and diagnostic catalogs arrive in
 * the form the registry declares for them (raw bytes, or a core region), the
 * project-owned roots receive nothing at all, and the delivered OpenCode
 * configuration's secret reference names this project's own `.secrets/`
 * directory — the directory the same run creates.
 */

import { mkdir, readFile, rm, stat, writeFile } from "node:fs/promises";
import { isAbsolute, join, relative, resolve } from "node:path";

import { describe, expect, test } from "vitest";

import { parseJsoncObject } from "#domain/synchronization/jsonc.ts";
import {
	CHECKOUT,
	REVISION,
	createRepresentativeFixture,
	invoke,
	type RepresentativeFixture,
} from "#support/aicore-cli.e2e-harness.ts";

/** Project-owned files a destination might hold before synchronization. */
const PROJECT_FILES: Readonly<Record<string, string>> = {
	"odd/tasks/2026-01-01-destination-change.md": [
		"# Destination change",
		"",
		"> **Status:** active",
		"",
		"## Specs",
		"",
		"- S1 — a destination-authored requirement survives synchronization.",
		"",
	].join("\n"),
	"odd/features/destination-capability.md": [
		"# Destination capability",
		"",
		"A capability this destination owns.",
		"",
		"**Status:** partial",
		"",
		"## Requirements",
		"",
		"- [x] R1 — a destination-authored requirement stays exactly as written.",
		"- [ ] R2 — an unticked requirement stays unticked.",
		"",
	].join("\n"),
	"incidents/diagnostics/problems.md": [
		"| ID | Date | Team | Symptom | System | Module | Problem | Discriminators | Exclusions | Evidence | Root cause | Lifecycle | Allow_exact | Status |",
		"|---|---|---|---|---|---|---|---|---|---|---|---|---|---|",
		"| P-001 | 2026-01-01 | incident | S-05, LOCAL:S-01 | billing | ingest | destination-owned pattern | host=cdn-a | host=cdn-b | case:incidents/2026-01-01 #1/ticket_1.md | cache miss | active | yes | open |",
		"",
	].join("\n"),
	"incidents/diagnostics/symptoms.md": [
		"| ID | Symptom / error signature | Required signals | Exclusions | Canonical diagnostic | Canonical fix routing |",
		"|---|---|---|---|---|---|",
		"| LOCAL:S-01 | destination-specific signature | a local signal | a local exclusion | local diagnostic | local routing |",
		"",
	].join("\n"),
	"incidents/2026-01-01 #1/ticket_1.md": ["# Ticket 1", "", "A destination-owned incident record.", ""].join("\n"),
};

/** The managed templates the registry clears as raw files. */
const MANAGED_TEMPLATES = [".aicore/core/odd/tasks/_template.md", ".aicore/core/odd/features/_template.md"] as const;

/** The diagnostic catalogs the registry clears as a region-mode directory root. */
const DIAGNOSTIC_CATALOGS = [
	".aicore/core/knowledge/diagnostics/symptoms.md",
	".aicore/core/knowledge/diagnostics/problems.md",
	".aicore/core/knowledge/diagnostics/diagnostic-guidance.md",
] as const;

/** The local register templates the incident skill ships as raw files. */
const INCIDENT_TEMPLATES = [
	".agents/skills/incident-workflow/references/local-symptoms-template.md",
	".agents/skills/incident-workflow/references/local-problems-template.md",
] as const;

/** The shipped OpenCode configuration and the secret reference it carries. */
const CONFIGURATION_PATH = join(".opencode", "opencode.jsonc");
const SECRET_REFERENCE = "{file:../.secrets/context7-api-key}";
const SECRET_RELATIVE_PATH = join(".secrets", "context7-api-key");

function argumentsFor(command: string, fixture: RepresentativeFixture): string[] {
	return [
		command,
		"--source",
		fixture.source,
		"--destination",
		fixture.destination,
		"--bindings",
		join(fixture.destination, ".aicore", "core.yaml"),
		"--source-revision",
		REVISION,
	];
}

/** Plant every project-owned fixture file and return its bytes. */
async function plant(fixture: RepresentativeFixture): Promise<Map<string, string>> {
	const planted = new Map<string, string>();
	for (const [path, content] of Object.entries(PROJECT_FILES)) {
		const target = join(fixture.destination, path);
		await mkdir(join(target, ".."), { recursive: true });
		await writeFile(target, content, "utf8");
		planted.set(path, content);
	}
	return planted;
}

async function readAll(fixture: RepresentativeFixture, paths: Iterable<string>): Promise<Map<string, string>> {
	const current = new Map<string, string>();
	for (const path of paths) {
		current.set(path, await readFile(join(fixture.destination, path), "utf8"));
	}
	return current;
}

/** Read one member of a parsed JSON value, or `undefined`. */
function member(value: unknown, key: string): unknown {
	return typeof value === "object" && value !== null ? (value as Record<string, unknown>)[key] : undefined;
}

describe("synchronization preserves project-owned artifacts", () => {
	test("enrollment, apply and check leave destination records byte-identical and still deliver managed payloads", async () => {
		const fixture = await createRepresentativeFixture({ editor: "opencode" });
		try {
			const enrollment = await invoke(
				[...argumentsFor("init", fixture), "--bind-cleared", "--editor", "opencode"],
				{ fixture, revision: REVISION },
			);
			expect(enrollment.status).toBe(0);

			const planted = await plant(fixture);

			const applied = await invoke(argumentsFor("apply", fixture), { fixture, revision: REVISION });
			expect(applied.status).toBe(0);

			const afterApply = await readAll(fixture, planted.keys());
			expect([...afterApply]).toEqual([...planted]);

			const template = await readFile(
				join(fixture.destination, ".aicore", "core", "odd", "tasks", "_template.md"),
				"utf8",
			);
			expect(template).toContain("## Specs");

			const skill = await readFile(
				join(fixture.destination, ".agents", "skills", "git-commit", "SKILL.md"),
				"utf8",
			);
			expect(skill).toContain("git-commit");

			const bindings = await readFile(join(fixture.destination, ".aicore", "core.yaml"), "utf8");
			expect(bindings).not.toMatch(/- source: (odd|incidents)\//);
			expect(bindings).not.toMatch(/\n\s+- (odd|incidents)\//);

			// A freshly enrolled destination lists its region files under `pending`
			// until its owner reconciles them, so the verification reports exactly
			// that drift — not "current", and not a status this test is free to guess.
			const checked = await invoke(argumentsFor("check", fixture), { fixture, revision: REVISION });
			expect(checked.status, `check stderr: ${checked.stderr}`).toBe(1);
			expect(checked.stderr).toMatch(/pending changes/);

			const afterCheck = await readAll(fixture, planted.keys());
			expect([...afterCheck]).toEqual([...planted]);
		} finally {
			await fixture.dispose();
		}
	});

	test("the cleared templates and catalogs arrive in their declared form and the project-owned roots receive nothing", async () => {
		const fixture = await createRepresentativeFixture({ editor: "opencode" });
		try {
			const enrollment = await invoke(
				[...argumentsFor("init", fixture), "--bind-cleared", "--editor", "opencode"],
				{ fixture, revision: REVISION },
			);
			expect(enrollment.status, `init stderr: ${enrollment.stderr}`).toBe(0);

			// Raw: the delivered file is the source's bytes, exactly.
			for (const path of [...MANAGED_TEMPLATES, ...INCIDENT_TEMPLATES]) {
				const delivered = await readFile(join(fixture.destination, path), "utf8");
				expect(delivered, path).toBe(await readFile(resolve(CHECKOUT, path), "utf8"));
			}

			// Region: the delivered file carries the core region the run spliced in.
			for (const path of DIAGNOSTIC_CATALOGS) {
				const delivered = await readFile(join(fixture.destination, path), "utf8");
				expect(delivered, path).toContain("<!-- core:begin -->");
			}

			// Nothing under the project-owned roots was created or bound.
			for (const root of ["odd", "incidents"]) {
				await expect(stat(join(fixture.destination, root))).rejects.toThrow();
				expect(await readFile(join(fixture.destination, ".aicore", "core.yaml"), "utf8")).not.toMatch(
					new RegExp(`(^|[\\s-])${root}/`, "mu"),
				);
			}
		} finally {
			await fixture.dispose();
		}
	});

	test("the delivered OpenCode configuration names this project's own .secrets/, never its parent", async () => {
		const fixture = await createRepresentativeFixture({ editor: "opencode" });
		try {
			const enrollment = await invoke(
				[...argumentsFor("init", fixture), "--bind-cleared", "--editor", "opencode"],
				{ fixture, revision: REVISION },
			);
			expect(enrollment.status, `init stderr: ${enrollment.stderr}`).toBe(0);

			// A decoy beside the destination proves the reference is not resolved
			// against the project root's parent.
			await mkdir(join(fixture.root, ".secrets"), { recursive: true });
			await writeFile(join(fixture.root, SECRET_RELATIVE_PATH), "parent decoy\n", "utf8");

			const deliveredText = await readFile(join(fixture.destination, CONFIGURATION_PATH), "utf8");
			const delivered = parseJsoncObject(deliveredText);
			expect(delivered, "the delivered configuration must be a JSONC object").not.toBeNull();

			const servers = member(member(delivered?.value, "mcp"), "servers");
			const headers = member(member(servers, "context7"), "headers");
			expect(member(headers, "CONTEXT7_API_KEY")).toBe(SECRET_REFERENCE);

			const reference = SECRET_REFERENCE.slice("{file:".length, -1);
			expect(isAbsolute(reference)).toBe(false);

			const resolved = resolve(join(fixture.destination, ".opencode"), reference);
			const expected = join(fixture.destination, SECRET_RELATIVE_PATH);
			expect(resolved).toBe(expected);
			expect(resolved).not.toBe(join(fixture.root, SECRET_RELATIVE_PATH));
			expect(isAbsolute(relative(fixture.destination, resolved))).toBe(false);
			expect(relative(fixture.destination, resolved).startsWith("..")).toBe(false);

			// The same run created the credential file the reference names, empty.
			expect((await stat(resolved)).size).toBe(0);

			// Absence is absence: removing the file does not move the reference out of
			// the project, and the parent's file is never what it names.
			await rm(resolved);
			expect(resolve(join(fixture.destination, ".opencode"), reference)).toBe(expected);
			await expect(stat(resolved)).rejects.toThrow();
		} finally {
			await fixture.dispose();
		}
	});
});
