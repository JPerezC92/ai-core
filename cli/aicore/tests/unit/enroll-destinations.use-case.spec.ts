/**
 * Unit: what the enrollment operation delivers and refuses, with its ports
 * doubled.
 *
 * One behavioral concern per group: enrollment never moves a destination (the
 * registry-drift refusal), it honours the destination's declared opt-outs and
 * restores a revoked one, its merge delivery omits the servers the clearance
 * record names, and an opt-out naming the baseline is refused before anything is
 * read or written (contract T2, T3).
 *
 * The remaining groups cover what an enrollment creates and how it resolves its
 * root: a markerless destination becomes a core region plus a project region
 * holding its prior body, a raw destination records neither a reconciliation
 * entry nor an outstanding path, a malformed or conflicting `--bind` declaration
 * is refused before anything is read, and a root-role source is enrolled at the
 * explicit root path or refused by name when no instruction root is detectable.
 */

import { beforeEach, describe, expect, test, vi } from "vitest";
import { mock, type MockProxy } from "vitest-mock-extended";

import { EnrollDestinations } from "#application/synchronization/enroll-destinations.ts";
import { CORE_BEGIN, CORE_END, PROJECT_BEGIN, PROJECT_END } from "#domain/synchronization/constants.ts";
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
	makeEnrollmentRequest,
	makeRelocatedClearanceLoad,
} from "#support/synchronization.factory.ts";

/** An optional skill directory root, as a clearance expansion names its files. */
const SKILL_ROOT = ".agents/skills/op-model/";

/** One file under that root. */
const SKILL_FILE = `${SKILL_ROOT}SKILL.md`;

/** The merge-mode source: the harness configuration. */
const CONFIGURED_SOURCE = ".opencode/opencode.jsonc";

/** One agent document, a cleared source a destination may opt out of. */
const AGENT_SOURCE = ".opencode/agents/forge.md";

type EnrollArrangement = {
	readonly document?: ReturnType<typeof makeBindingsDocument>;
	readonly clearance?: MockProxy<ClearanceStore>;
	readonly existing?: readonly string[];
	readonly sourceText?: Readonly<Record<string, string>>;
	readonly destinationText?: Readonly<Record<string, string>>;
	/** Bound sources this run treats as removed from the source tree. */
	readonly absentSources?: readonly string[];
	/** Sources the source tree holds; defaults to the document's bindings. */
	readonly sourceFiles?: readonly string[];
};

/** The enrollment operation, its ports doubled and arranged for one run. */
function makeEnrollmentArrangement(options: EnrollArrangement = {}): {
	readonly useCase: EnrollDestinations;
	readonly bindings: MockProxy<BindingsStore>;
	readonly sources: MockProxy<SourceFiles>;
	readonly destinations: MockProxy<DestinationFiles>;
	readonly layout: MockProxy<FilesystemLayout>;
	readonly guard: MockProxy<WriteTargetGuard>;
} {
	const bindings = mock<BindingsStore>();
	bindings.load.mockResolvedValue(options.document ?? makeBindingsDocument());

	const clearance = options.clearance ?? (mock<ClearanceStore>() as MockProxy<ClearanceStore>);
	if (options.clearance === undefined) {
		clearance.load.mockResolvedValue(makeClearanceLoad({ [BOUND_SOURCE]: { mode: "region" } }));
	}

	const guard = mock<WriteTargetGuard>();
	guard.refuse.mockResolvedValue(null);

	const existing = new Set(options.existing ?? []);
	const document = options.document ?? makeBindingsDocument();
	const boundSources = new Set(document.bindings.map((entry) => entry.source));
	const boundDestinations = new Set(document.bindings.flatMap((entry) => entry.destinations));
	const absentSources = new Set(options.absentSources ?? []);
	const sourceFiles = new Set(options.sourceFiles ?? [...boundSources]);
	const layout = mock<FilesystemLayout>();
	layout.join.mockImplementation((root, relative) => `${root}/${relative}`);
	layout.exists.mockImplementation(async (path) => existing.has(path));
	// A destination this document binds answers from `existing`, so a bound
	// destination that is not there reads as absent whatever its relative path is.
	// Every other path answers for a source the source tree holds.
	layout.isFile.mockImplementation(async (path) => {
		const endsWith = (candidate: string) => path.endsWith(`/${candidate}`);
		if ([...boundDestinations].some(endsWith)) {
			return existing.has(path);
		}
		if (existing.has(path)) {
			return true;
		}
		return [...sourceFiles].some(endsWith) && ![...absentSources].some(endsWith);
	});
	layout.parent.mockImplementation((path) => path.slice(0, path.lastIndexOf("/")));

	const sources = mock<SourceFiles>();
	const sourceText = options.sourceText ?? {};
	sources.readText.mockImplementation(async (path) => sourceText[path] ?? null);

	const destinations = mock<DestinationFiles>();
	const destinationText = options.destinationText ?? {};
	destinations.readText.mockImplementation(async (path) => destinationText[path] ?? null);

	const useCase = new EnrollDestinations({
		bindings,
		clearance,
		sources,
		destinations,
		layout,
		guard,
	});
	return { useCase, bindings, sources, destinations, layout, guard };
}

/** The bindings document one run saved. */
function savedDocument(bindings: MockProxy<BindingsStore>) {
	const call = bindings.save.mock.calls[0];
	expect(call, "the run saved no bindings document").toBeDefined();
	return call?.[1];
}

describe("destination drift refusal", () => {
	beforeEach(() => {
		vi.clearAllMocks();
	});

	test("a source the registry relocated is refused by name and nothing is written", async () => {
		const clearance = mock<ClearanceStore>();
		clearance.load.mockResolvedValue(makeRelocatedClearanceLoad());
		const { useCase, bindings, sources, destinations, layout } = makeEnrollmentArrangement({ clearance });

		const outcome = await useCase.execute(makeEnrollmentRequest());

		expect(outcome.ok).toBe(false);
		const failure = outcome.ok ? null : outcome.failure;
		expect(failure?.code).toBe("drift");
		// The report names the source, the destination it is bound to, and the one
		// the registry now declares.
		expect(failure?.message).toContain(`destination drift: ${BOUND_SOURCE} is bound to '${BOUND_SOURCE}'`);
		expect(failure?.message).toContain(`now declares '${RELOCATED_BOUND_DESTINATION}'`);

		// Enrollment never moves a destination: no payload was read, no file was
		// created or rewritten, and no bindings or reconciliation report was saved.
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

describe("removed sources", () => {
	beforeEach(() => {
		vi.clearAllMocks();
	});

	test("a bound source the tree no longer holds is preserved and listed for reconciliation", async () => {
		const clearance = mock<ClearanceStore>();
		clearance.load.mockResolvedValue(makeClearanceLoad({ [SKILL_ROOT]: { mode: "region" } }));
		const { useCase, bindings, destinations, layout } = makeEnrollmentArrangement({
			document: makeBindingsDocument({
				bindings: [{ source: SKILL_FILE, destinations: [SKILL_FILE], declaredMode: "region" }],
			}),
			clearance,
			existing: [`${SYNCHRONIZATION_DESTINATION_ROOT}/${SKILL_FILE}`],
			absentSources: [SKILL_FILE],
		});

		const outcome = await useCase.execute(makeEnrollmentRequest());

		expect(outcome.ok).toBe(true);
		const saved = savedDocument(bindings);
		expect(saved?.bindings.map((entry) => entry.source)).toEqual([SKILL_FILE]);
		expect(saved?.pending).toEqual([SKILL_FILE]);
		expect(destinations.remove).not.toHaveBeenCalled();
		expect(destinations.writeText.mock.calls.filter(([target]) => target.endsWith(`/${SKILL_FILE}`))).toEqual([]);
		expect(destinations.writeBytes.mock.calls.filter(([target]) => target.endsWith(`/${SKILL_FILE}`))).toEqual([]);
		expect(layout.syncBlocker.mock.calls[0]?.[3]).toEqual([
			{ source: SKILL_FILE, destination: SKILL_FILE, reason: "missing" },
		]);
	});
});

describe("declared opt-outs", () => {
	beforeEach(() => {
		vi.clearAllMocks();
	});

	test("a file entry and a directory root drop their bindings and pend their destinations", async () => {
		const clearance = mock<ClearanceStore>();
		clearance.load.mockResolvedValue(
			makeClearanceLoad({ [AGENT_SOURCE]: { mode: "region" }, [SKILL_FILE]: { mode: "raw" } }),
		);
		const { useCase, bindings, sources, destinations } = makeEnrollmentArrangement({
			document: makeBindingsDocument({
				exclude: [AGENT_SOURCE, SKILL_ROOT],
				bindings: [
					{ source: AGENT_SOURCE, destinations: [AGENT_SOURCE], declaredMode: "region" },
					{ source: SKILL_FILE, destinations: [SKILL_FILE], declaredMode: "raw" },
				],
			}),
			clearance,
		});

		const outcome = await useCase.execute(makeEnrollmentRequest());

		expect(outcome.ok).toBe(true);
		const saved = savedDocument(bindings);
		expect(saved?.bindings).toEqual([]);
		// Nothing is deleted: the destination paths are the outstanding state.
		expect(saved?.pending).toEqual([AGENT_SOURCE, SKILL_FILE]);
		// The declaration survives, so a later enrollment cannot reintroduce either.
		expect(saved?.exclude).toEqual([AGENT_SOURCE, SKILL_ROOT]);
		// An opted-out source is never read or rewritten.
		expect(sources.readCore).not.toHaveBeenCalled();
		expect(sources.readBytes).not.toHaveBeenCalled();
		expect(destinations.writeText).not.toHaveBeenCalled();
		expect(destinations.writeBytes).not.toHaveBeenCalled();
	});

	test("only a directory root covers a prefix; a file entry with a similar prefix names one source", async () => {
		const payload = new TextEncoder().encode("skill bytes\n");
		const fileEntry = mock<ClearanceStore>();
		fileEntry.load.mockResolvedValue(makeClearanceLoad({ [SKILL_FILE]: { mode: "raw" } }));

		const similarPrefix = makeEnrollmentArrangement({
			document: makeBindingsDocument({
				exclude: [".agents/skills/op"],
				bindings: [{ source: SKILL_FILE, destinations: [SKILL_FILE], declaredMode: "raw" }],
			}),
			clearance: fileEntry,
		});
		similarPrefix.sources.readBytes.mockResolvedValue(payload);
		similarPrefix.destinations.readBytes.mockResolvedValue(payload);

		await similarPrefix.useCase.execute(makeEnrollmentRequest());

		// `.agents/skills/op` is a file entry, not the directory root, so the source
		// under `.agents/skills/op-model/` keeps its binding.
		expect(savedDocument(similarPrefix.bindings)?.bindings.map((entry) => entry.source)).toEqual([SKILL_FILE]);

		const directoryRoot = mock<ClearanceStore>();
		directoryRoot.load.mockResolvedValue(makeClearanceLoad({ [SKILL_FILE]: { mode: "raw" } }));
		const covered = makeEnrollmentArrangement({
			document: makeBindingsDocument({
				exclude: [SKILL_ROOT],
				bindings: [{ source: SKILL_FILE, destinations: [SKILL_FILE], declaredMode: "raw" }],
			}),
			clearance: directoryRoot,
		});

		await covered.useCase.execute(makeEnrollmentRequest());

		// The directory root covers it: no binding, and its destination is pending.
		const dropped = savedDocument(covered.bindings);
		expect(dropped?.bindings).toEqual([]);
		expect(dropped?.pending).toEqual([SKILL_FILE]);
	});

	test("a revoked opt-out re-binds a cleared source whose destination is still pending", async () => {
		const payload = new TextEncoder().encode("skill bytes\n");
		const clearance = mock<ClearanceStore>();
		clearance.load.mockResolvedValue(makeClearanceLoad({ [SKILL_FILE]: { mode: "raw" } }));
		const { useCase, bindings, sources, destinations } = makeEnrollmentArrangement({
			document: makeBindingsDocument({ exclude: [], bindings: [], pending: [SKILL_FILE] }),
			clearance,
			sourceFiles: [SKILL_FILE],
		});
		sources.readBytes.mockResolvedValue(payload);
		destinations.readBytes.mockResolvedValue(payload);

		const outcome = await useCase.execute(makeEnrollmentRequest());

		expect(outcome.ok).toBe(true);
		const saved = savedDocument(bindings);
		expect(saved?.bindings.map((entry) => entry.source)).toEqual([SKILL_FILE]);
		expect(saved?.pending).toEqual([]);
	});

	test("a reconciled opt-out stays absent, and a document with no opt-out is saved as it was read", async () => {
		const clearance = mock<ClearanceStore>();
		clearance.load.mockResolvedValue(makeClearanceLoad({ [SKILL_FILE]: { mode: "raw" } }));
		const document = makeBindingsDocument({ exclude: [], bindings: [], pending: [] });
		const { useCase, bindings, sources, destinations } = makeEnrollmentArrangement({
			document,
			clearance,
		});

		const outcome = await useCase.execute(makeEnrollmentRequest());

		expect(outcome.ok).toBe(true);
		const saved = savedDocument(bindings);
		// No pending entry means no outstanding opt-out to restore, and no opt-out
		// means nothing is projected: the saved document carries what it was read.
		expect(saved?.bindings).toEqual([]);
		expect(saved?.pending).toEqual([]);
		expect(saved?.exclude).toEqual([]);
		expect(sources.readBytes).not.toHaveBeenCalled();
		expect(destinations.readBytes).not.toHaveBeenCalled();
	});

	test("both baseline sources are refused by name and nothing is written", async () => {
		for (const source of ["AGENTS.md", ".opencode/opencode.jsonc"]) {
			vi.clearAllMocks();
			const { useCase, bindings, sources, destinations } = makeEnrollmentArrangement({
				document: makeBindingsDocument({ exclude: [source] }),
			});

			const outcome = await useCase.execute(makeEnrollmentRequest());

			expect(outcome.ok, source).toBe(false);
			const failure = outcome.ok ? null : outcome.failure;
			expect(failure?.code).toBe("invalid");
			expect(failure?.message).toContain("protected exclusion");
			expect(failure?.message).toContain(source);
			expect(bindings.save).not.toHaveBeenCalled();
			expect(sources.readBytes).not.toHaveBeenCalled();
			expect(destinations.writeBytes).not.toHaveBeenCalled();
		}
	});
});

describe("merge delivery", () => {
	beforeEach(() => {
		vi.clearAllMocks();
	});

	test("the merged configuration omits the named server and retargets qmd to this destination", async () => {
		const sourceText = `{
  "mcp": {
    "servers": {
      "system-one": { "type": "local", "command": ["node", "mcp-servers/system-one/src/mcp/stdio.ts"] },
      "qmd": { "type": "local", "command": ["npx", "-y", "@tobilu/qmd@2.8.3", "--index", "ai-core", "mcp"] }
    }
  }
}`;
		const clearance = mock<ClearanceStore>();
		clearance.load.mockResolvedValue(
			makeClearanceLoad({ [CONFIGURED_SOURCE]: { mode: "merge", omit_mcp_servers: ["system-one"] } }),
		);
		const destinationPath = `G:/projects/destination/${CONFIGURED_SOURCE}`;
		const { useCase, destinations, bindings } = makeEnrollmentArrangement({
			document: makeBindingsDocument({
				editor: "opencode",
				bindings: [{ source: CONFIGURED_SOURCE, destinations: [CONFIGURED_SOURCE], declaredMode: "merge" }],
			}),
			clearance,
			sourceText: { [`G:/projects/ai-core/${CONFIGURED_SOURCE}`]: sourceText },
			destinationText: { [destinationPath]: "{}" },
		});

		const outcome = await useCase.execute(makeEnrollmentRequest({ editor: "opencode" }));

		expect(outcome.ok).toBe(true);
		const written = destinations.writeText.mock.calls.find(([path]) => path === destinationPath)?.[1] ?? "";
		// The omitted server is never written, and qmd is retargeted to this
		// destination's own folder name.
		expect(written).not.toMatch(/system-one/u);
		expect(written).toMatch(/"--index",\s*"destination"/u);
		expect(written).toMatch(/"qmd"/u);
		expect(savedDocument(bindings)?.bindings.map((entry) => entry.source)).toEqual([CONFIGURED_SOURCE]);
	});
});

/** The cleared source one enrollment delivers in region mode. */
const REGION_SOURCE_TEXT = "---\ntitle: core title\n---\n";

/** The markerless destination body an enrollment must preserve. */
const PRIOR_BODY = "this project's prior body\n";

/** One text write's content, as it was handed to the destination port. */
function textWrittenTo(destinations: MockProxy<DestinationFiles>, path: string): string {
	const call = destinations.writeText.mock.calls.find(([target]) => target === path);
	return call?.[1] ?? "";
}

describe("region enrollment", () => {
	beforeEach(() => {
		vi.clearAllMocks();
	});

	test("a markerless destination becomes a core region plus a project region holding its prior body", async () => {
		const destinationPath = `G:/projects/destination/${BOUND_SOURCE}`;
		const arrangement = makeEnrollmentArrangement({
			document: makeBindingsDocument(),
			sourceText: { [`G:/projects/ai-core/${BOUND_SOURCE}`]: REGION_SOURCE_TEXT },
			destinationText: { [destinationPath]: PRIOR_BODY },
		});
		arrangement.sources.readCore.mockResolvedValue({ kind: "core", core: "core body\n" });

		const outcome = await arrangement.useCase.execute(makeEnrollmentRequest());

		expect(outcome.ok).toBe(true);
		const written = textWrittenTo(arrangement.destinations, destinationPath);
		expect(written).toContain(CORE_BEGIN);
		expect(written).toContain("core body");
		expect(written).toContain(PROJECT_BEGIN);
		expect(written).toContain(PRIOR_BODY);
		expect(written).toContain(PROJECT_END);
		// The destination's own content moves into the project region, after the
		// core region the source supplied.
		expect(written.indexOf(CORE_END)).toBeLessThan(written.indexOf(PROJECT_BEGIN));
		expect(written.indexOf(PRIOR_BODY)).toBeGreaterThan(written.indexOf(PROJECT_BEGIN));
	});
});

describe("raw enrollment", () => {
	beforeEach(() => {
		vi.clearAllMocks();
	});

	test("a raw destination records no report entry and no pending entry", async () => {
		const payload = new TextEncoder().encode("raw bytes\n");
		const destinationPath = `G:/projects/destination/${BOUND_SOURCE}`;
		const clearance = mock<ClearanceStore>();
		clearance.load.mockResolvedValue(makeClearanceLoad({ [BOUND_SOURCE]: { mode: "raw" } }));
		const arrangement = makeEnrollmentArrangement({
			document: makeBindingsDocument({
				bindings: [{ source: BOUND_SOURCE, destinations: [BOUND_SOURCE], declaredMode: "raw" }],
			}),
			clearance,
		});
		arrangement.sources.readBytes.mockResolvedValue(payload);
		arrangement.destinations.readBytes.mockResolvedValue(null);

		const outcome = await arrangement.useCase.execute(makeEnrollmentRequest());

		expect(outcome.ok).toBe(true);
		// The raw payload is the source's bytes exactly, so it holds no region.
		const written = arrangement.destinations.writeBytes.mock.calls.find(([path]) => path === destinationPath)?.[1];
		expect(written).toEqual(payload);
		expect(arrangement.destinations.writeText).not.toHaveBeenCalled();
		// A raw destination is not region-bound, so it earns neither an
		// `initialized` entry nor an outstanding-path entry.
		expect(arrangement.bindings.writeReport).not.toHaveBeenCalled();
		expect(savedDocument(arrangement.bindings)?.pending).toEqual([]);
	});
});

describe("init declarations", () => {
	beforeEach(() => {
		vi.clearAllMocks();
	});

	test("a malformed declaration is refused before any read or write", async () => {
		const { useCase, bindings, destinations, guard } = makeEnrollmentArrangement();

		const outcome = await useCase.execute(makeEnrollmentRequest({ regionDeclarations: ["no-equals-sign"] }));

		expect(outcome.ok).toBe(false);
		const failure = outcome.ok ? null : outcome.failure;
		expect(failure?.code).toBe("invalid");
		expect(failure?.message).toBe("invalid init binding: malformed or unsafe binding declaration: no-equals-sign");
		expect(bindings.save).not.toHaveBeenCalled();
		expect(bindings.writeReport).not.toHaveBeenCalled();
		expect(destinations.writeText).not.toHaveBeenCalled();
		expect(destinations.writeBytes).not.toHaveBeenCalled();
		expect(guard.refuse).not.toHaveBeenCalled();
	});

	test("a declaration whose destination another source already owns fails closed", async () => {
		const { useCase, bindings, destinations } = makeEnrollmentArrangement({
			document: makeBindingsDocument({
				bindings: [{ source: AGENT_SOURCE, destinations: ["shared.md"], declaredMode: "region" }],
			}),
		});

		const outcome = await useCase.execute(
			makeEnrollmentRequest({ regionDeclarations: ["other/source.md=shared.md"] }),
		);

		expect(outcome.ok).toBe(false);
		const failure = outcome.ok ? null : outcome.failure;
		expect(failure?.code).toBe("invalid");
		expect(failure?.message).toBe("invalid init binding: destination mapping conflicts for shared.md");
		expect(bindings.save).not.toHaveBeenCalled();
		expect(destinations.writeText).not.toHaveBeenCalled();
	});
});

describe("root role", () => {
	beforeEach(() => {
		vi.clearAllMocks();
	});

	/** The clearance registry naming the root runtime file as the root-role source. */
	function rootClearance(): MockProxy<ClearanceStore> {
		const clearance = mock<ClearanceStore>();
		clearance.load.mockResolvedValue(makeClearanceLoad({ [BOUND_SOURCE]: { mode: "region", role: "root" } }));
		return clearance;
	}

	test("a root-role source with no detectable instruction root is refused instead of guessed", async () => {
		const { useCase, bindings, destinations, layout } = makeEnrollmentArrangement({
			document: makeBindingsDocument({ bindings: [] }),
			clearance: rootClearance(),
		});
		// Detection reads only the supported instruction file: this destination's
		// instruction file has another name, so nothing is detected.
		layout.detectRootFile.mockResolvedValue(null);

		const outcome = await useCase.execute(makeEnrollmentRequest({ bindCleared: true }));

		expect(outcome.ok).toBe(false);
		const failure = outcome.ok ? null : outcome.failure;
		expect(failure?.code).toBe("drift");
		expect(failure?.message).toBe("destination instruction root not found; pass --root");
		// The refusal names the explicit option instead of writing a guessed file.
		expect(failure?.message).toContain("--root");
		expect(bindings.save).not.toHaveBeenCalled();
		expect(destinations.writeText).not.toHaveBeenCalled();
	});

	test("--root enrolls the root-role source at the named path", async () => {
		const rootPath = "CLAUDE.md";
		const destinationPath = `G:/projects/destination/${rootPath}`;
		const arrangement = makeEnrollmentArrangement({
			document: makeBindingsDocument({ bindings: [] }),
			clearance: rootClearance(),
		});
		arrangement.sources.readCore.mockResolvedValue({ kind: "core", core: "root core\n" });
		arrangement.layout.detectRootFile.mockResolvedValue(null);

		const outcome = await arrangement.useCase.execute(
			makeEnrollmentRequest({ bindCleared: true, rootOverride: rootPath }),
		);

		expect(outcome.ok).toBe(true);
		const saved = savedDocument(arrangement.bindings);
		expect(saved?.root).toBe(rootPath);
		expect(saved?.bindings).toEqual([{ source: BOUND_SOURCE, destinations: [rootPath], declaredMode: "region" }]);
		expect(textWrittenTo(arrangement.destinations, destinationPath)).toContain(CORE_BEGIN);
	});
});
