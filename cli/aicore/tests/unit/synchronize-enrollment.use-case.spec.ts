/**
 * Unit: enrollment of a destination that is not yet bound.
 *
 * Exercises the application operation with its collaborators doubled (contract
 * T2). The assertion is on the operation's returned domain result and the
 * request it handed to the operation it chose — never on operator copy or an
 * exit status, which belong to the delivery edge.
 */

import { beforeEach, describe, expect, test, vi } from "vitest";
import type { MockProxy } from "vitest-mock-extended";

import { SynchronizeDestination } from "#application/synchronize-destination.ts";
import type { FilesystemProbe } from "#domain/ports/filesystem-probe.ts";
import type { SelectionStore } from "#domain/ports/selection-store.ts";
import {
	CHECKOUT_ROOT,
	DESTINATION_PATH,
	OTHER_REVISION,
	REVISION,
	makeDrifted,
	makeEnrollmentRequest,
	makeFilesystem,
	makeOperations,
	makeOutcomeRefused,
	makeSelections,
	makeSettings,
	makeSynchronizationRequest,
	type OperationDoubles,
} from "#support/aicore-cli.factory.ts";

function operation(options: {
	operations: OperationDoubles;
	files?: MockProxy<FilesystemProbe>;
	selections?: MockProxy<SelectionStore>;
	sourceRevision?: string | undefined;
}) {
	return new SynchronizeDestination({
		checkoutRoot: CHECKOUT_ROOT,
		settings: makeSettings({ sourceRevision: options.sourceRevision ?? REVISION }),
		...options.operations,
		files: options.files ?? makeFilesystem({ directories: [DESTINATION_PATH] }),
		selections: options.selections ?? makeSelections(),
	});
}

describe("enrollment decision", () => {
	beforeEach(() => {
		vi.clearAllMocks();
	});

	test("an unbound destination is enrolled with bulk clearance, then verified", async () => {
		const operations = makeOperations();

		const result = await operation({ operations }).execute({
			target: DESTINATION_PATH,
			editor: "opencode",
			revision: undefined,
		});

		expect(result.ok).toBeTruthy();
		expect(operations.enroll.execute).toHaveBeenCalledTimes(1);
		expect(operations.enroll.execute).toHaveBeenCalledWith(makeEnrollmentRequest());
		expect(operations.check.execute).toHaveBeenCalledTimes(1);
		expect(operations.check.execute).toHaveBeenCalledWith(makeSynchronizationRequest());
		expect(operations.apply.execute).not.toHaveBeenCalled();
		expect(operations.enroll.execute.mock.invocationCallOrder[0]).toBeLessThan(
			operations.check.execute.mock.invocationCallOrder[0] as number,
		);
		expect(result.ok && result.value.enrolled).toBe(true);
		expect(result.ok && result.value.current).toBe(true);
	});

	test("the requested editor reaches the enrollment as the profile to deliver", async () => {
		const operations = makeOperations();

		const result = await operation({ operations }).execute({
			target: DESTINATION_PATH,
			editor: "cursor",
			revision: undefined,
		});

		expect(result.ok).toBeTruthy();
		const request = operations.enroll.execute.mock.calls[0]?.[0];
		expect(request?.editor).toBe("cursor");
		expect(result.ok && result.value.editor).toBe("cursor");
	});

	test("the explicitly supplied revision wins over the operator setting", async () => {
		const operations = makeOperations();

		const result = await operation({ operations, sourceRevision: OTHER_REVISION }).execute({
			target: DESTINATION_PATH,
			editor: "opencode",
			revision: REVISION,
		});

		expect(result.ok).toBeTruthy();
		// The operation is told the explicit revision, and never falls back to the
		// setting.
		const request = operations.enroll.execute.mock.calls[0]?.[0];
		expect(request?.sourceRevision).toBe(REVISION);
		expect(request?.sourceRevision).not.toBe(OTHER_REVISION);
	});

	test("the verification's result decides currency, not the write", async () => {
		const operations = makeOperations();
		operations.check.execute.mockResolvedValueOnce(makeDrifted());

		const result = await operation({ operations }).execute({
			target: DESTINATION_PATH,
			editor: "opencode",
			revision: undefined,
		});

		expect(result.ok).toBeTruthy();
		expect(result.ok && result.value.current).toBe(false);
		expect(result.ok && result.value.runs.length).toBe(2);
	});

	test("a failed write stops before verification", async () => {
		const operations = makeOperations();
		operations.enroll.execute.mockResolvedValueOnce(makeOutcomeRefused());

		const result = await operation({ operations }).execute({
			target: DESTINATION_PATH,
			editor: "opencode",
			revision: undefined,
		});

		expect(result.ok).toBeTruthy();
		expect(operations.enroll.execute).toHaveBeenCalledTimes(1);
		expect(operations.check.execute).not.toHaveBeenCalled();
		expect(result.ok && result.value.current).toBe(false);
		expect(result.ok && result.value.runs.length).toBe(1);
	});
});
