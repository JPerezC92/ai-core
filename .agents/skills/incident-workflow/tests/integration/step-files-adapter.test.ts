import { mkdirSync, mkdtempSync, rmSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";
import { afterEach, describe, expect, it } from "vitest";

import { Filesystem } from "#scripts/incident_workflow_pkg/infrastructure/filesystem.ts";

const roots: string[] = [];

function temporaryAnalysis(): string {
	const root = mkdtempSync(join(tmpdir(), "incident-step-files-test-"));
	roots.push(root);
	const analysis = join(root, "analysis");
	mkdirSync(analysis, { recursive: true });
	return analysis;
}

afterEach(() => {
	for (const root of roots.splice(0)) rmSync(root, { recursive: true, force: true });
});

describe("step files adapter", () => {
	it("returns the step files the analysis directory holds", () => {
		const analysis = temporaryAnalysis();
		writeFileSync(join(analysis, "01-identify.md"), "identify", "utf8");
		writeFileSync(join(analysis, "03-synthesize.md"), "synthesize", "utf8");

		expect(new Filesystem().loadStepFiles(analysis)).toEqual({
			"01-identify.md": "identify",
			"03-synthesize.md": "synthesize",
		});
	});

	it("omits a step file that is not written yet", () => {
		const analysis = temporaryAnalysis();
		writeFileSync(join(analysis, "01-identify.md"), "identify", "utf8");

		const contents = new Filesystem().loadStepFiles(analysis);

		expect(Object.hasOwn(contents, "02-investigate.md")).toBe(false);
		expect(Object.hasOwn(contents, "03-synthesize.md")).toBe(false);
		expect(contents["01-identify.md"]).toBe("identify");
	});
});
