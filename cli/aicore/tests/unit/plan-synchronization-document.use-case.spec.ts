/**
 * Unit: the document determination — root resolution, enrollment and lifecycle.
 *
 * One behavioral concern per group: the instruction root is resolved or refused,
 * an enrollment binds the cleared sources the run asks for, a preserved source
 * leaves its destination outstanding, and the determination never finalizes the
 * document. The layout is doubled; every document comes from the shared factory
 * (contract T2, T3, T15).
 */

import { beforeEach, describe, expect, test, vi } from "vitest";
import { mock, type MockProxy } from "vitest-mock-extended";

import {
	PlanSynchronizationDocument,
	type DocumentDeterminationInput,
	type SynchronizationIntent,
} from "#application/synchronization/plan-synchronization-document.ts";
import type { ClearanceModes } from "#application/synchronization/clearance-modes.ts";
import type { BindingMode } from "#domain/synchronization/constants.ts";
import type { ClearanceEntry } from "#domain/synchronization/clearance.ts";
import { parseClearanceDocument } from "#domain/synchronization/clearance.ts";
import type { BindingsDocument } from "#domain/synchronization/bindings.ts";
import type { FilesystemLayout } from "#domain/synchronization/ports.ts";
import {
	BOUND_SOURCE,
	SOURCE_ROOT,
	SYNCHRONIZATION_DESTINATION_ROOT,
	makeBindingsDocument,
	makeClearanceText,
} from "#support/synchronization.factory.ts";

/** The expanded clearance one run acts on, from the factory's registry text. */
function makeClearance(cleared: Readonly<Record<string, Readonly<Record<string, unknown>>>>): ClearanceModes {
	const parsed = parseClearanceDocument(JSON.parse(makeClearanceText(cleared)));
	if (!parsed.ok) {
		throw new Error(`factory clearance text is unreadable: ${parsed.reason}`);
	}
	const modes = new Map<string, BindingMode>();
	const destinations = new Map<string, string>();
	for (const [key, entry] of parsed.entries) {
		if (entry.kind !== "file") {
			continue;
		}
		modes.set(key, entry.mode);
		destinations.set(key, key);
	}
	return {
		modes,
		destinations,
		entries: parsed.entries as ReadonlyMap<string, ClearanceEntry>,
		exists: true,
		reason: null,
	};
}

/** A determination input over the given document, clearance and intent. */
function makeInput(
	document: BindingsDocument,
	clearance: ClearanceModes,
	intent: SynchronizationIntent,
): DocumentDeterminationInput {
	return {
		document,
		clearance,
		editor: "opencode",
		sourceRoot: SOURCE_ROOT,
		destinationRoot: SYNCHRONIZATION_DESTINATION_ROOT,
		intent,
	};
}

/** The operation with its layout doubled. */
function makeOperation(): {
	readonly operation: PlanSynchronizationDocument;
	readonly layout: MockProxy<FilesystemLayout>;
} {
	const layout = mock<FilesystemLayout>();
	layout.join.mockImplementation((root, relative) => `${root}/${relative}`);
	return { operation: new PlanSynchronizationDocument({ layout }), layout };
}

const UPDATE: SynchronizationIntent = { kind: "update" };

describe("instruction root resolution", () => {
	beforeEach(() => {
		vi.clearAllMocks();
	});

	test("a root-role source with no detectable instruction root is refused instead of guessed", async () => {
		const { operation, layout } = makeOperation();
		layout.detectRootFile.mockResolvedValue(null);
		const clearance = makeClearance({ [BOUND_SOURCE]: { mode: "region", role: "root" } });

		const outcome = await operation.execute(makeInput(makeBindingsDocument({ bindings: [] }), clearance, UPDATE));

		expect(outcome.ok).toBe(false);
		const failure = outcome.ok ? null : outcome.failure;
		expect(failure?.code).toBe("drift");
		expect(failure?.message).toBe("destination instruction root not found; pass --root");
	});

	test("an enrollment places the root-role source at the explicit override", async () => {
		const { operation, layout } = makeOperation();
		layout.isFile.mockResolvedValue(true);
		const clearance = makeClearance({ [BOUND_SOURCE]: { mode: "region", role: "root" } });

		const outcome = await operation.execute(
			makeInput(makeBindingsDocument({ bindings: [] }), clearance, {
				kind: "enroll",
				rootOverride: "CLAUDE.md",
				enrollUnseen: true,
			}),
		);

		expect(outcome.ok).toBe(true);
		expect(outcome.ok && outcome.value.rootSource).toBe(BOUND_SOURCE);
		expect(outcome.ok && outcome.value.rootDestination).toBe("CLAUDE.md");
		expect(outcome.ok && outcome.value.document.root).toBe("CLAUDE.md");
	});
});

describe("enrollment", () => {
	beforeEach(() => {
		vi.clearAllMocks();
	});

	test("an update enrolls a newly cleared source and classifies it distributable", async () => {
		const { operation, layout } = makeOperation();
		layout.exists.mockResolvedValue(false);
		layout.isFile.mockResolvedValue(true);
		const clearance = makeClearance({ [BOUND_SOURCE]: { mode: "raw" } });

		const outcome = await operation.execute(makeInput(makeBindingsDocument({ bindings: [] }), clearance, UPDATE));

		expect(outcome.ok).toBe(true);
		const value = outcome.ok ? outcome.value : null;
		expect(value?.document.bindings.map((entry) => entry.source)).toEqual([BOUND_SOURCE]);
		expect(value?.distributable.map((entry) => entry.source)).toEqual([BOUND_SOURCE]);
		expect(value?.newRawDestinations.has(BOUND_SOURCE)).toBe(true);
	});

	test("an enrollment that is not asked to bind cleared sources enrolls nothing", async () => {
		const { operation, layout } = makeOperation();
		layout.isFile.mockResolvedValue(true);
		const clearance = makeClearance({ [BOUND_SOURCE]: { mode: "raw" } });

		const outcome = await operation.execute(
			makeInput(makeBindingsDocument({ bindings: [] }), clearance, {
				kind: "enroll",
				rootOverride: null,
				enrollUnseen: false,
			}),
		);

		expect(outcome.ok).toBe(true);
		expect(outcome.ok && outcome.value.document.bindings).toEqual([]);
		expect(outcome.ok && outcome.value.newRawDestinations.size).toBe(0);
	});
});

describe("lifecycle classification", () => {
	beforeEach(() => {
		vi.clearAllMocks();
	});

	test("a source whose ownership the registry no longer declares is preserved and leaves pending", async () => {
		const { operation, layout } = makeOperation();
		layout.isFile.mockResolvedValue(false);
		const document = makeBindingsDocument({
			bindings: [{ source: BOUND_SOURCE, destinations: [BOUND_SOURCE], declaredMode: "raw" }],
		});

		const outcome = await operation.execute(makeInput(document, makeClearance({}), UPDATE));

		expect(outcome.ok).toBe(true);
		const value = outcome.ok ? outcome.value : null;
		expect(value?.retired).toEqual([]);
		expect(value?.distributable).toEqual([]);
		expect(value?.requiresReconciliation.map((entry) => entry.reason)).toEqual(["unestablished"]);
		// The determination records the outstanding path but does not finalize it:
		// the command's payload planner owns the pinned document.
		expect(value?.document.pending).toContain(BOUND_SOURCE);
	});
});
