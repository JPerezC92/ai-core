/**
 * Unit: refusals that stop a run before anything is written.
 *
 * One behavioral concern — every pre-write precondition reports a typed failure
 * and runs no operation (contract T2, T3; refusal is a returned value).
 */

import { beforeEach, describe, expect, test, vi } from "vitest";
import type { MockProxy } from "vitest-mock-extended";

import { SynchronizeDestination } from "#application/synchronize-destination.ts";
import type { FilesystemProbe } from "#domain/ports/filesystem-probe.ts";
import type { SelectionStore } from "#domain/ports/selection-store.ts";
import {
	BINDINGS_PATH,
	CHECKOUT_ROOT,
	DESTINATION_PATH,
	REVISION,
	makeFilesystem,
	makeOperations,
	makeSavedSelection,
	makeSelections,
	makeSettings,
	type OperationDoubles,
} from "#support/aicore-cli.factory.ts";

function operation(options: {
	operations: OperationDoubles;
	files?: MockProxy<FilesystemProbe>;
	selections?: MockProxy<SelectionStore>;
	/** Omitted means "use the valid default revision"; pass `null` to omit it. */
	sourceRevision?: string | null;
}) {
	const sourceRevision = options.sourceRevision === null ? undefined : (options.sourceRevision ?? REVISION);
	return new SynchronizeDestination({
		checkoutRoot: CHECKOUT_ROOT,
		settings: makeSettings({ sourceRevision }),
		...options.operations,
		files: options.files ?? makeFilesystem({ directories: [DESTINATION_PATH] }),
		selections: options.selections ?? makeSelections(),
	});
}

/** No operation was run: a refusal writes nothing and asks no operation anything. */
function expectNoOperationRun(operations: OperationDoubles): void {
	expect(operations.check.execute).not.toHaveBeenCalled();
	expect(operations.apply.execute).not.toHaveBeenCalled();
	expect(operations.enroll.execute).not.toHaveBeenCalled();
}

describe("pre-write refusals", () => {
	beforeEach(() => {
		vi.clearAllMocks();
	});

	test("an unknown editor is refused by name and runs no operation", async () => {
		const operations = makeOperations();
		const result = await operation({ operations }).execute({
			target: DESTINATION_PATH,
			editor: "vim",
			revision: undefined,
		});

		expect(!result.ok).toBeTruthy();
		expect(result.ok ? "" : result.failure.code).toBe("unsupported-editor");
		expect(result.ok ? "" : result.failure.message).toMatch(/unknown editor "vim"/);
		expectNoOperationRun(operations);
	});

	test("a missing revision runs no operation", async () => {
		const operations = makeOperations();
		const result = await operation({ operations, sourceRevision: null }).execute({
			target: DESTINATION_PATH,
			editor: "opencode",
			revision: undefined,
		});

		expect(!result.ok).toBeTruthy();
		expect(result.ok ? "" : result.failure.code).toBe("invalid-revision");
		expectNoOperationRun(operations);
	});

	test("a destination that is not a directory is refused", async () => {
		const operations = makeOperations();
		const result = await operation({ operations, files: makeFilesystem() }).execute({
			target: DESTINATION_PATH,
			editor: "opencode",
			revision: undefined,
		});

		expect(!result.ok).toBeTruthy();
		expect(result.ok ? "" : result.failure.code).toBe("invalid-destination");
		expectNoOperationRun(operations);
	});

	test("a destination inside the checkout is refused", async () => {
		const operations = makeOperations();
		const result = await operation({
			operations,
			files: makeFilesystem({
				directories: [DESTINATION_PATH],
				insideCheckout: [DESTINATION_PATH],
			}),
		}).execute({
			target: DESTINATION_PATH,
			editor: "opencode",
			revision: undefined,
		});

		expect(!result.ok).toBeTruthy();
		expect(result.ok ? "" : result.failure.code).toBe("invalid-destination");
		expectNoOperationRun(operations);
	});

	test("a bound destination without a recorded editor is never inferred", async () => {
		const operations = makeOperations();
		const result = await operation({
			operations,
			files: makeFilesystem({
				directories: [DESTINATION_PATH],
				files: [BINDINGS_PATH],
			}),
		}).execute({ target: DESTINATION_PATH, editor: undefined, revision: undefined });

		expect(!result.ok).toBeTruthy();
		expect(result.ok ? "" : result.failure.code).toBe("unknown-editor");
		expectNoOperationRun(operations);
	});

	test("switching destination without an editor is refused", async () => {
		const operations = makeOperations();
		const result = await operation({
			operations,
			selections: makeSelections(makeSavedSelection({ target: "G:/projects/old" })),
		}).execute({ target: DESTINATION_PATH, editor: undefined, revision: undefined });

		expect(!result.ok).toBeTruthy();
		expect(result.ok ? "" : result.failure.code).toBe("unknown-editor");
		expectNoOperationRun(operations);
	});

	test("no target and no saved selection is refused", async () => {
		const operations = makeOperations();
		const result = await operation({
			operations,
			selections: makeSelections(),
		}).execute({ target: undefined, editor: "opencode", revision: undefined });

		expect(!result.ok).toBeTruthy();
		expect(result.ok ? "" : result.failure.code).toBe("unavailable-configuration");
		expect(result.ok ? "" : result.failure.message).toMatch(/no destination selected/);
		expectNoOperationRun(operations);
	});
});
