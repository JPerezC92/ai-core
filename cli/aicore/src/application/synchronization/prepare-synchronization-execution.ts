/**
 * Application operation: prepare and validate a synchronization run's mutations.
 *
 * Once the command's payload plan and the pinned document exist, this operation
 * decides what the run will write beyond that payload: the OpenCode secret
 * directory, the ignore rule and an absent credential, the root runtime file's
 * blocker, the bindings document and the reconciliation report. It clears the
 * ignore file before the secret planner reads it, projects the blocker from the
 * ordered payload, assembles the complete mutation envelope with each path's
 * owner, and validates that envelope before the first mutation happens.
 *
 * It decides nothing about the payload and performs no write: the coordinator
 * executes the validated envelope through the existing executors.
 */

import { RECONCILIATION_DIRECTORY, RECONCILIATION_FILENAME } from "#domain/synchronization/constants.ts";
import type { BindingMode } from "#domain/synchronization/constants.ts";
import type { BindingsDocument } from "#domain/synchronization/bindings.ts";
import type { EditorProfile } from "#domain/synchronization/editor-profile.ts";
import type { SynchronizationFailure } from "#domain/synchronization/failures.ts";
import type { MissingRegionSource } from "#domain/synchronization/reconciliation.ts";
import type {
	DestinationFiles,
	FilesystemLayout,
	PlannedMutation,
	PlannedPayload,
	PlannedRead,
	WriteTargetGuard,
} from "#domain/synchronization/ports.ts";

import { planOpenCodeSecretWrites, prepareOpenCodeSecrets } from "./open-code-secrets.ts";

/** One pending text write a command's payload plan records. */
export type ExecutionTextWrite = {
	readonly path: string;
	readonly content: string;
};

/** One pending byte write a command's payload plan records. */
export type ExecutionByteWrite = {
	readonly path: string;
	readonly content: Uint8Array;
};

/** The payload plan of one command, as its planner produced it. */
export type SynchronizationPayloadPlan = {
	readonly textWrites: readonly ExecutionTextWrite[];
	readonly byteWrites: readonly ExecutionByteWrite[];
	/** The absolute paths whose managed files this run removes. */
	readonly deletions: readonly string[];
	/** The pending effects, in the order the run applies them. */
	readonly payload: readonly PlannedPayload[];
};

/** What the execution preparation needs to project and validate a run. */
export type ExecutionPreparationInput = {
	/** The command whose preflight this is: `apply` or `init`. */
	readonly command: "apply" | "init";
	readonly sourceRoot: string;
	readonly destinationRoot: string;
	readonly bindingsPath: string;
	/** The effective document the guard request is evaluated against. */
	readonly document: BindingsDocument;
	/** The document this run persists once its payload and pending are known. */
	readonly pinned: BindingsDocument;
	readonly pending: readonly string[];
	readonly missingRegions: readonly MissingRegionSource[];
	readonly modes: ReadonlyMap<string, BindingMode>;
	readonly newRawDestinations: ReadonlySet<string>;
	readonly editor: EditorProfile;
	readonly plan: SynchronizationPayloadPlan;
	/** Whether this run writes a reconciliation report beside the bindings. */
	readonly writesReconciliationReport: boolean;
};

/** The validated mutation envelope, with each path's owner. */
export type PreparedExecution = {
	/** The read paths the read preflight cleared before they were read. */
	readonly clearedReadPaths: readonly PlannedRead[];
	/** Every mutation this run performs, validated before the first one. */
	readonly mutations: readonly PlannedMutation[];
	/** The root runtime file write this run performs, or `null`. */
	readonly blocker: { readonly path: string; readonly content: string } | null;
	/** The secret mutations the setup will perform after the payload. */
	readonly secretMutations: readonly PlannedMutation[];
};

/** A validated envelope, or the refusal the preflight earns. */
export type ExecutionPreparationOutcome =
	| { readonly ok: true; readonly value: PreparedExecution }
	| { readonly ok: false; readonly failure: SynchronizationFailure };

/** Collaborators the execution preparation needs. */
export type PrepareSynchronizationExecutionDependencies = {
	readonly destinations: DestinationFiles;
	readonly layout: FilesystemLayout;
	readonly guard: WriteTargetGuard;
};

export class PrepareSynchronizationExecution {
	readonly #dependencies: PrepareSynchronizationExecutionDependencies;

	constructor(dependencies: PrepareSynchronizationExecutionDependencies) {
		this.#dependencies = dependencies;
	}

	async execute(input: ExecutionPreparationInput): Promise<ExecutionPreparationOutcome> {
		const { destinations, layout, guard } = this.#dependencies;
		const {
			command,
			sourceRoot,
			destinationRoot,
			bindingsPath,
			document,
			pinned,
			pending,
			missingRegions,
			modes,
			newRawDestinations,
			editor,
			plan,
			writesReconciliationReport,
		} = input;

		// The secret setup reads the ignore file only when it has to plan its
		// rule, so that read is cleared on its own.
		const preparation = await prepareOpenCodeSecrets(editor, destinationRoot, plan.payload, layout);
		const clearedReadPaths: PlannedRead[] = [];
		if (preparation.readsIgnore) {
			const readPaths: PlannedRead[] = [{ path: preparation.paths.gitignore, owner: "secret" }];
			const ignoreRefusal = await guard.refuse({
				command,
				sourceRoot,
				destinationRoot,
				bindingsPath,
				document,
				modes,
				newRawDestinations,
				phase: "read",
				readPaths,
			});
			if (ignoreRefusal !== null) {
				return { ok: false, failure: ignoreRefusal };
			}
			clearedReadPaths.push(...readPaths);
		}
		const secretMutations = await planOpenCodeSecretWrites(editor, preparation, plan.payload, {
			destinations,
			layout,
		});

		// The root runtime file's blocker is a write of its own, and the
		// projection says whether this run performs one.
		const blocker =
			(await layout.planBlocker(destinationRoot, pinned, pending, missingRegions, plan.payload)) ?? null;

		const mutations: PlannedMutation[] = [
			...plan.textWrites.map((write) => ({
				path: write.path,
				kind: "file-write" as const,
				owner: "payload" as const,
			})),
			...plan.byteWrites.map((write) => ({
				path: write.path,
				kind: "file-write" as const,
				owner: "payload" as const,
			})),
			...plan.deletions.map((path) => ({ path, kind: "file-delete" as const, owner: "payload" as const })),
			{ path: bindingsPath, kind: "file-write", owner: "bindings" },
			...(writesReconciliationReport
				? [
						{
							path: layout.join(
								layout.parent(bindingsPath),
								`${RECONCILIATION_DIRECTORY}/${RECONCILIATION_FILENAME}`,
							),
							kind: "file-write" as const,
							owner: "report" as const,
						},
					]
				: []),
			...(blocker === null ? [] : [{ path: blocker.path, kind: "file-write" as const, owner: "root" as const }]),
			...secretMutations,
		];
		const mutationRefusal = await guard.refuse({
			command,
			sourceRoot,
			destinationRoot,
			bindingsPath,
			document,
			modes,
			newRawDestinations,
			phase: "mutations",
			mutations,
		});
		if (mutationRefusal !== null) {
			return { ok: false, failure: mutationRefusal };
		}

		return { ok: true, value: { clearedReadPaths, mutations, blocker, secretMutations } };
	}
}
