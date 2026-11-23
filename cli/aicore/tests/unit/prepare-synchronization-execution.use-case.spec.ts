/**
 * Unit: the execution preparation — what a run writes beyond its payload.
 *
 * One behavioral concern per group: the secret setup's ignore read is cleared
 * before it is read, the complete mutation envelope carries each path's owner,
 * the root blocker is projected as its own write, and the reconciliation report
 * is included only when the run writes one. The ports are doubled (contract
 * T2, T3, T15).
 */

import { beforeEach, describe, expect, test, vi } from "vitest";
import { mock, type MockProxy } from "vitest-mock-extended";

import {
	PrepareSynchronizationExecution,
	type ExecutionPreparationInput,
	type SynchronizationPayloadPlan,
} from "#application/synchronization/prepare-synchronization-execution.ts";
import type { BindingsDocument } from "#domain/synchronization/bindings.ts";
import type { DestinationFiles, FilesystemLayout, WriteTargetGuard } from "#domain/synchronization/ports.ts";
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

describe("secret preparation", () => {
	beforeEach(() => {
		vi.clearAllMocks();
	});

	test("the ignore read is cleared before the secret planner reads it", async () => {
		const { preparation, layout } = makePreparation();

		const outcome = await preparation.execute(makeInput(makeConfigurationPlan()));

		expect(outcome.ok).toBe(true);
		const value = outcome.ok ? outcome.value : null;
		expect(value?.clearedReadPaths).toEqual([{ path: GITIGNORE_PATH, owner: "secret" }]);
		// The ignore rule, the directory and the absent credential are all planned.
		const secrets = value?.secretMutations.map((mutation) => mutation.path) ?? [];
		expect(secrets).toEqual([GITIGNORE_PATH, SECRETS_DIRECTORY, SECRET_PATH]);
		expect(layout.ensureDirectory).not.toHaveBeenCalled();
	});
});

describe("mutation envelope", () => {
	beforeEach(() => {
		vi.clearAllMocks();
	});

	test("an unsafe mutation stops the run before the mutation phase", async () => {
		const { preparation, guard } = makePreparation();
		guard.refuse.mockResolvedValueOnce({ code: "invalid", message: "unsafe write target" });

		const outcome = await preparation.execute(makeInput(makeConfigurationPlan()));

		expect(outcome.ok).toBe(false);
		expect(guard.refuse).toHaveBeenCalledTimes(1);
	});

	test("the root blocker is projected as its own write", async () => {
		const { preparation, layout } = makePreparation();
		layout.planBlocker.mockResolvedValue({ path: ROOT_PATH, content: "blocker\n" });

		const outcome = await preparation.execute(
			makeInput({ textWrites: [], byteWrites: [], deletions: [], payload: [] }),
		);

		expect(outcome.ok).toBe(true);
		const value = outcome.ok ? outcome.value : null;
		expect(value?.blocker).toEqual({ path: ROOT_PATH, content: "blocker\n" });
		expect(value?.mutations).toContainEqual({ path: ROOT_PATH, kind: "file-write", owner: "root" });
	});
});

describe("reconciliation report", () => {
	beforeEach(() => {
		vi.clearAllMocks();
	});

	test("a run that writes a report includes its path; one that does not omits it", async () => {
		const withReport = makePreparation();
		const reported = await withReport.preparation.execute(
			makeInput(
				{ textWrites: [], byteWrites: [], deletions: [], payload: [] },
				{ writesReconciliationReport: true },
			),
		);
		expect(reported.ok && reported.value.mutations).toContainEqual({
			path: REPORT_PATH,
			kind: "file-write",
			owner: "report",
		});

		const withoutReport = makePreparation();
		const plain = await withoutReport.preparation.execute(
			makeInput({ textWrites: [], byteWrites: [], deletions: [], payload: [] }),
		);
		expect(plain.ok && plain.value.mutations.map((mutation) => mutation.owner)).toEqual(["bindings"]);
	});
});
