/**
 * Unit: what one update plans to write.
 *
 * One behavioral concern per group: a raw write is queued even when its bytes
 * match, a merge destination is never created, malformed destination markers are
 * refused, and the ordered payload is built from the writes exactly once. The
 * ports are doubled (contract T2, T3, T15).
 */

import { beforeEach, describe, expect, test, vi } from "vitest";
import { mock, type MockProxy } from "vitest-mock-extended";

import type { ClearanceModes } from "#application/synchronization/clearance-modes.ts";
import { PlanUpdateChanges, type UpdateChangeRequest } from "#application/synchronization/plan-update-changes.ts";
import type { BindingMode } from "#domain/synchronization/constants.ts";
import { parseClearanceDocument, type ClearanceEntry } from "#domain/synchronization/clearance.ts";
import type { BindingsDocument } from "#domain/synchronization/bindings.ts";
import type { DestinationFiles, FilesystemLayout, SourceFiles } from "#domain/synchronization/ports.ts";
import {
	BOUND_SOURCE,
	SYNCHRONIZATION_DESTINATION_ROOT,
	makeBindingsDocument,
	makeClearanceText,
	makeSynchronizationRequest,
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
			makeRequest(makeBindingsDocument(), makeClearance({ [BOUND_SOURCE]: { mode: "raw" } })),
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
			makeRequest(makeBindingsDocument(), makeClearance({ [BOUND_SOURCE]: { mode: "raw" } })),
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
			makeRequest(makeBindingsDocument(), makeClearance({ [BOUND_SOURCE]: { mode: "merge" } })),
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
			makeRequest(makeBindingsDocument(), makeClearance({ [BOUND_SOURCE]: { mode: "region" } })),
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

	test("a retired destination is a payload deletion after the writes", async () => {
		const source = ".agents/skills/old/SKILL.md";
		const { planner } = makePlanner();
		const document = makeBindingsDocument({ bindings: [] });

		const outcome = await planner.execute({
			document,
			request: makeSynchronizationRequest(),
			clearance: makeClearance({}),
			distributable: [],
			retired: [{ source, destinations: [source], reason: "missing" }],
		});

		expect(outcome.ok).toBe(true);
		expect(outcome.ok && outcome.plan.payload).toEqual([
			{ kind: "file-delete", path: `${SYNCHRONIZATION_DESTINATION_ROOT}/${source}` },
		]);
		expect(outcome.ok && outcome.plan.deletions).toEqual([`${SYNCHRONIZATION_DESTINATION_ROOT}/${source}`]);
	});
});
