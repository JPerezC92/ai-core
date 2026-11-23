/**
 * Unit: what one enrollment plans to write.
 *
 * One behavioral concern per group: a raw destination is rewritten only when its
 * bytes differ, a markerless region destination is initialized and recorded for
 * reconciliation, an unchanged region destination is not refreshed, and a merge
 * destination is created only when this run newly bound it. The ports are
 * doubled and the clearance expansion comes from the shared factory through the
 * real reader (contract T2, T3, T15).
 */

import { beforeEach, describe, expect, test, vi } from "vitest";
import { mock, type MockProxy } from "vitest-mock-extended";

import { readClearanceModes, type ClearanceModes } from "#application/synchronization/clearance-modes.ts";
import {
	PlanEnrollmentChanges,
	type EnrollmentChangeRequest,
} from "#application/synchronization/plan-enrollment-changes.ts";
import { ACTION_INITIALIZED } from "#domain/synchronization/constants.ts";
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

/** An enrollment-plan request over one document and clearance. */
function makeRequest(
	document: BindingsDocument,
	clearance: ClearanceModes,
	newMergeDestinations: ReadonlySet<string> = new Set<string>(),
): EnrollmentChangeRequest {
	return {
		document,
		request: makeSynchronizationRequest(),
		clearance,
		distributable: document.bindings,
		retired: [],
		newMergeDestinations,
	};
}

type PlannerPorts = {
	readonly sources: MockProxy<SourceFiles>;
	readonly destinations: MockProxy<DestinationFiles>;
	readonly layout: MockProxy<FilesystemLayout>;
};

/** The planner over doubled ports. */
function makePlanner(options: Partial<PlannerPorts> = {}): PlannerPorts & { readonly planner: PlanEnrollmentChanges } {
	const ports: PlannerPorts = {
		sources: options.sources ?? mock<SourceFiles>(),
		destinations: options.destinations ?? mock<DestinationFiles>(),
		layout: options.layout ?? mock<FilesystemLayout>(),
	};
	ports.layout.join.mockImplementation((root, relative) => `${root}/${relative}`);
	return { ...ports, planner: new PlanEnrollmentChanges(ports) };
}

describe("raw mode", () => {
	beforeEach(() => {
		vi.clearAllMocks();
	});

	test("a raw destination that already holds the source's bytes is not written again", async () => {
		const { planner, sources, destinations, layout } = makePlanner();
		const payload = new TextEncoder().encode("payload\n");
		sources.readBytes.mockResolvedValue(payload);
		destinations.readBytes.mockResolvedValue(payload);

		const outcome = await planner.execute(
			makeRequest(makeBindingsDocument(), await makeClearance({ [BOUND_SOURCE]: { mode: "raw" } }, layout)),
		);

		expect(outcome.ok).toBe(true);
		expect(outcome.ok && outcome.plan.byteWrites).toEqual([]);
		expect(outcome.ok && outcome.plan.reportEntries).toEqual([]);
	});

	test("a raw destination whose bytes differ is rewritten without a report entry", async () => {
		const { planner, sources, destinations, layout } = makePlanner();
		sources.readBytes.mockResolvedValue(new TextEncoder().encode("payload\n"));
		destinations.readBytes.mockResolvedValue(new TextEncoder().encode("stale\n"));

		const outcome = await planner.execute(
			makeRequest(makeBindingsDocument(), await makeClearance({ [BOUND_SOURCE]: { mode: "raw" } }, layout)),
		);

		expect(outcome.ok).toBe(true);
		expect(outcome.ok && outcome.plan.byteWrites).toHaveLength(1);
		expect(outcome.ok && outcome.plan.reportEntries).toEqual([]);
		expect(outcome.ok && outcome.plan.pending).toEqual([]);
	});
});

describe("region mode", () => {
	beforeEach(() => {
		vi.clearAllMocks();
	});

	test("a markerless destination is initialized and recorded for reconciliation", async () => {
		const { planner, sources, destinations, layout } = makePlanner();
		sources.readCore.mockResolvedValue({ kind: "core", core: "core body\n" });
		sources.readText.mockResolvedValue("");
		destinations.readText.mockResolvedValue("this project's prior body\n");
		const document = makeBindingsDocument({ pending: [BOUND_SOURCE] });

		const outcome = await planner.execute(
			makeRequest(document, await makeClearance({ [BOUND_SOURCE]: { mode: "region" } }, layout)),
		);

		expect(outcome.ok).toBe(true);
		const plan = outcome.ok ? outcome.plan : null;
		expect(plan?.textWrites).toHaveLength(1);
		expect(plan?.reportEntries).toEqual([
			{ destination: BOUND_SOURCE, source: BOUND_SOURCE, action: ACTION_INITIALIZED },
		]);
		expect(plan?.pending).toEqual([BOUND_SOURCE]);
	});

	test("an unchanged region destination is not refreshed", async () => {
		const { planner, sources, destinations, layout } = makePlanner();
		sources.readCore.mockResolvedValue({ kind: "core", core: "core body\n" });
		sources.readText.mockResolvedValue("");
		destinations.readText.mockResolvedValue(
			"<!-- core:begin -->\ncore body\n<!-- core:end -->\n\n<!-- project:begin -->\nowned\n<!-- project:end -->\n",
		);

		const outcome = await planner.execute(
			makeRequest(makeBindingsDocument(), await makeClearance({ [BOUND_SOURCE]: { mode: "region" } }, layout)),
		);

		expect(outcome.ok).toBe(true);
		expect(outcome.ok && outcome.plan.textWrites).toEqual([]);
		expect(outcome.ok && outcome.plan.reportEntries).toEqual([]);
	});
});

describe("merge mode", () => {
	beforeEach(() => {
		vi.clearAllMocks();
	});

	test("a merge destination this run newly bound is created", async () => {
		const { planner, sources, destinations, layout } = makePlanner();
		sources.readText.mockResolvedValue("{}");
		destinations.readText.mockResolvedValue(null);
		layout.exists.mockResolvedValue(false);

		const outcome = await planner.execute(
			makeRequest(
				makeBindingsDocument(),
				await makeClearance({ [BOUND_SOURCE]: { mode: "merge" } }, layout),
				new Set([BOUND_SOURCE]),
			),
		);

		expect(outcome.ok).toBe(true);
		expect(outcome.ok && outcome.plan.textWrites.map((write) => write.path)).toEqual([
			`${SYNCHRONIZATION_DESTINATION_ROOT}/${BOUND_SOURCE}`,
		]);
	});

	test("a merge destination this run did not bind is drift, not a creation", async () => {
		const { planner, sources, destinations, layout } = makePlanner();
		sources.readText.mockResolvedValue("{}");
		destinations.readText.mockResolvedValue(null);
		layout.exists.mockResolvedValue(false);

		const outcome = await planner.execute(
			makeRequest(makeBindingsDocument(), await makeClearance({ [BOUND_SOURCE]: { mode: "merge" } }, layout)),
		);

		expect(outcome.ok).toBe(false);
		const failure = outcome.ok ? null : outcome.failure;
		expect(failure?.code).toBe("drift");
		expect(failure?.message).toBe(
			`missing destination: ${SYNCHRONIZATION_DESTINATION_ROOT}/${BOUND_SOURCE} ` +
				"(merge mode cannot create it; the destination must exist)",
		);
	});
});
