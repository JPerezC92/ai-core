import { mkdtempSync, rmSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";
import { afterEach, describe, expect, it } from "vitest";

import { Filesystem } from "#scripts/incident_workflow_pkg/infrastructure/filesystem.ts";
import { makeRegister, makeRegisterRow } from "#tests/support/incident-validator-fixtures.ts";

const roots: string[] = [];

function temporaryRoot(): string {
	const root = mkdtempSync(join(tmpdir(), "incident-problem-rows-test-"));
	roots.push(root);
	return root;
}

afterEach(() => {
	for (const root of roots.splice(0)) rmSync(root, { recursive: true, force: true });
});

describe("declared problem rows adapter", () => {
	it("reads the rows a present register declares", () => {
		const path = join(temporaryRoot(), "problems.md");
		writeFileSync(
			path,
			makeRegister(
				makeRegisterRow({ id: "P-001", symptom: "S-05" }),
				makeRegisterRow({ id: "P-002", team: "bogus" }),
			),
			"utf8",
		);

		expect(new Filesystem().loadProblemRows(path)).toEqual([
			{ id: "P-001", symptom: "S-05" },
			{ id: "P-002", symptom: "S-05" },
		]);
	});

	it("reads an absent register as no rows at all", () => {
		const path = join(temporaryRoot(), "problems.md");

		expect(new Filesystem().loadProblemRows(path)).toBeNull();
	});
});
