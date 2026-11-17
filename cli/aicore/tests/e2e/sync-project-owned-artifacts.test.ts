/**
 * End-to-end: synchronization never disturbs project-owned artifacts.
 *
 * One behavioral concern (S8) — with a real enrollment, real `apply` and real
 * `check` over disposable fixtures, a destination's own ODD records and
 * diagnostic registers keep byte-identical contents across synchronization
 * while AICore-managed payloads still arrive. The source is a representative
 * tree, never the checkout, and the destination is a temporary directory the
 * harness owns.
 */

import { mkdir, readFile, writeFile } from "node:fs/promises";
import { join } from "node:path";

import { describe, expect, test } from "vitest";

import {
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

			const checked = await invoke(argumentsFor("check", fixture), { fixture, revision: REVISION });
			expect([0, 1]).toContain(checked.status);

			const afterCheck = await readAll(fixture, planted.keys());
			expect([...afterCheck]).toEqual([...planted]);
		} finally {
			await fixture.dispose();
		}
	});
});
