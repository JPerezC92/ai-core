import { describe, expect, it } from "vitest";

import {
	checkDiagnosticKnowledge,
	makeLocalSymptoms,
	makeProblemRows,
	makeRegisterRow,
} from "#tests/support/incident-validator-fixtures.ts";

// The symptom-identifier grammar is owned by the diagnostic-knowledge check, so
// every case below observes the grammar through that operation: a register id
// the grammar reads, and a problem cell segment the grammar accepts or rejects.
describe("symptom identifiers", () => {
	it("accepts a baseline class id", () => {
		// A baseline-form id is read as a class of the local register, and it is
		// not a destination-owned class: the check reports it as a non-local id.
		expect(
			checkDiagnosticKnowledge({
				localSymptoms: makeLocalSymptoms([{ id: "S-01", description: "baseline form" }]),
			}),
		).toEqual(["KNOWLEDGE-7: local register defines a non-LOCAL symptom id: S-01"]);
	});

	it("accepts a destination-owned class id", () => {
		// A destination-owned id is read as a class of the local register and is
		// not reported as a non-local id: a problem row may cite it.
		expect(
			checkDiagnosticKnowledge({
				localSymptoms: makeLocalSymptoms([{ id: "LOCAL:S-01", description: "mine" }]),
				localProblemRows: makeProblemRows(makeRegisterRow({ symptom: "LOCAL:S-01" })),
			}),
		).toEqual([]);
	});

	it("rejects a substring match", () => {
		// Neither "XS-01" nor "S-01x" is a complete identifier, so each segment is
		// reported as an invalid token of the cell it appears in.
		expect(
			checkDiagnosticKnowledge({
				localProblemRows: makeProblemRows(
					makeRegisterRow({ id: "P-001", symptom: "XS-01" }),
					makeRegisterRow({ id: "P-002", symptom: "S-01x" }),
				),
			}),
		).toEqual([
			"KNOWLEDGE-5: P-001 Symptom cell has an invalid token: XS-01",
			"KNOWLEDGE-5: P-002 Symptom cell has an invalid token: S-01x",
		]);
	});

	it("rejects a malformed local prefix", () => {
		expect(
			checkDiagnosticKnowledge({
				localProblemRows: makeProblemRows(
					makeRegisterRow({ id: "P-001", symptom: "local:S-01" }),
					makeRegisterRow({ id: "P-002", symptom: "LOCAL-S-01" }),
				),
			}),
		).toEqual([
			"KNOWLEDGE-5: P-001 Symptom cell has an invalid token: local:S-01",
			"KNOWLEDGE-5: P-002 Symptom cell has an invalid token: LOCAL-S-01",
		]);
	});

	it("keeps an open-ended numeric width", () => {
		// "S-123" is read as a class of the local register, and "LOCAL:S-1234" is
		// read as a destination-owned class a problem row may cite.
		expect(
			checkDiagnosticKnowledge({
				localSymptoms: makeLocalSymptoms([
					{ id: "S-123", description: "wide baseline form" },
					{ id: "LOCAL:S-1234", description: "wide local form" },
				]),
				localProblemRows: makeProblemRows(makeRegisterRow({ symptom: "LOCAL:S-1234" })),
			}),
		).toEqual(["KNOWLEDGE-7: local register defines a non-LOCAL symptom id: S-123"]);
	});

	it("parses a comma-separated cell into complete tokens", () => {
		// "S-05, LOCAL:S-01" is two complete identifiers, so the cell reports no
		// invalid token and both of the classes it names are known to the check.
		expect(
			checkDiagnosticKnowledge({
				localSymptoms: makeLocalSymptoms([{ id: "LOCAL:S-01", description: "mine" }]),
				localProblemRows: makeProblemRows(makeRegisterRow({ symptom: "S-05, LOCAL:S-01" })),
			}),
		).toEqual([]);
	});

	it("reports the segments that are not whole identifiers", () => {
		// Only "S-05" is a complete identifier, and the two remaining segments are
		// reported as invalid tokens in the order the cell declares them.
		expect(
			checkDiagnosticKnowledge({
				localProblemRows: makeProblemRows(makeRegisterRow({ symptom: "S-05, unclassified, S-" })),
			}),
		).toEqual(["KNOWLEDGE-5: P-001 Symptom cell has an invalid token: unclassified, S-"]);
	});

	it("ignores empty segments", () => {
		// The empty segment of the cell is neither an identifier nor an invalid
		// token, and the one identifier it carries is known to the check.
		expect(
			checkDiagnosticKnowledge({
				localProblemRows: makeProblemRows(makeRegisterRow({ symptom: " S-05 , " })),
			}),
		).toEqual([]);
	});
});
