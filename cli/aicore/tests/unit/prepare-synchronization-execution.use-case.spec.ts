/**
 * Unit: the execution preparation — validation only, no write.
 *
 * One behavioral concern per group: the secret setup's ignore read is cleared
 * only when it will be read, an unsafe mutation refuses the run before anything
 * is written, the root blocker is projected as its own write, and the
 * reconciliation report is included only when the run writes one. The operation
 * returns a success or a refusal; the mutation set and each path's owner are
 * observed through the guard it validates them with (contract T2, T3, T15).
 */

import { beforeEach, describe, expect, test, vi } from "vitest";
import { mock, type MockProxy } from "vitest-mock-extended";

import {
	PrepareSynchronizationExecution,
	type ExecutionPreparationInput,
	type SynchronizationPayloadPlan,
} from "#application/synchronization/prepare-synchronization-execution.ts";
import type { BindingsDocument } from "#domain/synchronization/bindings.ts";
import type {
	DestinationFiles,
	FilesystemLayout,
	PlannedMutation,
	WriteTargetGuard,
	WriteTargetRequest,
} from "#domain/synchronization/ports.ts";
import {
	SYNCHRONIZATION_BINDINGS_PATH,
	SYNCHRONIZATION_DESTINATION_ROOT,
	makeBindingsDocument,
} from "#support/synchronization.factory.ts";

const CONFIGURATION_PATH = `${SYNCHRONIZATION_DESTINATION_ROOT}/.opencode/opencode.jsonc`;
const GITIGNORE_PATH = `${SYNCHRONIZATION_DESTINATION_ROOT}/.gitignore`;
const SECRETS_DIRECTORY = `${SYNCHRONIZATION_DESTINATION_ROOT}/.secrets`;
const SECRET_PATH = `${SYNCHRONIZATION_DESTINATION_ROOT}/.secrets/context7-api-key`;
const REPORT_PATH = `${SYNCHRONIZATION_DESTINATION_ROOT}/.aicore/reconciliation/init.yaml`;
const ROOT_PATH = `${SYNCHRONIZATION_DESTINATION_ROOT}/AGENTS.md`;

/** A payload plan that creates the OpenCode configuration. */
function makeConfigurationPlan(): SynchronizationPayloadPlan {
	return {
		textWrites: [{ path: CONFIGURATION_PATH, content: "{}\n" }],
		byteWrites: [],
		deletions: [],
		payload: [{ kind: "text-write", path: CONFIGURATION_PATH, content: "{}\n" }],
	};
}

/** A payload plan with no effects at all. */
function makeEmptyPlan(): SynchronizationPayloadPlan {
	return { textWrites: [], byteWrites: [], deletions: [], payload: [] };
}

/** The preparation input over one document and payload plan. */
function makeInput(
	plan: SynchronizationPayloadPlan,
	overrides: Partial<ExecutionPreparationInput> = {},
): ExecutionPreparationInput {
	const document: BindingsDocument = makeBindingsDocument();
	return {
		command: "apply",
		sourceRoot: "G:/projects/ai-core",
		destinationRoot: SYNCHRONIZATION_DESTINATION_ROOT,
		bindingsPath: SYNCHRONIZATION_BINDINGS_PATH,
		document,
		pinned: document,
		pending: [],
		missingRegions: [],
		modes: new Map(),
		newRawDestinations: new Set<string>(),
		editor: "opencode",
		plan,
		writesReconciliationReport: false,
		...overrides,
	};
}

type PreparationPorts = {
	readonly destinations: MockProxy<DestinationFiles>;
	readonly layout: MockProxy<FilesystemLayout>;
	readonly guard: MockProxy<WriteTargetGuard>;
};

/** The operation over doubled ports, arranged to accept the run. */
function makePreparation(options: Partial<PreparationPorts> = {}): PreparationPorts & {
	readonly preparation: PrepareSynchronizationExecution;
} {
	const ports: PreparationPorts = {
		destinations: options.destinations ?? mock<DestinationFiles>(),
		layout: options.layout ?? mock<FilesystemLayout>(),
		guard: options.guard ?? mock<WriteTargetGuard>(),
	};
	ports.layout.join.mockImplementation((root, relative) => `${root}/${relative}`);
	ports.layout.parent.mockImplementation((path) => path.slice(0, path.lastIndexOf("/")));
	ports.layout.exists.mockResolvedValue(false);
	ports.layout.planBlocker.mockResolvedValue(null);
	ports.guard.refuse.mockResolvedValue(null);
	ports.destinations.readText.mockResolvedValue(null);
	return { ...ports, preparation: new PrepareSynchronizationExecution(ports) };
}

/** The guard request of one phase, as the operation validated it. */
function guardRequest(guard: MockProxy<WriteTargetGuard>, phase: "read" | "mutations"): WriteTargetRequest | undefined {
	return guard.refuse.mock.calls.find(([request]) => request.phase === phase)?.[0];
}

/** The paths and owners of one validated mutation set. */
function mutationOwners(guard: MockProxy<WriteTargetGuard>): readonly PlannedMutation[] {
	return guardRequest(guard, "mutations")?.mutations ?? [];
}

describe("secret preparation", () => {
	beforeEach(() => {
		vi.clearAllMocks();
	});

	test("the ignore read is cleared only when the secret setup will read it", async () => {
		const withConfiguration = makePreparation();

		const prepared = await withConfiguration.preparation.execute(makeInput(makeConfigurationPlan()));

		expect(prepared.ok).toBe(true);
		expect(guardRequest(withConfiguration.guard, "read")?.readPaths).toEqual([
			{ path: GITIGNORE_PATH, owner: "secret" },
		]);
		// The ignore rule, the directory and the absent credential are all validated.
		expect(mutationOwners(withConfiguration.guard).map((mutation) => mutation.path)).toEqual([
			CONFIGURATION_PATH,
			SYNCHRONIZATION_BINDINGS_PATH,
			GITIGNORE_PATH,
			SECRETS_DIRECTORY,
			SECRET_PATH,
		]);

		// A destination with no OpenCode configuration reads no ignore file.
		const withoutConfiguration = makePreparation();
		await withoutConfiguration.preparation.execute(makeInput(makeEmptyPlan()));
		expect(guardRequest(withoutConfiguration.guard, "read")).toBeUndefined();
	});
});

describe("mutation envelope", () => {
	beforeEach(() => {
		vi.clearAllMocks();
	});

	test("an unsafe mutation stops the run before anything is written", async () => {
		const { preparation, destinations, layout, guard } = makePreparation();
		guard.refuse.mockResolvedValueOnce({ code: "invalid", message: "unsafe write target" });

		const outcome = await preparation.execute(makeInput(makeConfigurationPlan()));

		expect(outcome.ok).toBe(false);
		expect(destinations.writeText).not.toHaveBeenCalled();
		expect(destinations.writeBytes).not.toHaveBeenCalled();
		expect(destinations.remove).not.toHaveBeenCalled();
		expect(layout.ensureDirectory).not.toHaveBeenCalled();
	});

	test("the root blocker is projected as its own validated write", async () => {
		const { preparation, layout, guard } = makePreparation();
		layout.planBlocker.mockResolvedValue({ path: ROOT_PATH, content: "blocker\n" });

		const outcome = await preparation.execute(makeInput(makeEmptyPlan()));

		expect(outcome.ok).toBe(true);
		expect(mutationOwners(guard)).toContainEqual({ path: ROOT_PATH, kind: "file-write", owner: "root" });
	});
});

describe("reconciliation report", () => {
	beforeEach(() => {
		vi.clearAllMocks();
	});

	test("a run that writes a report validates its path; one that does not omits it", async () => {
		const withReport = makePreparation();
		const reported = await withReport.preparation.execute(
			makeInput(makeEmptyPlan(), { writesReconciliationReport: true }),
		);
		expect(reported.ok).toBe(true);
		expect(mutationOwners(withReport.guard)).toContainEqual({
			path: REPORT_PATH,
			kind: "file-write",
			owner: "report",
		});

		const withoutReport = makePreparation();
		const plain = await withoutReport.preparation.execute(makeInput(makeEmptyPlan()));
		expect(plain.ok).toBe(true);
		expect(mutationOwners(withoutReport.guard).map((mutation) => mutation.owner)).toEqual(["bindings"]);
	});
});
