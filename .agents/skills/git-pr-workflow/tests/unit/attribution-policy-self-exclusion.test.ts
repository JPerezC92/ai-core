import { describe, expect, it } from "vitest";
import {
	loadApprovedPolicy,
	makeAttributionLine,
	makeChangedFile,
	makeChangedFiles,
	makeSnapshotWithArtifactContent,
	scanAttribution,
} from "#tests/support/attribution-fixtures.ts";

describe("policy self-exclusion", () => {
	it("excludes only the exact policy path and reports the exclusion", () => {
		const policy = loadApprovedPolicy();
		const matchingLine = makeAttributionLine(policy);
		const excludedPath = policy.self_excluded_file;
		const snapshot = makeSnapshotWithArtifactContent(
			"pr-title",
			"",
			makeChangedFiles(
				makeChangedFile(excludedPath, matchingLine),
				makeChangedFile(`./${excludedPath}`, matchingLine),
			),
		);

		const result = scanAttribution(snapshot, policy);

		expect(result.exclusions).toEqual([{ path: excludedPath, reason: "policy self-exclusion" }]);
		expect(result.matches.map((match) => match.path)).toEqual([`./${excludedPath}`]);
	});

	it("normalizes the slash direction of the excluded path", () => {
		const policy = loadApprovedPolicy();
		const windowsPath = policy.self_excluded_file.replace(/\//gu, "\\");
		const snapshot = makeSnapshotWithArtifactContent(
			"pr-title",
			"",
			makeChangedFiles(makeChangedFile(windowsPath, makeAttributionLine(policy))),
		);

		const result = scanAttribution(snapshot, policy);

		expect(result.exclusions).toEqual([{ path: windowsPath, reason: "policy self-exclusion" }]);
		expect(result.matches).toEqual([]);
	});
});
