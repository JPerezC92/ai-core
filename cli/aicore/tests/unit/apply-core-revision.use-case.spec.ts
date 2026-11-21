/**
 * Unit: the update use case — its refusals, and what each mode writes.
 *
 * The refusals stop a run before anything is written: the update use case reports
 * a typed returned failure — never an exception — that names what diverged, and
 * no destination payload is read, no binding is saved and no blocker is synced. A
 * run that asks for another editor than the destination is enrolled for never
 * reaches the write-target preflight; a source whose clearance record now
 * declares another destination is the destination drift `apply` refuses, naming
 * the source and both destinations (contract T2, T3).
 *
 * The remaining groups cover one mode each: a raw target is created byte-verbatim
 * and named as created, a region target is created as a core region, and a merge
 * target is never created while an existing one keeps its own servers and takes
 * the retargeted index. A pending path whose source is no longer region-bound is
 * cleared instead of reconciled.
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
	SOURCE_ROOT,
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
	/** The paths the document already records as outstanding. */
	readonly pending?: readonly string[];
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
			pending: options.pending ?? [],
		}),
	);

	const clearance = mock<ClearanceStore>();
	clearance.load.mockResolvedValue(makeClearanceLoad({ [BOUND_SOURCE]: { mode: "raw" } }));

	const existing = new Set(options.existing ?? [CONFIGURATION_PATH, PAYLOAD_PATH]);
	const layout = mock<FilesystemLayout>();
	layout.join.mockImplementation((root, relative) => `${root}/${relative}`);
	layout.exists.mockImplementation(async (path) => existing.has(path));
	layout.isFile.mockImplementation(async (path) => existing.has(path) || path.startsWith(SOURCE_ROOT));

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

describe("source retirement", () => {
	beforeEach(() => {
		vi.clearAllMocks();
	});

	test("a fully Core-owned source that no longer exists retires its destination and its binding", async () => {
		const source = ".agents/skills/x/a.ts";
		const bindings = mock<BindingsStore>();
		bindings.load.mockResolvedValue(
			makeBindingsDocument({ bindings: [{ source, destinations: [source], declaredMode: "raw" }] }),
		);
		const clearance = mock<ClearanceStore>();
		clearance.load.mockResolvedValue(makeClearanceLoad({ ".agents/skills/x/": { mode: "raw" } }));
		const layout = mock<FilesystemLayout>();
		layout.join.mockImplementation((root, relative) => `${root}/${relative}`);
		layout.exists.mockResolvedValue(true);
		// The destination still exists; the source tree no longer holds the source.
		layout.isFile.mockImplementation(async (path) => path.startsWith(`${SYNCHRONIZATION_DESTINATION_ROOT}/`));
		const destinations = mock<DestinationFiles>();
		destinations.readText.mockResolvedValue(null);
		const guard = mock<WriteTargetGuard>();
		guard.refuse.mockResolvedValue(null);
		const useCase = new ApplyCoreRevision({
			bindings,
			clearance,
			sources: mock<SourceFiles>(),
			destinations,
			layout,
			guard,
		});

		const outcome = await useCase.execute(makeSynchronizationRequest({ editor: "opencode" }));

		expect(outcome.ok).toBe(true);
		expect(outcome.ok && outcome.message).toContain(`retired: ${source}`);
		expect(destinations.remove).toHaveBeenCalledWith(`${SYNCHRONIZATION_DESTINATION_ROOT}/${source}`);
		expect(bindings.save.mock.calls[0]?.[1].bindings).toEqual([]);
	});

	test("a cleared source the tree no longer holds is retired instead of failing the run", async () => {
		// The registry still declares the file, so clearance alone would call it
		// distributable; distributability requires physical presence too, so the
		// ownership rule retires it and unrelated safe updates still complete.
		const source = ".agents/skills/x/a.ts";
		const bindings = mock<BindingsStore>();
		bindings.load.mockResolvedValue(
			makeBindingsDocument({ bindings: [{ source, destinations: [source], declaredMode: "raw" }] }),
		);
		const clearance = mock<ClearanceStore>();
		clearance.load.mockResolvedValue(makeClearanceLoad({ [source]: { mode: "raw" } }));
		const layout = mock<FilesystemLayout>();
		layout.join.mockImplementation((root, relative) => `${root}/${relative}`);
		layout.exists.mockResolvedValue(true);
		// The destination still exists; the source tree no longer holds the source.
		layout.isFile.mockImplementation(async (path) => path.startsWith(`${SYNCHRONIZATION_DESTINATION_ROOT}/`));
		const destinations = mock<DestinationFiles>();
		destinations.readText.mockResolvedValue(null);
		const guard = mock<WriteTargetGuard>();
		guard.refuse.mockResolvedValue(null);
		const useCase = new ApplyCoreRevision({
			bindings,
			clearance,
			sources: mock<SourceFiles>(),
			destinations,
			layout,
			guard,
		});

		const outcome = await useCase.execute(makeSynchronizationRequest({ editor: "opencode" }));

		expect(outcome.ok).toBe(true);
		expect(destinations.remove).toHaveBeenCalledWith(`${SYNCHRONIZATION_DESTINATION_ROOT}/${source}`);
		expect(writtenTo(destinations, `${SYNCHRONIZATION_DESTINATION_ROOT}/${source}`)).toEqual([]);
		expect(bindings.save.mock.calls[0]?.[1].bindings).toEqual([]);
	});

	test("a fully Core-owned source withdrawn from distribution is retired", async () => {
		const source = ".agents/skills/x/a.ts";
		const bindings = mock<BindingsStore>();
		bindings.load.mockResolvedValue(
			makeBindingsDocument({ bindings: [{ source, destinations: [source], declaredMode: "raw" }] }),
		);
		const clearance = mock<ClearanceStore>();
		clearance.load.mockResolvedValue(
			makeClearanceLoad({
				[source]: {
					mode: "raw",
					editors: { opencode: { omitted: true }, cursor: { destination: source } },
				},
			}),
		);
		const layout = mock<FilesystemLayout>();
		layout.join.mockImplementation((root, relative) => `${root}/${relative}`);
		// The source is still there; only its delivery was withdrawn.
		layout.isFile.mockResolvedValue(true);
		layout.exists.mockResolvedValue(true);
		const destinations = mock<DestinationFiles>();
		destinations.readText.mockResolvedValue(null);
		const guard = mock<WriteTargetGuard>();
		guard.refuse.mockResolvedValue(null);
		const useCase = new ApplyCoreRevision({
			bindings,
			clearance,
			sources: mock<SourceFiles>(),
			destinations,
			layout,
			guard,
		});

		const outcome = await useCase.execute(makeSynchronizationRequest({ editor: "opencode" }));

		expect(outcome.ok).toBe(true);
		expect(destinations.remove).toHaveBeenCalledWith(`${SYNCHRONIZATION_DESTINATION_ROOT}/${source}`);
		expect(bindings.save.mock.calls[0]?.[1].bindings).toEqual([]);
	});
});

describe("source preservation", () => {
	beforeEach(() => {
		vi.clearAllMocks();
	});

	test("a source whose ownership the registry no longer declares is preserved, never deleted", async () => {
		const source = ".agents/skills/x/a.ts";
		const bindings = mock<BindingsStore>();
		bindings.load.mockResolvedValue(
			makeBindingsDocument({ bindings: [{ source, destinations: [source], declaredMode: "raw" }] }),
		);
		const clearance = mock<ClearanceStore>();
		// No record covers the bound path at all.
		clearance.load.mockResolvedValue(makeClearanceLoad({ ".env": { mode: "raw" } }));
		const layout = mock<FilesystemLayout>();
		layout.join.mockImplementation((root, relative) => `${root}/${relative}`);
		layout.exists.mockResolvedValue(true);
		layout.isFile.mockImplementation(async (path) => path.startsWith(`${SYNCHRONIZATION_DESTINATION_ROOT}/`));
		const destinations = mock<DestinationFiles>();
		destinations.readText.mockResolvedValue(null);
		const guard = mock<WriteTargetGuard>();
		guard.refuse.mockResolvedValue(null);
		const useCase = new ApplyCoreRevision({
			bindings,
			clearance,
			sources: mock<SourceFiles>(),
			destinations,
			layout,
			guard,
		});

		const outcome = await useCase.execute(makeSynchronizationRequest({ editor: "opencode" }));

		expect(outcome.ok).toBe(true);
		expect(destinations.remove).not.toHaveBeenCalledWith(`${SYNCHRONIZATION_DESTINATION_ROOT}/${source}`);
		// The preserved destination is neither rewritten nor replaced.
		expect(writtenTo(destinations, `${SYNCHRONIZATION_DESTINATION_ROOT}/${source}`)).toEqual([]);
		expect(destinations.writeText.mock.calls.filter(([target]) => target.endsWith(`/${source}`))).toEqual([]);
		const saved = bindings.save.mock.calls[0]?.[1];
		expect(saved?.bindings.map((entry) => entry.source)).toContain(source);
		expect(saved?.pending).toContain(source);
		expect(layout.syncBlocker.mock.calls[0]?.[3]).toEqual([
			{ source, destination: source, reason: "unestablished" },
		]);
	});

	test("a source that still exists but did not join the expansion is preserved, never deleted", async () => {
		const source = ".agents/skills/x/a.ts";
		const bindings = mock<BindingsStore>();
		bindings.load.mockResolvedValue(
			makeBindingsDocument({ bindings: [{ source, destinations: [source], declaredMode: "raw" }] }),
		);
		const clearance = mock<ClearanceStore>();
		clearance.load.mockResolvedValue(makeClearanceLoad({ ".agents/skills/x/": { mode: "raw" } }));
		const layout = mock<FilesystemLayout>();
		layout.join.mockImplementation((root, relative) => `${root}/${relative}`);
		layout.exists.mockResolvedValue(true);
		// The source is present and its path is still covered, but enumeration missed it.
		layout.isFile.mockResolvedValue(true);
		layout.enumerateFilesUnder.mockResolvedValue([]);
		const destinations = mock<DestinationFiles>();
		destinations.readText.mockResolvedValue(null);
		const guard = mock<WriteTargetGuard>();
		guard.refuse.mockResolvedValue(null);
		const useCase = new ApplyCoreRevision({
			bindings,
			clearance,
			sources: mock<SourceFiles>(),
			destinations,
			layout,
			guard,
		});

		const outcome = await useCase.execute(makeSynchronizationRequest({ editor: "opencode" }));

		expect(outcome.ok).toBe(true);
		expect(destinations.remove).not.toHaveBeenCalledWith(`${SYNCHRONIZATION_DESTINATION_ROOT}/${source}`);
		// The preserved destination is neither rewritten nor replaced.
		expect(writtenTo(destinations, `${SYNCHRONIZATION_DESTINATION_ROOT}/${source}`)).toEqual([]);
		expect(destinations.writeText.mock.calls.filter(([target]) => target.endsWith(`/${source}`))).toEqual([]);
		expect(bindings.save.mock.calls[0]?.[1].pending).toContain(source);
		expect(layout.syncBlocker.mock.calls[0]?.[3]).toEqual([{ source, destination: source, reason: "anomaly" }]);
	});
});

describe("merge-managed source preservation", () => {
	beforeEach(() => {
		vi.clearAllMocks();
	});

	test("a merge-managed source that no longer exists is preserved, never deleted or rewritten", async () => {
		// A merge destination holds destination-owned keys alongside the Core-owned
		// ones, so the file is never exclusively Core-owned and its removal would
		// destroy destination content.
		const source = ".opencode/opencode.jsonc";
		const bindings = mock<BindingsStore>();
		bindings.load.mockResolvedValue(
			makeBindingsDocument({ bindings: [{ source, destinations: [source], declaredMode: "merge" }] }),
		);
		const clearance = mock<ClearanceStore>();
		clearance.load.mockResolvedValue(makeClearanceLoad({ ".opencode/": { mode: "merge" } }));
		const layout = mock<FilesystemLayout>();
		layout.join.mockImplementation((root, relative) => `${root}/${relative}`);
		layout.exists.mockResolvedValue(true);
		// The destination still exists; the source tree no longer holds the source.
		layout.isFile.mockImplementation(async (path) => path.startsWith(`${SYNCHRONIZATION_DESTINATION_ROOT}/`));
		const destinations = mock<DestinationFiles>();
		destinations.readText.mockResolvedValue(null);
		const guard = mock<WriteTargetGuard>();
		guard.refuse.mockResolvedValue(null);
		const useCase = new ApplyCoreRevision({
			bindings,
			clearance,
			sources: mock<SourceFiles>(),
			destinations,
			layout,
			guard,
		});

		const outcome = await useCase.execute(makeSynchronizationRequest({ editor: "opencode" }));

		expect(outcome.ok).toBe(true);
		// Neither the file nor its content is touched: it is neither removed nor
		// replaced with an empty or default object.
		expect(destinations.remove).not.toHaveBeenCalledWith(`${SYNCHRONIZATION_DESTINATION_ROOT}/${source}`);
		expect(writtenTo(destinations, `${SYNCHRONIZATION_DESTINATION_ROOT}/${source}`)).toEqual([]);
		// A merge destination is delivered through the text channel, so the absence
		// of a write there is what proves it was not rewritten.
		expect(destinations.writeText.mock.calls.filter(([target]) => target.endsWith(`/${source}`))).toEqual([]);
		// The binding survives and the destination is recorded as requiring
		// reconciliation through the existing lifecycle contract.
		const saved = bindings.save.mock.calls[0]?.[1];
		expect(saved?.bindings.map((entry) => entry.source)).toContain(source);
		expect(saved?.pending).toContain(source);
		expect(layout.syncBlocker.mock.calls[0]?.[3]).toEqual([{ source, destination: source, reason: "missing" }]);
	});
});

describe("destination ownership", () => {
	beforeEach(() => {
		vi.clearAllMocks();
	});

	test("a retired raw source and a distributable region source share a destination without deleting it", async () => {
		const retired = ".agents/skills/old/SKILL.md";
		const live = ".agents/skills/new/SKILL.md";
		const destination = ".opencode/skills/shared/SKILL.md";
		const destinationPath = `${SYNCHRONIZATION_DESTINATION_ROOT}/${destination}`;
		const bindings = mock<BindingsStore>();
		bindings.load.mockResolvedValue(
			makeBindingsDocument({
				bindings: [
					{ source: retired, destinations: [destination], declaredMode: "raw" },
					{ source: live, destinations: [destination], declaredMode: "region" },
				],
			}),
		);
		const clearance = mock<ClearanceStore>();
		clearance.load.mockResolvedValue(makeClearanceLoad({ [retired]: { mode: "raw" }, [live]: { mode: "region" } }));
		const layout = mock<FilesystemLayout>();
		layout.join.mockImplementation((root, relative) => `${root}/${relative}`);
		layout.exists.mockResolvedValue(true);
		// The retired source is gone; the live source and the destination exist.
		layout.isFile.mockImplementation(
			async (path) =>
				path === `${SOURCE_ROOT}/${live}` || path.startsWith(`${SYNCHRONIZATION_DESTINATION_ROOT}/`),
		);
		const sources = mock<SourceFiles>();
		sources.readCore.mockResolvedValue({ kind: "core", core: "new core\n" });
		sources.readText.mockResolvedValue("");
		const destinations = mock<DestinationFiles>();
		destinations.readText.mockResolvedValue(
			"<!-- core:begin -->\nstale core\n<!-- core:end -->\n\n<!-- project:begin -->\nowned\n<!-- project:end -->\n",
		);
		const guard = mock<WriteTargetGuard>();
		guard.refuse.mockResolvedValue(null);
		const useCase = new ApplyCoreRevision({ bindings, clearance, sources, destinations, layout, guard });

		const outcome = await useCase.execute(makeSynchronizationRequest({ editor: "opencode" }));

		expect(outcome.ok).toBe(true);
		// The destination is still in use, so it is never removed.
		expect(destinations.remove).not.toHaveBeenCalledWith(destinationPath);
		// The live source's mode contract applies to the file that stayed.
		expect(destinations.writeText.mock.calls.filter(([target]) => target === destinationPath)).toHaveLength(1);
		const written = destinations.writeText.mock.calls.find(([target]) => target === destinationPath)?.[1] ?? "";
		expect(written).toContain("new core");
		expect(written).toContain("owned");
		// The obsolete binding is gone and the document carries only the live one.
		expect(bindings.save.mock.calls[0]?.[1].bindings.map((entry) => entry.source)).toEqual([live]);
	});

	test("a retired raw source and a distributable merge source share a destination and keep its own keys", async () => {
		const retired = ".agents/skills/old/config.jsonc";
		const live = ".opencode/opencode.jsonc";
		const destinationPath = `${SYNCHRONIZATION_DESTINATION_ROOT}/${live}`;
		const bindings = mock<BindingsStore>();
		bindings.load.mockResolvedValue(
			makeBindingsDocument({
				bindings: [
					{ source: retired, destinations: [live], declaredMode: "raw" },
					{ source: live, destinations: [live], declaredMode: "merge" },
				],
			}),
		);
		const clearance = mock<ClearanceStore>();
		clearance.load.mockResolvedValue(makeClearanceLoad({ [retired]: { mode: "raw" }, [live]: { mode: "merge" } }));
		const layout = mock<FilesystemLayout>();
		layout.join.mockImplementation((root, relative) => `${root}/${relative}`);
		layout.exists.mockResolvedValue(true);
		// The retired source is gone; the live source and the destination exist.
		layout.isFile.mockImplementation(
			async (path) =>
				path === `${SOURCE_ROOT}/${live}` || path.startsWith(`${SYNCHRONIZATION_DESTINATION_ROOT}/`),
		);
		const sources = mock<SourceFiles>();
		sources.readText.mockImplementation(async (path) =>
			path === `${SOURCE_ROOT}/${live}` ? MERGE_SOURCE_TEXT : "",
		);
		const destinations = mock<DestinationFiles>();
		destinations.readText.mockImplementation(async (path) =>
			path === destinationPath ? MERGE_DESTINATION_TEXT : null,
		);
		const guard = mock<WriteTargetGuard>();
		guard.refuse.mockResolvedValue(null);
		const useCase = new ApplyCoreRevision({ bindings, clearance, sources, destinations, layout, guard });

		const outcome = await useCase.execute(makeSynchronizationRequest({ editor: "opencode" }));

		expect(outcome.ok).toBe(true);
		// The merge cannot create its destination, so the file has to survive.
		expect(destinations.remove).not.toHaveBeenCalledWith(destinationPath);
		const written = textWrittenTo(destinations, destinationPath);
		// Destination-owned configuration survives; the shipped index is retargeted.
		expect(written).toMatch(/"local-only"/u);
		expect(written).toMatch(/"ownKey": true/u);
		expect(written).toMatch(/"--index",\s*"destination"/u);
		// The obsolete binding is gone; only the valid binding remains.
		expect(bindings.save.mock.calls[0]?.[1].bindings.map((entry) => entry.source)).toEqual([live]);
	});

	test("two live bindings claiming one destination are refused before anything is mutated", async () => {
		const first = ".agents/skills/a/SKILL.md";
		const second = ".agents/skills/b/SKILL.md";
		const destination = ".opencode/skills/shared/SKILL.md";
		const bindings = mock<BindingsStore>();
		bindings.load.mockResolvedValue(
			makeBindingsDocument({
				bindings: [
					{ source: first, destinations: [destination], declaredMode: "raw" },
					{ source: second, destinations: [destination], declaredMode: "raw" },
				],
			}),
		);
		const clearance = mock<ClearanceStore>();
		clearance.load.mockResolvedValue(makeClearanceLoad({ [first]: { mode: "raw" }, [second]: { mode: "raw" } }));
		const layout = mock<FilesystemLayout>();
		layout.join.mockImplementation((root, relative) => `${root}/${relative}`);
		layout.exists.mockResolvedValue(true);
		layout.isFile.mockImplementation(async (path) => path.startsWith(SOURCE_ROOT));
		const sources = mock<SourceFiles>();
		sources.readBytes.mockResolvedValue(new TextEncoder().encode("payload\n"));
		const destinations = mock<DestinationFiles>();
		const guard = mock<WriteTargetGuard>();
		guard.refuse.mockResolvedValue(null);
		const useCase = new ApplyCoreRevision({ bindings, clearance, sources, destinations, layout, guard });

		const outcome = await useCase.execute(makeSynchronizationRequest({ editor: "opencode" }));

		expect(outcome.ok).toBe(false);
		const failure = outcome.ok ? null : outcome.failure;
		expect(failure?.code).toBe("invalid");
		expect(failure?.message).toContain("conflicting destination ownership");
		expect(destinations.writeText).not.toHaveBeenCalled();
		expect(destinations.writeBytes).not.toHaveBeenCalled();
		expect(destinations.remove).not.toHaveBeenCalled();
		expect(bindings.save).not.toHaveBeenCalled();
	});
});

describe("newly cleared sources", () => {
	beforeEach(() => {
		vi.clearAllMocks();
	});

	test("a newly cleared source is enrolled and written by an ordinary update", async () => {
		const source = ".agents/skills/x/new.ts";
		const bindings = mock<BindingsStore>();
		bindings.load.mockResolvedValue(makeBindingsDocument({ bindings: [] }));
		const clearance = mock<ClearanceStore>();
		clearance.load.mockResolvedValue(makeClearanceLoad({ ".agents/skills/x/": { mode: "raw" } }));
		const layout = mock<FilesystemLayout>();
		layout.join.mockImplementation((root, relative) => `${root}/${relative}`);
		layout.enumerateFilesUnder.mockResolvedValue(["new.ts"]);
		layout.exists.mockResolvedValue(false);
		// The enumeration reported the source, so the source tree holds it; the
		// destination is what does not exist yet.
		layout.isFile.mockImplementation(async (path) => path.startsWith(SOURCE_ROOT));
		const sources = mock<SourceFiles>();
		sources.readBytes.mockResolvedValue(PAYLOAD);
		const destinations = mock<DestinationFiles>();
		const guard = mock<WriteTargetGuard>();
		guard.refuse.mockResolvedValue(null);
		const useCase = new ApplyCoreRevision({ bindings, clearance, sources, destinations, layout, guard });

		const outcome = await useCase.execute(makeSynchronizationRequest({ editor: "opencode" }));

		expect(outcome.ok).toBe(true);
		expect(writtenTo(destinations, `${SYNCHRONIZATION_DESTINATION_ROOT}/${source}`)).toEqual([PAYLOAD]);
		expect(bindings.save.mock.calls[0]?.[1].bindings.map((entry) => entry.source)).toEqual([source]);
	});
});

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

describe("raw mode", () => {
	beforeEach(() => {
		vi.clearAllMocks();
	});

	test("a declared but absent raw target is created, written verbatim and named as created", async () => {
		const { useCase, destinations } = makeWritableUpdate({ existing: [CONFIGURATION_PATH] });

		const outcome = await useCase.execute(makeSynchronizationRequest({ editor: "opencode" }));

		expect(outcome.ok).toBe(true);
		expect(outcome.ok && outcome.message).toContain(`created: ${BOUND_SOURCE}`);
		// A raw destination is the source's bytes exactly: it carries no region.
		expect(writtenTo(destinations, PAYLOAD_PATH)).toEqual([PAYLOAD]);
	});

	test("a pending path whose source is raw-bound leaves pending instead of being reconciled", async () => {
		const { useCase, bindings } = makeWritableUpdate({
			existing: [CONFIGURATION_PATH, PAYLOAD_PATH],
			pending: [BOUND_SOURCE],
		});

		const outcome = await useCase.execute(makeSynchronizationRequest({ editor: "opencode" }));

		expect(outcome.ok).toBe(true);
		// A non-region destination has no region to reconcile, so `apply` clears it.
		expect(bindings.save.mock.calls[0]?.[1].pending).toEqual([]);
	});
});

/** The region-mode source's core bytes, as its reader reports them. */
const REGION_CORE = "core body\n";

/** The merge-mode source: the harness configuration. */
const MERGE_SOURCE = ".opencode/opencode.jsonc";

/** A source configuration whose only MCP server is the shipped qmd entry. */
const MERGE_SOURCE_TEXT = `{
  "mcp": {
    "servers": {
      "qmd": { "type": "local", "command": ["npx", "-y", "@tobilu/qmd@2.8.3", "--index", "ai-core", "mcp"] }
    }
  }
}`;

/** A destination configuration holding its own server and another qmd index. */
const MERGE_DESTINATION_TEXT = `{
  "mcp": {
    "servers": {
      "qmd": { "type": "local", "command": ["npx", "-y", "@tobilu/qmd@2.8.3", "--index", "old-index", "mcp"] },
      "local-only": { "type": "local", "command": ["node", "local/server.js"] }
    }
  },
  "ownKey": true
}`;

type BindingUpdateOptions = {
	readonly mode: "region" | "merge";
	/** Absolute paths the destination already holds. */
	readonly existing?: readonly string[];
	/** The source document's text, as its reader reports it. */
	readonly sourceText?: string | null;
	/** The destination document's text, as its reader reports it. */
	readonly destinationText?: string | null;
};

/**
 * The update use case arranged over one bound source in the given mode.
 *
 * The source mirrors to itself, every other port is doubled, and only the files
 * a case names are on disk, so the case states just what it varies.
 */
function makeBindingUpdate(options: BindingUpdateOptions) {
	const source = options.mode === "merge" ? MERGE_SOURCE : BOUND_SOURCE;
	const destinationPath = `${SYNCHRONIZATION_DESTINATION_ROOT}/${source}`;

	const bindings = mock<BindingsStore>();
	bindings.load.mockResolvedValue(
		makeBindingsDocument({
			editor: "opencode",
			bindings: [{ source, destinations: [source], declaredMode: options.mode }],
		}),
	);

	const clearance = mock<ClearanceStore>();
	clearance.load.mockResolvedValue(makeClearanceLoad({ [source]: { mode: options.mode } }));

	const existing = new Set(options.existing ?? []);
	const layout = mock<FilesystemLayout>();
	layout.join.mockImplementation((root, relative) => `${root}/${relative}`);
	layout.exists.mockImplementation(async (path) => existing.has(path));
	layout.isFile.mockImplementation(async (path) => existing.has(path) || path.startsWith(SOURCE_ROOT));
	layout.parent.mockImplementation((path) => path.slice(0, path.lastIndexOf("/")));

	const guard = mock<WriteTargetGuard>();
	guard.refuse.mockResolvedValue(null);

	const sources = mock<SourceFiles>();
	sources.readCore.mockResolvedValue({ kind: "core", core: REGION_CORE });
	sources.readText.mockResolvedValue(options.sourceText ?? null);

	const destinations = mock<DestinationFiles>();
	destinations.readText.mockResolvedValue(options.destinationText ?? null);

	const useCase = new ApplyCoreRevision({ bindings, clearance, sources, destinations, layout, guard });
	return { useCase, bindings, destinations, layout, destinationPath };
}

/** One text write's content, as it was handed to the destination port. */
function textWrittenTo(destinations: MockProxy<DestinationFiles>, path: string): string {
	const call = destinations.writeText.mock.calls.find(([target]) => target === path);
	return call?.[1] ?? "";
}

describe("region mode", () => {
	beforeEach(() => {
		vi.clearAllMocks();
	});

	test("a declared but absent region target is created from the source and named as created", async () => {
		const { useCase, destinations, destinationPath } = makeBindingUpdate({
			mode: "region",
			existing: [],
		});

		const outcome = await useCase.execute(makeSynchronizationRequest({ editor: "opencode" }));

		expect(outcome.ok).toBe(true);
		expect(outcome.ok && outcome.message).toContain(`created: ${BOUND_SOURCE}`);
		// A created destination is a core region from the source and an empty
		// project region, never a copy of the source's own file.
		const written = textWrittenTo(destinations, destinationPath);
		expect(written).toContain("<!-- core:begin -->");
		expect(written).toContain(REGION_CORE.trim());
		expect(written).toContain("<!-- project:begin -->");
		expect(written).toContain("<!-- project:end -->");
	});
});

describe("merge mode", () => {
	beforeEach(() => {
		vi.clearAllMocks();
	});

	test("a merge destination that is absent is drift, and nothing is created or written", async () => {
		const { useCase, destinations, layout } = makeBindingUpdate({
			mode: "merge",
			existing: [],
			sourceText: MERGE_SOURCE_TEXT,
		});

		const outcome = await useCase.execute(makeSynchronizationRequest({ editor: "opencode" }));

		expect(outcome.ok).toBe(false);
		const failure = outcome.ok ? null : outcome.failure;
		expect(failure?.code).toBe("drift");
		expect(failure?.message).toContain("(merge mode cannot create it; the destination must exist)");
		// Only a first enrollment may create a merge target.
		expect(destinations.writeText).not.toHaveBeenCalled();
		expect(layout.ensureDirectory).not.toHaveBeenCalled();
	});

	test("a merge keeps a destination-only server and retargets qmd to the destination folder name", async () => {
		const { useCase, destinations, destinationPath } = makeBindingUpdate({
			mode: "merge",
			existing: [`${SYNCHRONIZATION_DESTINATION_ROOT}/.opencode/opencode.jsonc`],
			sourceText: MERGE_SOURCE_TEXT,
			destinationText: MERGE_DESTINATION_TEXT,
		});

		const outcome = await useCase.execute(makeSynchronizationRequest({ editor: "opencode" }));

		expect(outcome.ok).toBe(true);
		const written = textWrittenTo(destinations, destinationPath);
		// The destination's own server and key survive the merge.
		expect(written).toMatch(/"local-only"/u);
		expect(written).toMatch(/"ownKey": true/u);
		// The shipped index is retargeted to this destination's own folder name.
		expect(written).toMatch(/"--index",\s*"destination"/u);
		expect(written).not.toMatch(/"ai-core"/u);
	});
});
