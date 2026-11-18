import { mkdtempSync, rmSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";
import { afterEach, describe, expect, it } from "vitest";
import { main as validateFeatures } from "#scripts/validate_feature.ts";
import { makeFeature } from "#tests/support/feature-fixtures.ts";

const temporaryDirectories: string[] = [];

function makeDirectory(): string {
	const directory = mkdtempSync(join(tmpdir(), "odd-workflow-validator-"));
	temporaryDirectories.push(directory);
	return directory;
}

afterEach(() => {
	for (const directory of temporaryDirectories.splice(0)) {
		rmSync(directory, { recursive: true, force: true });
	}
});

// The entry point's own rendered output, exit statuses and argument diagnostics are
// proven once, by the spawned source-only copy in tests/e2e/isolated-copy.test.ts, and
// the findings the validator reports are proven by the use case at tests/unit. What
// remains here is the behaviour the entry point alone owns: the output it has already
// printed stays printed when a later read fails.
describe("validate_feature CLI entry point with the real filesystem adapter", () => {
	it("preserves earlier output when a later filesystem read fails", () => {
		const directory = makeDirectory();
		const earlier = join(directory, "a.md");
		writeFileSync(earlier, makeFeature(), "utf8");
		writeFileSync(join(directory, "z.md"), Buffer.from([0xff]));
		const lines: string[] = [];

		expect(() => validateFeatures([directory], (line) => lines.push(line))).toThrow();
		expect(lines).toEqual([`ok ${earlier}`]);
	});
});
