/**
 * Unit: the update use case's refusals that stop a run before anything is
 * written.
 *
 * One behavioral concern, one group per refusal: the update use case reports a
 * typed returned failure — never an exception — that names what diverged, and no
 * destination payload is read, no binding is saved and no blocker is synced. A
 * run that asks for another editor than the destination is enrolled for never
 * reaches the write-target preflight; a source whose clearance record now
 * declares another destination is the destination drift `apply` refuses, naming
 * the source and both destinations (contract T2, T3).
 */

import { beforeEach, describe, expect, test, vi } from "vitest";
import { mock, type MockProxy } from "vitest-mock-extended";

import { ApplyCoreRevision } from "#application/synchronization/apply-core-revision.ts";
import type {
	BindingsStore,
	ClearanceStore,
	DestinationFiles,
	FilesystemLayout,
	SourceFiles,
	WriteTargetGuard,
} from "#domain/synchronization/ports.ts";
import {
	BOUND_SOURCE,
	RELOCATED_BOUND_DESTINATION,
	SYNCHRONIZATION_DESTINATION_ROOT,
	makeBindingsDocument,
	makeClearanceLoad,
	makeRelocatedClearanceLoad,
	makeSynchronizationRequest,
} from "#support/synchronization.factory.ts";

/** The update use case's doubled collaborators. */
type UpdatePorts = {
	readonly bindings: MockProxy<BindingsStore>;
	readonly clearance: MockProxy<ClearanceStore>;
	readonly sources: MockProxy<SourceFiles>;
	readonly destinations: MockProxy<DestinationFiles>;
	readonly layout: MockProxy<FilesystemLayout>;
	readonly guard: MockProxy<WriteTargetGuard>;
};

/** The update use case with every port doubled, overridable per case. */
function makeUpdate(overrides: Partial<UpdatePorts> = {}): UpdatePorts & { readonly useCase: ApplyCoreRevision } {
	const bindings = overrides.bindings ?? mock<BindingsStore>();
	bindings.load.mockResolvedValue(makeBindingsDocument());
	const ports: UpdatePorts = {
		bindings,
		clearance: overrides.clearance ?? mock<ClearanceStore>(),
		sources: overrides.sources ?? mock<SourceFiles>(),
		destinations: overrides.destinations ?? mock<DestinationFiles>(),
		layout: overrides.layout ?? mock<FilesystemLayout>(),
		guard: overrides.guard ?? mock<WriteTargetGuard>(),
	};
	return { ...ports, useCase: new ApplyCoreRevision(ports) };
}

describe("enrolled-editor refusal", () => {
	beforeEach(() => {
		vi.clearAllMocks();
	});

	test("a run for another editor is refused by name and never reaches the write-target guard", async () => {
		const { useCase, bindings, guard } = makeUpdate();

		const outcome = await useCase.execute(makeSynchronizationRequest({ editor: "cursor" }));

		expect(outcome.ok).toBe(false);
		const failure = outcome.ok ? null : outcome.failure;
		expect(failure?.code).toBe("invalid");
		expect(failure?.message).toMatch(/enrolled for editor 'opencode'/);
		expect(failure?.message).toMatch(/requested 'cursor'/);

		// A refusal is reached before any write target is even classified.
		expect(guard.refuse).not.toHaveBeenCalled();
		expect(bindings.save).not.toHaveBeenCalled();
	});
});

describe("destination drift refusal", () => {
	beforeEach(() => {
		vi.clearAllMocks();
	});

	test("a source the registry relocated is refused by name and nothing is written", async () => {
		const clearance = mock<ClearanceStore>();
		clearance.load.mockResolvedValue(makeRelocatedClearanceLoad());
		const layout = mock<FilesystemLayout>();
		layout.join.mockImplementation((root, relative) => `${root}/${relative}`);
		const guard = mock<WriteTargetGuard>();
		guard.refuse.mockResolvedValue(null);
		const { useCase, bindings, sources, destinations } = makeUpdate({ clearance, layout, guard });

		const outcome = await useCase.execute(makeSynchronizationRequest());

		expect(outcome.ok).toBe(false);
		const failure = outcome.ok ? null : outcome.failure;
		expect(failure?.code).toBe("drift");
		// The report names the source, the destination it is bound to, and the one
		// the registry now declares.
		expect(failure?.message).toContain(`destination drift: ${BOUND_SOURCE} is bound to '${BOUND_SOURCE}'`);
		expect(failure?.message).toContain(`now declares '${RELOCATED_BOUND_DESTINATION}'`);

		// Nothing was written and no payload was read from a destination: the moved
		// destination is the destination owner's migration, not this run's.
		expect(bindings.save).not.toHaveBeenCalled();
		expect(bindings.writeReport).not.toHaveBeenCalled();
		expect(destinations.readText).not.toHaveBeenCalled();
		expect(destinations.readBytes).not.toHaveBeenCalled();
		expect(destinations.writeText).not.toHaveBeenCalled();
		expect(destinations.writeBytes).not.toHaveBeenCalled();
		expect(layout.syncBlocker).not.toHaveBeenCalled();
		expect(layout.ensureDirectory).not.toHaveBeenCalled();
		expect(sources.readCore).not.toHaveBeenCalled();
	});
});

/** The destination paths the OpenCode secret material is written to. */
const DESTINATION_ROOT = SYNCHRONIZATION_DESTINATION_ROOT;
const CONFIGURATION_PATH = `${DESTINATION_ROOT}/.opencode/opencode.jsonc`;
const GITIGNORE_PATH = `${DESTINATION_ROOT}/.gitignore`;
const SECRETS_DIRECTORY = `${DESTINATION_ROOT}/.secrets`;
const SECRET_PATH = `${DESTINATION_ROOT}/.secrets/context7-api-key`;
const PAYLOAD_PATH = `${DESTINATION_ROOT}/${BOUND_SOURCE}`;

/** The one cleared raw source's bytes. */
const PAYLOAD = new TextEncoder().encode("payload\n");

type WritableUpdateOptions = {
	readonly editor?: "opencode" | "cursor";
	/** Absolute paths the destination already holds. */
	readonly existing?: readonly string[];
	/** The destination's `.gitignore` text; `null` means it is absent. */
	readonly gitignore?: string | null;
};

/**
 * The update use case arranged to reach its writes: one cleared raw source, an
 * existing destination payload, and the OpenCode configuration the secret work
 * keys off.
 */
function makeWritableUpdate(options: WritableUpdateOptions = {}) {
	const bindings = mock<BindingsStore>();
	bindings.load.mockResolvedValue(
		makeBindingsDocument({
			editor: options.editor ?? "opencode",
			bindings: [{ source: BOUND_SOURCE, destinations: [BOUND_SOURCE], declaredMode: "raw" }],
		}),
	);

	const clearance = mock<ClearanceStore>();
	clearance.load.mockResolvedValue(makeClearanceLoad({ [BOUND_SOURCE]: { mode: "raw" } }));

	const existing = new Set(options.existing ?? [CONFIGURATION_PATH, PAYLOAD_PATH]);
	const layout = mock<FilesystemLayout>();
	layout.join.mockImplementation((root, relative) => `${root}/${relative}`);
	layout.exists.mockImplementation(async (path) => existing.has(path));
	layout.isFile.mockImplementation(async (path) => existing.has(path));

	const guard = mock<WriteTargetGuard>();
	guard.refuse.mockResolvedValue(null);

	const sources = mock<SourceFiles>();
	sources.readBytes.mockResolvedValue(PAYLOAD);

	const gitignore = options.gitignore ?? null;
	const destinations = mock<DestinationFiles>();
	destinations.readText.mockImplementation(async (path) => (path === GITIGNORE_PATH ? gitignore : null));

	const useCase = new ApplyCoreRevision({ bindings, clearance, sources, destinations, layout, guard });
	return { useCase, bindings, destinations, layout };
}

/** Every byte payload written to one destination path. */
function writtenTo(destinations: MockProxy<DestinationFiles>, path: string): readonly Uint8Array[] {
	return destinations.writeBytes.mock.calls.filter(([target]) => target === path).map(([, bytes]) => bytes);
}

/** One written payload, as text. */
function textOf(bytes: Uint8Array | undefined): string {
	return new TextDecoder().decode(bytes);
}

describe("OpenCode secret material", () => {
	beforeEach(() => {
		vi.clearAllMocks();
	});

	test("an OpenCode run creates the secret directory, an empty credential file and the ignore rule", async () => {
		const { useCase, destinations, layout } = makeWritableUpdate();

		const outcome = await useCase.execute(makeSynchronizationRequest({ editor: "opencode" }));

		expect(outcome.ok).toBe(true);
		// The run reached its writes: the bound payload is on disk.
		expect(writtenTo(destinations, PAYLOAD_PATH)).toHaveLength(1);
		expect(layout.ensureDirectory).toHaveBeenCalledWith(SECRETS_DIRECTORY);
		expect(writtenTo(destinations, SECRET_PATH)).toEqual([new Uint8Array()]);
		expect(textOf(writtenTo(destinations, GITIGNORE_PATH)[0])).toBe(".secrets/\n");
	});

	test("an existing credential file keeps its bytes and is never rewritten", async () => {
		const { useCase, destinations } = makeWritableUpdate({
			existing: [CONFIGURATION_PATH, PAYLOAD_PATH, SECRET_PATH],
		});

		const outcome = await useCase.execute(makeSynchronizationRequest({ editor: "opencode" }));

		expect(outcome.ok).toBe(true);
		expect(writtenTo(destinations, SECRET_PATH)).toEqual([]);
	});

	test("a cursor run writes no secret material at all", async () => {
		const { useCase, destinations, layout } = makeWritableUpdate({ editor: "cursor" });

		const outcome = await useCase.execute(makeSynchronizationRequest({ editor: "cursor" }));

		expect(outcome.ok).toBe(true);
		expect(writtenTo(destinations, PAYLOAD_PATH)).toHaveLength(1);
		expect(layout.ensureDirectory).not.toHaveBeenCalledWith(SECRETS_DIRECTORY);
		expect(writtenTo(destinations, SECRET_PATH)).toEqual([]);
		expect(writtenTo(destinations, GITIGNORE_PATH)).toEqual([]);
	});
});

describe("the destination's ignore rule", () => {
	beforeEach(() => {
		vi.clearAllMocks();
	});

	test("an effective .secrets/ rule among other rules is left alone", async () => {
		const existing = "node_modules/\n.secrets/\n*.log\n";
		const { useCase, destinations } = makeWritableUpdate({ gitignore: existing });

		await useCase.execute(makeSynchronizationRequest({ editor: "opencode" }));

		expect(writtenTo(destinations, GITIGNORE_PATH)).toEqual([]);
	});

	test("an effective rule with a trailing comment counts", async () => {
		const existing = ".secrets # local credentials\n";
		const { useCase, destinations } = makeWritableUpdate({ gitignore: existing });

		await useCase.execute(makeSynchronizationRequest({ editor: "opencode" }));

		expect(writtenTo(destinations, GITIGNORE_PATH)).toEqual([]);
	});

	test("a commented-out line does not count", async () => {
		const { useCase, destinations } = makeWritableUpdate({ gitignore: "# .secrets/\n" });

		await useCase.execute(makeSynchronizationRequest({ editor: "opencode" }));

		expect(textOf(writtenTo(destinations, GITIGNORE_PATH)[0])).toBe("# .secrets/\n.secrets/\n");
	});

	test("other rules are preserved, including a missing trailing newline", async () => {
		const { useCase, destinations } = makeWritableUpdate({ gitignore: "dist" });

		await useCase.execute(makeSynchronizationRequest({ editor: "opencode" }));

		expect(textOf(writtenTo(destinations, GITIGNORE_PATH)[0])).toBe("dist\n.secrets/\n");
	});
});
