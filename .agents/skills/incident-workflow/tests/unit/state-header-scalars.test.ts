import { describe, expect, it } from "vitest";

import { InputError } from "#scripts/incident_workflow_pkg/domain/errors.ts";
import { parseStateHeader, parseTicketRecord } from "#scripts/incident_workflow_pkg/infrastructure/records.ts";

const SOURCE = "analysis/state.md";

// Builds a complete state header, because the parser reports missing fields before it reads any
// value. The Phase entry is supplied whole so a nested mapping or list keeps its own YAML shape.
function stateHeader(phaseLines: string | readonly string[]): string {
	const phase = Array.isArray(phaseLines) ? phaseLines : [phaseLines];
	return [
		"---",
		...phase,
		'SLA-due: "2099-01-01T00:00"',
		'Updated: "2000-01-01T00:00"',
		'Hypotheses-outstanding: "0/3"',
		'Query-budget: "0/6"',
		'identification_verdict: "no_match"',
		'Same-query-reruns: "0/2"',
		"---",
		"",
	].join("\n");
}

describe("analysis header scalars", () => {
	it("renders string, number, boolean and null header values as before", () => {
		expect(parseStateHeader(stateHeader('Phase: "synthesize"'), SOURCE).Phase).toBe("synthesize");
		expect(parseStateHeader(stateHeader("Phase: 3"), SOURCE).Phase).toBe("3");
		expect(parseStateHeader(stateHeader("Phase: true"), SOURCE).Phase).toBe("True");
		expect(parseStateHeader(stateHeader("Phase: null"), SOURCE).Phase).toBe("None");
	});

	it("rejects a mapping in a scalar header field and names the field", () => {
		const document = stateHeader(["Phase:", "  nested: value"]);
		expect(() => parseStateHeader(document, SOURCE)).toThrow(InputError);
		expect(() => parseStateHeader(document, SOURCE)).toThrow(
			`Field 'Phase' in ${SOURCE} must be a scalar value, found a mapping`,
		);
	});

	it("rejects a list in a scalar header field and names the field", () => {
		const document = stateHeader(["Phase:", "  - a", "  - b"]);
		expect(() => parseStateHeader(document, SOURCE)).toThrow(
			`Field 'Phase' in ${SOURCE} must be a scalar value, found a list`,
		);
	});

	it("names a non-plain object instead of calling it a mapping", () => {
		// This skill parses frontmatter with the YAML 1.1 schema, which resolves a full ISO
		// timestamp or a bare date into a Date. It is not a mapping, and the message must say
		// what actually arrived. The documented `YYYY-MM-DDTHH:MM` form stays a string.
		const document = [
			"---",
			'Phase: "synthesize"',
			"SLA-due: 2099-01-01T00:00:00Z",
			'Updated: "2000-01-01T00:00"',
			'Hypotheses-outstanding: "0/3"',
			'Query-budget: "0/6"',
			'identification_verdict: "no_match"',
			'Same-query-reruns: "0/2"',
			"---",
			"",
		].join("\n");
		expect(() => parseStateHeader(document, SOURCE)).toThrow(
			`Field 'SLA-due' in ${SOURCE} must be a scalar value, found a Date value`,
		);
	});

	it("keeps accepting a list where the ticket contract declares one", () => {
		const ticket = [
			"---",
			"symptom_ids:",
			"  - S-01",
			"  - S-02",
			"known_problem_ids: []",
			'identification_verdict: "pending"',
			"---",
			"",
		].join("\n");
		expect(parseTicketRecord(ticket, "ticket.md").symptom_ids).toEqual(["S-01", "S-02"]);
	});
});
