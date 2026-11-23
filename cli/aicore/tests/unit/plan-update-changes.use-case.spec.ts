/**
 * Unit: what one update plans to write.
 *
 * One behavioral concern per group: a raw write is queued even when its bytes
 * match, a merge destination is never created, malformed destination markers are
 * refused, and the ordered payload is built from the writes exactly once. The
 * ports are doubled and the clearance expansion comes from the shared factory
 * through the real reader (contract T2, T3, T15).
 */

import { beforeEach, describe, expect, test, vi } from "vitest";
import { mock, type MockProxy } from "vitest-mock-extended";

import { readClearanceModes, type ClearanceModes } from "#application/synchronization/clearance-modes.ts";
import { PlanUpdateChanges, type UpdateChangeRequest } from "#application/synchronization/plan-update-changes.ts";
import type { BindingsDocument } from "#domain/synchronization/bindings.ts";
import type { ClearanceStore, DestinationFiles, FilesystemLayout, SourceFiles } from "#domain/synchronization/ports.ts";
import {
	BOUND_SOURCE,
	SOURCE_ROOT,
	SYNCHRONIZATION_DESTINATION_ROOT,
	makeBindingsDocument,
	makeClearanceLoad,
	makeSynchronizationRequest,
} from "#support/synchronization.factory.ts";

/** The expanded clearance one run acts on, read from the factory's registry. */
async function makeClearance(
	cleared: Readonly<Record<string, Readonly<Record<string, unknown>>>>,
	layout: MockProxy<FilesystemLayout>,
): Promise<ClearanceModes> {
	const clearance = mock<ClearanceStore>();
	clearance.load.mockResolvedValue(makeClearanceLoad(cleared));
	return readClearanceModes(clearance, layout, SOURCE_ROOT, "opencode");
}

/** An update-plan request over one document and clearance. */
function makeRequest(document: BindingsDocument, clearance: ClearanceModes): UpdateChangeRequest {
	return {
		document,
		request: makeSynchronizationRequest(),
		clearance,
		distributable: document.bindings,
		retired: [],
	};
}

type PlannerPorts = {
	readonly sources: MockProxy<SourceFiles>;
	readonly destinations: MockProxy<DestinationFiles>;
	readonly layout: MockProxy<FilesystemLayout>;
};

/** The planner over doubled ports. */
function makePlanner(options: Partial<PlannerPorts> = {}): PlannerPorts & { readonly planner: PlanUpdateChanges } {
	const ports: PlannerPorts = {
		sources: options.sources ?? mock<SourceFiles>(),
		destinations: options.destinations ?? mock<DestinationFiles>(),
		layout: options.layout ?? mock<FilesystemLayout>(),
	};
	ports.layout.join.mockImplementation((root, relative) => `${root}/${relative}`);
	ports.layout.parent.mockImplementation((path) => path.slice(0, path.lastIndexOf("/")));
	return { ...ports, planner: new PlanUpdateChanges(ports) };
}

describe("raw mode", () => {
	beforeEach(() => {
		vi.clearAllMocks();
	});

	test("a raw write is queued even when the destination already holds the source's bytes", async () => {
		const { planner, sources, layout } = makePlanner();
		const payload = new TextEncoder().encode("payload\n");
		sources.readBytes.mockResolvedValue(payload);
		layout.isFile.mockResolvedValue(true);
		layout.exists.mockResolvedValue(true);

		const outcome = await planner.execute(
			makeRequest(makeBindingsDocument(), await makeClearance({ [BOUND_SOURCE]: { mode: "raw" } }, layout)),
		);

		expect(outcome.ok).toBe(true);
		const plan = outcome.ok ? outcome.plan : null;
		expect(plan?.byteWrites.map((write) => write.content)).toEqual([payload]);
		expect(plan?.created).toEqual([]);
		// The payload is the writes and the retired deletions, in application order.
		expect(plan?.payload).toEqual([
			{ kind: "byte-write", path: `${SYNCHRONIZATION_DESTINATION_ROOT}/${BOUND_SOURCE}`, content: payload },
		]);
		// A raw destination is non-region, so its outstanding path is not reconciled.
		expect(plan?.pending).toEqual([]);
	});

	test("a declared but absent raw target is named as created", async () => {
		const { planner, sources, layout } = makePlanner();
		sources.readBytes.mockResolvedValue(new TextEncoder().encode("payload\n"));
		layout.isFile.mockResolvedValue(false);
		layout.exists.mockResolvedValue(false);

		const outcome = await planner.execute(
			makeRequest(makeBindingsDocument(), await makeClearance({ [BOUND_SOURCE]: { mode: "raw" } }, layout)),
		);

		expect(outcome.ok).toBe(true);
		expect(outcome.ok && outcome.plan.created).toEqual([BOUND_SOURCE]);
	});
});

describe("merge mode", () => {
	beforeEach(() => {
		vi.clearAllMocks();
	});

	test("a merge destination that is absent is drift and nothing is created", async () => {
		const { planner, sources, layout } = makePlanner();
		sources.readText.mockResolvedValue("{}");
		layout.isFile.mockResolvedValue(false);
		layout.exists.mockResolvedValue(false);

		const outcome = await planner.execute(
			makeRequest(makeBindingsDocument(), await makeClearance({ [BOUND_SOURCE]: { mode: "merge" } }, layout)),
		);

		expect(outcome.ok).toBe(false);
		const failure = outcome.ok ? null : outcome.failure;
		expect(failure?.code).toBe("drift");
		expect(failure?.message).toContain("(merge mode cannot create it; the destination must exist)");
	});
});

describe("region mode", () => {
	beforeEach(() => {
		vi.clearAllMocks();
	});

	test("a destination without markers is refused as invalid markers", async () => {
		const { planner, sources, destinations, layout } = makePlanner();
		sources.readCore.mockResolvedValue({ kind: "core", core: "core body\n" });
		sources.readText.mockResolvedValue("");
		destinations.readText.mockResolvedValue("no markers here\n");
		layout.isFile.mockResolvedValue(true);

		const outcome = await planner.execute(
			makeRequest(makeBindingsDocument(), await makeClearance({ [BOUND_SOURCE]: { mode: "region" } }, layout)),
		);

		expect(outcome.ok).toBe(false);
		const failure = outcome.ok ? null : outcome.failure;
		expect(failure?.code).toBe("invalid");
		expect(failure?.message).toBe(
			`invalid destination markers: ${SYNCHRONIZATION_DESTINATION_ROOT}/${BOUND_SOURCE}`,
		);
	});
});

describe("retired paths", () => {
	beforeEach(() => {
		vi.clearAllMocks();
	});

	test("a retired destination is a payload deletion carrying its own path and destination", async () => {
		const source = ".agents/skills/old/SKILL.md";
		const { planner, layout } = makePlanner();
		const document = makeBindingsDocument({ bindings: [] });

		const outcome = await planner.execute({
			document,
			request: makeSynchronizationRequest(),
			clearance: await makeClearance({}, layout),
			distributable: [],
			retired: [{ source, destinations: [source], reason: "missing" }],
		});

		expect(outcome.ok).toBe(true);
		expect(outcome.ok && outcome.plan.payload).toEqual([
			{ kind: "file-delete", path: `${SYNCHRONIZATION_DESTINATION_ROOT}/${source}` },
		]);
		expect(outcome.ok && outcome.plan.deletions).toEqual([
			{ path: `${SYNCHRONIZATION_DESTINATION_ROOT}/${source}`, destination: source },
		]);
	});
});
