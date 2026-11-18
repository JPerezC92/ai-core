import { describe, expect, it } from "vitest";

import {
	checkDiagnosticKnowledge,
	makeLocalSymptoms,
	makeProblemRows,
	makeRegisterRow,
} from "#tests/support/incident-validator-fixtures.ts";

describe("diagnostic knowledge", () => {
	it("accepts a valid empty local register", () => {
		expect(checkDiagnosticKnowledge()).toEqual([]);
	});

	it("accepts a local class and a problem citing it", () => {
		expect(
			checkDiagnosticKnowledge({
				localSymptoms: makeLocalSymptoms([{ id: "LOCAL:S-01", description: "local class" }]),
				localProblemRows: makeProblemRows(makeRegisterRow({ symptom: "LOCAL:S-01" })),
			}),
		).toEqual([]);
	});

	it("reports a missing local symptom register instead of treating it as empty", () => {
		expect(checkDiagnosticKnowledge({ localSymptoms: null })).toEqual([
			"KNOWLEDGE-1: local symptom register missing: incidents/diagnostics/symptoms.md",
		]);
	});

	it("reports a missing local problem register instead of treating it as empty", () => {
		expect(checkDiagnosticKnowledge({ localProblemRows: null })).toEqual([
			"KNOWLEDGE-2: local problem register missing: incidents/diagnostics/problems.md",
		]);
	});

	it("reports a class defined twice in the local register", () => {
		expect(
			checkDiagnosticKnowledge({
				localSymptoms: makeLocalSymptoms([
					{ id: "LOCAL:S-01", description: "a" },
					{ id: "LOCAL:S-01", description: "b" },
				]),
			}),
		).toEqual(["KNOWLEDGE-3: local symptom register defines an id twice: LOCAL:S-01"]);
	});

	it("reports a local class that reuses a baseline id", () => {
		expect(
			checkDiagnosticKnowledge({ localSymptoms: makeLocalSymptoms([{ id: "S-05", description: "shadowed" }]) }),
		).toEqual([
			"KNOWLEDGE-4: id defined in both baseline and local registers: S-05",
			"KNOWLEDGE-7: local register defines a non-LOCAL symptom id: S-05",
		]);
	});

	it("rejects a baseline-form id invented in the local register", () => {
		expect(
			checkDiagnosticKnowledge({ localSymptoms: makeLocalSymptoms([{ id: "S-08", description: "invented" }]) }),
		).toEqual(["KNOWLEDGE-7: local register defines a non-LOCAL symptom id: S-08"]);
	});

	it("reports a problem citing an unknown class", () => {
		expect(
			checkDiagnosticKnowledge({ localProblemRows: makeProblemRows(makeRegisterRow({ symptom: "S-99" })) }),
		).toEqual(["KNOWLEDGE-6: P-001 references an unknown symptom: S-99"]);
	});

	it("reports a symptom cell containing a non-identifier segment", () => {
		expect(
			checkDiagnosticKnowledge({
				localProblemRows: makeProblemRows(makeRegisterRow({ symptom: "S-05, unclassified" })),
			}),
		).toEqual(["KNOWLEDGE-5: P-001 Symptom cell has an invalid token: unclassified"]);
	});
});
