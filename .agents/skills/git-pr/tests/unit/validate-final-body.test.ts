import { describe, expect, it } from "vitest";

import { execute } from "#scripts/pr_content/application/validate_final_body.ts";
import { validatePreservation } from "#scripts/pr_content/domain/review_content_preservation.ts";
import { HEAD_SHA, makeCompletedBody, makeMetadata } from "#tests/support/review-content-fixtures.ts";

const BODY = makeCompletedBody();
const METADATA = makeMetadata();

describe("preservation of baseline content", () => {
	it("accepts an unchanged body", () => {
		expect(validatePreservation(BODY, BODY)).toBeUndefined();
	});

	it("rejects a rewritten Summary", () => {
		const changed = BODY.replace("Adds the review preparation commands.", "Different prose.");
		expect(validatePreservation(BODY, changed)?.code).toBe("BODY_INVALID");
	});

	it("accepts a checkbox change in the test plan", () => {
		const changed = BODY.replace("- [x] Run the focused suite", "- [ ] Run the focused suite");
		expect(validatePreservation(BODY, changed)).toBeUndefined();
	});

	it("rejects an added plan line", () => {
		const changed = BODY.replace(
			"- [x] Confirm the import map resolves",
			"- [x] Confirm the import map resolves\n- [x] extra item",
		);
		expect(validatePreservation(BODY, changed)?.code).toBe("BODY_INVALID");
	});

	it("accepts an unchanged body whose findings section is followed by the verdict line", () => {
		const body = [
			"## Summary",
			"",
			"- Adds the review preparation commands.",
			"",
			"## Test plan",
			"",
			"- [ ] Run the focused suite",
			"- [ ] Confirm the import map resolves",
			"",
			"## Findings / blockers",
			"",
			"No findings.",
			"",
			"[PASS] — 0 open findings",
			"",
		].join("\n");

		expect(validatePreservation(body, body)).toBeUndefined();
	});

	it("refuses a protected rewrite no supplied record scopes", () => {
		const changed = BODY.replace(
			"Adds the review preparation commands.",
			"Corrected after the user superseded the premise.",
		);

		expect(validatePreservation(BODY, changed)?.code).toBe("BODY_INVALID");
	});

	it("accepts a protected rewrite scoped to the section the user instruction names", () => {
		const changed = BODY.replace(
			"Adds the review preparation commands.",
			"Corrected after the user superseded the premise.",
		);
		const decisions = {
			notApplicable: [],
			acceptance: [],
			debt: [],
			authorizedUpdates: [
				{
					section: "Summary",
					instruction: "replace the superseded summary sentence",
					source: "the user's instruction in the PR 1 delivery conversation",
				},
			],
		};

		expect(validatePreservation(BODY, changed, decisions)).toBeUndefined();
	});

	it("still refuses a Breaking changes rewrite when only Summary is scoped", () => {
		const changed = makeCompletedBody({
			summary: "Corrected after the user superseded the premise.\n",
		}).replace("## Test plan", "## Breaking changes\n\nThe previous behavior is withdrawn.\n\n## Test plan");
		const decisions = {
			notApplicable: [],
			acceptance: [],
			debt: [],
			authorizedUpdates: [
				{
					section: "Summary",
					instruction: "replace the superseded summary sentence",
					source: "the user's instruction in the PR 1 delivery conversation",
				},
			],
		};

		expect(validatePreservation(BODY, changed, decisions)?.code).toBe("BODY_INVALID");
	});
});

const FINDING = (id: string, severity: string, status: string): string =>
	`| ${id} | ${severity} | ${status} | \`a.ts:1\` — literal result | owner — next action |`;

describe("preservation of finding identity", () => {
	const withFindings = (rows: readonly string[]): string =>
		makeCompletedBody({
			findings: [
				"| ID | Severity | Status | Evidence | Owner / resolution |",
				"|---|---|---|---|---|",
				...rows,
				"",
			].join("\n"),
		});

	it("rejects removing a finding from the baseline", () => {
		const baseline = withFindings([FINDING("F1", "`BLOCK`", "`OPEN`"), FINDING("F2", "`ADVISORY`", "`OPEN`")]);
		const candidate = withFindings([FINDING("F1", "`BLOCK`", "`OPEN`")]);

		expect(validatePreservation(baseline, candidate)?.code).toBe("BODY_INVALID");
	});

	it("rejects changing a finding's severity", () => {
		const baseline = withFindings([FINDING("F1", "`BLOCK`", "`OPEN`")]);
		const candidate = withFindings([FINDING("F1", "`ADVISORY`", "`OPEN`")]);

		expect(validatePreservation(baseline, candidate)?.code).toBe("BODY_INVALID");
	});

	it("accepts an appended finding and a status change on an existing one", () => {
		const baseline = withFindings([FINDING("F1", "`BLOCK`", "`OPEN`")]);
		const candidate = withFindings([FINDING("F1", "`BLOCK`", "`FIXED`"), FINDING("F2", "`ADVISORY`", "`OPEN`")]);

		expect(validatePreservation(baseline, candidate)).toBeUndefined();
	});
});
describe("final body validation", () => {
	it("accepts a fresh matching completed body", () => {
		const outcome = execute({ baseline: METADATA, current: METADATA, body: BODY });
		expect("code" in outcome ? outcome.code : outcome.body).toBe(BODY);
	});

	it("rejects a diverged remote metadata record", () => {
		const outcome = execute({
			baseline: METADATA,
			current: { ...METADATA, headRefOid: "ffffffffffffffffffffffffffffffffffffffff" },
			body: BODY,
		});
		expect("code" in outcome ? outcome.code : "").toBe("REMOTE_DIVERGED");
	});

	it("rejects stale metadata that is not valid at all", () => {
		const outcome = execute({ baseline: METADATA, current: { ...METADATA, state: "MERGED" }, body: BODY });
		expect("code" in outcome ? outcome.code : "").toBe("METADATA_INVALID");
	});

	it("rejects decisions bound to another head", () => {
		const outcome = execute({
			baseline: METADATA,
			current: METADATA,
			body: BODY,
			decisions: { pr_number: 12, head_sha: "deadbeef", not_applicable: [], acceptance: [], debt: [] },
		});
		expect("code" in outcome ? outcome.code : "").toBe("DECISIONS_INVALID");
	});

	it("does not treat a matching head as a passing body", () => {
		const broken = BODY.replace("[PASS] — 0 open findings", "not a verdict");
		const outcome = execute({
			baseline: makeMetadata({ body: broken }),
			current: makeMetadata({ body: broken }),
			body: broken,
		});
		expect("code" in outcome ? outcome.code : "").toBe("BODY_INVALID");
	});

	it("rejects a body whose protected prose changed after acceptance", () => {
		const changed = makeCompletedBody({ summary: "Rewritten after acceptance.\n" });
		const outcome = execute({ baseline: METADATA, current: METADATA, body: changed });
		expect("code" in outcome ? outcome.code : "").toBe("BODY_INVALID");
	});

	it("refuses an unscoped protected rewrite through the full execute path", () => {
		const changed = makeCompletedBody({ summary: "Corrected after the user superseded the premise.\n" });
		const outcome = execute({
			baseline: METADATA,
			current: METADATA,
			body: changed,
			decisions: {
				pr_number: 12,
				head_sha: HEAD_SHA,
				not_applicable: [],
				acceptance: [],
				debt: [],
			},
		});

		expect("code" in outcome ? outcome.code : "").toBe("BODY_INVALID");
	});

	it("accepts a protected rewrite scoped by the supplied authorized update", () => {
		const changed = makeCompletedBody({ summary: "Corrected after the user superseded the premise.\n" });
		const outcome = execute({
			baseline: METADATA,
			current: METADATA,
			body: changed,
			decisions: {
				pr_number: 12,
				head_sha: HEAD_SHA,
				not_applicable: [],
				acceptance: [],
				debt: [],
				authorized_updates: [
					{
						section: "Summary",
						instruction: "replace the superseded summary sentence",
						source: "the user's instruction in the PR 1 delivery conversation",
					},
				],
			},
		});

		expect("code" in outcome ? outcome.code : outcome.body).toBe(changed);
	});

	it("keeps the immutable head visible in the accepted body", () => {
		const outcome = execute({ baseline: METADATA, current: METADATA, body: BODY });
		expect("code" in outcome ? "" : outcome.body.includes(HEAD_SHA)).toBe(true);
	});
});
