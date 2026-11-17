/**
 * Unit: the reconciliation proposal use case.
 *
 * One behavioral concern per group: a bound pair whose bytes agree is proposed
 * as kept with nothing to act on, a pair whose bytes differ is preserved for the
 * destination owner, and the three inputs a proposal cannot work from — a
 * target that is not a directory, an absent bindings document and a written one
 * that cannot be read — are returned as typed failures rather than thrown
 * (contract T2, T3).
 *
 * The domain's rule is `classifyBoundPath` and `proposalRequiresAction`, so the
 * expected class, action and `requiresAction` below are read from that rule, not
 * asserted from what the operation happens to return.
 */

import { beforeEach, describe, expect, test, vi } from "vitest";
import { mock, type MockProxy } from "vitest-mock-extended";

import { ReconcileDestination } from "#application/reconcile-destination.ts";
import type { BindingsReader } from "#domain/ports/bindings-reader.ts";
import type { DestinationReader } from "#domain/ports/destination-reader.ts";
import type { FilesystemProbe } from "#domain/ports/filesystem-probe.ts";
import type { PathInspection } from "#domain/ports/path-inspection.ts";
import type { BindingsDocument } from "#domain/synchronization/bindings.ts";
import type { ClearanceLoad, ClearanceStore, SourceFiles } from "#domain/synchronization/ports.ts";
import {
	BOUND_SOURCE,
	SOURCE_ROOT,
	SYNCHRONIZATION_BINDINGS_PATH,
	SYNCHRONIZATION_DESTINATION_ROOT,
	makeBindingsDocument,
	makeClearanceLoad,
} from "#support/synchronization.factory.ts";

/** The port doubles one reconciliation run is given. */
type ReconcilePorts = {
	readonly files: MockProxy<FilesystemProbe>;
	readonly bindings: MockProxy<BindingsReader>;
	readonly clearance: MockProxy<ClearanceStore>;
	readonly sources: MockProxy<SourceFiles>;
	readonly destinations: MockProxy<DestinationReader>;
	readonly layout: MockProxy<PathInspection>;
};

/** The bindings document describing the one raw source these cases reconcile. */
function makeBoundDocument(): BindingsDocument {
	return makeBindingsDocument({
		bindings: [{ source: BOUND_SOURCE, destinations: [BOUND_SOURCE], declaredMode: "raw" }],
	});
}

/** The clearance registry that clears that source raw at its own path. */
function makeBoundClearance(): ClearanceLoad {
	return makeClearanceLoad({ [BOUND_SOURCE]: { mode: "raw" } });
}

/**
 * A filesystem probe answering the directory and file questions for one target.
 *
 * Each case states the two answers it needs; a case that never reaches them
 * takes the enrolled-looking defaults.
 */
function makeProbe(
	options: { readonly directory?: boolean; readonly bindingsPresent?: boolean } = {},
): MockProxy<FilesystemProbe> {
	const probe = mock<FilesystemProbe>();
	probe.resolve.mockImplementation((path) => path);
	probe.isDirectory.mockResolvedValue(options.directory ?? true);
	probe.isFile.mockResolvedValue(options.bindingsPresent ?? false);
	return probe;
}

/** The use case with every port doubled, overridable per case. */
function makeReconciliation(
	overrides: Partial<ReconcilePorts> = {},
): ReconcilePorts & { readonly useCase: ReconcileDestination } {
	const layout = overrides.layout ?? mock<PathInspection>();
	layout.join.mockImplementation((root, relative) => `${root}/${relative}`);
	layout.isFile.mockResolvedValue(true);
	layout.enumerateFilesUnder.mockResolvedValue([]);
	const ports: ReconcilePorts = {
		files: overrides.files ?? makeProbe(),
		bindings: overrides.bindings ?? mock<BindingsReader>(),
		clearance: overrides.clearance ?? mock<ClearanceStore>(),
		sources: overrides.sources ?? mock<SourceFiles>(),
		destinations: overrides.destinations ?? mock<DestinationReader>(),
		layout,
	};
	return { ...ports, useCase: new ReconcileDestination({ checkoutRoot: SOURCE_ROOT, ...ports }) };
}

describe("bound pair whose bytes agree", () => {
	beforeEach(() => {
		vi.clearAllMocks();
	});

	test("one bound path is managed and kept, and nothing needs the destination owner", async () => {
		const bytes = new TextEncoder().encode(`# ${BOUND_SOURCE}\n`);
		const bindings = mock<BindingsReader>();
		bindings.load.mockResolvedValue(makeBoundDocument());
		const clearance = mock<ClearanceStore>();
		clearance.load.mockResolvedValue(makeBoundClearance());
		const sources = mock<SourceFiles>();
		sources.readBytes.mockResolvedValue(bytes);
		const destinations = mock<DestinationReader>();
		destinations.readBytes.mockResolvedValue(bytes);
		const { useCase } = makeReconciliation({ bindings, clearance, sources, destinations });

		const result = await useCase.execute({ target: SYNCHRONIZATION_DESTINATION_ROOT });

		expect(result.ok).toBe(true);
		const proposal = result.ok ? result.value : null;
		// The registry still clears the source and still delivers it where the
		// bindings record it, and the destination still carries the source's bytes,
		// so the rule's `managedInPlace` branch is reached with `matchesSource`.
		expect(proposal?.entries).toEqual([
			{
				path: BOUND_SOURCE,
				source: BOUND_SOURCE,
				classification: "managed",
				action: "kept",
				detail: `matches ${BOUND_SOURCE}`,
			},
		]);
		// `proposalRequiresAction` is false only when every entry's action is `kept`.
		expect(proposal?.requiresAction).toBe(false);
	});
});

describe("bound pair whose bytes differ", () => {
	beforeEach(() => {
		vi.clearAllMocks();
	});

	test("a destination copy that no longer carries its source is preserved and requires action", async () => {
		const bindings = mock<BindingsReader>();
		bindings.load.mockResolvedValue(makeBoundDocument());
		const clearance = mock<ClearanceStore>();
		clearance.load.mockResolvedValue(makeBoundClearance());
		const sources = mock<SourceFiles>();
		sources.readBytes.mockResolvedValue(new TextEncoder().encode(`# ${BOUND_SOURCE}\n`));
		const destinations = mock<DestinationReader>();
		destinations.readBytes.mockResolvedValue(new TextEncoder().encode("# edited in the destination\n"));
		const { useCase } = makeReconciliation({ bindings, clearance, sources, destinations });

		const result = await useCase.execute({ target: SYNCHRONIZATION_DESTINATION_ROOT });

		expect(result.ok).toBe(true);
		const proposal = result.ok ? result.value : null;
		// `managedInPlace` with `matchesSource` false is the "locally modified"
		// class, and its action is "preserved": the difference is the destination
		// owner's to keep or to discard.
		expect(proposal?.entries.map((entry) => [entry.classification, entry.action])).toEqual([
			["locally modified", "preserved"],
		]);
		expect(proposal?.entries[0]?.detail).toContain(`content differs from ${BOUND_SOURCE}`);
		expect(proposal?.requiresAction).toBe(true);
	});
});

describe("target that is not a directory", () => {
	beforeEach(() => {
		vi.clearAllMocks();
	});

	test("a target that is not a directory is returned as an invalid-destination failure", async () => {
		const files = makeProbe({ bindingsPresent: false, directory: false });
		const { useCase, bindings, clearance } = makeReconciliation({ files });

		const result = await useCase.execute({ target: SYNCHRONIZATION_DESTINATION_ROOT });

		expect(result.ok).toBe(false);
		const failure = result.ok ? null : result.failure;
		expect(failure?.code).toBe("invalid-destination");
		expect(failure?.message).toContain(`destination is not a directory: ${SYNCHRONIZATION_DESTINATION_ROOT}`);
		// Nothing was read: no bindings document and no clearance registry.
		expect(bindings.load).not.toHaveBeenCalled();
		expect(clearance.load).not.toHaveBeenCalled();
	});
});

describe("absent bindings", () => {
	beforeEach(() => {
		vi.clearAllMocks();
	});

	test("a directory with no bindings document is returned as an unavailable-configuration failure", async () => {
		const files = makeProbe({ bindingsPresent: false, directory: true });
		const bindings = mock<BindingsReader>();
		// The reader reports absent and unreadable identically; the probe's answer
		// to "is there a file here" is what separates them.
		bindings.load.mockResolvedValue(null);
		const { useCase, clearance, layout } = makeReconciliation({ files, bindings });

		const result = await useCase.execute({ target: SYNCHRONIZATION_DESTINATION_ROOT });

		expect(result.ok).toBe(false);
		const failure = result.ok ? null : result.failure;
		expect(failure?.code).toBe("unavailable-configuration");
		expect(failure?.message).toContain(`no bindings: ${SYNCHRONIZATION_BINDINGS_PATH}`);
		// An unenrolled destination has nothing to reconcile, so the registry is
		// never consulted.
		expect(clearance.load).not.toHaveBeenCalled();
		expect(layout.isFile).not.toHaveBeenCalled();
	});
});

describe("bindings document that cannot be read", () => {
	beforeEach(() => {
		vi.clearAllMocks();
	});

	test("a written bindings document that does not load is returned as an invalid-bindings failure", async () => {
		const files = makeProbe({ bindingsPresent: true, directory: true });
		const bindings = mock<BindingsReader>();
		bindings.load.mockResolvedValue(null);
		const { useCase, clearance, layout } = makeReconciliation({ files, bindings });

		const result = await useCase.execute({ target: SYNCHRONIZATION_DESTINATION_ROOT });

		expect(result.ok).toBe(false);
		const failure = result.ok ? null : result.failure;
		expect(failure?.code).toBe("invalid-bindings");
		expect(failure?.message).toContain(`invalid bindings: ${SYNCHRONIZATION_BINDINGS_PATH}`);
		expect(clearance.load).not.toHaveBeenCalled();
		expect(layout.isFile).not.toHaveBeenCalled();
	});
});
