import { describe, expect, it } from "vitest";

import { parseArguments } from "#scripts/incident_workflow_pkg/infrastructure/arguments.ts";

// The argument loader is the command line's own parser: it turns argv into the
// validated arguments the validator runs on, or reports why it cannot.
describe("validator command-line arguments", () => {
	it("rejects a command line without an analysis directory", () => {
		expect(parseArguments([])).toEqual({
			kind: "error",
			message: "the following arguments are required: analysis_dir",
		});
	});

	it("rejects an invalid --step choice", () => {
		expect(parseArguments(["/fixture", "--step", "guess"])).toEqual({
			kind: "error",
			message: "argument --step: invalid choice: 'guess' (choose from 'identify', 'investigate', 'synthesize')",
		});
	});

	it("rejects conflicting modes", () => {
		expect(parseArguments(["/fixture", "--scaffold", "--pre-close"])).toEqual({
			kind: "error",
			message: "argument --pre-close: not allowed with argument --scaffold",
		});
	});

	it("rejects an unrecognised argument", () => {
		expect(parseArguments(["/fixture", "--unknown"])).toEqual({
			kind: "error",
			message: "unrecognized arguments: --unknown",
		});
	});

	it("rejects an ambiguous option abbreviation", () => {
		expect(parseArguments(["/fixture", "--s"])).toEqual({
			kind: "error",
			message: "ambiguous option: --s could match --step, --scaffold",
		});
	});

	it("rejects an inline argument on a flag", () => {
		expect(parseArguments(["/fixture", "--scaffold=x"])).toEqual({
			kind: "error",
			message: "argument --scaffold: ignored explicit argument 'x'",
		});
	});
});
