import { describe, expect, it } from "vitest";
import { ValidateFeatureFiles } from "#scripts/feature_file_validation/application/validate_feature_files.ts";
import {
	InvalidFeatureFileError,
	NoFeatureFileDocumentsError,
	ValidFeatureFile,
} from "#scripts/feature_file_validation/domain/records.ts";
import type { PathComparisonPolicy } from "#scripts/feature_file_validation/domain/rules.ts";
import { assessFeatureFile, validateFeatureFile } from "#scripts/feature_file_validation/domain/rules.ts";
import {
	FeatureFileSourceFake,
	featureFileApostropheFixture,
	featureFileCaseOrderFixture,
	featureFileDirectoryFixture,
	featureFileFailingFixture,
	featureFileSingleFixture,
	featureFileTemplateOnlyFixture,
} from "#tests/support/feature-file-fixtures.ts";

const caseSensitivePolicy: PathComparisonPolicy = { caseSensitive: true };
const caseInsensitivePolicy: PathComparisonPolicy = { caseSensitive: false };

describe("ValidateFeatureFiles.execute", () => {
	it("sorts candidates, skips the template, and returns the derived status", () => {
		const fixture = featureFileDirectoryFixture();
		const source = new FeatureFileSourceFake(fixture.references, fixture.documents);

		const results = [...new ValidateFeatureFiles(source, caseSensitivePolicy).execute("features")];

		expect(source.reads).toEqual(["features/a.md", "features/z.md"]);
		expect(results).toEqual([
			new ValidFeatureFile("features/a.md", "partial"),
			new ValidFeatureFile("features/z.md", "partial"),
		]);
	});

	it("returns typed no-files and invalid outcomes", () => {
		const emptyFixture = featureFileTemplateOnlyFixture();
		const empty = new FeatureFileSourceFake(emptyFixture.references, emptyFixture.documents);
		const invalidFixture = featureFileSingleFixture("achieved");
		const invalid = new FeatureFileSourceFake(invalidFixture.references, invalidFixture.documents);

		expect([...new ValidateFeatureFiles(empty, caseSensitivePolicy).execute("features")]).toEqual([
			new NoFeatureFileDocumentsError(),
		]);
		const [rejected] = [...new ValidateFeatureFiles(invalid, caseSensitivePolicy).execute("features")];
		expect(rejected).toBeInstanceOf(InvalidFeatureFileError);
		expect(rejected).toMatchObject({
			path: "features/a.md",
			findings: [
				"feature-file-status-derivation: declared status 'achieved' does not match the status derived from the ticks 'partial'",
			],
		});
	});

	it("reports the double-quoted diagnostics for an apostrophe-bearing status and mark", () => {
		const fixture = featureFileApostropheFixture();
		const source = new FeatureFileSourceFake(fixture.references, fixture.documents);

		const [rejected] = [...new ValidateFeatureFiles(source, caseSensitivePolicy).execute("features")];

		expect(rejected).toBeInstanceOf(InvalidFeatureFileError);
		expect(rejected).toMatchObject({
			path: "features/a.md",
			findings: [
				"feature-file-status: status must be one of 'achieved', 'partial' or 'not started'; found \"achieved's\"",
				"feature-file-requirement-mark: requirement 1 carries an unknown mark \"owner's mark\"; marks are 'upstream', 'upstream · local detail', 'upstream · narrowed', 'local' or 'local · conflicts'",
			],
		});
	});

	it("yields earlier results before a later read exception", () => {
		const failure = new Error("later feature file cannot be read");
		const fixture = featureFileFailingFixture();
		const source = new FeatureFileSourceFake(fixture.references, fixture.documents, failure);
		const iterator = new ValidateFeatureFiles(source, caseSensitivePolicy).execute("features");

		expect(iterator.next().value).toEqual(new ValidFeatureFile("features/a.md", "partial"));
		expect(() => iterator.next()).toThrow(failure);
	});

	it("orders references by the injected path case-sensitivity policy", () => {
		const fixture = featureFileCaseOrderFixture();

		const insensitive = new FeatureFileSourceFake(fixture.references, fixture.documents);
		const insensitiveResults = [
			...new ValidateFeatureFiles(insensitive, caseInsensitivePolicy).execute("features"),
		];
		expect(insensitiveResults).toHaveLength(2);
		expect(insensitive.reads).toEqual(["features/a.md", "features/B.md"]);

		const sensitive = new FeatureFileSourceFake(fixture.references, fixture.documents);
		const sensitiveResults = [...new ValidateFeatureFiles(sensitive, caseSensitivePolicy).execute("features")];
		expect(sensitiveResults).toHaveLength(2);
		expect(sensitive.reads).toEqual(["features/B.md", "features/a.md"]);
	});
});

describe("durable feature-file validation of fenced content", () => {
	/** A fully ticked feature file: its derived status is "achieved". */
	function achieved(): string {
		return [
			"# Sample feature",
			"",
			"The feature states what it is in one paragraph.",
			"",
			"**Status:** achieved",
			"",
			"## Requirements",
			"",
			"- [x] R1 — the requirement remains true.",
			"",
		].join("\n");
	}

	it("does not derive status from a fenced requirement line", () => {
		const text = achieved().replace(
			"- [x] R1 — the requirement remains true.",
			["- [x] R1 — the requirement remains true.", "```text", "- [ ] R2 — a quoted example", "```"].join("\n"),
		);
		expect(validateFeatureFile(text)).toStrictEqual([]);
		// The derived status itself, not only the findings, must ignore the fenced line.
		expect(assessFeatureFile(text).status).toBe("achieved");
	});

	it("reports no derived status when no genuine requirement exists", () => {
		const text = [
			"# Sample feature",
			"",
			"The feature states what it is in one paragraph.",
			"",
			"**Status:** not started",
			"",
			"## Requirements",
			"",
			"```text",
			"- [x] R1 — a quoted example",
			"```",
			"",
		].join("\n");
		expect(assessFeatureFile(text).status).toBeNull();
		expect(validateFeatureFile(text)).toContain(
			"feature-file-requirements: '## Requirements' needs at least one '- [ ] R<n> — <requirement>' line",
		);
	});

	it("reports a genuine placeholder and ignores a fenced one", () => {
		const fenced = achieved().replace(
			"- [x] R1 — the requirement remains true.",
			["- [x] R1 — the requirement remains true.", "```text", "<placeholder>", "```"].join("\n"),
		);
		expect(validateFeatureFile(fenced)).toStrictEqual([]);
		const genuine = achieved().replace(
			"- [x] R1 — the requirement remains true.",
			["- [x] R1 — the requirement remains true.", "<placeholder>"].join("\n"),
		);
		expect(validateFeatureFile(genuine)).toStrictEqual([
			"feature-file-unfilled-placeholder: unfilled placeholder: <placeholder>",
		]);
	});

	it("does not let a fenced requirement satisfy the requirement obligation", () => {
		const text = [
			"# Sample feature",
			"",
			"The feature states what it is in one paragraph.",
			"",
			"**Status:** not started",
			"",
			"## Requirements",
			"",
			"```text",
			"- [ ] R1 — a quoted example",
			"```",
			"",
		].join("\n");
		expect(validateFeatureFile(text)).toContain(
			"feature-file-requirements: '## Requirements' needs at least one '- [ ] R<n> — <requirement>' line",
		);
	});

	it("reports no unknown mark for a fenced example", () => {
		const text = achieved().replace(
			"- [x] R1 — the requirement remains true.",
			[
				"- [x] R1 — the requirement remains true.",
				"```text",
				"- [x] R2 `bogus mark` — a quoted example",
				"```",
			].join("\n"),
		);
		expect(validateFeatureFile(text)).toStrictEqual([]);
	});

	it("reports no duplicate requirements heading for a fenced example", () => {
		const text = achieved().replace(
			"## Requirements",
			["```text", "## Requirements", "```", "", "## Requirements"].join("\n"),
		);
		expect(validateFeatureFile(text)).toStrictEqual([]);
	});

	it("does not report the completion sheet for a fenced example", () => {
		const text = achieved().replace(
			"- [x] R1 — the requirement remains true.",
			["- [x] R1 — the requirement remains true.", "```text", "## Completion", "```"].join("\n"),
		);
		expect(validateFeatureFile(text)).toStrictEqual([]);
	});

	it("rejects a feature file whose fence never closes", () => {
		const text = achieved().replace(
			"- [x] R1 — the requirement remains true.",
			["- [x] R1 — the requirement remains true.", "```text", "quoted"].join("\n"),
		);
		expect(validateFeatureFile(text)).toStrictEqual([
			"feature-file-unclosed-fence: unclosed code fence opened at line 10 with 3 backtick character(s); add the closing fence",
		]);
	});
});
