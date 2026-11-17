/**
 * Unit: forwarding an advanced engine command.
 *
 * One behavioral concern per group: the operation hands the engine the command
 * and the passthrough verbatim and returns the engine's typed result unchanged,
 * and a failure to execute the engine at all stays a boundary exception instead
 * of being converted into a value (contract T2, C5).
 */

import { beforeEach, describe, expect, test, vi } from "vitest";
import { mock } from "vitest-mock-extended";

import { RunAdvancedCommand } from "#application/run-advanced-command.ts";
import type { EngineRunner } from "#domain/ports/engine-runner.ts";
import { makeEngine, makeEngineRun } from "#support/aicore-cli.factory.ts";

describe("command forwarding", () => {
	beforeEach(() => {
		vi.clearAllMocks();
	});

	test("the engine runs once with the command and its passthrough, and its result is returned unchanged", async () => {
		const engine = makeEngine();
		const run = makeEngineRun({ status: 3, stdout: "advanced stdout\n", stderr: "advanced stderr\n" });
		engine.run.mockResolvedValue(run);

		const execution = new RunAdvancedCommand(engine).execute({
			command: "apply",
			passthrough: ["--bind-cleared"],
		});

		await expect(execution).resolves.toBe(run);
		expect(engine.run).toHaveBeenCalledTimes(1);
		expect(engine.run).toHaveBeenCalledWith("apply", ["--bind-cleared"]);
	});
});

describe("engine that fails to execute", () => {
	beforeEach(() => {
		vi.clearAllMocks();
	});

	test("a port that cannot execute propagates its exception instead of returning a value", async () => {
		const engine = mock<EngineRunner>();
		const failure = new Error("engine unavailable");
		engine.run.mockRejectedValue(failure);

		const execution = new RunAdvancedCommand(engine).execute({ command: "check", passthrough: [] });

		// The same exception instance reaches the caller: the operation neither
		// caught it nor turned it into an engine outcome.
		await expect(execution).rejects.toBe(failure);
		expect(engine.run).toHaveBeenCalledTimes(1);
		expect(engine.run).toHaveBeenCalledWith("check", []);
	});
});
