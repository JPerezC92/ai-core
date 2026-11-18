/**
 * Unit: updating a destination that is already bound.
 *
 * One behavioral concern — the update path runs the update operation and the
 * verification, and never enrolls (contract T2, application use case with
 * doubled collaborators).
 */

import { beforeEach, describe, expect, test, vi } from "vitest";
import type { MockProxy } from "vitest-mock-extended";

import { SynchronizeDestination } from "#application/synchronize-destination.ts";
import type { SelectionStore } from "#domain/ports/selection-store.ts";
import {
	BINDINGS_PATH,
	CHECKOUT_ROOT,
	DESTINATION_PATH,
	makeFilesystem,
	makeOperations,
	makeSavedSelection,
	makeSelections,
	makeSettings,
	makeSynchronizationRequest,
	type OperationDoubles,
} from "#support/aicore-cli.factory.ts";

function operation(options: { operations: OperationDoubles; selections?: MockProxy<SelectionStore> }) {
	return new SynchronizeDestination({
		checkoutRoot: CHECKOUT_ROOT,
		settings: makeSettings(),
		...options.operations,
		files: makeFilesystem({
			directories: [DESTINATION_PATH],
			files: [BINDINGS_PATH],
		}),
		selections: options.selections ?? makeSelections(makeSavedSelection()),
	});
}

describe("update decision", () => {
	beforeEach(() => {
		vi.clearAllMocks();
	});

	test("a bound destination is updated with the update operation and never re-enrolled", async () => {
		const operations = makeOperations();

		const result = await operation({ operations }).execute({
			target: undefined,
			editor: undefined,
			revision: undefined,
		});

		expect(result.ok).toBeTruthy();
		expect(operations.apply.execute).toHaveBeenCalledWith(makeSynchronizationRequest());
		expect(operations.apply.execute).toHaveBeenCalledTimes(1);
		expect(operations.check.execute).toHaveBeenCalledWith(makeSynchronizationRequest());
		expect(operations.check.execute).toHaveBeenCalledTimes(1);
		// The update path never enrolls: the enrollment operation is not run, and the
		// request it would carry a bulk-clearance declaration on is never built.
		expect(operations.enroll.execute).not.toHaveBeenCalled();
		expect(operations.apply.execute.mock.calls[0]?.[0]).not.toHaveProperty("bindCleared");
		expect(result.ok && result.value.enrolled).toBe(false);
	});

	test("the update runs before the verification", async () => {
		const operations = makeOperations();

		await operation({ operations }).execute({
			target: undefined,
			editor: undefined,
			revision: undefined,
		});

		expect(operations.apply.execute.mock.invocationCallOrder[0]).toBeLessThan(
			operations.check.execute.mock.invocationCallOrder[0] as number,
		);
	});

	test("a run that reused the saved selection writes no new selection", async () => {
		const operations = makeOperations();
		const selections = makeSelections(makeSavedSelection());

		await operation({ operations, selections }).execute({
			target: undefined,
			editor: undefined,
			revision: undefined,
		});

		expect(selections.write).not.toHaveBeenCalled();
	});
});
