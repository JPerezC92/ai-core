import { describe, expect, it } from "vitest";
import { validateFeature } from "#scripts/feature_validation/domain/rules.ts";
import { makeFeatureWithLog } from "#tests/support/feature-fixtures.ts";

const CLOSED_WITH_GENUINE_CLOSE = ["- L1 — original request", "- L2 — Close: delivered"];
const MISSING_CLOSE_FINDING = "closed feature needs a Log 'Close:' entry";
const ACTIVE_CLOSE_FINDING = "active feature has a Log 'Close:' entry; set Status: closed";

/** The unclosed-fence findings for a document. */
function fenceFindings(text: string): string[] {
	return validateFeature(text).filter((finding) => finding.startsWith("unclosed Markdown code fence"));
}

describe("validateFeature structural interpretation of fenced content", () => {
	const FENCED = (lines: readonly string[]): string[] => ["```text", ...lines, "```"];

	it("does not report a duplicate required heading for a fenced example", () => {
		const text = makeFeatureWithLog({
			log: ["- L1 — a", "", ...FENCED(["## Tasks", "## Log", "## Specs"]), "- L2 — b"],
		});
		expect(validateFeature(text)).toStrictEqual([]);
	});

	it("does not accept a fenced Status line as the record's status", () => {
		const text = makeFeatureWithLog({ log: ["- L1 — a", "", ...FENCED(["> **Status:** closed"])] });
		expect(validateFeature(text)).toStrictEqual([]);
	});

	it("requires a genuine L1 entry when only a fenced one exists", () => {
		const text = makeFeatureWithLog({ log: ["- L2 — a", "", ...FENCED(["- L1 — quoted"])] });
		expect(validateFeature(text)).toContain("Log needs an L1 entry");
	});

	it("accepts a genuine L1 entry that follows a fenced example", () => {
		const text = makeFeatureWithLog({ log: ["", ...FENCED(["- L1 — quoted"]), "- L1 — genuine"] });
		expect(validateFeature(text)).toStrictEqual([]);
	});

	it("does not accept a fenced Tasks entry as the record's task", () => {
		const text = makeFeatureWithLog({ log: ["- L1 — a"] }).replace(
			"- T1 | S1 | route | open | commit: pending",
			"```text\n- T1 | S1 | route | done | commit: abc1234\n```",
		);
		expect(validateFeature(text)).toContain(
			"Tasks needs at least one '- T# | S# | ... | status | commit: ...' entry",
		);
	});

	it("does not accept a fenced Specs entry as the record's spec", () => {
		const text = makeFeatureWithLog({ log: ["- L1 — a"] });
		const fenced = text.replace("- S1 — A requirement.", "```text\n- S1 — quoted\n```");
		expect(validateFeature(fenced)).toContain("Specs needs at least one '- S# — ...' entry");
	});

	it("does not accept a fenced user authorization as cancellation evidence", () => {
		const text = [
			"# Sample feature",
			"",
			"> **Status:** closed",
			"> **Owner:** Cipher (Lead Orchestrator)",
			"> **Created:** 2026-11-24",
			"> **Closed:** 2026-11-24",
			"> **Disposition:** cancelled",
			"",
			"## Specs",
			"",
			"- S1 — A requirement.",
			"",
			"## Tasks",
			"",
			"- T1 | S1 | route | done | commit: abc1234",
			"",
			"## Log",
			"",
			"- L1 — a",
			"```text",
			"user authorized this cancellation",
			"```",
			"",
		].join("\n");
		expect(validateFeature(text)).toContain(
			"cancelled feature needs a Log entry recording explicit user authorization for the cancellation",
		);
	});

	it("accepts genuine user authorization recorded outside a fence", () => {
		const text = [
			"# Sample feature",
			"",
			"> **Status:** closed",
			"> **Owner:** Cipher (Lead Orchestrator)",
			"> **Created:** 2026-11-24",
			"> **Closed:** 2026-11-24",
			"> **Disposition:** cancelled",
			"",
			"## Specs",
			"",
			"- S1 — A requirement.",
			"",
			"## Tasks",
			"",
			"- T1 | S1 | route | done | commit: abc1234",
			"",
			"## Log",
			"",
			"- L1 — the user authorized this cancellation",
			"- L2 — Close: cancelled on that authorization",
			"",
		].join("\n");
		expect(validateFeature(text)).toStrictEqual([]);
	});
});

describe("validateFeature fenced Close entries", () => {
	it("accepts a closed record carrying a genuine Close entry", () => {
		expect(validateFeature(makeFeatureWithLog({ status: "closed", log: CLOSED_WITH_GENUINE_CLOSE }))).toStrictEqual(
			[],
		);
	});

	it("reports a closed record whose only Close entry is inside a balanced fence", () => {
		const text = makeFeatureWithLog({
			status: "closed",
			log: [
				"- L1 — original request",
				"- L2 — history, quoted:",
				"",
				"```text",
				"- L3 — Close: delivered",
				"```",
			],
		});
		expect(validateFeature(text)).toStrictEqual([MISSING_CLOSE_FINDING]);
	});

	it("reports the active-record diagnostic for a genuine Close entry", () => {
		expect(
			validateFeature(makeFeatureWithLog({ log: ["- L1 — original request", "- L2 — Close: delivered"] })),
		).toStrictEqual([ACTIVE_CLOSE_FINDING]);
	});

	it("ignores a Close entry that exists only inside a balanced fence on an active record", () => {
		const text = makeFeatureWithLog({
			log: [
				"- L1 — original request",
				"- L2 — history, quoted:",
				"",
				"```text",
				"- L3 — Close: delivered",
				"```",
			],
		});
		expect(validateFeature(text)).toStrictEqual([]);
	});

	it("finds the genuine Close entry that follows a balanced fence holding a Close entry", () => {
		const text = makeFeatureWithLog({
			status: "closed",
			log: [
				"- L1 — original request",
				"- L2 — history, quoted:",
				"",
				"```text",
				"- L3 — Close: not a real close",
				"```",
				"- L4 — Close: delivered",
			],
		});
		expect(validateFeature(text)).toStrictEqual([]);
	});

	it("reads a tilde-fenced Close entry as quoted content", () => {
		const text = makeFeatureWithLog({
			log: ["- L1 — original request", "- L2 — quoted:", "", "~~~text", "- L3 — Close: delivered", "~~~"],
		});
		expect(validateFeature(text)).toStrictEqual([]);
	});
});

describe("validateFeature Log section extraction", () => {
	it("does not start the Log section at a heading inside a fence", () => {
		// The only `## Log` line in this document is inside a fence, so the record has no
		// readable Log at all and a fenced Close entry cannot stand in for a genuine one.
		const specsBeforeLog = ["```text", "## Log", "- L9 — Close: quoted", "```", ""];
		const text = makeFeatureWithLog({ status: "closed", log: [], specsBeforeLog });
		expect(validateFeature(text)).toContain(MISSING_CLOSE_FINDING);
	});

	it("does not end the Log section at a required heading inside a fence", () => {
		// The duplicate heading itself is a pre-existing finding this change does not alter;
		// the property under test is that the fenced heading does not truncate the Log.
		const text = makeFeatureWithLog({
			status: "closed",
			log: [
				"- L1 — original request",
				"- L2 — quoted:",
				"",
				"```text",
				"## Tasks",
				"```",
				"- L3 — Close: delivered",
			],
		});
		expect(validateFeature(text)).not.toContain(MISSING_CLOSE_FINDING);
	});

	it("reads a genuine Close entry that follows a fence which itself contains a heading", () => {
		const text = makeFeatureWithLog({
			status: "closed",
			log: ["- L1 — original request", "```md", "## Specs", "## Tasks", "```", "- L2 — Close: delivered"],
		});
		expect(validateFeature(text)).not.toContain(MISSING_CLOSE_FINDING);
	});
});

describe("validateFeature superseded obsolescence explanations", () => {
	/** A superseded record with no Superseded-by line, so the obsolescence clause decides. */
	function supersededWith(log: readonly string[]): string {
		return [
			"# Sample feature",
			"",
			"> **Status:** closed",
			"> **Owner:** Cipher (Lead Orchestrator)",
			"> **Created:** 2026-11-24",
			"> **Closed:** 2026-11-24",
			"> **Disposition:** superseded",
			"",
			"## Specs",
			"",
			"- S1 — A requirement.",
			"",
			"## Tasks",
			"",
			"- T1 | S1 | route | done | commit: abc1234",
			"",
			"## Log",
			"",
			...log,
			"",
		].join("\n");
	}

	const SUPERSEDED_FINDING =
		"superseded feature needs a Superseded-by delivery reference or a Close entry explaining why its requirements are obsolete";

	it("accepts a genuine Close entry explaining obsolescence", () => {
		expect(
			validateFeature(supersededWith(["- L1 — a", "- L2 — Close: delivered; the requirements are obsolete"])),
		).toStrictEqual([]);
	});

	it("does not accept a fenced Close entry as the obsolescence explanation", () => {
		expect(
			validateFeature(
				supersededWith(["- L1 — a", "- L2 — quoted:", "", "```text", "- L3 — Close: obsolete", "```"]),
			),
		).toStrictEqual([SUPERSEDED_FINDING, MISSING_CLOSE_FINDING]);
	});
});

describe("validateFeature unbalanced fences", () => {
	it("rejects a record carrying the documented pre-3dd918c fence shape", () => {
		const text = makeFeatureWithLog({
			log: [
				"- L1 — original request",
				"- L2 — the record's fence defect, quoted:",
				"",
				"````markdown",
				"- L3 — a quoted entry",
				"```»",
				"- L4 — a swallowed entry",
			],
		});
		expect(fenceFindings(text)).toStrictEqual([
			"unclosed Markdown code fence opened at line 20 with 4 backtick character(s); add the closing fence",
		]);
	});

	it("rejects a record whose fence is ended by its container instead of a closer", () => {
		const text = makeFeatureWithLog({
			log: ["- L1 — a", "", "  ```text", "  inside", "- L2 — b"],
		});
		expect(fenceFindings(text).length).toBe(1);
	});

	it("rejects a record whose fence never closes before the end of the file", () => {
		const text = makeFeatureWithLog({ log: ["- L1 — a", "", "~~~text", "- L2 — swallowed"] });
		expect(fenceFindings(text)).toStrictEqual([
			"unclosed Markdown code fence opened at line 19 with 3 tilde character(s); add the closing fence",
		]);
	});

	it("accepts balanced fences in every supported container", () => {
		const cases = [
			["```text", "inside", "```"],
			["````text", "```", "inside", "````"],
			["  ```text", "  inside", "  ```"],
			["  1. step", "", "     ```json", "     { }", "     ```"],
			["  > ```text", "  > inside", "  > ```"],
			["<!--", "```", "-->"],
			["A top-level paragraph.", "", "    indented code", "    ```"],
		];
		for (const block of cases) {
			const text = makeFeatureWithLog({ log: ["- L1 — a", ...block, "- L2 — b"] });
			expect(fenceFindings(text)).toStrictEqual([]);
		}
	});
});

describe("validateFeature preserved contracts under fenced content", () => {
	it("still reads Log identifiers from outside fenced blocks", () => {
		const text = makeFeatureWithLog({
			log: ["- L1 — a", "", "```text", "- L2 — quoted, out of order in the quote", "```", "- L2 — b"],
		});
		expect(validateFeature(text)).toStrictEqual([]);
	});

	it("still rejects identifiers that descend outside fenced blocks", () => {
		const text = makeFeatureWithLog({ log: ["- L2 — a", "- L1 — b"] });
		expect(validateFeature(text)).toContain("first Log entry must be L1: L2");
	});

	it("still ignores placeholders inside fenced blocks", () => {
		const text = makeFeatureWithLog({ log: ["- L1 — a", "", "```text", "<placeholder>", "```"] });
		expect(validateFeature(text)).toStrictEqual([]);
	});
});
