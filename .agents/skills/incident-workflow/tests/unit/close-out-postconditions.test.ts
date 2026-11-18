import { describe, expect, it } from "vitest";

import type { CloseOutOutcome } from "#scripts/incident_workflow_pkg/application/validate_close_out.ts";
import { ValidateCloseOut } from "#scripts/incident_workflow_pkg/application/validate_close_out.ts";
import {
	makeClosedSnapshot,
	makeRegister,
	makeRegisterRow,
	makeTicketRecord,
} from "#tests/support/incident-validator-fixtures.ts";
import { parseProblemRegister } from "#scripts/incident_workflow_pkg/infrastructure/records.ts";

/** The violations a checked close-out reports; a skipped close-out reports none. */
function violations(outcome: CloseOutOutcome): string[] {
	if (outcome.kind === "skipped") throw new Error(`unexpected close-out skip: ${outcome.reason}`);
	return outcome.violations;
}

function checked(snapshot = makeClosedSnapshot()) {
	return violations(new ValidateCloseOut().execute(snapshot, null, []));
}

describe("close-out postconditions", () => {
	it("accepts a completed durable set", () => {
		expect(checked()).toEqual([]);
	});

	it("reports a missing ticket record", () => {
		// The close is skipped, not failed: there is no durable record to check the
		// postconditions against, and the outcome carries the stable code for it.
		expect(new ValidateCloseOut().execute(makeClosedSnapshot({ ticketFileNames: [] }), null, [])).toEqual({
			kind: "skipped",
			code: "CLOSE-0",
			reason: "ticket_<id>.md not found",
		});
	});

	it("reports more than one ticket record", () => {
		expect(checked(makeClosedSnapshot({ ticketFileNames: ["ticket_1.md", "ticket_2.md"] }))).toContain(
			"CLOSE-6: multiple ticket_<id>.md records found: ticket_1.md, ticket_2.md",
		);
	});

	it("reports a working analysis file left in place", () => {
		expect(checked(makeClosedSnapshot({ workingAnalysisFiles: ["state.md"] }))).toContain(
			"CLOSE-1: working analysis file remains after close: state.md",
		);
	});

	it("reports a surviving response draft", () => {
		expect(checked(makeClosedSnapshot({ responseDraftPresent: true }))).toContain(
			"CLOSE-2: response-draft.md remains after close",
		);
	});

	it("reports the durable directories the collapse must keep", () => {
		expect(checked(makeClosedSnapshot({ screenshotsDirPresent: false, validationsDirPresent: false }))).toEqual(
			expect.arrayContaining([
				"CLOSE-3: screenshots/ missing from the durable set",
				"CLOSE-4: validations/ missing from the durable set",
			]),
		);
	});

	it("reports a cited image that does not exist", () => {
		expect(checked(makeClosedSnapshot({ missingImagePaths: ["screenshots/response-1/gone.png"] }))).toContain(
			"CLOSE-5: cited image path is not an existing file inside the ticket folder: screenshots/response-1/gone.png",
		);
	});

	it("reports a citation that is not a response screenshot", () => {
		expect(checked(makeClosedSnapshot({ citedPaths: ["downloads/x.png"] }))).toContain(
			"CLOSE-8: cited path is not screenshots/response-<digits>/<filename>: downloads/x.png",
		);
	});

	it("reports a leftover download", () => {
		expect(checked(makeClosedSnapshot({ leftoverDownloadFiles: ["downloads/report.csv"] }))).toContain(
			"CLOSE-9: unused download file remains after close: downloads/report.csv",
		);
	});

	it("reports an unparseable durable ticket record", () => {
		const outcome = new ValidateCloseOut().execute(makeClosedSnapshot(), { error: "bad ticket" }, []);
		expect(violations(outcome)).toContain("CLOSE-7: ticket record cannot be parsed: bad ticket");
	});

	it("checks the durable verdict against the register", () => {
		const register = parseProblemRegister(makeRegister(makeRegisterRow()));
		const outcome = new ValidateCloseOut().execute(
			makeClosedSnapshot(),
			{ value: makeTicketRecord({ known_problem_ids: ["P-999"], identification_verdict: "structural" }) },
			register,
		);
		expect(violations(outcome)).toContain("VERDICT-4: cited P-999 is not an incident P-NNN row");
	});
});
