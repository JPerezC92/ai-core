/**
 * Unit: persisting an explicit selection.
 *
 * One behavioral concern — an explicitly stated destination or editor is
 * recorded for later runs, and the recorded value is the resolved destination.
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
	makeOutcomeRefused,
	makeSavedSelection,
	makeSelections,
	makeSettings,
	type OperationDoubles,
} from "#support/aicore-cli.factory.ts";

function operation(options: { operations: OperationDoubles; selections: MockProxy<SelectionStore> }) {
	return new SynchronizeDestination({
		checkoutRoot: CHECKOUT_ROOT,
		settings: makeSettings(),
		...options.operations,
		files: makeFilesystem({
			directories: [DESTINATION_PATH],
			files: [BINDINGS_PATH],
		}),
		selections: options.selections,
	});
}

describe("selection persistence", () => {
	beforeEach(() => {
		vi.clearAllMocks();
	});

	test("an explicit target is recorded against the resolved destination", async () => {
		const selections = makeSelections(makeSavedSelection({ target: "G:/projects/old" }));
		await operation({ operations: makeOperations(), selections }).execute({
			target: DESTINATION_PATH,
			editor: "opencode",
			revision: undefined,
		});

		expect(selections.write).toHaveBeenCalledWith({
			target: DESTINATION_PATH,
			editor: "opencode",
		});
	});

	test("an explicit editor alone is recorded for the current destination", async () => {
		const selections = makeSelections(makeSavedSelection());
		await operation({ operations: makeOperations(), selections }).execute({
			target: undefined,
			editor: "opencode",
			revision: undefined,
		});

		expect(selections.write).toHaveBeenCalledWith({
			target: DESTINATION_PATH,
			editor: "opencode",
		});
	});

	test("a failed write records no selection", async () => {
		const selections = makeSelections();
		const operations = makeOperations();
		operations.apply.execute.mockResolvedValueOnce(makeOutcomeRefused());

		await operation({ operations, selections }).execute({
			target: DESTINATION_PATH,
			editor: "opencode",
			revision: undefined,
		});

		expect(selections.write).not.toHaveBeenCalled();
	});
});
