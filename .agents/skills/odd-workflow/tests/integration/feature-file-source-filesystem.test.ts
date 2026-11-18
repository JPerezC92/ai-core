import { mkdtempSync, rmSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";
import { afterEach, describe, expect, it } from "vitest";
import { ValidateFeatureFiles } from "#scripts/feature_file_validation/application/validate_feature_files.ts";
import type { FeatureFileSource } from "#scripts/feature_file_validation/domain/ports.ts";
import { ValidFeatureFile } from "#scripts/feature_file_validation/domain/records.ts";
import type { PathComparisonPolicy } from "#scripts/feature_file_validation/domain/rules.ts";
import { FilesystemFeatureFileSource } from "#scripts/feature_file_validation/infrastructure/filesystem.ts";
import { makeFeatureFile } from "#tests/support/feature-file-fixtures.ts";

const temporaryDirectories: string[] = [];

function makeDirectory(): string {
	const directory = mkdtempSync(join(tmpdir(), "odd-workflow-feature-file-source-"));
	temporaryDirectories.push(directory);
	return directory;
}

/** The host path-comparison policy: Windows paths compare case-insensitively. */
const hostPathComparisonPolicy: PathComparisonPolicy = {
	caseSensitive: process.platform !== "win32",
};

afterEach(() => {
	for (const directory of temporaryDirectories.splice(0)) {
		rmSync(directory, { recursive: true, force: true });
	}
});

// The adapter's discovery, normalization and strict-UTF-8 read behaviours are the
// shared implementation's, and they are covered once in feature-source-filesystem.
// What is distinct here is this adapter's own contract: the FeatureFileSource port
// it declares, and the feature-file application that consumes it through that port.
describe("FilesystemFeatureFileSource as the feature-file source port", () => {
	it("satisfies the FeatureFileSource port the feature-file application composes", () => {
		const source: FeatureFileSource = new FilesystemFeatureFileSource();
		expect(typeof source.discover).toBe("function");
		expect(typeof source.read).toBe("function");

		const directory = makeDirectory();
		const file = join(directory, "feature.md");
		writeFileSync(file, makeFeatureFile(), "utf8");

		const operation = new ValidateFeatureFiles(source, hostPathComparisonPolicy);
		const results = [...operation.execute(directory)];

		expect(results).toHaveLength(1);
		expect(results[0]).toBeInstanceOf(ValidFeatureFile);
		expect(results[0]).toMatchObject({ path: file, status: "partial" });
	});
});
