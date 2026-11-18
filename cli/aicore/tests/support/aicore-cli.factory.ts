/**
 * Shared test data for the synchronization CLI suite.
 *
 * Contract T15: test data comes from a factory, never from inline literals
 * scattered across modules.
 *
 * Contract T16: a doubled use-case collaborator is a typed `MockProxy` built
 * with `vitest-mock-extended`, never a hand-written mock. Every double is
 * constructed by the test that owns it, so no mock is shared across cases and
 * no queued one-shot implementation survives into another case.
 */

import { mock, type MockProxy } from "vitest-mock-extended";

import { ApplyCoreRevision } from "#application/synchronization/apply-core-revision.ts";
import { EnrollDestinations } from "#application/synchronization/enroll-destinations.ts";
import type { EnrollmentRequest, SynchronizationRequest } from "#application/synchronization/requests.ts";
import { VerifyDestinations } from "#application/synchronization/verify-destinations.ts";
import type { SynchronizeOutcome } from "#domain/outcomes.ts";
import type { FilesystemProbe } from "#domain/ports/filesystem-probe.ts";
import type { SavedSelection, SelectionStore } from "#domain/ports/selection-store.ts";
import type { OperatorSettings } from "#domain/settings.ts";
import { drift, type OperationOutcome } from "#domain/synchronization/failures.ts";

/** A valid 40-character lowercase hex revision. */
export const REVISION = "0123456789abcdef0123456789abcdef01234567";

/** A second distinct valid revision, for override comparisons. */
export const OTHER_REVISION = "fedcba9876543210fedcba9876543210fedcba98";

export const CHECKOUT_ROOT = "G:/projects/ai-core";

export const DESTINATION_PATH = "G:/projects/destination";

export const BINDINGS_PATH = `${DESTINATION_PATH}/.aicore/core.yaml`;

export function makeSettings(overrides: Partial<OperatorSettings> = {}): OperatorSettings {
	return { sourceRevision: REVISION, localConfigPath: undefined, ...overrides };
}

/** The request a synchronization run hands to its operations. */
export function makeSynchronizationRequest(overrides: Partial<SynchronizationRequest> = {}): SynchronizationRequest {
	return {
		sourceRoot: CHECKOUT_ROOT,
		destinationRoot: DESTINATION_PATH,
		bindingsPath: BINDINGS_PATH,
		sourceRevision: REVISION,
		editor: "opencode",
		...overrides,
	};
}

/** The request a first enrollment hands to its operation. */
export function makeEnrollmentRequest(overrides: Partial<EnrollmentRequest> = {}): EnrollmentRequest {
	return {
		...makeSynchronizationRequest(),
		regionDeclarations: [],
		rawDeclarations: [],
		bindCleared: true,
		rootOverride: null,
		...overrides,
	};
}

/** A completed operation's domain result. */
export function makeSucceeded(message = "applied"): OperationOutcome {
	return { ok: true, message };
}

/** An operation's domain result for a destination that is not current. */
export function makeDrifted(message = "destination is not current"): OperationOutcome {
	return { ok: false, failure: drift(message) };
}

/** An operation's domain result for input the operation refuses. */
export function makeOutcomeRefused(message = "invalid bindings"): OperationOutcome {
	return {
		ok: false,
		failure: { code: "invalid", message },
	};
}

export function makeSynchronizeOutcome(overrides: Partial<SynchronizeOutcome> = {}): SynchronizeOutcome {
	return {
		destination: DESTINATION_PATH,
		editor: "opencode",
		enrolled: true,
		runs: [makeSucceeded()],
		current: true,
		...overrides,
	};
}

export function makeSavedSelection(overrides: Partial<SavedSelection> = {}): SavedSelection {
	return { target: DESTINATION_PATH, editor: "opencode", ...overrides };
}

/** The three application operations a synchronization run collaborates with. */
export type OperationDoubles = {
	readonly check: MockProxy<VerifyDestinations>;
	readonly apply: MockProxy<ApplyCoreRevision>;
	readonly enroll: MockProxy<EnrollDestinations>;
};

/**
 * The three operations, each reporting its own successful result by default.
 *
 * A case that needs a different result queues it on the operation it concerns,
 * so the assertion stays on the operation whose behaviour it measures.
 */
export function makeOperations(): OperationDoubles {
	const operations: OperationDoubles = {
		check: mock<VerifyDestinations>(),
		apply: mock<ApplyCoreRevision>(),
		enroll: mock<EnrollDestinations>(),
	};

	operations.check.execute.mockResolvedValue(makeSucceeded("current"));
	operations.apply.execute.mockResolvedValue(makeSucceeded("applied"));
	operations.enroll.execute.mockResolvedValue(makeSucceeded("initialized"));
	return operations;
}

/** A filesystem double describing an imaginary destination. */
export function makeFilesystem(
	options: {
		readonly directories?: readonly string[];
		readonly files?: readonly string[];
		readonly insideCheckout?: readonly string[];
	} = {},
): MockProxy<FilesystemProbe> {
	const directories = options.directories ?? [];
	const files = options.files ?? [];
	const insideCheckout = options.insideCheckout ?? [];

	const probe = mock<FilesystemProbe>();
	probe.resolve.mockImplementation((path) => path);
	probe.isDirectory.mockImplementation(async (path) => directories.includes(path));
	probe.isFile.mockImplementation(async (path) => files.includes(path));
	probe.isInside.mockImplementation((_root, path) => insideCheckout.includes(path));
	return probe;
}

/**
 * A selection store double.
 *
 * A write replaces the stored selection, so a later read observes it; the write
 * itself is asserted on the port mock.
 */
export function makeSelections(saved?: SavedSelection): MockProxy<SelectionStore> {
	let stored = saved;

	const selections = mock<SelectionStore>();
	selections.read.mockImplementation(async () => stored);
	selections.write.mockImplementation(async (selection) => {
		stored = selection;
	});
	return selections;
}
