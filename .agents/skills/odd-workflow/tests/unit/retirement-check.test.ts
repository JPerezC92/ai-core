import { describe, expect, it } from "vitest";
import { CheckRetirements } from "#scripts/retirement_check/application/check_retirements.ts";
import { NoTaskRecordsError, RetirementReport } from "#scripts/retirement_check/domain/records.ts";
import type { RetirementDecision } from "#scripts/retirement_check/domain/records.ts";
import { evaluateRetirement } from "#scripts/retirement_check/domain/rules.ts";
import { makeTaskRecord, RetirementSourceFake } from "#tests/support/retirement-fixtures.ts";

const AS_OF = "2026-11-14";
const REFERENCE = "records/a.md";

/** Runs the retirement check over one record and returns the decision it reports. */
function decisionFor(text: string, asOfDate: string): RetirementDecision {
	const source = new RetirementSourceFake([REFERENCE], new Map([[REFERENCE, text]]));
	const results = [...new CheckRetirements(source).execute("records", asOfDate)];
	const [result] = results;
	if (!(result instanceof RetirementReport)) {
		throw new Error(`expected a retirement report, received ${result?.constructor.name ?? "no result"}`);
	}
	return result.decision;
}

/**
 * Runs the retention rule alone, without the validation prerequisite.
 *
 * The retention arithmetic and the metadata rules are properties of the domain rule, so they are
 * asserted here directly; the prerequisite that gates them is asserted through the application.
 */
function domainDecisionFor(text: string, asOfDate: string): RetirementDecision {
	return evaluateRetirement(text, asOfDate);
}

describe("CheckRetirements.execute fenced content", () => {
	/** A record whose quoted example sits in a balanced fence inside the Log. */
	function withQuotedExample(record: string, example: readonly string[]): string {
		return record.replace(
			"- L1 — original request",
			["- L1 — original request", "", "```text", ...example, "```"].join("\n"),
		);
	}

	it("excludes an active record carrying quoted closed metadata", () => {
		const text = withQuotedExample(makeTaskRecord({ status: "active", closedOn: null }), [
			"> **Status:** closed",
			"> **Closed:** 2026-01-01",
		]);
		expect(domainDecisionFor(text, AS_OF)).toStrictEqual({ kind: "excluded", reason: "status is not closed" });
	});

	it("excludes a closed record whose only closure date is fenced", () => {
		const record = makeTaskRecord({ closedOn: null });
		const text = record.replace(
			"- L1 — original request",
			["- L1 — original request", "", "```text", "> **Closed:** 2026-01-01", "```"].join("\n"),
		);
		expect(domainDecisionFor(text, AS_OF)).toStrictEqual({ kind: "excluded", reason: "no recorded closure date" });
	});

	it("lets genuine closed metadata govern over a conflicting fenced example", () => {
		const text = withQuotedExample(makeTaskRecord({ closedOn: "2026-11-01" }), ["> **Closed:** 2026-01-01"]);
		// The genuine date governs: 2026-11-01 to 2026-11-14 is 13 complete days, not the
		// much older fenced date, so the quoted example cannot shorten the retention period.
		expect(decisionFor(text, AS_OF)).toStrictEqual({
			kind: "candidate",
			closedOn: "2026-11-01",
			ageDays: 13,
		});
	});

	it("excludes ambiguous closure metadata instead of choosing one", () => {
		const first = makeTaskRecord({ closedOn: "2026-11-01" });
		const text = first.replace(
			"> **Closed:** 2026-11-01",
			["> **Closed:** 2026-11-01", "> **Closed:** 2026-10-01"].join("\n"),
		);
		expect(decisionFor(text, AS_OF)).toStrictEqual({ kind: "excluded", reason: "ambiguous closure metadata" });
	});

	it("excludes an otherwise eligible record whose fence never closes", () => {
		const record = makeTaskRecord({ closedOn: "2026-11-01" });
		const text = record.replace(
			"- L1 — original request",
			["- L1 — original request", "", "```text", "quoted"].join("\n"),
		);
		expect(domainDecisionFor(text, "2026-12-31")).toStrictEqual({
			kind: "excluded",
			reason: "unbalanced code fence",
		});
	});

	it("keeps the calendar arithmetic for a valid closed record", () => {
		expect(decisionFor(makeTaskRecord({ closedOn: "2026-11-01" }), "2026-11-08")).toStrictEqual({
			kind: "candidate",
			closedOn: "2026-11-01",
			ageDays: 7,
		});
	});

	it("ignores closed metadata quoted in an indented code block", () => {
		// Column-zero header metadata is genuine; an indented copy is a quoted example, so an
		// active record stays excluded even though its prose shows a closed header.
		const record = makeTaskRecord({ status: "active", closedOn: null });
		const text = record.replace(
			"- L1 — original request",
			["- L1 — original request", "", "    > **Status:** closed", "    > **Closed:** 2025-01-02"].join("\n"),
		);
		expect(domainDecisionFor(text, "2026-11-14")).toStrictEqual({
			kind: "excluded",
			reason: "status is not closed",
		});
	});

	it("excludes a record whose status metadata is contradictory", () => {
		const record = makeTaskRecord({ closedOn: "2026-11-01" });
		const text = record.replace(
			"> **Status:** closed",
			["> **Status:** closed", "> **Status:** active"].join("\n"),
		);
		expect(domainDecisionFor(text, AS_OF)).toStrictEqual({
			kind: "excluded",
			reason: "ambiguous closure metadata",
		});
	});

	it("excludes a record whose status line carries a trailing space", () => {
		// The status must be exactly `> **Status:** closed`; a stray space is not that line,
		// and the validator reports the same record rather than accepting it silently.
		const text = makeTaskRecord({ closedOn: "2026-11-01" }).replace(
			"> **Status:** closed",
			"> **Status:** closed ",
		);
		expect(domainDecisionFor(text, "2026-12-31")).toStrictEqual({
			kind: "excluded",
			reason: "status is not closed",
		});
	});
});

describe("CheckRetirements.execute validation prerequisite", () => {
	it("excludes a record that fails feature validation, whatever its metadata says", () => {
		// Genuine closed header and an old closure date, but the record's Log carries no Close
		// entry, so its structure is not trustworthy enough to delete evidence on.
		const text = makeTaskRecord({ closedOn: "2026-11-01", closeEntry: false });
		const decision = decisionFor(text, "2026-12-31");
		expect(decision.kind).toBe("excluded");
		expect(decision).toMatchObject({
			kind: "excluded",
			reason: expect.stringContaining("does not pass feature validation"),
		});
	});

	it("still reports a valid closed record as a candidate", () => {
		expect(decisionFor(makeTaskRecord({ closedOn: "2026-11-01" }), "2026-12-31")).toStrictEqual({
			kind: "candidate",
			closedOn: "2026-11-01",
			ageDays: 60,
		});
	});
});

describe("CheckRetirements.execute genuine header metadata", () => {
	it("ignores a closure date quoted at column zero inside the Log", () => {
		// The genuine header is closed but states no closure date; the only date is a column-zero
		// quotation in the body. Neither validation nor retention may take it as the real date.
		const text = [
			"# Record",
			"",
			"> **Status:** closed",
			"> **Owner:** Cipher",
			"> **Created:** 2026-10-01",
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
			"- L1 — the user's message quoted:",
			"> **Closed:** 2025-01-01",
			"- L2 — Close: delivered",
			"",
		].join("\n");
		expect(decisionFor(text, "2026-11-24")).toMatchObject({
			kind: "excluded",
			reason: expect.stringContaining("does not pass feature validation"),
		});
	});

	it("ignores a status quoted at column zero inside the Log", () => {
		const text = makeTaskRecord({ status: "active", closedOn: null }).replace(
			"- L1 — original request",
			["- L1 — original request", "> **Status:** closed", "> **Closed:** 2025-01-01"].join("\n"),
		);
		expect(decisionFor(text, "2026-11-24").kind).toBe("excluded");
	});

	it("keeps genuine metadata authoritative over a conflicting quotation", () => {
		const text = makeTaskRecord({ closedOn: "2026-11-01" }).replace(
			"- L1 — original request",
			["- L1 — original request", "", "```text", "> **Closed:** 2025-01-01", "```"].join("\n"),
		);
		expect(decisionFor(text, "2026-11-08")).toStrictEqual({
			kind: "candidate",
			closedOn: "2026-11-01",
			ageDays: 7,
		});
	});
});

describe("CheckRetirements.execute", () => {
	it("reads the recorded closure date as its UTC midnight", () => {
		expect(decisionFor(makeTaskRecord({ closedOn: "2026-11-01" }), "2026-11-01")).toStrictEqual({
			kind: "excluded",
			reason: "0 complete calendar days since closure; 7 required",
		});
		expect(decisionFor(makeTaskRecord({ closedOn: "2026-11-01" }), "2026-11-02")).toStrictEqual({
			kind: "excluded",
			reason: "1 complete calendar days since closure; 7 required",
		});
		expect(decisionFor(makeTaskRecord({ closedOn: "2026-11-01" }), "2026-11-15")).toStrictEqual({
			kind: "candidate",
			closedOn: "2026-11-01",
			ageDays: 14,
		});
	});

	it("excludes a record whose closure date is not a calendar date", () => {
		for (const closureDate of ["2026-13-01", "2026-11-31", "2026-02-30", "1 November 2026"]) {
			expect(domainDecisionFor(makeTaskRecord({ closedOn: closureDate }), AS_OF)).toStrictEqual({
				kind: "excluded",
				reason: "closure date is not a calendar date",
			});
		}
	});

	it("counts whole calendar days across a month boundary", () => {
		expect(domainDecisionFor(makeTaskRecord({ closedOn: "2026-11-30" }), "2026-12-07")).toStrictEqual({
			kind: "candidate",
			closedOn: "2026-11-30",
			ageDays: 7,
		});
	});

	it("excludes a record closed six complete calendar days before the report date", () => {
		expect(decisionFor(makeTaskRecord({ closedOn: "2026-11-08" }), AS_OF)).toStrictEqual({
			kind: "excluded",
			reason: "6 complete calendar days since closure; 7 required",
		});
	});

	it("reports a record closed exactly seven complete calendar days before the report date", () => {
		expect(decisionFor(makeTaskRecord({ closedOn: "2026-11-07" }), AS_OF)).toStrictEqual({
			kind: "candidate",
			closedOn: "2026-11-07",
			ageDays: 7,
		});
	});

	it("reports a record closed eight complete calendar days before the report date", () => {
		expect(decisionFor(makeTaskRecord({ closedOn: "2026-11-06" }), AS_OF)).toStrictEqual({
			kind: "candidate",
			closedOn: "2026-11-06",
			ageDays: 8,
		});
	});

	it("reports a record at the seven-day boundary across a year change", () => {
		expect(domainDecisionFor(makeTaskRecord({ closedOn: "2026-12-28" }), "2027-01-04")).toStrictEqual({
			kind: "candidate",
			closedOn: "2026-12-28",
			ageDays: 7,
		});
	});

	it("reports a record at the seven-day boundary across a leap day", () => {
		expect(domainDecisionFor(makeTaskRecord({ closedOn: "2028-02-24" }), "2028-03-02")).toStrictEqual({
			kind: "candidate",
			closedOn: "2028-02-24",
			ageDays: 7,
		});
	});

	it("excludes a record whose status is not closed", () => {
		expect(domainDecisionFor(makeTaskRecord({ status: "active", closedOn: null }), AS_OF)).toStrictEqual({
			kind: "excluded",
			reason: "status is not closed",
		});
	});

	it("excludes a closed record with no recorded closure date", () => {
		expect(domainDecisionFor(makeTaskRecord({ closedOn: null }), AS_OF)).toStrictEqual({
			kind: "excluded",
			reason: "no recorded closure date",
		});
	});

	it("excludes a record whose closure date is after the report date", () => {
		expect(decisionFor(makeTaskRecord({ closedOn: "2026-11-20" }), AS_OF)).toStrictEqual({
			kind: "excluded",
			reason: "closure date is after the as-of date",
		});
	});

	it("excludes a closed record whose task row is unfinished, because validation comes first", () => {
		expect(decisionFor(makeTaskRecord({ taskStatus: "in progress" }), AS_OF)).toMatchObject({
			kind: "excluded",
			reason: expect.stringContaining("does not pass feature validation"),
		});
	});

	it("excludes a closed record with no Close log entry, because validation comes first", () => {
		expect(decisionFor(makeTaskRecord({ closeEntry: false }), AS_OF)).toMatchObject({
			kind: "excluded",
			reason: expect.stringContaining("does not pass feature validation"),
		});
	});

	it("excludes every record when the report date is not a calendar date", () => {
		const source = new RetirementSourceFake(
			["records/a.md", "records/b.md"],
			new Map([
				["records/a.md", makeTaskRecord()],
				["records/b.md", makeTaskRecord()],
			]),
		);

		expect([...new CheckRetirements(source).execute("records", "14 November 2026")]).toStrictEqual([
			new RetirementReport("records/a.md", {
				kind: "excluded",
				reason: "as-of date is not a calendar date",
			}),
			new RetirementReport("records/b.md", {
				kind: "excluded",
				reason: "as-of date is not a calendar date",
			}),
		]);
		expect(decisionFor(makeTaskRecord(), "")).toStrictEqual({
			kind: "excluded",
			reason: "as-of date is not a calendar date",
		});
	});

	it("reports an unreadable record as an exclusion and continues with the rest", () => {
		const failure = new Error("later record cannot be read");
		const source = new RetirementSourceFake(
			["records/a.md", "records/b.md"],
			new Map([["records/a.md", makeTaskRecord({ closedOn: "2026-11-01" })]]),
			failure,
		);

		const results = [...new CheckRetirements(source).execute("records", AS_OF)];

		expect(results).toStrictEqual([
			new RetirementReport("records/a.md", { kind: "candidate", closedOn: "2026-11-01", ageDays: 13 }),
			new RetirementReport("records/b.md", {
				kind: "excluded",
				reason: "cannot be read: later record cannot be read",
			}),
		]);
	});

	it("excludes the template and reports that no task records remain", () => {
		const source = new RetirementSourceFake(["records/_template.md"], new Map());

		expect([...new CheckRetirements(source).execute("records", AS_OF)]).toStrictEqual([new NoTaskRecordsError()]);
		expect(source.reads).toStrictEqual([]);
	});
});
