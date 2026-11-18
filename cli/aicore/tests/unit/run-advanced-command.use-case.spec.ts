/**
 * Unit: running one advanced synchronization command.
 *
 * Two behavioral concerns, one per group: the operation routes an accepted
 * command to the operation that performs it and returns that operation's domain
 * result unchanged, and it owns the argument-validity policy — the revision
 * syntax, an editor the profiles do not implement, and a flag only `init`
 * accepts — refusing each before anything is dispatched (contract T2, C5).
 */

import { beforeEach, describe, expect, test, vi } from "vitest";

import { RunAdvancedCommand } from "#application/run-advanced-command.ts";
import {
	REVISION,
	makeEnrollmentRequest,
	makeOperations,
	makeSucceeded,
	makeSynchronizationRequest,
	type OperationDoubles,
} from "#support/aicore-cli.factory.ts";

function operation(operations: OperationDoubles): RunAdvancedCommand {
	return new RunAdvancedCommand(operations);
}

/** Assert that a refusal dispatched to no operation at all. */
function expectNoDispatch(operations: OperationDoubles): void {
	expect(operations.check.execute).not.toHaveBeenCalled();
	expect(operations.apply.execute).not.toHaveBeenCalled();
	expect(operations.enroll.execute).not.toHaveBeenCalled();
}

describe("command routing", () => {
	beforeEach(() => {
		vi.clearAllMocks();
	});

	test("each command runs the operation that performs it, once, and its result is returned unchanged", async () => {
		const operations = makeOperations();
		const outcome = makeSucceeded("applied; created: notes.md");

		operations.check.execute.mockResolvedValue(outcome);
		operations.apply.execute.mockResolvedValue(outcome);
		operations.enroll.execute.mockResolvedValue(outcome);

		await expect(
			operation(operations).execute({
				command: "check",
				request: makeSynchronizationRequest(),
				requestedEditor: "opencode",
				initOnlyArguments: [],
			}),
		).resolves.toBe(outcome);
		expect(operations.check.execute).toHaveBeenCalledTimes(1);
		expect(operations.apply.execute).not.toHaveBeenCalled();
		expect(operations.enroll.execute).not.toHaveBeenCalled();

		await expect(
			operation(operations).execute({
				command: "apply",
				request: makeSynchronizationRequest(),
				requestedEditor: "opencode",
				initOnlyArguments: [],
			}),
		).resolves.toBe(outcome);
		expect(operations.apply.execute).toHaveBeenCalledTimes(1);
		expect(operations.apply.execute).toHaveBeenCalledWith(makeSynchronizationRequest());

		await expect(
			operation(operations).execute({
				command: "init",
				request: makeEnrollmentRequest(),
				requestedEditor: "opencode",
				initOnlyArguments: [],
			}),
		).resolves.toBe(outcome);
		expect(operations.enroll.execute).toHaveBeenCalledTimes(1);
		expect(operations.enroll.execute).toHaveBeenCalledWith(makeEnrollmentRequest());
		expect(operations.check.execute).toHaveBeenCalledTimes(1);
	});
});

describe("argument-validity policy", () => {
	beforeEach(() => {
		vi.clearAllMocks();
	});

	test("a malformed source revision is refused before any operation runs", async () => {
		const operations = makeOperations();

		const outcome = await operation(operations).execute({
			command: "check",
			request: makeSynchronizationRequest({ sourceRevision: "not-a-revision" }),
			requestedEditor: "opencode",
			initOnlyArguments: [],
		});

		expect(outcome).toStrictEqual({
			ok: false,
			failure: {
				code: "invalid",
				message: "argument --source-revision: must be a 40-character lowercase hex string",
			},
		});
		expectNoDispatch(operations);
	});

	test("an editor the profiles do not implement is refused by name, with the supported set", async () => {
		const operations = makeOperations();

		const outcome = await operation(operations).execute({
			command: "check",
			request: makeSynchronizationRequest(),
			requestedEditor: "vim",
			initOnlyArguments: [],
		});

		expect(outcome).toStrictEqual({
			ok: false,
			failure: {
				code: "invalid",
				message: "argument --editor: unknown editor 'vim' (supported: opencode, cursor)",
			},
		});
		expectNoDispatch(operations);
	});

	test("a declaration only init accepts is refused, naming every one that was supplied", async () => {
		const operations = makeOperations();

		const outcome = await operation(operations).execute({
			command: "apply",
			request: makeSynchronizationRequest({ sourceRevision: REVISION }),
			requestedEditor: "opencode",
			initOnlyArguments: ["--bind", "--bind-cleared"],
		});

		expect(outcome).toStrictEqual({
			ok: false,
			failure: { code: "invalid", message: "unrecognized arguments: --bind --bind-cleared" },
		});
		expectNoDispatch(operations);
	});
});

describe("operation that fails to execute", () => {
	beforeEach(() => {
		vi.clearAllMocks();
	});

	test("an operation that cannot execute propagates its exception instead of returning a value", async () => {
		const operations = makeOperations();
		const failure = new Error("the destination is unreadable");
		operations.apply.execute.mockRejectedValue(failure);

		const execution = operation(operations).execute({
			command: "apply",
			request: makeSynchronizationRequest(),
			requestedEditor: "opencode",
			initOnlyArguments: [],
		});

		// The same exception instance reaches the caller: the operation neither
		// caught it nor turned it into a domain outcome.
		await expect(execution).rejects.toBe(failure);
		expect(operations.apply.execute).toHaveBeenCalledTimes(1);
	});
});
