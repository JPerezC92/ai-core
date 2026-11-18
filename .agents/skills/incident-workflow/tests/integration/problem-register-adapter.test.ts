import { mkdtempSync, rmSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";
import { afterEach, describe, expect, it } from "vitest";

import { Filesystem } from "#scripts/incident_workflow_pkg/infrastructure/filesystem.ts";
import { makeRegister, makeRegisterRow } from "#tests/support/incident-validator-fixtures.ts";

const roots: string[] = [];

function temporaryRoot(): string {
	const root = mkdtempSync(join(tmpdir(), "incident-register-test-"));
	roots.push(root);
	return root;
}

afterEach(() => {
	for (const root of roots.splice(0)) rmSync(root, { recursive: true, force: true });
});

describe("problem register adapter", () => {
	it("parses the rows a present register declares", () => {
		const path = join(temporaryRoot(), "problems.md");
		writeFileSync(path, makeRegister(makeRegisterRow(), makeRegisterRow({ id: "P-002", team: "dev" })), "utf8");

		const rows = new Filesystem().loadProblemRegister(path);

		expect(rows.map((row) => row.id)).toEqual(["P-001", "P-002"]);
		expect(rows[0]?.isIncident).toBe(true);
		expect(rows[0]?.lifecycle).toBe("active");
		expect(rows[0]?.isExactMatchEligible).toBe(true);
		expect(rows[1]?.isIncident).toBe(false);
	});

	it("reads an absent register as no rows", () => {
		const path = join(temporaryRoot(), "problems.md");

		expect(new Filesystem().loadProblemRegister(path)).toEqual([]);
	});
});
