import { mkdtempSync, rmSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";
import { afterEach, describe, expect, it } from "vitest";
import { main as validateFeatureFiles } from "#scripts/validate_feature_file.ts";
import { makeFeatureFile } from "#tests/support/feature-file-fixtures.ts";

const temporaryDirectories: string[] = [];

function makeDirectory(): string {
	const directory = mkdtempSync(join(tmpdir(), "odd-workflow-feature-file-cli-"));
	temporaryDirectories.push(directory);
	return directory;
}

afterEach(() => {
	for (const directory of temporaryDirectories.splice(0)) {
		rmSync(directory, { recursive: true, force: true });
	}
});

// The entry point's own rendered output, exit statuses and argument diagnostics are
// proven once, by the spawned source-only copy in
// tests/e2e/feature-file-validator-isolated-copy.test.ts, and the findings the
// validator reports are proven by the use case at tests/unit. What remains here is the
// behaviour the entry point alone owns: the output it has already printed stays
// printed when a later read fails.
describe("validate_feature_file CLI entry point with the real filesystem adapter", () => {
	it("preserves earlier output when a later UTF-8 read fails", () => {
		const directory = makeDirectory();
		const earlier = join(directory, "a.md");
		writeFileSync(earlier, makeFeatureFile(), "utf8");
		writeFileSync(join(directory, "z.md"), Buffer.from([0xff]));
		const lines: string[] = [];

		expect(() => validateFeatureFiles([directory], (line) => lines.push(line))).toThrow();
		expect(lines).toEqual([`ok ${earlier} — status: partial`]);
	});
});
