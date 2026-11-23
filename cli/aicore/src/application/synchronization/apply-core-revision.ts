/**
 * Use case: splice each source core into its destinations and pin the revision.
 *
 * This coordinator holds the update's own request handling, its validation gates
 * in their original order, the read preflight, execution of the validated
 * envelope and the result message. The effective document is determined by
 * `PlanSynchronizationDocument`, the payload changes by `PlanUpdateChanges`,
 * and the mutations by `PrepareSynchronizationExecution`.
 *
 * A region destination's core region is replaced and its frontmatter identity
 * keys are refreshed from the source; an unrefreshable frontmatter keeps its
 * text and is named in the result message. A declared but absent region or raw
 * target is recreated, because a declaration must not depend on when it was
 * recorded. A merge destination is never created here: only a first enrollment
 * creates one.
 *
 * Writes happen only after every destination has been classified, so a later
 * refusal cannot leave a directory or a half-applied payload behind.
 *
 * The run reads and writes through two preflights. The read preflight clears
 * every path whose contents the run reads; the mutation preflight clears the
 * complete set of writes the run performs, including the ones it only
 * performs when their content changes.
 */

import { CLEARANCE_FILENAME } from "#domain/synchronization/constants.ts";
import {
	bindingModeConflict,
	destinationDrift,
	duplicatedDestinations,
	protectedExclusionFailure,
	withOptOuts,
	withRestoredOptOuts,
} from "#domain/synchronization/bindings.ts";
import { drift, failed, invalid, succeeded, type OperationOutcome } from "#domain/synchronization/failures.ts";
import { editorMismatch, effectiveEditor } from "#domain/synchronization/editor-profile.ts";
import { missingRegionSources } from "#domain/synchronization/reconciliation.ts";
import type {
	BindingsStore,
	ClearanceStore,
	DestinationFiles,
	FilesystemLayout,
	WriteTargetGuard,
} from "#domain/synchronization/ports.ts";

import { invalidClearance, readClearanceModes } from "./clearance-modes.ts";
import { PlanSynchronizationDocument } from "./plan-synchronization-document.ts";
import { ensureOpenCodeSecrets } from "./open-code-secrets.ts";
import { PlanUpdateChanges } from "./plan-update-changes.ts";
import { destinationReadPaths, PrepareSynchronizationExecution } from "./prepare-synchronization-execution.ts";
import type { SynchronizationRequest } from "./requests.ts";

/** Collaborators the update needs. */
export type ApplyCoreRevisionDependencies = {
	readonly bindings: BindingsStore;
	readonly clearance: ClearanceStore;
	readonly destinations: DestinationFiles;
	readonly layout: FilesystemLayout;
	readonly guard: WriteTargetGuard;
	readonly determineDocument: PlanSynchronizationDocument;
	readonly planChanges: PlanUpdateChanges;
	readonly prepareExecution: PrepareSynchronizationExecution;
};

export class ApplyCoreRevision {
	readonly #dependencies: ApplyCoreRevisionDependencies;

	constructor(dependencies: ApplyCoreRevisionDependencies) {
		this.#dependencies = dependencies;
	}

	async execute(request: SynchronizationRequest): Promise<OperationOutcome> {
		const {
			bindings,
			clearance: clearanceStore,
			destinations,
			layout,
			guard,
			determineDocument,
			planChanges,
			prepareExecution,
		} = this.#dependencies;

		const document = await bindings.load(request.bindingsPath);
		if (document === null) {
			return failed(invalid(`invalid bindings: ${request.bindingsPath}`));
		}

		const mismatch = editorMismatch(document.editor, request.editor);
		if (mismatch !== null) {
			return failed(mismatch);
		}
		const editor = effectiveEditor(request.editor, document.editor);

		const protectedExclusion = protectedExclusionFailure(document);
		if (protectedExclusion !== null) {
			return failed(protectedExclusion);
		}

		const clearance = await readClearanceModes(clearanceStore, layout, request.sourceRoot, editor);

		// A source this destination opted out of is unmanaged: no binding, no write
		// and no drift. The refusal below therefore never names it as uncleared, and
		// the write-target preflight never observes its old destination as a target.
		const managed = withOptOuts(document);
		// An opt-out its owner revoked — the entry is gone and the source is cleared
		// for this run — is delivered again, and its outstanding path leaves
		// `pending`.
		const current = withRestoredOptOuts(managed, clearance.modes, clearance.destinations);

		const clearancePath = layout.join(request.sourceRoot, CLEARANCE_FILENAME);
		if (!clearance.exists) {
			return failed(drift(`missing clearance file: ${clearancePath}`));
		}
		if (clearance.entries === null) {
			return failed(invalidClearance(clearancePath, clearance));
		}

		const determination = await determineDocument.execute({
			document: current,
			clearance,
			editor,
			sourceRoot: request.sourceRoot,
			destinationRoot: request.destinationRoot,
			intent: { kind: "update" },
		});
		if (!determination.ok) {
			return failed(determination.failure);
		}
		const determined = determination.value;
		const effective = determined.document;

		// Every path this run reads is cleared before it is read: the effective
		// document the run acts on is guarded before any payload read.
		const readRefusal = await guard.refuse({
			command: "apply",
			sourceRoot: request.sourceRoot,
			destinationRoot: request.destinationRoot,
			bindingsPath: request.bindingsPath,
			document: effective,
			modes: clearance.modes,
			newRawDestinations: determined.newRawDestinations,
			phase: "read",
			readPaths: await destinationReadPaths(effective, request.destinationRoot, layout),
		});
		if (readRefusal !== null) {
			return failed(readRefusal);
		}

		for (const entry of effective.bindings) {
			const conflict = bindingModeConflict(entry, clearance.modes);
			if (conflict !== null) {
				return failed(conflict);
			}
		}
		// Two live bindings cannot own one destination, and a distributable binding
		// must not displace one awaiting reconciliation. Nothing is mutated first.
		const duplicated = duplicatedDestinations(effective);
		if (duplicated.length > 0) {
			return failed(invalid(`conflicting destination ownership: ${duplicated.join(", ")}`));
		}
		const relocated = destinationDrift(effective, clearance.entries, clearance.destinations);
		if (relocated !== null) {
			return failed(relocated);
		}

		const planned = await planChanges.execute({
			document: effective,
			request,
			clearance,
			distributable: determined.distributable,
			retired: determined.retired,
		});
		if (!planned.ok) {
			return failed(planned.failure);
		}
		const plan = planned.plan;

		const pinned = { ...effective, coreRevision: request.sourceRevision, pending: plan.pending };

		// The secret setup, the root blocker and the complete mutation set are
		// prepared and validated before the first mutation.
		const preparation = await prepareExecution.execute({
			command: "apply",
			sourceRoot: request.sourceRoot,
			destinationRoot: request.destinationRoot,
			bindingsPath: request.bindingsPath,
			document: effective,
			pinned,
			pending: plan.pending,
			missingRegions: missingRegionSources(determined.requiresReconciliation),
			modes: clearance.modes,
			newRawDestinations: determined.newRawDestinations,
			editor,
			plan,
			writesReconciliationReport: false,
		});
		if (!preparation.ok) {
			return failed(preparation.failure);
		}

		const notes = [...plan.notes];
		for (const write of plan.textWrites) {
			await layout.ensureDirectory(layout.parent(write.path));
			await destinations.writeText(write.path, write.content);
		}
		for (const write of plan.byteWrites) {
			await layout.ensureDirectory(layout.parent(write.path));
			await destinations.writeBytes(write.path, write.content);
		}
		// A retired source owns no destination content, so its managed copy is
		// removed: nothing of the destination's own could be in it. The planner's
		// deletion set is the same set the preflight validated.
		for (const deletion of plan.deletions) {
			await destinations.remove(deletion.path);
			notes.push(`retired: ${deletion.destination}`);
		}
		await ensureOpenCodeSecrets(editor, request.destinationRoot, {
			destinations,
			layout,
		});

		await bindings.save(request.bindingsPath, pinned);
		await layout.syncBlocker(
			request.destinationRoot,
			pinned,
			plan.pending,
			missingRegionSources(determined.requiresReconciliation),
		);

		const parts = ["applied", ...notes];
		if (plan.created.length > 0) {
			parts.push(`created: ${plan.created.join(", ")}`);
		}
		return succeeded(parts.join("; "));
	}
}
